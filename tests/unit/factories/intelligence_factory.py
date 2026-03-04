"""
情报测试数据工厂
用于生成单元测试和集成测试的模拟数据
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import random
from unittest.mock import Mock

from backend.models.intelligence import (
    Intelligence, IntelligenceType, IntelligenceSource, IntelligenceRelation, IntelligenceAnalytics,
    ConfidenceLevelEnum, ImportanceLevelEnum, IntelligenceTypeEnum, IntelligenceSourceEnum
)
from backend.models.match import Match
from backend.models.team import Team
from backend.models.player import Player


class IntelligenceFactory:
    """情报数据工厂类"""
    
    @staticmethod
    def create_intelligence_type(
        name: str = "测试情报类型",
        code: str = "test_type",
        category: str = "match",
        default_weight: float = 0.5,
        default_confidence: str = "medium",
        is_system: bool = False
    ) -> IntelligenceType:
        """创建情报类型模拟数据"""
        intel_type = IntelligenceType()
        intel_type.id = random.randint(1, 1000)
        intel_type.name = name
        intel_type.code = code
        intel_type.category = category
        intel_type.default_weight = default_weight
        intel_type.default_confidence = ConfidenceLevelEnum(default_confidence)
        intel_type.is_system = is_system
        intel_type.is_active = True
        intel_type.display_order = 0
        intel_type.icon = "test-icon"
        intel_type.color = "#FF0000"
        intel_type.description = f"测试情报类型: {name}"
        
        return intel_type
    
    @staticmethod
    def create_intelligence_source(
        name: str = "测试信息来源",
        code: str = "test_source",
        source_type: str = "official",
        reliability_score: float = 0.8,
        is_verified: bool = True,
        is_official: bool = False
    ) -> IntelligenceSource:
        """创建信息来源模拟数据"""
        source = IntelligenceSource()
        source.id = random.randint(1, 1000)
        source.name = name
        source.code = code
        source.source_type = source_type
        source.reliability_score = reliability_score
        source.is_verified = is_verified
        source.is_official = is_official
        source.is_active = True
        source.url = "https://example.com"
        source.logo_url = "https://example.com/logo.png"
        source.description = f"测试信息来源: {name}"
        source.total_items = 100
        source.success_rate = 0.85
        source.update_frequency = "hourly"
        source.last_crawled_at = datetime.utcnow()
        source.config = {}
        
        return source
    
    @staticmethod
    def create_match(
        match_id: int = None,
        league_id: int = 1,
        home_team_id: int = 1,
        away_team_id: int = 2
    ) -> Match:
        """创建比赛模拟数据"""
        match = Match()
        match.id = match_id or random.randint(1, 1000)
        match.league_id = league_id
        match.home_team_id = home_team_id
        match.away_team_id = away_team_id
        match.match_time = datetime.utcnow() + timedelta(days=1)
        match.status = "scheduled"
        match.created_at = datetime.utcnow()
        match.updated_at = datetime.utcnow()
        
        return match
    
    @staticmethod
    def create_team(team_id: int = None, name: str = "测试球队") -> Team:
        """创建球队模拟数据"""
        team = Team()
        team.id = team_id or random.randint(1, 1000)
        team.name = name
        team.short_name = name[:3].upper()
        team.country = "测试国家"
        team.logo_url = "https://example.com/logo.png"
        team.created_at = datetime.utcnow()
        team.updated_at = datetime.utcnow()
        
        return team
    
    @staticmethod
    def create_player(player_id: int = None, name: str = "测试球员") -> Player:
        """创建球员模拟数据"""
        player = Player()
        player.id = player_id or random.randint(1, 1000)
        player.name = name
        player.position = "前锋"
        player.jersey_number = 10
        player.team_id = 1
        player.created_at = datetime.utcnow()
        player.updated_at = datetime.utcnow()
        
        return player
    
    @staticmethod
    def create_intelligence(
        intelligence_id: int = None,
        match_id: int = 1,
        type_id: int = 1,
        source_id: int = 1,
        base_weight: float = 0.5,
        confidence: str = "medium",
        importance: str = "medium",
        weight_multiplier: float = 1.0,
        published_at: Optional[datetime] = None,
        is_verified: bool = False
    ) -> Intelligence:
        """创建情报模拟数据"""
        intel = Intelligence()
        intel.id = intelligence_id or random.randint(1, 1000)
        intel.match_id = match_id
        intel.type_id = type_id
        intel.source_id = source_id
        intel.base_weight = base_weight
        intel.confidence = ConfidenceLevelEnum(confidence)
        intel.confidence_score = IntelligenceFactory._confidence_to_score(confidence)
        intel.importance = ImportanceLevelEnum(importance)
        intel.weight_multiplier = weight_multiplier
        intel.calculated_weight = 0.0  # 将由calculate_weight()计算
        
        # 内容信息
        intel.title = f"测试情报标题 {intel.id}"
        intel.content = f"测试情报内容 {intel.id}"
        intel.summary = f"测试情报摘要 {intel.id}"
        intel.keywords = '["测试", "情报"]'
        intel.tags = '["重要", "紧急"]'
        
        # 时间信息
        intel.created_at = datetime.utcnow()
        intel.updated_at = datetime.utcnow()
        intel.published_at = published_at or datetime.utcnow()
        intel.event_time = datetime.utcnow() + timedelta(hours=2)
        intel.expiration_at = datetime.utcnow() + timedelta(days=7)
        
        # 状态信息
        intel.status = "active"
        intel.is_verified = is_verified
        intel.is_duplicate = False
        intel.duplicate_of = None
        
        # 外部数据
        intel.external_id = f"EXT{intel.id}"
        intel.external_url = f"https://example.com/intel/{intel.id}"
        intel.external_data = {}
        intel.odds_data = {"home": 2.5, "draw": 3.0, "away": 2.8}
        intel.stats_data = {"possession": 55, "shots": 12}
        intel.prediction_data = {"home_win_prob": 45, "draw_prob": 30, "away_win_prob": 25}
        intel.attachments = {}
        intel.images = '["image1.jpg", "image2.jpg"]'
        
        # 统计信息
        intel.view_count = random.randint(0, 100)
        intel.like_count = random.randint(0, 50)
        intel.comment_count = random.randint(0, 20)
        intel.share_count = random.randint(0, 10)
        intel.popularity_score = 0.0
        intel.trending_score = 0.0
        
        # 创建关联对象
        intel.type_info = IntelligenceFactory.create_intelligence_type()
        intel.source_info = IntelligenceFactory.create_intelligence_source()
        
        return intel
    
    @staticmethod
    def create_intelligence_relation(
        intelligence_id: int = 1,
        related_intelligence_id: int = 2,
        relation_type: str = "confirms",
        relation_strength: float = 0.8
    ) -> IntelligenceRelation:
        """创建情报关联模拟数据"""
        relation = IntelligenceRelation()
        relation.id = random.randint(1, 1000)
        relation.intelligence_id = intelligence_id
        relation.related_intelligence_id = related_intelligence_id
        relation.relation_type = relation_type
        relation.relation_strength = relation_strength
        relation.description = f"测试关联: {relation_type}"
        relation.created_at = datetime.utcnow()
        relation.created_by = 1
        
        return relation
    
    @staticmethod
    def create_intelligence_analytics(
        date: datetime = None,
        intelligence_type: str = "injury",
        intelligence_source: str = "official"
    ) -> IntelligenceAnalytics:
        """创建情报分析模拟数据"""
        analytics = IntelligenceAnalytics()
        analytics.id = random.randint(1, 1000)
        analytics.date = date or datetime.utcnow().date()
        analytics.hour = 12
        analytics.intelligence_type = intelligence_type
        analytics.intelligence_source = intelligence_source
        analytics.league_id = 1
        
        # 统计指标
        analytics.total_items = random.randint(50, 200)
        analytics.verified_items = random.randint(30, 150)
        analytics.high_importance_items = random.randint(10, 50)
        
        # 时效性指标
        analytics.avg_response_time = random.uniform(0.5, 2.5)
        analytics.items_within_1h = random.randint(10, 40)
        analytics.items_within_24h = random.randint(30, 120)
        
        # 质量指标
        analytics.avg_confidence_score = random.uniform(0.6, 0.9)
        analytics.avg_weight = random.uniform(0.5, 0.8)
        
        # 用户互动指标
        analytics.total_views = random.randint(1000, 5000)
        analytics.total_likes = random.randint(100, 500)
        analytics.total_comments = random.randint(50, 200)
        analytics.total_shares = random.randint(20, 100)
        
        # 热门度指标
        analytics.avg_popularity_score = random.uniform(0.4, 0.7)
        analytics.trending_items = random.randint(5, 25)
        
        analytics.created_at = datetime.utcnow()
        analytics.updated_at = datetime.utcnow()
        
        return analytics
    
    @staticmethod
    def _confidence_to_score(confidence: str) -> float:
        """将置信度枚举转换为数值分数"""
        confidence_scores = {
            "very_low": 0.2,
            "low": 0.4,
            "medium": 0.6,
            "high": 0.8,
            "very_high": 0.9,
            "confirmed": 1.0
        }
        return confidence_scores.get(confidence, 0.6)
    
    @staticmethod
    def create_intelligence_batch(count: int = 10, **kwargs) -> list[Intelligence]:
        """批量创建情报数据"""
        return [IntelligenceFactory.create_intelligence(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_mock_session() -> Mock:
        """创建模拟数据库会话"""
        mock_session = Mock()
        mock_session.query = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.close = Mock()
        return mock_session


def get_test_intelligence_data() -> Dict[str, Any]:
    """获取测试用的情报数据字典"""
    return {
        "intelligence": IntelligenceFactory.create_intelligence(),
        "intelligence_type": IntelligenceFactory.create_intelligence_type(),
        "intelligence_source": IntelligenceFactory.create_intelligence_source(),
        "intelligence_relation": IntelligenceFactory.create_intelligence_relation(),
        "intelligence_analytics": IntelligenceFactory.create_intelligence_analytics(),
        "match": IntelligenceFactory.create_match(),
        "team": IntelligenceFactory.create_team(),
        "player": IntelligenceFactory.create_player(),
    }


# 预定义的测试数据集合
class TestDataSets:
    """预定义的测试数据集"""
    
    @staticmethod
    def basic_intelligence() -> Intelligence:
        """基础情报测试数据"""
        return IntelligenceFactory.create_intelligence(
            base_weight=0.5,
            confidence="medium",
            importance="medium"
        )
    
    @staticmethod
    def high_confidence_intelligence() -> Intelligence:
        """高置信度情报测试数据"""
        return IntelligenceFactory.create_intelligence(
            base_weight=0.7,
            confidence="high",
            importance="high"
        )
    
    @staticmethod
    def low_confidence_intelligence() -> Intelligence:
        """低置信度情报测试数据"""
        return IntelligenceFactory.create_intelligence(
            base_weight=0.3,
            confidence="low",
            importance="low"
        )
    
    @staticmethod
    def expired_intelligence() -> Intelligence:
        """过期情报测试数据"""
        return IntelligenceFactory.create_intelligence(
            published_at=datetime.utcnow() - timedelta(days=2),
            base_weight=0.6,
            confidence="medium",
            importance="medium"
        )
    
    @staticmethod
    def verified_intelligence() -> Intelligence:
        """已验证情报测试数据"""
        return IntelligenceFactory.create_intelligence(
            is_verified=True,
            base_weight=0.8,
            confidence="confirmed",
            importance="critical"
        )