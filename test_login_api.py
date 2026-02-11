import requests
import json
import sys

print("Testing login API...")
print("=" * 50)

# 测试不同的端点
endpoints = [
    "http://localhost:8000/api/v1/auth/login",
    "http://localhost:8000/api/auth/login",  # 兼容端点
    "http://127.0.0.1:8000/api/v1/auth/login",
]

for url in endpoints:
    print(f"\nTesting URL: {url}")
    try:
        # 测试OPTIONS请求（CORS预检）
        print("  Sending OPTIONS request...")
        options_resp = requests.options(url, timeout=5)
        print(f"    Status: {options_resp.status_code}")
        print(f"    Headers: {dict(options_resp.headers)}")
        
        # 测试POST请求
        print("  Sending POST request...")
        payload = {"username": "admin", "password": "admin123"}
        headers = {"Content-Type": "application/json"}
        
        post_resp = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"    Status: {post_resp.status_code}")
        
        if post_resp.status_code == 200:
            data = post_resp.json()
            print(f"    Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"    Headers: {dict(post_resp.headers)}")
            try:
                error_data = post_resp.json()
                print(f"    Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"    Text: {post_resp.text[:200]}")
                
    except requests.exceptions.ConnectionError:
        print("  Connection failed - service may not be running")
    except requests.exceptions.Timeout:
        print("  Request timed out")
    except Exception as e:
        print(f"  Error: {e}")

# 检查CORS头
print("\n" + "=" * 50)
print("Checking CORS headers...")
test_url = "http://localhost:8000/api/v1/auth/login"

try:
    resp = requests.options(test_url, timeout=3)
    cors_headers = {
        'Access-Control-Allow-Origin': resp.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': resp.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': resp.headers.get('Access-Control-Allow-Headers'),
        'Access-Control-Allow-Credentials': resp.headers.get('Access-Control-Allow-Credentials'),
    }
    print(f"CORS headers received: {json.dumps(cors_headers, indent=2)}")
    
    # 检查是否允许localhost:3000
    if cors_headers['Access-Control-Allow-Origin'] in ('*', 'http://localhost:3000'):
        print("✅ CORS配置正确")
    else:
        print("⚠️ CORS配置可能有问题")
        
except Exception as e:
    print(f"Error checking CORS: {e}")