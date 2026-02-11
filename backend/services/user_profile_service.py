from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.betting_record import BettingRecord
from sqlalchemy.exc import OperationalError
from datetime import datetime


class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
    
    def build_profile(self, user_id: int) -> Dict[str, Any]:
        # 获取用户历史投注记录
        try:
            records = self.db.query(BettingRecord).filter(BettingRecord.user_id == user_id).all()
        except OperationalError:
            # 表不存在或未初始化时，回退为空记录
            records = []
        
        profile = {
            "risk_tolerance": self.calculate_risk_tolerance(records),
            "preferred_teams": self.get_preferred_teams(records),
            "betting_patterns": self.analyze_betting_patterns(records),
            "success_rate": self.calculate_success_rate(records),
            "last_updated": datetime.now().isoformat()
        }
        
        return profile
    
    def calculate_risk_tolerance(self, records: List[BettingRecord]) -> float:
        # 计算用户风险承受能力
        if not records:
            return 0.5  # 默认中等风险承受能力
        
        total_amount = sum(record.amount for record in records)
        high_risk_bets = sum(1 for record in records if record.amount > 100)
        
        if len(records) == 0:
            return 0.5
        
        risk_ratio = high_risk_bets / len(records)
        return min(risk_ratio, 1.0)  # 限制在0-1范围内
    
    def get_preferred_teams(self, records: List[BettingRecord]) -> List[str]:
        # 获取用户偏好的球队
        team_counts = {}
        for record in records:
            if hasattr(record, 'team_name') and record.team_name:
                team_counts[record.team_name] = team_counts.get(record.team_name, 0) + 1
        
        # 按出现次数排序，返回前5个
        sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)
        return [team for team, _ in sorted_teams[:5]]
    
    def analyze_betting_patterns(self, records: List[BettingRecord]) -> Dict[str, Any]:
        # 分析用户投注模式
        if not records:
            return {
                "avg_bet_amount": 0,
                "most_common_bet_type": "unknown",
                "peak_betting_time": "unknown",
                "betting_frequency": "none"
            }
        
        # 计算平均投注金额
        avg_amount = sum(record.amount for record in records) / len(records)
        
        # 找到最常见的投注类型
        bet_types = {}
        for record in records:
            bet_type = getattr(record, 'bet_type', 'unknown')
            bet_types[bet_type] = bet_types.get(bet_type, 0) + 1
        
        most_common_type = max(bet_types, key=bet_types.get) if bet_types else "unknown"
        
        # 分析投注频率
        if len(records) > 30:
            frequency = "high"
        elif len(records) > 10:
            frequency = "medium"
        elif len(records) > 0:
            frequency = "low"
        else:
            frequency = "none"
        
        return {
            "avg_bet_amount": avg_amount,
            "most_common_bet_type": most_common_type,
            "betting_frequency": frequency
        }
    
    def calculate_success_rate(self, records: List[BettingRecord]) -> float:
        # 计算用户投注成功率
        if not records:
            return 0.0
        
        successful_bets = sum(1 for record in records if getattr(record, 'is_winning', False))
        return successful_bets / len(records) if len(records) > 0 else 0.0
