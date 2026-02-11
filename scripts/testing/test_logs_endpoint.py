import sys
import requests
import json

BASE = "http://localhost:8000"

# 可能的端点路径
candidates = [
    "/api/v1/admin/system/logs/db/system",
    "/api/v1/v1/admin/system/system/logs/db/system",
    "/api/v1/admin/system/system/logs/db/system",
    "/api/v1/v1/admin/system/logs/db/system",
    "/api/v1/v1/admin/logs/db/system",
    "/api/v1/admin/logs/db/system",
    "/api/v1/logs/db/system",
]

for path in candidates:
    url = BASE + path
    try:
        resp = requests.get(url, timeout=5)
        print(f"{url} -> {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Success! Found {len(data) if isinstance(data, list) else 'data'}")
            break
    except Exception as e:
        print(f"{url} -> ERROR: {e}")

# 另外，获取 OpenAPI 规范以查看路由
try:
    resp = requests.get(BASE + "/openapi.json", timeout=5)
    if resp.status_code == 200:
        spec = resp.json()
        paths = list(spec.get('paths', {}).keys())
        print(f"\nFound {len(paths)} paths in OpenAPI")
        # 过滤出包含 'log' 的路径
        log_paths = [p for p in paths if 'log' in p.lower()]
        print(f"Paths containing 'log': {log_paths}")
except Exception as e:
    print(f"Failed to fetch OpenAPI: {e}")