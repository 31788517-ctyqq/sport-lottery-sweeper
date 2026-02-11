#!/usr/bin/env python3
"""
测试修复后的500错误端点
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

def test_endpoint(endpoint, token, path_params=None, expected_status=None):
    """测试单个端点"""
    url = BASE_URL + endpoint
    
    # 替换路径参数
    if path_params:
        for key, value in path_params.items():
            placeholder = f"{{{key}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*80}")
    print(f"测试端点: {endpoint}")
    print(f"完整URL: {url}")
    if path_params:
        print(f"路径参数: {path_params}")
    if expected_status:
        print(f"期望状态码: {expected_status}")
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        status_code = response.status_code
        
        print(f"实际状态码: {status_code}")
        print(f"响应预览: {response.text[:200]}")
        
        if expected_status and status_code == expected_status:
            print(f"[OK] 符合期望")
        elif not expected_status and status_code != 500:
            print(f"[OK] 不再是500错误")
        else:
            print(f"[ERROR] 不符合期望")
            
        return status_code, response.text[:500]
    except Exception as e:
        print(f"请求异常: {e}")
        return 0, str(e)

def main():
    print("测试修复后的500错误端点")
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌")
        return
    
    print("令牌获取成功")
    
    # 测试之前有问题的端点
    test_cases = [
        {
            "endpoint": "/api/v1/admin/crawler/headers/{header_id}",
            "description": "爬虫请求头详情",
            "path_params": {"header_id": 999},  # 使用不存在的ID
            "expected_status": 404  # 资源不存在应该返回404
        },
        {
            "endpoint": "/api/v1/admin/headers/{header_id}",
            "description": "管理请求头详情",
            "path_params": {"header_id": 999},
            "expected_status": 404
        },
        {
            "endpoint": "/api/v1/admin/ip-pools/{pool_id}",
            "description": "IP池详情",
            "path_params": {"pool_id": 999},
            "expected_status": 404
        },
        {
            "endpoint": "/api/v1/admin/users/admin/{admin_id}",
            "description": "管理员详情",
            "path_params": {"admin_id": 999},
            "expected_status": 404  # 也可能是500，但至少不应该返回500因为资源不存在
        }
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n测试: {case['description']}")
        status_code, response = test_endpoint(
            case["endpoint"],
            token,
            case.get("path_params"),
            case.get("expected_status")
        )
        
        results.append({
            "endpoint": case["endpoint"],
            "description": case["description"],
            "status_code": status_code,
            "expected_status": case.get("expected_status"),
            "response_preview": response[:200]
        })
    
    # 分析结果
    print(f"\n{'='*80}")
    print("分析结果:")
    print(f"{'='*80}")
    
    total = len(results)
    success_404 = sum(1 for r in results if r["status_code"] == 404 and r["expected_status"] == 404)
    still_500 = sum(1 for r in results if r["status_code"] == 500)
    other_status = sum(1 for r in results if r["status_code"] not in [404, 500])
    
    print(f"总测试用例: {total}")
    print(f"正确返回404: {success_404}")
    print(f"仍返回500: {still_500}")
    print(f"其他状态码: {other_status}")
    
    print(f"\n详细结果:")
    for r in results:
        status = r["status_code"]
        expected = r["expected_status"]
        
        if status == 404 and expected == 404:
            indicator = "[OK]"
        elif status == 500:
            indicator = "[ERROR]"
        else:
            indicator = "[WARN]"
            
        print(f"{indicator} {r['description']}: 状态码 {status} (期望: {expected})")
    
    # 总结
    print(f"\n{'='*80}")
    print("修复总结:")
    print(f"{'='*80}")
    
    if still_500 > 0:
        print(f"⚠️  仍有 {still_500} 个端点返回500错误")
        for r in results:
            if r["status_code"] == 500:
                print(f"  • {r['endpoint']}")
    else:
        print("✅ 所有测试端点都不再返回500错误!")
    
    if success_404 == 3:  # 前三个端点应该返回404
        print("✅ 资源不存在时正确返回404状态码")
    else:
        print(f"⚠️  只有 {success_404}/3 个资源不存在端点返回404")

if __name__ == "__main__":
    main()