import requests
import json
from datetime import datetime
import sqlite3
from pathlib import Path
import sys

# 添加backend目录到Python路径
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

def create_task_and_verify():
    # 创建任务
    url = "http://localhost:8001/api/admin/crawler/tasks"
    payload = {
        "name": f"验证任务_{datetime.now().strftime('%H%M%S')}",
        "source_id": "DS008",  # 使用DS008源ID
        "task_type": "crawl",
        "cron_expression": "0 */2 * * *",  # 每2小时执行一次
        "is_active": True,
        "config": {"timeout": 30, "retry_count": 3}
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"当前时间: {datetime.now()}")
    print(f"创建任务请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            resp_data = response.json()
            print(f"API返回的创建时间: {resp_data['data']['created_at']}")
            print(f"任务ID: {resp_data['data']['id']}")
            print(f"源ID (数据库): {resp_data['data']['source_id']}")
            print(f"源ID (业务): {resp_data['data']['source_source_id']}")
            
            # 查询数据库验证
            print("\n=== 验证数据库记录 ===")
            db_path = backend_path / "data/sport_lottery.db"
            if not db_path.exists():
                print(f"数据库文件不存在: {db_path}")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            try:
                # 查询刚创建的任务
                task_id = resp_data['data']['id']
                cursor.execute("""
                    SELECT id, name, source_id, task_type, status, created_at 
                    FROM crawler_tasks 
                    WHERE id = ?
                """, (task_id,))
                
                task_record = cursor.fetchone()
                if task_record:
                    print(f"数据库记录 - 任务ID: {task_record[0]}, 名称: {task_record[1]}, 源ID: {task_record[2]}, 类型: {task_record[3]}, 状态: {task_record[4]}, 创建时间: {task_record[5]}")
                    
                    # 同时查询对应的数据源信息
                    cursor.execute("""
                        SELECT id, source_id, name 
                        FROM data_sources 
                        WHERE id = ?
                    """, (task_record[2],))
                    
                    source_record = cursor.fetchone()
                    if source_record:
                        print(f"关联数据源 - ID: {source_record[0]}, 源ID: {source_record[1]}, 名称: {source_record[2]}")
                    else:
                        print("未找到关联的数据源记录")
                        
                else:
                    print(f"未在数据库中找到任务ID {task_id}")
                    
            except sqlite3.Error as e:
                print(f"查询数据库时发生错误: {e}")
            finally:
                conn.close()
        else:
            print(f"创建任务失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    create_task_and_verify()