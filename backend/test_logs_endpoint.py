#!/usr/bin/env python3
"""测试日志API端点"""
import sys
import os
sys.path.append('.')

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("Testing logs API endpoints...")

# 测试健康检查
print("\n1. Testing health endpoint...")
try:
    response = client.get("/api/v1/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:100]}")
except Exception as e:
    print(f"   Error: {e}")

# 测试日志统计
print("\n2. Testing logs statistics endpoint...")
try:
    response = client.get("/api/v1/admin/system/logs/db/statistics")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# 测试系统日志
print("\n3. Testing system logs endpoint...")
try:
    response = client.get("/api/v1/admin/system/logs/db/system?skip=0&limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Received {len(data)} logs")
        for i, log in enumerate(data[:2]):
            print(f"   Log {i}: level={log.get('level')}, module={log.get('module')}, message={log.get('message')[:50]}")
    else:
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")