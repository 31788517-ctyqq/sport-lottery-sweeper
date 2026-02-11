#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表结构初始化脚本
用于创建或更新数据库表结构，确保数据源和爬虫配置的关联关系
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.database import engine, Base
from backend.models.data_sources import DataSource
from backend.models.crawler_config import CrawlerConfig
from backend.models.user import User
from backend.models.matches import FootballMatch
from backend.models.odds_companies import OddsCompany
from backend.models.sp_records import SPRecord
from backend.models.sp_modification_logs import SPModificationLog
from backend.models.admin_user import AdminUser
from backend.models.intelligence import Intelligence
from backend.models.log_entry import LogEntry

def init_db_tables():
    """初始化数据库表结构"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表结构初始化完成！")
        
        # 检查数据源表是否已存在
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'data_sources' in tables:
            print("✓ 数据源表已存在")
        else:
            print("⚠ 数据源表不存在")
            
        if 'crawler_configs' in tables:
            print("✓ 爬虫配置表已存在")
        else:
            print("⚠ 爬虫配置表不存在")
            
        # 检查source_id列是否存在
        columns = inspector.get_columns('crawler_configs')
        column_names = [col['name'] for col in columns]
        
        if 'source_id' in column_names:
            print("✓ crawler_configs表已包含source_id列")
        else:
            print("⚠ crawler_configs表缺少source_id列，需要手动添加")
            print("  请执行SQL: ALTER TABLE crawler_configs ADD COLUMN source_id INTEGER;")
            print("  并添加外键约束: ALTER TABLE crawler_configs ADD CONSTRAINT fk_crawler_configs_source_id FOREIGN KEY (source_id) REFERENCES data_sources(id);")
        
        return True
    except Exception as e:
        print(f"数据库表结构初始化失败: {e}")
        return False


def check_data_source_sync():
    """检查数据源和爬虫配置的同步状态"""
    from sqlalchemy.orm import sessionmaker
    from backend.models.data_sources import DataSource
    from backend.models.crawler_config import CrawlerConfig
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 统计数据源数量
        data_source_count = db.query(DataSource).count()
        print(f"数据源总数: {data_source_count}")
        
        # 统计爬虫配置数量
        crawler_config_count = db.query(CrawlerConfig).count()
        print(f"爬虫配置总数: {crawler_config_count}")
        
        # 统计已关联的爬虫配置数量
        linked_config_count = db.query(CrawlerConfig).filter(CrawlerConfig.source_id.isnot(None)).count()
        print(f"已关联数据源的爬虫配置数: {linked_config_count}")
        
        # 显示未关联的数据源
        unlinked_sources = db.query(DataSource).outerjoin(CrawlerConfig, DataSource.id == CrawlerConfig.source_id).filter(CrawlerConfig.id.is_(None)).all()
        if unlinked_sources:
            print(f"未关联爬虫配置的数据源 ({len(unlinked_sources)}):")
            for source in unlinked_sources:
                print(f"  - ID: {source.id}, Name: {source.name}")
        else:
            print("所有数据源均已关联爬虫配置")
        
        return {
            "data_source_count": data_source_count,
            "crawler_config_count": crawler_config_count,
            "linked_config_count": linked_config_count,
            "unlinked_sources": unlinked_sources
        }
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化数据库表结构...")
    
    # 初始化表结构
    success = init_db_tables()
    
    if success:
        print("\n检查数据源和爬虫配置同步状态...")
        check_data_source_sync()
        print("\n初始化完成！")
    else:
        print("\n初始化失败！")
        sys.exit(1)