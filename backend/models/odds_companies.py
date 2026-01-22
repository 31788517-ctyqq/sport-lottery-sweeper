"""
赔率公司表模型
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class OddsCompany(Base):
    """赔率公司表"""
    
    __tablename__ = "odds_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="公司名称")
    short_name = Column(String(20), comment="简称")
    logo_url = Column(String(200), comment="Logo地址")
    status = Column(Boolean, default=True, comment="启用状态")
    weight = Column(Numeric(3, 2), default=1.0, comment="权重/优先级")
    created_at = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    
    # 关联关系
    sp_records = relationship("SPRecord", back_populates="company")
    
    def __repr__(self):
        return f"<OddsCompany(id={self.id}, name='{self.name}', short_name='{self.short_name}')"
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.short_name or self.name