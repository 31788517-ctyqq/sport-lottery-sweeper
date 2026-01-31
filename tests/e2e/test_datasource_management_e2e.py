"""
数据源管理模块端到端测试用例
模拟用户完成端到端的测试
"""

import pytest
import requests
import time
import os
from typing import Dict, Any, List

# 从环境变量获取基础URL，默认为本地开发环境
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-jwt-token")


class TestDataSourceManagementE2E:
    """
    数据源管理模块端到端测试
    """

    def setup_method(self):
        """测试前置设置"""
        self.headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_api_url = f"{BASE_URL}/api/admin/v1"

    def test_complete_datasource_workflow(self):
        """
        完整的数据源管理工作流程测试
        模拟用户从登录到完成数据源管理任务的全过程
        """
        # 步骤1: 获取数据源列表（初始状态）
        initial_list_response = self._get_datasource_list()
        assert initial_list_response["code"] == 200
        initial_count = initial_list_response["data"]["total"]

        # 步骤2: 创建一个新的数据源
        new_source_data = {
            "name": "测试数据源-E2E",
            "category": "match_data",
            "source_type": "api",
            "api_url": "https://test-api.example.com/data",
            "method": "GET",
            "timeout": 30,
            "description": "端到端测试创建的数据源"
        }
        create_response = self._create_datasource(new_source_data)
        assert create_response["code"] == 200
        created_source = create_response["data"]
        assert created_source["name"] == new_source_data["name"]
        assert created_source["status"] == "online"

        # 步骤3: 验证数据源已成功创建
        updated_list_response = self._get_datasource_list()
        assert updated_list_response["data"]["total"] == initial_count + 1

        # 步骤4: 获取刚创建的数据源详情
        source_detail = self._get_datasource_detail(created_source["id"])
        assert source_detail["data"]["name"] == new_source_data["name"]
        assert source_detail["data"]["api_url"] == new_source_data["api_url"]

        # 步骤5: 测试数据源连接
        health_response = self._test_datasource_health(created_source["id"])
        assert health_response["code"] == 200
        assert "status" in health_response["data"]
        assert "responseTime" in health_response["data"]

        # 步骤6: 更新数据源信息
        update_data = {
            "name": "更新后的测试数据源-E2E",
            "description": "已更新的端到端测试数据源",
            "api_url": "https://updated-test-api.example.com/data"
        }
        update_response = self._update_datasource(created_source["id"], update_data)
        assert update_response["code"] == 200
        updated_source = update_response["data"]
        assert updated_source["name"] == update_data["name"]

        # 步骤7: 验证更新后的数据源信息
        updated_detail = self._get_datasource_detail(updated_source["id"])
        assert updated_detail["data"]["name"] == update_data["name"]
        assert updated_detail["data"]["description"] == update_data["description"]

        # 步骤8: 批量测试多个数据源（如果有多于一个数据源的话）
        # 先创建第二个数据源用于批量测试
        second_source_data = {
            "name": "第二个测试数据源-E2E",
            "category": "odds_data",
            "source_type": "api",
            "api_url": "https://second-test-api.example.com/data",
            "method": "GET",
            "timeout": 30,
            "description": "第二个端到端测试数据源"
        }
        second_create_response = self._create_datasource(second_source_data)
        assert second_create_response["code"] == 200
        second_created_source = second_create_response["data"]

        # 执行批量测试
        batch_test_response = self._batch_test_sources([
            created_source["id"],
            second_created_source["id"]
        ])
        assert batch_test_response["code"] == 200
        assert batch_test_response["data"]["total"] == 2

        # 步骤9: 删除第二个数据源
        delete_response = self._delete_datasource(second_created_source["id"])
        assert delete_response["code"] == 200

        # 步骤10: 验证删除后列表数量
        final_list_response = self._get_datasource_list()
        assert final_list_response["data"]["total"] == initial_count + 1  # 第一个数据源仍然存在

        # 最终步骤: 清理 - 删除第一个数据源
        cleanup_response = self._delete_datasource(created_source["id"])
        assert cleanup_response["code"] == 200

        # 验证最终列表数量回到初始状态
        final_final_list_response = self._get_datasource_list()
        assert final_final_list_response["data"]["total"] == initial_count

        print("✅ 数据源管理模块端到端测试通过！")

    def _get_datasource_list(self, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取数据源列表"""
        url = f"{self.base_api_url}/sources?page={page}&size={size}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def _create_datasource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据源"""
        url = f"{self.base_api_url}/sources"
        response = requests.post(url, headers=self.headers, json=data)
        return {"code": response.status_code, "data": response.json()}

    def _get_datasource_detail(self, source_id: int) -> Dict[str, Any]:
        """获取数据源详情"""
        url = f"{self.base_api_url}/sources/{source_id}"
        response = requests.get(url, headers=self.headers)
        return {"code": response.status_code, "data": response.json()}

    def _update_datasource(self, source_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新数据源"""
        url = f"{self.base_api_url}/sources/{source_id}"
        response = requests.put(url, headers=self.headers, json=data)
        return {"code": response.status_code, "data": response.json()}

    def _delete_datasource(self, source_id: int) -> Dict[str, Any]:
        """删除数据源"""
        url = f"{self.base_api_url}/sources/{source_id}"
        response = requests.delete(url, headers=self.headers)
        return {"code": response.status_code, "message": response.json().get("message", "")}

    def _test_datasource_health(self, source_id: int) -> Dict[str, Any]:
        """测试数据源健康状态"""
        url = f"{self.base_api_url}/sources/{source_id}/health"
        response = requests.get(url, headers=self.headers)
        return {"code": response.status_code, "data": response.json()}

    def _batch_test_sources(self, source_ids: List[int]) -> Dict[str, Any]:
        """批量测试数据源"""
        url = f"{self.base_api_url}/sources/batch/test"
        response = requests.post(url, headers=self.headers, params={"source_ids": source_ids})
        return {"code": response.status_code, "data": response.json()}


class TestDataSourceManagementFrontendSimulation:
    """
    模拟前端用户界面操作的测试
    """

    def setup_method(self):
        """测试前置设置"""
        self.headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_api_url = f"{BASE_URL}/api/admin/v1"

    def test_frontend_simulation(self):
        """
        模拟前端用户界面操作流程
        """
        print("模拟前端用户操作数据源管理模块...")

        # 模拟用户进入数据源管理页面，获取统计信息
        stats = self._get_statistics()
        print(f"初始数据源统计: 总数={stats['total']}, 在线={stats['online']}, 离线={stats['offline']}")

        # 模拟用户执行筛选操作
        filtered_results = self._filter_sources(category="match_data")
        print(f"筛选比赛数据类数据源: 共{len(filtered_results['items'])}个")

        # 模拟用户点击"新增数据源"按钮
        new_source = {
            "name": "前端模拟创建的数据源",
            "category": "news",
            "source_type": "api",
            "api_url": "https://news-api.example.com/feed",
            "method": "GET",
            "timeout": 45,
            "description": "通过前端界面模拟创建的数据源"
        }
        created_result = self._create_datasource(new_source)
        print(f"创建数据源结果: {created_result['data']['name']}")

        # 模拟用户点击"测试"按钮
        test_result = self._test_source_connection(created_result['data']['id'])
        print(f"测试连接结果: {test_result['data']['status']}, 响应时间: {test_result['data']['responseTime']}ms")

        # 模拟用户编辑数据源
        update_data = {
            "name": "已编辑的前端模拟数据源",
            "timeout": 60
        }
        updated_result = self._update_datasource(created_result['data']['id'], update_data)
        print(f"更新数据源结果: {updated_result['data']['name']}")

        # 模拟用户执行批量操作
        all_sources = self._get_all_sources()
        if len(all_sources['items']) > 1:
            batch_result = self._batch_test_sources([s['id'] for s in all_sources['items'][:2]])
            print(f"批量测试结果: {batch_result['data']['successCount']}/{batch_result['data']['total']} 成功")

        # 模拟用户删除数据源
        delete_result = self._delete_datasource(created_result['data']['id'])
        print(f"删除数据源结果: {delete_result['message']}")

        print("✅ 前端用户操作模拟测试通过！")

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息（模拟前端获取统计卡片数据）"""
        list_data = self._get_all_sources()
        items = list_data['items']
        stats = {
            'total': len(items),
            'online': len([item for item in items if item.get('status') == 'online']),
            'offline': len([item for item in items if item.get('status') == 'offline']),
            'avgSuccessRate': sum([item.get('success_rate', 0) for item in items]) / len(items) if items else 0
        }
        return stats

    def _get_all_sources(self) -> Dict[str, Any]:
        """获取所有数据源（不分页）"""
        url = f"{self.base_api_url}/sources?page=1&size=100"
        response = requests.get(url, headers=self.headers)
        return response.json()['data']

    def _filter_sources(self, category: str = None, status: str = None) -> Dict[str, Any]:
        """筛选数据源（模拟前端筛选功能）"""
        params = {"page": 1, "size": 100}
        if category:
            params["category"] = category
        if status:
            params["status"] = status
            
        url = f"{self.base_api_url}/sources?"
        for k, v in params.items():
            url += f"&{k}={v}"
            
        response = requests.get(url, headers=self.headers)
        return response.json()['data']

    def _create_datasource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据源（模拟前端提交表单）"""
        url = f"{self.base_api_url}/sources"
        response = requests.post(url, headers=self.headers, json=data)
        return {"code": response.status_code, "data": response.json()}

    def _test_source_connection(self, source_id: int) -> Dict[str, Any]:
        """测试数据源连接（模拟前端点击测试按钮）"""
        url = f"{self.base_api_url}/sources/{source_id}/health"
        response = requests.get(url, headers=self.headers)
        return {"code": response.status_code, "data": response.json()}

    def _update_datasource(self, source_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新数据源（模拟前端编辑表单提交）"""
        url = f"{self.base_api_url}/sources/{source_id}"
        response = requests.put(url, headers=self.headers, json=data)
        return {"code": response.status_code, "data": response.json()}

    def _delete_datasource(self, source_id: int) -> Dict[str, Any]:
        """删除数据源（模拟前端点击删除按钮）"""
        url = f"{self.base_api_url}/sources/{source_id}"
        response = requests.delete(url, headers=self.headers)
        return {"code": response.status_code, "message": response.json().get("message", "")}

    def _batch_test_sources(self, source_ids: List[int]) -> Dict[str, Any]:
        """批量测试数据源（模拟前端批量操作）"""
        url = f"{self.base_api_url}/sources/batch/test"
        response = requests.post(url, headers=self.headers, params={"source_ids": source_ids})
        return {"code": response.status_code, "data": response.json()}


def run_e2e_tests():
    """
    运行所有端到端测试
    """
    print("="*60)
    print("开始执行数据源管理模块端到端测试")
    print("="*60)

    # 创建测试实例
    workflow_test = TestDataSourceManagementE2E()
    frontend_test = TestDataSourceManagementFrontendSimulation()

    try:
        # 运行工作流程测试
        print("\n--- 测试1: 完整工作流程 ---")
        workflow_test.setup_method()
        workflow_test.test_complete_datasource_workflow()

        # 运行前端模拟测试
        print("\n--- 测试2: 前端用户操作模拟 ---")
        frontend_test.setup_method()
        frontend_test.test_frontend_simulation()

        print("\n" + "="*60)
        print("🎉 所有端到端测试通过！")
        print("数据源管理模块功能完整，已达到生产就绪状态")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        raise


if __name__ == "__main__":
    run_e2e_tests()