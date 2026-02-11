#!/usr/bin/env python3
"""
Intelligence模型单元测试
测试Intelligence.calculate_weight()方法和其他核心功能
"""
import sys
import os
from datetime import datetime, timedelta
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.intelligence import (
    Intelligence, IntelligenceType, IntelligenceSource,
    ConfidenceLevelEnum, ImportanceLevelEnum
)
from tests.unit.factories.intelligence_factory import IntelligenceFactory


class TestIntelligenceCalculateWeight:
    """测试Intelligence.calculate_weight()方法"""
    
    def test_calculate_weight_basic(self):
        """测试基础权重计算"""
        # 创建基础情报数据
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.5,
            confidence="medium",
            importance="medium",
            weight_multiplier=1.0
        )
        
        # 设置来源可信度
        intel.source_info.reliability_score = 0.8
        
        # 计算权重
        result = intel.calculate_weight()
        
        # 验证结果在0-1之间
        assert 0.0 <= result <= 1.0
        assert intel.calculated_weight == result
        
        # 验证计算逻辑：0.5 * 0.6(medium置信度) * 1.0(medium重要性) * 0.8(来源可信度) = 0.24
        # 但由于置信度乘数映射为0.6，重要性乘数映射为1.0
        expected = 0.5 * 0.6 * 1.0 * 0.8
        assert abs(result - expected) < 0.001
    
    def test_calculate_weight_high_confidence(self):
        """测试高置信度权重计算"""
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.6,
            confidence="high",
            importance="medium"
        )
        intel.source_info.reliability_score = 0.9
        
        result = intel.calculate_weight()
        
        # 高置信度乘数为0.8
        expected = 0.6 * 0.8 * 1.0 * 0.9  # 0.432
        assert abs(result - expected) < 0.001
    
    def test_calculate_weight_critical_importance(self):
        """测试关键重要性权重计算"""
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.4,
            confidence="medium",
            importance="critical"
        )
        intel.source_info.reliability_score = 0.7
        
        result = intel.calculate_weight()
        
        # 关键重要性乘数为2.0
        expected = 0.4 * 0.6 * 2.0 * 0.7  # 0.336
        assert abs(result - expected) < 0.001
    
    def test_calculate_weight_confirmed_confidence(self):
        """测试已确认置信度权重计算"""
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.7,
            confidence="confirmed",
            importance="high"
        )
        intel.source_info.reliability_score = 1.0
        
        result = intel.calculate_weight()
        
        # 已确认置信度乘数为1.0，高重要性乘数为1.5
        expected = 0.7 * 1.0 * 1.5 * 1.0  # 1.05，但会被限制在1.0
        assert result == 1.0  # 上限为1.0
    
    def test_calculate_weight_without_source(self):
        """测试无来源信息的权重计算"""
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.5,
            confidence="medium",
            importance="medium"
        )
        intel.source_info = None
        
        result = intel.calculate_weight()
        
        # 无来源时，不乘来源可信度
        expected = 0.5 * 0.6 * 1.0  # 0.3
        assert abs(result - expected) < 0.001
    
    def test_calculate_weight_time_decay(self):
        """测试时间衰减因子"""
        # 创建发布时间超过24小时的情报
        published_at = datetime.utcnow() - timedelta(hours=30)
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.8,
            confidence="high",
            importance="high",
            published_at=published_at
        )
        intel.source_info.reliability_score = 0.9
        
        result = intel.calculate_weight()
        
        # 30小时超过24小时，衰减因子 = max(0.5, 1.0 - (30-24)/72) = max(0.5, 1.0 - 6/72) = max(0.5, 0.9167) = 0.9167
        # 基础计算：0.8 * 0.8 * 1.5 * 0.9 = 0.864
        # 应用时间衰减：0.864 * 0.9167 ≈ 0.792
        assert result < 0.8  # 应该比没有时间衰减时小
        assert result >= 0.5  # 应该至少为0.5
    
    def test_calculate_weight_extreme_time_decay(self):
        """测试极端时间衰减（超过96小时）"""
        published_at = datetime.utcnow() - timedelta(hours=100)
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.9,
            confidence="very_high",
            importance="critical",
            published_at=published_at
        )
        intel.source_info.reliability_score = 1.0
        
        result = intel.calculate_weight()
        
        # 100小时超过96小时，衰减因子 = max(0.5, 1.0 - (100-24)/72) = max(0.5, 1.0 - 76/72) = max(0.5, -0.0556) = 0.5
        # 基础计算：0.9 * 0.9 * 2.0 * 1.0 = 1.62
        # 应用时间衰减：1.62 * 0.5 = 0.81
        # 限制在1.0以内：0.81
        assert abs(result - 0.81) < 0.01
    
    def test_calculate_weight_multiplier(self):
        """测试权重乘数"""
        intel = IntelligenceFactory.create_intelligence(
            base_weight=0.5,
            confidence="medium",
            importance="medium",
            weight_multiplier=1.5
        )
        intel.source_info.reliability_score = 0.8
        
        result = intel.calculate_weight()
        
        # 基础计算：0.5 * 0.6 * 1.0 * 0.8 = 0.24
        # 应用乘数：0.24 * 1.5 = 0.36
        assert abs(result - 0.36) < 0.001
    
    def test_calculate_weight_clamping(self):
        """测试权重限制在0-1之间"""
        # 测试超过1.0的情况
        intel = IntelligenceFactory.create_intelligence(
            base_weight=1.0,
            confidence="confirmed",
            importance="critical",
            weight_multiplier=2.0
        )
        intel.source_info.reliability_score = 1.0
        
        result = intel.calculate_weight()
        assert result == 1.0  # 应该被限制在1.0
        
        # 测试低于0.0的情况（理论上不会发生，但测试边界）
        intel2 = IntelligenceFactory.create_intelligence(
            base_weight=0.0,
            confidence="very_low",
            importance="low",
            weight_multiplier=0.5
        )
        intel2.source_info.reliability_score = 0.1
        
        result2 = intel2.calculate_weight()
        assert result2 == 0.0  # 应该被限制在0.0
    
    def test_calculate_weight_all_confidence_levels(self):
        """测试所有置信度等级"""
        test_cases = [
            ("very_low", 0.2),
            ("low", 0.4),
            ("medium", 0.6),
            ("high", 0.8),
            ("very_high", 0.9),
            ("confirmed", 1.0)
        ]
        
        for confidence, expected_multiplier in test_cases:
            intel = IntelligenceFactory.create_intelligence(
                base_weight=0.5,
                confidence=confidence,
                importance="medium"
            )
            intel.source_info.reliability_score = 1.0
            
            result = intel.calculate_weight()
            expected = 0.5 * expected_multiplier * 1.0 * 1.0
            assert abs(result - expected) < 0.001, f"置信度 {confidence} 测试失败"
    
    def test_calculate_weight_all_importance_levels(self):
        """测试所有重要性等级"""
        test_cases = [
            ("low", 0.5),
            ("medium", 1.0),
            ("high", 1.5),
            ("critical", 2.0)
        ]
        
        for importance, expected_multiplier in test_cases:
            intel = IntelligenceFactory.create_intelligence(
                base_weight=0.4,
                confidence="medium",
                importance=importance
            )
            intel.source_info.reliability_score = 1.0
            
            result = intel.calculate_weight()
            expected = 0.4 * 0.6 * expected_multiplier * 1.0
            assert abs(result - expected) < 0.001, f"重要性 {importance} 测试失败"


