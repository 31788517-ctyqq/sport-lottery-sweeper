from __future__ import annotations

import asyncio
from datetime import timedelta

from fastapi.testclient import TestClient

from backend.core.cache_manager import MemoryCache
from backend.core.security import create_access_token, verify_token
from backend.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "healthy"


def test_health_live_endpoint():
    with TestClient(app) as client:
        response = client.get("/health/live")
    assert response.status_code == 200


def test_access_token_roundtrip():
    token = create_access_token(
        "release-smoke-user",
        expires_delta=timedelta(minutes=5),
        additional_claims={"scope": "smoke"},
    )
    payload = verify_token(token, token_type="access")
    assert payload["sub"] == "release-smoke-user"
    assert payload["type"] == "access"
    assert payload["scope"] == "smoke"


def test_memory_cache_roundtrip():
    cache = MemoryCache()

    async def _run():
        await cache.set("release:smoke:key", {"ok": True}, ttl=60)
        value = await cache.get("release:smoke:key")
        stats = await cache.get_stats()
        return value, stats

    value, stats = asyncio.run(_run())
    assert value == {"ok": True}
    assert "release:smoke:key" in stats["keys"]
