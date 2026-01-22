#!/usr/bin/env python
"""
最终登录测试
"""
import requests
import json
import time

def test():
    print("等待后端启动...")
    for i in range(10):
        try:
            r = requests.get('http://localhost:8000/docs', timeout=2)
            print('后端已启动')
            break
        except:
            print(f'等待... ({i+1}/10)')
            time.sleep(1)
    else:
        print('后端未启动')
        return
    
    # 测试登录
    print("\n测试登录...")
    data = {'username': 'admin', 'password': 'admin123'}
    
    try:
        r = requests.post('http://localhost:8000/api/v1/auth/login', 
                         json=data, 
                         timeout=10)
        
        print(f"状态码: {r.status_code}")
        print(f"响应: {r.text}")
        
        if r.status_code == 200:
            resp = r.json()
            if resp.get('code') == 200:
                print("✅ 登录成功!")
                token = resp.get('data', {}).get('access_token', '')
                if token:
                    print(f"   令牌: {token[:50]}...")
                else:
                    print(f"   完整响应: {resp}")
            else:
                print(f"❌ 登录失败: {resp.get('message')}")
        else:
            print(f"❌ HTTP错误: {r.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()