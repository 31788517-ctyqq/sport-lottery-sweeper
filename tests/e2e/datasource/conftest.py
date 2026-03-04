"""
E2E测试共享配置和Fixture
"""
import pytest
import os
from typing import Dict, Any

@pytest.fixture(scope="session")
def base_url():
    """基础URL配置"""
    return os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def admin_headers():
    """管理员认证头"""
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-jwt-token")
    return {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def base_api_url(base_url):
    """API基础URL"""
    return f"{base_url}/api/admin/v1"

@pytest.fixture
def sample_datasource_data():
    """示例数据源数据"""
    return {
        "name": "测试数据源",
        "category": "match_data",
        "source_type": "api",
        "api_url": "https://test-api.example.com/data",
        "method": "GET",
        "timeout": 30,
        "description": "测试用数据源"
    }
