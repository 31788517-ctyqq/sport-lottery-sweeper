import requests
import json

# 测试多种可能的请求情况
url = "http://localhost:8001/api/admin/crawler/tasks"

# 测试用例1：正常数据
payload1 = {
    "name": "测试任务",
    "source_id": 29,
    "task_type": "DATA_COLLECTION",
    "cron_expression": "0 * * * *",
    "is_active": True,
    "config": {}
}

# 测试用例2：空字符串情况（可能是前端未验证时的情况）
payload2 = {
    "name": "",
    "source_id": "",
    "task_type": "",
    "cron_expression": "",
    "is_active": True,
    "config": {}
}

# 测试用例3：source_id为NaN的情况（转换后）
payload3 = {
    "name": "测试任务",
    "source_id": 0,  # NaN转换后可能变成0或其他值
    "task_type": "DATA_COLLECTION",
    "cron_expression": "0 * * * *",
    "is_active": True,
    "config": {}
}

# 测试用例4：source_id为字符串的情况
payload4 = {
    "name": "测试任务",
    "source_id": "29",
    "task_type": "DATA_COLLECTION",
    "cron_expression": "0 * * * *",
    "is_active": True,
    "config": {}
}

test_cases = [
    ("正常数据", payload1),
    ("空字符串数据", payload2),
    ("无效source_id", payload3),
    ("字符串source_id", payload4)
]

headers = {
    "Content-Type": "application/json"
}

for case_name, payload in test_cases:
    print(f"\n--- 测试用例: {case_name} ---")
    print(f"发送的请求数据: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 422:
            print("422错误详情:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print("无法解析错误详情")
        else:
            print(f"响应内容: {response.text[:200]}...")  # 只显示前200字符
            
    except Exception as e:
        print(f"请求错误: {e}")