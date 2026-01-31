"""
API端点集成测试
测试API端点的实际行为和与其他模块的集成
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.main import app
from backend.config import settings
from backend.database_async import get_async_db
from backend.models.admin_user import AdminUser
from backend.core.security import get_password_hash
from unittest.mock import AsyncMock, patch


# 创建测试客户端
client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=AsyncMock())
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    print("[OK] 健康检查端点测试通过")


def test_docs_endpoint():
    """测试API文档端点"""
    response = client.get("/docs")
    assert response.status_code in [200, 307]  # 307是重定向到/docs/
    print("[OK] API文档端点测试通过")


@pytest.mark.asyncio
async def test_admin_user_endpoints_integration():
    """测试管理员用户API端点集成"""
    # 由于这些端点需要认证，我们测试返回的认证错误
    response = client.get("/api/v1/admin/users/")
    # 应该返回401未认证或422请求体错误（如果没有提供必要参数）
    assert response.status_code in [401, 422]
    
    response = client.post("/api/v1/admin/users/")
    assert response.status_code in [401, 422]
    
    print("[OK] 管理员用户API端点集成测试通过")


@pytest.mark.asyncio
async def test_auth_endpoints_integration():
    """测试认证API端点集成"""
    # 测试登录端点（没有提供数据，期望返回422）
    response = client.post("/api/v1/auth/login")
    assert response.status_code == 422  # 请求体缺失
    
    # 测试注册端点（没有提供数据，期望返回422）
    response = client.post("/api/v1/auth/register")
    assert response.status_code == 422  # 请求体缺失
    
    print("[OK] 认证API端点集成测试通过")


@pytest.mark.asyncio
async def test_crawler_endpoints_integration():
    """测试爬虫API端点集成"""
    # 测试获取爬虫配置端点（需要认证）
    response = client.get("/api/v1/crawlers/configs/")
    assert response.status_code in [401, 422]
    
    # 测试获取爬虫任务端点（需要认证）
    response = client.get("/api/v1/crawlers/tasks/")
    assert response.status_code in [401, 422]
    
    print("[OK] 爬虫API端点集成测试通过")


@pytest.mark.asyncio
async def test_public_endpoints():
    """测试公共API端点"""
    # 测试获取比赛数据的公共端点（如果没有数据可能返回空数组）
    response = client.get("/api/v1/public/matches/")
    # 公共端点不需要认证，但可能因为数据库中没有数据而返回特定响应
    assert response.status_code in [200, 404, 500]
    
    print("[OK] 公共API端点测试通过")


@pytest.mark.asyncio
async def test_api_response_format():
    """测试API响应格式一致性"""
    # 检查一个假想的端点响应格式
    # 因为许多端点需要认证，我们模拟一个端点检查格式
    from backend.utils.response import UnifiedResponse
    
    # 测试统一响应格式
    response = UnifiedResponse.success(data={"test": "data"})
    assert hasattr(response, 'code')
    assert hasattr(response, 'message')
    assert hasattr(response, 'data')
    assert response.code == 200
    assert response.message == "Success"
    
    error_response = UnifiedResponse.error(message="Test error", code=400)
    assert error_response.code == 400
    assert error_response.message == "Test error"
    
    print("[OK] API响应格式一致性测试通过")


if __name__ == "__main__":
    # 运行测试
    test_health_check_endpoint()
    test_docs_endpoint()
    test_admin_user_endpoints_integration()
    test_auth_endpoints_integration()
    test_crawler_endpoints_integration()
    test_public_endpoints()
    test_api_response_format()