#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北单投注模拟相关Schema"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BettingSelection(BaseModel):
    matchSeq: str = Field(..., description="场次序号")
    homeTeam: str
    awayTeam: str
    matchTime: Optional[str] = None
    selectedResult: str = Field(..., description="win/draw/lose")
    odds: float = Field(..., ge=0)


class BettingSchemeCreate(BaseModel):
    expect: str = Field(..., description="期号")
    name: Optional[str] = Field(default=None, description="方案名称")
    stake: float = Field(..., gt=0, description="投注金额")
    passType: List[int] = Field(..., description="串关类型，如[2,3]表示2串1+3串1")
    splitMode: str = Field(default="even", description="金额分配方式")
    selections: List[BettingSelection] = Field(..., min_items=1)


class BettingSchemeUpdate(BaseModel):
    name: Optional[str] = None
    stake: Optional[float] = None
    passType: Optional[List[int]] = None
    splitMode: Optional[str] = None
    selections: Optional[List[BettingSelection]] = None


class BettingSchemeItemResponse(BettingSelection):
    id: int
    result: Optional[str] = None


class BettingSchemeResponse(BaseModel):
    id: int
    expect: str
    name: str
    stake: float
    passType: str
    splitMode: str
    totalOdds: float
    status: str
    winAmount: float
    profit: float
    ticketed: bool = False
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    items: List[BettingSchemeItemResponse] = []


class BettingSchemeListResponse(BaseModel):
    items: List[BettingSchemeResponse]
    total: int
    page: int
    pageSize: int
