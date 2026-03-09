"""
LangChain服务工厂
用于创建和管理LangChain服务实例
"""

import logging
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass
from enum import Enum

from .langchain_service import LangChainService, create_preset_chain
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class LangChainProviderType(Enum):
    """LangChain提供商类型"""
    OPENAI = "openai"
    GEMINI = "gemini"
    QWEN = "qwen"
    CUSTOM = "custom"


@dataclass
class LangChainConfig:
    """LangChain配置"""
    provider_type: LangChainProviderType
    api_key: str
    model_name: str = "default"
    temperature: float = 0.7
    max_tokens: int = 1000
    enable_memory: bool = True
    enable_tools: bool = True
    enable_agents: bool = False
    
    # LangSmith配置
    langsmith_enabled: bool = False
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None
    
    # 向量存储配置
    vector_store_enabled: bool = False
    vector_store_type: str = "faiss"  # faiss, pgvector, milvus
    
    def __post_init__(self):
        """验证配置"""
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        
        if self.langsmith_enabled and not self.langsmith_api_key:
            raise ValueError("启用LangSmith必须提供API密钥")


class LangChainFactory:
    """LangChain服务工厂"""
    
    _instances: Dict[str, LangChainService] = {}
    
    @classmethod
    def create_service(cls, config: LangChainConfig, service_name: str = "default") -> LangChainService:
        """创建LangChain服务实例"""
        if service_name in cls._instances:
            logger.warning(f"LangChain服务 {service_name} 已存在，返回现有实例")
            return cls._instances[service_name]
        
        # 创建LLMService
        llm_service = LLMService()
        
        # 注册提供商
        provider_name = config.provider_type.value
        llm_service.register_provider(provider_name, config.api_key)
        llm_service.set_default_provider(provider_name)
        
        # 创建LangChain服务
        langchain_service = LangChainService(llm_service)
        
        # 配置LangSmith（如果启用）
        if config.langsmith_enabled:
            cls._setup_langsmith(config, langchain_service)
        
        # 创建预设链
        cls._create_preset_chains(langchain_service)
        
        # 存储实例
        cls._instances[service_name] = langchain_service
        
        logger.info(f"LangChain服务 {service_name} 创建成功")
        return langchain_service
    
    @classmethod
    def get_service(cls, service_name: str = "default") -> Optional[LangChainService]:
        """获取LangChain服务实例"""
        return cls._instances.get(service_name)
    
    @classmethod
    def destroy_service(cls, service_name: str):
        """销毁LangChain服务实例"""
        if service_name in cls._instances:
            del cls._instances[service_name]
            logger.info(f"LangChain服务 {service_name} 已销毁")
    
    @classmethod
    def list_services(cls) -> Dict[str, Any]:
        """列出所有服务实例"""
        return {
            name: {
                "provider": service.llm_service.default_provider,
                "chains": list(service.chains.keys()),
                "tools": list(service.tools.keys())
            }
            for name, service in cls._instances.items()
        }
    
    @classmethod
    def _setup_langsmith(cls, config: LangChainConfig, service: LangChainService):
        """设置LangSmith可观测性"""
        try:
            os.environ["LANGSMITH_API_KEY"] = config.langsmith_api_key
            os.environ["LANGSMITH_PROJECT"] = config.langsmith_project or "sport-lottery-agents"
            # 设置LangChain追踪环境变量（根据LangSmith文档）
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project or "sport-lottery-agents"
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key
            
            logger.info("LangSmith配置已启用（LANGCHAIN_TRACING_V2=true）")
        except Exception as e:
            logger.warning(f"LangSmith配置失败: {e}")
    
    @classmethod
    def _create_preset_chains(cls, service: LangChainService):
        """创建预设链"""
        try:
            # 预测分析链
            create_preset_chain(service, "prediction_analysis", "prediction_chain")
            
            # 风险评估链
            create_preset_chain(service, "risk_assessment", "risk_chain")
            
            # 日志分析链
            create_preset_chain(service, "log_analysis", "log_analysis_chain")
            
            logger.info("预设链创建完成")
        except Exception as e:
            logger.warning(f"创建预设链失败: {e}")


def create_default_langchain_service() -> LangChainService:
    """创建默认LangChain服务（从环境变量读取配置）"""
    
    # 从环境变量读取配置
    provider_type = os.getenv("LANGCHAIN_PROVIDER", "openai")
    api_key = os.getenv("LANGCHAIN_API_KEY")
    
    if not api_key:
        raise ValueError("必须设置LANGCHAIN_API_KEY环境变量")
    
    # 确定提供商类型
    if provider_type.lower() == "openai":
        provider_enum = LangChainProviderType.OPENAI
    elif provider_type.lower() == "gemini":
        provider_enum = LangChainProviderType.GEMINI
    elif provider_type.lower() == "qwen":
        provider_enum = LangChainProviderType.QWEN
    else:
        raise ValueError(f"不支持的LangChain提供商: {provider_type}")
    
    # 创建配置
    config = LangChainConfig(
        provider_type=provider_enum,
        api_key=api_key,
        model_name=os.getenv("LANGCHAIN_MODEL", "default"),
        temperature=float(os.getenv("LANGCHAIN_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LANGCHAIN_MAX_TOKENS", "1000")),
        langsmith_enabled=bool(os.getenv("LANGSMITH_ENABLED", "false").lower() == "true"),
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        langsmith_project=os.getenv("LANGSMITH_PROJECT", "sport-lottery-agents")
    )
    
    # 创建服务
    return LangChainFactory.create_service(config)


def get_langchain_service(service_name: str = "default") -> LangChainService:
    """获取LangChain服务（单例模式）"""
    service = LangChainFactory.get_service(service_name)
    
    if service is None:
        service = create_default_langchain_service()
    
    return service


# 全局服务实例
_default_service: Optional[LangChainService] = None


def get_default_service() -> LangChainService:
    """获取全局默认服务"""
    global _default_service
    
    if _default_service is None:
        _default_service = create_default_langchain_service()
    
    return _default_service


def reset_default_service():
    """重置全局默认服务"""
    global _default_service
    _default_service = None
    LangChainFactory.destroy_service("default")