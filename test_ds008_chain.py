import requests
import json
import sqlite3
from pathlib import Path
import sys

# 添加backend目录到Python路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

def test_ds008_chain():
    # 检查数据库中DS008数据源相关信息
    db_path = backend_path / "sport_lottery.db"
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("=== 检查数据库中的DS008相关记录 ===")
    try:
        # 查询DS008数据源
        cursor.execute("SELECT id, source_id, name FROM data_sources WHERE source_id = 'DS008'")
        ds_records = cursor.fetchall()
        print(f"数据源DS008: {ds_records}")
        
        # 查询与数据源ID 8关联的爬虫配置
        cursor.execute("SELECT id, name, source_id FROM crawler_configs WHERE source_id = 8")
        config_records = cursor.fetchall()
        print(f"与数据源ID 8关联的爬虫配置: {config_records}")
        
        # 查询使用配置ID 1的任务（如果存在）
        cursor.execute("SELECT id, name, source_id FROM crawler_tasks WHERE source_id = 1")
        task_records = cursor.fetchall()
        print(f"使用配置ID 1的任务: {task_records}")
        
        # 查询所有任务
        cursor.execute("SELECT id, name, source_id FROM crawler_tasks ORDER BY id DESC LIMIT 10")
        all_tasks = cursor.fetchall()
        print(f"最近10个任务: {all_tasks}")
        
        # 检查所有任务及其关联的配置
        print("\n=== 检查任务与其配置的关联 ===")
        for task_id, task_name, config_id in all_tasks:
            cursor.execute("SELECT id, name, source_id FROM crawler_configs WHERE id = ?", (config_id,))
            config = cursor.fetchone()
            if config:
                config_id_db, config_name, data_source_id = config
                if data_source_id:
                    cursor.execute("SELECT source_id, name FROM data_sources WHERE id = ?", (data_source_id,))
                    ds = cursor.fetchone()
                    if ds:
                        print(f"任务ID {task_id} ({task_name}) -> 配置ID {config_id_db} ({config_name}) -> 数据源ID {data_source_id} (源ID: {ds[0]})")
                    else:
                        print(f"任务ID {task_id} ({task_name}) -> 配置ID {config_id_db} ({config_name}) -> 数据源ID {data_source_id} (不存在)")
                else:
                    print(f"任务ID {task_id} ({task_name}) -> 配置ID {config_id_db} ({config_name}) -> 未关联数据源")
            else:
                print(f"任务ID {task_id} ({task_name}) -> 配置ID {config_id} (不存在)")
                
    except sqlite3.Error as e:
        print(f"查询数据库时发生错误: {e}")
    finally:
        conn.close()

    print("\n=== 测试API响应 ===")
    # 测试获取任务列表API
    url = "http://localhost:8001/api/admin/crawler/tasks"
    params = {
        "page": 1,
        "size": 20,
        "name": "",
        "task_type": "",
        "status": "",
        "source_id": ""
    }

    try:
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回任务数量: {len(data)}")
            if data:
                print("前5个任务信息:")
                for i, task in enumerate(data[:5]):
                    print(f"  {i+1}. ID: {task.get('id')}, 名称: {task.get('name')}, "
                          f"源ID: {task.get('source_id')}, 源源ID: {task.get('source_source_id')}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_ds008_chain()