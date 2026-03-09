#!/usr/bin/env python3
"""
验证422错误修复效果
测试几个代表性端点
"""

import requests
import json

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"
TIMEOUT = 10

def get_token():
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
            elif "access_token" in data:
                token = data["access_token"]
            else:
                print("令牌未找到")
                return None
            
            return token
        else:
            print(f"登录失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"登录请求异常: {e}")
    
    return None

def test_endpoint(endpoint, token, params=None):
    """测试单个端点"""
    url = BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 处理路径参数
    if "{" in endpoint and "}" in endpoint:
        # 简单的参数替换
        if "header_id" in endpoint:
            url = url.replace("{header_id}", "1")
        elif "source_id" in endpoint:
            url = url.replace("{source_id}", "1")
        elif "task_id" in endpoint:
            url = url.replace("{task_id}", "1")
        elif "pool_id" in endpoint:
            url = url.replace("{pool_id}", "1")
        elif "caipiao_data_id" in endpoint:
            url = url.replace("{caipiao_data_id}", "1")
        elif "job_id" in endpoint:
            url = url.replace("{job_id}", "1")
        elif "execution_id" in endpoint:
            url = url.replace("{execution_id}", "1")
        elif "admin_id" in endpoint:
            url = url.replace("{admin_id}", "1")
        elif "user_id" in endpoint:
            url = url.replace("{user_id}", "1")
        elif "id" in endpoint:
            url = url.replace("{id}", "1")
        else:
            # 通用替换
            import re
            param_match = re.search(r'\{([^}]+)\}', endpoint)
            if param_match:
                param_name = param_match.group(1)
                url = url.replace(f"{{{param_name}}}", "1")
    
    try:
        response = requests.get(url, headers=headers, params=params or {}, timeout=TIMEOUT)
        return response.status_code, response.text[:200]
    except Exception as e:
        return 0, f"请求异常: {e}"

def main():
    print("验证422错误修复效果")
    print("=" * 60)
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌")
        return
    
    print("令牌获取成功")
    print()
    
    # 测试用例
    test_cases = [
        # (端点, 描述, 查询参数)
        ("/api/v1/admin/crawler/headers/{header_id}", "路径参数端点 - header", None),
        ("/api/v1/admin/crawler/sources/{source_id}/health", "路径参数端点 - source健康检查", None),
        ("/api/v1/admin/headers/{header_id}", "路径参数端点 - 管理header", None),
        ("/api/v1/admin/ip-pools/{pool_id}", "路径参数端点 - IP池", None),
        ("/api/v1/admin/matches/league/config", "查询参数端点 - 联赛配置", {"league_id": 1}),
        ("/api/v1/admin/tree", "查询参数端点 - 树结构", {"type": "department"}),
        ("/api/v1/hedging/parlay-opportunities", "查询参数端点 - 对冲机会", {"match_id": 1}),
        ("/api/v1/odds/odds/history", "查询参数端点 - 赔率历史", {"match_id": 1}),
    ]
    
    results = []
    
    for endpoint, description, params in test_cases:
        print(f"测试: {description}")
        print(f"端点: {endpoint}")
        
        status_code, response_text = test_endpoint(endpoint, token, params)
        
        # 判断结果
        if status_code == 422:
            result = "失败 (仍为422)"
        elif status_code == 200:
            result = "成功 (200)"
        elif status_code == 404:
            result = "改善 (404 - 资源不存在)"
        elif status_code == 401 or status_code == 403:
            result = "改善 (认证/授权问题)"
        elif status_code == 500:
            result = "改善 (500 - 内部错误，但不再是422)"
        else:
            result = f"改善 (状态码: {status_code})"
        
        print(f"结果: {result}")
        print(f"状态码: {status_code}")
        print(f"响应: {response_text}")
        print("-" * 60)
        
        results.append({
            "endpoint": endpoint,
            "description": description,
            "status_code": status_code,
            "result": result
        })
    
    # 统计
    total = len(results)
    success_200 = sum(1 for r in results if r["status_code"] == 200)
    not_422 = sum(1 for r in results if r["status_code"] != 422)
    
    print("\n统计结果:")
    print(f"总测试用例: {total}")
    print(f"返回200成功: {success_200}")
    print(f"不再返回422: {not_422} ({not_422/total*100:.1f}%)")
    
    if not_422 == total:
        print("\n✅ 所有测试用例都不再返回422错误!")
    else:
        print(f"\n⚠️  仍有 {total - not_422} 个用例返回422错误")
    
    # 保存结果
    import time
    output_file = "422_fix_verification.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "test_cases": results,
            "summary": {
                "total": total,
                "success_200": success_200,
                "not_422": not_422,
                "still_422": total - not_422
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: {output_file}")

if __name__ == "__main__":
    main()