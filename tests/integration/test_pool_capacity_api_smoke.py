from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.v1.admin.headers_management import router as headers_router
from backend.api.v1.ip_pool_adapter import router as ip_pool_router
from backend.database import get_db
from backend.models.base import Base
from backend.models.data_source_headers import DataSourceHeader
from backend.models.data_sources import DataSource
from backend.models.headers import RequestHeader
from backend.models.ip_pool import IPPool


@pytest.fixture
def api_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(
        engine,
        tables=[
            IPPool.__table__,
            RequestHeader.__table__,
            DataSource.__table__,
            DataSourceHeader.__table__,
        ],
    )
    session = Session()
    session.add_all(
        [
            IPPool(ip="10.0.0.1", port=8080, protocol="http", status="active", created_at=datetime.utcnow()),
            IPPool(ip="10.0.0.2", port=8080, protocol="http", status="testing", created_at=datetime.utcnow()),
            RequestHeader(
                domain="m.100qiu.com",
                name="User-Agent",
                value="ua-a",
                type="general",
                priority=3,
                status="enabled",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            RequestHeader(
                domain="m.100qiu.com",
                name="Accept",
                value="application/json",
                type="general",
                priority=2,
                status="enabled",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            DataSource(
                name="100qiu_source",
                type="100qiu",
                status=1,
                url="https://m.100qiu.com/api/list",
                config="{}",
                source_id="DS100",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
    )
    session.commit()

    app = FastAPI()
    app.include_router(ip_pool_router, prefix="/api/v1/admin")
    app.include_router(headers_router, prefix="/api/v1/admin")

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    try:
        yield client, session
    finally:
        session.close()


def test_ip_pool_stats_contains_capacity_fields(api_client):
    client, _ = api_client
    resp = client.get("/api/v1/admin/ip-pools/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "activeTarget" in body["data"]
    assert "standbyTarget" in body["data"]
    assert "activeGap" in body["data"]
    assert "capacity" in body["data"]


def test_ip_pool_reconcile_endpoint_smoke(api_client):
    client, _ = api_client
    resp = client.post("/api/v1/admin/ip-pools/reconcile", json={"dry_run": True})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert body["data"]["dry_run"] is True
    assert "risk_level" in body["data"]
    assert "actions" in body["data"]


def test_headers_stats_contains_domain_capacity(api_client):
    client, _ = api_client
    resp = client.get("/api/v1/admin/headers/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "domain_stats" in body["data"]
    assert "capacity" in body["data"]
    assert body["data"]["capacity"]["domains_count"] >= 1
    assert "bindings_coverage" in body["data"]["capacity"]


def test_auto_bind_headers_to_data_source(api_client):
    client, session = api_client
    resp = client.post(
        "/api/v1/admin/headers/auto-bind/data-source",
        json={"dataSourceId": 1, "dryRun": False, "minBindings": 2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["bound_count"] >= 1

    bound = session.query(DataSourceHeader).filter(DataSourceHeader.data_source_id == 1).all()
    assert len(bound) >= 1
