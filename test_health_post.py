#!/usr/bin/env python3
import requests
import json

url = "http://localhost:8000/api/v1/admin/sources/1/health"
print(f"测试POST请求: {url}")
response = requests.post(url, timeout=10)
print(f"状态码: {response.status_code}")
print(f"响应头: {response.headers}")
print(f"响应体: {response.text}")

if response.status_code == 200:
    data = response.json()
    print("解析的JSON:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 检查data.message是否存在（前端期望的字段）
    if "data" in data and "message" in data["data"]:
        print(f"✓ data.message字段存在: {data['data']['message']}")
    else:
        print("✗ data.message字段不存在")
else:
    print("请求失败")