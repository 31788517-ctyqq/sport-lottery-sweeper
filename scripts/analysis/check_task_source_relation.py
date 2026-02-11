import sqlite3
from pathlib import Path
import sys

# 添加backend目录到Python路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

def check_task_source_relation():
    db_path = backend_path / "sport_lottery.db"
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 查询最新的几个任务及其关联的数据源
        print("=== 任务与数据源的关联关系 ===")
        cursor.execute("""
            SELECT ct.id, ct.name, ct.source_id as config_id, cc.source_id as config_source_id, ds.id as ds_id, ds.source_id as ds_source_id, ds.name as ds_name
            FROM crawler_tasks ct
            LEFT JOIN crawler_configs cc ON ct.source_id = cc.id
            LEFT JOIN data_sources ds ON cc.source_id = ds.id
            ORDER BY ct.id DESC
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"任务ID: {row[0]}, 任务名称: {row[1]}")
            print(f"  -> 任务关联配置ID: {row[2]}")
            print(f"  -> 配置关联数据源ID: {row[3]}")
            print(f"  -> 数据源ID: {row[4]}, 源ID: {row[5]}, 名称: {row[6]}")
            print()
            
        # 检查DS008相关的任务
        print("=== DS008相关任务 ===")
        cursor.execute("""
            SELECT ds.source_id, ds.name, cc.id as config_id, ct.id as task_id, ct.name as task_name
            FROM data_sources ds
            LEFT JOIN crawler_configs cc ON ds.id = cc.source_id
            LEFT JOIN crawler_tasks ct ON cc.id = ct.source_id
            WHERE ds.source_id = 'DS008'
        """)
        
        ds008_results = cursor.fetchall()
        for row in ds008_results:
            print(f"数据源: {row[0]} ({row[1]})")
            print(f"  -> 配置ID: {row[2]}")
            print(f"  -> 关联任务: {row[3]} ({row[4]})")
        
    except sqlite3.Error as e:
        print(f"查询数据库时发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_task_source_relation()