"""
SP值修改日志表模型
"""

from sqlalchemy import Column, Integer, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class SPModificationLog(Base):
    """SP值修改日志表"""
    
    __tablename__ = "sp_modification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sp_record_id = Column(Integer, ForeignKey("sp_records.id"), nullable=False, comment="SP记录ID")
    original_value = Column(Numeric(8, 2), nullable=False, comment="原值")
    modified_value = Column(Numeric(8, 2), nullable=False, comment="修改后的值")
    modified_by = Column(Integer, nullable=False, comment="修改人ID")
    reason = Column(Text, comment="修改原因")
    created_at = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    
    # 关联关系
    sp_record = relationship("SPRecord", back_populates="modification_logs")
    
    def __repr__(self):
        return f"<SPModificationLog(id={self.id}, sp_record_id={self.sp_record_id}, {self.original_value}->{self.modified_value})"
    
    @property
    def change_amount(self) -> float:
        """变化金额"""
        return float(self.modified_value) - float(self.original_value)
    
    @property
    def change_percentage(self) -> float:
        """变化百分比"""
        if self.original_value == 0:
            return 0
        return (self.change_amount / float(self.original_value)) * 100