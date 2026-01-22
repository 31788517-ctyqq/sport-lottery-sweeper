"""
SP值记录表模型
"""

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class SPRecord(Base):
    """SP值记录表"""
    
    __tablename__ = "sp_records"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("football_matches.id"), nullable=False, comment="比赛ID")
    company_id = Column(Integer, ForeignKey("odds_companies.id"), nullable=False, comment="公司ID")
    handicap_type = Column(String(20), nullable=False, comment="盘口类型: handicap/no_handicap")
    handicap_value = Column(Numeric(4, 1), comment="让球数值")
    sp_value = Column(Numeric(8, 2), nullable=False, comment="SP值")
    recorded_at = Column(DateTime, nullable=False, comment="记录时间")
    created_at = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    
    # 关联关系
    match = relationship("FootballMatch", back_populates="sp_records")
    company = relationship("OddsCompany", back_populates="sp_records")
    modification_logs = relationship("SPModificationLog", back_populates="sp_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SPRecord(id={self.id}, match_id={self.match_id}, company_id={self.company_id}, sp_value={self.sp_value})"
    
    @property
    def handicap_display(self) -> str:
        """显示盘口"""
        if self.handicap_type == 'no_handicap':
            return "不让球"
        elif self.handicap_value is not None:
            direction = "-" if self.handicap_value > 0 else "+"
            return f"{direction}{abs(self.handicap_value)}"
        return self.handicap_type
    
    @property
    def is_modified(self) -> bool:
        """是否被修改过"""
        return len(self.modification_logs) > 0