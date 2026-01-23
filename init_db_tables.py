#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库表初始化脚本
用于创建所有必需的数据库表
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from backend.models.base import Base
from backend.models.user import User, Role, Permission
from backend.models.match import Match, League, Team, Player, MatchLineup, MatchEvent
from backend.models.odds import *
from backend.models.intelligence import Intelligence
from backend.models.system_config import SystemConfig
from backend.models.crawler_config import CrawlerConfig
from backend.models.crawler_logs import *
from backend.models.crawler_tasks import *
from backend.models.crawler_alert_records import *
from backend.models.sp_core import *
from backend.config import settings


def create_tables():
    """创建所有数据库表"""
    # 使用同步引擎创建表
    sync_engine = create_engine(settings.DATABASE_URL, echo=True)
    Base.metadata.create_all(bind=sync_engine)
    print('✅ 数据库表创建成功！')


if __name__ == "__main__":
    create_tables()