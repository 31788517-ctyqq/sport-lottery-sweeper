#!/usr/bin/env python3
"""
带鉴权的全模块GET冒烟测试
测试所有GET端点，使用JWT令牌进行认证
"""

import requests
import json
import sys
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/v1/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"

# 输出文件
OUTPUT_FILE = "auth_smoke_get_results.txt"

def get_auth_token() -> Optional[str]:
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    print(f"正在登录: {login_url}")
    try:
        response = requests.post(login_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 不同API的响应结构可能不同
            if isinstance(data, dict):
                if "access_token" in data:
                    token = data["access_token"]
                elif "data" in data and "access_token" in data["data"]:
                    token = data["data"]["access_token"]
                else:
                    # 尝试其他常见字段
                    for key in ["token", "jwt", "accessToken"]:
                        if key in data:
                            token = data[key]
                            break
                    else:
                        token = None
            else:
                token = None
            
            if token:
                print(f"✅ 登录成功，令牌获取成功")
                return token
            else:
                print(f"❌ 登录响应中未找到令牌字段")
                print(f"响应: {data}")
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
    
    return None

def get_all_get_routes() -> List[str]:
    """获取所有GET路由列表"""
    # 方法1: 使用扫描器获取路由
    try:
        # 将项目根目录添加到Python路径
        sys.path.insert(0, str(Path(__file__).parent))
        
        from backend.scanner.api_scanner import APIScanner
        scanner = APIScanner()
        # 扫描目录
        report = scanner.scan_directory("api/v1")
        
        # 从报告中提取GET路由
        get_routes = []
        if "routes" in report:
            for route in report["routes"]:
                if "methods" in route and "GET" in route["methods"]:
                    get_routes.append(route["path"])
        
        print(f"从扫描器获取到 {len(get_routes)} 个GET路由")
        return get_routes
    except Exception as e:
        print(f"⚠️ 使用扫描器获取路由失败: {e}")
        # 方法2: 从现有结果文件中读取路由
        print("尝试从现有结果文件中读取路由...")
        try:
            with open("smoke_get_results.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            get_routes = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # 格式: /path   状态码
                    parts = line.split()
                    if len(parts) >= 1:
                        path = parts[0]
                        if path.startswith("/"):
                            get_routes.append(path)
            
            print(f"从现有文件获取到 {len(get_routes)} 个路由")
            return get_routes
        except Exception as e2:
            print(f"❌ 从文件读取路由失败: {e2}")
            return []

def test_get_endpoint_with_auth(route: str, token: str) -> Tuple[int, str, Optional[str]]:
    """测试单个GET端点（带认证）"""
    url = BASE_URL + route
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        status_code = response.status_code
        
        # 尝试解析响应
        try:
            if response.content:
                data = response.json()
                # 简化数据表示
                if isinstance(data, dict):
                    summary = json.dumps(data, ensure_ascii=False)[:200]
                else:
                    summary = str(data)[:200]
            else:
                summary = "空响应"
        except:
            summary = response.text[:200] if response.text else "无文本响应"
        
        return status_code, summary, None
        
    except requests.exceptions.Timeout:
        return 0, "请求超时", "timeout"
    except Exception as e:
        return 0, f"请求异常: {e}", "error"

def main():
    print("=" * 70)
    print("带鉴权的全模块GET冒烟测试")
    print("=" * 70)
    
    # 1. 获取认证令牌
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证令牌，测试终止")
        sys.exit(1)
    
    # 2. 获取所有GET路由
    print("\n" + "-" * 70)
    print("获取路由列表...")
    routes = get_all_get_routes()
    
    if not routes:
        print("❌ 未找到任何路由，测试终止")
        sys.exit(1)
    
    print(f"找到 {len(routes)} 个路由进行测试")
    
    # 3. 测试每个路由
    print("\n" + "-" * 70)
    print("开始测试...")
    
    results = []
    success_count = 0
    auth_failures = 0
    other_failures = 0
    
    for i, route in enumerate(routes, 1):
        print(f"[{i}/{len(routes)}] 测试: {route}")
        
        status_code, summary, error_type = test_get_endpoint_with_auth(route, token)
        
        # 记录结果
        if status_code == 200:
            success_count += 1
            status_display = "✅ 200"
        elif status_code == 401:
            auth_failures += 1
            status_display = "🔐 401 (认证失败)"
        elif status_code == 403:
            auth_failures += 1
            status_display = "🚫 403 (权限不足)"
        elif status_code == 404:
            other_failures += 1
            status_display = "❓ 404 (未找到)"
        elif status_code == 422:
            other_failures += 1
            status_display = "⚠️  422 (参数验证失败)"
        elif status_code == 0:
            other_failures += 1
            status_display = "⏱️  0 (请求错误)"
        else:
            other_failures += 1
            status_display = f"❌ {status_code}"
        
        result_line = f"{route}\t{status_code}\t{summary}"
        results.append(result_line)
        
        print(f"    结果: {status_display}")
        if summary and summary != "空响应":
            print(f"    摘要: {summary}")
    
    # 4. 生成报告
    print("\n" + "=" * 70)
    print("测试结果汇总:")
    print(f"  总路由数: {len(routes)}")
    print(f"  成功 (200): {success_count}")
    print(f"  认证失败 (401/403): {auth_failures}")
    print(f"  其他失败: {other_failures}")
    print(f"  成功率: {success_count/len(routes)*100:.1f}%")
    
    # 保存结果
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 带鉴权的全模块GET冒烟测试结果\n")
        f.write(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 测试URL: {BASE_URL}\n")
        f.write(f"# 总路由数: {len(routes)}\n")
        f.write(f"# 成功: {success_count}, 认证失败: {auth_failures}, 其他失败: {other_failures}\n")
        f.write("#" * 80 + "\n")
        for result in results:
            f.write(result + "\n")
    
    print(f"\n详细结果已保存到: {OUTPUT_FILE}")
    
    # 5. 输出有问题的路由
    if auth_failures > 0:
        print("\n🔍 认证失败的路由:")
        for result in results:
            if "401" in result or "403" in result:
                parts = result.split("\t")
                print(f"  {parts[0]} - {parts[1]}")
    
    if other_failures > 0:
        print("\n🔍 其他失败的路由:")
        for result in results:
            if "404" in result or "422" in result or "0" in result:
                parts = result.split("\t")
                print(f"  {parts[0]} - {parts[1]}")
    
    print("\n" + "=" * 70)
    print("测试完成!")

if __name__ == "__main__":
    main()