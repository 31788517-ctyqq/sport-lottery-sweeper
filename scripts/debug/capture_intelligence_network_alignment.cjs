const fs = require('fs');
const path = require('path');
const { chromium, request: pwRequest } = require('@playwright/test');

const FRONTEND_URL = process.env.E2E_FRONTEND_URL || 'http://localhost:3000/admin/intelligence/collection';
const BACKEND_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';
const ADMIN_USER = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.E2E_ADMIN_PASS || 'admin123';
const OUT_DIR = path.resolve(process.cwd(), 'logs');
const LOG_FILE = path.resolve(process.cwd(), 'logs', 'backend_8000.log');

function nowIso() {
  return new Date().toISOString();
}

function parseLogTimestamp(line) {
  const m = line.match(/^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) - /);
  if (!m) return null;
  const ts = new Date(`${m[1]}T${m[2]}`);
  return Number.isNaN(ts.getTime()) ? null : ts;
}

async function getToken() {
  const api = await pwRequest.newContext({ baseURL: BACKEND_URL });
  let resp = await api.post('/api/v1/login', { data: { username: ADMIN_USER, password: ADMIN_PASS } });
  if (resp.status() === 404) {
    resp = await api.post('/api/v1/auth/login', { data: { username: ADMIN_USER, password: ADMIN_PASS } });
  }
  if (resp.status() !== 200) {
    const txt = await resp.text();
    throw new Error(`login failed: ${resp.status()} ${txt.slice(0, 300)}`);
  }
  const json = await resp.json();
  const token = json?.access_token || json?.data?.access_token;
  if (!token) throw new Error(`token missing from login response: ${JSON.stringify(json).slice(0, 300)}`);
  await api.dispose();
  return token;
}

