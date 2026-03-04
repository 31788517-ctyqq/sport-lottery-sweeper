"""Pool reconcile service for IP/Headers capacity planning and execution."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.models.data_source_headers import DataSourceHeader
from backend.models.data_sources import DataSource
from backend.models.headers import RequestHeader
from backend.models.ip_pool import IPPool


def _safe_success_rate(usage_count: int, success_count: int) -> float:
    if usage_count <= 0:
        return 100.0
    return round((success_count / usage_count) * 100, 2)


def _extract_domain(raw_url: Optional[str]) -> str:
    if not raw_url:
        return "__global__"
    try:
        host = (urlparse(raw_url).hostname or "").strip().lower()
        return host or "__global__"
    except Exception:
        return "__global__"


class PoolReconcilerService:
    """Build and optionally execute pool reconcile plans."""

    ACTIVE_IP_STATUSES = {"active"}
    STANDBY_IP_STATUSES = {"inactive", "pending"}
    TESTING_IP_STATUSES = {"testing"}
    COOLING_IP_STATUSES = {"cooling"}

    def __init__(self, db: Optional[Session] = None) -> None:
        self._external_db = db is not None
        self.db = db or SessionLocal()

    def close(self) -> None:
        if not self._external_db:
            self.db.close()

    def _ip_capacity_snapshot(self) -> Dict[str, int]:
        rows = self.db.query(IPPool.status).all()
        bucket = defaultdict(int)
        for (status,) in rows:
            bucket[(status or "").lower()] += 1

        active = sum(bucket[s] for s in self.ACTIVE_IP_STATUSES)
        standby = sum(bucket[s] for s in self.STANDBY_IP_STATUSES)
        testing = sum(bucket[s] for s in self.TESTING_IP_STATUSES)
        cooling = sum(bucket[s] for s in self.COOLING_IP_STATUSES)
        banned = bucket["banned"]
        total = sum(bucket.values())

        return {
            "total": total,
            "active": active,
            "standby": standby,
            "testing": testing,
            "cooling": cooling,
            "banned": banned,
            "active_target": max(0, int(settings.IP_POOL_TARGET_ACTIVE)),
            "standby_target": max(0, int(settings.IP_POOL_TARGET_STANDBY)),
            "active_gap": max(0, int(settings.IP_POOL_TARGET_ACTIVE) - active),
            "standby_gap": max(0, int(settings.IP_POOL_TARGET_STANDBY) - standby),
        }

    def _headers_domain_snapshot(self, active_ip_count: int) -> Dict[str, Dict[str, Any]]:
        by_domain: Dict[str, Dict[str, Any]] = {}

        rows = self.db.query(RequestHeader).all()
        grouped: Dict[str, List[RequestHeader]] = defaultdict(list)
        for row in rows:
            grouped[(row.domain or "__global__").strip().lower() or "__global__"].append(row)

        min_usage = int(settings.HEADER_POOL_LOW_QUALITY_MIN_USAGE)
        low_success = float(settings.HEADER_POOL_LOW_QUALITY_SUCCESS_RATE)
        target_per_domain = max(
            int(settings.HEADER_POOL_MIN_ACTIVE_PER_DOMAIN),
            int(active_ip_count * int(settings.HEADER_POOL_HEADERS_PER_ACTIVE_IP)),
        )

        for domain, headers in grouped.items():
            enabled = [x for x in headers if (x.status or "").lower() == "enabled"]
            active = len(enabled)
            low_quality = 0
            for header in enabled:
                usage = int(header.usage_count or 0)
                success = int(header.success_count or 0)
                if usage < min_usage:
                    continue
                if _safe_success_rate(usage, success) < low_success:
                    low_quality += 1

            by_domain[domain] = {
                "domain": domain,
                "total": len(headers),
                "enabled": active,
                "disabled": len(headers) - active,
                "low_quality": low_quality,
                "target": target_per_domain,
                "gap": max(0, target_per_domain - active),
            }

        # Ensure existing source domains are represented even if they have no headers.
        for source in self.db.query(DataSource).all():
            domain = _extract_domain(source.url)
            if domain not in by_domain:
                by_domain[domain] = {
                    "domain": domain,
                    "total": 0,
                    "enabled": 0,
                    "disabled": 0,
                    "low_quality": 0,
                    "target": target_per_domain,
                    "gap": target_per_domain,
                }

        return by_domain

    def build_plan(self) -> Dict[str, Any]:
        ip_capacity = self._ip_capacity_snapshot()
        headers_by_domain = self._headers_domain_snapshot(ip_capacity["active"])

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "dry_run_default": bool(settings.POOL_RECONCILE_DRY_RUN),
            "ip_capacity": ip_capacity,
            "headers_capacity": {
                "domains": sorted(headers_by_domain.values(), key=lambda x: x["domain"]),
                "domains_count": len(headers_by_domain),
            },
        }

    def _compute_fetch_pages(self, active_gap: int) -> int:
        expected_per_page = max(1, int(settings.IP_POOL_EXPECTED_ACTIVE_PER_FETCH_PAGE))
        return max(1, math.ceil(active_gap / expected_per_page))

    def _replenish_ip_pool(self, active_gap: int) -> Dict[str, Any]:
        from backend.tasks.ip_pool_refresh import refresh_ip_pool

        fetch_pages = self._compute_fetch_pages(active_gap)
        return refresh_ip_pool(
            fetch_pages=fetch_pages,
            target_active=int(settings.IP_POOL_TARGET_ACTIVE),
            current_active=max(0, int(settings.IP_POOL_TARGET_ACTIVE) - active_gap),
        )

    def _build_headers_actions(self, domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []
        for row in domains:
            if row["gap"] > 0:
                actions.append(
                    {
                        "action": "headers_pool.replenish",
                        "domain": row["domain"],
                        "gap": row["gap"],
                        "target": row["target"],
                        "enabled": row["enabled"],
                    }
                )
        return actions

    def _evaluate_risk_level(self, ip_capacity: Dict[str, Any], header_domains: List[Dict[str, Any]]) -> str:
        active_gap = int(ip_capacity.get("active_gap", 0))
        standby_gap = int(ip_capacity.get("standby_gap", 0))
        header_gap_domains = sum(1 for d in header_domains if int(d.get("gap", 0)) > 0)
        low_quality_total = sum(int(d.get("low_quality", 0)) for d in header_domains)

        if active_gap > 0 or header_gap_domains >= 3:
            return "high"
        if standby_gap > 0 or low_quality_total > 0 or header_gap_domains > 0:
            return "medium"
        return "low"

    def reconcile(self, *, dry_run: bool = True) -> Dict[str, Any]:
        plan = self.build_plan()
        ip_capacity = plan["ip_capacity"]
        header_domains = plan["headers_capacity"]["domains"]
        actions: List[Dict[str, Any]] = []
        execution: Dict[str, Any] = {"ip": None, "headers": None}

        if ip_capacity["active_gap"] > 0:
            actions.append(
                {
                    "action": "ip_pool.replenish",
                    "active_gap": ip_capacity["active_gap"],
                    "standby_gap": ip_capacity["standby_gap"],
                    "fetch_pages_hint": self._compute_fetch_pages(ip_capacity["active_gap"]),
                }
            )

        actions.extend(self._build_headers_actions(header_domains))

        if not dry_run:
            if ip_capacity["active_gap"] > 0 and settings.IP_POOL_AUTO_REPLENISH_ENABLED:
                execution["ip"] = self._replenish_ip_pool(ip_capacity["active_gap"])
            if settings.HEADER_POOL_AUTO_REPLENISH_ENABLED:
                from backend.services.headers_pool_service import HeadersPoolService

                headers_service = HeadersPoolService(self.db)
                execution["headers"] = headers_service.ensure_minimum_capacity(dry_run=False)

        risk_level = self._evaluate_risk_level(ip_capacity, header_domains)
        recommended_actions = [str(a.get("action")) for a in actions]

        return {
            "timestamp": plan["timestamp"],
            "dry_run": dry_run,
            "risk_level": risk_level,
            "recommended_actions": recommended_actions,
            "ip_gap": {
                "active_gap": int(ip_capacity.get("active_gap", 0)),
                "standby_gap": int(ip_capacity.get("standby_gap", 0)),
            },
            "header_gap": {
                "domains_with_gap": sum(1 for d in header_domains if int(d.get("gap", 0)) > 0),
                "total_gap": sum(int(d.get("gap", 0)) for d in header_domains),
            },
            "actions": actions,
            "plan": plan,
            "execution": execution,
        }

    def summarize_for_api(self) -> Dict[str, Any]:
        plan = self.build_plan()
        ip = plan["ip_capacity"]
        domains = plan["headers_capacity"]["domains"]
        low_quality_total = sum(int(x["low_quality"]) for x in domains)

        return {
            "ip": ip,
            "headers": {
                "domains_count": len(domains),
                "low_quality_total": low_quality_total,
                "domains": domains,
            },
        }

    @staticmethod
    def resolve_data_source_header_coverage(db: Session) -> Dict[str, Any]:
        source_total = db.query(DataSource.id).count()
        bound_source_total = (
            db.query(DataSourceHeader.data_source_id)
            .group_by(DataSourceHeader.data_source_id)
            .count()
        )
        return {
            "sources_total": int(source_total),
            "sources_with_header_binding": int(bound_source_total),
            "coverage_rate": round((bound_source_total / source_total) * 100, 2) if source_total else 100.0,
        }
