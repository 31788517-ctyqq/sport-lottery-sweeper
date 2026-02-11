#!/usr/bin/env python3
"""
诊断修复422后暴露的5个500错误端点
"""

import requests
import json
import time

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

def test_endpoint(endpoint, token, params=None, path_params=None):
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
    
    try:
        response = requests.get(url, headers=headers, params=params or {}, timeout=TIMEOUT)
        return response.status_code, response.text[:500]
    except Exception as e:
        return 0, f"请求异常: {e}"

def main():
    print("诊断修复422后暴露的500错误端点")
    print("=" * 70)
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌")
        return
    
    print("令牌获取成功")
    print()
    
    # 根据之前报告，这些端点可能返回500
    # 让我们测试这些端点（提供有效路径参数）
    test_cases = [
        {
            "endpoint": "/api/v1/admin/crawler/headers/{header_id}",
            "description": "爬虫请求头详情",
            "path_params": {"header_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/headers/{header_id}",
            "description": "管理请求头详情",
            "path_params": {"header_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/ip-pools/{pool_id}",
            "description": "IP池详情",
            "path_params": {"pool_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/crawler/sources/{source_id}/health",
            "description": "数据源健康检查",
            "path_params": {"source_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/sources/{source_id}",
            "description": "数据源详情",
            "path_params": {"source_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/sources/{source_id}/health",
            "description": "数据源健康检查(重复)",
            "path_params": {"source_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/tasks/{task_id}",
            "description": "任务详情",
            "path_params": {"task_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/tasks/{task_id}/logs",
            "description": "任务日志",
            "path_params": {"task_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/user-profiles/{user_id}",
            "description": "用户资料详情",
            "path_params": {"user_id": 1},
            "query_params": None
        },
        {
            "endpoint": "/api/v1/admin/users/admin/{admin_id}",
            "description": "管理员详情",
            "path_params": {"admin_id": 1},
            "query_params": None
        },
    ]
    
    results = []
    
    for case in test_cases:
        endpoint = case["endpoint"]
        description = case["description"]
        path_params = case["path_params"]
        query_params = case["query_params"]
        
        print(f"测试: {description}")
        print(f"端点: {endpoint}")
        print(f"路径参数: {path_params}")
        
        status_code, response_text = test_endpoint(endpoint, token, query_params, path_params)
        
        print(f"状态码: {status_code}")
        print(f"响应预览: {response_text[:200]}...")
        print("-" * 70)
        
        results.append({
            "endpoint": endpoint,
            "description": description,
            "path_params": path_params,
            "status_code": status_code,
            "response_preview": response_text[:200]
        })
    
    # 分析结果
    print("\n分析结果:")
    print("=" * 70)
    
    success_200 = sum(1 for r in results if r["status_code"] == 200)
    not_found_404 = sum(1 for r in results if r["status_code"] == 404)
    internal_error_500 = sum(1 for r in results if r["status_code"] == 500)
    validation_error_422 = sum(1 for r in results if r["status_code"] == 422)
    other_status = sum(1 for r in results if r["status_code"] not in [200, 404, 500, 422])
    
    print(f"总测试用例: {len(results)}")
    print(f"成功 (200): {success_200}")
    print(f"资源不存在 (404): {not_found_404}")
    print(f"内部错误 (500): {internal_error_500}")
    print(f"验证错误 (422): {validation_error_422}")
    print(f"其他状态码: {other_status}")
    
    print("\n详细分类:")
    
    if internal_error_500 > 0:
        print(f"\n❌ 发现 {internal_error_500} 个500内部错误:")
        for r in results:
            if r["status_code"] == 500:
                print(f"  • {r['endpoint']} (参数: {r['path_params']})")
                print(f"    响应: {r['response_preview']}")
    
    if success_200 > 0:
        print(f"\n✅ {success_200} 个端点成功返回200:")
        for r in results:
            if r["status_code"] == 200:
                print(f"  • {r['endpoint']}")
    
    if not_found_404 > 0:
        print(f"\nℹ️  {not_found_404} 个端点返回404 (资源不存在，正常业务逻辑):")
        for r in results:
            if r["status_code"] == 404:
                print(f"  • {r['endpoint']}")
    
    if validation_error_422 > 0:
        print(f"\n⚠️  {validation_error_422} 个端点仍返回422 (需要其他参数):")
        for r in results:
            if r["status_code"] == 422:
                print(f"  • {r['endpoint']}")
    
    # 保存结果
    output_file = "500_errors_diagnosis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "test_cases": results,
            "summary": {
                "total": len(results),
                "success_200": success_200,
                "not_found_404": not_found_404,
                "internal_error_500": internal_error_500,
                "validation_error_422": validation_error_422,
                "other_status": other_status
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: {output_file}")
    
    # 提供修复建议
    if internal_error_500 > 0:
        print(f"\n🔧 修复建议:")
        print("1. 检查数据库表结构是否完整")
        print("2. 验证模型类属性是否正确")
        print("3. 检查异常处理逻辑，确保记录不存在时返回404而非500")
        print("4. 确保数据库连接正常")

if __name__ == "__main__":
    main()