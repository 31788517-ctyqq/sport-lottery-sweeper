#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建500万彩票数据源的脚本
AI_WORKING: coder1 @2026-01-26 10:30:00 - 创建500万彩票数据源模拟用户操作
"""

import sys
sys.path.append('backend')

from sqlalchemy.orm import sessionmaker
from core.database import engine
from models.data_sources import DataSource as CrawlerSourceModel
import json
from datetime import datetime

# AI_WORKING: coder1 @2026-01-26 10:30:00 - 开始创建数据源
print("=" * 60)
print("模拟用户操作：在数据源管理页面新增数据源")
print("=" * 60)

Session = sessionmaker(bind=engine)
db = Session()

try:
    # 检查是否已存在
    existing = db.query(CrawlerSourceModel).filter(
        CrawlerSourceModel.name == "500万彩票"
    ).first()
    
    if existing:
        print(f"✓ 数据源'500万彩票'已存在，ID: {existing.id}")
        source_id = existing.id
    else:
        # 按用户要求创建：名称=500万彩票，网址=https://trade.500.com/jczq/
        print("✓ 正在创建数据源...")
        print("  - 名称：500万彩票")
        print("  - 网址：https://trade.500.com/jczq/")
        print("  - 类型：API")
        print("  - 状态：启用")
        print("  - 分类：竞彩赛程")
        print("  - 描述：500万彩票网竞彩足球比赛数据源")
        print("  - 自动抓取：是")
        print("  - 抓取间隔：3600秒")
        print("  - 优先级：高")
        
        new_source = CrawlerSourceModel(
            name="500万彩票",
            type="api",
            url="https://trade.500.com/jczq/",
            status=True,
            config=json.dumps({
                "baseUrl": "https://trade.500.com/jczq/",
                "description": "500万彩票网竞彩足球比赛数据源，提供最新的竞彩足球比赛信息",
                "category": "竞彩赛程",
                "auto_crawl": True,
                "crawl_interval": 3600,
                "priority": "high",
                "created_by": "user_operation",
                "created_at": datetime.now().isoformat()
            }, ensure_ascii=False),
            created_at=datetime.now()
        )
        
        db.add(new_source)
        db.commit()
        db.refresh(new_source)
        
        source_id = new_source.id
        print(f"✓ 数据源创建成功！ID: {source_id}")
    
    print("\n📋 数据源信息汇总：")
    print(f"   名称：500万彩票")
    print(f"   ID：{source_id}")
    print(f"   网址：https://trade.500.com/jczq/")
    print(f"   状态：启用")
    print(f"   分类：竞彩赛程")
    
finally:
    db.close()
    # AI_DONE: coder1 @2026-01-26 10:30:00
