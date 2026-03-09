#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from core.database import SessionLocal
from models.crawler_config import CrawlerConfig

def main():
    db = SessionLocal()
    try:
        exists = db.query(CrawlerConfig).filter(CrawlerConfig.source_name == "500.com足球竞彩").first()
        if exists:
            print("500.com配置已存在，跳过插入")
            return
        cfg = CrawlerConfig(
            source_name="500.com足球竞彩",
            url_pattern="https://trade.500.com/jczq/",
            interval=4,
            enabled=1
        )
        db.add(cfg)
        db.commit()
        print("✅ 500.com爬虫配置已成功插入数据库")
    except Exception as e:
        db.rollback()
        print(f"❌ 插入失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
