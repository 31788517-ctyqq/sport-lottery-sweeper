#!/usr/bin/env python3
"""
详细调试北单比赛500错误
"""
import requests
import sys
import os
import json
import traceback
from datetime import datetime

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"

def get_token():
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 令牌在 data.access_token 中
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
                print(f"令牌获取成功，长度: {len(token)}")
                return token
            elif "access_token" in data:
                token = data["access_token"]
                print(f"令牌获取成功 (备选结构)，长度: {len(token)}")
                return token
            else:
                print("令牌未找到，响应结构:", data.keys())
                print("完整响应:", json.dumps(data, indent=2))
        else:
            print(f"登录失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"登录请求异常: {e}")
        traceback.print_exc()
    return None

def test_beidan_endpoint(token):
    """测试北单比赛端点"""
    url = BASE_URL + "/api/v1/admin/matches/beidan/matches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"测试端点: {url}")
    print(f"请求头: {headers}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("=" * 60)
            print("500 内部服务器错误详情:")
            print("=" * 60)
            try:
                error_data = response.json()
                print("JSON 错误响应:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("原始响应文本:")
                print(response.text[:2000])
            print("=" * 60)
        else:
            print("响应摘要:")
            try:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            except:
                print(response.text[:1000])
        
        return response.status_code, response.text
        
    except Exception as e:
        print(f"请求异常: {e}")
        traceback.print_exc()
        return None, str(e)

def check_logs():
    """检查可能的日志文件"""
    log_paths = [
        "logs/app.log",
        "logs/error.log",
        "backend/logs/app.log",
        "backend/logs/error.log",
        "logs/backend_start.err"
    ]
    
    print("\n检查日志文件:")
    for path in log_paths:
        if os.path.exists(path):
            print(f"\n找到日志文件: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 显示最后50行
                    recent = lines[-50:] if len(lines) > 50 else lines
                    print(f"最后{len(recent)}行:")
                    for line in recent:
                        line = line.rstrip()
                        if 'error' in line.lower() or 'traceback' in line.lower() or 'exception' in line.lower():
                            print(f"  ! {line}")
                        else:
                            print(f"    {line}")
            except Exception as e:
                print(f"  读取失败: {e}")
        else:
            print(f"  未找到: {path}")

def main():
    print("=" * 70)
    print("北单比赛500错误详细调试")
    print("=" * 70)
    
    # 1. 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌，退出")
        sys.exit(1)
    
    # 2. 检查日志
    check_logs()
    
    # 3. 测试端点
    print("\n" + "=" * 70)
    print("开始测试端点...")
    status_code, response_text = test_beidan_endpoint(token)
    
    # 4. 如果有错误，尝试从响应中提取更多信息
    if status_code == 500:
        print("\n尝试分析错误原因...")
        # 检查是否是数据库错误
        if "sqlalchemy" in response_text.lower() or "database" in response_text.lower():
            print("错误可能与数据库相关")
        elif "import" in response_text.lower() or "module" in response_text.lower():
            print("错误可能与导入相关")
        elif "attribute" in response_text.lower() or "method" in response_text.lower():
            print("错误可能与对象属性或方法相关")
        else:
            print("错误类型不确定")
    
    print("\n" + "=" * 70)
    print("调试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()