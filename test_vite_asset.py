import requests
import json

def test_vite_assets():
    """测试Vite服务器是否能正确提供资源"""
    
    base_url = "http://localhost:3000"
    
    # 测试1: 获取主HTML文件
    print("Test 1: Getting main HTML")
    try:
        resp = requests.get(base_url + "/", timeout=5)
        print(f"  Status: {resp.status_code}")
        print(f"  Content-Type: {resp.headers.get('Content-Type')}")
        if resp.status_code == 200:
            print("  [OK] Main page accessible")
        else:
            print(f"  [ERROR] Main page failed: {resp.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
    
    # 测试2: 获取Vite客户端脚本
    print("\nTest 2: Getting Vite client script")
    try:
        resp = requests.get(base_url + "/@vite/client", timeout=5)
        print(f"  Status: {resp.status_code}")
        print(f"  Content-Type: {resp.headers.get('Content-Type')}")
        if resp.status_code == 200:
            print("  ✓ Vite client script accessible")
        else:
            print(f"  ✗ Vite client failed: {resp.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
    
    # 测试3: 获取移动端路由的JavaScript
    print("\nTest 3: Testing mobile route JS")
    try:
        # 首先获取主页面查看引用了哪些JS文件
        resp = requests.get(base_url + "/m/beidan-filter", timeout=5)
        if resp.status_code == 200:
            content = resp.text
            # 查找JS文件引用
            import re
            js_files = re.findall(r'src="([^"]+\.js)"', content)
            print(f"  Found {len(js_files)} JS files referenced")
            for js in js_files[:3]:  # 只检查前3个
                if js.startswith('/'):
                    js_url = base_url + js
                else:
                    js_url = base_url + '/' + js
                print(f"  Testing: {js_url}")
                try:
                    js_resp = requests.get(js_url, timeout=5)
                    print(f"    Status: {js_resp.status_code}, Type: {js_resp.headers.get('Content-Type')}")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
        else:
            print(f"  ✗ Could not get page: {resp.status_code}")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
    
    # 测试4: 直接测试API代理
    print("\nTest 4: Testing API proxy")
    try:
        resp = requests.get(base_url + "/api/v1/health", timeout=5)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  ✓ API proxy working: {resp.text[:50]}")
        else:
            print(f"  ✗ API proxy failed: {resp.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

if __name__ == "__main__":
    test_vite_assets()