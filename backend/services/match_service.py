#!/usr/bin/env python3
"""
比赛数据处理业务逻辑服务
处理比赛的创建、更新、查询等核心业务
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.database import get_db
from backend.models.match import Match, Team, League, MatchStatusEnum, MatchTypeEnum, MatchImportanceEnum
from backend.models.intelligence import Intelligence, IntelligenceTypeEnum, IntelligenceSourceEnum
from backend.models.odds import Odds, OddsTypeEnum, OddsMovementTypeEnum
from backend.models.predictions import Prediction, PredictionTypeEnum
from backend.core.exceptions import ValidationException, NotFoundException, BusinessException
from backend.core.security import get_password_hash

logger = logging.getLogger(__name__)

class MatchService:
    """比赛服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_match(self, match_data: Dict[str, Any]) -> Match:
        """创建新比赛"""
        try:
            # 验证必需字段
            required_fields = ['home_team_id', 'away_team_id', 'league_id', 'match_date']
            for field in required_fields:
                if field not in match_data or not match_data[field]:
                    raise ValidationException(f"缺少必需字段: {field}")
            
            # 检查队伍是否存在
            home_team = self.db.query(Team).filter(Team.id == match_data['home_team_id']).first()
            if not home_team:
                raise NotFoundException("主队")
            
            away_team = self.db.query(Team).filter(Team.id == match_data['away_team_id']).first()
            if not away_team:
                raise NotFoundException("客队")
            
            # 检查联赛是否存在
            league = self.db.query(League).filter(League.id == match_data['league_id']).first()
            if not league:
                raise NotFoundException("联赛")
            
            # 检查比赛日期是否合理
            match_date = match_data['match_date']
            if isinstance(match_date, str):
                match_date = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
            
            if match_date < datetime.utcnow():
                raise ValidationException("比赛日期不能是过去的时间")
            
            # 创建比赛对象
            match = Match(
                home_team_id=match_data['home_team_id'],
                away_team_id=match_data['away_team_id'],
                league_id=match_data['league_id'],
                match_date=match_date,
                match_time=match_data.get('match_time'),
                venue=match_data.get('venue'),
                round_number=match_data.get('round_number'),
                match_week=match_data.get('match_week'),
                season=match_data.get('season'),
                weather=match_data.get('weather'),
                temperature=match_data.get('temperature'),
                humidity=match_data.get('humidity'),
                status=MatchStatusEnum.SCHEDULED,
                match_type=MatchTypeEnum(match_data.get('match_type', 'regular')),
                importance_level=MatchImportanceEnum(match_data.get('importance_level', 'medium')),
                is_live=match_data.get('is_live', False),
                allow_draw_prediction=match_data.get('allow_draw_prediction', True),
                bet_closing_time=match_data.get('bet_closing_time'),
                notes=match_data.get('notes')
            )
            
            self.db.add(match)
            self.db.commit()
            self.db.refresh(match)
            
            logger.info(f"创建比赛成功: {match.home_team.name} vs {match.away_team.name}")
            return match
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建比赛失败: {e}")
            raise
    
    def update_match(self, match_id: int, match_data: Dict[str, Any]) -> Match:
        """更新比赛信息"""
        try:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise NotFoundException("比赛")
            
            # 更新字段
            updatable_fields = [
                'match_date', 'match_time', 'venue', 'round_number', 'match_week',
                'season', 'weather', 'temperature', 'humidity', 'status',
                'match_type', 'importance_level', 'is_live', 'allow_draw_prediction',
                'bet_closing_time', 'notes'
            ]
            
            for field in updatable_fields:
                if field in match_data:
                    if field == 'match_date' and isinstance(match_data[field], str):
                        match_data[field] = datetime.fromisoformat(match_data[field].replace('Z', '+00:00'))
                    elif field == 'status' and isinstance(match_data[field], str):
                        match_data[field] = MatchStatusEnum(match_data[field])
                    elif field == 'match_type' and isinstance(match_data[field], str):
                        match_data[field] = MatchTypeEnum(match_data[field])
                    elif field == 'importance_level' and isinstance(match_data[field], str):
                        match_data[field] = MatchImportanceEnum(match_data[field])
                    
                    setattr(match, field, match_data[field])
            
            match.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(match)
            
            logger.info(f"更新比赛成功: {match.id}")
            return match
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新比赛失败: {e}")
            raise
    
    def get_match_by_id(self, match_id: int) -> Match:
        """根据ID获取比赛详情"""
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise NotFoundException("比赛")
        return match
    
    def get_matches_by_filters(self, filters: Dict[str, Any]) -> List[Match]:
        """根据条件筛选比赛"""
        query = self.db.query(Match)
        
        # 联赛筛选
        if filters.get('league_id'):
            query = query.filter(Match.league_id == filters['league_id'])
        
        # 状态筛选
        if filters.get('status'):
            if isinstance(filters['status'], str):
                status = MatchStatusEnum(filters['status'])
            else:
                status = filters['status']
            query = query.filter(Match.status == status)
        
        # 日期范围筛选
        if filters.get('date_from'):
            date_from = filters['date_from']
            if isinstance(date_from, str):
                date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Match.match_date >= date_from)
        
        if filters.get('date_to'):
            date_to = filters['date_to']
            if isinstance(date_to, str):
                date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Match.match_date <= date_to)
        
        # 重要性筛选
        if filters.get('importance_level'):
            if isinstance(filters['importance_level'], str):
                importance = MatchImportanceEnum(filters['importance_level'])
            else:
                importance = filters['importance_level']
            query = query.filter(Match.importance_level == importance)
        
        # 直播筛选
        if filters.get('is_live') is not None:
            query = query.filter(Match.is_live == filters['is_live'])
        
        # 允许平局预测筛选
        if filters.get('allow_draw_prediction') is not None:
            query = query.filter(Match.allow_draw_prediction == filters['allow_draw_prediction'])
        
        # 排序
        sort_by = filters.get('sort_by', 'match_date')
        sort_order = filters.get('sort_order', 'asc')
        
        if hasattr(Match, sort_by):
            order_column = getattr(Match, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # 分页
        page = filters.get('page', 1)
        size = filters.get('size', 20)
        offset = (page - 1) * size
        
        matches = query.offset(offset).limit(size).all()
        return matches
    
    def get_upcoming_matches(self, days: int = 7, limit: int = 50) -> List[Match]:
        """获取即将到来的比赛"""
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)
        
        matches = self.db.query(Match).filter(
            and_(
                Match.match_date >= now,
                Match.match_date <= future_date,
                Match.status.in_([MatchStatusEnum.SCHEDULED, MatchStatusEnum.LIVE])
            )
        ).order_by(Match.match_date.asc()).limit(limit).all()
        
        return matches
    
    def get_live_matches(self) -> List[Match]:
        """获取正在进行的比赛"""
        matches = self.db.query(Match).filter(
            Match.status == MatchStatusEnum.LIVE
        ).order_by(Match.match_date.desc()).all()
        
        return matches
    
    def update_match_status(self, match_id: int, status: MatchStatusEnum, 
                          home_score: Optional[int] = None, away_score: Optional[int] = None) -> Match:
        """更新比赛状态"""
        try:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            if not match:
                raise NotFoundException("比赛")
            
            match.status = status
            match.updated_at = datetime.utcnow()
            
            # 如果提供了比分，更新比分
            if home_score is not None:
                match.home_score = home_score
            if away_score is not None:
                match.away_score = away_score
            
            # 如果比赛结束，设置结束时间
            if status in [MatchStatusEnum.FINISHED, MatchStatusEnum.CANCELLED, MatchStatusEnum.POSTPONED]:
                match.actual_end_time = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(match)
            
            logger.info(f"更新比赛状态成功: {match.id} -> {status}")
            return match
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新比赛状态失败: {e}")
            raise
    
    def get_match_statistics(self, match_id: int) -> Dict[str, Any]:
        """获取比赛统计数据"""
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise NotFoundException("比赛")
        
        # 获取相关情报数量
        intelligence_count = self.db.query(Intelligence).filter(
            Intelligence.related_match_id == match_id
        ).count()
        
        # 获取赔率数量
        odds_count = self.db.query(Ords).filter(
            Odds.match_id == match_id
        ).count()
        
        # 获取预测数量
        prediction_count = self.db.query(Prediction).filter(
            Prediction.match_id == match_id
        ).count()
        
        return {
            "match_id": match_id,
            "match_info": {
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "league": match.league.name,
                "match_date": match.match_date,
                "status": match.status.value,
                "final_score": f"{match.home_score}:{match.away_score}" if match.home_score is not None else None
            },
            "statistics": {
                "intelligence_count": intelligence_count,
                "odds_count": odds_count,
                "prediction_count": prediction_count
            }
        }

# 全局服务实例
def get_match_service():
    """获取比赛服务实例"""
    db = next(get_db())
    return MatchService(db)