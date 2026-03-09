import requests
import sys

# 测试main.js是否正常加载
url = "http://localhost:3000/src/main.js"

try:
    print(f"Testing main.js: {url}")
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        print("OK: main.js loaded successfully")
        # 检查是否有JavaScript错误语法
        content = response.text
        if "import" in content and "createApp" in content:
            print("OK: Contains Vue imports")
        else:
            print("WARNING: May not be correct main.js content")
            print(f"First 200 chars: {content[:200]}")
    else:
        print(f"ERROR: Failed to load main.js")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    sys.exit(1)