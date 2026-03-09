from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings
from backend.models.base import Base
from backend.models.data_source_headers import DataSourceHeader
from backend.models.data_sources import DataSource
from backend.models.headers import RequestHeader
from backend.models.ip_pool import IPPool
from backend.services.pool_reconciler_service import PoolReconcilerService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
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
    try:
        yield session
    finally:
        session.close()


def _seed_capacity_data(session):
    session.add_all(
        [
            IPPool(ip="1.1.1.1", port=8080, protocol="http", status="active", created_at=datetime.utcnow()),
            IPPool(ip="2.2.2.2", port=8080, protocol="http", status="inactive", created_at=datetime.utcnow()),
            IPPool(ip="3.3.3.3", port=8080, protocol="http", status="cooling", created_at=datetime.utcnow()),
        ]
    )
    session.add(
        DataSource(
            name="100qiu",
            type="100qiu",
            status=1,
            url="https://m.100qiu.com/api/list",
            config="{}",
            source_id="DS001",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    session.add_all(
        [
            RequestHeader(
                domain="m.100qiu.com",
                name="User-Agent",
                value="ua-1",
                type="general",
                priority=2,
                status="enabled",
                usage_count=30,
                success_count=10,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            RequestHeader(
                domain="m.100qiu.com",
                name="Accept",
                value="application/json",
                type="general",
                priority=1,
                status="enabled",
                usage_count=5,
                success_count=5,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
    )
    session.commit()


def test_pool_reconcile_build_plan_has_gap(db_session, monkeypatch):
    monkeypatch.setattr(settings, "IP_POOL_TARGET_ACTIVE", 4)
    monkeypatch.setattr(settings, "IP_POOL_TARGET_STANDBY", 2)
    monkeypatch.setattr(settings, "HEADER_POOL_MIN_ACTIVE_PER_DOMAIN", 4)
    monkeypatch.setattr(settings, "HEADER_POOL_HEADERS_PER_ACTIVE_IP", 2)
    _seed_capacity_data(db_session)

    service = PoolReconcilerService(db_session)
    plan = service.build_plan()

    assert plan["ip_capacity"]["active"] == 1
    assert plan["ip_capacity"]["active_gap"] == 3
    assert plan["headers_capacity"]["domains_count"] >= 1
    domain_map = {x["domain"]: x for x in plan["headers_capacity"]["domains"]}
    assert "m.100qiu.com" in domain_map
    assert domain_map["m.100qiu.com"]["gap"] >= 1


def test_pool_reconcile_apply_executes_ip_replenish(db_session, monkeypatch):
    monkeypatch.setattr(settings, "IP_POOL_TARGET_ACTIVE", 2)
    monkeypatch.setattr(settings, "IP_POOL_AUTO_REPLENISH_ENABLED", True)
    monkeypatch.setattr(settings, "HEADER_POOL_AUTO_REPLENISH_ENABLED", False)
    db_session.add(IPPool(ip="8.8.8.8", port=8080, protocol="http", status="active", created_at=datetime.utcnow()))
    db_session.commit()

    service = PoolReconcilerService(db_session)
    service._replenish_ip_pool = lambda gap: {"success": True, "gap": gap}
    result = service.reconcile(dry_run=False)

    assert result["dry_run"] is False
    assert result["risk_level"] in {"low", "medium", "high"}
    assert "ip_gap" in result
    assert "header_gap" in result
    assert result["execution"]["ip"]["success"] is True
