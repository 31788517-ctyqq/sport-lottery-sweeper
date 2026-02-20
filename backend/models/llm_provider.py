"""
LLM供应商数据模型
用于存储和管理远程AI服务提供商的配置信息
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
)
from sqlalchemy.sql import func
import enum

from .base import BaseAuditModel


class LLMProviderTypeEnum(enum.Enum):
    """LLM供应商类型枚举"""
    OPENAI = "openai"                # OpenAI GPT系列
    ANTHROPIC = "anthropic"          # Anthropic Claude系列
    GOOGLE = "google"               # Google Gemini系列
    AZURE = "azure"                  # Azure OpenAI
    ALIBABA = "alibaba"              # 阿里云通义千问
    OLLAMA = "ollama"                # Ollama本地部署
    VLLM = "vllm"                    # vLLM本地部署
    ZHIPUAI = "zhipuai"              # 智谱AI
    CUSTOM = "custom"                # 自定义提供商


class LLMProviderStatusEnum(enum.Enum):
    """LLM供应商状态枚举"""
    HEALTHY = "healthy"              # 健康 - 连接正常
    UNHEALTHY = "unhealthy"          # 不健康 - 连接失败
    CHECKING = "checking"            # 检查中 - 正在测试连接
    DISABLED = "disabled"            # 禁用 - 手动禁用


class LLMProvider(BaseAuditModel):
    """
    LLM供应商模型
    存储远程AI服务提供商的配置信息
    """
    __tablename__ = "llm_providers"
    __table_args__ = {'extend_existing': True}
    
    # 基本信息
    name = Column(String(200), nullable=False, index=True, unique=True, 
                  comment="供应商名称（唯一标识）")
    provider_type = Column(
        Enum(
            LLMProviderTypeEnum,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        index=True,
        comment="供应商类型",
    )
    description = Column(Text, nullable=True, comment="供应商描述")
    
    # API配置
    api_key = Column(Text, nullable=False, comment="API密钥（加密存储）")
    base_url = Column(String(500), nullable=True, comment="基础URL（可选）")
    default_model = Column(String(100), nullable=True, comment="默认模型名称")
    available_models = Column(JSON, nullable=True, default=list, 
                              comment="可用模型列表")
    
    # 运行配置
    enabled = Column(Boolean, default=True, nullable=False, 
                     index=True, comment="是否启用")
    priority = Column(Integer, default=10, nullable=False, 
                      index=True, comment="优先级（1-10，值越小优先级越高）")
    max_requests_per_minute = Column(Integer, default=60, nullable=False,
                                     comment="每分钟最大请求数")
    timeout_seconds = Column(Integer, default=30, nullable=False,
                             comment="API调用超时时间（秒）")
    
    # 状态监控
    health_status = Column(
        Enum(
            LLMProviderStatusEnum,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
            validate_strings=True,
        ),
        default=LLMProviderStatusEnum.CHECKING,
        nullable=False,
        index=True,
        comment="健康状态",
    )
    last_checked_at = Column(DateTime, nullable=True, comment="最后检查时间")
    last_success_at = Column(DateTime, nullable=True, comment="最后成功时间")
    total_requests = Column(Integer, default=0, nullable=False,
                            comment="总请求数")
    successful_requests = Column(Integer, default=0, nullable=False,
                                 comment="成功请求数")
    failed_requests = Column(Integer, default=0, nullable=False,
                             comment="失败请求数")
    
    # 成本监控
    cost_per_token = Column(JSON, nullable=True, default=dict,
                            comment="每token成本（输入/输出）")
    total_cost = Column(Integer, default=0, nullable=False,
                         comment="累计成本（单位：分）")
    monthly_cost = Column(Integer, default=0, nullable=False,
                          comment="本月成本（单位：分）")
    
    # 高级配置
    rate_limit_strategy = Column(String(50), default="fixed_window",
                                 nullable=False, comment="限流策略")
    retry_policy = Column(JSON, nullable=True, default=dict,
                          comment="重试策略配置")
    circuit_breaker_config = Column(JSON, nullable=True, default=dict,
                                    comment="熔断器配置")
    
    # 元数据
    version = Column(String(50), nullable=True, comment="配置版本")
    tags = Column(JSON, nullable=True, default=list, comment="标签")
    
    def __repr__(self) -> str:
        return f"<LLMProvider(id={self.id}, name={self.name}, type={self.provider_type}, enabled={self.enabled})>"
    
    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            "id": self.id,
            "name": self.name,
            "provider_type": self.provider_type.value,
            "description": self.description,
            "base_url": self.base_url,
            "default_model": self.default_model,
            "available_models": self.available_models or [],
            "enabled": self.enabled,
            "priority": self.priority,
            "max_requests_per_minute": self.max_requests_per_minute,
            "timeout_seconds": self.timeout_seconds,
            "health_status": self.health_status.value,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_cost": self.total_cost / 100.0,  # 转换为元
            "monthly_cost": self.monthly_cost / 100.0,  # 转换为元
            "rate_limit_strategy": self.rate_limit_strategy,
            "retry_policy": self.retry_policy or {},
            "circuit_breaker_config": self.circuit_breaker_config or {},
            "version": self.version,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }
        
        if include_sensitive:
            data["api_key"] = self.api_key
            if self.cost_per_token:
                data["cost_per_token"] = self.cost_per_token
        
        return data
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_requests == 0:
            return 0.0
        return round(self.successful_requests / self.total_requests * 100, 2)
    
    @property
    def is_available(self) -> bool:
        """判断是否可用"""
        return (self.enabled and 
                self.health_status == LLMProviderStatusEnum.HEALTHY)
    
    def update_health_status(self, is_healthy: bool):
        """更新健康状态"""
        from datetime import datetime
        
        self.last_checked_at = datetime.utcnow()
        
        if is_healthy:
            self.health_status = LLMProviderStatusEnum.HEALTHY
            self.last_success_at = datetime.utcnow()
        else:
            self.health_status = LLMProviderStatusEnum.UNHEALTHY
        
        self.updated_at = datetime.utcnow()
