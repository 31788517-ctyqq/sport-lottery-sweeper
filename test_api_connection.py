import requests
import json

def test_api():
    try:
        url = "http://localhost:8001/api/admin/crawler/tasks?page=1&size=20"
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()