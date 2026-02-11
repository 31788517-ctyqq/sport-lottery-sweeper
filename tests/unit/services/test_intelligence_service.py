#!/usr/bin/env python3
"""
IntelligenceService单元测试
测试IntelligenceService的关键方法
"""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.intelligence_service import IntelligenceService
from backend.models.intelligence import Intelligence, ConfidenceLevelEnum, ImportanceLevelEnum
from backend.models.match import Match
from backend.models.crawler_logs import CrawlerTaskLog
from backend.schemas.crawler import (
    CrawlerIntelligenceStats, CrawlerIntelligenceData, 
    TrendAnalysisData, ErrorDistributionData
)
from tests.unit.factories.intelligence_factory import IntelligenceFactory


class TestIntelligenceService:
    """测试IntelligenceService类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_db = Mock()
        self.service = IntelligenceService(self.mock_db)
        
        # 创建模拟数据
        self.test_intelligence = IntelligenceFactory.create_intelligence()
        self.test_match = IntelligenceFactory.create_match()
        self.test_log = Mock(spec=CrawlerTaskLog)
        self.test_log.id = 1
        self.test_log.started_at = datetime.utcnow() - timedelta(hours=1)
        self.test_log.status = "failed"
        self.test_log.error_message = "网络连接超时"
        
        # 设置默认mock行为
        self.mock_db.query.return_value = Mock()
    
    def test_get_stats_basic(self):
        """测试获取基础统计数据"""
        # 模拟查询结果
        mock_query = Mock()
        mock_count = Mock()
        mock_count.count.return_value = 100
        mock_query.count.return_value = 100
        
        # 模拟今日统计查询
        mock_today_stats = Mock()
        mock_today_stats.total = 20
        mock_today_stats.success = 15
        
        # 模拟成功情报查询
        mock_success_query = Mock()
        mock_success_query.count.return_value = 80
        
        # 模拟数据源查询
        mock_source_query = Mock()
        mock_source_query.distinct.return_value = Mock()
        mock_source_query.distinct.return_value.count.return_value = 5
        
        # 设置mock链
        self.mock_db.query.side_effect = [
            mock_query,  # total_count查询
            Mock(),      # today_stats查询（需要进一步配置）
            mock_success_query,  # successful_intelligence查询
            mock_source_query    # active_sources查询
        ]
        
        # 配置today_stats查询
        today_query_mock = Mock()
        today_filter_mock = Mock()
        today_first_mock = Mock()
        today_first_mock.first.return_value = mock_today_stats
        today_filter_mock.filter.return_value = today_first_mock
        today_query_mock.filter.return_value = today_filter_mock
        
        # 替换第二次查询的返回值
        self.mock_db.query.side_effect = [
            mock_query,
            today_query_mock,
            mock_success_query,
            mock_source_query
        ]
        
        # 调用方法
        result = self.service.get_stats()
        
        # 验证结果类型
        assert isinstance(result, CrawlerIntelligenceStats)
        
        # 验证调用次数
        assert self.mock_db.query.call_count >= 4
        
        # 验证基本字段
        assert result.total_crawled == 100
        assert result.today_crawled == 20
        assert result.today_success == 15
        assert result.today_failed == 5
        assert result.active_sources == 5
    
    def test_get_stats_empty_data(self):
        """测试空数据情况下的统计"""
        # 模拟空查询结果
        mock_query = Mock()
        mock_query.count.return_value = 0
        
        # 模拟今日统计查询
        mock_today_stats = Mock()
        mock_today_stats.total = 0
        mock_today_stats.success = 0
        
        # 设置mock链
        today_query_mock = Mock()
        today_filter_mock = Mock()
        today_first_mock = Mock()
        today_first_mock.first.return_value = mock_today_stats
        today_filter_mock.filter.return_value = today_first_mock
        today_query_mock.filter.return_value = today_filter_mock
        
        self.mock_db.query.side_effect = [
            mock_query,
            today_query_mock,
            mock_query,  # successful_intelligence查询
            Mock()       # active_sources查询
        ]
        
        result = self.service.get_stats()
        
        assert result.total_crawled == 0
        assert result.today_crawled == 0
        assert result.today_success == 0
        assert result.today_failed == 0
        assert result.overall_success_rate == 0.0
    
    def test_get_real_error_distribution(self):
        """测试获取真实错误分布"""
        # 模拟失败日志查询
        mock_log_query = Mock()
        mock_filter = Mock()
        mock_all = Mock()
        mock_all.all.return_value = [self.test_log]
        
        mock_filter.filter.return_value = mock_all
        mock_log_query.filter.return_value = mock_filter
        
        self.mock_db.query.return_value = mock_log_query
        
        # 调用方法
        result = self.service._get_real_error_distribution()
        
        # 验证结果
        assert isinstance(result, list)
        if result:  # 如果有分类结果
            assert len(result) > 0
            for item in result:
                assert "name" in item
                assert "value" in item
                assert "color" in item
                assert item["value"] > 0
    
    def test_get_real_error_distribution_empty(self):
        """测试空错误分布"""
        # 模拟空查询结果
        mock_log_query = Mock()
        mock_filter = Mock()
        mock_all = Mock()
        mock_all.all.return_value = []
        
        mock_filter.filter.return_value = mock_all
        mock_log_query.filter.return_value = mock_filter
        
        self.mock_db.query.return_value = mock_log_query
        
        result = self.service._get_real_error_distribution()
        
        assert result == []
    
    def test_get_intelligence_data_basic(self):
        """测试获取情报数据列表"""
        # 模拟查询结果
        mock_query = Mock()
        mock_join = Mock()
        mock_filter = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        
        # 创建模拟情报列表
        mock_intelligence_list = [self.test_intelligence, self.test_intelligence]
        
        # 设置mock链
        mock_limit.all.return_value = mock_intelligence_list
        mock_offset.limit.return_value = mock_limit
        mock_filter.offset.return_value = mock_offset
        mock_query.filter.return_value = mock_filter
        mock_join.filter.return_value = mock_query
        self.mock_db.query.return_value.join.return_value = mock_join
        
        # 调用方法
        result = self.service.get_intelligence_data(
            source_id=1,
            category="match",
            status="new",
            page=1,
            page_size=20
        )
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert isinstance(item, CrawlerIntelligenceData)
            assert item.id == self.test_intelligence.id
            assert item.category in ["match", "general"]  # 可能被转换
    
    def test_get_intelligence_data_with_filters(self):
        """测试带筛选条件的情报数据获取"""
        # 测试各种筛选条件组合
        test_cases = [
            {"source_id": 1, "category": "match", "status": "new"},
            {"source_id": None, "category": "player", "status": "processed"},
            {"source_id": 2, "category": None, "status": None},
        ]
        
        for filters in test_cases:
            # 重置mock
            self.mock_db.reset_mock()
            
            # 模拟查询结果
            mock_all = Mock()
            mock_all.all.return_value = []
            self.mock_db.query.return_value.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
            
            # 调用方法
            result = self.service.get_intelligence_data(
                source_id=filters["source_id"],
                category=filters["category"],
                status=filters["status"],
                page=1,
                page_size=10
            )
            
            assert isinstance(result, list)
    
    def test_get_trend_analysis(self):
        """测试趋势分析"""
        # 调用方法
        result = self.service.get_trend_analysis(days=7)
        
        # 验证结果类型
        assert isinstance(result, TrendAnalysisData)
        
        # 验证数据结构
        assert hasattr(result, "dates")
        assert hasattr(result, "crawl_counts")
        assert hasattr(result, "success_counts")
        assert hasattr(result, "error_counts")
        
        # 验证数组长度一致
        assert len(result.dates) == 7
        assert len(result.crawl_counts) == 7
        assert len(result.success_counts) == 7
        assert len(result.error_counts) == 7
        
        # 验证数据合理性
        for i in range(7):
            assert result.crawl_counts[i] >= 0
            assert result.success_counts[i] >= 0
            assert result.error_counts[i] >= 0
            # 成功数+错误数应等于抓取数
            assert result.success_counts[i] + result.error_counts[i] == result.crawl_counts[i]
    
    def test_mark_as_invalid_success(self):
        """测试成功标记情报为无效"""
        # 模拟查询结果
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        # 创建模拟情报对象
        mock_intelligence = Mock(spec=Intelligence)
        mock_intelligence.id = 1
        mock_intelligence.weight = 0.5
        
        mock_first.first.return_value = mock_intelligence
        mock_filter.filter.return_value = mock_first
        mock_query.filter.return_value = mock_filter
        
        self.mock_db.query.return_value = mock_query
        
        # 调用方法
        result = self.service.mark_as_invalid(1, 100)
        
        # 验证结果
        assert result is True
        
        # 验证权重被设置为0
        assert mock_intelligence.weight == 0.0
        
        # 验证更新时间被设置
        assert mock_intelligence.updated_at is not None
        
        # 验证提交被调用
        self.mock_db.commit.assert_called_once()
    
    def test_mark_as_invalid_not_found(self):
        """测试标记不存在的情报为无效"""
        # 模拟查询返回None
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        mock_first.first.return_value = None
        mock_filter.filter.return_value = mock_first
        mock_query.filter.return_value = mock_filter
        
        self.mock_db.query.return_value = mock_query
        
        # 调用方法
        result = self.service.mark_as_invalid(999, 100)
        
        # 验证结果
        assert result is False
        
        # 验证没有提交
        self.mock_db.commit.assert_not_called()
    
    def test_recrawl_data_success(self):
        """测试成功重新抓取数据"""
        # 模拟查询结果
        mock_intelligence = Mock(spec=Intelligence)
        mock_intelligence.id = 1
        mock_intelligence.content = "原始内容"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_intelligence
        
        # 使用patch模拟随机选择和睡眠
        with patch('random.choice', return_value=True):
            with patch('time.sleep'):
                with patch('time.time', side_effect=[0.0, 0.5]):
                    # 调用方法
                    result = self.service.recrawl_data(1, 100)
        
        # 验证结果
        assert result["intelligence_id"] == 1
        assert result["status"] == "success"
        assert result["success"] is True
        assert "execution_time" in result
        assert result["new_content"] is not None
        
        # 验证内容已更新
        assert mock_intelligence.content != "原始内容"
        
        # 验证权重已重置
        assert 0.5 <= mock_intelligence.weight <= 1.0
        
        # 验证提交被调用
        self.mock_db.commit.assert_called_once()
    
    def test_recrawl_data_not_found(self):
        """测试重新抓取不存在的情报"""
        # 模拟查询返回None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # 验证抛出异常
        with pytest.raises(ValueError, match="情报不存在"):
            self.service.recrawl_data(999, 100)
    
    def test_batch_mark_data_invalid(self):
        """测试批量标记为无效"""
        # 模拟更新操作
        mock_update = Mock()
        mock_update.update.return_value = 3  # 模拟更新了3条记录
        
        self.mock_db.query.return_value.filter.return_value.update.return_value = mock_update
        
        # 调用方法
        result = self.service.batch_mark_data([1, 2, 3], "invalid", 100)
        
        # 验证结果
        assert result == 3
        
        # 验证更新参数
        update_call = self.mock_db.query.return_value.filter.return_value.update.call_args
        update_kwargs = update_call[1]
        assert update_kwargs["synchronize_session"] == False
        assert Intelligence.weight in update_kwargs
        assert Intelligence.updated_at in update_kwargs
    
    def test_batch_mark_data_active(self):
        """测试批量标记为有效"""
        # 模拟更新操作
        mock_update = Mock()
        mock_update.update.return_value = 2
        
        self.mock_db.query.return_value.filter.return_value.update.return_value = mock_update
        
        # 调用方法
        result = self.service.batch_mark_data([4, 5], "active", 100)
        
        assert result == 2
    
    def test_batch_mark_data_invalid_status(self):
        """测试无效状态参数"""
        # 调用方法
        result = self.service.batch_mark_data([1, 2, 3], "unknown_status", 100)
        
        assert result == 0
    
    def test_export_data_csv(self):
        """测试导出CSV数据"""
        # 模拟查询结果
        mock_intelligence_list = [self.test_intelligence]
        
        self.mock_db.query.return_value.all.return_value = mock_intelligence_list
        
        # 调用方法
        result = self.service.export_data(format="csv")
        
        # 验证结果
        assert result["format"] == "csv"
        assert "data" in result
        assert "filename" in result
        assert "size" in result
        
        # 验证CSV数据包含预期字段
        csv_data = result["data"]
        assert "ID" in csv_data
        assert "比赛ID" in csv_data
        assert "分类" in csv_data
        assert "来源" in csv_data
    
    def test_export_data_json(self):
        """测试导出JSON数据"""
        # 模拟查询结果
        mock_intelligence_list = [self.test_intelligence]
        
        self.mock_db.query.return_value.all.return_value = mock_intelligence_list
        
        # 调用方法
        result = self.service.export_data(format="json")
        
        # 验证结果
        assert result["format"] == "json"
        assert "data" in result
        assert isinstance(result["data"], list)
        assert "count" in result
        assert result["count"] == 1
        
        # 验证JSON结构
        json_item = result["data"][0]
        assert "id" in json_item
        assert "match_id" in json_item
        assert "category" in json_item
        assert "content" in json_item
    
    def test_export_data_invalid_format(self):
        """测试无效导出格式"""
        with pytest.raises(ValueError, match="不支持的导出格式"):
            self.service.export_data(format="xml")
    
    def test_get_error_distribution(self):
        """测试获取错误分布"""
        # 调用方法
        result = self.service.get_error_distribution()
        
        # 验证结果类型
        assert isinstance(result, ErrorDistributionData)
        
        # 验证数据结构
        assert hasattr(result, "error_types")
        assert hasattr(result, "error_counts")
        assert hasattr(result, "percentages")
        
        # 验证数组长度一致
        assert len(result.error_types) == len(result.error_counts)
        assert len(result.error_counts) == len(result.percentages)
        
        # 验证百分比计算
        total = sum(result.error_counts)
        if total > 0:
            for i, count in enumerate(result.error_counts):
                expected_percent = round(count / total * 100, 1)
                assert result.percentages[i] == expected_percent
    
    def test_analyze_intelligence_quality(self):
        """测试情报质量分析"""
        # 模拟查询结果
        mock_intelligence_list = [
            IntelligenceFactory.create_intelligence(base_weight=0.8, is_verified=True),
            IntelligenceFactory.create_intelligence(base_weight=0.6, is_verified=False),
            IntelligenceFactory.create_intelligence(base_weight=0.4, is_verified=True)
        ]
        
        for intel in mock_intelligence_list:
            intel.content = "测试内容"  # 确保有内容
            intel.is_new = random.choice([True, False])
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_intelligence_list
        
        # 调用方法
        result = self.service.analyze_intelligence_quality(days=7)
        
        # 验证结果结构
        assert "period_days" in result
        assert result["period_days"] == 7
        
        assert "total_count" in result
        assert result["total_count"] == 3
        
        assert "quality_metrics" in result
        metrics = result["quality_metrics"]
        assert "completeness_rate" in metrics
        assert "average_weight" in metrics
        assert "freshness_rate" in metrics
        assert "quality_score" in metrics
        
        # 验证质量分数在0-100之间
        assert 0 <= metrics["quality_score"] <= 100
        
        # 验证建议存在
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
    
    def test_analyze_intelligence_quality_empty(self):
        """测试空数据的情报质量分析"""
        # 模拟空查询结果
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # 调用方法
        result = self.service.analyze_intelligence_quality(days=7)
        
        # 验证空结果结构
        assert result["total_count"] == 0
        assert result["quality_metrics"] == {}
    
    def test_generate_quality_recommendations(self):
        """测试生成质量改进建议"""
        # 测试各种质量水平
        test_cases = [
            (75.0, 0.55, 65.0),  # 所有指标都较低
            (85.0, 0.65, 75.0),  # 中等水平
            (95.0, 0.85, 90.0),  # 高水平
            (100.0, 1.0, 100.0),  # 完美水平
        ]
        
        for completeness, avg_weight, freshness in test_cases:
            recommendations = self.service._generate_quality_recommendations(
                completeness, avg_weight, freshness
            )
            
            assert isinstance(recommendations, list)
            
            # 根据质量水平验证建议内容
            if completeness < 80:
                assert any("完整性" in rec for rec in recommendations)
            if avg_weight < 0.6:
                assert any("质量权重" in rec or "数据源筛选" in rec for rec in recommendations)
            if freshness < 70:
                assert any("采集频率" in rec or "及时性" in rec for rec in recommendations)
            if completeness >= 80 and avg_weight >= 0.6 and freshness >= 70:
                assert any("质量良好" in rec for rec in recommendations)


if __name__ == "__main__":
    # 直接运行测试
    import sys
    sys.exit(pytest.main([__file__, "-v"]))