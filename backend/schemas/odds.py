"""
赔率相关的Pydantic模型
用于API请求和响应验证
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..models.odds import OddsTypeEnum, OddsMovementTypeEnum, OddsProviderEnum


# ==================== 基础模型 ====================

class OddsBase(BaseModel):
    """赔率基础模型"""
    match_id: int = Field(..., description="比赛ID")
    bookmaker_id: int = Field(..., description="庄家ID")
    provider_id: Optional[int] = Field(None, description="赔率提供商ID")
    odds_type: OddsTypeEnum = Field(..., description="赔率类型")
    home_win_odds: Optional[float] = Field(None, description="主胜赔率")
    draw_odds: Optional[float] = Field(None, description="平局赔率")
    away_win_odds: Optional[float] = Field(None, description="客胜赔率")
    asian_handicap_home: Optional[float] = Field(None, description="亚盘主队让球")
    asian_handicap_away: Optional[float] = Field(None, description="亚盘客队让球")
    handicap_line: Optional[float] = Field(None, description="让球线")
    over_under_line: Optional[float] = Field(None, description="大小球线")
    over_odds: Optional[float] = Field(None, description="大球赔率")
    under_odds: Optional[float] = Field(None, description="小球赔率")
    is_live: bool = Field(False, description="是否实时赔率")
    market_depth: Dict[str, Any] = Field(default_factory=dict, description="市场深度")
    liquidity: float = Field(0.0, description="流动性")
    volume: float = Field(0.0, description="交易量")
    volatility: float = Field(0.0, description="波动率")
    is_opening: bool = Field(False, description="是否开盘赔率")
    is_closing: bool = Field(False, description="是否收盘赔率")


class OddsCreate(OddsBase):
    """创建赔率模型"""
    pass


class OddsUpdate(BaseModel):
    """更新赔率模型"""
    home_win_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_win_odds: Optional[float] = None
    asian_handicap_home: Optional[float] = None
    asian_handicap_away: Optional[float] = None
    handicap_line: Optional[float] = None
    over_under_line: Optional[float] = None
    over_odds: Optional[float] = None
    under_odds: Optional[float] = None
    is_live: Optional[bool] = None
    market_depth: Optional[Dict[str, Any]] = None
    liquidity: Optional[float] = None
    volume: Optional[float] = None
    volatility: Optional[float] = None
    is_opening: Optional[bool] = None
    is_closing: Optional[bool] = None


class OddsResponse(OddsBase):
    """赔率响应模型"""
    id: int = Field(..., description="赔率ID")
    last_updated: datetime = Field(..., description="最后更新时间")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# ==================== 庄家模型 ====================

class BookmakerBase(BaseModel):
    """庄家基础模型"""
    name: str = Field(..., max_length=100, description="庄家名称")
    code: str = Field(..., max_length=50, description="庄家代码")
    full_name: Optional[str] = Field(None, max_length=200, description="庄家全称")
    country: Optional[str] = Field(None, max_length=100, description="国家")
    country_code: Optional[str] = Field(None, max_length=10, description="国家代码")
    website: Optional[str] = Field(None, max_length=200, description="网站")
    is_active: bool = Field(True, description="是否激活")


class BookmakerCreate(BookmakerBase):
    """创建庄家模型"""
    pass


class BookmakerUpdate(BaseModel):
    """更新庄家模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    full_name: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class BookmakerResponse(BookmakerBase):
    """庄家响应模型"""
    id: int = Field(..., description="庄家ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# ==================== 赔率提供商模型 ====================

class OddsProviderBase(BaseModel):
    """赔率提供商基础模型"""
    name: str = Field(..., max_length=100, description="提供商名称")
    code: str = Field(..., max_length=50, description="提供商代码")
    full_name: Optional[str] = Field(None, max_length=200, description="提供商全称")
    country: Optional[str] = Field(None, max_length=100, description="国家")
    country_code: Optional[str] = Field(None, max_length=10, description="国家代码")
    website: Optional[str] = Field(None, max_length=200, description="网站")
    api_endpoint: Optional[str] = Field(None, max_length=200, description="API端点")
    is_active: bool = Field(True, description="是否激活")
    reliability_score: float = Field(0.0, description="可靠性分数")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置信息")


class OddsProviderCreate(OddsProviderBase):
    """创建赔率提供商模型"""
    pass


class OddsProviderUpdate(BaseModel):
    """更新赔率提供商模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    full_name: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    website: Optional[str] = None
    api_endpoint: Optional[str] = None
    is_active: Optional[bool] = None
    reliability_score: Optional[float] = None
    config: Optional[Dict[str, Any]] = None


class OddsProviderResponse(OddsProviderBase):
    """赔率提供商响应模型"""
    id: int = Field(..., description="提供商ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# ==================== 赔率变动模型 ====================

class OddsMovementBase(BaseModel):
    """赔率变动基础模型"""
    odds_id: int = Field(..., description="赔率ID")
    movement_type: OddsMovementTypeEnum = Field(..., description="变动类型")
    change_percentage: float = Field(..., description="变动百分比")
    previous_value: Optional[float] = Field(None, description="之前的值")
    new_value: Optional[float] = Field(None, description="新的值")
    market_impact: Optional[float] = Field(None, description="市场影响")
    confidence_score: Optional[float] = Field(None, description="置信度分数")


class OddsMovementCreate(OddsMovementBase):
    """创建赔率变动模型"""
    pass


class OddsMovementUpdate(BaseModel):
    """更新赔率变动模型"""
    movement_type: Optional[OddsMovementTypeEnum] = None
    change_percentage: Optional[float] = None
    previous_value: Optional[float] = None
    new_value: Optional[float] = None
    market_impact: Optional[float] = None
    confidence_score: Optional[float] = None


class OddsMovementResponse(OddsMovementBase):
    """赔率变动响应模型"""
    id: int = Field(..., description="变动ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")

    class Config:
        from_attributes = True


# ==================== 列表响应模型 ====================

class OddsListResponse(BaseModel):
    """赔率列表响应模型"""
    items: List[OddsResponse] = Field(..., description="赔率列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class BookmakerListResponse(BaseModel):
    """庄家列表响应模型"""
    items: List[BookmakerResponse] = Field(..., description="庄家列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class OddsProviderListResponse(BaseModel):
    """赔率提供商列表响应模型"""
    items: List[OddsProviderResponse] = Field(..., description="提供商列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")