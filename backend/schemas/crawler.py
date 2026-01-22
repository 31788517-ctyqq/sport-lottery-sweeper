"""
爬虫模块数据模式定义
使用 Pydantic 定义 API 请求和响应的数据结构
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 数据源相关 Schemas ====================

class CrawlerSourceBase(BaseModel):
    """数据源基础模型"""
    name: str = Field(..., description="数据源名称")
    url: str = Field(..., description="数据源URL")
    description: Optional[str] = Field(None, description="数据源描述")
    source_type: str = Field(..., description="数据源类型")
    status: str = Field("online", description="数据源状态")
    priority: int = Field(1, description="优先级")
    timeout: int = Field(30, description="超时时间(秒)")
    retry_times: int = Field(3, description="重试次数")


class CrawlerSourceCreate(CrawlerSourceBase):
    """创建数据源请求模型"""
    config: Optional[Dict[str, Any]] = Field({}, description="配置参数")


class CrawlerSourceUpdate(BaseModel):
    """更新数据源请求模型"""
    name: Optional[str] = Field(None, description="数据源名称")
    url: Optional[str] = Field(None, description="数据源URL")
    description: Optional[str] = Field(None, description="数据源描述")
    source_type: Optional[str] = Field(None, description="数据源类型")
    status: Optional[str] = Field(None, description="数据源状态")
    priority: Optional[int] = Field(None, description="优先级")
    timeout: Optional[int] = Field(None, description="超时时间(秒)")
    retry_times: Optional[int] = Field(None, description="重试次数")
    config: Optional[Dict[str, Any]] = Field(None, description="配置参数")


class CrawlerSourceResponse(CrawlerSourceBase):
    """数据源响应模型"""
    id: int = Field(..., description="数据源ID")
    status: str = Field(..., description="数据源状态")
    success_rate: float = Field(0.0, description="成功率")
    response_time: float = Field(0.0, description="平均响应时间(ms)")
    last_check_time: Optional[datetime] = Field(None, description="最后检查时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# ==================== 任务调度相关 Schemas ====================

class CrawlerTaskBase(BaseModel):
    """爬虫任务基础模型"""
    name: str = Field(..., description="任务名称")
    source_id: int = Field(..., description="数据源ID")
    task_type: str = Field(..., description="任务类型")
    cron_expression: str = Field(..., description="Cron表达式")
    is_active: bool = Field(True, description="是否激活")
    config: Optional[Dict[str, Any]] = Field({}, description="任务配置")


class CrawlerTaskCreate(CrawlerTaskBase):
    """创建任务请求模型"""
    pass


class CrawlerTaskUpdate(BaseModel):
    """更新任务请求模型"""
    name: Optional[str] = Field(None, description="任务名称")
    task_type: Optional[str] = Field(None, description="任务类型")
    cron_expression: Optional[str] = Field(None, description="Cron表达式")
    is_active: Optional[bool] = Field(None, description="是否激活")
    config: Optional[Dict[str, Any]] = Field(None, description="任务配置")


class CrawlerTaskResponse(CrawlerTaskBase):
    """任务响应模型"""
    id: int = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    last_run_time: Optional[datetime] = Field(None, description="最后运行时间")
    next_run_time: Optional[datetime] = Field(None, description="下次运行时间")
    run_count: int = Field(0, description="运行次数")
    success_count: int = Field(0, description="成功次数")
    error_count: int = Field(0, description="错误次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# ==================== 数据情报相关 Schemas ====================

class CrawlerIntelligenceStats(BaseModel):
    """数据情报统计模型"""
    total_crawled: int = Field(0, description="总抓取数量")
    today_crawled: int = Field(0, description="今日抓取数量")
    today_success: int = Field(0, description="今日成功数量")
    today_failed: int = Field(0, description="今日失败数量")
    overall_success_rate: float = Field(0.0, description="总体成功率")
    active_sources: int = Field(0, description="活跃数据源数量")
    error_distribution: List[Dict[str, Any]] = Field([], description="错误分布")


class CrawlerIntelligenceData(BaseModel):
    """数据情报模型"""
    id: int = Field(..., description="情报ID")
    source_id: int = Field(..., description="数据源ID")
    source_name: str = Field(..., description="数据源名称")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    category: str = Field(..., description="分类")
    status: str = Field(..., description="状态")
    confidence_score: float = Field(0.0, description="置信度分数")
    crawled_at: datetime = Field(..., description="抓取时间")
    processed_at: Optional[datetime] = Field(None, description="处理时间")


class CrawlerIntelligenceResponse(CrawlerIntelligenceData):
    """数据情报响应模型"""
    
    class Config:
        from_attributes = True


class TrendAnalysisData(BaseModel):
    """趋势分析数据模型"""
    dates: List[str] = Field(..., description="日期列表")
    crawl_counts: List[int] = Field(..., description="抓取数量列表")
    success_counts: List[int] = Field(..., description="成功数量列表")
    error_counts: List[int] = Field(..., description="错误数量列表")


class ErrorDistributionData(BaseModel):
    """错误分布数据模型"""
    error_types: List[str] = Field(..., description="错误类型列表")
    error_counts: List[int] = Field(..., description="错误数量列表")
    percentages: List[float] = Field(..., description="百分比列表")


# ==================== 爬虫配置相关 Schemas ====================

class CrawlerConfigBase(BaseModel):
    """爬虫配置基础模型"""
    config_key: str = Field(..., description="配置键")
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    config_type: str = Field("general", description="配置类型")


class CrawlerConfigCreate(CrawlerConfigBase):
    """创建配置请求模型"""
    pass


class CrawlerConfigUpdate(BaseModel):
    """更新配置请求模型"""
    config_value: Optional[str] = Field(None, description="配置值")
    description: Optional[str] = Field(None, description="配置描述")


class CrawlerConfigResponse(CrawlerConfigBase):
    """配置响应模型"""
    id: int = Field(..., description="配置ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True