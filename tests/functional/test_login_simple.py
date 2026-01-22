#!/usr/bin/env python
"""
测试登录API
"""
import requests
import json
import time

def test_login():
    print("测试登录API...")
    
    # 等待后端启动
    for i in range(10):
        try:
            r = requests.get('http://localhost:8000/docs', timeout=2)
            print('后端已启动')
            break
        except:
            print(f'等待后端启动... ({i+1}/10)')
            time.sleep(1)
    else:
        print('后端未启动')
        return
    
    # 测试登录
    try:
        print("发送登录请求...")
        data = {'username': 'admin', 'password': 'admin123'}
        print(f"请求数据: {data}")
        
        r = requests.post('http://localhost:8000/api/v1/auth/login', 
                         json=data, 
                         timeout=10)
        
        print(f"响应状态码: {r.status_code}")
        print(f"响应内容: {r.text}")
        
        if r.status_code == 200:
            print("✅ 登录成功!")
            response_data = r.json()
            if 'access_token' in response_data:
                print(f"   访问令牌: {response_data['access_token'][:50]}...")
        else:
            print("❌ 登录失败")
            
    except Exception as e:
        print(f"登录请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login()