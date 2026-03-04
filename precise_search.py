import requests
import json

def precise_search():
    """精确搜索用户提到的记录"""
    
    print("=" * 60)
    print("精确搜索用户提到的记录")
    print("=" * 60)
    
    # 获取所有API日志记录
    all_logs = []
    skip = 0
    limit = 100
    
    while True:
        params = {'skip': skip, 'limit': limit}
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api', params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            
            all_logs.extend(data)
            
            if len(data) < limit:
                break
            
            skip += limit
        else:
            print(f"请求失败: {response.status_code}")
            break
    
    print(f"总共扫描了 {len(all_logs)} 条记录")
    
    # 用户提到的具体值
    target_timestamp = "2026-01-31T12:31:00"
    target_path = "/crawler/task/5"
    target_status = 500
    target_duration = 8200
    target_message = "Crawler task 5: completed"
    
    print(f"\n搜索目标:")
    print(f"  时间戳: {target_timestamp}")
    print(f"  请求路径: {target_path}")
    print(f"  状态码: {target_status}")
    print(f"  耗时: {target_duration}")
    print(f"  消息: {target_message}")
    print()
    
    # 搜索完全匹配的记录
    exact_match = None
    for log in all_logs:
        if (log.get('timestamp') == target_timestamp and
            log.get('request_path') == target_path and
            log.get('response_status') == target_status and
            log.get('duration_ms') == target_duration and
            log.get('message') == target_message):
            exact_match = log
            break
    
    if exact_match:
        print("找到完全匹配的记录!")
        print(json.dumps(exact_match, indent=2, ensure_ascii=False))
    else:
        print("❌ 未找到完全匹配的记录")
        
        # 寻找部分匹配的记录
        print("\n寻找部分匹配的记录...")
        
        # 搜索时间戳接近的记录
        time_matches = [log for log in all_logs if target_timestamp[:13] in log.get('timestamp', '')]
        if time_matches:
            print(f"找到 {len(time_matches)} 条时间戳接近的记录:")
            for log in time_matches:
                print(f"  - {log.get('timestamp')} | {log.get('request_path')} | {log.get('message')}")
        else:
            print("未找到时间戳接近的记录")
        
        # 搜索task/5的记录
        path_matches = [log for log in all_logs if '/crawler/task/5' == log.get('request_path')]
        if path_matches:
            print(f"\n找到 {len(path_matches)} 条路径匹配的记录:")
            for log in path_matches:
                print(f"  - {log.get('timestamp')} | {log.get('request_path')} | {log.get('message')} | 状态: {log.get('response_status')} | 耗时: {log.get('duration_ms')}")
        else:
            print("\n未找到路径匹配的记录")
        
        # 搜索消息中包含'completed'的记录
        completed_matches = [log for log in all_logs if 'completed' in log.get('message', '')]
        if completed_matches:
            print(f"\n找到 {len(completed_matches)} 条消息包含'completed'的记录:")
            for log in completed_matches:
                print(f"  - {log.get('timestamp')} | {log.get('request_path')} | {log.get('message')} | 状态: {log.get('response_status')} | 耗时: {log.get('duration_ms')}")
        else:
            print("\n未找到消息包含'completed'的记录")
    
    print("\n结论分析:")
    print("- 如果找不到匹配记录，可能是以下原因之一:")
    print("  1. 用户界面显示的是缓存数据")
    print("  2. 用户界面应用了某些过滤条件（如搜索、筛选）")
    print("  3. 用户查看的是不同时间段的数据")
    print("  4. 数据在前端处理时发生了变化")
    print("  5. 用户查看的不是API日志页面，而是其他类型的日志页面")

if __name__ == "__main__":
    precise_search()