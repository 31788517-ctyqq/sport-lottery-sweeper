"""
LLM供应商模式定义
用于API请求/响应验证
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import enum


class LLMProviderType(str, enum.Enum):
    """LLM供应商类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    ALIBABA = "alibaba"
    OLLAMA = "ollama"
    VLLM = "vllm"
    ZHIPUAI = "zhipuai"
    CUSTOM = "custom"


class LLMProviderStatus(str, enum.Enum):
    """LLM供应商状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CHECKING = "checking"
    DISABLED = "disabled"


# 基础模式
class LLMProviderBase(BaseModel):
    """LLM供应商基础模式"""
    name: str = Field(..., min_length=1, max_length=200, description="供应商名称（唯一标识）")
    provider_type: LLMProviderType = Field(..., description="供应商类型")
    description: Optional[str] = Field(None, description="供应商描述")
    
    # API配置
    api_key: str = Field(..., min_length=1, description="API密钥")
    base_url: Optional[str] = Field(None, max_length=500, description="基础URL（可选）")
    default_model: Optional[str] = Field(None, max_length=100, description="默认模型名称")
    available_models: Optional[List[str]] = Field(default_factory=list, description="可用模型列表")
    
    # 运行配置
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=10, ge=1, le=10, description="优先级（1-10，值越小优先级越高）")
    max_requests_per_minute: int = Field(default=60, ge=1, description="每分钟最大请求数")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="API调用超时时间（秒）")
    
    # 成本监控
    cost_per_token: Optional[Dict[str, float]] = Field(default_factory=dict, description="每token成本（输入/输出）")
    
    # 高级配置
    rate_limit_strategy: str = Field(default="fixed_window", description="限流策略")
    retry_policy: Optional[Dict[str, Any]] = Field(default_factory=dict, description="重试策略配置")
    circuit_breaker_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="熔断器配置")
    
    # 元数据
    version: Optional[str] = Field(None, max_length=50, description="配置版本")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        """验证名称格式"""
        if not v.strip():
            raise ValueError('供应商名称不能为空')
        # 检查名称是否包含特殊字符
        import re
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', v):
            raise ValueError('供应商名称只能包含字母、数字、下划线、连字符和空格')
        return v.strip()
    
    @validator('base_url')
    def base_url_must_be_valid(cls, v):
        """验证基础URL格式"""
        if v is None or v == '':
            return v
        
        from urllib.parse import urlparse
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError('基础URL格式无效')
            if result.scheme not in ['http', 'https']:
                raise ValueError('基础URL必须使用HTTP或HTTPS协议')
        except Exception:
            raise ValueError('基础URL格式无效')
        return v
    
    @validator('api_key')
    def api_key_must_be_valid(cls, v):
        """验证API密钥格式（基本验证）"""
        if not v.strip():
            raise ValueError('API密钥不能为空')
        # 检查最小长度
        if len(v.strip()) < 8:
            raise ValueError('API密钥长度太短')
        return v.strip()


# 创建模式
class LLMProviderCreate(LLMProviderBase):
    """创建LLM供应商模式"""
    pass


# 更新模式
class LLMProviderUpdate(BaseModel):
    """更新LLM供应商模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="供应商名称")
    description: Optional[str] = Field(None, description="供应商描述")
    
    # API配置
    api_key: Optional[str] = Field(None, min_length=1, description="API密钥")
    base_url: Optional[str] = Field(None, max_length=500, description="基础URL")
    default_model: Optional[str] = Field(None, max_length=100, description="默认模型")
    available_models: Optional[List[str]] = Field(None, description="可用模型列表")
    
    # 运行配置
    enabled: Optional[bool] = Field(None, description="是否启用")
    priority: Optional[int] = Field(None, ge=1, le=10, description="优先级")
    max_requests_per_minute: Optional[int] = Field(None, ge=1, description="每分钟最大请求数")
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300, description="超时时间")
    
    # 成本监控
    cost_per_token: Optional[Dict[str, float]] = Field(None, description="每token成本")
    
    # 高级配置
    rate_limit_strategy: Optional[str] = Field(None, description="限流策略")
    retry_policy: Optional[Dict[str, Any]] = Field(None, description="重试策略")
    circuit_breaker_config: Optional[Dict[str, Any]] = Field(None, description="熔断器配置")
    
    # 元数据
    version: Optional[str] = Field(None, max_length=50, description="配置版本")
    tags: Optional[List[str]] = Field(None, description="标签")


