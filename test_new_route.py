import requests

url = "http://localhost:3000/test-simple"

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        content = response.text
        print(f"Content length: {len(content)}")
        if "Test Simple Component" in content:
            print("SUCCESS: Test component rendered!")
            print(f"First 500 chars:\n{content[:500]}")
        else:
            print("WARNING: Component may not have rendered")
            print(f"First 200 chars:\n{content[:200]}")
    else:
        print(f"ERROR: Non-200 status")
        
except Exception as e:
    print(f"Error: {e}")