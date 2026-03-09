"""
场地数据模型
"""
from datetime import datetime
from typing import List, Optional
import sqlalchemy as sa
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, CheckConstraint, Index, Table, Date
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel


class VenueTypeEnum(enum.Enum):
    """场馆类型枚举"""
    STADIUM = "stadium"                     # 体育场
    ARENA = "arena"                         # 竞技场
    FIELD = "field"                         # 足球场
    DOME = "dome"                          # 圆顶场馆


class VenueSurfaceEnum(enum.Enum):
    """场地表面类型枚举"""
    GRASS = "grass"                         # 天然草
    ARTIFICIAL_TURF = "artificial_turf"     # 人造草
    HARD_COURT = "hard_court"               # 硬地球场
    CLAY = "clay"                          # 红土
    CONCRETE = "concrete"                   # 混凝土


class Venue(BaseFullModel):
    """
    场地模型
    """
    __tablename__ = "venues"
    
    # 基本信息
    name = Column(String(200), nullable=False, index=True)
    capacity = Column(Integer, nullable=True, index=True)  # 容量
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    coordinates = Column(String(100), nullable=True, index=True)  # 坐标 (lat,lng)
    
    # 场地信息
    surface_type = Column(Enum(VenueSurfaceEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=True, index=True)  # 地面类型
    roof_type = Column(String(50), nullable=True, index=True)  # 屋顶类型 (open, closed, dome)
    
    # 建筑信息
    year_built = Column(Integer, nullable=True, index=True)  # 建造年份
    architect = Column(String(100), nullable=True)  # 建筑师
    
    # 图片资源
    image_urls = Column(sa.JSON, default=list, nullable=False)  # 图片URL数组，SQLite JSON存储  # 图片URL数组
    logo_url = Column(String(500), nullable=True)  # 标志图片
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_neutral = Column(Boolean, default=False, nullable=False, index=True)  # 是否中立场地
    
    # 设施信息
    facilities = Column(sa.JSON, default=list, nullable=False)  # 设施列表，SQLite JSON存储  # 设施列表
    
    # 气候信息
    climate_controlled = Column(Boolean, default=False, nullable=False)  # 是否气候受控
    altitude = Column(Float, nullable=True)  # 海拔高度
    
    # 维护信息
    last_maintenance = Column(DateTime(timezone=True), nullable=True)  # 最后维护时间
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)  # 外部数据来源
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 场馆配置
    
    # 关系
    matches = relationship("Match", back_populates="venue", cascade="all, delete-orphan")
    
    # 索引与表配置
    __table_args__ = (
        Index('idx_venues_city_country', 'city', 'country'),
        Index('idx_venues_capacity_active', 'capacity', 'is_active'),
        Index('idx_venues_surface_active', 'surface_type', 'is_active'),
        Index('idx_venues_coordinates', 'coordinates'),
        Index('idx_venues_active_neutral', 'is_active', 'is_neutral'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name={self.name}, city={self.city})>"


# 创建场地与球队的中间表
team_home_venues = Table(
    'team_home_venues', Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('venue_id', Integer, ForeignKey('venues.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), default=func.now(), nullable=False)
)