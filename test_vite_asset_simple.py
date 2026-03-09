import requests
import re
import sys

def test_vite_assets():
    """测试Vite服务器是否能正确提供资源"""
    
    base_url = "http://localhost:3000"
    
    print("Testing Vite server assets...")
    
    # 测试1: 获取主HTML文件
    print("\n1. Testing main HTML page:")
    try:
        resp = requests.get(base_url + "/", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Content-Type: {resp.headers.get('Content-Type')}")
        if resp.status_code == 200:
            print("   [OK] Main page accessible")
            # 检查是否包含Vue应用标记
            if "<div id=\"app\">" in resp.text:
                print("   [OK] Found Vue app div")
            else:
                print("   [WARNING] Vue app div not found")
        else:
            print(f"   [ERROR] Main page failed")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # 测试2: 获取移动端页面
    print("\n2. Testing mobile route (/m/beidan-filter):")
    try:
        resp = requests.get(base_url + "/m/beidan-filter", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Content-Type: {resp.headers.get('Content-Type')}")
        if resp.status_code == 200:
            print("   [OK] Mobile page accessible")
            content = resp.text
            # 检查组件内容
            if "Mobile Beidan Filter" in content:
                print("   [OK] Found component content")
            else:
                print("   [WARNING] Component content not found")
                # 显示页面结构
                print("\n   Page structure analysis:")
                if "<!DOCTYPE html>" in content:
                    print("   - Has DOCTYPE")
                if "<html" in content:
                    print("   - Has HTML tag")
                if "<body" in content:
                    print("   - Has body tag")
                if "<script" in content:
                    script_count = len(re.findall(r'<script', content))
                    print(f"   - Has {script_count} script tags")
        else:
            print(f"   [ERROR] Mobile page failed: {resp.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # 测试3: 测试API代理
    print("\n3. Testing API proxy (/api/v1/health):")
    try:
        resp = requests.get(base_url + "/api/v1/health", timeout=5)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   [OK] API proxy working: {resp.text[:50]}")
        elif resp.status_code == 404:
            print("   [WARNING] API endpoint not found (backend might not be running)")
        else:
            print(f"   [ERROR] API proxy failed: {resp.text[:100]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # 测试4: 测试Vite客户端脚本
    print("\n4. Testing Vite client script (/@vite/client):")
    try:
        resp = requests.get(base_url + "/@vite/client", timeout=3)
        print(f"   Status: {resp.status_code}")
        print(f"   Content-Type: {resp.headers.get('Content-Type')}")
        if resp.status_code == 200:
            print("   [OK] Vite client script accessible")
        else:
            print(f"   [ERROR] Vite client script not accessible")
    except Exception as e:
        print(f"   [ERROR] {e}")

if __name__ == "__main__":
    test_vite_assets()