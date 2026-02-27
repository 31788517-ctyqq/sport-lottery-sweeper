"""
头部管理API测试
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.v1.admin.headers_management import router
from backend.models.headers import RequestHeader


class TestHeadersManagementAPI:
    """测试头部管理API"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock(spec=Session)
        return db

    @pytest.fixture
    def mock_request_header(self):
        """模拟请求头对象"""
        header = Mock(spec=RequestHeader)
        header.id = 1
        header.domain = "example.com"
        header.name = "User-Agent"
        header.value = "Mozilla/5.0"
        header.type = "request"
        header.priority = 1
        header.status = "enabled"
        header.remarks = "测试请求头"
        header.created_at = datetime.utcnow()
        header.updated_at = datetime.utcnow()

        # 添加to_dict方法
        header.to_dict = Mock(return_value={
            "id": header.id,
            "domain": header.domain,
            "name": header.name,
            "value": header.value,
            "type": header.type,
            "priority": header.priority,
            "status": header.status,
            "remarks": header.remarks,
            "created_at": header.created_at.isoformat(),
            "updated_at": header.updated_at.isoformat()
        })

        return header

    @pytest.fixture
    def mock_query_result(self, mock_request_header):
        """模拟查询结果"""
        query_result = Mock()
        query_result.count = Mock(return_value=1)
        query_result.offset = Mock(return_value=query_result)
        query_result.limit = Mock(return_value=[mock_request_header])
        query_result.all = Mock(return_value=[mock_request_header])
        query_result.filter = Mock(return_value=query_result)
        query_result.first = Mock(return_value=mock_request_header)
        return query_result

    @pytest.fixture
    def test_client(self, mock_db):
        """创建测试客户端"""
        # 创建测试应用
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/admin")

        # 模拟依赖项
        def override_get_db():
            return mock_db

        app.dependency_overrides[router.dependencies[0].dependency] = override_get_db

        return TestClient(app)

    def test_get_headers_success(
        self, test_client, mock_db, mock_query_result, mock_request_header
    ):
        """测试获取请求头列表成功"""
        # 模拟查询
        mock_db.query.return_value = mock_query_result

        response = test_client.get(
            "/api/v1/admin/headers",
            params={"page": 1, "size": 10},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["id"] == mock_request_header.id

    def test_get_headers_with_filters(
        self, test_client, mock_db, mock_query_result
    ):
        """测试带筛选条件的请求头列表获取"""
        mock_db.query.return_value = mock_query_result

        response = test_client.get(
            "/api/v1/admin/headers",
            params={
                "page": 1,
                "size": 10,
                "domain": "example.com",
                "status": "enabled",
                "type": "request",
                "search": "User-Agent",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 验证筛选条件被应用（通过mock验证）
        mock_query_result.filter.assert_called()

    def test_create_header_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试创建请求头成功"""
        # 模拟新创建的请求头
        new_header = mock_request_header

        response = test_client.post(
            "/api/v1/admin/headers",
            json={
                "domain": "example.com",
                "name": "User-Agent",
                "value": "Mozilla/5.0",
                "type": "request",
                "priority": 1,
                "status": "enabled",
                "remarks": "测试请求头",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "请求头创建成功"
        assert data["data"]["id"] == new_header.id
        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_header_detail_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试获取单个请求头详情成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_request_header
        )

        response = test_client.get("/api/v1/admin/headers/1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == mock_request_header.id

    def test_get_header_detail_not_found(self, test_client, mock_db):
        """测试获取不存在的请求头详情"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        response = test_client.get("/api/v1/admin/headers/999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "请求头不存在" in data["detail"]

    def test_update_header_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试更新请求头成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_request_header
        )

        response = test_client.put(
            "/api/v1/admin/headers/1",
            json={
                "value": "Updated-User-Agent",
                "status": "disabled",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "请求头更新成功"
        # 验证字段被更新
        assert mock_request_header.value == "Updated-User-Agent"
        assert mock_request_header.status == "disabled"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_header_not_found(self, test_client, mock_db):
        """测试更新不存在的请求头"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        response = test_client.put(
            "/api/v1/admin/headers/999",
            json={"value": "Updated-User-Agent"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "请求头不存在" in data["detail"]

    def test_delete_header_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试删除请求头成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_request_header
        )

        response = test_client.delete("/api/v1/admin/headers/1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "请求头删除成功"
        assert data["data"]["id"] == 1
        mock_db.delete.assert_called_once_with(mock_request_header)
        mock_db.commit.assert_called_once()

    def test_delete_header_not_found(self, test_client, mock_db):
        """测试删除不存在的请求头"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        response = test_client.delete("/api/v1/admin/headers/999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "请求头不存在" in data["detail"]

    def test_batch_delete_headers_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试批量删除请求头成功"""
        # 模拟查询结果
        mock_headers = [mock_request_header]
        mock_db.query.return_value.filter.return_value.all.return_value = (
            mock_headers
        )

        response = test_client.post(
            "/api/v1/admin/headers/batch",
            json={"ids": [1, 2, 3]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "批量删除请求头成功"
        assert data["data"]["deleted_count"] == len(mock_headers)
        # 验证每个请求头都被删除
        assert mock_db.delete.call_count == len(mock_headers)
        mock_db.commit.assert_called_once()

    def test_batch_test_headers_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试批量测试请求头成功"""
        # 模拟查询结果
        mock_headers = [mock_request_header, mock_request_header]
        mock_db.query.return_value.filter.return_value.all.return_value = (
            mock_headers
        )

        response = test_client.post(
            "/api/v1/admin/headers/batch/test",
            json={"ids": [1, 2]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "批量测试请求头完成"
        assert data["data"]["tested_count"] == len(mock_headers)
        assert data["data"]["success_count"] == len(mock_headers)

    def test_get_headers_stats_success(self, test_client, mock_db):
        """测试获取请求头统计信息成功"""
        # 模拟统计查询
        mock_db.query.return_value.count.return_value = 10
        mock_db.query.return_value.filter.return_value.count.return_value = 8

        # 模拟按类型分组统计
        with patch("backend.api.v1.admin.headers_management.func") as mock_func:
            mock_func.count.return_value = 5
            mock_db.query.return_value.group_by.return_value.all.return_value = [
                ("request", 6),
                ("response", 4),
            ]

        response = test_client.get("/api/v1/admin/headers/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "统计信息获取成功"
        assert "total" in data["data"]
        assert "enabled" in data["data"]
        assert "disabled" in data["data"]
        assert "by_type" in data["data"]

    def test_test_header_success(
        self, test_client, mock_db, mock_request_header
    ):
        """测试单个请求头测试成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_request_header
        )

        response = test_client.post("/api/v1/admin/headers/1/test")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "请求头测试完成"
        assert "data" in data
        assert data["data"]["id"] == mock_request_header.id
        assert data["data"]["status"] == "success"

    def test_test_header_not_found(self, test_client, mock_db):
        """测试不存在的请求头测试"""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        response = test_client.post("/api/v1/admin/headers/999/test")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "请求头不存在" in data["detail"]