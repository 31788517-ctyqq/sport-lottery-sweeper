import requests
import json
from datetime import datetime, timedelta
import jwt
from backend.config import settings

def generate_test_token():
    payload = {
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "user_type": "admin",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

if __name__ == "__main__":
    base_url = "http://localhost:8000/api/v1/admin"
    token = generate_test_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print('测试API端点...')
    try:
        response = requests.get(f"{base_url}/admin-users", headers=headers, params={"skip": 0, "limit": 10})
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text[:500]}')
    except Exception as e:
        print(f'错误: {e}')