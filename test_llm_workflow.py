#!/usr/bin/env python3
"""
完整的LLM供应商管理端到端工作流测试
测试从创建、读取、更新、删除到连接测试的完整流程
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers"

# 测试用户凭据（使用admin账户）
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

class LLMWorkflowTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.created_provider_id = None
        self.test_results = {}
        
    def get_headers(self) -> Dict[str, str]:
        """获取包含认证token的请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self) -> bool:
        """用户登录获取JWT令牌"""
        print("步骤1: 用户登录...")
        try:
            response = self.session.post(
                LOGIN_URL,
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"   [OK] 登录成功，获取到token: {self.token[:20]}...")
                return True
            else:
                print(f"   [FAIL] 登录失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"   [FAIL] 登录异常: {e}")
            return False
    
    def create_llm_provider(self) -> bool:
        """创建LLM供应商"""
        print("\n步骤2: 创建LLM供应商...")
        
        # 测试数据 - 使用模拟的API密钥（在实际测试中可以使用真实密钥或测试密钥）
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
            response = self.session.post(
                LLM_PROVIDERS_URL,
                json=provider_data,
                headers=self.get_headers()
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.created_provider_id = data.get("id")
                print(f"   ✅ 供应商创建成功，ID: {self.created_provider_id}")
                print(f"   名称: {data.get('name')}")
                print(f"   类型: {data.get('provider_type')}")
                print(f"   状态: {data.get('health_status')}")
                self.test_results["create"] = True
                return True
            else:
                print(f"   ❌ 供应商创建失败")
                print(f"   响应: {response.text}")
                self.test_results["create"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 创建异常: {e}")
            self.test_results["create"] = False
            return False
    
    def get_llm_providers(self) -> bool:
        """获取LLM供应商列表"""
        print("\n📋 步骤3: 获取LLM供应商列表...")
        
        try:
            response = self.session.get(
                LLM_PROVIDERS_URL,
                headers=self.get_headers(),
                params={"limit": 10}
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                providers = data
                if isinstance(data, dict) and "data" in data:
                    providers = data["data"]
                
                print(f"   ✅ 获取到 {len(providers)} 个供应商")
                
                # 显示前几个供应商
                for i, provider in enumerate(providers[:3]):
                    print(f"   {i+1}. {provider.get('name')} ({provider.get('provider_type')}) - {provider.get('health_status')}")
                
                self.test_results["list"] = True
                return True
            else:
                print(f"   ❌ 获取供应商列表失败")
                print(f"   响应: {response.text}")
                self.test_results["list"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 获取列表异常: {e}")
            self.test_results["list"] = False
            return False
    
    def get_single_provider(self) -> bool:
        """获取单个供应商详情"""
        if not self.created_provider_id:
            print("\n⚠️  跳过步骤4: 未创建供应商，无法获取详情")
            self.test_results["get_single"] = False
            return False
            
        print(f"\n🔍 步骤4: 获取供应商详情 (ID: {self.created_provider_id})...")
        
        try:
            response = self.session.get(
                f"{LLM_PROVIDERS_URL}/{self.created_provider_id}",
                headers=self.get_headers()
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 获取详情成功")
                print(f"   名称: {data.get('name')}")
                print(f"   类型: {data.get('provider_type')}")
                print(f"   启用: {data.get('enabled')}")
                print(f"   健康状态: {data.get('health_status')}")
                self.test_results["get_single"] = True
                return True
            else:
                print(f"   ❌ 获取详情失败")
                print(f"   响应: {response.text}")
                self.test_results["get_single"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 获取详情异常: {e}")
            self.test_results["get_single"] = False
            return False
    
    def test_provider_connection(self) -> bool:
        """测试供应商连接"""
        if not self.created_provider_id:
            print("\n⚠️  跳过步骤5: 未创建供应商，无法测试连接")
            self.test_results["test_connection"] = False
            return False
            
        print(f"\n🧪 步骤5: 测试供应商连接 (ID: {self.created_provider_id})...")
        
        test_data = {
            "test_prompt": "Hello, please respond with 'OK' to confirm connectivity.",
            "timeout_ms": 5000
        }
        
        try:
            response = self.session.post(
                f"{LLM_PROVIDERS_URL}/{self.created_provider_id}/test",
                json=test_data,
                headers=self.get_headers()
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 连接测试完成")
                print(f"   成功: {data.get('success')}")
                print(f"   消息: {data.get('message')}")
                print(f"   响应时间: {data.get('response_time_ms', 'N/A')}ms")
                
                # 注意：由于我们使用的是模拟API密钥，测试可能会失败
                # 但API应该返回适当的错误消息而不是崩溃
                self.test_results["test_connection"] = True
                return True
            else:
                print(f"   ❌ 连接测试失败")
                print(f"   响应: {response.text}")
                self.test_results["test_connection"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 连接测试异常: {e}")
            self.test_results["test_connection"] = False
            return False
    
    def update_provider(self) -> bool:
        """更新供应商信息"""
        if not self.created_provider_id:
            print("\n⚠️  跳过步骤6: 未创建供应商，无法更新")
            self.test_results["update"] = False
            return False
            
        print(f"\n✏️  步骤6: 更新供应商信息 (ID: {self.created_provider_id})...")
        
        update_data = {
            "description": "更新后的描述 - 端到端测试完成",
            "priority": 3,  # 提高优先级
            "max_requests_per_minute": 100
        }
        
        try:
            response = self.session.put(
                f"{LLM_PROVIDERS_URL}/{self.created_provider_id}",
                json=update_data,
                headers=self.get_headers()
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 更新成功")
                print(f"   新描述: {data.get('description')}")
                print(f"   新优先级: {data.get('priority')}")
                print(f"   新请求限制: {data.get('max_requests_per_minute')}")
                self.test_results["update"] = True
                return True
            else:
                print(f"   ❌ 更新失败")
                print(f"   响应: {response.text}")
                self.test_results["update"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 更新异常: {e}")
            self.test_results["update"] = False
            return False
    
    def disable_and_enable_provider(self) -> bool:
        """禁用并重新启用供应商"""
        if not self.created_provider_id:
            print("\n⚠️  跳过步骤7: 未创建供应商，无法启用/禁用")
            self.test_results["toggle_status"] = False
            return False
            
        print(f"\n🔧 步骤7: 测试启用/禁用功能 (ID: {self.created_provider_id})...")
        
        # 首先禁用
        try:
            response = self.session.post(
                f"{LLM_PROVIDERS_URL}/{self.created_provider_id}/disable",
                headers=self.get_headers()
            )
            
            print(f"   禁用状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 禁用成功")
                print(f"   启用状态: {data.get('enabled')}")
                
                # 等待一下
                time.sleep(1)
                
                # 然后重新启用
                response = self.session.post(
                    f"{LLM_PROVIDERS_URL}/{self.created_provider_id}/enable",
                    headers=self.get_headers()
                )
                
                print(f"   启用状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 启用成功")
                    print(f"   启用状态: {data.get('enabled')}")
                    self.test_results["toggle_status"] = True
                    return True
                else:
                    print(f"   ❌ 启用失败")
                    print(f"   响应: {response.text}")
                    self.test_results["toggle_status"] = False
                    return False
            else:
                print(f"   ❌ 禁用失败")
                print(f"   响应: {response.text}")
                self.test_results["toggle_status"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 启用/禁用异常: {e}")
            self.test_results["toggle_status"] = False
            return False
    
    def delete_provider(self) -> bool:
        """删除供应商"""
        if not self.created_provider_id:
            print("\n⚠️  跳过步骤8: 未创建供应商，无法删除")
            self.test_results["delete"] = False
            return False
            
        print(f"\n🗑️  步骤8: 删除供应商 (ID: {self.created_provider_id})...")
        
        try:
            response = self.session.delete(
                f"{LLM_PROVIDERS_URL}/{self.created_provider_id}",
                headers=self.get_headers()
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 删除成功")
                print(f"   消息: {data.get('message')}")
                self.test_results["delete"] = True
                return True
            else:
                print(f"   ❌ 删除失败")
                print(f"   响应: {response.text}")
                self.test_results["delete"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 删除异常: {e}")
            self.test_results["delete"] = False
            return False
    
    def get_provider_stats(self) -> bool:
        """获取供应商统计信息"""
        print("\n📊 步骤9: 获取LLM供应商统计概览...")
        
        try:
            response = self.session.get(
                f"{LLM_PROVIDERS_URL}/stats/overview",
                headers=self.get_headers()
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 获取统计成功")
                print(f"   总供应商数: {data.get('total_providers', 'N/A')}")
                print(f"   启用供应商数: {data.get('enabled_providers', 'N/A')}")
                print(f"   健康供应商数: {data.get('healthy_providers', 'N/A')}")
                print(f"   本月总成本: ¥{data.get('monthly_total_cost', 0) / 100:.2f}")
                self.test_results["stats"] = True
                return True
            else:
                print(f"   ❌ 获取统计失败")
                print(f"   响应: {response.text}")
                self.test_results["stats"] = False
                return False
                
        except Exception as e:
            print(f"   ❌ 获取统计异常: {e}")
            self.test_results["stats"] = False
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("=" * 60)
        print("🚀 开始LLM供应商管理端到端工作流测试")
        print("=" * 60)
        
        # 运行所有测试步骤
        steps = [
            self.login,
            self.create_llm_provider,
            self.get_llm_providers,
            self.get_single_provider,
            self.test_provider_connection,
            self.update_provider,
            self.disable_and_enable_provider,
            self.get_provider_stats,
            self.delete_provider
        ]
        
        all_passed = True
        for step_func in steps:
            if not step_func():
                all_passed = False
                # 如果关键步骤失败，可能继续测试其他步骤
                # 但如果是登录失败，整个测试无法继续
                if step_func == self.login:
                    print("❌ 登录失败，无法继续测试")
                    break
        
        # 打印测试总结
        print("\n" + "=" * 60)
        print("📋 测试结果总结")
        print("=" * 60)
        
        for test_name, passed in self.test_results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"  {test_name:20} {status}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for passed in self.test_results.values() if passed)
        
        print(f"\n  总计: {passed_tests}/{total_tests} 个测试通过")
        
        if all_passed and passed_tests == total_tests:
            print("\n🎉 所有测试通过！LLM供应商管理功能完整可用。")
            return True
        else:
            print(f"\n⚠️  部分测试失败，需要进一步检查。")
            return False

def main():
    """主函数"""
    test = LLMWorkflowTest()
    
    try:
        success = test.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()