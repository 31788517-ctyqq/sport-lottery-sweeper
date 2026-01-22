"""
使用requests库测试登录功能
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

import requests
import json

def test_login():
    """测试登录功能"""
    url = "http://localhost:8000/api/v1/auth/login"
    credentials = {
        "username": "admin",
        "password": "Admin123!@#"
    }
    
    try:
        response = requests.post(url, json=credentials)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("登录成功!")
            print(f"访问令牌: {data.get('access_token', 'N/A')}")
        else:
            print("登录失败")
            
    except Exception as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    test_login()