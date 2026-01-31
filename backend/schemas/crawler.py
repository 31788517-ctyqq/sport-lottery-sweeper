"""
爬虫相关数据结构定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CrawlerSource(str, Enum):
    """爬虫数据源枚举"""
    SPORTTERY = "sporttery"
    FIVEHUNDRED = "500wan"
    DATA_CENTER = "data_center"


class MatchCreate(BaseModel):
    """创建比赛数据模型"""
    match_id: str = Field(..., description="比赛ID")
    league: str = Field(..., description="联赛名称")
    home_team: str = Field(..., description="主队名称")
    away_team: str = Field(..., description="客队名称")
    match_date: datetime = Field(..., description="比赛日期时间")
    match_time: Optional[str] = Field(None, description="比赛时间")
    venue: Optional[str] = Field(None, description="比赛场地")
    round_number: Optional[str] = Field(None, description="轮次")
    home_score: Optional[int] = Field(None, description="主队得分")
    away_score: Optional[int] = Field(None, description="客队得分")
    status: str = Field("scheduled", description="比赛状态")
    odds_home_win: float = Field(2.0, description="主胜赔率")
    odds_draw: float = Field(3.0, description="平局赔率")
    odds_away_win: float = Field(3.5, description="客胜赔率")
    popularity: int = Field(50, description="热度评分")
    source: CrawlerSource = Field(CrawlerSource.FIVEHUNDRED, description="数据来源")
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerStatus(BaseModel):
    """爬虫状态模型"""
    crawler_name: str
    status: str
    last_run: Optional[str]
    records_processed: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CrawlerLog(BaseModel):
    """爬虫日志模型"""
    crawler_name: str
    logs: List[str]
    total_lines: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CrawlStatistics(BaseModel):
    """爬取统计模型"""
    period_days: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    data_records_collected: int
    average_response_time: float
    top_sources: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CrawlerTaskConfig(BaseModel):
    """爬虫任务配置模型"""
    task_name: str
    source: CrawlerSource
    schedule: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel):
    """API响应基础模型"""
    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 数据源管理相关 ====================

class CrawlerSourceCreate(BaseModel):
    """创建爬虫数据源模型"""
    name: str = Field(..., description="数据源名称")
    category: str = Field(..., description="数据源类别")
    url: str = Field(..., description="数据源URL")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置参数")
    status: str = Field("active", description="状态")
    createTime: Optional[str] = Field(None, description="创建时间")
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerSourceUpdate(BaseModel):
    """更新爬虫数据源模型"""
    name: Optional[str] = Field(None, description="数据源名称")
    category: Optional[str] = Field(None, description="数据源类别")
    url: Optional[str] = Field(None, description="数据源URL")
    config: Optional[Dict[str, Any]] = Field(None, description="配置参数")
    status: Optional[str] = Field(None, description="状态")
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerSourceResponse(BaseModel):
    """爬虫数据源响应模型"""
    id: int
    name: str
    category: str
    url: str
    config: Dict[str, Any]
    status: str
    createTime: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerTaskCreate(BaseModel):
    """创建爬虫任务模型"""
    task_name: str
    source: str
    schedule: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerTaskResponse(BaseModel):
    """爬虫任务响应模型"""
    id: int
    task_name: str
    source: str
    schedule: str
    enabled: bool
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 情报分析相关 ====================

class CrawlerIntelligenceStats(BaseModel):
    """爬虫情报统计模型"""
    total_intelligence: int
    high_value_intelligence: int
    medium_value_intelligence: int
    low_value_intelligence: int
    processed_intelligence: int
    pending_intelligence: int
    average_processing_time: float
    top_sources: List[Dict[str, Any]]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class CrawlerIntelligenceData(BaseModel):
    """爬虫情报数据模型"""
    id: int
    source_id: int
    source_name: str
    category: str
    title: str
    content: str
    weight: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 趋势分析相关 ====================

class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    period_days: int
    total_matches: int
    average_odds_home: float
    average_odds_draw: float
    average_odds_away: float
    volatility_index: float
    trend_direction: str  # up/down/stable
    top_leagues: List[Dict[str, Any]]
    prediction_confidence: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True