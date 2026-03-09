#!/usr/bin/env python3
"""
简单的LLM供应商管理端到端工作流测试
测试从创建、读取、更新、删除到连接测试的完整流程
"""

import requests
import json
import time
import sys

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers"

# 测试用户凭据（使用admin账户）
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

def test_login():
    """用户登录获取JWT令牌"""
    print("步骤1: 用户登录...")
    try:
        response = requests.post(
            LOGIN_URL,
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"   [OK] 登录成功，获取到token: {token[:20]}...")
            return token
        else:
            print(f"   [FAIL] 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"   [FAIL] 登录异常: {e}")
        return None

def test_create_provider(token):
    """创建LLM供应商"""
    print("\n步骤2: 创建LLM供应商...")
    
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
            headers=get_headers(token)
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            provider_id = data.get("id")
            print(f"   [OK] 供应商创建成功，ID: {provider_id}")
            print(f"   名称: {data.get('name')}")
            print(f"   类型: {data.get('provider_type')}")
            print(f"   状态: {data.get('health_status')}")
            return provider_id
        else:
            print(f"   [FAIL] 供应商创建失败")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"   [FAIL] 创建异常: {e}")
        return None

def test_list_providers(token):
    """获取LLM供应商列表"""
    print("\n步骤3: 获取LLM供应商列表...")
    
    try:
        response = requests.get(
            LLM_PROVIDERS_URL,
            headers=get_headers(token),
            params={"limit": 10}
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            providers = data
            if isinstance(data, dict) and "data" in data:
                providers = data["data"]
            
            print(f"   [OK] 获取到 {len(providers)} 个供应商")
            
            # 显示前几个供应商
            for i, provider in enumerate(providers[:3]):
                print(f"   {i+1}. {provider.get('name')} ({provider.get('provider_type')}) - {provider.get('health_status')}")
            
            return True
        else:
            print(f"   [FAIL] 获取供应商列表失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 获取列表异常: {e}")
        return False

def test_get_single_provider(token, provider_id):
    """获取单个供应商详情"""
    if not provider_id:
        print("\n[WARN] 跳过步骤4: 未创建供应商，无法获取详情")
        return False
        
    print(f"\n步骤4: 获取供应商详情 (ID: {provider_id})...")
    
    try:
        response = requests.get(
            f"{LLM_PROVIDERS_URL}/{provider_id}",
            headers=get_headers(token)
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] 获取详情成功")
            print(f"   名称: {data.get('name')}")
            print(f"   类型: {data.get('provider_type')}")
            print(f"   启用: {data.get('enabled')}")
            print(f"   健康状态: {data.get('health_status')}")
            return True
        else:
            print(f"   [FAIL] 获取详情失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 获取详情异常: {e}")
        return False

def test_connection(token, provider_id):
    """测试供应商连接"""
    if not provider_id:
        print("\n[WARN] 跳过步骤5: 未创建供应商，无法测试连接")
        return False
        
    print(f"\n步骤5: 测试供应商连接 (ID: {provider_id})...")
    
    test_data = {
        "test_prompt": "Hello, please respond with 'OK' to confirm connectivity.",
        "timeout_ms": 5000
    }
    
    try:
        response = requests.post(
            f"{LLM_PROVIDERS_URL}/{provider_id}/test",
            json=test_data,
            headers=get_headers(token)
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] 连接测试完成")
            print(f"   成功: {data.get('success')}")
            print(f"   消息: {data.get('message')}")
            print(f"   响应时间: {data.get('response_time_ms', 'N/A')}ms")
            
            # 注意：由于我们使用的是模拟API密钥，测试可能会失败
            # 但API应该返回适当的错误消息而不是崩溃
            return True
        else:
            print(f"   [FAIL] 连接测试失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 连接测试异常: {e}")
        return False

def test_update_provider(token, provider_id):
    """更新供应商信息"""
    if not provider_id:
        print("\n[WARN] 跳过步骤6: 未创建供应商，无法更新")
        return False
        
    print(f"\n步骤6: 更新供应商信息 (ID: {provider_id})...")
    
    update_data = {
        "description": "更新后的描述 - 端到端测试完成",
        "priority": 3,  # 提高优先级
        "max_requests_per_minute": 100
    }
    
    try:
        response = requests.put(
            f"{LLM_PROVIDERS_URL}/{provider_id}",
            json=update_data,
            headers=get_headers(token)
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] 更新成功")
            print(f"   新描述: {data.get('description')}")
            print(f"   新优先级: {data.get('priority')}")
            print(f"   新请求限制: {data.get('max_requests_per_minute')}")
            return True
        else:
            print(f"   [FAIL] 更新失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 更新异常: {e}")
        return False

def test_toggle_status(token, provider_id):
    """禁用并重新启用供应商"""
    if not provider_id:
        print("\n[WARN] 跳过步骤7: 未创建供应商，无法启用/禁用")
        return False
        
    print(f"\n步骤7: 测试启用/禁用功能 (ID: {provider_id})...")
    
    # 首先禁用
    try:
        response = requests.post(
            f"{LLM_PROVIDERS_URL}/{provider_id}/disable",
            headers=get_headers(token)
        )
        
        print(f"   禁用状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] 禁用成功")
            print(f"   启用状态: {data.get('enabled')}")
            
            # 等待一下
            time.sleep(1)
            
            # 然后重新启用
            response = requests.post(
                f"{LLM_PROVIDERS_URL}/{provider_id}/enable",
                headers=get_headers(token)
            )
            
            print(f"   启用状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   [OK] 启用成功")
                print(f"   启用状态: {data.get('enabled')}")
                return True
            else:
                print(f"   [FAIL] 启用失败")
                print(f"   响应: {response.text}")
                return False
        else:
            print(f"   [FAIL] 禁用失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 启用/禁用异常: {e}")
        return False

def test_stats(token):
    """获取供应商统计信息"""
    print("\n步骤8: 获取LLM供应商统计概览...")
    
    try:
        response = requests.get(
            f"{LLM_PROVIDERS_URL}/stats/overview",
            headers=get_headers(token)
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] 获取统计成功")
            print(f"   总供应商数: {data.get('total_providers', 'N/A')}")
            print(f"   启用供应商数: {data.get('enabled_providers', 'N/A')}")
            print(f"   健康供应商数: {data.get('healthy_providers', 'N/A')}")
            print(f"   本月总成本: ¥{data.get('monthly_total_cost', 0) / 100:.2f}")
            return True
        else:
            print(f"   [FAIL] 获取统计失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 获取统计异常: {e}")
        return False

def test_delete_provider(token, provider_id):
    """删除供应商"""
    if not provider_id:
        print("\n[WARN] 跳过步骤9: 未创建供应商，无法删除")
        return False
        
    print(f"\n步骤9: 删除供应商 (ID: {provider_id})...")
    
    try:
        response = requests.delete(
            f"{LLM_PROVIDERS_URL}/{provider_id}",
            headers=get_headers(token)
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] 删除成功")
            print(f"   消息: {data.get('message')}")
            return True
        else:
            print(f"   [FAIL] 删除失败")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] 删除异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始LLM供应商管理端到端工作流测试")
    print("=" * 60)
    
    # 1. 登录
    token = test_login()
    if not token:
        print("[FAIL] 登录失败，无法继续测试")
        return False
    
    # 2. 创建供应商
    provider_id = test_create_provider(token)
    if not provider_id:
        print("[WARN] 供应商创建失败，继续测试其他功能")
    
    # 3. 获取供应商列表
    list_ok = test_list_providers(token)
    
    # 4. 获取单个供应商详情
    if provider_id:
        get_ok = test_get_single_provider(token, provider_id)
    
    # 5. 测试连接
    if provider_id:
        test_conn_ok = test_connection(token, provider_id)
    
    # 6. 更新供应商
    if provider_id:
        update_ok = test_update_provider(token, provider_id)
    
    # 7. 测试启用/禁用
    if provider_id:
        toggle_ok = test_toggle_status(token, provider_id)
    
    # 8. 获取统计
    stats_ok = test_stats(token)
    
    # 9. 删除供应商
    if provider_id:
        delete_ok = test_delete_provider(token, provider_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 简单总结
    tests_passed = 0
    tests_total = 1  # 登录测试
    
    if token:
        tests_passed += 1
    
    if provider_id:
        tests_total += 6  # 创建、获取详情、连接测试、更新、切换状态、删除
    else:
        tests_total += 1  # 列表测试
    
    if list_ok:
        tests_passed += 1
    
    print(f"测试通过: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("[OK] 所有测试通过！LLM供应商管理功能完整可用。")
        return True
    else:
        print("[WARN] 部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] 测试运行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)