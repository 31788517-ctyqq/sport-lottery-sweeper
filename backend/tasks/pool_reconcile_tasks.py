#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Celery tasks for pool reconcile workflow."""

from backend.config import settings
from backend.services.pool_reconciler_service import PoolReconcilerService
from backend.tasks.simple_celery import celery


@celery.task(name="pool.reconcile")
def reconcile_pool(dry_run: bool = True) -> dict:
    service = PoolReconcilerService()
    try:
        return service.reconcile(dry_run=dry_run)
    finally:
        service.close()


@celery.task(name="pool.reconcile.scheduled")
def scheduled_reconcile_pool() -> dict:
    service = PoolReconcilerService()
    try:
        return service.reconcile(dry_run=bool(settings.POOL_RECONCILE_DRY_RUN))
    finally:
        service.close()
