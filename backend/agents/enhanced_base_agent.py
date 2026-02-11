"""
增强的智能体基类
支持LangChain集成和更丰富的功能
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.agents import Tool

from ..services.langchain_service import LangChainService

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """智能体能力枚举"""
    DATA_PROCESSING = "data_processing"
    PREDICTION = "prediction"
    ANALYSIS = "analysis"
    MONITORING = "monitoring"
    ALERTING = "alerting"
    RECOMMENDATION = "recommendation"
    AUTOMATION = "automation"
    COLLABORATION = "collaboration"


class AgentExecutionMode(Enum):
    """智能体执行模式"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"


class EnhancedBaseAgent(ABC):
    """增强的智能体基类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        execution_mode: AgentExecutionMode = AgentExecutionMode.SYNCHRONOUS,
        langchain_service: Optional[LangChainService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.execution_mode = execution_mode
        self.langchain_service = langchain_service
        self.config = config or {}
        
        # 执行状态
        self._is_running = False
        self._last_execution: Optional[datetime] = None
        self._execution_count = 0
        self._error_count = 0
        
        # LangChain组件
        self._chains: Dict[str, Any] = {}
        self._tools: Dict[str, Tool] = {}
        
        # 初始化LangChain组件
        self._initialize_langchain_components()
        
        logger.info(f"智能体 {name} 初始化完成")
    
    def _initialize_langchain_components(self):
        """初始化LangChain组件"""
        if self.langchain_service:
            # 根据能力创建相应的链
            if AgentCapability.PREDICTION in self.capabilities:
                self._create_prediction_chain()
            
            if AgentCapability.ANALYSIS in self.capabilities:
                self._create_analysis_chain()
            
            if AgentCapability.MONITORING in self.capabilities:
                self._create_monitoring_chain()
            
            # 创建通用工具
            self._create_basic_tools()
    
    def _create_prediction_chain(self):
        """创建预测链"""
        if not self.langchain_service:
            return
        
        template = """基于以下数据，请提供专业预测分析：

数据：{data}
上下文：{context}

请提供详细的预测结果和置信度分析："""
        
        self._chains["prediction"] = self.langchain_service.create_simple_chain(
            f"{self.name}_prediction",
            template,
            input_variables=["data", "context"]
        )
    
    def _create_analysis_chain(self):
        """创建分析链"""
        if not self.langchain_service:
            return
        
        template = """请分析以下数据，提供深入洞察：

数据：{data}
分析目标：{analysis_goal}

请提供详细的分析报告："""
        
        self._chains["analysis"] = self.langchain_service.create_simple_chain(
            f"{self.name}_analysis",
            template,
            input_variables=["data", "analysis_goal"]
        )
    
    def _create_monitoring_chain(self):
        """创建监控链"""
        if not self.langchain_service:
            return
        
        template = """请监控以下系统状态，识别潜在问题：

状态数据：{status_data}
监控指标：{metrics}

