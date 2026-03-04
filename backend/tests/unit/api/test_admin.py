#!/usr/bin/env python3
"""
管理员API单元测试
测试后台管理相关的API端点
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.security import create_access_token
from backend.models.user import UserRole


@pytest.fixture
def admin_user_token():
    """生成管理员用户token"""
    return create_access_token({
        "sub": "admin@test.com",
        "role": UserRole.ADMIN.value
    })


@pytest.fixture
def operator_user_token():
    """生成运营用户token"""
    return create_access_token({
        "sub": "operator@test.com",
        "role": UserRole.OPERATOR.value
    })


@pytest.fixture
def normal_user_token():
    """生成普通用户token"""
    return create_access_token({
        "sub": "user@test.com",
        "role": UserRole.USER.value
    })


class TestAdminUserManagement:
    """测试管理员用户管理功能"""

    @patch('backend.api.v1.admin.User')
    def test_get_users_as_admin(self, mock_user_class, admin_user_token):
        """测试管理员获取用户列表"""
        # Mock用户查询
        mock_users = [
            MagicMock(
                id=1, email="user1@test.com", role=UserRole.USER.value,
                is_active=True, created_at="2024-01-01T00:00:00",
                last_login="2024-01-15T10:30:00"
            ),
            MagicMock(
                id=2, email="user2@test.com", role=UserRole.USER.value,
                is_active=False, created_at="2024-01-02T00:00:00",
                last_login=None
            )
        ]
        mock_user_class.query.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_users
        mock_user_class.query.filter.return_value.count.return_value = 2

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users?skip=0&limit=100",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["users"]) == 2
        assert data["data"]["total"] == 2
        assert data["data"]["skip"] == 0
        assert data["data"]["limit"] == 100

    @patch('backend.api.v1.admin.User')
    def test_get_users_as_operator(self, mock_user_class, operator_user_token):
        """测试运营人员获取用户列表"""
        mock_user_class.query.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_user_class.query.filter.return_value.count.return_value = 0

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {operator_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_users_permission_denied(self, normal_user_token):
        """测试普通用户访问管理员接口被拒绝"""
        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == 403

    @patch('backend.api.v1.admin.User')
    def test_get_user_by_id_success(self, mock_user_class, admin_user_token):
        """测试根据ID获取用户信息成功"""
        mock_user = MagicMock(
            id=1, email="user@test.com", role=UserRole.USER.value,
            is_active=True, created_at="2024-01-01T00:00:00",
            last_login="2024-01-15T10:30:00"
        )
        mock_user_class.query.get_or_404.return_value = mock_user

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == 1
        assert data["data"]["email"] == "user@test.com"

    @patch('backend.api.v1.admin.User')
    def test_update_user_role_success(self, mock_user_class, admin_user_token):
        """测试更新用户角色成功"""
        mock_user = MagicMock(id=1, email="user@test.com", role=UserRole.USER.value)
        mock_user_class.query.get_or_404.return_value = mock_user

        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/users/1/role",
            json={"role": "operator"},
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "用户角色更新成功"
        assert mock_user.role == "operator"

    @patch('backend.api.v1.admin.User')
    def test_update_user_role_invalid_role(self, mock_user_class, admin_user_token):
        """测试更新用户角色为无效角色"""
        mock_user = MagicMock()
        mock_user_class.query.get_or_404.return_value = mock_user

        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/users/1/role",
            json={"role": "invalid_role"},
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400

    @patch('backend.api.v1.admin.User')
    def test_toggle_user_status_success(self, mock_user_class, admin_user_token):
        """测试切换用户状态成功"""
        mock_user = MagicMock(id=1, email="user@test.com", is_active=True)
        mock_user_class.query.get_or_404.return_value = mock_user

        client = TestClient(app)
        response = client.patch(
            "/api/v1/admin/users/1/toggle-status",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "用户状态切换成功"
        assert mock_user.is_active == False

    @patch('backend.api.v1.admin.User')
    def test_delete_user_success(self, mock_user_class, admin_user_token):
        """测试删除用户成功"""
        mock_user = MagicMock(id=1, email="user@test.com")
        mock_user_class.query.get_or_404.return_value = mock_user

        client = TestClient(app)
        response = client.delete(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "用户删除成功"


class TestAdminStats:
    """测试管理员统计功能"""

    @patch('backend.api.v1.admin.User')
    def test_get_system_stats(self, mock_user_class, admin_user_token):
        """测试获取系统统计信息"""
        # Mock统计数据
        mock_user_class.query.filter.return_value.count.side_effect = [150, 120, 25, 5]
        
        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/stats/system",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        stats = data["data"]
        assert stats["total_users"] == 150
        assert stats["active_users"] == 120
        assert stats["inactive_users"] == 25
        assert stats["admin_users"] == 5


class TestAdminValidation:
    """测试管理员API的输入验证"""

    def test_get_users_invalid_pagination(self, admin_user_token):
        """测试无效的分页参数"""
        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users?skip=-1&limit=10000",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        # FastAPI应该自动验证并返回422
        assert response.status_code in [422, 400]

    def test_update_user_role_missing_field(self, admin_user_token):
        """测试缺少role字段的请求"""
        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/users/1/role",
            json={},
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 422

    def test_update_user_role_empty_role(self, admin_user_token):
        """测试空role字段的请求"""
        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/users/1/role",
            json={"role": ""},
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 400


class TestAdminErrorHandling:
    """测试管理员API的错误处理"""

    @patch('backend.api.v1.admin.User')
    def test_get_user_not_found(self, mock_user_class, admin_user_token):
        """测试获取不存在的用户"""
        from sqlalchemy.exc import SQLAlchemyError
        mock_user_class.query.get_or_404.side_effect = SQLAlchemyError("User not found")

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users/999",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 500

    @patch('backend.api.v1.admin.User')
    def test_database_error_handling(self, mock_user_class, admin_user_token):
        """测试数据库错误处理"""
        from sqlalchemy.exc import SQLAlchemyError
        mock_user_class.query.filter.side_effect = SQLAlchemyError("Database connection failed")

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 500


# 性能测试相关
class TestAdminPerformance:
    """测试管理员API的性能相关场景"""

    @patch('backend.api.v1.admin.User')
    def test_get_users_large_dataset(self, mock_user_class, admin_user_token):
        """测试大数据集下的用户列表查询"""
        # Mock大量用户数据
        mock_users = [MagicMock(id=i, email=f"user{i}@test.com") for i in range(1000)]
        mock_user_class.query.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_users[:50]  # 限制返回50条
        mock_user_class.query.filter.return_value.count.return_value = 1000

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/users?skip=0&limit=50",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["users"]) == 50
        assert data["data"]["total"] == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
