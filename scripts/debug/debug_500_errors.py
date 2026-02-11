#!/usr/bin/env python3
"""
调试500错误路由脚本
获取详细的错误信息，包括响应正文和可能的异常堆栈
"""
import sys
import json
import time
import requests
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置
BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = "/api/auth/login"
ADMIN_CREDENTIALS = {
    "username": "sa_mock_data_2026_01_19",
    "password": "SuperAdmin@123456"
}

def get_auth_token():
    """获取JWT令牌"""
    try:
        response = requests.post(
            f"{BASE_URL}{AUTH_ENDPOINT}",
            json=ADMIN_CREDENTIALS,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"认证失败: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"认证请求异常: {e}")
        return None

def test_route_with_details(route, token):
    """测试单个路由并返回详细信息"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{route}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        result = {
            "route": route,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "success": 200 <= response.status_code < 300
        }
        
        # 尝试解析响应正文
        try:
            if response.text:
                result["response_text"] = response.text[:1000]  # 限制长度
                # 尝试解析JSON
                if "application/json" in response.headers.get("Content-Type", ""):
                    result["response_json"] = response.json()
        except:
            result["response_text"] = response.text[:1000] if response.text else ""
            
        return result
        
    except Exception as e:
        return {
            "route": route,
            "status_code": 0,
            "error": str(e),
            "success": False
        }

def main():
    print("开始调试500错误路由...")
    
    # 获取令牌
    print("获取认证令牌...")
    token = get_auth_token()
    if not token:
        print("无法获取认证令牌，退出")
        return
    
    print(f"令牌获取成功: {token[:50]}...")
    
    # 从结果文件中读取500错误路由
    results_file = Path(__file__).parent / "auth_smoke_get_results.txt"
    if not results_file.exists():
        print("结果文件不存在")
        return
    
    error_500_routes = []
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '\t' in line:
                route, status = line.split('\t', 1)
                if status == '500':
                    error_500_routes.append(route)
    
    print(f"找到 {len(error_500_routes)} 个500错误路由")
    
    # 测试前10个路由（避免太多请求）
    test_routes = error_500_routes[:10]
    detailed_results = []
    
    for i, route in enumerate(test_routes):
        print(f"测试路由 {i+1}/{len(test_routes)}: {route}")
        result = test_route_with_details(route, token)
        detailed_results.append(result)
        
        # 打印摘要
        if result.get('error'):
            print(f"  错误: {result['error']}")
        else:
            print(f"  状态码: {result['status_code']}")
            if result['status_code'] == 500:
                print(f"  响应: {result.get('response_text', '')[:200]}")
        
        # 短暂延迟避免过载
        time.sleep(0.5)
    
    # 保存详细结果
    output_file = Path(__file__).parent / "debug_500_details.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: {output_file}")
    
    # 分析结果
    print("\n=== 500错误分析 ===")
    for result in detailed_results:
        if result.get('status_code') == 500:
            print(f"\n路由: {result['route']}")
            if 'response_text' in result:
                # 尝试提取错误信息
                text = result['response_text']
                if 'detail' in text:
                    import re
                    detail_match = re.search(r'"detail":\s*"([^"]+)"', text)
                    if detail_match:
                        print(f"  错误详情: {detail_match.group(1)}")
                else:
                    print(f"  响应片段: {text[:300]}")
    
    print("\n调试完成")

if __name__ == "__main__":
    main()