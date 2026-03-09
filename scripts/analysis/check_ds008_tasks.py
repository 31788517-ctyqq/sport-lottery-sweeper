import os
import sys
from pathlib import Path

# 添加项目根目录和backend目录到Python路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

# 手动导入必要的模块
import sqlite3

def check_ds008_tasks():
    # 连接到SQLite数据库
    db_path = backend_path / "data/sport_lottery.db"
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"数据库文件大小: {db_path.stat().st_size} bytes")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 检查DS008数据源信息
        print("=== DS008数据源信息 ===")
        cursor.execute("SELECT id, source_id, name, type FROM data_sources WHERE source_id = 'DS008';")
        ds008_source = cursor.fetchone()
        if ds008_source:
            print(f"ID: {ds008_source[0]}, 源ID: {ds008_source[1]}, 名称: {ds008_source[2]}, 类型: {ds008_source[3]}")
        else:
            print("未找到DS008数据源")
        
        # 检查与DS008关联的任务
        print("\n=== 与DS008数据源关联的任务 ===")
        # 根据前面的输出，DS008的数据库ID是8
        cursor.execute("SELECT id, name, source_id, task_type, status, created_at FROM crawler_tasks WHERE source_id = 8;")
        ds008_tasks = cursor.fetchall()
        
        if ds008_tasks:
            print(f"找到 {len(ds008_tasks)} 个与DS008关联的任务:")
            for task in ds008_tasks:
                print(f"  任务ID: {task[0]}, 名称: {task[1]}, 源ID: {task[2]}, 类型: {task[3]}, 状态: {task[4]}, 创建时间: {task[5]}")
        else:
            print("未找到与DS008数据源关联的任务")
            
        # 再次确认所有任务
        print("\n=== 所有任务列表 ===")
        cursor.execute("SELECT id, name, source_id FROM crawler_tasks;")
        all_tasks = cursor.fetchall()
        for task in all_tasks:
            print(f"任务ID: {task[0]}, 名称: {task[1]}, 源ID: {task[2]}")
        
    except sqlite3.Error as e:
        print(f"查询数据库时发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_ds008_tasks()