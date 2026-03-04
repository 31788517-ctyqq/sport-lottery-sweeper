#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速插入500.com爬虫配置到crawler_configs表"""
import sys
import os
from datetime import datetime

# 添加backend到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from core.database import SessionLocal
from models.crawler_config import CrawlerConfig

def insert_500_config():
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(CrawlerConfig).filter(CrawlerConfig.config_key == '500com_jczq').first()
        if existing:
            print("500.com配置已存在，跳过插入")
            return
        
        config = CrawlerConfig(
            name="500.com足球竞彩",
            config_key="500com_jczq",
            config_value='{"source_url": "https://trade.500.com/jczq/", "crawler_type": "daily_match", "days": 3}',
            config_type="source",
            description="500.com竞彩足球3天赛程抓取配置",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(config)
        db.commit()
        print("✅ 500.com爬虫配置已成功插入数据库")
    except Exception as e:
        db.rollback()
        print(f"❌ 插入失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_500_config()
