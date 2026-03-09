import requests

url = "http://localhost:3000/admin/beidan-filter"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        content = response.text
        print(f"Content length: {len(content)}")
        if "beidan-filter-panel" in content or "北单" in content:
            print("SUCCESS: Admin component rendered!")
            # 保存内容检查
            with open("admin_output.html", "w", encoding="utf-8") as f:
                f.write(content[:2000])
            print("Saved first 2000 chars to admin_output.html")
        else:
            print("WARNING: Component may not have rendered")
            print(f"First 200 chars:\n{content[:200]}")
    else:
        print(f"ERROR: Non-200 status")
        
except Exception as e:
    print(f"Error: {e}")