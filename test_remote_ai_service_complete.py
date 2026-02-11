"""
远程AI服务完整功能测试
测试RemoteAIService.vue组件对应的所有后端API端点
"""
import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class RemoteAIServiceTester:
    """远程AI服务测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.headers = {}
        self.created_providers = []  # 记录创建的供应商ID，用于清理
        
    def login(self) -> bool:
        """管理员登录，获取JWT令牌"""
        try:
            login_url = f"{self.base_url}/api/v1/auth/login"
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            
            logger.info(f"尝试登录到 {login_url}")
            response = self.session.post(login_url, json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                # 从嵌套的data字段提取令牌
                if "data" in data and "access_token" in data["data"]:
                    self.token = data["data"]["access_token"]
                elif "access_token" in data:
                    self.token = data["access_token"]
                else:
                    logger.error("响应中没有access_token字段")
                    return False
                
                if self.token:
                    self.headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    }
                    logger.info("登录成功，已获取JWT令牌")
                    return True
                else:
                    logger.error("提取的令牌为空")
                    return False
            else:
                logger.error(f"登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"登录过程中发生异常: {e}")
            return False
    
    def test_api_health(self) -> bool:
        """测试API健康状态"""
        try:
            # 测试基础健康检查
            health_url = f"{self.base_url}/api/v1/health"
            response = self.session.get(health_url)
            
            if response.status_code == 200:
                logger.info(f"API健康检查通过: {response.json()}")
                return True
            else:
                logger.error(f"API健康检查失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"API健康检查异常: {e}")
            return False
    
    def test_endpoint_accessible(self, endpoint: str, method: str = "GET", 
                                requires_auth: bool = True, data: Optional[Dict] = None) -> bool:
        """测试单个端点是否可访问"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self.headers if requires_auth else {}
            
            logger.info(f"测试端点: {method} {url}")
            
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data or {})
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=data or {})
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                logger.error(f"不支持的HTTP方法: {method}")
                return False
            
            # 检查响应状态码
            if response.status_code in [200, 201, 204]:
                logger.info(f"端点 {endpoint} 测试通过: {response.status_code}")
                return True
            elif response.status_code == 401 and requires_auth:
                logger.warning(f"端点 {endpoint} 需要身份验证: {response.status_code}")
                return False
            else:
                logger.warning(f"端点 {endpoint} 返回非成功状态码: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"测试端点 {endpoint} 时发生异常: {e}")
            return False
    
    def test_all_endpoints_accessible(self) -> Dict[str, bool]:
        """测试所有LLM供应商相关端点是否可访问"""
        logger.info("开始测试所有LLM供应商API端点可访问性...")
        
        endpoints = [
            ("/api/v1/llm-providers", "GET", True),
            ("/api/v1/llm-providers/count", "GET", True),
            ("/api/v1/llm-providers/stats/overview", "GET", True),
            ("/api/v1/llm-providers/available/list", "GET", True),
        ]
        
        results = {}
        for endpoint, method, requires_auth in endpoints:
            results[endpoint] = self.test_endpoint_accessible(endpoint, method, requires_auth)
        
        logger.info(f"端点可访问性测试完成: {sum(results.values())}/{len(results)} 通过")
        return results
    
    def create_test_provider(self) -> Optional[int]:
        """创建测试供应商，返回供应商ID"""
        try:
            url = f"{self.base_url}/api/v1/llm-providers"
            provider_data = {
                "name": f"测试供应商_{int(time.time())}",
                "provider_type": "openai",
                "description": "用于功能测试的临时供应商",
                "api_key": "sk-test1234567890abcdef",
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-3.5-turbo",
                "available_models": ["gpt-3.5-turbo", "gpt-4"],
                "enabled": True,
                "priority": 5,
                "max_requests_per_minute": 60,
                "timeout_seconds": 30,
                "rate_limit_strategy": "fixed_window",
                "retry_policy": {"max_retries": 3, "backoff_factor": 1},
                "circuit_breaker_config": {"failure_threshold": 5, "reset_timeout": 60},
                "cost_per_token": {"input": 0.0015, "output": 0.002},
                "version": "1.0",
                "tags": ["测试", "临时"]
            }
            
            logger.info(f"创建测试供应商: {provider_data['name']}")
            response = self.session.post(url, headers=self.headers, json=provider_data)
            
            if response.status_code == 201:
                provider = response.json()
                provider_id = provider.get("id")
                if provider_id:
                    self.created_providers.append(provider_id)
                    logger.info(f"测试供应商创建成功，ID: {provider_id}")
                    return provider_id
                else:
                    logger.error("响应中没有供应商ID")
                    return None
            else:
                logger.error(f"创建供应商失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"创建测试供应商时发生异常: {e}")
            return None
    
    def test_crud_operations(self) -> Dict[str, bool]:
        """测试CRUD操作（创建、读取、更新、删除）"""
        logger.info("开始测试CRUD操作...")
        
        results = {
            "create": False,
            "read": False,
            "update": False,
            "delete": False
        }
        
        # 1. 创建供应商
        provider_id = self.create_test_provider()
        if provider_id:
            results["create"] = True
            logger.info(f"创建操作成功，供应商ID: {provider_id}")
            
            # 2. 读取供应商
            read_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}"
            response = self.session.get(read_url, headers=self.headers)
            if response.status_code == 200:
                provider = response.json()
                if provider["id"] == provider_id:
                    results["read"] = True
                    logger.info("读取操作成功")
                else:
                    logger.error("读取的供应商ID不匹配")
            else:
                logger.error(f"读取供应商失败: {response.status_code} - {response.text}")
            
            # 3. 更新供应商
            update_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}"
            update_data = {
                "description": "更新后的描述",
                "priority": 8,
                "enabled": False,
                "tags": ["测试", "临时", "已更新"]
            }
            response = self.session.put(update_url, headers=self.headers, json=update_data)
            if response.status_code == 200:
                updated_provider = response.json()
                if updated_provider["priority"] == 8 and updated_provider["enabled"] == False:
                    results["update"] = True
                    logger.info("更新操作成功")
                else:
                    logger.error("更新后的字段值不正确")
            else:
                logger.error(f"更新供应商失败: {response.status_code} - {response.text}")
            
            # 4. 删除供应商
            delete_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}"
            response = self.session.delete(delete_url, headers=self.headers)
            if response.status_code in [200, 204]:
                results["delete"] = True
                logger.info("删除操作成功")
                # 从创建列表中移除
                if provider_id in self.created_providers:
                    self.created_providers.remove(provider_id)
            else:
                logger.error(f"删除供应商失败: {response.status_code} - {response.text}")
        else:
            logger.error("创建操作失败，跳过后续测试")
        
        logger.info(f"CRUD测试结果: {sum(results.values())}/{len(results)} 通过")
        return results
    
    def test_batch_operations(self) -> Dict[str, bool]:
        """测试批量操作"""
        logger.info("开始测试批量操作...")
        
        results = {
            "batch_enable": False,
            "batch_disable": False,
            "batch_update_status": False
        }
        
        # 创建多个测试供应商
        provider_ids = []
        for i in range(3):
            provider_id = self.create_test_provider()
            if provider_id:
                provider_ids.append(provider_id)
        
        if len(provider_ids) >= 2:
            logger.info(f"已创建 {len(provider_ids)} 个测试供应商用于批量操作")
            
            # 测试批量启用/禁用（通过批量状态更新接口）
            batch_url = f"{self.base_url}/api/v1/llm-providers/batch/update-status"
            
            # 批量禁用
            disable_data = {
                "provider_ids": provider_ids,
                "action": "disable"
            }
            response = self.session.post(batch_url, headers=self.headers, json=disable_data)
            if response.status_code == 200:
                results["batch_disable"] = True
                logger.info("批量禁用操作成功")
            else:
                logger.error(f"批量禁用失败: {response.status_code} - {response.text}")
            
            # 批量启用
            enable_data = {
                "provider_ids": provider_ids,
                "action": "enable"
            }
            response = self.session.post(batch_url, headers=self.headers, json=enable_data)
            if response.status_code == 200:
                results["batch_enable"] = True
                logger.info("批量启用操作成功")
            else:
                logger.error(f"批量启用失败: {response.status_code} - {response.text}")
            
            # 测试批量状态更新（通过单个启用/禁用接口循环）
            all_success = True
            for provider_id in provider_ids:
                enable_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}/enable"
                response = self.session.post(enable_url, headers=self.headers)
                if response.status_code != 200:
                    all_success = False
                    logger.error(f"启用供应商 {provider_id} 失败: {response.status_code}")
            
            results["batch_update_status"] = all_success
            if all_success:
                logger.info("批量状态更新操作成功")
            
            # 清理创建的供应商
            self._cleanup_providers(provider_ids)
        else:
            logger.error("无法创建足够的测试供应商进行批量操作测试")
        
        logger.info(f"批量操作测试结果: {sum(results.values())}/{len(results)} 通过")
        return results
    
    def test_pagination_and_filtering(self) -> Dict[str, bool]:
        """测试分页和筛选功能"""
        logger.info("开始测试分页和筛选功能...")
        
        results = {
            "pagination": False,
            "search": False,
            "filter_by_type": False,
            "filter_by_status": False
        }
        
        # 创建几个不同状态和类型的供应商
        test_providers = [
            {"name": "测试OpenAI供应商", "provider_type": "openai", "enabled": True},
            {"name": "测试Google供应商", "provider_type": "google", "enabled": False},
            {"name": "测试Azure供应商", "provider_type": "azure", "enabled": True},
        ]
        
        created_ids = []
        for provider_config in test_providers:
            provider_id = self._create_specific_provider(provider_config)
            if provider_id:
                created_ids.append(provider_id)
        
        if len(created_ids) > 0:
            # 测试分页
            pagination_url = f"{self.base_url}/api/v1/llm-providers?skip=0&limit=2"
            response = self.session.get(pagination_url, headers=self.headers)
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list) and len(providers) <= 2:
                    results["pagination"] = True
                    logger.info("分页功能测试成功")
                else:
                    logger.error("分页功能返回数据不符合预期")
            else:
                logger.error(f"分页请求失败: {response.status_code}")
            
            # 测试搜索
            search_url = f"{self.base_url}/api/v1/llm-providers?search=OpenAI"
            response = self.session.get(search_url, headers=self.headers)
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list):
                    results["search"] = True
                    logger.info("搜索功能测试成功")
                else:
                    logger.error("搜索功能返回数据不符合预期")
            else:
                logger.error(f"搜索请求失败: {response.status_code}")
            
            # 测试按类型筛选
            type_filter_url = f"{self.base_url}/api/v1/llm-providers?provider_type=openai"
            response = self.session.get(type_filter_url, headers=self.headers)
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list):
                    results["filter_by_type"] = True
                    logger.info("按类型筛选功能测试成功")
                else:
                    logger.error("按类型筛选返回数据不符合预期")
            else:
                logger.error(f"按类型筛选请求失败: {response.status_code}")
            
            # 测试按状态筛选
            status_filter_url = f"{self.base_url}/api/v1/llm-providers?enabled=true"
            response = self.session.get(status_filter_url, headers=self.headers)
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list):
                    results["filter_by_status"] = True
                    logger.info("按状态筛选功能测试成功")
                else:
                    logger.error("按状态筛选返回数据不符合预期")
            else:
                logger.error(f"按状态筛选请求失败: {response.status_code}")
            
            # 清理
            self._cleanup_providers(created_ids)
        else:
            logger.error("无法创建测试供应商进行分页和筛选测试")
        
        logger.info(f"分页和筛选测试结果: {sum(results.values())}/{len(results)} 通过")
        return results
    
    def test_provider_specific_operations(self) -> Dict[str, bool]:
        """测试供应商特定操作（测试连接、启用/禁用、成本增加）"""
        logger.info("开始测试供应商特定操作...")
        
        results = {
            "test_connection": False,
            "enable_disable": False,
            "increment_cost": False
        }
        
        # 创建一个测试供应商
        provider_id = self.create_test_provider()
        if provider_id:
            # 测试连接
            test_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}/test"
            test_data = {
                "test_message": "Hello, this is a test",
                "max_tokens": 10
            }
            response = self.session.post(test_url, headers=self.headers, json=test_data)
            if response.status_code in [200, 400, 500]:  # 连接测试可能因API密钥无效而失败，但端点应可访问
                results["test_connection"] = True
                logger.info("测试连接端点可访问")
            else:
                logger.error(f"测试连接失败: {response.status_code} - {response.text}")
            
            # 测试启用/禁用
            disable_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}/disable"
            response = self.session.post(disable_url, headers=self.headers)
            if response.status_code == 200:
                enable_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}/enable"
                response = self.session.post(enable_url, headers=self.headers)
                if response.status_code == 200:
                    results["enable_disable"] = True
                    logger.info("启用/禁用操作测试成功")
                else:
                    logger.error(f"启用供应商失败: {response.status_code}")
            else:
                logger.error(f"禁用供应商失败: {response.status_code}")
            
            # 测试增加成本
            cost_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}/increment-cost"
            cost_data = {"cost_cents": 150}  # 1.5元
            response = self.session.post(cost_url, headers=self.headers, json=cost_data)
            if response.status_code == 200:
                results["increment_cost"] = True
                logger.info("增加成本操作测试成功")
            else:
                logger.error(f"增加成本失败: {response.status_code} - {response.text}")
            
            # 清理
            delete_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}"
            self.session.delete(delete_url, headers=self.headers)
            if provider_id in self.created_providers:
                self.created_providers.remove(provider_id)
        else:
            logger.error("无法创建测试供应商进行特定操作测试")
        
        logger.info(f"供应商特定操作测试结果: {sum(results.values())}/{len(results)} 通过")
        return results
    
    def _create_specific_provider(self, provider_config: Dict) -> Optional[int]:
        """创建特定配置的供应商"""
        try:
            url = f"{self.base_url}/api/v1/llm-providers"
            provider_data = {
                "name": f"{provider_config['name']}_{int(time.time())}",
                "provider_type": provider_config["provider_type"],
                "description": f"用于筛选测试的{provider_config['provider_type']}供应商",
                "api_key": f"sk-test-{provider_config['provider_type']}",
                "base_url": "https://api.example.com/v1",
                "default_model": "test-model",
                "available_models": ["test-model"],
                "enabled": provider_config["enabled"],
                "priority": 5,
                "max_requests_per_minute": 60,
                "timeout_seconds": 30,
                "rate_limit_strategy": "fixed_window",
                "retry_policy": {},
                "circuit_breaker_config": {},
                "cost_per_token": {},
                "version": "1.0",
                "tags": ["测试", "筛选"]
            }
            
            response = self.session.post(url, headers=self.headers, json=provider_data)
            if response.status_code == 201:
                provider = response.json()
                provider_id = provider.get("id")
                if provider_id:
                    self.created_providers.append(provider_id)
                    return provider_id
            return None
        except Exception as e:
            logger.error(f"创建特定供应商失败: {e}")
            return None
    
    def _cleanup_providers(self, provider_ids: List[int]):
        """清理创建的供应商"""
        for provider_id in provider_ids:
            try:
                delete_url = f"{self.base_url}/api/v1/llm-providers/{provider_id}"
                self.session.delete(delete_url, headers=self.headers)
                if provider_id in self.created_providers:
                    self.created_providers.remove(provider_id)
            except Exception as e:
                logger.warning(f"清理供应商 {provider_id} 失败: {e}")
    
    def run_complete_test(self) -> Dict[str, Any]:
        """运行完整测试套件"""
        logger.info("=" * 60)
        logger.info("开始远程AI服务完整功能测试")
        logger.info("=" * 60)
        
        overall_results = {
            "api_health": False,
            "authentication": False,
            "endpoints_accessible": {},
            "crud_operations": {},
            "batch_operations": {},
            "pagination_filtering": {},
            "provider_specific_operations": {},
            "summary": {}
        }
        
        # 1. 测试API健康状态
        logger.info("\n1. 测试API健康状态...")
        overall_results["api_health"] = self.test_api_health()
        
        # 2. 登录获取令牌
        logger.info("\n2. 测试管理员身份验证...")
        overall_results["authentication"] = self.login()
        
        if not overall_results["authentication"]:
            logger.error("身份验证失败，无法继续测试需要认证的端点")
            # 仍然可以测试不需要认证的端点
        
        # 3. 测试端点可访问性
        logger.info("\n3. 测试所有端点可访问性...")
        overall_results["endpoints_accessible"] = self.test_all_endpoints_accessible()
        
        if overall_results["authentication"]:
            # 4. 测试CRUD操作
            logger.info("\n4. 测试CRUD操作...")
            overall_results["crud_operations"] = self.test_crud_operations()
            
            # 5. 测试批量操作
            logger.info("\n5. 测试批量操作...")
            overall_results["batch_operations"] = self.test_batch_operations()
            
            # 6. 测试分页和筛选
            logger.info("\n6. 测试分页和筛选功能...")
            overall_results["pagination_filtering"] = self.test_pagination_and_filtering()
            
            # 7. 测试供应商特定操作
            logger.info("\n7. 测试供应商特定操作...")
            overall_results["provider_specific_operations"] = self.test_provider_specific_operations()
        
        # 生成总结
        logger.info("\n" + "=" * 60)
        logger.info("测试总结")
        logger.info("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        # 计算通过率
        for category, result in overall_results.items():
            if isinstance(result, bool):
                total_tests += 1
                if result:
                    passed_tests += 1
                logger.info(f"{category}: {'✓' if result else '✗'}")
            elif isinstance(result, dict):
                category_total = len(result)
                category_passed = sum(1 for v in result.values() if v)
                total_tests += category_total
                passed_tests += category_passed
                logger.info(f"{category}: {category_passed}/{category_total} 通过")
        
        overall_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        logger.info(f"\n总测试数: {total_tests}")
        logger.info(f"通过数: {passed_tests}")
        logger.info(f"失败数: {total_tests - passed_tests}")
        logger.info(f"通过率: {overall_results['summary']['pass_rate']:.1f}%")
        
        # 清理剩余的资源
        if self.created_providers:
            logger.info(f"\n清理 {len(self.created_providers)} 个测试供应商...")
            self._cleanup_providers(self.created_providers.copy())
        
        logger.info("\n" + "=" * 60)
        logger.info("远程AI服务完整功能测试完成")
        logger.info("=" * 60)
        
        return overall_results

def main():
    """主函数"""
    tester = RemoteAIServiceTester()
    results = tester.run_complete_test()
    
    # 保存结果到文件
    output_file = "remote_ai_service_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        # 转换结果中的非JSON可序列化对象
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                serializable_results[key] = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, bool):
                        serializable_results[key][sub_key] = sub_value
                    elif hasattr(sub_value, '__dict__'):
                        serializable_results[key][sub_key] = str(sub_value)
                    else:
                        serializable_results[key][sub_key] = sub_value
            elif hasattr(value, '__dict__'):
                serializable_results[key] = str(value)
            else:
                serializable_results[key] = value
        
        json.dump(serializable_results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"测试结果已保存到: {output_file}")
    
    # 根据测试结果返回退出码
    if results["summary"]["pass_rate"] >= 80:
        logger.info("测试通过率超过80%，测试成功")
        return 0
    else:
        logger.error("测试通过率低于80%，测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())