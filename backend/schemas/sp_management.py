"""
足球SP管理模块 - Pydantic数据模型和验证器
"""
from pydantic import BaseModel, Field, validator, HttpUrl, conint, confloat
from typing import Optional, List, Dict, Any, Union
import json
from datetime import datetime
import re

# =============================================================================
# 数据源管理相关模型
# =============================================================================

class DataSourceBase(BaseModel):
    """数据源基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="数据源名称")
    type: str = Field(..., description="数据源类型: api/file")
    url: Optional[str] = Field(None, max_length=500, description="接口地址或文件路径")
    config: Optional[Union[Dict[str, Any], str]] = Field(None, description="配置信息(JSON格式)")
    status: bool = Field(True, description="启用状态")

class DataSourceCreate(DataSourceBase):
    """创建数据源请求模型"""
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['api', 'file']:
            raise ValueError('type必须是api或file')
        return v
    
    @validator('url')
    def validate_url(cls, v, values):
        if values.get('type') == 'api' and not v:
            raise ValueError('API类型数据源必须提供url')
        if v and values.get('type') == 'api':
            # 简单的URL格式验证
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(v):
                raise ValueError('请输入有效的URL地址')
        return v

class DataSourceUpdate(BaseModel):
    """更新数据源请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, max_length=500)
    config: Optional[Union[Dict[str, Any], str]] = None
    status: Optional[bool] = None

    @validator('config', pre=True)
    def validate_config(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return {}
        return v

class DataSourceResponse(DataSourceBase):
    """数据源响应模型"""
    id: int
    last_update: Optional[datetime] = None
    error_rate: float = Field(0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# =============================================================================
# 比赛信息管理相关模型
# =============================================================================

class MatchBase(BaseModel):
    """比赛基础模型"""
    match_id: str = Field(..., min_length=1, max_length=50, description="比赛唯一标识")
    home_team: str = Field(..., min_length=1, max_length=100, description="主队名称")
    away_team: str = Field(..., min_length=1, max_length=100, description="客队名称")
    match_time: datetime = Field(..., description="比赛时间")
    league: Optional[str] = Field(None, max_length=100, description="联赛/杯赛")
    status: str = Field('pending', description="比赛状态: pending/ongoing/finished")

class MatchCreate(MatchBase):
    """创建比赛请求模型"""
    home_score: Optional[int] = Field(None, ge=0, description="主队得分")
    away_score: Optional[int] = Field(None, ge=0, description="客队得分")
    final_result: Optional[str] = Field(None, max_length=20, description="最终赛果")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['pending', 'ongoing', 'finished']:
            raise ValueError('status必须是pending、ongoing或finished')
        return v
    
    @validator('match_time')
    def validate_match_time(cls, v):
        if v <= datetime.now():
            # 允许创建过去时间的比赛（用于补录历史数据）
            pass
        return v
    
    @validator('home_score', 'away_score')
    def validate_scores(cls, v, values, **kwargs):
        # 如果设置了比分，状态应该是finished
        status = values.get('status')
        field_name = kwargs.get('field').name
        
        if v is not None and status != 'finished':
            # 允许在创建时设置比分，但给出警告
            pass
        return v

class MatchUpdate(BaseModel):
    """更新比赛请求模型"""
    home_team: Optional[str] = Field(None, min_length=1, max_length=100)
    away_team: Optional[str] = Field(None, min_length=1, max_length=100)
    match_time: Optional[datetime] = None
    league: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    home_score: Optional[int] = Field(None, ge=0)
    away_score: Optional[int] = Field(None, ge=0)
    final_result: Optional[str] = Field(None, max_length=20)
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'ongoing', 'finished']:
            raise ValueError('status必须是pending、ongoing或finished')
        return v

class MatchResponse(MatchBase):
    """比赛响应模型"""
    id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    final_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
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
    
    class Config:
        from_attributes = True

# =============================================================================
# 赔率公司管理相关模型
# =============================================================================

class OddsCompanyBase(BaseModel):
    """赔率公司基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="公司名称")
    short_name: Optional[str] = Field(None, max_length=20, description="简称")
    logo_url: Optional[str] = Field(None, max_length=200, description="Logo地址")
    status: bool = Field(True, description="启用状态")
    weight: float = Field(1.0, ge=0, le=10, description="权重/优先级")

class OddsCompanyCreate(OddsCompanyBase):
    """创建赔率公司请求模型"""
    pass

class OddsCompanyUpdate(BaseModel):
    """更新赔率公司请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    short_name: Optional[str] = Field(None, max_length=20)
    logo_url: Optional[str] = Field(None, max_length=200)
    status: Optional[bool] = None
    weight: Optional[float] = Field(None, ge=0, le=10)

class OddsCompanyResponse(OddsCompanyBase):
    """赔率公司响应模型"""
    id: int
    created_at: datetime
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.short_name or self.name
    
    class Config:
        from_attributes = True

# =============================================================================
# SP值管理相关模型
# =============================================================================

class SPRecordBase(BaseModel):
    """SP值记录基础模型"""
    match_id: int = Field(..., gt=0, description="比赛ID")
    company_id: int = Field(..., gt=0, description="公司ID")
    handicap_type: str = Field(..., description="盘口类型: handicap/no_handicap")
    handicap_value: Optional[float] = Field(None, description="让球数值")
    sp_value: float = Field(..., gt=0, description="SP值")
    recorded_at: datetime = Field(..., description="记录时间")

class SPRecordCreate(SPRecordBase):
    """创建SP值记录请求模型"""
    
    @validator('handicap_type')
    def validate_handicap_type(cls, v):
        if v not in ['handicap', 'no_handicap']:
            raise ValueError('handicap_type必须是handicap或no_handicap')
        return v
    
    @validator('sp_value')
    def validate_sp_value(cls, v):
        if v <= 0:
            raise ValueError('SP值必须大于0')
        if v > 1000:  # 合理的SP值上限
            raise ValueError('SP值超出合理范围')
        return v
    
    @validator('handicap_value')
    def validate_handicap_value(cls, v, values):
        if values.get('handicap_type') == 'no_handicap' and v is not None:
            raise ValueError('no_handicap类型不应设置让球数值')
        if v is not None and abs(v) > 10:  # 合理的让球范围
            raise ValueError('让球数值超出合理范围(-10到10)')
        return v

class SPRecordUpdate(BaseModel):
    """更新SP值记录请求模型"""
    sp_value: Optional[float] = Field(None, gt=0)
    
    @validator('sp_value')
    def validate_sp_value(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('SP值必须大于0')
            if v > 1000:
                raise ValueError('SP值超出合理范围')
        return v

class SPRecordResponse(SPRecordBase):
    """SP值记录响应模型"""
    id: int
    created_at: datetime
    
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
        # 这里需要在服务层实现检查逻辑
        return False
    
    class Config:
        from_attributes = True

# =============================================================================
# SP值修改日志相关模型
# =============================================================================

class SPModificationLogResponse(BaseModel):
    """SP值修改日志响应模型"""
    id: int
    sp_record_id: int
    original_value: float
    modified_value: float
    modified_by: int
    reason: Optional[str] = None
    created_at: datetime
    
    @property
    def change_amount(self) -> float:
        """变化金额"""
        return self.modified_value - self.original_value
    
    @property
    def change_percentage(self) -> float:
        """变化百分比"""
        if self.original_value == 0:
            return 0
        return (self.change_amount / self.original_value) * 100
    
    class Config:
        from_attributes = True

# =============================================================================
# 查询参数模型
# =============================================================================

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")

class DataSourceFilterParams(PaginationParams):
    """数据源筛选参数"""
    type: Optional[str] = Field(None, description="数据源类型")
    status: Optional[bool] = Field(None, description="启用状态")
    search: Optional[str] = Field(None, max_length=50, description="搜索关键词")

class MatchFilterParams(PaginationParams):
    """比赛筛选参数"""
    status: Optional[str] = Field(None, description="比赛状态")
    league: Optional[str] = Field(None, max_length=50, description="联赛名称")
    team: Optional[str] = Field(None, max_length=50, description="队伍名称")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")

class SPRecordFilterParams(PaginationParams):
    """SP值记录筛选参数"""
    match_id: Optional[int] = Field(None, description="比赛ID")
    company_id: Optional[int] = Field(None, description="公司ID")
    handicap_type: Optional[str] = Field(None, description="盘口类型")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")

# =============================================================================
# 响应包装模型
# =============================================================================

from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(items=items, total=total, page=page, size=size, pages=pages)