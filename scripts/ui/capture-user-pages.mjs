import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const mode = process.argv[2] || 'before';
const base = (process.env.BASE_URL || 'http://127.0.0.1:3000').replace(/\/$/, '');
const outDir = path.resolve(`artifacts/user-style-compare/${mode}`);
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

const pages = [
  { name: '01-users-list', url: '/admin/users/list' },
  { name: '02-users-roles', url: '/admin/users/roles' },
  { name: '03-users-departments', url: '/admin/users/departments' },
  { name: '04-users-profile', url: '/admin/users/profile' },
  { name: '05-users-profiles', url: '/admin/users/profiles' },
  { name: '06-users-logs', url: '/admin/users/logs' },
];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1600, height: 1100 } });
const page = await context.newPage();

async function login() {
  await page.goto(`${base}/#/login`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.fill('input[name="username"]', process.env.ADMIN_USERNAME || 'admin');
  await page.fill('input[name="password"]', process.env.ADMIN_PASSWORD || 'admin123');
  await page.click('.login-btn');
  await page.waitForTimeout(2500);
}

await login();
const hashMode = page.url().includes('/#/');
const buildUrl = (p) => (hashMode ? `${base}/#${p}` : `${base}${p}`);

for (const p of pages) {
  const target = buildUrl(p.url);
  try {
    await page.goto(target, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2200);
    await page.screenshot({ path: path.join(outDir, `${p.name}.png`), fullPage: true });
    console.log(`[ok] ${p.url} => ${page.url()}`);
  } catch (e) {
    console.error(`[fail] ${p.url}: ${e.message}`);
  }
}

await browser.close();
