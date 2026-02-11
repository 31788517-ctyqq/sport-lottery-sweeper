"""
直接测试SQL查询
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database import engine
from backend.models.data_sources import DataSource
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

def test_sql_query():
    """测试SQL查询"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("测试直接SQL查询...")
        
        # 测试原始查询 - 查找所有数据源
        print("\n1. 查询所有数据源:")
        all_sources = db.query(DataSource).all()
        print(f"   总共有 {len(all_sources)} 条数据源记录")
        
        # 测试SQL查询 - 不带分类筛选
        print("\n2. 执行不带分类筛选的查询:")
        base_query = """
            SELECT id, source_id, name, type, status, url, config 
            FROM data_sources
            ORDER BY created_at DESC
            LIMIT 5
        """
        result = db.execute(text(base_query))
        rows = result.fetchall()
        for row in rows:
            print(f"   ID: {row[0]}, Name: {row[2]}, Config: {row[6]}")
        
        # 测试SQL查询 - 使用json_extract
        print("\n3. 执行带分类筛选的查询 (json_extract):")
        category_query = """
            SELECT id, source_id, name, type, status, url, config 
            FROM data_sources
            WHERE json_extract(config, '$.category') IS NOT NULL 
            AND json_extract(config, '$.category') = :category
            ORDER BY created_at DESC
        """
        params = {'category': 'match_data'}
        result = db.execute(text(category_query), params)
        rows = result.fetchall()
        print(f"   按 'match_data' 分类找到 {len(rows)} 条记录")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[2]}, Config: {row[6]}")
        
        # 测试SQL查询 - 查找包含category字段的所有记录
        print("\n4. 查找所有配置中包含category字段的记录:")
        has_category_query = """
            SELECT id, source_id, name, type, status, url, config 
            FROM data_sources
            WHERE json_extract(config, '$.category') IS NOT NULL
            ORDER BY created_at DESC
        """
        result = db.execute(text(has_category_query))
        rows = result.fetchall()
        print(f"   找到 {len(rows)} 条配置中包含category字段的记录")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[2]}, Config: {row[6]}")
            
        # 测试SQL查询 - 查找特定source_id
        print("\n5. 查找source_id为'DS009'的记录:")
        source_id_query = """
            SELECT id, source_id, name, type, status, url, config 
            FROM data_sources
            WHERE source_id = :source_id
            ORDER BY created_at DESC
        """
        params = {'source_id': 'DS009'}
        result = db.execute(text(source_id_query), params)
        rows = result.fetchall()
        print(f"   找到 {len(rows)} 条source_id为'DS009'的记录")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[2]}, Config: {row[6]}")
        
    except Exception as e:
        print(f"   查询失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_sql_query()