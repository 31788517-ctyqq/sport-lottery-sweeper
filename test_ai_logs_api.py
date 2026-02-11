#!/usr/bin/env python3
"""
测试AI日志API端点
"""
import requests
import json

base_url = "http://localhost:8000"
endpoint = "/api/v1/admin/system/logs/db/ai"

try:
    # 首先登录获取token（如果需要认证）
    # 但日志端点可能需要管理员认证，这里简化处理
    response = requests.get(base_url + endpoint, params={"skip": 0, "limit": 10})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if isinstance(data, list):
            print(f"返回了 {len(data)} 条日志记录")
        elif isinstance(data, dict) and 'data' in data:
            items = data['data'].get('items', [])
            total = data['data'].get('total', 0)
            print(f"返回了 {len(items)} 条日志记录，总计 {total} 条")
    else:
        print(f"错误响应: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")