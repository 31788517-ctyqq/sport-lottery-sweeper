from __future__ import annotations

import copy

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.v1.admin import entity_mapping as entity_mapping_api
from backend.config.entity_mappings import TEAM_MAPPINGS


def _build_client() -> TestClient:
    app = FastAPI()
    app.include_router(entity_mapping_api.router, prefix="/api/v1")
    return TestClient(app)


def test_get_team_mappings_success():
    client = _build_client()
    response = client.get("/api/v1/entity-mapping/mappings/team")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "real_madrid" in body["data"]


def test_standardize_match_data_success():
    client = _build_client()
    payload = {
        "home_team": "Real Madrid",
        "away_team": "FC Barcelona",
        "league": "La Liga",
        "match_time": "2026-03-15T20:00:00",
    }
    response = client.post(
        "/api/v1/entity-mapping/matches/standardize",
        params={"source_id": "sports_data_api"},
        json=payload,
    )
    assert response.status_code == 200
    body = response.json()
    standardized = body["standardized_data"]
    assert standardized["home_team_id"] == "real_madrid"
    assert standardized["away_team_id"] == "barcelona"
    assert standardized["league_id"] == "la_liga"


def test_verify_all_endpoint_uses_service(monkeypatch):
    client = _build_client()
    calls = []

    async def _stub(entity_type: str = "all"):
        calls.append(entity_type)
        return {
            "teams": {},
            "leagues": {},
            "summary": {"total": 0, "valid": 0, "invalid": 0, "needs_update": 0},
        }

    monkeypatch.setattr(entity_mapping_api.official_info_service, "verify_all_official_links", _stub)

    response = client.post("/api/v1/entity-mapping/official-info/verify-all", params={"entity_type": "teams"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["summary"]["total"] == 0
    assert calls == ["teams"]


def test_summary_endpoint_does_not_block_on_remote_check(monkeypatch):
    client = _build_client()

    async def _failing_stub(entity_type: str = "all"):
        raise RuntimeError("should not be called when force_verify=false")

    monkeypatch.setattr(entity_mapping_api.official_info_service, "verify_all_official_links", _failing_stub)

    response = client.get("/api/v1/entity-mapping/official-info/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["summary"]["total"] >= 1


def test_discover_all_endpoint_uses_service(monkeypatch):
    client = _build_client()
    calls = []

    async def _stub(entity_type: str, entity_id: str):
        calls.append((entity_type, entity_id))
        return {"website": f"https://example.com/{entity_id}", "confidence": 0.9}

    monkeypatch.setattr(entity_mapping_api.official_info_service, "discover_official_links", _stub)

    response = client.post("/api/v1/entity-mapping/official-info/discover-all", params={"entity_type": "teams"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["summary"]["total"] == len(TEAM_MAPPINGS)
    assert len(calls) == len(TEAM_MAPPINGS)


def test_update_official_info_respects_verified_false():
    client = _build_client()
    entity_id = "real_madrid"
    backup = copy.deepcopy(TEAM_MAPPINGS[entity_id]["official_info"])
    try:
        response = client.put(
            f"/api/v1/entity-mapping/official-info/team/{entity_id}",
            json={"website": "https://www.realmadrid.com/", "verified": False},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert TEAM_MAPPINGS[entity_id]["official_info"]["verified"] is False
    finally:
        TEAM_MAPPINGS[entity_id]["official_info"] = backup
