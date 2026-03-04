"""
Entity-mapping and official-info API smoke test.
"""

from __future__ import annotations

import sys
import time
import os
from typing import Callable, Tuple

import requests

BASE_URL = os.getenv("API_TEST_BASE_URL", "http://localhost:8000/api/v1")
REQUEST_TIMEOUT_SECONDS = 15
SESSION = requests.Session()
SESSION.trust_env = False


def _safe_print(message: str) -> None:
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode("ascii"))


def _run(name: str, test_func: Callable[[], bool]) -> bool:
    _safe_print(f"\n[TEST] {name}")
    try:
        passed = test_func()
    except Exception as exc:  # pragma: no cover - smoke script
        _safe_print(f"[FAIL] {name}: {exc}")
        return False
    _safe_print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    return passed


def test_health_check() -> bool:
    response = SESSION.get(f"{BASE_URL}/health/live", timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code != 200:
        return False
    body = response.json()
    return body.get("status") == "healthy"


def test_get_team_mappings() -> bool:
    response = SESSION.get(f"{BASE_URL}/entity-mapping/mappings/team", timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code != 200:
        return False
    body = response.json()
    data = body.get("data") or {}
    _safe_print(f"Team mappings count: {len(data)}")
    return body.get("status") == "success" and "real_madrid" in data


def test_get_league_mappings() -> bool:
    response = SESSION.get(f"{BASE_URL}/entity-mapping/mappings/league", timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code != 200:
        return False
    body = response.json()
    data = body.get("data") or {}
    _safe_print(f"League mappings count: {len(data)}")
    return body.get("status") == "success" and "la_liga" in data


def test_standardize_match_data() -> bool:
    payload = {
        "home_team": "皇家马德里",
        "away_team": "巴塞罗那",
        "match_time": "2026-03-15T20:00:00",
        "league": "西甲联赛",
    }
    response = SESSION.post(
        f"{BASE_URL}/entity-mapping/matches/standardize",
        params={"source_id": "sports_data_api"},
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        return False
    body = response.json()
    standardized = body.get("standardized_data") or {}
    return standardized.get("home_team_id") == "real_madrid" and standardized.get("away_team_id") == "barcelona"


def test_get_official_info_summary() -> bool:
    response = SESSION.get(f"{BASE_URL}/entity-mapping/official-info/summary", timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code != 200:
        return False
    body = response.json()
    summary = (body.get("data") or {}).get("summary") or {}
    _safe_print(f"Summary total={summary.get('total')} valid={summary.get('valid')} invalid={summary.get('invalid')}")
    return body.get("status") == "success" and isinstance(summary.get("total"), int)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    _safe_print("Starting API smoke tests...")
    time.sleep(1)

    tests: Tuple[Tuple[str, Callable[[], bool]], ...] = (
        ("Health check", test_health_check),
        ("Get team mappings", test_get_team_mappings),
        ("Get league mappings", test_get_league_mappings),
        ("Standardize match data", test_standardize_match_data),
        ("Official-info summary", test_get_official_info_summary),
    )

    passed = sum(1 for name, test_func in tests if _run(name, test_func))
    total = len(tests)
    _safe_print(f"\nResult: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
