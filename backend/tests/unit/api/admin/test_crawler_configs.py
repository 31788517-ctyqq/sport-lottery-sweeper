"""
源配置API测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from backend.api.v1.admin.crawler_configs import router, CrawlerConfig, CreateConfigRequest


class TestCrawlerConfigsAPI:
    """测试源配置API"""
    
    @pytest.fixture
    def test_client(self):
        """创建测试客户端"""
        # 创建测试应用
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/admin")
        
        return TestClient(app)
    
    def test_get_configs_success(self, test_client):
        """测试获取配置列表成功"""
        response = test_client.get("/api/v1/admin/crawler/config")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # 验证返回的数据结构
        config = data[0]
        assert "id" in config
        assert "name" in config
        assert "config_type" in config
        assert "content" in config
        assert "version" in config
        assert "created_at" in config
        assert "updated_at" in config
        
        # 验证mock数据
        assert config["name"] == "全局默认配置"
        assert config["config_type"] == "global"
        assert "timeout" in config["content"]
        assert "retry" in config["content"]
        assert "headers" in config["content"]
    
    def test_get_configs_content_structure(self, test_client):
        """测试配置内容结构"""
        response = test_client.get("/api/v1/admin/crawler/config")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证第一个配置（全局配置）
        global_config = data[0]
        assert global_config["config_type"] == "global"
        assert global_config["content"]["timeout"] == 10
        assert global_config["content"]["retry"] == 3
        assert global_config["content"]["headers"]["User-Agent"] == "default-agent"
        
        # 验证第二个配置（单源配置）
        single_config = data[1]
        assert single_config["config_type"] == "single"
        assert single_config["content"]["frequency"] == "5m"
        assert single_config["content"]["depth"] == 2
        assert single_config["content"]["parse_rules"]["title"] == "h1"
    
    def test_create_config_success(self, test_client):
        """测试创建配置成功"""
        config_data = {
            "name": "测试配置",
            "config_type": "test",
            "content": {
                "timeout": 20,
                "retry": 5,
                "custom_setting": "value"
            }
        }
        
        response = test_client.post(
            "/api/v1/admin/crawler/config",
            json=config_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "created"
        assert "id" in data
        assert data["id"] == 999
    
    def test_create_config_validation(self, test_client):
        """测试创建配置的数据验证"""
        # 测试缺少必需字段
        incomplete_data = {
            "name": "测试配置"
            # 缺少config_type和content
        }
        
        response = test_client.post(
            "/api/v1/admin/crawler/config",
            json=incomplete_data
        )
        
        # 应该返回422验证错误
        assert response.status_code == 422
    
    def test_update_config_success(self, test_client):
        """测试更新配置成功"""
        config_id = 1
        
        response = test_client.put(f"/api/v1/admin/crawler/config/{config_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "updated"
    
    def test_update_config_with_request_body(self, test_client):
        """测试更新配置（即使没有请求体，路由也应该工作）"""
        config_id = 2
        
        response = test_client.put(
            f"/api/v1/admin/crawler/config/{config_id}",
            json={"name": "更新后的配置"}  # 即使API不接受请求体，发送也没关系
        )
        
        # 即使不接受请求体，PUT方法也应该返回200
        assert response.status_code == 200
    
    def test_delete_config_success(self, test_client):
        """测试删除配置成功"""
        config_id = 1
        
        response = test_client.delete(f"/api/v1/admin/crawler/config/{config_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "deleted"
    
    def test_config_data_types(self, test_client):
        """测试配置数据的类型"""
        response = test_client.get("/api/v1/admin/crawler/config")
        
        assert response.status_code == 200
        data = response.json()
        
        for config in data:
            # 验证数据类型
            assert isinstance(config["id"], int)
            assert isinstance(config["name"], str)
            assert isinstance(config["config_type"], str)
            assert isinstance(config["content"], dict)
            assert isinstance(config["version"], int)
            assert isinstance(config["created_at"], str)
            assert isinstance(config["updated_at"], str)
            
            # 验证时间格式（ISO格式）
            try:
                datetime.fromisoformat(config["created_at"].replace('Z', '+00:00'))
                datetime.fromisoformat(config["updated_at"].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("时间格式不是有效的ISO格式")
    
    def test_config_content_validation(self, test_client):
        """测试配置内容的结构验证"""
        response = test_client.get("/api/v1/admin/crawler/config")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证第一个配置（全局配置）的内容
        global_config = data[0]
        content = global_config["content"]
        
        assert "timeout" in content
        assert "retry" in content
        assert "headers" in content
        
        # 验证类型
        assert isinstance(content["timeout"], int)
        assert isinstance(content["retry"], int)
        assert isinstance(content["headers"], dict)
        assert "User-Agent" in content["headers"]
        assert isinstance(content["headers"]["User-Agent"], str)
    
    def test_config_endpoint_resilience(self, test_client):
        """测试配置端点的健壮性"""
        # 测试无效的配置ID
        invalid_config_id = "invalid"
        
        response = test_client.put(f"/api/v1/admin/crawler/config/{invalid_config_id}")
        
        # 即使参数解析失败，也应该有响应
        # 可能是404或422，取决于FastAPI的路由匹配
        assert response.status_code in [404, 422, 400]
    
    def test_config_list_consistency(self, test_client):
        """测试配置列表的一致性"""
        response = test_client.get("/api/v1/admin/crawler/config")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证返回的配置数量
        assert len(data) >= 2
        
        # 验证每个配置都有完整的数据
        for config in data:
            required_fields = ["id", "name", "config_type", "content", "version", "created_at", "updated_at"]
            for field in required_fields:
                assert field in config, f"缺少字段: {field}"
                
            # 验证内容字段是字典
            assert isinstance(config["content"], dict), "content字段必须是字典"
            
            # 验证版本号是正数
            assert config["version"] > 0, "版本号必须是正数"