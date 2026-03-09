import requests
import json

try:
    response = requests.get("http://localhost:8001/openapi.json")
    if response.status_code == 200:
        data = response.json()
        paths = data.get("paths", {})
        print("Available routes:")
        for path, methods in paths.items():
            if "logs" in path.lower():  # 只打印包含logs的路径
                print(f"  {path}: {list(methods.keys())}")
    else:
        print(f"Failed to get openapi.json: Status {response.status_code}")
except Exception as e:
    print(f"Error getting openapi.json: {e}")