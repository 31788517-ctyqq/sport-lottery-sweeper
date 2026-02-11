import requests

base_url = "http://localhost:8001"

# 测试超出限制的参数
print("Testing parameter validation...")

# 测试超出limit上限的请求
url = f"{base_url}/api/v1/admin/system/logs/db/system?skip=0&limit=2000"
response = requests.get(url)
print(f"Request: {url}")
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error response: {response.text}")
else:
    data = response.json()
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")

# 测试正常limit值
url = f"{base_url}/api/v1/admin/system/logs/db/system?skip=0&limit=10"
response = requests.get(url)
print(f"\nRequest: {url}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
else:
    print(f"Error response: {response.text}")

# 测试负数skip值
url = f"{base_url}/api/v1/admin/system/logs/db/system?skip=-5&limit=10"
response = requests.get(url)
print(f"\nRequest: {url}")
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error response: {response.text}")