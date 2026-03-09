"""
LangChain服务封装层
兼容现有LLMService，提供LangChain接口支持
"""

import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import asyncio

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain, RetrievalQA
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .llm_service import LLMService, BaseLLMProvider

logger = logging.getLogger(__name__)


class LangChainWrapperLLM(ABC):
    """LangChain LLM包装器抽象基类"""
    
    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> str:
        """同步调用LLM"""
        pass
    
    @abstractmethod
    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """异步调用LLM"""
        pass


class LLMServiceWrapper(LangChainWrapperLLM):
    """将现有LLMService包装为LangChain兼容的LLM"""
    
    def __init__(self, llm_service: LLMService, provider_name: str = None):
        self.llm_service = llm_service
        self.provider_name = provider_name or llm_service.default_provider
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """同步调用（通过异步包装）"""
        return asyncio.run(self.ainvoke(prompt, **kwargs))
    
    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """异步调用LLMService"""
        try:
            response = await self.llm_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"LangChain LLM调用失败: {e}")
            raise


class LangChainService:
    """LangChain服务主类"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.llm_wrapper = LLMServiceWrapper(llm_service)
        self.chains: Dict[str, Any] = {}
        self.tools: Dict[str, Tool] = {}
        self.memory = ConversationBufferMemory()
        
        # 初始化基础工具
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """初始化默认工具"""
        # 数据查询工具
        self.tools["data_query"] = Tool(
            name="DataQuery",
            func=self._query_data,
            description="查询比赛数据、赔率信息等"
        )
        
        # 数据分析工具
        self.tools["data_analysis"] = Tool(
            name="DataAnalysis",
            func=self._analyze_data,
            description="分析比赛数据，生成统计报告"
        )
        
        # 系统状态检查工具
        self.tools["system_status"] = Tool(
            name="SystemStatus",
            func=self._check_system_status,
            description="检查系统运行状态和健康度"
        )
    
    def create_simple_chain(self, chain_name: str, template: str, **kwargs) -> LLMChain:
        """创建简单LLM链"""
        prompt = PromptTemplate(
            input_variables=kwargs.get("input_variables", ["input"]),
            template=template
        )
        
        chain = LLMChain(
            llm=self.llm_wrapper,
            prompt=prompt,
            output_key=kwargs.get("output_key", "output")
        )
        
        self.chains[chain_name] = chain
        logger.info(f"创建LangChain链: {chain_name}")
        return chain
    
    def create_sequential_chain(self, chain_name: str, chains_config: List[Dict]) -> SequentialChain:
        """创建顺序链"""
        chains = []
        input_variables = set()
        
        for config in chains_config:
            chain = self.create_simple_chain(
                f"{chain_name}_{config['name']}",
                config["template"],
                input_variables=config.get("input_variables"),
                output_key=config.get("output_key")
            )
            chains.append(chain)
            
            if config.get("input_variables"):
                input_variables.update(config["input_variables"])
        
        sequential_chain = SequentialChain(
            chains=chains,
            input_variables=list(input_variables),
            output_variables=[chain.output_key for chain in chains],
            verbose=True
        )
        
        self.chains[chain_name] = sequential_chain
        logger.info(f"创建顺序链: {chain_name}")
        return sequential_chain
    
    def create_agent(self, agent_name: str, tools: List[str], agent_type: str = "zero-shot-react-description") -> Any:
        """创建智能体"""
        available_tools = [self.tools[tool] for tool in tools if tool in self.tools]
        
        if not available_tools:
            raise ValueError(f"没有找到可用的工具: {tools}")
        
        agent = initialize_agent(
            tools=available_tools,
            llm=self.llm_wrapper,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )
        
        self.chains[agent_name] = agent
        logger.info(f"创建智能体: {agent_name}")
        return agent
    
    async def run_chain(self, chain_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """运行指定链"""
        if chain_name not in self.chains:
            raise ValueError(f"链 {chain_name} 不存在")
        
        chain = self.chains[chain_name]
        
        try:
            if hasattr(chain, 'arun'):
                result = await chain.arun(inputs)
            else:
                result = chain.run(inputs)
            
            logger.info(f"链 {chain_name} 执行完成")
            return {"success": True, "result": result, "chain": chain_name}
            
        except Exception as e:
            logger.error(f"链 {chain_name} 执行失败: {e}")
            return {"success": False, "error": str(e), "chain": chain_name}
    
    async def run_agent(self, agent_name: str, query: str) -> Dict[str, Any]:
        """运行智能体"""
        if agent_name not in self.chains:
            raise ValueError(f"智能体 {agent_name} 不存在")
        
        agent = self.chains[agent_name]
        
        try:
            if hasattr(agent, 'arun'):
                result = await agent.arun(query)
            else:
                result = agent.run(query)
            
            logger.info(f"智能体 {agent_name} 执行完成")
            return {"success": True, "result": result, "agent": agent_name}
            
        except Exception as e:
            logger.error(f"智能体 {agent_name} 执行失败: {e}")
            return {"success": False, "error": str(e), "agent": agent_name}
    
    # 工具函数实现
    def _query_data(self, query: str) -> str:
        """数据查询工具"""
        # TODO: 实现具体的数据查询逻辑
        return f"数据查询工具: 查询 '{query}' 的功能待实现"
    
    def _analyze_data(self, data_description: str) -> str:
        """数据分析工具"""
        # TODO: 实现具体的数据分析逻辑
        return f"数据分析工具: 分析 '{data_description}' 的功能待实现"
    
    def _check_system_status(self, _: str = "") -> str:
        """系统状态检查工具"""
        # TODO: 实现具体的系统状态检查逻辑
        return "系统状态检查工具: 系统状态检查功能待实现"
    
    def get_chain_info(self) -> Dict[str, Any]:
        """获取所有链的信息"""
        return {
            "chains": list(self.chains.keys()),
            "tools": list(self.tools.keys()),
            "memory_size": len(self.memory.chat_memory.messages) if self.memory.chat_memory else 0
        }


# 预定义的链模板
CHAIN_TEMPLATES = {
    "prediction_analysis": {
        "name": "预测分析链",
        "template": """基于以下比赛数据，分析平局概率：
比赛信息：{match_info}
历史数据：{historical_data}

请提供详细的概率分析和理由：""",
        "input_variables": ["match_info", "historical_data"]
    },
    "risk_assessment": {
        "name": "风险评估链", 
        "template": """评估以下投注策略的风险：
策略：{strategy}
市场条件：{market_conditions}

请分析潜在风险和回报：""",
        "input_variables": ["strategy", "market_conditions"]
    },
    "log_analysis": {
        "name": "日志分析链",
        "template": """分析以下系统日志，识别潜在问题：
日志内容：{log_content}

请提供分析结果和建议：""",
        "input_variables": ["log_content"]
    }
}


def create_preset_chain(langchain_service: LangChainService, template_name: str, chain_name: str = None) -> LLMChain:
    """创建预设链"""
    if template_name not in CHAIN_TEMPLATES:
        raise ValueError(f"预设模板 {template_name} 不存在")
    
    template = CHAIN_TEMPLATES[template_name]
    chain_name = chain_name or template_name
    
    return langchain_service.create_simple_chain(
        chain_name=chain_name,
        template=template["template"],
        input_variables=template["input_variables"]
    )