"""
IP池管理API测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from backend.api.v1.admin.ip_pool_management import router
from backend.models.ip_pool import IPPool
from backend.schemas.ip_pool import IPPoolCreate, IPPoolUpdate


class TestIPPoolManagementAPI:
    """测试IP池管理API"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def mock_ip_pool(self):
        """模拟IP池对象"""
        pool = Mock(spec=IPPool)
        pool.id = 1
        pool.ip = "192.168.1.100"
        pool.port = 8080
        pool.protocol = "http"
        pool.location = "中国北京"
        pool.status = "active"
        pool.remarks = "测试IP池"
        pool.created_at = datetime.utcnow()
        pool.updated_at = datetime.utcnow()
        
        # 添加to_dict方法
        pool.to_dict = Mock(return_value={
            "id": pool.id,
            "ip": pool.ip,
            "port": pool.port,
            "protocol": pool.protocol,
            "location": pool.location,
            "status": pool.status,
            "remarks": pool.remarks,
            "created_at": pool.created_at.isoformat(),
            "updated_at": pool.updated_at.isoformat()
        })
        
        return pool
    
    @pytest.fixture
    def mock_query_result(self, mock_ip_pool):
        """模拟查询结果"""
        query_result = Mock()
        query_result.count = Mock(return_value=1)
        query_result.offset = Mock(return_value=query_result)
        query_result.limit = Mock(return_value=[mock_ip_pool])
        query_result.all = Mock(return_value=[mock_ip_pool])
        query_result.filter = Mock(return_value=query_result)
        query_result.first = Mock(return_value=mock_ip_pool)
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
    
    def test_get_ip_pools_success(self, test_client, mock_db, mock_query_result, mock_ip_pool):
        """测试获取IP池列表成功"""
        # 模拟查询
        mock_db.query.return_value = mock_query_result
        
        response = test_client.get("/api/v1/admin/ip-pools", params={"page": 1, "size": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["id"] == mock_ip_pool.id
    
    def test_get_ip_pools_with_filters(self, test_client, mock_db, mock_query_result):
        """测试带筛选条件的IP池列表获取"""
        mock_db.query.return_value = mock_query_result
        
        response = test_client.get(
            "/api/v1/admin/ip-pools",
            params={
                "page": 1,
                "size": 10,
                "status": "active",
                "search": "192.168"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 验证筛选条件被应用（通过mock验证）
        mock_query_result.filter.assert_called()
    
    def test_create_ip_pool_success(self, test_client, mock_db, mock_ip_pool):
        """测试创建IP池成功"""
        # 模拟新创建的IP池
        new_pool = mock_ip_pool
        
        response = test_client.post(
            "/api/v1/admin/ip-pools",
            json={
                "ip": "192.168.1.100",
                "port": 8080,
                "protocol": "http",
                "location": "中国北京",
                "status": "active",
                "remarks": "测试IP池"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "IP池创建成功"
        assert data["data"]["id"] == new_pool.id
        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_get_ip_pool_detail_success(self, test_client, mock_db, mock_ip_pool):
        """测试获取单个IP池详情成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_ip_pool
        
        response = test_client.get("/api/v1/admin/ip-pools/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == mock_ip_pool.id
    
    def test_get_ip_pool_detail_not_found(self, test_client, mock_db):
        """测试获取不存在的IP池详情"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.get("/api/v1/admin/ip-pools/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "IP池不存在" in data["detail"]
    
    def test_update_ip_pool_success(self, test_client, mock_db, mock_ip_pool):
        """测试更新IP池成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_ip_pool
        
        response = test_client.put(
            "/api/v1/admin/ip-pools/1",
            json={
                "status": "inactive",
                "remarks": "已更新"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "IP池更新成功"
        # 验证字段被更新
        assert mock_ip_pool.status == "inactive"
        assert mock_ip_pool.remarks == "已更新"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_ip_pool_not_found(self, test_client, mock_db):
        """测试更新不存在的IP池"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.put(
            "/api/v1/admin/ip-pools/999",
            json={"status": "inactive"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "IP池不存在" in data["detail"]
    
    def test_delete_ip_pool_success(self, test_client, mock_db, mock_ip_pool):
        """测试删除IP池成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_ip_pool
        
        response = test_client.delete("/api/v1/admin/ip-pools/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "IP池删除成功"
        assert data["data"]["id"] == 1
        mock_db.delete.assert_called_once_with(mock_ip_pool)
        mock_db.commit.assert_called_once()
    
    def test_delete_ip_pool_not_found(self, test_client, mock_db):
        """测试删除不存在的IP池"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.delete("/api/v1/admin/ip-pools/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "IP池不存在" in data["detail"]
    
    def test_test_ip_pool_connection_success(self, test_client, mock_db, mock_ip_pool):
        """测试IP池连接测试成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_ip_pool
        
        response = test_client.post("/api/v1/admin/ip-pools/1/test-connection")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "连接测试完成"
        assert "data" in data
        assert data["data"]["id"] == mock_ip_pool.id
        assert data["data"]["status"] == "success"
    
    def test_test_ip_pool_connection_not_found(self, test_client, mock_db):
        """测试不存在的IP池连接测试"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.post("/api/v1/admin/ip-pools/999/test-connection")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "IP池不存在" in data["detail"]
    
    def test_batch_update_ip_pool_status_success(self, test_client, mock_db, mock_ip_pool):
        """测试批量更新IP池状态成功"""
        # 模拟查询结果
        mock_pools = [mock_ip_pool, mock_ip_pool]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_pools
        
        response = test_client.post(
            "/api/v1/admin/ip-pools/batch-update-status",
            json={
                "ids": [1, 2],
                "status": "banned"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "批量更新状态成功"
        assert data["data"]["updated_count"] == len(mock_pools)
        # 验证每个IP池的状态都被更新
        for pool in mock_pools:
            assert pool.status == "banned"
        mock_db.commit.assert_called_once()
    
    def test_get_ip_pool_health_success(self, test_client, mock_db, mock_ip_pool):
        """测试获取IP池健康状态成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_ip_pool
        
        response = test_client.get("/api/v1/admin/ip-pools/1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "健康状态获取成功"
        assert "data" in data
        assert data["data"]["id"] == mock_ip_pool.id
        assert data["data"]["status"] == mock_ip_pool.status
        assert "response_time_ms" in data["data"]
    
    def test_get_ip_pool_health_not_found(self, test_client, mock_db):
        """测试获取不存在的IP池健康状态"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.get("/api/v1/admin/ip-pools/999/health")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "IP池不存在" in data["detail"]
    
    def test_get_ip_pool_stats_success(self, test_client, mock_db):
        """测试获取IP池统计信息成功"""
        # 模拟统计查询
        mock_db.query.return_value.count.return_value = 50
        
        # 模拟按状态筛选的查询
        def side_effect(*args, **kwargs):
            if "active" in args:
                return 30
            elif "inactive" in args:
                return 15
            elif "banned" in args:
                return 5
            return Mock()
        
        mock_db.query.return_value.filter.return_value.count.side_effect = side_effect
        
        response = test_client.get("/api/v1/admin/ip-pools/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "统计信息获取成功"
        assert "total" in data["data"]
        assert "active" in data["data"]
        assert "inactive" in data["data"]
        assert "banned" in data["data"]
        assert "latest_update" in data["data"]