from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

from ..schemas.hedging import ParlayCombination, HedgingResult
from ..crud.hedging import get_default_hedging_config
try:
    from ..models.sp_records import SPRecord  # SP记录模型
    from ..models.match import Match  # 主比赛模型
except ImportError:
    # 如果找不到这些模型，使用模拟数据
    SPRecord = None
    Match = None
    logging.warning("未能导入SPRecord或Match模型，将使用模拟数据")


class HedgingService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.config = get_default_hedging_config(db)
        except Exception:
            # 如果无法获取配置，使用默认值
            class MockConfig:
                min_profit_rate = 0.02
                commission_rate = 0.8
                cost_factor = 0.2
            self.config = MockConfig()

    def calculate_hedging(self, C: float, Sc: float, Se: float) -> dict:
        """
        计算对冲方案关键指标
        :param C: 竞彩卖出金额（通常为1单位便于百分比计算）
        :param Sc: 竞彩组合赔率
        :param Se: 欧指组合赔率
        :return: 包含E(欧指投入)、R(利润)、profit_rate(利润率)的字典
        """
        E = C * (Sc - self.config.cost_factor) / Se
        R = self.config.commission_rate * C - E
        profit_rate = R / C
        
        return {
            "investment": E,
            "revenue": self.config.commission_rate * C,
            "profit": R,
            "profit_rate": profit_rate,
            "is_profitable": profit_rate >= self.config.min_profit_rate
        }

    def find_parlay_combinations(self, target_date: str) -> HedgingResult:
        """
        查找指定日期的二串一组合
        :param target_date: 目标日期，格式为 "YYYY-MM-DD"
        :return: 包含所有符合条件的二串一组合的 HedgingResult
        """
        # 检查是否应该使用模拟数据
        use_mock_data = True  # 可以通过环境变量控制
        
        if use_mock_data:
            return self._generate_mock_data(target_date)
        
        # 获取指定日期的所有比赛
        matches = self._get_matches_for_date(target_date)
        
        # 生成二串一组合
        parlay_combinations = []
        
        for i in range(len(matches)):
            for j in range(i + 1, len(matches)):
                match1 = matches[i]
                match2 = matches[j]
                
                # 检查时间间隔是否超过1小时
                time_diff = abs((match2.start_time - match1.start_time).total_seconds())
                if time_diff < 3600:  # 小于1小时，跳过
                    continue
                
                # 计算组合赔率
                total_sp_odd = match1.sp_value * match2.sp_value
                total_european_odd = match1.european_odd * match2.european_odd
                
                # 计算对冲数据
                hedging_data = self.calculate_hedging(1000, total_sp_odd, total_european_odd)
                
                # 如果不符合利润要求，跳过
                if not hedging_data["is_profitable"]:
                    continue
                
                combination = ParlayCombination(
                    match1_id=match1.id,
                    match1_home_team=match1.home_team,
                    match1_away_team=match1.away_team,
                    match1_start_time=match1.start_time,
                    match1_sp_value=match1.sp_value,
                    match1_european_odd=match1.european_odd,
                    match2_id=match2.id,
                    match2_home_team=match2.home_team,
                    match2_away_team=match2.away_team,
                    match2_start_time=match2.start_time,
                    match2_sp_value=match2.sp_value,
                    match2_european_odd=match2.european_odd,
                    total_sp_odd=total_sp_odd,
                    total_european_odd=total_european_odd,
                    investment_amount=hedging_data["investment"],
                    revenue_amount=hedging_data["revenue"],
                    profit_amount=hedging_data["profit"],
                    profit_rate=hedging_data["profit_rate"],
                    is_profitable=hedging_data["is_profitable"]
                )
                
                parlay_combinations.append(combination)
        
        return HedgingResult(
            date=target_date,
            opportunities=parlay_combinations,
            total_count=len(parlay_combinations)
        )

    def _generate_mock_data(self, target_date: str) -> HedgingResult:
        """
        生成模拟对冲数据
        """
        from datetime import datetime, timedelta
        
        # 解析目标日期
        base_date = datetime.strptime(target_date, "%Y-%m-%d")
        
        # 创建模拟比赛数据
        mock_matches = [
            {
                'id': 1,
                'home_team': '巴塞罗那',
                'away_team': '皇家马德里',
                'start_time': base_date.replace(hour=15, minute=0),
                'sp_value': 3.2,
                'european_odd': 3.8
            },
            {
                'id': 2,
                'home_team': '拜仁慕尼黑',
                'away_team': '多特蒙德',
                'start_time': base_date.replace(hour=17, minute=30),
                'sp_value': 2.8,
                'european_odd': 3.1
            },
            {
                'id': 3,
                'home_team': '曼城',
                'away_team': '切尔西',
                'start_time': base_date.replace(hour=20, minute=0),
                'sp_value': 2.5,
                'european_odd': 2.9
            },
            {
                'id': 4,
                'home_team': '尤文图斯',
                'away_team': 'AC米兰',
                'start_time': base_date.replace(hour=22, minute=45),
                'sp_value': 3.0,
                'european_odd': 3.5
            }
        ]
        
        # 生成模拟的二串一组合
        parlay_combinations = []
        
        for i in range(len(mock_matches)):
            for j in range(i + 1, len(mock_matches)):
                match1 = type('MockMatch1', (), mock_matches[i])()
                match2 = type('MockMatch2', (), mock_matches[j])()
                
                # 检查时间间隔是否超过1小时
                time_diff = abs((match2.start_time - match1.start_time).total_seconds())
                if time_diff < 3600:  # 小于1小时，跳过
                    continue
                
                # 计算组合赔率
                total_sp_odd = match1.sp_value * match2.sp_value
                total_european_odd = match1.european_odd * match2.european_odd
                
                # 计算对冲数据
                hedging_data = self.calculate_hedging(1000, total_sp_odd, total_european_odd)
                
                # 如果不符合利润要求，跳过
                if not hedging_data["is_profitable"]:
                    continue
                
                combination = ParlayCombination(
                    match1_id=match1.id,
                    match1_home_team=match1.home_team,
                    match1_away_team=match1.away_team,
                    match1_start_time=match1.start_time,
                    match1_sp_value=match1.sp_value,
                    match1_european_odd=match1.european_odd,
                    match2_id=match2.id,
                    match2_home_team=match2.home_team,
                    match2_away_team=match2.away_team,
                    match2_start_time=match2.start_time,
                    match2_sp_value=match2.sp_value,
                    match2_european_odd=match2.european_odd,
                    total_sp_odd=total_sp_odd,
                    total_european_odd=total_european_odd,
                    investment_amount=hedging_data["investment"],
                    revenue_amount=hedging_data["revenue"],
                    profit_amount=hedging_data["profit"],
                    profit_rate=hedging_data["profit_rate"],
                    is_profitable=hedging_data["is_profitable"]
                )
                
                parlay_combinations.append(combination)
        
        return HedgingResult(
            date=target_date,
            opportunities=parlay_combinations,
            total_count=len(parlay_combinations)
        )

    def _get_matches_for_date(self, target_date: str) -> List:
        """
        获取指定日期的比赛数据
        这里是一个模拟实现，实际需要根据数据库结构进行调整
        """
        if SPRecord is None:
            # 如果没有SPRecord模型，则返回空列表
            return []
            
        # 将字符串日期转换为datetime范围
        from datetime import datetime, timedelta
        start_datetime = datetime.strptime(target_date, "%Y-%m-%d")
        end_datetime = start_datetime + timedelta(days=1)
        
        # 查询SP记录（需要根据实际数据库结构调整）
        # 这里假设SPRecord包含比赛ID、SP值和时间信息
        try:
            sp_records = self.db.query(SPRecord).filter(
                SPRecord.created_at >= start_datetime,
                SPRecord.created_at < end_datetime
            ).all()
        except Exception:
            # 如果查询失败，返回空列表
            return []
        
        # 这里需要结合Match表获取比赛详细信息
        # 实际实现中需要根据你的数据库结构进行调整
        matches = []
        for record in sp_records:
            # 假设record.match_id可以关联到比赛信息
            # 这里需要根据实际数据库结构进行调整
            match_info = self._get_match_details(record.match_id)
            if match_info:
                # 假设SPRecord同时包含竞彩SP值和欧指数据
                match_obj = type('MatchObj', (), {})()
                match_obj.id = record.match_id
                match_obj.home_team = getattr(match_info, 'home_team', f'HomeTeam_{record.match_id}')
                match_obj.away_team = getattr(match_info, 'away_team', f'AwayTeam_{record.match_id}')
                match_obj.start_time = getattr(match_info, 'start_time', datetime.now())
                match_obj.sp_value = record.sp_value
                match_obj.european_odd = getattr(record, 'european_odd', 2.5)  # 默认欧指
                matches.append(match_obj)
        
        return matches

    def _get_match_details(self, match_id: int):
        """
        获取比赛详情
        这里是一个模拟实现，实际需要根据数据库结构进行调整
        """
        if Match is None:
            # 如果没有Match模型，返回模拟对象
            match_obj = type('MatchDetail', (), {})()
            match_obj.id = match_id
            match_obj.home_team = f"HomeTeam_{match_id}"
            match_obj.away_team = f"AwayTeam_{match_id}"
            match_obj.start_time = datetime.now()
            return match_obj
            
        # 实际实现中需要根据你的数据库结构查询比赛信息
        # 例如，从Match表或其他相关表获取比赛详情
        try:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            return match
        except Exception:
            # 如果查询失败，返回模拟对象
            match_obj = type('MatchDetail', (), {})()
            match_obj.id = match_id
            match_obj.home_team = f"HomeTeam_{match_id}"
            match_obj.away_team = f"AwayTeam_{match_id}"
            match_obj.start_time = datetime.now()
            return match_obj