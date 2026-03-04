import requests
import sys

def test_vite_page():
    try:
        # 测试移动端页面
        url = "http://localhost:3000/m/beidan-filter"
        print(f"Testing URL: {url}")
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        # 检查响应内容
        content = response.text
        print(f"Content length: {len(content)} chars")
        
        # 检查关键标记
        if "<!DOCTYPE html>" in content:
            print("✓ Found DOCTYPE")
        if "<html" in content:
            print("✓ Found HTML tag")
        if "<body" in content:
            print("✓ Found body tag")
        if "<div id=\"app\">" in content:
            print("✓ Found Vue app div")
        if "Mobile Beidan Filter" in content:
            print("✓ Found component content")
        else:
            print("✗ Component content not found")
            # 显示前500个字符
            print("\nFirst 500 chars:")
            print(content[:500])
            
        # 测试API代理
        print("\n--- Testing API Proxy ---")
        api_url = "http://localhost:3000/api/v1/health"
        try:
            api_response = requests.get(api_url, timeout=5)
            print(f"API Status: {api_response.status_code}")
            print(f"API Response: {api_response.text[:100]}...")
        except Exception as e:
            print(f"API test failed: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vite_page()