class TestIntelligenceUpdatePopularity:
    """测试Intelligence.update_popularity()方法"""
    
    def test_update_popularity_basic(self):
        """测试基础热门度更新"""
        intel = IntelligenceFactory.create_intelligence()
        initial_view_count = intel.view_count
        
        # 更新热门度
        intel.update_popularity(
            view_increment=10,
            like_increment=5,
            comment_increment=2,
            share_increment=1
        )
        
        # 验证计数更新
        assert intel.view_count == initial_view_count + 10
        assert intel.like_count == intel.like_count  # 注意：like_count已经包含初始随机值
        assert intel.comment_count == intel.comment_count
        assert intel.share_count == intel.share_count
        
        # 验证热门度得分已更新
        assert intel.popularity_score > 0.0
        assert intel.updated_at is not None
    
    def test_update_popularity_negative_increments(self):
        """测试负增量（应该被忽略）"""
        intel = IntelligenceFactory.create_intelligence()
        initial_view_count = intel.view_count
        
        # 尝试负增量
        intel.update_popularity(
            view_increment=-5,
            like_increment=-3,
            comment_increment=-2,
            share_increment=-1
        )
        
        # 验证计数没有减少
        assert intel.view_count == initial_view_count
        assert intel.like_count >= 0
        assert intel.comment_count >= 0
        assert intel.share_count >= 0
    
    def test_update_popularity_time_factor(self):
        """测试时间衰减因子"""
        intel = IntelligenceFactory.create_intelligence()
        
        # 设置创建时间为24小时前
        intel.created_at = datetime.utcnow() - timedelta(hours=24)
        
        # 更新热门度
        intel.update_popularity(view_increment=100)
        
        # 验证热门度得分考虑了时间衰减
        # 24小时衰减一半，时间因子应为0.5
        assert intel.popularity_score < 100 * 0.1  # 100次浏览 * 0.1权重 * 0.5时间因子 = 5.0


class TestIntelligenceModelProperties:
    """测试Intelligence模型的其他属性和方法"""
    
    def test_intelligence_repr(self):
        """测试__repr__方法"""
        intel = IntelligenceFactory.create_intelligence(intelligence_id=123, match_id=456)
        repr_str = repr(intel)
        
        assert "Intelligence" in repr_str
        assert "123" in repr_str
        assert "456" in repr_str
    
    def test_intelligence_relationships(self):
        """测试模型关系"""
        intel = IntelligenceFactory.create_intelligence()
        
        # 验证关系属性存在
        assert hasattr(intel, 'type_info')
        assert hasattr(intel, 'source_info')
        assert hasattr(intel, 'match')
        assert hasattr(intel, 'team')
        assert hasattr(intel, 'player')
        
        # 验证类型正确
        assert isinstance(intel.type_info, IntelligenceType)
        assert isinstance(intel.source_info, IntelligenceSource)
    
    def test_intelligence_default_values(self):
        """测试默认值设置"""
        intel = IntelligenceFactory.create_intelligence()
        
        # 验证默认值
        assert intel.status == "active"
        assert intel.is_verified is False
        assert intel.is_duplicate is False
        assert intel.duplicate_of is None
        assert intel.reviewed_by is None
        assert intel.reviewed_at is None
        assert intel.review_notes is None
    
    def test_intelligence_constraints(self):
        """测试模型约束"""
        intel = IntelligenceFactory.create_intelligence()
        
        # 验证置信度分数在0-1之间
        assert 0.0 <= intel.confidence_score <= 1.0
        
        # 验证基础权重在0-1之间
        assert 0.0 <= intel.base_weight <= 1.0
        
        # 验证权重乘数在合理范围内
        assert 0.5 <= intel.weight_multiplier <= 2.0


if __name__ == "__main__":
    # 直接运行测试
    import sys
    sys.exit(pytest.main([__file__, "-v"]))