"""
数据源配置表模型
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from .base import Base
import json


class DataSource(Base):
    """数据源配置表"""
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="数据源名称")
    type = Column(String(20), nullable=False, comment="类型: api/file")
    status = Column(Boolean, default=True, comment="启用状态")
    url = Column(String(500), comment="接口地址或文件路径")
    config = Column(Text, comment="配置信息(JSON格式)")
    last_update = Column(DateTime, comment="最后更新时间")
    error_rate = Column(Float(5, 2), default=0, comment="错误率")
    created_at = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    created_by = Column(Integer, comment="创建人ID")
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}', type='{self.type}')"
    
    @property
    def config_dict(self) -> dict:
        """获取配置字典"""
        if self.config:
            try:
                return json.loads(self.config)
            except:
                return {}
        return {}
    
    @config_dict.setter
    def config_dict(self, value: dict):
        """设置配置字典"""
        self.config = json.dumps(value, ensure_ascii=False)