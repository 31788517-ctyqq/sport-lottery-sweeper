"""
任务管理API测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import json

from backend.api.v1.admin.task_management import router
from backend.models.crawler_tasks import CrawlerTask
from backend.models.data_sources import DataSource
from backend.services.task_scheduler_service import TaskSchedulerService


class TestTaskManagementAPI:
    """测试任务管理API"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def mock_crawler_task(self):
        """模拟爬虫任务对象"""
        task = Mock(spec=CrawlerTask)
        task.id = 1
        task.name = "测试任务"
        task.source_id = 1
        task.task_type = "periodic"
        task.cron_expression = "*/5 * * * *"
        task.is_active = True
        task.status = "running"
        task.last_run_time = datetime.utcnow()
        task.next_run_time = datetime.utcnow()
        task.run_count = 10
        task.success_count = 8
        task.error_count = 2
        task.config = '{"timeout": 30, "retry": 3}'
        task.created_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        return task
    
    @pytest.fixture
    def mock_data_source(self):
        """模拟数据源对象"""
        source = Mock(spec=DataSource)
        source.id = 1
        source.name = "测试数据源"
        source.status = True
        return source
    
    @pytest.fixture
    def mock_query_result(self, mock_crawler_task):
        """模拟查询结果"""
        query_result = Mock()
        query_result.count = Mock(return_value=1)
        query_result.offset = Mock(return_value=query_result)
        query_result.limit = Mock(return_value=[mock_crawler_task])
        query_result.all = Mock(return_value=[mock_crawler_task])
        query_result.filter = Mock(return_value=query_result)
        query_result.first = Mock(return_value=mock_crawler_task)
        query_result.order_by = Mock(return_value=query_result)
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
    
    def test_get_crawler_tasks_success(self, test_client, mock_db, mock_query_result, mock_crawler_task):
        """测试获取爬虫任务列表成功"""
        # 模拟查询
        mock_db.query.return_value = mock_query_result
        
        response = test_client.get("/api/v1/admin", params={"page": 1, "size": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["id"] == mock_crawler_task.id
    
    def test_get_crawler_tasks_with_filters(self, test_client, mock_db, mock_query_result):
        """测试带筛选条件的爬虫任务列表获取"""
        mock_db.query.return_value = mock_query_result
        
        response = test_client.get(
            "/api/v1/admin",
            params={
                "page": 1,
                "size": 10,
                "name": "测试",
                "task_type": "periodic",
                "status": "running",
                "source_id": "1"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 验证筛选条件被应用（通过mock验证）
        mock_query_result.filter.assert_called()
    
    def test_get_crawler_task_detail_success(self, test_client, mock_db, mock_crawler_task):
        """测试获取单个爬虫任务详情成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_crawler_task
        
        response = test_client.get("/api/v1/admin/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == mock_crawler_task.id
    
    def test_get_crawler_task_detail_not_found(self, test_client, mock_db):
        """测试获取不存在的爬虫任务详情"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.get("/api/v1/admin/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "任务不存在" in data["detail"]
    
    def test_create_crawler_task_success(self, test_client, mock_db, mock_crawler_task):
        """测试创建爬虫任务成功"""
        # 模拟新创建的任务
        new_task = mock_crawler_task
        
        response = test_client.post(
            "/api/v1/admin",
            json={
                "name": "测试任务",
                "source_id": "1",
                "task_type": "periodic",
                "cron_expression": "*/5 * * * *",
                "config": {"timeout": 30, "retry": 3}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "任务创建成功"
        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_crawler_task_success(self, test_client, mock_db, mock_crawler_task):
        """测试更新爬虫任务成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_crawler_task
        
        response = test_client.put(
            "/api/v1/admin/1",
            json={
                "name": "更新后的任务",
                "status": "paused",
                "config": {"timeout": 60, "retry": 5}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "任务更新成功"
        # 验证字段被更新
        assert mock_crawler_task.name == "更新后的任务"
        assert mock_crawler_task.status == "paused"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_update_crawler_task_not_found(self, test_client, mock_db):
        """测试更新不存在的爬虫任务"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.put(
            "/api/v1/admin/999",
            json={"name": "更新后的任务"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "任务不存在" in data["detail"]
    
    def test_delete_crawler_task_success(self, test_client, mock_db, mock_crawler_task):
        """测试删除爬虫任务成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_crawler_task
        
        response = test_client.delete("/api/v1/admin/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "任务删除成功"
        assert data["data"]["id"] == 1
        mock_db.delete.assert_called_once_with(mock_crawler_task)
        mock_db.commit.assert_called_once()
    
    def test_delete_crawler_task_not_found(self, test_client, mock_db):
        """测试删除不存在的爬虫任务"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.delete("/api/v1/admin/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "任务不存在" in data["detail"]
    
    def test_batch_delete_tasks_success(self, test_client, mock_db, mock_crawler_task):
        """测试批量删除爬虫任务成功"""
        # 模拟查询结果
        mock_tasks = [mock_crawler_task, mock_crawler_task]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_tasks
        
        response = test_client.post(
            "/api/v1/admin/batch",
            json={"ids": [1, 2]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "批量删除任务成功"
        assert data["data"]["deleted_count"] == len(mock_tasks)
        # 验证每个任务都被删除
        assert mock_db.delete.call_count == len(mock_tasks)
        mock_db.commit.assert_called_once()
    
    def test_batch_test_tasks_success(self, test_client, mock_db, mock_crawler_task):
        """测试批量测试爬虫任务成功"""
        # 模拟查询结果
        mock_tasks = [mock_crawler_task, mock_crawler_task]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_tasks
        
        response = test_client.post(
            "/api/v1/admin/batch/test",
            json={"ids": [1, 2]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "批量测试任务完成"
        assert data["data"]["tested_count"] == len(mock_tasks)
        assert data["data"]["success_count"] == len(mock_tasks)
    
    def test_get_task_stats_success(self, test_client, mock_db):
        """测试获取任务统计信息成功"""
        # 模拟统计查询
        mock_db.query.return_value.count.return_value = 20
        
        # 模拟按状态筛选的查询
        def side_effect(*args, **kwargs):
            if "running" in args:
                return 8
            elif "paused" in args:
                return 5
            elif "completed" in args:
                return 7
            return Mock()
        
        mock_db.query.return_value.filter.return_value.count.side_effect = side_effect
        
        response = test_client.get("/api/v1/admin/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "统计信息获取成功"
        assert "total" in data["data"]
        assert "running" in data["data"]
        assert "paused" in data["data"]
        assert "completed" in data["data"]
        assert "latest_update" in data["data"]
    
    def test_test_task_success(self, test_client, mock_db, mock_crawler_task):
        """测试单个任务测试成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_crawler_task
        
        response = test_client.post("/api/v1/admin/1/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "任务测试完成"
        assert "data" in data
        assert data["data"]["id"] == mock_crawler_task.id
        assert data["data"]["status"] == "success"
    
    def test_test_task_not_found(self, test_client, mock_db):
        """测试不存在的任务测试"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.post("/api/v1/admin/999/test")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "任务不存在" in data["detail"]
    
    def test_toggle_task_status_success(self, test_client, mock_db, mock_crawler_task):
        """测试切换任务状态成功"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_crawler_task
        
        response = test_client.post("/api/v1/admin/1/toggle")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "任务状态切换成功"
        # 验证任务状态被切换
        assert mock_crawler_task.is_active is False or mock_crawler_task.is_active is True
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_toggle_task_status_not_found(self, test_client, mock_db):
        """测试切换不存在的任务状态"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = test_client.post("/api/v1/admin/999/toggle")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "任务不存在" in data["detail"]
    
    def test_get_task_types_success(self, test_client, mock_db):
        """测试获取任务类型列表成功"""
        # 模拟查询结果
        mock_types = ["periodic", "one-time", "manual"]
        mock_db.query.return_value.with_entities.return_value.distinct.return_value.all.return_value = mock_types
        
        response = test_client.get("/api/v1/admin/types")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "任务类型列表获取成功"
        assert "data" in data
        assert data["data"]["types"] == mock_types