from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Base = declarative_base()


class Match(Base):
    """比赛数据模型"""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), unique=True, index=True)
    league = Column(String(50))
    home_team = Column(String(100))
    away_team = Column(String(100))
    venue = Column(String(200))
    kickoff_time = Column(DateTime)
    sell_deadline = Column(DateTime)

    # 建立与情报的关联
    intelligence = relationship("Intelligence", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match(match_id='{self.match_id}', league='{self.league}')>"


class Intelligence(Base):
    """情报数据模型"""
    __tablename__ = "intelligence"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), ForeignKey("matches.match_id"))
    summary = Column(String(500))
    content = Column(Text)
    category = Column(String(50))
    source = Column(String(50))
    weight = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    publish_time = Column(DateTime)
    is_new = Column(Boolean, default=False)

    # 建立与比赛的关联
    match = relationship("Match", back_populates="intelligence")

    def __repr__(self):
        return f"<Intelligence(match_id='{self.match_id}', category='{self.category}')>"


class Prediction(Base):
    """预测数据模型"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), ForeignKey("matches.match_id"))
    type = Column(String(50))
    prediction = Column(String(500))
    source = Column(String(100))
    weight = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction(match_id='{self.match_id}', type='{self.type}')>"