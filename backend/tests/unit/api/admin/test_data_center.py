"""
数据中心API测试
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from backend.api.v1.admin.data_center import router
from backend.models.data_sources import DataSource


class TestDataCenterAPI:
    """测试数据中心API"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        db = Mock(spec=Session)
        return db

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

        app.dependency_overrides[
            router.dependencies[0].dependency
        ] = override_get_db

        return TestClient(app)

    def test_get_data_center_overview_success(self, test_client, mock_db):

        """测试获取数据中心总览数据成功"""
        # 模拟统计查询
        mock_db.query.return_value.count.return_value = 100
        mock_db.query.return_value.filter.return_value.count.return_value = 50

        response = test_client.get("/api/v1/admin/data-center/overview")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "数据中心总览获取成功"
        assert "data" in data

        overview_data = data["data"]
        assert "totalMatches" in overview_data
        assert "totalOdds" in overview_data
        assert "totalSPRecords" in overview_data
        assert "activeSources" in overview_data
        assert "todayNewData" in overview_data
        assert "lastUpdate" in overview_data

        # 验证查询被调用
        assert mock_db.query.call_count >= 4  # 至少调用4次查询

    def test_get_data_trend_success(self, test_client, mock_db):
        """测试获取数据趋势成功"""
        response = test_client.get(
            "/api/v1/admin/data-center/data-trend",
            params={"days": 30}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "数据趋势获取成功"
        assert "data" in data

        trend_data = data["data"]
        assert "trends" in trend_data
        assert "summary" in trend_data

        trends = trend_data["trends"]
        summary = trend_data["summary"]

        # 验证趋势数据
        assert len(trends) == 30  # 30天的数据
        for trend in trends:
            assert "date" in trend
            assert "matches" in trend
            assert "odds" in trend
            assert "sp_records" in trend

            # 验证数据类型
            assert isinstance(trend["date"], str)
            assert isinstance(trend["matches"], int)
            assert isinstance(trend["odds"], int)
            assert isinstance(trend["sp_records"], int)

        # 验证汇总信息
        assert "totalTrendPoints" in summary
        assert "startDate" in summary
        assert "endDate" in summary
        assert summary["totalTrendPoints"] == 30

    def test_get_data_trend_with_default_days(self, test_client):
        """测试使用默认天数获取数据趋势"""
        response = test_client.get("/api/v1/admin/data-center/data-trend")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        trend_data = data["data"]
        trends = trend_data["trends"]

        # 默认应该是30天
        assert len(trends) == 30

    def test_get_data_trend_with_custom_days(self, test_client):
        """测试使用自定义天数获取数据趋势"""
        response = test_client.get(
            "/api/v1/admin/data-center/data-trend",
            params={"days": 7}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        trend_data = data["data"]
        trends = trend_data["trends"]

        # 应该是7天的数据
        assert len(trends) == 7

    def test_get_data_trend_date_range(self, test_client):
        """测试数据趋势的日期范围"""
        response = test_client.get(
            "/api/v1/admin/data-center/data-trend",
            params={"days": 10}
        )

        assert response.status_code == 200
        data = response.json()

        trend_data = data["data"]
        summary = trend_data["summary"]

        # 验证开始日期和结束日期
        start_date_text = summary["startDate"].replace('Z', '+00:00')
        end_date_text = summary["endDate"].replace('Z', '+00:00')
        start_date = datetime.fromisoformat(start_date_text).date()
        end_date = datetime.fromisoformat(end_date_text).date()

        # 计算日期差
        date_diff = (end_date - start_date).days
        assert date_diff == 9  # 10天包含开始和结束，所以差值是9

    def test_get_data_trend_data_consistency(self, test_client):
        """测试数据趋势的数据一致性"""
        response = test_client.get(
            "/api/v1/admin/data-center/data-trend",
            params={"days": 5}
        )

        assert response.status_code == 200
        data = response.json()

        trend_data = data["data"]
        trends = trend_data["trends"]

        # 验证数据增长趋势
        previous_matches = None
        for trend in trends:
            current_matches = trend["matches"]
            if previous_matches is not None:
                # 验证数据在增长（根据模拟逻辑）
                assert current_matches >= previous_matches - 10  # 允许小幅波动
            previous_matches = current_matches

    def test_get_data_sources_success(self, test_client, mock_db):
        """测试获取数据源列表成功"""
        # 模拟查询结果
        mock_source = Mock(spec=DataSource)
        mock_source.id = 1
        mock_source.name = "测试数据源"
        mock_source.status = True
        mock_source.source_type = "api"
        mock_source.created_at = datetime.utcnow()
        mock_source.updated_at = datetime.utcnow()
        mock_source.to_dict = Mock(return_value={
            "id": mock_source.id,
            "name": mock_source.name,
            "status": mock_source.status,
            "source_type": mock_source.source_type,
            "created_at": mock_source.created_at.isoformat(),
            "updated_at": mock_source.updated_at.isoformat()
        })

        mock_query_result = Mock()
        mock_query_result.count.return_value = 1
        mock_query_result.offset.return_value = mock_query_result
        mock_query_result.limit.return_value = [mock_source]
        mock_query_result.all.return_value = [mock_source]
        mock_query_result.filter.return_value = mock_query_result

        mock_db.query.return_value = mock_query_result

        response = test_client.get("/api/v1/admin/data-center/data-sources")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "数据源列表获取成功"
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1

    def test_get_data_sources_with_filters(
        self, test_client, mock_db, mock_query_result
    ):
        """测试带筛选条件的数据源列表获取"""

        mock_db.query.return_value = mock_query_result

        response = test_client.get(
            "/api/v1/admin/data-center/data-sources",
            params={
                "page": 1,
                "size": 10,
                "status": "true",
                "source_type": "api"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 验证筛选条件被应用
        mock_query_result.filter.assert_called()

    def test_get_detail_data_success(self, test_client, mock_db):
        """测试获取详细数据成功"""
        # 模拟详细数据
        detail_data = {
            "matches": [
                {
                    "id": 1,
                    "home_team": "Team A",
                    "away_team": "Team B",
                    "status": "upcoming"
                }
            ],
            "odds": [
                {"id": 1, "match_id": 1, "company": "Bet365", "home_odds": 1.8}
            ],
            "sp_records": [
                {"id": 1, "match_id": 1, "sp_value": 2.5}
            ],
            "summary": {
                "total_matches": 1,
                "total_odds": 1,
                "total_sp": 1,
                "last_update": datetime.utcnow().isoformat()
            }
        }

        # 模拟查询
        mock_db.query.return_value.limit.return_value.all.side_effect = [
            detail_data["matches"],  # matches
            detail_data["odds"],  # odds
            detail_data["sp_records"]  # sp_records
        ]

        response = test_client.get("/api/v1/admin/data-center/detail-data")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "详细数据获取成功"
        assert "data" in data
        assert "matches" in data["data"]
        assert "odds" in data["data"]
        assert "sp_records" in data["data"]
        assert "summary" in data["data"]

    def test_export_data_success(self, test_client, mock_db):
        """测试导出数据成功"""
        response = test_client.get(
            "/api/v1/admin/data-center/export-data",
            params={"format": "json"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "数据导出成功"
        assert "data" in data
        assert "downloadUrl" in data["data"]

        # 验证下载URL格式
        download_url = data["data"]["downloadUrl"]
        assert download_url.startswith("/api/v1/admin/data-center/download/")
        assert "json" in download_url.lower()

    def test_export_data_with_csv_format(self, test_client, mock_db):
        """测试以CSV格式导出数据"""
        response = test_client.get(
            "/api/v1/admin/data-center/export-data",
            params={"format": "csv"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        download_url = data["data"]["downloadUrl"]
        assert "csv" in download_url.lower()

    def test_export_data_with_invalid_format(self, test_client):
        """测试使用无效格式导出数据"""
        response = test_client.get(
            "/api/v1/admin/data-center/export-data",
            params={"format": "invalid"}
        )

        # 应该返回200，但格式可能被忽略或使用默认值
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_overview_data_consistency(self, test_client, mock_db):
        """测试总览数据的一致性"""
        # 设置模拟返回值
        mock_db.query.return_value.count.side_effect = [100, 200, 300, 50]

        response = test_client.get("/api/v1/admin/data-center/overview")

        assert response.status_code == 200
        data = response.json()
        overview_data = data["data"]

        # 验证数据一致性
        assert overview_data["totalMatches"] == 100
        assert overview_data["totalOdds"] == 200
        assert overview_data["totalSPRecords"] == 300
        assert overview_data["activeSources"] == 50

    def test_data_trend_date_format(self, test_client):
        """测试数据趋势的日期格式"""
        response = test_client.get(
            "/api/v1/admin/data-center/data-trend",
            params={"days": 3}
        )

        assert response.status_code == 200
        data = response.json()

        trends = data["data"]["trends"]
        for trend in trends:
            date_str = trend["date"]
            # 验证日期是ISO格式
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"无效的日期格式: {date_str}")

    def test_error_handling(self, test_client, mock_db):
        """测试错误处理"""
        # 模拟数据库异常
        mock_db.query.side_effect = Exception("数据库连接失败")

        response = test_client.get("/api/v1/admin/data-center/overview")

        # 应该返回500错误
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "数据库连接失败" in data["detail"]
