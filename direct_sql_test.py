"""
直接执行SQL查询测试
"""
import sqlite3
from pathlib import Path
import json

def direct_sql_test():
    """直接执行SQL查询测试"""
    db_path = Path(__file__).parent / "backend" / "data/sport_lottery.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("直接SQL查询测试...")
        
        # 测试分类筛选
        print("\n1. 查询所有数据源配置中包含category字段的记录:")
        cursor.execute("""
            SELECT id, name, config 
            FROM data_sources 
            WHERE json_extract(config, '$.category') IS NOT NULL
        """)
        rows = cursor.fetchall()
        print(f"   找到 {len(rows)} 条配置中包含category字段的记录:")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[1]}, Config: {row[2]}")
        
        # 测试特定分类筛选
        print("\n2. 查询分类为'match_data'的记录:")
        cursor.execute("""
            SELECT id, name, config 
            FROM data_sources 
            WHERE json_extract(config, '$.category') = 'match_data'
        """)
        rows = cursor.fetchall()
        print(f"   找到 {len(rows)} 条分类为'match_data'的记录:")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[1]}, Config: {row[2]}")
        
        # 测试模糊匹配查询（我们之前使用的）
        print("\n3. 查询配置中包含'match_data'字符串的记录:")
        cursor.execute("""
            SELECT id, name, config 
            FROM data_sources 
            WHERE config LIKE '%match_data%'
        """)
        rows = cursor.fetchall()
        print(f"   找到 {len(rows)} 条配置中包含'match_data'的记录:")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[1]}, Config: {row[2]}")
        
        # 测试源ID查询
        print("\n4. 查询源ID为'DS009'的记录:")
        cursor.execute("""
            SELECT id, name, config 
            FROM data_sources 
            WHERE source_id = 'DS009'
        """)
        rows = cursor.fetchall()
        print(f"   找到 {len(rows)} 条源ID为'DS009'的记录:")
        for row in rows:
            print(f"     ID: {row[0]}, Name: {row[1]}, Config: {row[2]}")
        
        # 检查是否有任何记录包含category字段
        print("\n5. 检查前5条记录的配置内容:")
        cursor.execute("""
            SELECT id, name, config 
            FROM data_sources 
            LIMIT 5
        """)
        rows = cursor.fetchall()
        for row in rows:
            config = row[2]
            print(f"   ID: {row[0]}, Name: {row[1]}")
            try:
                config_dict = json.loads(config) if config else {}
                print(f"     完整配置: {config_dict}")
                category = config_dict.get('category', 'Not found')
                print(f"     Category字段: {category}")
            except:
                print(f"     配置解析失败: {config}")
            print()
        
        conn.close()
        print("SQL查询测试完成")
        
    except Exception as e:
        print(f"SQL查询测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    direct_sql_test()