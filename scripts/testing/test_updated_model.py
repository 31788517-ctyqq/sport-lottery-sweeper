#!/usr/bin/env python3
"""
测试更新后的数据源模型
"""

from backend.database import get_db
from backend.models.data_sources import DataSource
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.config import settings

def test_updated_model():
    """测试更新后的模型"""
    try:
        # 直接创建数据库会话
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("=" * 60)
        print("测试更新后的数据源模型")
        print("=" * 60)
        
        # 尝试查询数据源
        sources = db.query(DataSource).all()
        print(f"成功查询到 {len(sources)} 个数据源")
        
        for source in sources[-5:]:  # 显示最近的5个
            print(f"ID: {source.id}, Name: {source.name}, Source ID: {getattr(source, 'source_id', 'N/A')}")
        
        # 尝试获取一个特定的数据源
        specific_source = db.query(DataSource).filter(DataSource.id == 8).first()
        if specific_source:
            print(f"\n详细信息 - ID 8:")
            print(f"  Name: {specific_source.name}")
            print(f"  Source ID: {getattr(specific_source, 'source_id', 'N/A')}")
            print(f"  Type: {specific_source.type}")
            print(f"  URL: {specific_source.url}")
            
            # 测试to_dict方法
            print(f"  to_dict result: {specific_source.to_dict()}")
        
        db.close()
        print("\n✅ 模型测试成功！")
                
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_updated_model()