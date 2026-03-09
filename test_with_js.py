import requests
import time
import sys

# 使用requests-html来执行JavaScript
try:
    from requests_html import HTMLSession
    USE_REQUESTS_HTML = True
except ImportError:
    USE_REQUESTS_HTML = False
    print("requests-html not available, using simple requests")

url = "http://localhost:3000/m/beidan-filter"

if USE_REQUESTS_HTML:
    session = HTMLSession()
    try:
        print(f"Loading page with JavaScript: {url}")
        response = session.get(url)
        # 渲染JavaScript
        response.html.render(timeout=20, sleep=2)
        
        print(f"Status Code: {response.status_code}")
        print(f"Page title: {response.html.find('title', first=True).text if response.html.find('title', first=True) else 'No title'}")
        
        # 检查内容
        content = response.html.html
        print(f"Content length: {len(content)}")
        
        # 检查关键元素
        if "mobile-layout-wrapper" in content:
            print("OK: Found mobile-layout-wrapper")
        if "TEST: MobileBeidanFilter component is rendering!" in content:
            print("OK: Found test message")
        if "北单三维筛选器" in content:
            print("OK: Found Chinese title")
            
        # 检查JavaScript错误
        print("\nChecking for JavaScript errors...")
        # requests-html doesn't capture console errors, but we can check for error messages in the page
        
    except Exception as e:
        print(f"Error with requests-html: {e}")
else:
    # 简单请求
    try:
        print(f"Loading page: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        content = response.text
        print(f"Content length: {len(content)}")
        
        # 保存完整内容
        with open("full_page_output.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved full page to full_page_output.html")
        
        # 检查是否有错误信息
        if "Loading module from" in content and "was blocked" in content:
            print("ERROR: Found module loading error")
            import re
            errors = re.findall(r'Loading module from.*?was blocked.*?\)', content)
            for err in errors[:3]:
                print(f"  - {err[:150]}")
        
        if "SyntaxError" in content:
            print("ERROR: Found JavaScript syntax error")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")