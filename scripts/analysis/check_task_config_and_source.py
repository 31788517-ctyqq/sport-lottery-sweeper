import requests
import json

def check_task_config_and_source():
    # 获取任务详情
    task_url = "http://localhost:3000/api/admin/crawler/tasks/32"
    
    print("检查任务ID 32的详细配置...")
    print("="*60)
    
    try:
        task_response = requests.get(task_url)
        print(f"任务详情请求状态: {task_response.status_code}")
        
        if task_response.status_code == 200:
            task_data = task_response.json()['data']
            print("任务详细配置:")
            print(f"  ID: {task_data['id']}")
            print(f"  名称: {task_data['name']}")
            print(f"  源ID: {task_data['source_id']}")
            print(f"  任务类型: {task_data['task_type']}")
            print(f"  Cron表达式: {task_data['cron_expression']}")
            print(f"  配置: {task_data['config']}")
            print(f"  状态: {task_data['status']}")
            print(f"  创建时间: {task_data['created_at']}")
            print(f"  更新时间: {task_data['updated_at']}")
            
            # 根据任务的source_id获取数据源信息
            source_id = task_data['source_id']
            print(f"\n正在获取数据源 {source_id} 的详细信息...")
            
            sources_url = "http://localhost:3000/api/admin/crawler/sources"
            sources_response = requests.get(sources_url)
            
            if sources_response.status_code == 200:
                sources_json = sources_response.json()
                sources_items = sources_json['data']['items']  # 正确提取items
                
                # 查找匹配的数据源
                target_source = None
                for source in sources_items:
                    if source.get('source_id') == source_id:
                        target_source = source
                        break
                
                if target_source:
                    print(f"\n数据源 {source_id} 详细信息:")
                    print(f"  ID: {target_source['id']}")
                    print(f"  源ID: {target_source.get('source_id', 'N/A')}")
                    print(f"  名称: {target_source['name']}")
                    print(f"  URL: {target_source['url']}")
                    print(f"  类型: {target_source['type']}")
                    print(f"  状态: {target_source['status']}")
                    print(f"  配置: {json.dumps(target_source['config'], indent=2, ensure_ascii=False)}")
                    print(f"  创建时间: {target_source['created_at']}")
                    print(f"  更新时间: {target_source['updated_at']}")
                    
                    # 测试数据源健康状态
                    print(f"\n正在测试数据源 {source_id} 的健康状态...")
                    health_check_url = f"http://localhost:3000/api/admin/crawler/sources/{target_source['id']}/health"
                    health_response = requests.get(health_check_url)
                    
                    if health_response.status_code == 200:
                        health_data = health_response.json()
                        print(f"  健康检查结果: {health_data}")
                    else:
                        print(f"  健康检查失败: {health_response.status_code} - {health_response.text}")
                        
                    # 尝试触发任务，看看是否能获得更多信息
                    print(f"\n正在尝试触发任务以测试数据源连接...")
                    trigger_url = f"http://localhost:3000/api/admin/crawler/tasks/{task_data['id']}/trigger"
                    trigger_response = requests.post(trigger_url)
                    
                    if trigger_response.status_code == 200:
                        trigger_result = trigger_response.json()
                        print(f"  任务触发结果: {trigger_result}")
                        
                        # 等待片刻后查看日志
                        import time
                        time.sleep(3)
                        
                        # 获取最新的日志
                        logs_url = f"http://localhost:3000/api/admin/crawler/tasks/{task_data['id']}/logs"
                        logs_response = requests.get(logs_url)
                        
                        if logs_response.status_code == 200:
                            logs_data = logs_response.json()['data']
                            if logs_data['items']:
                                latest_log = logs_data['items'][0]
                                print(f"  最新日志: {latest_log}")
                        else:
                            print(f"  获取日志失败: {logs_response.status_code}")
                    else:
                        print(f"  任务触发失败: {trigger_response.status_code} - {trigger_response.text}")
                else:
                    print(f"  未找到source_id为 {source_id} 的数据源")
                    print(f"  可用的数据源列表:")
                    for idx, source in enumerate(sources_items):
                        print(f"    {idx+1}. ID: {source['id']}, Source ID: {source.get('source_id', 'N/A')}, Name: {source['name']}, Status: {source['status']}")
            else:
                print(f"获取数据源列表失败: {sources_response.status_code}")
        else:
            print(f"获取任务详情失败: {task_response.status_code} - {task_response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

    print("="*60)

if __name__ == "__main__":
    check_task_config_and_source()