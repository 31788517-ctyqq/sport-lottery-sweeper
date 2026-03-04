import requests
import sys

url = "http://localhost:3000/m/beidan-filter"

try:
    print(f"Testing URL: {url}")
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content Length: {len(response.text)}")
    
    # 检查是否有Vue组件加载错误
    if "Loading module from" in response.text and "disallowed MIME type" in response.text:
        print("ERROR: Found MIME type error in response")
        # 提取错误信息
        import re
        mime_error = re.findall(r'Loading module from.*?was blocked.*?MIME type.*?"\)', response.text, re.DOTALL)
        if mime_error:
            print(f"MIME Error: {mime_error[0][:200]}")
    
    # 检查是否包含Vue应用的基本结构
    if "<!DOCTYPE html>" in response.text:
        print("OK: Has HTML doctype")
    if "<html" in response.text:
        print("OK: Has <html> tag")
    if "id=\"app\"" in response.text:
        print("OK: Has Vue app div")
    if "mobile-layout-wrapper" in response.text:
        print("OK: Has mobile layout wrapper")
    if "MobileBeidanFilter" in response.text:
        print("OK: Mentions MobileBeidanFilter")
        
    # 检查script标签
    import re
    scripts = re.findall(r'<script[^>]*>.*?</script>', response.text, re.DOTALL)
    print(f"Found {len(scripts)} script tags")
    for i, script in enumerate(scripts[:3]):
        print(f"  Script {i+1}: {script[:100]}...")
        
    # 保存前2000字符用于分析
    with open("test_mime_output.html", "w", encoding="utf-8") as f:
        f.write(response.text[:2000])
    print("Saved first 2000 chars to test_mime_output.html")
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    sys.exit(1)