# 响应模式（不包含敏感信息）
class LLMProviderResponse(BaseModel):
    """LLM供应商响应模式"""
    id: int = Field(..., description="供应商ID")
    name: str = Field(..., description="供应商名称")
    provider_type: LLMProviderType = Field(..., description="供应商类型")
    description: Optional[str] = Field(None, description="供应商描述")
    
    # API配置（不包含敏感信息）
    base_url: Optional[str] = Field(None, description="基础URL")
    default_model: Optional[str] = Field(None, description="默认模型")
    available_models: List[str] = Field(default_factory=list, description="可用模型列表")
    
    # 运行配置
    enabled: bool = Field(..., description="是否启用")
    priority: int = Field(..., description="优先级")
    max_requests_per_minute: int = Field(..., description="每分钟最大请求数")
    timeout_seconds: int = Field(..., description="超时时间")
    
    # 状态监控
    health_status: LLMProviderStatus = Field(..., description="健康状态")
    last_checked_at: Optional[datetime] = Field(None, description="最后检查时间")
    last_success_at: Optional[datetime] = Field(None, description="最后成功时间")
    total_requests: int = Field(..., description="总请求数")
    successful_requests: int = Field(..., description="成功请求数")
    failed_requests: int = Field(..., description="失败请求数")
    
    # 成本监控
    total_cost: float = Field(..., description="累计成本（元）")
    monthly_cost: float = Field(..., description="本月成本（元）")
    
    # 高级配置
    rate_limit_strategy: str = Field(..., description="限流策略")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="重试策略")
    circuit_breaker_config: Dict[str, Any] = Field(default_factory=dict, description="熔断器配置")
    
    # 元数据
    version: Optional[str] = Field(None, description="配置版本")
    tags: List[str] = Field(default_factory=list, description="标签")
    
    # 审计信息
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[int] = Field(None, description="创建人ID")
    updated_by: Optional[int] = Field(None, description="更新人ID")
    
    # 计算属性
    success_rate: float = Field(..., description="成功率（百分比）")
    is_available: bool = Field(..., description="是否可用")
    
    class Config:
        from_attributes = True


# 列表响应模式
class LLMProviderListResponse(BaseModel):
    """LLM供应商列表响应模式"""
    providers: List[LLMProviderResponse] = Field(..., description="供应商列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


# 连接测试请求模式
class LLMProviderTestRequest(BaseModel):
    """LLM供应商连接测试请求模式"""
    test_prompt: Optional[str] = Field(default="Hello, how are you?", description="测试提示词")
    model: Optional[str] = Field(None, description="测试使用的模型（可选）")


# 连接测试响应模式
class LLMProviderTestResponse(BaseModel):
    """LLM供应商连接测试响应模式"""
    success: bool = Field(..., description="测试是否成功")
    response_time_ms: Optional[int] = Field(None, description="响应时间（毫秒）")
    response_text: Optional[str] = Field(None, description="响应文本")
    error_message: Optional[str] = Field(None, description="错误信息")
    health_status: LLMProviderStatus = Field(..., description="新的健康状态")


# 健康检查响应模式
class LLMProviderHealthResponse(BaseModel):
    """LLM供应商健康检查响应模式"""
    provider_id: int = Field(..., description="供应商ID")
    provider_name: str = Field(..., description="供应商名称")
    health_status: LLMProviderStatus = Field(..., description="健康状态")
    last_checked_at: datetime = Field(..., description="最后检查时间")
    success_rate: float = Field(..., description="成功率")
    is_available: bool = Field(..., description="是否可用")


# 批量操作请求模式
class LLMProviderBatchRequest(BaseModel):
    """LLM供应商批量操作请求模式"""
    provider_ids: List[int] = Field(..., min_items=1, description="供应商ID列表")
    action: str = Field(..., description="操作类型：enable, disable, test")


# 批量操作响应模式
class LLMProviderBatchResponse(BaseModel):
    """LLM供应商批量操作响应模式"""
    success_count: int = Field(..., description="成功操作数量")
    failed_count: int = Field(..., description="失败操作数量")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="详细结果列表")


# 统计信息响应模式
class LLMProviderStatsResponse(BaseModel):
    """LLM供应商统计信息响应模式"""
    total_providers: int = Field(..., description="总供应商数量")
    enabled_providers: int = Field(..., description="启用供应商数量")
    healthy_providers: int = Field(..., description="健康供应商数量")
    total_requests: int = Field(..., description="总请求数")
    total_cost: float = Field(..., description="总成本（元）")
    monthly_cost: float = Field(..., description="本月成本（元）")
    provider_stats: List[Dict[str, Any]] = Field(default_factory=list, description="各供应商统计信息")