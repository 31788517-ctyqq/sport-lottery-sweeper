"""
比赛信息表模型（足球SP管理专用）
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base  # 使用与 match.py 相同的 Base


class FootballMatch(Base):
    """比赛信息表（足球SP管理专用）"""
    
    __tablename__ = "football_matches"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), unique=True, nullable=False, comment="比赛唯一标识")
    home_team = Column(String(100), nullable=False, comment="主队名称")
    away_team = Column(String(100), nullable=False, comment="客队名称")
    match_time = Column(DateTime, nullable=False, comment="比赛时间")
    league = Column(String(100), comment="联赛/杯赛")
    status = Column(String(20), default='pending', comment="比赛状态: pending/ongoing/finished")
    home_score = Column(Integer, comment="主队得分")
    away_score = Column(Integer, comment="客队得分")
    final_result = Column(String(20), comment="最终赛果")
    created_at = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    
    # 关联关系
    sp_records = relationship("SPRecord", back_populates="match", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FootballMatch(id={self.id}, {self.home_team} vs {self.away_team}, {self.match_time})>"
    
    @property
    def score_display(self) -> str:
        """显示比分"""
        if self.status == 'finished' and self.home_score is not None and self.away_score is not None:
            return f"{self.home_score}:{self.away_score}"
        return "-" 
    
    @property
    def status_display(self) -> str:
        """显示状态"""
        status_map = {
            'pending': '未开始',
            'ongoing': '进行中',
            'finished': '已结束'
        }
        return status_map.get(self.status, self.status)

# 注意：不要使用 Match 别名，它与 models.match.Match 冲突