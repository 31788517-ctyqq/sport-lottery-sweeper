#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    response = requests.post(LOGIN_URL, json=login_data, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应体: {response.text}")
except Exception as e:
    print(f"异常: {e}")