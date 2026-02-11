#!/usr/bin/env python3
"""初始化数据库表"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.database import engine
from sqlalchemy import inspect
from backend.models.caipiao_data import CaipiaoData

def init_db():
    print("开始初始化数据库...")
    
    # 使用inspect来检查表是否存在
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"当前数据库中存在的表: {tables}")
    
    # 特定创建彩票数据表
    print("检查并创建 caipiao_data 表...")
    if 'caipiao_data' not in tables:
        CaipiaoData.__table__.create(engine)
        print("✅ caipiao_data 表创建成功")
    else:
        print("ℹ️  caipiao_data 表已存在")
    
    # 创建所有未创建的表
    from backend.database import Base
    Base.metadata.create_all(bind=engine)
    print("✅ 所有缺失的表结构创建完成")
    
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_db()