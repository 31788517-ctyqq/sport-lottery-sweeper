#!/usr/bin/env python3
"""
简单测试后端是否响应
"""
import subprocess
import time
import requests
import sys

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    proc = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        cwd="c:/Users/11581/Downloads/sport-lottery-sweeper",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    return proc

def test_health():
    """测试健康检查"""
    try:
        r = requests.get("http://localhost:8000/health/ready", timeout=5)
        print(f"健康检查: {r.status_code} - {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_login():
    """测试登录"""
    try:
        data = {"email": "admin", "password": "admin123"}
        r = requests.post(
            "http://localhost:8000/api/auth/login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"登录测试: {r.status_code} - {r.text}")
        if r.status_code == 200:
            print("✓ 登录成功!")
            return True
        else:
            print("✗ 登录失败")
            return False
    except Exception as e:
        print(f"登录测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 后端POST请求测试 ===")
    
    # 启动后端
    proc = start_backend()
    
    try:
        # 测试健康检查
        if test_health():
            print("✓ 后端服务正常")
            
            # 测试登录
            if test_login():
                print("\n=== 测试结果: 成功 ===")
            else:
                print("\n=== 测试结果: 登录失败 ===")
        else:
            print("✗ 后端服务未就绪")
    finally:
        # 清理
        proc.terminate()
        proc.wait()
        print("\n后端服务已停止")
