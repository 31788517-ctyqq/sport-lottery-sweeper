#!/usr/bin/env python3
"""
LLM供应商管理端到端工作流测试
使用正确的响应解析
"""

import requests
import json
import time
import sys

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers"

# 测试用户凭据
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def get_headers(token=None):
    """获取包含认证token的请求头"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def login():
    """用户登录获取JWT令牌"""
    print("1. 用户登录...")
    try:
        response = requests.post(
            LOGIN_URL,
            json=TEST_USER,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # 提取嵌套的access_token
            token = data.get("data", {}).get("access_token")
            if token:
                print(f"   成功，token: {token[:30]}...")
                return token
            else:
                print(f"   失败: 响应中未找到token")
                print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return None
        else:
            print(f"   失败: 状态码 {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"   异常: {e}")
        return None

def create_provider(token):
    """创建LLM供应商"""
    print("\n2. 创建LLM供应商...")
    
    provider_data = {
        "name": f"test-openai-{int(time.time())}",
        "provider_type": "openai",
        "description": "用于端到端测试的OpenAI供应商",
        "api_key": "sk-test-key-1234567890abcdef",  # 模拟密钥
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-3.5-turbo",
        "enabled": True,
        "priority": 5,
        "max_requests_per_minute": 60,
        "timeout_seconds": 30
    }
    
    try:
        response = requests.post(
            LLM_PROVIDERS_URL,
            json=provider_data,
            headers=get_headers(token),
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            provider_id = data.get("id")
            print(f"   成功，ID: {provider_id}")
            print(f"   名称: {data.get('name')}")
            print(f"   类型: {data.get('provider_type')}")
            print(f"   健康状态: {data.get('health_status')}")
            return provider_id
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"   异常: {e}")
        return None

def list_providers(token):
    """获取LLM供应商列表"""
    print("\n3. 获取LLM供应商列表...")
    
    try:
        response = requests.get(
            LLM_PROVIDERS_URL,
            headers=get_headers(token),
            params={"limit": 10},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            providers = data
            if isinstance(data, dict) and "data" in data:
                providers = data["data"]
            
            print(f"   成功，获取到 {len(providers)} 个供应商")
            
            for i, provider in enumerate(providers[:3]):
                print(f"   {i+1}. {provider.get('name')} ({provider.get('provider_type')}) - {provider.get('health_status')}")
            
            return True
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def get_provider(token, provider_id):
    """获取单个供应商详情"""
    print(f"\n4. 获取供应商详情 (ID: {provider_id})...")
    
    try:
        response = requests.get(
            f"{LLM_PROVIDERS_URL}/{provider_id}",
            headers=get_headers(token),
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功")
            print(f"   名称: {data.get('name')}")
            print(f"   类型: {data.get('provider_type')}")
            print(f"   启用: {data.get('enabled')}")
            print(f"   健康状态: {data.get('health_status')}")
            return True
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def test_connection(token, provider_id):
    """测试供应商连接"""
    print(f"\n5. 测试供应商连接 (ID: {provider_id})...")
    
    test_data = {
        "test_prompt": "Hello, please respond with 'OK' to confirm connectivity.",
        "timeout_ms": 5000
    }
    
    try:
        response = requests.post(
            f"{LLM_PROVIDERS_URL}/{provider_id}/test",
            json=test_data,
            headers=get_headers(token),
            timeout=15  # 给测试更多时间
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   测试完成")
            print(f"   成功: {data.get('success')}")
            print(f"   消息: {data.get('message')}")
            print(f"   响应时间: {data.get('response_time_ms', 'N/A')}ms")
            return True
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def update_provider(token, provider_id):
    """更新供应商信息"""
    print(f"\n6. 更新供应商信息 (ID: {provider_id})...")
    
    update_data = {
        "description": "更新后的描述 - 端到端测试完成",
        "priority": 3,
        "max_requests_per_minute": 100
    }
    
    try:
        response = requests.put(
            f"{LLM_PROVIDERS_URL}/{provider_id}",
            json=update_data,
            headers=get_headers(token),
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功")
            print(f"   新描述: {data.get('description')}")
            print(f"   新优先级: {data.get('priority')}")
            print(f"   新请求限制: {data.get('max_requests_per_minute')}")
            return True
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def toggle_status(token, provider_id):
    """禁用并重新启用供应商"""
    print(f"\n7. 测试启用/禁用功能 (ID: {provider_id})...")
    
    # 禁用
    try:
        response = requests.post(
            f"{LLM_PROVIDERS_URL}/{provider_id}/disable",
            headers=get_headers(token),
            timeout=10
        )
        
        print(f"   禁用状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   禁用成功")
            print(f"   启用状态: {data.get('enabled')}")
            
            time.sleep(1)
            
            # 启用
            response = requests.post(
                f"{LLM_PROVIDERS_URL}/{provider_id}/enable",
                headers=get_headers(token),
                timeout=10
            )
            
            print(f"   启用状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   启用成功")
                print(f"   启用状态: {data.get('enabled')}")
                return True
            else:
                print(f"   启用失败")
                print(f"   响应: {response.text}")
                return False
        else:
            print(f"   禁用失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def get_stats(token):
    """获取供应商统计信息"""
    print("\n8. 获取LLM供应商统计概览...")
    
    try:
        response = requests.get(
            f"{LLM_PROVIDERS_URL}/stats/overview",
            headers=get_headers(token),
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功")
            print(f"   总供应商数: {data.get('total_providers', 'N/A')}")
            print(f"   启用供应商数: {data.get('enabled_providers', 'N/A')}")
            print(f"   健康供应商数: {data.get('healthy_providers', 'N/A')}")
            print(f"   本月总成本: ¥{data.get('monthly_total_cost', 0) / 100:.2f}")
            return True
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def delete_provider(token, provider_id):
    """删除供应商"""
    print(f"\n9. 删除供应商 (ID: {provider_id})...")
    
    try:
        response = requests.delete(
            f"{LLM_PROVIDERS_URL}/{provider_id}",
            headers=get_headers(token),
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功")
            print(f"   消息: {data.get('message')}")
            return True
        else:
            print(f"   失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("LLM供应商管理端到端工作流测试")
    print("=" * 60)
    
    results = {}
    
    # 1. 登录
    token = login()
    if not token:
        print("\n[失败] 登录失败，无法继续测试")
        return False
    results["login"] = True
    
    # 2. 创建供应商
    provider_id = create_provider(token)
    if provider_id:
        results["create"] = True
    else:
        results["create"] = False
        print("\n[警告] 供应商创建失败，部分测试将被跳过")
    
    # 3. 获取供应商列表
    list_ok = list_providers(token)
    results["list"] = list_ok
    
    # 4. 获取单个供应商详情
    if provider_id:
        get_ok = get_provider(token, provider_id)
        results["get"] = get_ok
    
    # 5. 测试连接
    if provider_id:
        test_ok = test_connection(token, provider_id)
        results["test"] = test_ok
    
    # 6. 更新供应商
    if provider_id:
        update_ok = update_provider(token, provider_id)
        results["update"] = update_ok
    
    # 7. 测试启用/禁用
    if provider_id:
        toggle_ok = toggle_status(token, provider_id)
        results["toggle"] = toggle_ok
    
    # 8. 获取统计
    stats_ok = get_stats(token)
    results["stats"] = stats_ok
    
    # 9. 删除供应商
    if provider_id:
        delete_ok = delete_provider(token, provider_id)
        results["delete"] = delete_ok
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "通过" if passed else "失败"
        print(f"  {test_name:10} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    print(f"\n  总计: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        print("\n[成功] 所有测试通过！LLM供应商管理功能完整可用。")
        return True
    else:
        print(f"\n[警告] 部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[失败] 测试运行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)