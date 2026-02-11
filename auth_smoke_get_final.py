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
import logging
import re

# 配置日志，避免Unicode问题
logging.basicConfig(level=logging.INFO, format='%(message)s')

# 配置
BASE_URL = "http://127.0.0.1:8000"
LOGIN_ENDPOINT = "/api/v1/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"

# 输出文件
OUTPUT_FILE = "auth_smoke_get_results_latest.txt"
TIMEOUT = 10

def get_auth_token() -> Optional[str]:
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    print(f"正在登录: {login_url}")
    try:
        response = requests.post(login_url, json=payload, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            # 提取令牌
            if "access_token" in data:
                token = data["access_token"]
            elif "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
            else:
                token = None
            
            if token:
                print(f"登录成功，令牌获取成功")
                return token
            else:
                print(f"登录响应中未找到令牌字段")
        else:
            print(f"登录失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"登录请求异常: {e}")
    
    return None

def get_all_get_routes_from_app() -> List[str]:
    """从FastAPI应用实例获取所有GET路由"""
    try:
        # 导入应用
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.main import app
        
        get_routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and 'GET' in route.methods:
                get_routes.append(route.path)
        
        print(f"从应用实例获取到 {len(get_routes)} 个GET路由")
        return sorted(set(get_routes))
    except Exception as e:
        print(f"从应用实例获取路由失败: {e}")
        return []

def get_all_get_routes_from_openapi() -> List[str]:
    """?????????OpenAPI????"""
    try:
        url = f"{BASE_URL}/openapi.json"
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"OpenAPI????: {resp.status_code}")
            return []
        data = resp.json()
        routes = []
        for path, methods in data.get("paths", {}).items():
            if "get" in {m.lower() for m in methods.keys()}:
                routes.append(path)
        print(f"?OpenAPI??? {len(routes)} ?GET??")
        return sorted(set(routes))
    except Exception as e:
        print(f"?OpenAPI??????: {e}")
        return []

def get_all_get_routes_from_scanner() -> List[str]:
    """使用扫描器获取所有GET路由"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.scanner.api_scanner import APIScanner
        
        scanner = APIScanner()
        report = scanner.scan_directory("api/v1")
        
        get_routes = []
        if "routes" in report:
            for route in report["routes"]:
                if "methods" in route and "GET" in route["methods"]:
                    get_routes.append(route["path"])
        
        print(f"从扫描器获取到 {len(get_routes)} 个GET路由")
        return sorted(set(get_routes))
    except Exception as e:
        print(f"使用扫描器获取路由失败: {e}")
        return []

def filter_v1_routes(routes: List[str]) -> List[str]:
    """仅保留/api/v1前缀路由，避免兼容路径偏离启动规范"""
    return sorted({r for r in routes if r.startswith("/api/v1")})


def get_all_get_routes() -> List[str]:
    """获取所有GET路由，尝试多种方法（仅保留/api/v1）"""
    # 方法0: 从OpenAPI获取（最接近运行实例）
    routes = get_all_get_routes_from_openapi()
    if routes:
        return filter_v1_routes(routes)

    # 方法1: 从应用实例获取
    routes = get_all_get_routes_from_app()
    if routes:
        return filter_v1_routes(routes)
    
    # 方法2: 使用扫描器
    routes = get_all_get_routes_from_scanner()
    if routes:
        return filter_v1_routes(routes)
    
    # 方法3: 从现有结果文件读取
    try:
        with open("smoke_get_results.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        get_routes = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 1:
                    path = parts[0]
                    if path.startswith("/"):
                        get_routes.append(path)
        
        print(f"从现有文件获取到 {len(get_routes)} 个路由")
        return filter_v1_routes(get_routes)
    except Exception as e:
        print(f"从文件读取路由失败: {e}")
        return []

def test_get_endpoint_with_auth(route: str, token: str) -> Tuple[int, str, Optional[str]]:
    """测试单个GET端点（带认证）"""
    url = BASE_URL + route
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        status_code = response.status_code
        
        # 尝试解析响应
        try:
            if response.content:
                data = response.json()
                # 简化数据表示
                if isinstance(data, dict):
                    summary = json.dumps(data, ensure_ascii=False)[:150]
                else:
                    summary = str(data)[:150]
            else:
                summary = "空响应"
        except:
            summary = response.text[:150] if response.text else "无文本响应"
        
        return status_code, summary, None
        
    except requests.exceptions.Timeout:
        return 0, "请求超时", "timeout"
    except Exception as e:
        return 0, f"请求异常: {e}", "error"

def resolve_route_params(route: str) -> str:
    """?????????????422"""
    param_matches = re.findall(r"\{([^}]+)\}", route)
    if not param_matches:
        return route

    def sample_for(name: str) -> str:
        name_l = name.lower()
        if "uuid" in name_l:
            return "00000000-0000-4000-8000-000000000000"
        if "date" in name_l:
            return "2025-01-01"
        if "time" in name_l:
            return "2025-01-01T00:00:00"
        if "code" in name_l:
            return "test"
        if "name" in name_l:
            return "test"
        if "id" in name_l:
            return "1"
        return "1"

    for name in param_matches:
        route = route.replace("{" + name + "}", sample_for(name))
    return route


def attach_required_query(route: str) -> str:
    """?????query????"""
    if route.endswith("/search"):
        sep = "&" if "?" in route else "?"
        return f"{route}{sep}q=test"
    return route


def main():
    print("=" * 70)
    print("带鉴权的全模块GET冒烟测试")
    print("=" * 70)
    
    # 1. 获取认证令牌
    token = get_auth_token()
    if not token:
        print("无法获取认证令牌，测试终止")
        sys.exit(1)
    
    # 2. 获取所有GET路由
    print("\n" + "-" * 70)
    print("获取路由列表...")
    routes = get_all_get_routes()
    
    if not routes:
        print("未找到任何路由，测试终止")
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
        test_route = attach_required_query(resolve_route_params(route))
        print(f"[{i}/{len(routes)}] 测试: {test_route}")
        
        status_code, summary, error_type = test_get_endpoint_with_auth(test_route, token)
        
        # 统计
        if 200 <= status_code < 300:
            success_count += 1
            status_display = f"200"
        elif status_code == 401:
            auth_failures += 1
            status_display = "401"
        elif status_code == 403:
            auth_failures += 1
            status_display = "403"
        elif status_code == 404:
            other_failures += 1
            status_display = "404"
        elif status_code == 422:
            other_failures += 1
            status_display = "422"
        elif status_code == 0:
            other_failures += 1
            status_display = "0"
        else:
            other_failures += 1
            status_display = f"{status_code}"
        
        result_line = f"{test_route}\t{status_code}"
        results.append(result_line)
        
        print(f"    状态码: {status_display}")
        if summary and summary != "空响应":
            print(f"    摘要: {summary}")
    
    # 4. 生成报告
    print("\n" + "=" * 70)
    print("测试结果汇总:")
    print(f"  总路由数: {len(routes)}")
    print(f"  成功 (2xx): {success_count}")
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
        print("\n认证失败的路由:")
        for result in results:
            if "401" in result or "403" in result:
                parts = result.split("\t")
                print(f"  {parts[0]} - {parts[1]}")
    
    if other_failures > 0:
        print("\n其他失败的路由:")
        for result in results:
            if "404" in result or "422" in result or "0" in result:
                parts = result.split("\t")
                print(f"  {parts[0]} - {parts[1]}")
    
    print("\n" + "=" * 70)
    print("测试完成!")

if __name__ == "__main__":
    main()