请提供监控报告和告警建议："""
        
        self._chains["monitoring"] = self.langchain_service.create_simple_chain(
            f"{self.name}_monitoring",
            template,
            input_variables=["status_data", "metrics"]
        )
    
    def _create_basic_tools(self):
        """创建基础工具"""
        # 数据验证工具
        self._tools["data_validation"] = Tool(
            name="DataValidation",
            func=self._validate_data,
            description="验证数据质量和完整性"
        )
        
        # 性能分析工具
        self._tools["performance_analysis"] = Tool(
            name="PerformanceAnalysis",
            func=self._analyze_performance,
            description="分析系统性能指标"
        )
        
        # 风险评估工具
        self._tools["risk_assessment"] = Tool(
            name="RiskAssessment",
            func=self._assess_risk,
            description="评估业务风险"
        )
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体主要逻辑（抽象方法）"""
        pass
    
    async def execute_with_langchain(self, chain_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """使用LangChain链执行"""
        if not self.langchain_service:
            raise RuntimeError("LangChain服务未配置")
        
        if chain_name not in self._chains:
            raise ValueError(f"链 {chain_name} 不存在")
        
        try:
            result = await self.langchain_service.run_chain(chain_name, inputs)
            return result
        except Exception as e:
            logger.error(f"LangChain链执行失败: {e}")
            raise
    
    async def predict(self, data: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """预测功能"""
        if "prediction" not in self._chains:
            raise RuntimeError("智能体不支持预测功能")
        
        inputs = {
            "data": str(data),
            "context": str(context or {})
        }
        
        return await self.execute_with_langchain("prediction", inputs)
    
    async def analyze(self, data: Any, analysis_goal: str) -> Dict[str, Any]:
        """分析功能"""
        if "analysis" not in self._chains:
            raise RuntimeError("智能体不支持分析功能")
        
        inputs = {
            "data": str(data),
            "analysis_goal": analysis_goal
        }
        
        return await self.execute_with_langchain("analysis", inputs)
    
    async def monitor(self, status_data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """监控功能"""
        if "monitoring" not in self._chains:
            raise RuntimeError("智能体不支持监控功能")
        
        inputs = {
            "status_data": str(status_data),
            "metrics": str(metrics)
        }
        
        return await self.execute_with_langchain("monitoring", inputs)
    
    def start(self):
        """启动智能体"""
        if self._is_running:
            logger.warning(f"智能体 {self.name} 已经在运行")
            return
        
        self._is_running = True
        logger.info(f"智能体 {self.name} 已启动")
    
    def stop(self):
        """停止智能体"""
        if not self._is_running:
            logger.warning(f"智能体 {self.name} 未运行")
            return
        
        self._is_running = False
        logger.info(f"智能体 {self.name} 已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": [capability.value for capability in self.capabilities],
            "execution_mode": self.execution_mode.value,
            "is_running": self._is_running,
            "last_execution": self._last_execution.isoformat() if self._last_execution else None,
            "execution_count": self._execution_count,
            "error_count": self._error_count,
            "success_rate": (1 - (self._error_count / max(self._execution_count, 1))) * 100,
            "available_chains": list(self._chains.keys()),
            "available_tools": list(self._tools.keys()),
            "langchain_enabled": self.langchain_service is not None
        }
    
    async def validate_input(self, context: Dict[str, Any]) -> bool:
        """验证输入数据"""
        # 基础验证逻辑，子类可以重写
        required_fields = self.config.get("required_fields", [])
        
        for field in required_fields:
            if field not in context:
                logger.error(f"缺少必需字段: {field}")
                return False
        
        return True
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """错误处理"""
        self._error_count += 1
        
        error_info = {
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.error(f"智能体 {self.name} 执行错误: {error}")
        
        # 根据错误类型进行不同的处理
        if isinstance(error, ValueError):
            error_info["suggestion"] = "请检查输入数据的格式和内容"
        elif isinstance(error, TimeoutError):
            error_info["suggestion"] = "执行超时，请尝试减少数据处理量或优化算法"
        elif isinstance(error, RuntimeError):
            error_info["suggestion"] = "系统资源不足，请检查系统状态"
        else:
            error_info["suggestion"] = "未知错误，请联系技术支持"
        
        return {
            "success": False,
            "error": error_info
        }
    
    # 工具函数实现
    def _validate_data(self, data_description: str) -> str:
        """数据验证工具"""
        # 简单的数据验证逻辑
        return f"数据验证工具: 验证 '{data_description}' 的功能待实现"
    
    def _analyze_performance(self, metrics_description: str) -> str:
        """性能分析工具"""
        # 简单的性能分析逻辑
        return f"性能分析工具: 分析 '{metrics_description}' 的功能待实现"
    
    def _assess_risk(self, risk_description: str) -> str:
        """风险评估工具"""
        # 简单的风险评估逻辑
        return f"风险评估工具: 评估 '{risk_description}' 的功能待实现"


class LangChainAgent(EnhancedBaseAgent):
    """基于LangChain的智能体"""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        langchain_service: LangChainService,
        agent_type: str = "zero-shot-react-description",
        tools: List[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name=name,
            description=description,
            capabilities=capabilities,
            langchain_service=langchain_service,
            config=config
        )
        
        self.agent_type = agent_type
        self.tools = tools or []
        
        # 创建LangChain智能体
        self._create_langchain_agent()
    
    def _create_langchain_agent(self):
        """创建LangChain智能体"""
        if not self.langchain_service:
            return
        
        # 使用LangChain服务创建智能体
        self._chains["agent"] = self.langchain_service.create_agent(
            f"{self.name}_agent",
            self.tools,
            self.agent_type
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体主要逻辑"""
        if "agent" not in self._chains:
            raise RuntimeError("LangChain智能体未初始化")
        
        # 准备查询
        query = context.get("query", "")
        if not query:
            query = self._build_query_from_context(context)
        
        # 执行智能体
        result = await self.langchain_service.run_agent(f"{self.name}_agent", query)
        
        # 更新执行状态
        self._execution_count += 1
        self._last_execution = datetime.now()
        
        return {
            "success": True,
            "result": result,
            "agent": self.name,
            "execution_time": datetime.now().isoformat()
        }
    
    def _build_query_from_context(self, context: Dict[str, Any]) -> str:
        """从上下文构建查询"""
        query_parts = []
        
        if "task" in context:
            query_parts.append(f"任务: {context['task']}")
        
        if "data" in context:
            query_parts.append(f"数据: {context['data']}")
        
        if "goal" in context:
            query_parts.append(f"目标: {context['goal']}")
        
        return " ".join(query_parts) if query_parts else "请执行默认任务"


class BusinessAgent(EnhancedBaseAgent):
    """业务智能体基类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        business_domain: str,
        langchain_service: Optional[LangChainService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        capabilities = [
            AgentCapability.DATA_PROCESSING,
            AgentCapability.PREDICTION,
            AgentCapability.ANALYSIS,
            AgentCapability.RECOMMENDATION
        ]
        
        super().__init__(
            name=name,
            description=description,
            capabilities=capabilities,
            langchain_service=langchain_service,
            config=config
        )
        
        self.business_domain = business_domain
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行业务逻辑"""
        # 验证输入
        if not await self.validate_input(context):
            return await self.handle_error(
                ValueError("输入验证失败"),
                context
            )
        
        try:
            # 执行业务逻辑
            result = await self._execute_business_logic(context)
            
            # 更新执行状态
            self._execution_count += 1
            self._last_execution = datetime.now()
            
            return {
                "success": True,
                "result": result,
                "agent": self.name,
                "domain": self.business_domain,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    @abstractmethod
    async def _execute_business_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行业务逻辑（抽象方法）"""
        pass


class OperationalAgent(EnhancedBaseAgent):
    """运维智能体基类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        langchain_service: Optional[LangChainService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        capabilities = [
            AgentCapability.MONITORING,
            AgentCapability.ALERTING,
            AgentCapability.AUTOMATION
        ]
        
        super().__init__(
            name=name,
            description=description,
            capabilities=capabilities,
            execution_mode=AgentExecutionMode.SCHEDULED,
            langchain_service=langchain_service,
            config=config
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行运维逻辑"""
        try:
            # 执行监控和运维逻辑
            result = await self._execute_operational_logic(context)
            
            # 更新执行状态
            self._execution_count += 1
            self._last_execution = datetime.now()
            
            return {
                "success": True,
                "result": result,
                "agent": self.name,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    @abstractmethod
    async def _execute_operational_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行运维逻辑（抽象方法）"""
        pass