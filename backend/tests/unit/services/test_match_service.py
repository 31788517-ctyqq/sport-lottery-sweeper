#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-29 - 创建MatchService单元测试
"""
MatchService单元测试模块
测试比赛服务的核心业务逻辑
"""
import pytest
from datetime import date, time, timedelta
from unittest.mock import Mock
from sqlalchemy.orm import Session

# 导入服务和模型
try:
    from backend.services.match_service import MatchService
    from backend.models.match import (
        Match,
        Team,
        League,
        MatchStatusEnum,
        MatchTypeEnum,
        MatchImportanceEnum,
    )
    from core.exceptions import ValidationException, NotFoundException
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    sys.path.append('.')
    from backend.services.match_service import MatchService
    from backend.models.match import (
        Match,
        Team,
        League,
        MatchStatusEnum,
        MatchTypeEnum,
        MatchImportanceEnum,
    )
    from core.exceptions import ValidationException, NotFoundException


class TestMatchService:

    """MatchService测试类"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def match_service(self, mock_db):
        """创建比赛服务实例"""
        return MatchService(mock_db)

    @pytest.fixture
    def sample_team(self):
        """创建示例球队"""
        team = Team()
        team.id = 1
        team.name = "Test Team"
        team.code = "TST"
        team.country = "Test Country"
        team.country_code = "TC"
        return team

    @pytest.fixture
    def sample_league(self):
        """创建示例联赛"""
        league = League()
        league.id = 1
        league.name = "Test League"
        league.code = "TSTL"
        league.country = "Test Country"
        league.country_code = "TC"
        league.level = 1
        league.type = "national"
        return league

    @pytest.fixture
    def sample_match(self):
        """创建示例比赛"""
        match = Match()
        match.id = 1
        match.home_team_id = 1
        match.away_team_id = 2
        match.league_id = 1
        match.match_date = date.today() + timedelta(days=7)
        match.match_time = time(20, 0)
        match.status = MatchStatusEnum.SCHEDULED
        match.match_type = MatchTypeEnum.LEAGUE
        match.importance_level = MatchImportanceEnum.MEDIUM
        match.is_live = False
        return match

    def test_init(self, mock_db):
        """测试服务初始化"""
        service = MatchService(mock_db)
        assert service.db == mock_db

    def test_create_match_success(
        self, match_service, mock_db, sample_team, sample_league
    ):
        """测试成功创建比赛"""

        # 模拟查询结果
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_team,  # home_team
            sample_team,  # away_team (使用同一球队简化)
            sample_league  # league
        ]

        # 模拟保存比赛
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # 准备比赛数据
        match_data = {
            'home_team_id': 1,
            'away_team_id': 1,
            'league_id': 1,
            'match_date': date.today() + timedelta(days=7),
            'match_time': time(20, 0),
            'venue': 'Test Stadium',
            'round_number': 10,
            'season': '2023-2024'
        }

        # 执行创建
        result = match_service.create_match(match_data)

        # 验证结果
        assert isinstance(result, Match)
        assert result.home_team_id == 1
        assert result.away_team_id == 1
        assert result.league_id == 1
        assert result.status == MatchStatusEnum.SCHEDULED

        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_create_match_missing_required_fields(self, match_service):
        """测试创建比赛 - 缺少必需字段"""
        match_data = {
            'home_team_id': 1,
            # 缺少 away_team_id, league_id, match_date
        }

        with pytest.raises(ValidationException, match='缺少必需字段'):
            match_service.create_match(match_data)

    def test_create_match_home_team_not_found(self, match_service, mock_db):
        """测试创建比赛 - 主队不存在"""
        # 模拟查询结果 - 主队不存在
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,  # home_team
            Mock(),  # away_team
            Mock()   # league
        ]

        match_data = {
            'home_team_id': 999,
            'away_team_id': 1,
            'league_id': 1,
            'match_date': date.today() + timedelta(days=7)
        }

        with pytest.raises(NotFoundException, match='主队'):
            match_service.create_match(match_data)

    def test_create_match_past_date(
        self, match_service, mock_db, sample_team, sample_league
    ):
        """测试创建比赛 - 过去日期"""
        # 模拟查询结果
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.side_effect = [
            sample_team, sample_team, sample_league
        ]

        match_data = {
            'home_team_id': 1,
            'away_team_id': 1,
            'league_id': 1,
            'match_date': date.today() - timedelta(days=1)  # 过去日期
        }

        with pytest.raises(
            ValidationException,
            match='比赛日期不能是过去的时间'
        ):
            match_service.create_match(match_data)

    def test_get_match_by_id_success(

        self, match_service, mock_db, sample_match
    ):
        """测试根据ID获取比赛 - 成功"""
        # 模拟查询结果
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = sample_match

        result = match_service.get_match_by_id(1)

        assert result == sample_match

        mock_db.query.assert_called_once()

    def test_get_match_by_id_not_found(self, match_service, mock_db):
        """测试根据ID获取比赛 - 不存在"""
        # 模拟查询结果 - 比赛不存在
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = None

        result = match_service.get_match_by_id(999)

        assert result is None

    def test_update_match_success(self, match_service, mock_db, sample_match):

        """测试更新比赛 - 成功"""
        # 模拟查询结果
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = sample_match

        mock_db.commit = Mock()

        update_data = {
            'venue': 'Updated Stadium',

            'round_number': 11,
            'notes': 'Updated notes'
        }

        result = match_service.update_match(1, update_data)

        assert result == sample_match
        assert sample_match.venue == 'Updated Stadium'
        assert sample_match.round_number == 11
        assert sample_match.notes == 'Updated notes'

        mock_db.commit.assert_called_once()

    def test_update_match_not_found(self, match_service, mock_db):
        """测试更新比赛 - 比赛不存在"""
        # 模拟查询结果 - 比赛不存在
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = None

        with pytest.raises(
            NotFoundException,
            match='比赛'
        ):
            match_service.update_match(999, {'venue': 'Test'})

    def test_update_match_status_success(
        self, match_service, mock_db, sample_match
    ):
        """测试更新比赛状态 - 成功"""
        # 模拟查询结果
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = sample_match

        mock_db.commit = Mock()

        result = match_service.update_match_status(
            1,
            MatchStatusEnum.LIVE
        )

        assert result == sample_match

        assert sample_match.status == MatchStatusEnum.LIVE
        assert sample_match.is_live is True

        mock_db.commit.assert_called_once()

    def test_get_upcoming_matches(self, match_service, mock_db):
        """测试获取即将到来的比赛"""
        # 模拟查询结果
        mock_matches = [Mock(spec=Match), Mock(spec=Match)]
        base_query = mock_db.query.return_value.filter.return_value
        order_query = base_query.order_by.return_value
        order_query.all.return_value = mock_matches

        result = match_service.get_upcoming_matches(days=7)

        assert result == mock_matches
        assert mock_db.query.call_count == 1

    def test_search_matches(self, match_service, mock_db):

        """测试搜索比赛"""
        # 模拟查询结果
        mock_matches = [Mock(spec=Match), Mock(spec=Match)]
        base_query = mock_db.query.return_value.filter.return_value
        order_query = base_query.order_by.return_value
        order_query.all.return_value = mock_matches

        filters = {
            'league_id': 1,
            'status': 'scheduled',
            'start_date': date.today(),

            'end_date': date.today() + timedelta(days=30)
        }

        result = match_service.search_matches(filters)

        assert result == mock_matches
        assert mock_db.query.call_count == 1

    def test_delete_match_success(self, match_service, mock_db, sample_match):
        """测试删除比赛 - 成功"""
        # 模拟查询结果
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = sample_match

        mock_db.delete = Mock()

        mock_db.commit = Mock()

        result = match_service.delete_match(1)

        assert result is True
        mock_db.delete.assert_called_once_with(sample_match)
        mock_db.commit.assert_called_once()

    def test_delete_match_not_found(self, match_service, mock_db):
        """测试删除比赛 - 比赛不存在"""
        # 模拟查询结果 - 比赛不存在
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = None

        result = match_service.delete_match(999)

        assert result is False

    def test_get_match_statistics(self, match_service, mock_db, sample_match):

        """测试获取比赛统计信息"""
        # 模拟查询结果
        first_query = mock_db.query.return_value.filter.return_value
        first_query.first.return_value = sample_match

        # 模拟相关数据查询
        count_query = mock_db.query.return_value.filter.return_value
        count_query.count.return_value = 5

        result = match_service.get_match_statistics(1)

        assert isinstance(result, dict)

        assert 'match' in result
        assert 'odds_count' in result
        assert 'predictions_count' in result
        assert result['match'] == sample_match

    def test_bulk_update_match_status(self, match_service, mock_db):
        """测试批量更新比赛状态"""
        # 模拟查询结果
        mock_matches = [Mock(spec=Match), Mock(spec=Match)]
        filter_query = mock_db.query.return_value.filter.return_value
        filter_query.all.return_value = mock_matches

        mock_db.commit = Mock()

        match_ids = [1, 2]

        new_status = MatchStatusEnum.FINISHED

        result = match_service.bulk_update_match_status(match_ids, new_status)

        assert result == len(match_ids)
        for match in mock_matches:
            assert match.status == new_status

        mock_db.commit.assert_called_once()


if __name__ == '__main__':

    pytest.main([__file__, '-v'])

# AI_DONE: coder1 @2026-01-29
