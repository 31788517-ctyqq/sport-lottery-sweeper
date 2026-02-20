import { test, expect } from '@playwright/test';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';

async function loginAndGetToken(request) {
  // Prefer current backend login endpoint
  let resp = await request.post(`${BACKEND_BASE_URL}/api/v1/login`, {
    data: { username: ADMIN_USERNAME, password: ADMIN_PASSWORD }
  });

  if (resp.status() === 404) {
    // Fallback for older auth route variants
    resp = await request.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
      data: { username: ADMIN_USERNAME, password: ADMIN_PASSWORD }
    });
  }

  expect(resp.status()).toBe(200);
  const json = await resp.json();
  const token = json?.access_token || json?.data?.access_token;
  expect(token).toBeTruthy();
  return token;
}

test.describe('Intelligence Collection Auth Smoke', () => {
  test('login + endpoints return 200 and valid data shape', async ({ request }) => {
    test.setTimeout(60000);

    const token = await loginAndGetToken(request);
    const headers = { Authorization: `Bearer ${token}` };

    const sourcesResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/intelligence/collection/sources`, {
      headers
    });
    expect(sourcesResp.status()).toBe(200);
    const sourcesJson = await sourcesResp.json();
    expect(sourcesJson?.success).toBe(true);
    expect(Array.isArray(sourcesJson?.data)).toBe(true);
    if (sourcesJson.data.length > 0) {
      const first = sourcesJson.data[0];
      expect(typeof first.code).toBe('string');
      expect(typeof first.name).toBe('string');
      expect(typeof first.url).toBe('string');
      expect(typeof first.item_count).toBe('number');
    }

    const matchesResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/intelligence/collection/matches`, {
      headers,
      params: { page: 1, size: 5 }
    });
    expect(matchesResp.status()).toBe(200);
    const matchesJson = await matchesResp.json();
    expect(matchesJson?.success).toBe(true);
    expect(matchesJson?.data).toBeTruthy();
    expect(Array.isArray(matchesJson.data.items)).toBe(true);
    expect(typeof matchesJson.data.total).toBe('number');
    expect(typeof matchesJson.data.page).toBe('number');
    expect(typeof matchesJson.data.size).toBe('number');
    if (matchesJson.data.items.length > 0) {
      const first = matchesJson.data.items[0];
      expect(typeof first.id).toBe('number');
      expect(typeof first.league_name).toBe('string');
      expect(typeof first.home_team).toBe('string');
      expect(typeof first.away_team).toBe('string');
      expect(typeof first.status).toBe('string');
    }

    const tasksResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/intelligence/collection/tasks`, {
      headers,
      params: { page: 1, size: 5 }
    });
    expect(tasksResp.status()).toBe(200);
    const tasksJson = await tasksResp.json();
    expect(tasksJson?.success).toBe(true);
    expect(tasksJson?.data).toBeTruthy();
    expect(Array.isArray(tasksJson.data.items)).toBe(true);
    expect(typeof tasksJson.data.total).toBe('number');
    expect(typeof tasksJson.data.page).toBe('number');
    expect(typeof tasksJson.data.size).toBe('number');
    if (tasksJson.data.items.length > 0) {
      const first = tasksJson.data.items[0];
      expect(typeof first.id).toBe('number');
      expect(typeof first.task_uuid).toBe('string');
      expect(typeof first.mode).toBe('string');
      expect(typeof first.status).toBe('string');
      expect(Array.isArray(first.match_ids)).toBe(true);
      expect(Array.isArray(first.sources)).toBe(true);
      expect(Array.isArray(first.intel_types)).toBe(true);
    }
  });
});
