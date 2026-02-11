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

def test_corrected_relation():
    # 创建任务
    url = "http://localhost:8001/api/admin/crawler/tasks"
    payload = {
        "name": f"修正测试_{datetime.now().strftime('%H%M%S')}",
        "source_id": "DS008",  # 使用DS008源ID
        "task_type": "crawl",
        "cron_expression": "0 */3 * * *",  # 每3小时执行一次
        "is_active": True,
        "config": {"timeout": 60, "retry_count": 2}
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
            print(f"源ID (配置): {resp_data['data']['source_id']}")  # 这是配置ID
            print(f"源ID (业务): {resp_data['data']['source_source_id']}")  # 这是DS008
            
            # 查询数据库验证关联关系
            print("\n=== 验证数据库关联关系 ===")
            db_path = backend_path / "sport_lottery.db"
            if not db_path.exists():
                print(f"数据库文件不存在: {db_path}")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            try:
                # 获取刚创建的任务信息
                task_id = resp_data['data']['id']
                cursor.execute("""
                    SELECT ct.id, ct.name, ct.source_id as config_id
                    FROM crawler_tasks ct
                    WHERE ct.id = ?
                """, (task_id,))
                
                task_record = cursor.fetchone()
                if task_record:
                    config_id = task_record[2]  # 爬虫配置ID
                    print(f"任务 {task_record[0]} ({task_record[1]}) 关联到配置ID: {config_id}")
                    
                    # 检查爬虫配置
                    cursor.execute("""
                        SELECT id, name, source_id as data_source_id
                        FROM crawler_configs
                        WHERE id = ?
                    """, (config_id,))
                    
                    config_record = cursor.fetchone()
                    if config_record:
                        print(f"配置 {config_record[0]} ({config_record[1]}) 关联到数据源ID: {config_record[2]}")
                        
                        # 检查数据源
                        if config_record[2]:
                            cursor.execute("""
                                SELECT id, source_id, name
                                FROM data_sources
                                WHERE id = ?
                            """, (config_record[2],))
                            
                            source_record = cursor.fetchone()
                            if source_record:
                                print(f"数据源 {source_record[0]} (源ID: {source_record[1]}) - {source_record[2]}")
                                print(f"\n✅ 完整关联链路: 任务 -> 配置 -> 数据源")
                                print(f"   任务ID {task_record[0]} -> 配置ID {config_id} -> 数据源ID {source_record[0]} (源ID: {source_record[1]})")
                            else:
                                print(f"❌ 未能找到ID为 {config_record[2]} 的数据源")
                        else:
                            print(f"⚠️  配置未关联到数据源")
                    else:
                        print(f"❌ 未能找到ID为 {config_id} 的爬虫配置")
                else:
                    print(f"❌ 未能在数据库中找到任务ID {task_id}")
                    
            except sqlite3.Error as e:
                print(f"查询数据库时发生错误: {e}")
            finally:
                conn.close()
        else:
            print(f"创建任务失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_corrected_relation()