#!/usr/bin/env python3
"""
查询数据库中数据源数量的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.models.sp_core import DataSource as SPDataSource  # 使用具体命名的数据源模型
from backend.models.base import Base


def count_data_sources():
    """查询数据库中数据源的数量"""
    try:
        # 创建数据库引擎
        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        
        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 计算SP数据源数量 (sp_core中的DataSource)
        sp_total_count = db.query(SPDataSource).count()
        
        # 查询启用的SP数据源数量
        sp_active_count = db.query(SPDataSource).filter(SPDataSource.is_active == True).count()
        
        # 查询禁用的SP数据源数量
        sp_inactive_count = db.query(SPDataSource).filter(SPDataSource.is_active == False).count()
        
        print("=" * 60)
        print("SP数据源统计信息 (backend/models/sp_core.py 中的DataSource):")
        print(f"总数据源数量: {sp_total_count}")
        print(f"启用的数据源: {sp_active_count}")
        print(f"禁用的数据源: {sp_inactive_count}")
        print("=" * 60)
        
        # 如果有数据源，显示详细信息
        if sp_total_count > 0:
            print("\nSP数据源详情:")
            sp_data_sources = db.query(SPDataSource).all()
            for idx, ds in enumerate(sp_data_sources, 1):
                print(f"{idx}. ID: {ds.id}, 源ID: {ds.source_id}, 名称: {ds.name}, "
                      f"类型: {ds.source_type}, 分类: {ds.category}, "
                      f"状态: {'启用' if ds.is_active else '禁用'}, URL: {ds.api_url}")
        
        db.close()
        
        return sp_total_count
        
    except Exception as e:
        print(f"查询数据源时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    count = count_data_sources()
    print(f"\n系统中共有 {count} 条SP数据源")