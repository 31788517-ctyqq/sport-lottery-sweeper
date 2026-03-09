#!/usr/bin/env python3
"""
更新数据库schema以解决ORM映射问题
"""

from backend.database import engine
from backend.models.base import Base
from backend.models.data_sources import DataSource
from sqlalchemy import DDL, event

def update_schema():
    """更新数据库schema"""
    try:
        print("=" * 60)
        print("更新数据库Schema")
        print("=" * 60)
        
        # 使用反射来获取数据库中的实际表结构
        from sqlalchemy import MetaData, inspect
        from sqlalchemy.schema import DropConstraint, AddConstraint
        
        # 获取当前metadata
        print("当前模型中的表名:", Base.registry._class_registry.keys())
        
        # 尝试直接执行SQL来确保表结构正确
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # 检查表结构
            result = conn.execute(text("""
                SELECT sql FROM sqlite_master WHERE type='table' AND name='data_sources';
            """))
            table_sql = result.fetchone()
            if table_sql:
                print(f"data_sources表定义: {table_sql[0]}")
        
        # 尝试创建表（如果不存在）或更新metadata
        Base.metadata.create_all(bind=engine)
        print("✅ Schema更新完成")
        
        # 验证是否能正确查询
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 测试查询
        sources = db.query(DataSource).all()
        print(f"✅ 成功查询到 {len(sources)} 条数据源记录")
        
        for source in sources:
            print(f"  ID: {source.id}, Name: {source.name}, Source ID: {source.source_id}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Schema更新失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    update_schema()