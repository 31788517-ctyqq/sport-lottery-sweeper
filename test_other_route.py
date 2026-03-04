import requests
import sys

# 测试其他路由是否正常
test_urls = [
    "http://localhost:3000/",
    "http://localhost:3000/admin/beidan-filter",
    "http://localhost:3000/admin/dashboard"
]

for url in test_urls:
    try:
        print(f"\nTesting URL: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            if "<!DOCTYPE html>" in response.text:
                print("OK: Returns HTML")
                if "id=\"app\"" in response.text:
                    print("OK: Has Vue app div")
                else:
                    print("WARNING: Missing Vue app div")
            else:
                print("WARNING: Not HTML response")
        else:
            print(f"ERROR: Non-200 status")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")