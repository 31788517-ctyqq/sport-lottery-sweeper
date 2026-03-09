import requests
import json

def compare_frontend_backend_data():
    """比较前端显示的API日志数据与后端API返回的数据是否一致"""
    
    # 从后端API获取数据
    response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=5')
    if response.status_code != 200:
        print(f"API请求失败: {response.status_code}")
        return
    
    backend_data = response.json()
    
    print("=" * 60)
    print("前端显示字段与后端API数据对比分析")
    print("=" * 60)
    
    if not backend_data:
        print("没有获取到后端数据")
        return
    
    # 检查第一条记录
    log = backend_data[0]
    
    print("后端API返回的字段值:")
    print(f"  timestamp (时间): {log.get('timestamp')}")
    print(f"  level (级别): {log.get('level')}")
    print(f"  request_path (请求路径): {log.get('request_path')}")
    print(f"  response_status (状态码): {log.get('response_status')}")
    print(f"  duration_ms (耗时): {log.get('duration_ms')}")
    print(f"  ip_address (IP地址): {log.get('ip_address')}")
    print(f"  message (消息): {log.get('message')}")
    print()
    
    print("前端列表对应的字段值 (根据用户提供的信息):")
    frontend_values = {
        'timestamp': '2026-01-31T12:31:00',
        'request_path': '/crawler/task/5',
        'response_status': 500,
        'duration_ms': 8200,
        'message': 'Crawler task 5: completed'
    }
    
    print(f"  timestamp (时间): {frontend_values['timestamp']}")
    print(f"  level (级别): INFO (未在用户提供信息中显示)")
    print(f"  request_path (请求路径): {frontend_values['request_path']}")
    print(f"  response_status (状态码): {frontend_values['response_status']}")
    print(f"  duration_ms (耗时): {frontend_values['duration_ms']}")
    print(f"  ip_address (IP地址): (未在用户提供信息中显示)")
    print(f"  message (消息): {frontend_values['message']}")
    print()
    
    print("对比分析:")
    print("-" * 40)
    
    # 对比各项值
    issues = []
    
    # 时间戳对比
    backend_time = log.get('timestamp')
    frontend_time = frontend_values['timestamp']
    if backend_time != frontend_time:
        print(f"⚠ 时间戳不匹配: 后端={backend_time}, 前端={frontend_time}")
        issues.append(f"时间戳不匹配: 后端={backend_time}, 前端={frontend_time}")
    else:
        print("✓ 时间戳匹配")
    
    # 请求路径对比
    backend_path = log.get('request_path')
    frontend_path = frontend_values['request_path']
    if backend_path != frontend_path:
        print(f"⚠ 请求路径不匹配: 后端={backend_path}, 前端={frontend_path}")
        issues.append(f"请求路径不匹配: 后端={backend_path}, 前端={frontend_path}")
    else:
        print("✓ 请求路径匹配")
    
    # 状态码对比
    backend_status = log.get('response_status')
    frontend_status = frontend_values['response_status']
    if backend_status != frontend_status:
        print(f"⚠ 状态码不匹配: 后端={backend_status}, 前端={frontend_status}")
        issues.append(f"状态码不匹配: 后端={backend_status}, 前端={frontend_status}")
    else:
        print("✓ 状态码匹配")
    
    # 耗时对比
    backend_duration = log.get('duration_ms')
    frontend_duration = frontend_values['duration_ms']
    if backend_duration != frontend_duration:
        print(f"⚠ 耗时不匹配: 后端={backend_duration}, 前端={frontend_duration}")
        issues.append(f"耗时不匹配: 后端={backend_duration}, 前端={frontend_duration}")
    else:
        print("✓ 耗时匹配")
    
    # 消息对比
    backend_msg = log.get('message')
    frontend_msg = frontend_values['message']
    if backend_msg != frontend_msg:
        print(f"⚠ 消息不匹配: 后端={backend_msg}, 前端={frontend_msg}")
        issues.append(f"消息不匹配: 后端={backend_msg}, 前端={frontend_msg}")
    else:
        print("✓ 消息匹配")
    
    print()
    if issues:
        print("发现问题:")
        for issue in issues:
            print(f"- {issue}")
        print("\n这表明前端显示的数据可能不是最新的，或者显示的是不同的日志记录。")
    else:
        print("所有字段值都匹配!")

if __name__ == "__main__":
    compare_frontend_backend_data()