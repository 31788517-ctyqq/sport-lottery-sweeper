#!/usr/bin/env python3
"""
重建数据源表结构以解决ORM映射问题
"""

from backend.database import engine
from backend.models.data_sources import DataSource
from backend.models.base import Base
from sqlalchemy import inspect, text

def rebuild_table():
    """重建数据源表"""
    try:
        print("=" * 60)
        print("检查并重建数据源表结构")
        print("=" * 60)
        
        # 获取当前数据库中的表信息
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('data_sources')]
        print(f"当前data_sources表的列: {existing_columns}")
        
        # 检查source_id是否在列中
        if 'source_id' in existing_columns:
            print("✅ source_id列已存在于数据库中")
        else:
            print("❌ source_id列不存在于数据库中")
            # 尝试添加source_id列
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE data_sources ADD COLUMN source_id VARCHAR(10);"))
                conn.commit()
            print("✅ 已添加source_id列")
        
        # 尝试更新现有记录的source_id值
        from sqlalchemy.orm import sessionmaker
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 查询所有数据源并更新其source_id
        sources = db.query(DataSource).all()
        print(f"发现 {len(sources)} 条数据源记录")
        
        for source in sources:
            if not source.source_id:
                source.source_id = f"DS{source.id:03d}"
                print(f"  更新 ID {source.id}: {source.name} -> source_id: {source.source_id}")
        
        db.commit()
        db.close()
        
        print("\n✅ 数据源表结构重建完成！")
        
    except Exception as e:
        print(f"❌ 重建失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    rebuild_table()