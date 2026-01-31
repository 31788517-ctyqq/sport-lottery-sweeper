#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-29 - 创建Match相关模型单元测试
"""
Match模型单元测试模块
测试Match、Team、League等模型的核心功能
"""
import pytest
from datetime import datetime, date, time
from sqlalchemy.exc import IntegrityError

# 导入模型
try:
    from backend.models.match import (
        Match, Team, League, 
        MatchStatusEnum, MatchTypeEnum, MatchImportanceEnum
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    sys.path.append('.')
    from backend.models.match import (
        Match, Team, League,
        MatchStatusEnum, MatchTypeEnum, MatchImportanceEnum
    )


class TestMatchEnums:
    """比赛枚举测试类"""
    
    def test_match_status_enum(self):
        """测试比赛状态枚举值"""
        assert MatchStatusEnum.SCHEDULED.value == "scheduled"
        assert MatchStatusEnum.LIVE.value == "live"
        assert MatchStatusEnum.HALFTIME.value == "halftime"
        assert MatchStatusEnum.FINISHED.value == "finished"
        assert MatchStatusEnum.POSTPONED.value == "postponed"
        assert MatchStatusEnum.CANCELLED.value == "cancelled"
        assert MatchStatusEnum.ABANDONED.value == "abandoned"
        assert MatchStatusEnum.SUSPENDED.value == "suspended"
    
    def test_match_type_enum(self):
        """测试比赛类型枚举值"""
        assert MatchTypeEnum.LEAGUE.value == "league"
        assert MatchTypeEnum.CUP.value == "cup"
        assert MatchTypeEnum.FRIENDLY.value == "friendly"
        assert MatchTypeEnum.QUALIFIER.value == "qualifier"
        assert MatchTypeEnum.PLAYOFF.value == "playoff"
        assert MatchTypeEnum.FINAL.value == "final"
    
    def test_match_importance_enum(self):
        """测试比赛重要性枚举值"""
        assert MatchImportanceEnum.LOW.value == "low"
        assert MatchImportanceEnum.MEDIUM.value == "medium"
        assert MatchImportanceEnum.HIGH.value == "high"
        assert MatchImportanceEnum.VERY_HIGH.value == "very_high"


class TestTeamModel:
    """Team模型测试类"""
    
    def test_team_creation(self):
        """测试球队创建"""
        team = Team(
            name="Manchester United",
            code="MUN",
            short_name="Man Utd",
            country="England",
            country_code="ENG",
            founded_year=1878,
            logo_url="logo.png",
            stadium="Old Trafford",
            stadium_capacity=74879
        )
        
        assert team.name == "Manchester United"
        assert team.code == "MUN"
        assert team.short_name == "Man Utd"
        assert team.country == "England"
        assert team.country_code == "ENG"
        assert team.founded_year == 1878
        assert team.logo_url == "logo.png"
        assert team.stadium == "Old Trafford"
        assert team.stadium_capacity == 74879
    
    def test_team_str_representation(self):
        """测试球队字符串表示"""
        team = Team(name="Liverpool", code="LIV")
        assert "Liverpool" in str(team)
        assert "LIV" in str(team)


class TestLeagueModel:
    """League模型测试类"""
    
    def test_league_creation(self):
        """测试联赛创建"""
        league = League(
            name="Premier League",
            code="EPL",
            short_name="PL",
            country="England",
            country_code="ENG",
            level=1,
            type="national",
            format="round_robin",
            current_season="2023-2024",
            season_start=date(2023, 8, 11),
            season_end=date(2024, 5, 19),
            total_teams=20,
            total_matches=380
        )
        
        assert league.name == "Premier League"
        assert league.code == "EPL"
        assert league.short_name == "PL"
        assert league.country == "England"
        assert league.country_code == "ENG"
        assert league.level == 1
        assert league.type == "national"
        assert league.format == "round_robin"
        assert league.current_season == "2023-2024"
        assert league.season_start == date(2023, 8, 11)
        assert league.season_end == date(2024, 5, 19)
        assert league.total_teams == 20
        assert league.total_matches == 380
    
    def test_league_str_representation(self):
        """测试联赛字符串表示"""
        league = League(name="La Liga", code="LL")
        assert "La Liga" in str(league)
        assert "LL" in str(league)


class TestMatchModel:
    """Match模型测试类"""
    
    def test_match_creation(self):
        """测试比赛创建"""
        match = Match(
            home_team_id=1,
            away_team_id=2,
            league_id=3,
            match_date=date(2024, 1, 15),
            match_time=time(20, 0),
            venue="Old Trafford",
            round_number=20,
            match_week=20,
            season="2023-2024",
            status=MatchStatusEnum.SCHEDULED,
            match_type=MatchTypeEnum.LEAGUE,
            importance_level=MatchImportanceEnum.HIGH,
            is_live=False,
            allow_draw_prediction=True,
            bet_closing_time=datetime(2024, 1, 15, 19, 30),
            notes="Important match"
        )
        
        assert match.home_team_id == 1
        assert match.away_team_id == 2
        assert match.league_id == 3
        assert match.match_date == date(2024, 1, 15)
        assert match.match_time == time(20, 0)
        assert match.venue == "Old Trafford"
        assert match.round_number == 20
        assert match.match_week == 20
        assert match.season == "2023-2024"
        assert match.status == MatchStatusEnum.SCHEDULED
        assert match.match_type == MatchTypeEnum.LEAGUE
        assert match.importance_level == MatchImportanceEnum.HIGH
        assert match.is_live is False
        assert match.allow_draw_prediction is True
        assert match.bet_closing_time == datetime(2024, 1, 15, 19, 30)
        assert match.notes == "Important match"
    
    def test_match_status_transitions(self):
        """测试比赛状态转换"""
        match = Match(status=MatchStatusEnum.SCHEDULED)
        
        # 验证状态转换
        match.status = MatchStatusEnum.LIVE
        assert match.status == MatchStatusEnum.LIVE
        
        match.status = MatchStatusEnum.FINISHED
        assert match.status == MatchStatusEnum.FINISHED
    
    def test_match_is_finished_property(self):
        """测试is_finished属性"""
        match = Match()
        
        match.status = MatchStatusEnum.SCHEDULED
        assert match.is_finished is False
        
        match.status = MatchStatusEnum.LIVE
        assert match.is_finished is False
        
        match.status = MatchStatusEnum.FINISHED
        assert match.is_finished is True
        
        match.status = MatchStatusEnum.CANCELLED
        assert match.is_finished is True
        
        match.status = MatchStatusEnum.ABANDONED
        assert match.is_finished is True
    
    def test_match_str_representation(self):
        """测试比赛字符串表示"""
        match = Match(
            home_team_id=1,
            away_team_id=2,
            match_date=date(2024, 1, 15)
        )
        match.id = 100
        
        representation = str(match)
        assert "100" in representation
        assert "2024-01-15" in representation
    
    def test_match_to_dict_method(self):
        """测试to_dict方法"""
        match = Match()
        match.id = 100
        match.home_team_id = 1
        match.away_team_id = 2
        match.league_id = 3
        match.match_date = date(2024, 1, 15)
        match.match_time = time(20, 0)
        match.status = MatchStatusEnum.SCHEDULED
        match.match_type = MatchTypeEnum.LEAGUE
        match.importance_level = MatchImportanceEnum.HIGH
        match.is_live = False
        match.created_at = datetime(2024, 1, 1, 0, 0, 0)
        match.updated_at = datetime(2024, 1, 1, 0, 0, 0)
        
        result = match.to_dict()
        
        assert result['id'] == 100
        assert result['home_team_id'] == 1
        assert result['away_team_id'] == 2
        assert result['league_id'] == 3
        assert result['match_date'] == '2024-01-15'
        assert result['match_time'] == '20:00:00'
        assert result['status'] == 'scheduled'
        assert result['match_type'] == 'league'
        assert result['importance_level'] == 'high'
        assert result['is_live'] is False
        assert result['created_at'] == '2024-01-01T00:00:00'
        assert result['updated_at'] == '2024-01-01T00:00:00'


def test_match_relationships():
    """测试比赛关系"""
    # 创建联赛
    league = League(name="Test League", code="TST", country="Test", country_code="TS")
    
    # 创建球队
    home_team = Team(name="Home Team", code="HT", country="Test", country_code="TS")
    away_team = Team(name="Away Team", code="AT", country="Test", country_code="TS")
    
    # 创建比赛
    match = Match(
        home_team=home_team,
        away_team=away_team,
        league=league,
        match_date=date.today(),
        status=MatchStatusEnum.SCHEDULED
    )
    
    # 验证关系
    assert match.home_team == home_team
    assert match.away_team == away_team
    assert match.league == league
    
    # 验证反向关系（如果定义）
    if hasattr(league, 'matches'):
        # 通常需要通过relationship添加
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# AI_DONE: coder1 @2026-01-29