"""
数据分析相关Schema定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    query: str = Field(..., description="查询语句")
    parameters: Optional[Dict[str, Any]] = Field(None, description="查询参数")


class ReportRequest(BaseModel):
    report_type: str = Field(..., description="报表类型")
    filters: Optional[Dict[str, Any]] = Field(None, description="过滤条件")
    format: str = Field("csv", description="导出格式")


class DistributionAnalysisResponse(BaseModel):
    total_count: int
    avg_sp_value: float
    min_sp_value: float
    max_sp_value: float
    distribution: Dict[str, int]
    charts_data: Dict[str, Any]


class VolatilityAnalysisResponse(BaseModel):
    total_matches: int
    volatile_matches: int
    volatility_rate: float
    top_volatile_cases: List[Dict[str, Any]]


class CompanyComparisonResponse(BaseModel):
    companies: List[Dict[str, Any]]
    comparison_metrics: Dict[str, Any]
    recommendations: List[str]


class CorrelationAnalysisResponse(BaseModel):
    correlation_coefficient: float
    sample_size: int
    insights: List[str]
    confidence_level: float