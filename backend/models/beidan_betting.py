#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北单投注模拟相关模型"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class BeidanBettingScheme(BaseModel):
    """北单投注方案"""
    __tablename__ = "beidan_betting_schemes"
    __table_args__ = {"extend_existing": True}

    admin_user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), index=True, nullable=False)
    expect = Column(String(20), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    stake = Column(Float, nullable=False, default=0.0)
    pass_type = Column(String(50), nullable=False, default="all")
    split_mode = Column(String(20), nullable=False, default="even")
    total_odds = Column(Float, nullable=True, default=0.0)
    status = Column(String(20), nullable=False, default="pending")
    win_amount = Column(Float, nullable=False, default=0.0)
    profit = Column(Float, nullable=False, default=0.0)
    ticketed = Column(Boolean, nullable=False, default=False)

    items = relationship(
        "BeidanBettingSchemeItem",
        back_populates="scheme",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class BeidanBettingSchemeItem(BaseModel):
    """北单投注方案明细"""
    __tablename__ = "beidan_betting_scheme_items"
    __table_args__ = {"extend_existing": True}

    scheme_id = Column(Integer, ForeignKey("beidan_betting_schemes.id", ondelete="CASCADE"), index=True, nullable=False)
    match_seq = Column(String(10), index=True, nullable=False)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    match_time = Column(String(30), nullable=True)
    selected_result = Column(String(10), nullable=False)
    odds = Column(Float, nullable=False, default=0.0)
    result = Column(String(10), nullable=True)

    scheme = relationship("BeidanBettingScheme", back_populates="items")
