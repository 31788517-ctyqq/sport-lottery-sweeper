"""
数据源配置表模型
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
import json
from datetime import datetime


class DataSource(Base):
    """数据源配置表"""
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="数据源名称")
    type = Column(String(20), nullable=False, comment="类型: api/file")  # 保持与API一致
    status = Column(Integer, default=1, comment="状态: 1=online/0=offline")  # 修改回Integer类型，使用数据库中的整数值
    url = Column(String(500), comment="接口地址或文件路径")
    config = Column(Text, comment="配置信息(JSON格式)")
    field_mapping = Column(JSON, nullable=True, comment="字段映射配置(JSON格式)")
    update_frequency = Column(Integer, default=60, nullable=False, comment="更新频率(分钟)")
    last_update = Column(DateTime, comment="最后更新时间")
    error_rate = Column(Float, default=0, comment="错误率")  # 修复：移除了精度参数，因为SQLite不支持
    created_at = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    created_by = Column(Integer, comment="创建人ID")
    source_id = Column(String(10), unique=True, comment="源ID")  # 移到最后，确保顺序不影响映射
    last_error = Column(Text, comment="上次错误信息")  # 新增：存储上次错误信息
    last_error_time = Column(DateTime, comment="上次错误时间")  # 新增：存储上次错误时间
    
    # 关系
    crawler_configs = relationship("CrawlerConfig", back_populates="data_source")
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"
    
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
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        # 将状态数字转换为字符串
        status_val = self.status
        if isinstance(status_val, int):
            # 假设1代表'online'，0代表'offline'，其他值可以根据需要映射
            if status_val == 1:
                status_str = 'online'
            elif status_val == 0:
                status_str = 'offline'
            else:
                status_str = 'online'  # 默认值
        else:
            status_str = status_val
        
        return {
            'id': self.id,
            'source_id': self.source_id or f"DS{self.id:03d}",  # 如果没有source_id，则自动生成
            'name': self.name,
            'type': self.type,
            'status': status_str,  # 使用转换后的状态字符串
            'url': self.url,
            'config': self.config_dict,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'error_rate': self.error_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'last_error': self.last_error,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None
        }