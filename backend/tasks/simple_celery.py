#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Celery配置 - 避免循环导入
"""

import os
import sys
from celery import Celery
from celery.schedules import crontab
from backend.config import settings

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建简单的Celery实例
celery = Celery(
    'simple_crawler',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'backend.tasks.500wang_scheduler',
        'backend.tasks.ip_pool_refresh',
        'backend.tasks.pool_reconcile_tasks',
    ]
)

# 基本配置
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

if settings.POOL_RECONCILE_ENABLED:
    celery.conf.beat_schedule = {
        **getattr(celery.conf, "beat_schedule", {}),
        "pool-reconcile-every-minute": {
            "task": "pool.reconcile.scheduled",
            "schedule": max(10, int(settings.POOL_RECONCILE_INTERVAL_SECONDS)),
        },
        "ip-pool-refresh-every-10-minutes": {
            "task": "ip_pool.refresh",
            "schedule": crontab(minute="*/10"),
        },
    }

print("[celery] simple configuration loaded")
