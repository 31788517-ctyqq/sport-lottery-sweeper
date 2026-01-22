#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Celery配置 - 避免循环导入
"""

import os
import sys
from celery import Celery

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建简单的Celery实例
celery = Celery(
    'simple_crawler',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'backend.tasks.500wang_scheduler'
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

print("✅ 简化Celery配置加载成功")