async function run() {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
  const startedAt = new Date();
  const startedAtIso = nowIso();

  const token = await getToken();
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

  await context.addInitScript((t) => {
    localStorage.setItem('access_token', t);
    localStorage.setItem('token', t);
    localStorage.setItem('auth_token', t);
  }, token);

  const page = await context.newPage();
  const network = [];

  page.on('request', (req) => {
    const url = req.url();
    if (!url.includes('/api/')) return;
    network.push({
      type: 'request',
      at: nowIso(),
      method: req.method(),
      url,
      path: (() => {
        try { return new URL(url).pathname; } catch { return url; }
      })(),
      query: (() => {
        try {
          const u = new URL(url);
          const q = {};
          for (const [k, v] of u.searchParams.entries()) q[k] = v;
          return q;
        } catch {
          return {};
        }
      })(),
      postData: req.postData() || null,
    });
  });

  page.on('response', async (resp) => {
    const url = resp.url();
    if (!url.includes('/api/')) return;
    let bodyPreview = null;
    try {
      const txt = await resp.text();
      bodyPreview = txt.slice(0, 350);
    } catch {}
    network.push({
      type: 'response',
      at: nowIso(),
      status: resp.status(),
      method: resp.request().method(),
      url,
      path: (() => {
        try { return new URL(url).pathname; } catch { return url; }
      })(),
      bodyPreview,
    });
  });

  await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(2500);

  // If redirected to login, perform UI login (captcha is locally generated on canvas)
  const usernameInput = page.locator('input[placeholder*="用户名"], input[name="username"]').first();
  const passwordInput = page.locator('input[placeholder*="密码"], input[name="password"]').first();
  if (await usernameInput.count()) {
    await usernameInput.fill(ADMIN_USER).catch(() => {});
    await passwordInput.fill(ADMIN_PASS).catch(() => {});
    const captchaInput = page.locator('input[placeholder*="验证码"], input[name="captcha"]').first();
    if (await captchaInput.count()) {
      const captchaText = await page.locator('canvas').first().evaluate((el) => (el && el.dataset ? el.dataset.captcha || '' : '')).catch(() => '');
      if (captchaText) {
        await captchaInput.fill(String(captchaText)).catch(() => {});
      }
    }
    const loginBtn = page.getByRole('button', { name: '登录' }).first();
    if (await loginBtn.count()) {
      await loginBtn.click({ timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(3000);
      if (!page.url().includes('/admin/intelligence/collection')) {
        await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      }
      await page.waitForTimeout(2000);
    }
  }

  const urlAfterGoto = page.url();

  // Try to force the exact request set user mentioned: date=2026-02-10 + query + create task
  // 1) date query
  const dateInput = page.locator('input[placeholder*="选择日期"], .el-date-editor input').first();
  if (await dateInput.count()) {
    await dateInput.click({ timeout: 5000 }).catch(() => {});
    await dateInput.fill('2026-02-10').catch(() => {});
    await dateInput.press('Enter').catch(() => {});
  }

  const queryBtn = page.getByRole('button', { name: '查询赛程' });
  if (await queryBtn.count()) {
    await queryBtn.click({ timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(3000);
  }

  // 2) select first row
  const firstCheckbox = page.locator('.el-table__body-wrapper .el-checkbox').first();
  if (await firstCheckbox.count()) {
    await firstCheckbox.click({ timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(800);
  }

  // 3) create task
  const createBtn = page.getByRole('button', { name: '创建任务' });
  if (await createBtn.count()) {
    await createBtn.click({ timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(6000);
  }

  const endedAt = new Date();
  const endedAtIso = nowIso();

  await page.screenshot({ path: path.resolve(OUT_DIR, 'intelligence_collection_capture.png'), fullPage: true });
  await browser.close();

  // Read backend logs in the same time window
  let backendLogLines = [];
  if (fs.existsSync(LOG_FILE)) {
    const lines = fs.readFileSync(LOG_FILE, 'utf8').split(/\r?\n/);
    backendLogLines = lines.filter((line) => {
      if (!line.includes('intelligence.collection')) return false;
      const ts = parseLogTimestamp(line);
      if (!ts) return false;
      return ts >= new Date(startedAt.getTime() - 5000) && ts <= new Date(endedAt.getTime() + 30000);
    });
  }

  const requestsOnly = network.filter((x) => x.type === 'request' && String(x.url).includes('/api/v1/admin/intelligence/collection'));
  const responsesOnly = network.filter((x) => x.type === 'response' && String(x.url).includes('/api/v1/admin/intelligence/collection'));
  const authAndCommon = network.filter((x) => String(x.url).includes('/api/auth/login') || String(x.url).includes('/api/v1/login'));

  const summary = {
    startedAt: startedAtIso,
    endedAt: endedAtIso,
    frontendUrl: FRONTEND_URL,
    urlAfterGoto,
    counts: {
      requests: requestsOnly.length,
      responses: responsesOnly.length,
      authRequests: authAndCommon.filter((x) => x.type === 'request').length,
      authResponses: authAndCommon.filter((x) => x.type === 'response').length,
      backendLogLines: backendLogLines.length,
    },
    network,
    backendLogLines,
  };

  const jsonOut = path.resolve(OUT_DIR, 'intelligence_collection_network_alignment.json');
  fs.writeFileSync(jsonOut, JSON.stringify(summary, null, 2), 'utf8');

  // Markdown one-to-one alignment (best-effort by endpoint)
  const byPath = {};
  for (const r of requestsOnly) {
    byPath[r.path] = byPath[r.path] || { request: [], response: [], backend: [] };
    byPath[r.path].request.push(r);
  }
  for (const r of responsesOnly) {
    byPath[r.path] = byPath[r.path] || { request: [], response: [], backend: [] };
    byPath[r.path].response.push(r);
  }
  for (const l of backendLogLines) {
    if (l.includes('[intelligence.collection.matches]')) {
      const p = '/api/v1/admin/intelligence/collection/matches';
      byPath[p] = byPath[p] || { request: [], response: [], backend: [] };
      byPath[p].backend.push(l);
    } else if (l.includes('[intelligence.collection.tasks.create]')) {
      const p = '/api/v1/admin/intelligence/collection/tasks';
      byPath[p] = byPath[p] || { request: [], response: [], backend: [] };
      byPath[p].backend.push(l);
    }
  }

  let md = '';
  md += '# Intelligence Collection Network vs Backend Log Alignment\n\n';
  md += `- startedAt: ${startedAtIso}\n`;
  md += `- endedAt: ${endedAtIso}\n`;
  md += `- pageAfterGoto: ${urlAfterGoto}\n`;
  md += `- screenshot: logs/intelligence_collection_capture.png\n\n`;

  for (const [p, group] of Object.entries(byPath)) {
    md += `## ${p}\n`;
    const req = group.request[0];
    if (req) {
      md += '- Browser request params:\n';
      md += '```json\n';
      md += JSON.stringify({ method: req.method, query: req.query, postData: req.postData }, null, 2);
      md += '\n```\n';
    } else {
      md += '- Browser request params: (no captured request)\n';
    }

    const resp = group.response[0];
    if (resp) {
      md += `- Browser response: status=${resp.status}\n`;
    } else {
      md += '- Browser response: (no captured response)\n';
    }

    if (group.backend.length) {
      md += '- Backend logs:\n';
      for (const line of group.backend) {
        md += `  - ${line}\n`;
      }
    } else {
      md += '- Backend logs: (no matched logs in window)\n';
    }
    md += '\n';
  }

  const mdOut = path.resolve(OUT_DIR, 'intelligence_collection_network_alignment.md');
  fs.writeFileSync(mdOut, md, 'utf8');

  console.log(`Wrote ${jsonOut}`);
  console.log(`Wrote ${mdOut}`);
  console.log(JSON.stringify(summary.counts));
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
