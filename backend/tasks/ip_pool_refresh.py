#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP池自动刷新任务（Celery）
调用 crawler.dynamic_proxy_updater 抓取免费代理，写回 ip_pools 表
"""
from datetime import datetime

from backend.config import settings
from backend.tasks.simple_celery import celery
from backend.database import SessionLocal
from backend.models.ip_pool import IPPool
from crawler.ip_fetcher_multi import MultiSourceProxyFetcher


@celery.task(name="ip_pool.refresh")
def refresh_ip_pool(fetch_pages: int = 3, target_active: int | None = None, current_active: int | None = None) -> dict:
    """
    从 89ip 抓取代理并写入数据库
    :param fetch_pages: 抓取页数（每页约5条），默认3页
    """
    db = SessionLocal()
    added = 0
    updated = 0
    try:
        active_now = current_active
        if active_now is None:
            active_now = db.query(IPPool).filter(IPPool.status == "active").count()
        target = int(target_active) if target_active is not None else int(settings.IP_POOL_TARGET_ACTIVE)
        if target > int(active_now):
            gap = target - int(active_now)
            expected = max(1, int(settings.IP_POOL_EXPECTED_ACTIVE_PER_FETCH_PAGE))
            dynamic_pages = max(fetch_pages, (gap + expected - 1) // expected)
        else:
            dynamic_pages = fetch_pages

        fetcher = MultiSourceProxyFetcher()
        proxies = [{"ip": ip, "port": port, "protocol": "http"} for ip, port in fetcher.fetch_all()]

        for proxy in proxies:
            ip = proxy.get("ip")
            port = int(proxy.get("port")) if proxy.get("port") is not None else None
            if not ip or port is None:
                continue

            existing = (
                db.query(IPPool)
                .filter(IPPool.ip == ip, IPPool.port == port)
                .first()
            )
            latency = proxy.get("response_time")

            if existing:
                existing.last_checked = datetime.utcnow()
                if latency:
                    existing.latency_ms = int(latency)
                if not existing.source:
                    existing.source = "dynamic_proxy_updater"
                if existing.status in {"inactive", "pending", "testing", "cooling"}:
                    existing.status = "testing"
                updated += 1
            else:
                new_pool = IPPool(
                    ip=ip,
                    port=port,
                    protocol=proxy.get("protocol", "http"),
                    status="testing",
                    source="multi_source_fetcher",
                    latency_ms=int(latency) if latency else None,
                    last_checked=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(new_pool)
                added += 1

        db.commit()
        return {
            "success": True,
            "added": added,
            "updated": updated,
            "total": len(proxies),
            "fetch_pages": dynamic_pages,
            "active_before": int(active_now),
            "target_active": int(target),
        }
    except Exception as exc:
        db.rollback()
        return {"success": False, "error": str(exc)}
    finally:
        db.close()
