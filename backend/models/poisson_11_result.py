from sqlalchemy import Column, Integer, Float, String, Date, DateTime, JSON
from datetime import datetime
from .base import Base


class Poisson11Result(Base):
    __tablename__ = "poisson_11_results"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(128), nullable=False, index=True, comment="比赛唯一标识")
    match_date = Column(Date, nullable=False, index=True, comment="比赛日期")
    match_time = Column(DateTime(timezone=True), nullable=False, comment="比赛开始时间")
    league = Column(String(100), nullable=True, comment="联赛")
    home_team = Column(String(100), nullable=False, comment="主队")
    away_team = Column(String(100), nullable=False, comment="客队")
    data_source = Column(String(50), nullable=False, index=True, comment="数据源")

    mu_total = Column(Float, nullable=False, comment="总进球均值")
    mu_diff = Column(Float, nullable=False, comment="强弱差均值")
    mu_home = Column(Float, nullable=False, comment="主队均值")
    mu_away = Column(Float, nullable=False, comment="客队均值")
    prob_11 = Column(Float, nullable=False, comment="1-1概率")
    rank = Column(Integer, nullable=True, comment="推荐排名")

    input_payload = Column(JSON, nullable=True, comment="模型输入与中间量")

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
