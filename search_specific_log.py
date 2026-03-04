import requests
import json

def search_specific_log():
    """搜索包含特定数据的日志记录"""
    
    print("=" * 60)
    print("搜索包含特定数据的日志记录")
    print("=" * 60)
    
    # 获取尽可能多的API日志记录
    all_logs = []
    skip = 0
    limit = 100  # 最大限制
    
    while True:
        params = {'skip': skip, 'limit': limit}
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api', params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                break  # 没有更多数据
            
            all_logs.extend(data)
            print(f"已获取 {len(data)} 条记录，总计 {len(all_logs)} 条")
            
            if len(data) < limit:
                break  # 没有更多数据
            
            skip += limit
        else:
            print(f"请求失败: {response.status_code}")
            break
    
    print(f"\n总共获取到 {len(all_logs)} 条API日志记录")
    
    # 搜索包含用户提到的数据的记录
    target_task_id = "/crawler/task/5"
    target_message_contains = "Crawler task 5: completed"
    target_status_code = 500
    target_duration = 8200
    
    found_records = []
    for log in all_logs:
        req_path = log.get('request_path', '')
        message = log.get('message', '')
        response_status = log.get('response_status')
        duration_ms = log.get('duration_ms')
        
        if (target_task_id in req_path and 
            '5: completed' in message):
            found_records.append({
                'index': all_logs.index(log),
                'log': log
            })
    
    print(f"\n找到 {len(found_records)} 条匹配记录:")
    for record in found_records:
        log = record['log']
        print(f"  位置: #{record['index']}")
        print(f"  时间: {log.get('timestamp')}")
        print(f"  请求路径: {log.get('request_path')}")
        print(f"  状态码: {log.get('response_status')}")
        print(f"  耗时: {log.get('duration_ms')}")
        print(f"  消息: {log.get('message')}")
        print()
    
    # 如果没找到匹配的记录，扩展搜索范围
    if not found_records:
        print("未找到完全匹配的记录，正在搜索接近的记录...")
        
        # 搜索包含task 5的记录
        task5_records = []
        for log in all_logs:
            req_path = log.get('request_path', '')
            message = log.get('message', '')
            
            if 'task/5' in req_path or '5:' in message:
                task5_records.append(log)
        
        if task5_records:
            print(f"找到 {len(task5_records)} 条与task/5相关的记录:")
            for i, log in enumerate(task5_records):
                print(f"  {i+1}. 时间: {log.get('timestamp')}, 路径: {log.get('request_path')}, 消息: {log.get('message')}")
        else:
            print("未找到任何与task/5相关的记录")
    
    # 搜索接近用户提到的耗时值的记录
    close_duration_records = []
    for log in all_logs:
        duration_ms = log.get('duration_ms')
        if duration_ms and abs(duration_ms - target_duration) <= 1000:  # 在1秒内的误差
            close_duration_records.append(log)
    
    if close_duration_records:
        print(f"\n找到 {len(close_duration_records)} 条耗时接近 {target_duration}ms 的记录:")
        for i, log in enumerate(close_duration_records[:5]):  # 只显示前5条
            print(f"  {i+1}. 时间: {log.get('timestamp')}, 路径: {log.get('request_path')}, 耗时: {log.get('duration_ms')}, 消息: {log.get('message')}")

if __name__ == "__main__":
    search_specific_log()