#!/usr/bin/env python3
"""
Live smoke check for /admin/intelligence/graph.

What it does:
1. Clear port blockers on 8000/3000.
2. Start backend and frontend dev servers.
3. Login via backend API.
4. Call graph overview API and save sample.
5. Open graph page with Playwright and take screenshot.
6. Write a concise markdown report.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

BACKEND_OUT = LOG_DIR / "graph_live_backend.out.log"
BACKEND_ERR = LOG_DIR / "graph_live_backend.err.log"
FRONTEND_OUT = LOG_DIR / "graph_live_frontend.out.log"
FRONTEND_ERR = LOG_DIR / "graph_live_frontend.err.log"
API_SAMPLE_JSON = LOG_DIR / "intelligence_graph_api_sample.json"
SCREENSHOT_PATH = LOG_DIR / "intelligence_graph_page.png"
REPORT_PATH = LOG_DIR / "intelligence_graph_live_report.md"

BACKEND_BASE = "http://127.0.0.1:8000"
FRONTEND_BASE = "http://127.0.0.1:3000"
HTTP = requests.Session()
HTTP.trust_env = False


@dataclass
class StartResult:
    backend_pid: Optional[int]
    frontend_pid: Optional[int]
    backend_ready: bool
    frontend_ready: bool


def _run(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )
    return (result.stdout or "") + (result.stderr or "")


def _find_listen_pid(port: int) -> Optional[int]:
    text = _run(["netstat", "-ano", "-p", "tcp"])
    pattern = re.compile(rf"^\s*TCP\s+\S+:{port}\s+\S+\s+LISTENING\s+(\d+)\s*$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return None
    return int(m.group(1))


def _kill_pid(pid: int) -> None:
    subprocess.run(
        ["taskkill", "/F", "/PID", str(pid)],
        text=True,
        capture_output=True,
        check=False,
    )


def _clear_ports() -> None:
    for port in (8000, 3000):
        pid = _find_listen_pid(port)
        if pid:
            _kill_pid(pid)
            time.sleep(1)


def _wait_http(url: str, timeout_sec: int = 120) -> bool:
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            resp = HTTP.get(url, timeout=2)
            if resp.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def _start_services() -> StartResult:
    py = sys.executable
    backend_out = open(BACKEND_OUT, "w", encoding="utf-8", errors="ignore")
    backend_err = open(BACKEND_ERR, "w", encoding="utf-8", errors="ignore")
    frontend_out = open(FRONTEND_OUT, "w", encoding="utf-8", errors="ignore")
    frontend_err = open(FRONTEND_ERR, "w", encoding="utf-8", errors="ignore")

    backend_proc = subprocess.Popen(
        [py, "main.py"],
        cwd=str(BACKEND_DIR),
        stdout=backend_out,
        stderr=backend_err,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    npm_cmd = r"C:\Program Files\nodejs\npm.cmd"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000"],
        cwd=str(FRONTEND_DIR),
        stdout=frontend_out,
        stderr=frontend_err,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    backend_ready = any(
        _wait_http(url, timeout_sec=120)
        for url in (
            f"{BACKEND_BASE}/health/live",
            f"{BACKEND_BASE}/api/v1/health/live",
            f"{BACKEND_BASE}/docs",
        )
    )
    if not backend_ready and _find_listen_pid(8000):
        backend_ready = True

    frontend_ready = any(
        _wait_http(url, timeout_sec=60)
        for url in (
            FRONTEND_BASE,
            f"{FRONTEND_BASE}/admin/intelligence/graph",
        )
    )
    if not frontend_ready and _find_listen_pid(3000):
        frontend_ready = True

    return StartResult(
        backend_pid=backend_proc.pid,
        frontend_pid=frontend_proc.pid,
        backend_ready=backend_ready,
        frontend_ready=frontend_ready,
    )


def _login_get_token() -> str:
    resp = HTTP.post(
        f"{BACKEND_BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    token = ((data or {}).get("data") or {}).get("access_token")
    if not token:
        raise RuntimeError(f"Login succeeded but token missing: {data}")
    return token


def _fetch_api_sample(token: str) -> dict:
    url = (
        f"{BACKEND_BASE}/api/v1/admin/intelligence/collection/graph/overview"
        "?days=7&limit=300&include_prediction=true"
    )
    resp = HTTP.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=40)
    resp.raise_for_status()
    body = resp.json()
    sample = {
        "request": {
            "url": url,
            "method": "GET",
            "status_code": resp.status_code,
        },
        "response_stats": ((body or {}).get("data") or {}).get("stats") or {},
        "response_network_metrics": ((body or {}).get("data") or {}).get("network_metrics") or {},
        "response_top_nodes": (((body or {}).get("data") or {}).get("top_nodes") or [])[:5],
        "response_source_stats": (((body or {}).get("data") or {}).get("source_stats") or [])[:5],
        "response_type_stats": (((body or {}).get("data") or {}).get("type_stats") or [])[:5],
        "raw_response": body,
    }
    API_SAMPLE_JSON.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
    return sample


def _capture_screenshot(token: str) -> dict:
    js = f"""
    const {{ chromium }} = require('playwright');
    (async () => {{
      const browser = await chromium.launch({{ headless: true }});
      const page = await browser.newPage({{ viewport: {{ width: 1600, height: 1000 }} }});
      const routerWarns = [];
      const errors = [];

      page.on('console', (msg) => {{
        const t = msg.text();
        if (msg.type() === 'warning' && t.includes('No match found for location')) routerWarns.push(t);
        if (msg.type() === 'error') errors.push(t);
      }});

      await page.addInitScript((accessToken) => {{
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('token', accessToken);
        localStorage.setItem('admin_token', accessToken);
        localStorage.setItem('admin_user', JSON.stringify({{ id: 1, username: 'admin', role: 'admin' }}));
      }}, {json.dumps(token)});

      await page.goto('{FRONTEND_BASE}/admin/intelligence/graph', {{ waitUntil: 'networkidle', timeout: 90000 }});
      await page.waitForTimeout(2500);
      const h2 = await page.locator('h2').first().textContent().catch(() => null);
      await page.screenshot({{ path: {json.dumps(str(SCREENSHOT_PATH))}, fullPage: true }});
      console.log(JSON.stringify({{
        url: page.url(),
        title: await page.title(),
        h2,
        router_warn_count: routerWarns.length,
        error_count: errors.length
      }}));
      await browser.close();
    }})().catch((e) => {{
      console.error(e && e.stack ? e.stack : String(e));
      process.exit(1);
    }});
    """
    proc = subprocess.run(
        ["node", "-e", js],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Playwright failed: {proc.stderr or proc.stdout}")
    line = (proc.stdout or "").strip().splitlines()[-1]
    return json.loads(line)


def _write_report(start_result: StartResult, api_sample: dict, shot_meta: dict) -> None:
    lines = [
        "# Intelligence Graph Live Report",
        "",
        f"- Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Backend PID: {start_result.backend_pid}",
        f"- Frontend PID: {start_result.frontend_pid}",
        f"- Backend ready: {start_result.backend_ready}",
        f"- Frontend ready: {start_result.frontend_ready}",
        "",
        "## Screenshot",
        "",
        f"- Path: `{SCREENSHOT_PATH}`",
        f"- Page URL: `{shot_meta.get('url')}`",
        f"- H2: `{shot_meta.get('h2')}`",
        f"- Router warnings: `{shot_meta.get('router_warn_count')}`",
        f"- Console errors: `{shot_meta.get('error_count')}`",
        "",
        "## API Sample",
        "",
        f"- Path: `{API_SAMPLE_JSON}`",
        f"- Request status: `{api_sample.get('request', {}).get('status_code')}`",
        f"- Stats: `{json.dumps(api_sample.get('response_stats', {}), ensure_ascii=False)}`",
        f"- Network metrics: `{json.dumps(api_sample.get('response_network_metrics', {}), ensure_ascii=False)}`",
        "",
        "## Service Logs",
        "",
        f"- Backend stdout: `{BACKEND_OUT}`",
        f"- Backend stderr: `{BACKEND_ERR}`",
        f"- Frontend stdout: `{FRONTEND_OUT}`",
        f"- Frontend stderr: `{FRONTEND_ERR}`",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    _clear_ports()
    start_result = _start_services()

    if not start_result.backend_ready or not start_result.frontend_ready:
        print(
            json.dumps(
                {
                    "ok": False,
                    "stage": "startup",
                    "backend_ready": start_result.backend_ready,
                    "frontend_ready": start_result.frontend_ready,
                    "backend_log": str(BACKEND_OUT),
                    "backend_err": str(BACKEND_ERR),
                    "frontend_log": str(FRONTEND_OUT),
                    "frontend_err": str(FRONTEND_ERR),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    token = _login_get_token()
    api_sample = _fetch_api_sample(token)
    shot_meta = _capture_screenshot(token)
    _write_report(start_result, api_sample, shot_meta)

    print(
        json.dumps(
            {
                "ok": True,
                "report": str(REPORT_PATH),
                "screenshot": str(SCREENSHOT_PATH),
                "api_sample": str(API_SAMPLE_JSON),
                "backend_pid": start_result.backend_pid,
                "frontend_pid": start_result.frontend_pid,
                "screenshot_meta": shot_meta,
                "api_stats": api_sample.get("response_stats", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
