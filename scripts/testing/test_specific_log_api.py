import requests

# 测试日志API端点
base_url = "http://localhost:8001"

# 测试端点 - 根据API文件中的定义
endpoints = [
    "/api/v1/admin/system/logs/db/statistics",
    "/api/v1/admin/system/logs/db/system",
    "/api/v1/admin/system/logs/db/user",
    "/api/v1/admin/system/logs/db/security",
    "/api/v1/admin/system/logs/db/api"
]

print("Testing specific API endpoints...")

for endpoint in endpoints:
    full_url = f"{base_url}{endpoint}?skip=0&limit=5"
    
    try:
        # 发送GET请求
        response = requests.get(full_url)
        print(f"{endpoint}: Status {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict response'}")
                print(f"  Sample data: {str(data)[:200]}...")
            except:
                print(f"  Non-JSON response: {response.text[:200]}")
        elif response.status_code != 404:
            print(f"  Response: {response.text[:200]}")
        
    except Exception as e:
        print(f"{endpoint}: Error - {e}")

print("\nTesting completed.")