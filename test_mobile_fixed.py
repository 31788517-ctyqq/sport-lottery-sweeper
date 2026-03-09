import requests
import time

url = "http://localhost:3000/m/beidan-filter"

try:
    # 等待Vite重新加载
    time.sleep(2)
    
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    content = response.text
    print(f"Content length: {len(content)}")
    
    # 保存内容
    with open("mobile_fixed.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved to mobile_fixed.html")
    
    # 检查关键内容
    if "Mobile Beidan Filter - SIMPLIFIED TEST" in content:
        print("SUCCESS: Mobile component rendered!")
    elif "mobile-layout-wrapper" in content:
        print("SUCCESS: Mobile layout wrapper found!")
    elif "北单" in content:
        print("SUCCESS: Chinese text found!")
    else:
        # 检查是否有JavaScript
        if "<script" in content:
            print("HTML has script tags, but component may not have rendered")
            # 查看是否有错误
            if "error" in content.lower() or "exception" in content.lower():
                print("WARNING: Possible error in content")
        
    # 检查是否有基本的Vue应用结构
    if "<!DOCTYPE html>" in content and "id=\"app\"" in content:
        print("Basic Vue app structure present")
        
except Exception as e:
    print(f"Error: {e}")