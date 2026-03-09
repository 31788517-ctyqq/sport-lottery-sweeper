#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源与爬虫配置同步脚本
用于同步现有的数据源到爬虫配置
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from backend.database import engine
from backend.models.data_sources import DataSource
from backend.models.crawler_config import CrawlerConfig
from backend.crawler.management import create_crawler_config_from_data_source


def sync_existing_data_sources():
    """同步现有的数据源到爬虫配置"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 获取所有数据源
        data_sources = db.query(DataSource).all()
        print(f"找到 {len(data_sources)} 个数据源")
        
        created_configs = 0
        skipped_configs = 0
        
        for source in data_sources:
            # 检查是否已存在对应的爬虫配置
            existing_config = db.query(CrawlerConfig).filter(
                CrawlerConfig.source_id == source.id
            ).first()
            
            if not existing_config:
                print(f"为数据源 '{source.name}' (ID: {source.id}) 创建爬虫配置...")
                try:
                    create_crawler_config_from_data_source(db, source)
                    created_configs += 1
                except Exception as e:
                    print(f"  创建爬虫配置失败: {e}")
            else:
                print(f"数据源 '{source.name}' (ID: {source.id}) 已有对应爬虫配置，跳过")
                skipped_configs += 1
        
        # 提交事务
        db.commit()
        
        print(f"\n同步完成!")
        print(f"- 创建了 {created_configs} 个爬虫配置")
        print(f"- 跳过了 {skipped_configs} 个已有配置")
        
        # 再次检查同步状态
        check_sync_status(db)
        
        return True
    except Exception as e:
        print(f"同步过程出错: {e}")
        return False
    finally:
        db.close()


def check_sync_status(db_session=None):
    """检查数据源和爬虫配置的同步状态"""
    # 如果没有提供会话，则创建一个新的
    own_session = False
    if db_session is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db_session = SessionLocal()
        own_session = True
    
    try:
        # 统计数据源数量
        data_source_count = db_session.query(DataSource).count()
        print(f"数据源总数: {data_source_count}")
        
        # 统计爬虫配置数量
        crawler_config_count = db_session.query(CrawlerConfig).count()
        print(f"爬虫配置总数: {crawler_config_count}")
        
        # 统计已关联的爬虫配置数量
        linked_config_count = db_session.query(CrawlerConfig).filter(CrawlerConfig.source_id.isnot(None)).count()
        print(f"已关联数据源的爬虫配置数: {linked_config_count}")
        
        # 显示未关联的数据源
        unlinked_sources = db_session.query(DataSource).outerjoin(CrawlerConfig, DataSource.id == CrawlerConfig.source_id).filter(CrawlerConfig.id.is_(None)).all()
        if unlinked_sources:
            print(f"未关联爬虫配置的数据源 ({len(unlinked_sources)}):")
            for source in unlinked_sources:
                print(f"  - ID: {source.id}, Name: {source.name}")
        else:
            print("✓ 所有数据源均已关联爬虫配置")
    finally:
        if own_session:
            db_session.close()


if __name__ == "__main__":
    print("开始同步数据源到爬虫配置...")
    print("="*50)
    
    success = sync_existing_data_sources()
    
    if success:
        print("\n" + "="*50)
        print("数据源与爬虫配置同步完成！")
    else:
        print("\n同步失败！")
        sys.exit(1)