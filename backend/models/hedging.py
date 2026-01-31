from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class HedgingOpportunity(Base):
    """对冲机会模型"""
    __tablename__ = "hedging_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    match_combination_id = Column(String, nullable=False)  # 比赛组合ID，如 "match1-match2"
    date = Column(DateTime, default=datetime.utcnow)
    
    # 第一场比赛信息
    match1_id = Column(Integer, nullable=False)
    match1_home_team = Column(String, nullable=False)
    match1_away_team = Column(String, nullable=False)
    match1_start_time = Column(DateTime, nullable=False)
    match1_sp_value = Column(Float, nullable=False)  # 竞彩SP值
    match1_european_odd = Column(Float, nullable=False)  # 欧指赔率
    
    # 第二场比赛信息
    match2_id = Column(Integer, nullable=False)
    match2_home_team = Column(String, nullable=False)
    match2_away_team = Column(String, nullable=False)
    match2_start_time = Column(DateTime, nullable=False)
    match2_sp_value = Column(Float, nullable=False)  # 竞彩SP值
    match2_european_odd = Column(Float, nullable=False)  # 欧指赔率
    
    # 对冲计算结果
    total_sp_odd = Column(Float, nullable=False)  # 竞彩组合赔率
    total_european_odd = Column(Float, nullable=False)  # 欧指组合赔率
    investment_amount = Column(Float, nullable=False)  # 欧指平台投入金额
    revenue_amount = Column(Float, nullable=False)  # 竞彩佣金收入
    profit_amount = Column(Float, nullable=False)  # 净收益
    profit_rate = Column(Float, nullable=False)  # 利润率
    is_profitable = Column(Boolean, default=False)  # 是否符合利润要求 (>2%)


class HedgingConfig(Base):
    """对冲配置模型"""
    __tablename__ = "hedging_configs"

    id = Column(Integer, primary_key=True, index=True)
    min_profit_rate = Column(Float, default=0.02)  # 最低利润率要求 (2%)
    commission_rate = Column(Float, default=0.8)  # 佣金率
    cost_factor = Column(Float, default=0.2)  # 成本因子
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)