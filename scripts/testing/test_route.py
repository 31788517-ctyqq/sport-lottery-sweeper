#!/usr/bin/env python3
import sys
sys.path.append('.')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# 测试健康端点
resp = client.get("/api/v1/health")
print(f"Health: {resp.status_code}")
print(resp.json())

# 测试日志端点（可能需要认证）
resp = client.get("/api/v1/admin/system/logs/db/system?skip=0&limit=5")
print(f"System logs: {resp.status_code}")
if resp.status_code == 200:
    print(resp.json())
elif resp.status_code == 401:
    print("Unauthorized (expected)")
else:
    print(resp.text)