#!/usr/bin/env python3
"""
验证数据源创建时source_id字段是否能正确生成
"""

from backend.database import get_db
from backend.models.data_sources import DataSource
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.config import settings
import json

def verify_source_id_generation():
    """验证source_id生成"""
    try:
        # 直接创建数据库会话
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("=" * 60)
        print("验证数据源创建和source_id生成")
        print("=" * 60)
        
        # 检查当前数据源数量
        existing_count = db.query(DataSource).count()
        print(f"当前数据源总数: {existing_count}")
        
        # 手动创建一个新数据源记录
        new_source_data = {
            "name": "测试数据源-验证source_id",
            "type": "api",
            "status": True,
            "url": "https://test-api.com/data",
            "config": json.dumps({
                "method": "GET",
                "timeout": 30,
                "headers": {"User-Agent": "Test Client"}
            }),
        }
        
        # 创建新数据源
        new_source = DataSource(**new_source_data)
        db.add(new_source)
        db.flush()  # 获取ID但暂不提交
        
        # 生成source_id
        new_source.source_id = f"DS{new_source.id:03d}"
        db.commit()
        
        print(f"✅ 成功创建新数据源，ID: {new_source.id}")
        print(f"✅ 生成的source_id: {new_source.source_id}")
        
        # 查询刚创建的数据源
        created_source = db.query(DataSource).filter(DataSource.id == new_source.id).first()
        print(f"✅ 查询结果 - ID: {created_source.id}, Name: {created_source.name}, Source ID: {created_source.source_id}")
        
        # 测试to_dict方法
        source_dict = created_source.to_dict()
        print(f"✅ to_dict() 结果: {source_dict}")
        
        # 验证source_id是否正确生成
        expected_source_id = f"DS{created_source.id:03d}"
        if created_source.source_id == expected_source_id:
            print(f"✅ source_id生成正确: {created_source.source_id} == {expected_source_id}")
        else:
            print(f"❌ source_id生成错误: {created_source.source_id} != {expected_source_id}")
        
        # 清理测试数据
        db.delete(created_source)
        db.commit()
        print(f"✅ 已清理测试数据，ID: {created_source.id}")
        
        db.close()
        print("\n✅ source_id生成逻辑验证完成！")
                
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    verify_source_id_generation()