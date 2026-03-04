"""Headers pool lifecycle service (capacity, quality and auto binding)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.models.data_source_headers import DataSourceHeader
from backend.models.data_sources import DataSource
from backend.models.headers import RequestHeader

_DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
]


def _extract_domain(raw_url: Optional[str]) -> str:
    if not raw_url:
        return "__global__"
    try:
        host = (urlparse(raw_url).hostname or "").strip().lower()
        return host or "__global__"
    except Exception:
        return "__global__"


class HeadersPoolService:
    """Manage headers quality and capacity."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self._external_db = db is not None
        self.db = db or SessionLocal()

    def close(self) -> None:
        if not self._external_db:
            self.db.close()

    @staticmethod
    def _success_rate(item: RequestHeader) -> float:
        usage = int(item.usage_count or 0)
        success = int(item.success_count or 0)
        if usage <= 0:
            return 100.0
        return round(success / usage * 100, 2)

    def domain_stats(self) -> List[Dict[str, Any]]:
        enabled_only = [x for x in self.db.query(RequestHeader).all() if (x.status or "").lower() == "enabled"]
        domains = {}
        for item in enabled_only:
            domain = (item.domain or "__global__").strip().lower() or "__global__"
            domain_stat = domains.setdefault(
                domain,
                {"domain": domain, "enabled": 0, "low_quality": 0, "high_priority": 0},
            )
            domain_stat["enabled"] += 1
            if int(item.priority or 0) >= 3:
                domain_stat["high_priority"] += 1
            if (
                int(item.usage_count or 0) >= int(settings.HEADER_POOL_LOW_QUALITY_MIN_USAGE)
                and self._success_rate(item) < float(settings.HEADER_POOL_LOW_QUALITY_SUCCESS_RATE)
            ):
                domain_stat["low_quality"] += 1

        for source in self.db.query(DataSource).all():
            domain = _extract_domain(source.url)
            domains.setdefault(domain, {"domain": domain, "enabled": 0, "low_quality": 0, "high_priority": 0})

        target = int(settings.HEADER_POOL_MIN_ACTIVE_PER_DOMAIN)
        for item in domains.values():
            item["target"] = target
            item["gap"] = max(0, target - int(item["enabled"]))
        return sorted(domains.values(), key=lambda x: x["domain"])

    def ensure_minimum_capacity(self, *, dry_run: bool = True) -> Dict[str, Any]:
        stats = self.domain_stats()
        actions: List[Dict[str, Any]] = []
        created = 0

        for row in stats:
            gap = int(row["gap"])
            if gap <= 0:
                continue

            actions.append({"domain": row["domain"], "create_count": gap})
            if dry_run:
                continue

            for idx in range(gap):
                ua = _DEFAULT_USER_AGENTS[idx % len(_DEFAULT_USER_AGENTS)]
                new_header = RequestHeader(
                    domain=row["domain"],
                    name="User-Agent",
                    value=ua,
                    type="general",
                    priority=2,
                    status="enabled",
                    remarks="auto_replenished",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                self.db.add(new_header)
                created += 1

        if not dry_run and created:
            self.db.commit()

        return {
            "dry_run": dry_run,
            "actions": actions,
            "created": created,
            "domains": stats,
        }

    def auto_bind_headers_for_data_source(
        self,
        *,
        data_source_id: int,
        domain: Optional[str] = None,
        dry_run: bool = True,
        min_bindings: Optional[int] = None,
    ) -> Dict[str, Any]:
        source = self.db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not source:
            return {"success": False, "message": "data_source_not_found", "bound_count": 0, "header_ids": []}

        resolved_domain = (domain or _extract_domain(source.url) or "__global__").strip().lower()
        min_required = max(1, int(min_bindings or settings.HEADER_POOL_MIN_BINDINGS_PER_SOURCE))

        candidates = (
            self.db.query(RequestHeader)
            .filter(RequestHeader.status == "enabled")
            .filter(RequestHeader.domain.in_([resolved_domain, "__global__"]))
            .order_by(RequestHeader.priority.desc(), RequestHeader.id.desc())
            .all()
        )

        selected = candidates[:min_required]
        selected_ids = [int(x.id) for x in selected]

        existing_ids = {
            x.header_id
            for x in self.db.query(DataSourceHeader)
            .filter(DataSourceHeader.data_source_id == data_source_id)
            .all()
        }
        pending_ids = [hid for hid in selected_ids if hid not in existing_ids]

        if not dry_run:
            for hid in pending_ids:
                self.db.add(
                    DataSourceHeader(
                        data_source_id=data_source_id,
                        header_id=hid,
                        enabled=True,
                    )
                )
            if pending_ids:
                self.db.commit()

        return {
            "success": True,
            "dry_run": dry_run,
            "data_source_id": data_source_id,
            "domain": resolved_domain,
            "required": min_required,
            "selected_count": len(selected_ids),
            "bound_count": len(pending_ids),
            "header_ids": selected_ids,
            "new_header_ids": pending_ids,
        }

