#!/usr/bin/env python3
"""
修复422验证错误的脚本
主要处理两类问题：
1. 路径参数端点 - 需要提供有效的ID值
2. 查询参数端点 - 需要提供必要的查询参数
"""

import requests
import sys
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict

# 配置
BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"
TIMEOUT = 10

class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.token = None
        self.headers = {}
    
    def get_token(self) -> Optional[str]:
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
                    print("令牌未找到，响应结构:", data.keys())
                    return None
                
                self.token = token
                self.headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                print("✅ 登录成功，令牌获取成功")
                return token
            else:
                print(f"登录失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"登录请求异常: {e}")
        
        return None
    
    def get_headers(self) -> Dict:
        """获取认证头"""
        if not self.token:
            self.get_token()
        return self.headers

class DataCollector:
    """数据收集器，用于获取有效的ID值"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth = auth_manager
        self.cache = defaultdict(list)
    
    def collect_ids_from_list(self, list_endpoint: str, id_field: str = "id") -> List[int]:
        """从列表API收集ID值"""
        if list_endpoint in self.cache:
            return self.cache[list_endpoint]
        
        url = BASE_URL + list_endpoint
        headers = self.auth.get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                
                # 尝试不同的响应结构
                items = []
                if "data" in data and "items" in data["data"]:
                    items = data["data"]["items"]
                elif "items" in data:
                    items = data["items"]
                elif isinstance(data, list):
                    items = data
                
                # 提取ID
                ids = []
                for item in items:
                    if isinstance(item, dict) and id_field in item:
                        try:
                            ids.append(int(item[id_field]))
                        except (ValueError, TypeError):
                            pass
                
                self.cache[list_endpoint] = ids
                print(f"从 {list_endpoint} 收集到 {len(ids)} 个ID")
                return ids
            else:
                print(f"列表API调用失败: {list_endpoint} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"收集ID时出错: {e}")
        
        return []
    
    def get_sample_id(self, list_endpoint: str, id_field: str = "id") -> Optional[int]:
        """获取一个样本ID"""
        ids = self.collect_ids_from_list(list_endpoint, id_field)
        return ids[0] if ids else None

class EndpointFixer:
    """端点修复器"""
    
    def __init__(self, auth_manager: AuthManager, data_collector: DataCollector):
        self.auth = auth_manager
        self.data = data_collector
        self.results = []
    
    def fix_path_param_endpoint(self, endpoint: str) -> Tuple[bool, int, str]:
        """修复路径参数端点"""
        headers = self.auth.get_headers()
        
        # 根据端点类型确定列表API和参数名
        endpoint_config = self._get_endpoint_config(endpoint)
        if not endpoint_config:
            return False, 0, f"无法确定端点配置: {endpoint}"
        
        list_endpoint = endpoint_config["list_endpoint"]
        param_name = endpoint_config["param_name"]
        param_type = endpoint_config["param_type"]
        
        # 获取样本ID
        sample_id = self.data.get_sample_id(list_endpoint)
        if not sample_id:
            # 尝试创建测试数据
            sample_id = self._create_test_data(endpoint_config)
            if not sample_id:
                return False, 0, f"无有效ID且无法创建测试数据: {endpoint}"
        
        # 构建完整URL
        if param_type == "int":
            resolved_endpoint = endpoint.replace(f"{{{param_name}}}", str(sample_id))
        else:
            resolved_endpoint = endpoint.replace(f"{{{param_name}}}", "test_id")
        
        url = BASE_URL + resolved_endpoint
        
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            status_code = response.status_code
            
            if 200 <= status_code < 300:
                return True, status_code, f"成功: 使用ID={sample_id}"
            elif status_code == 404:
                return False, status_code, f"资源不存在: ID={sample_id}"
            elif status_code == 422:
                return False, status_code, f"仍返回422: 可能需要其他参数"
            else:
                return False, status_code, f"其他错误: {response.text[:100]}"
                
        except Exception as e:
            return False, 0, f"请求异常: {e}"
    
    def fix_query_param_endpoint(self, endpoint: str) -> Tuple[bool, int, str]:
        """修复查询参数端点"""
        headers = self.auth.get_headers()
        url = BASE_URL + endpoint
        
        # 根据端点类型提供不同的查询参数
        query_params = self._get_query_params_for_endpoint(endpoint)
        
        try:
            response = requests.get(url, headers=headers, params=query_params, timeout=TIMEOUT)
            status_code = response.status_code
            
            if 200 <= status_code < 300:
                return True, status_code, f"成功: 使用参数{query_params}"
            elif status_code == 422:
                # 尝试不同的参数组合
                alternative_params = self._get_alternative_params(endpoint)
                for alt_params in alternative_params:
                    try:
                        alt_response = requests.get(url, headers=headers, params=alt_params, timeout=TIMEOUT)
                        if 200 <= alt_response.status_code < 300:
                            return True, alt_response.status_code, f"成功: 使用替代参数{alt_params}"
                    except:
                        continue
                
                return False, status_code, f"仍返回422: 尝试多种参数组合无效"
            else:
                return False, status_code, f"其他错误: {response.text[:100]}"
                
        except Exception as e:
            return False, 0, f"请求异常: {e}"
    
    def _get_endpoint_config(self, endpoint: str) -> Optional[Dict]:
        """获取端点配置"""
        configs = {
            # header相关端点
            "/api/v1/admin/crawler/headers/{header_id}": {
                "list_endpoint": "/api/v1/admin/crawler/headers",
                "param_name": "header_id",
                "param_type": "int",
                "model": "RequestHeader"
            },
            "/api/v1/admin/headers/{header_id}": {
                "list_endpoint": "/api/v1/admin/headers",
                "param_name": "header_id", 
                "param_type": "int",
                "model": "RequestHeader"
            },
            
            # source相关端点
            "/api/v1/admin/crawler/sources/{source_id}/health": {
                "list_endpoint": "/api/v1/admin/crawler/sources",
                "param_name": "source_id",
                "param_type": "int",
                "model": "DataSource"
            },
            "/api/v1/admin/sources/{source_id}": {
                "list_endpoint": "/api/v1/admin/sources",
                "param_name": "source_id",
                "param_type": "int",
                "model": "DataSource"
            },
            "/api/v1/admin/sources/{source_id}/health": {
                "list_endpoint": "/api/v1/admin/sources", 
                "param_name": "source_id",
                "param_type": "int",
                "model": "DataSource"
            },
            "/api/v1/data-source-100qiu/{source_id}": {
                "list_endpoint": "/api/v1/data-source-100qiu/",
                "param_name": "source_id",
                "param_type": "int",
                "model": "DataSource100Qiu"
            },
            "/api/v1/sources/sources/{source_id}": {
                "list_endpoint": "/api/v1/sources/sources",
                "param_name": "source_id",
                "param_type": "int",
                "model": "Source"
            },
            "/api/v1/sources/sources/{source_id}/health": {
                "list_endpoint": "/api/v1/sources/sources",
                "param_name": "source_id",
                "param_type": "int",
                "model": "Source"
            },
            "/api/v1/sources/{source_id}": {
                "list_endpoint": "/api/v1/sources",
                "param_name": "source_id",
                "param_type": "int",
                "model": "Source"
            },
            
            # task相关端点
            "/api/v1/admin/crawler/tasks/{task_id}/logs": {
                "list_endpoint": "/api/v1/admin/crawler/tasks",
                "param_name": "task_id",
                "param_type": "int",
                "model": "CrawlerTask"
            },
            "/api/v1/admin/tasks/{task_id}": {
                "list_endpoint": "/api/v1/admin/tasks",
                "param_name": "task_id",
                "param_type": "int",
                "model": "Task"
            },
            "/api/v1/admin/tasks/{task_id}/logs": {
                "list_endpoint": "/api/v1/admin/tasks",
                "param_name": "task_id",
                "param_type": "int",
                "model": "Task"
            },
            "/api/v1/tasks/{task_id}": {
                "list_endpoint": "/api/v1/tasks",
                "param_name": "task_id",
                "param_type": "int",
                "model": "Task"
            },
            "/api/v1/tasks/{task_id}/logs": {
                "list_endpoint": "/api/v1/tasks",
                "param_name": "task_id",
                "param_type": "int",
                "model": "Task"
            },
            
            # 其他端点
            "/api/v1/admin/ip-pools/{pool_id}": {
                "list_endpoint": "/api/v1/admin/ip-pools",
                "param_name": "pool_id",
                "param_type": "int",
                "model": "IpPool"
            },
            
            # user相关端点
            "/api/v1/admin/user-profiles/{user_id}": {
                "list_endpoint": "/api/v1/admin/user-profiles/",
                "param_name": "user_id",
                "param_type": "int",
                "model": "UserProfile"
            },
            "/api/v1/admin/users/admin/{admin_id}": {
                "list_endpoint": "/api/v1/admin/users/",
                "param_name": "admin_id",
                "param_type": "int",
                "model": "User"
            },
            "/api/v1/admin/{id}": {
                "list_endpoint": "/api/v1/admin/",
                "param_name": "id",
                "param_type": "int",
                "model": "Admin"
            },
            "/api/v1/admin/{id}/members": {
                "list_endpoint": "/api/v1/admin/",
                "param_name": "id",
                "param_type": "int",
                "model": "Admin"
            },
            "/api/v1/admin/{id}/permissions": {
                "list_endpoint": "/api/v1/admin/",
                "param_name": "id",
                "param_type": "int",
                "model": "Admin"
            },
            "/api/v1/admin/{user_id}": {
                "list_endpoint": "/api/v1/admin/",
                "param_name": "user_id",
                "param_type": "int",
                "model": "User"
            },
            "/api/v1/users/admin/{admin_id}": {
                "list_endpoint": "/api/v1/users/",
                "param_name": "admin_id",
                "param_type": "int",
                "model": "User"
            },
            
            # 其他类型端点
            "/api/v1/caipiao-data/{caipiao_data_id}": {
                "list_endpoint": "/api/v1/caipiao-data/",
                "param_name": "caipiao_data_id",
                "param_type": "int",
                "model": "CaipiaoData"
            },
            "/api/v1/draw-prediction/training-jobs/{job_id}/logs": {
                "list_endpoint": "/api/v1/draw-prediction/training-jobs",
                "param_name": "job_id",
                "param_type": "int",
                "model": "TrainingJob"
            },
            "/api/v1/predictions/draw-prediction/training-jobs/{job_id}/logs": {
                "list_endpoint": "/api/v1/predictions/draw-prediction/training-jobs",
                "param_name": "job_id",
                "param_type": "int",
                "model": "TrainingJob"
            },
            "/api/v1/task-monitor/executions/{execution_id}": {
                "list_endpoint": "/api/v1/task-monitor/executions",
                "param_name": "execution_id",
                "param_type": "int",
                "model": "Execution"
            },
            "/api/v1/task-monitor/executions/{execution_id}/logs": {
                "list_endpoint": "/api/v1/task-monitor/executions",
                "param_name": "execution_id",
                "param_type": "int",
                "model": "Execution"
            },
        }
        
        return configs.get(endpoint)
    
    def _create_test_data(self, config: Dict) -> Optional[int]:
        """创建测试数据"""
        # 简化实现：返回一个测试ID
        # 实际项目中可能需要调用创建API
        print(f"⚠️  无现有数据，使用测试ID 1 进行测试")
        return 1
    
    def _get_query_params_for_endpoint(self, endpoint: str) -> Dict:
        """根据端点类型获取查询参数"""
        param_map = {
            "/api/v1/admin/matches/league/config": {
                "league_id": 1,
                "include_matches": "true"
            },
            "/api/v1/admin/tree": {
                "type": "department",
                "parent_id": 0
            },
            "/api/v1/hedging/parlay-opportunities": {
                "match_id": 1,
                "min_odds": 1.5,
                "max_odds": 3.0
            },
            "/api/v1/logs/system/logs/db/search": {
                "page": 1,
                "size": 10,
                "log_type": "api"
            },
            "/api/v1/matches/admin/matches/league/config": {
                "league_id": 1,
                "season": "2024"
            },
            "/api/v1/odds/odds/history": {
                "match_id": 1,
                "company_id": 1,
                "days": 7
            },
            "/api/v1/simple-hedging/parlay-opportunities": {
                "match_id": 1,
                "odds_type": "european"
            }
        }
        
        return param_map.get(endpoint, {})
    
    def _get_alternative_params(self, endpoint: str) -> List[Dict]:
        """获取替代参数组合"""
        alternatives = []
        
        # 添加一些常见的替代参数组合
        alternatives.append({"page": 1, "size": 10})
        alternatives.append({"limit": 20, "offset": 0})
        alternatives.append({"status": "active"})
        
        return alternatives
    
    def run_fixes(self, endpoints: List[str]):
        """运行修复"""
        print(f"开始修复 {len(endpoints)} 个端点...")
        print("=" * 80)
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"[{i}/{len(endpoints)}] 修复: {endpoint}")
            
            # 判断端点类型
            if "{" in endpoint and "}" in endpoint:
                # 路径参数端点
                success, status_code, message = self.fix_path_param_endpoint(endpoint)
            else:
                # 查询参数端点
                success, status_code, message = self.fix_query_param_endpoint(endpoint)
            
            result = {
                "endpoint": endpoint,
                "success": success,
                "status_code": status_code,
                "message": message
            }
            
            self.results.append(result)
            
            status_icon = "✅" if success else "❌"
            print(f"  结果: {status_icon} {message}")
            print()
        
        # 生成报告
        self._generate_report()
    
    def _generate_report(self):
        """生成修复报告"""
        total = len(self.results)
        success_count = sum(1 for r in self.results if r["success"])
        failure_count = total - success_count
        
        print("=" * 80)
        print("修复结果汇总:")
        print(f"  总端点数: {total}")
        print(f"  成功修复: {success_count}")
        print(f"  修复失败: {failure_count}")
        print("=" * 80)
        
        if failure_count > 0:
            print("\n失败端点详情:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['endpoint']}")
                    print(f"    状态码: {result['status_code']}")
                    print(f"    信息: {result['message']}")
        
        # 保存结果到文件
        output_file = "422_fixes_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "base_url": BASE_URL,
                "total_endpoints": total,
                "successful_fixes": success_count,
                "failed_fixes": failure_count,
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: {output_file}")

def main():
    """主函数"""
    print("=" * 80)
    print("422验证错误修复工具")
    print("=" * 80)
    
    # 读取422错误端点
    endpoints = []
    try:
        with open('auth_smoke_get_results_latest.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2 and parts[1] == '422':
                endpoints.append(parts[0])
    except FileNotFoundError:
        print("错误: 找不到测试结果文件")
        sys.exit(1)
    
    if not endpoints:
        print("未找到422错误端点")
        sys.exit(0)
    
    print(f"发现 {len(endpoints)} 个需要修复的端点")
    
    # 初始化管理器
    auth_manager = AuthManager()
    data_collector = DataCollector(auth_manager)
    fixer = EndpointFixer(auth_manager, data_collector)
    
    # 运行修复
    fixer.run_fixes(endpoints)

if __name__ == "__main__":
    main()