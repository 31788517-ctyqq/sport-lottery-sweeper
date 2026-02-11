"""
智能体管理器核心框架
基于LangChain的智能体系统管理
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from ..agents.base_agent import BaseAgent
from .langchain_service import LangChainService

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """智能体状态枚举"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    PAUSED = "paused"


class AgentType(Enum):
    """智能体类型枚举"""
    BUSINESS = "business"  # 业务智能体
    OPERATIONAL = "operational"  # 运维智能体
    DATA_PROCESSING = "data_processing"  # 数据处理智能体
    USER_SERVICE = "user_service"  # 用户服务智能体


@dataclass
class AgentMetrics:
    """智能体指标数据"""
    executions: int = 0
    errors: int = 0
    avg_response_time: float = 0.0
    total_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    success_rate: float = 100.0
    
    def update_success(self, execution_time: float):
        """更新成功执行指标"""
        self.executions += 1
        self.total_execution_time += execution_time
        self.avg_response_time = self.total_execution_time / self.executions
        self.last_execution = datetime.now()
        self.success_rate = (1 - (self.errors / self.executions)) * 100
    
    def update_error(self):
        """更新错误指标"""
        self.errors += 1
        self.last_execution = datetime.now()
        if self.executions > 0:
            self.success_rate = (1 - (self.errors / self.executions)) * 100


@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    agent_type: AgentType
    description: str = ""
    enabled: bool = True
    
    # 执行配置
    max_concurrent: int = 1
    timeout: int = 300  # 秒
    retry_count: int = 3
    retry_delay: int = 5  # 秒
    
    # 调度配置
    schedule_enabled: bool = False
    schedule_interval: int = 300  # 秒
    schedule_cron: Optional[str] = None
    
    # LangChain配置
    langchain_chain: Optional[str] = None
    langchain_tools: List[str] = field(default_factory=list)
    
    # 监控配置
    health_check_interval: int = 60  # 秒
    metrics_retention: int = 86400  # 秒（24小时）
    
    # 自定义配置
    custom_config: Dict[str, Any] = field(default_factory=dict)


class ManagedAgent:
    """托管智能体"""
    
    def __init__(self, agent_id: str, agent_instance: BaseAgent, config: AgentConfig):
        self.id = agent_id
        self.agent = agent_instance
        self.config = config
        self.status = AgentStatus.STOPPED
        self.metrics = AgentMetrics()
        self.created_at = datetime.now()
        self.last_heartbeat = None
        self.error_message: Optional[str] = None
        
        # 执行控制
        self._current_task: Optional[asyncio.Task] = None
        self._scheduled_task: Optional[asyncio.Task] = None
        self._health_check_task: Optional[asyncio.Task] = None
        
        # 线程池用于同步操作
        self._executor = ThreadPoolExecutor(max_workers=config.max_concurrent)
    
    async def start(self):
        """启动智能体"""
        if self.status in [AgentStatus.RUNNING, AgentStatus.STARTING]:
            logger.warning(f"智能体 {self.id} 已经在运行或启动中")
            return
        
        self.status = AgentStatus.STARTING
        logger.info(f"启动智能体: {self.id}")
        
        try:
            # 启动健康检查
            if self.config.health_check_interval > 0:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            # 启动调度任务
            if self.config.schedule_enabled:
                self._scheduled_task = asyncio.create_task(self._schedule_loop())
            
            self.status = AgentStatus.RUNNING
            self.last_heartbeat = datetime.now()
            logger.info(f"智能体 {self.id} 启动成功")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.error_message = str(e)
            logger.error(f"智能体 {self.id} 启动失败: {e}")
            raise
    
    async def stop(self):
        """停止智能体"""
        if self.status == AgentStatus.STOPPED:
            return
        
        self.status = AgentStatus.STOPPING
        logger.info(f"停止智能体: {self.id}")
        
        # 取消所有任务
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
        
        if self._scheduled_task:
            self._scheduled_task.cancel()
        
        if self._health_check_task:
            self._health_check_task.cancel()
        
        # 等待任务完成
        await asyncio.sleep(0.1)
        
        self.status = AgentStatus.STOPPED
        logger.info(f"智能体 {self.id} 停止成功")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体任务"""
        if self.status != AgentStatus.RUNNING:
            raise RuntimeError(f"智能体 {self.id} 未运行")
        
        start_time = datetime.now()
        
        try:
            # 检查并发限制
            if len(self._get_active_tasks()) >= self.config.max_concurrent:
                raise RuntimeError(f"智能体 {self.id} 已达到最大并发限制")
            
            # 执行任务
            self._current_task = asyncio.create_task(
                self._execute_with_timeout(context)
            )
            
            result = await self._current_task
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 更新指标
            self.metrics.update_success(execution_time)
            self.last_heartbeat = datetime.now()
            
            logger.info(f"智能体 {self.id} 执行完成，耗时: {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.update_error()
            self.error_message = str(e)
            logger.error(f"智能体 {self.id} 执行失败: {e}")
            raise
    
    async def _execute_with_timeout(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """带超时的执行"""
        try:
            return await asyncio.wait_for(
                self.agent.execute(context),
                timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"智能体执行超时 ({self.config.timeout}s)")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.status == AgentStatus.RUNNING:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                # 检查最后心跳时间
                if self.last_heartbeat:
                    time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
                    if time_since_heartbeat > self.config.health_check_interval * 2:
                        logger.warning(f"智能体 {self.id} 心跳超时")
                        self.status = AgentStatus.ERROR
                        self.error_message = "心跳超时"
                        break
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"智能体 {self.id} 健康检查失败: {e}")
    
    async def _schedule_loop(self):
        """调度循环"""
        while self.status == AgentStatus.RUNNING:
            try:
                await asyncio.sleep(self.config.schedule_interval)
                
                if self.status == AgentStatus.RUNNING:
                    # 执行调度任务
                    await self.execute({})
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"智能体 {self.id} 调度执行失败: {e}")
    
    def _get_active_tasks(self) -> List[asyncio.Task]:
        """获取活动任务列表"""
        tasks = []
        if self._current_task and not self._current_task.done():
            tasks.append(self._current_task)
        return tasks
    
    def get_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "id": self.id,
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "status": self.status.value,
            "description": self.config.description,
            "enabled": self.config.enabled,
            "metrics": {
                "executions": self.metrics.executions,
                "errors": self.metrics.errors,
                "avg_response_time": self.metrics.avg_response_time,
                "success_rate": self.metrics.success_rate,
                "last_execution": self.metrics.last_execution.isoformat() if self.metrics.last_execution else None
            },
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "error_message": self.error_message,
            "active_tasks": len(self._get_active_tasks())
        }


class AgentManager:
    """智能体管理器"""
    
    def __init__(self, langchain_service: Optional[LangChainService] = None):
        self.agents: Dict[str, ManagedAgent] = {}
        self.langchain_service = langchain_service
        
        # 消息队列用于智能体间通信
        self.message_queue = asyncio.Queue()
        
        # WebSocket连接管理
        self.websocket_connections: set = set()
        
        # 事件监听器
        self.event_listeners: Dict[str, List[Callable]] = {}
        
        logger.info("智能体管理器初始化完成")
    
    async def get_langsmith_stats(self) -> Dict[str, Any]:
        """获取LangSmith统计信息（如果启用）"""
        import os
        
        langsmith_api_key = os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")
        
        if not langsmith_api_key:
            return {
                "status": "disabled",
                "message": "LangSmith未启用，请设置LANGSMITH_API_KEY环境变量"
            }
        
        try:
            from langsmith import Client
            
            client = Client()
            project_name = os.environ.get("LANGSMITH_PROJECT") or os.environ.get("LANGCHAIN_PROJECT") or "sport-lottery-agents"
            
            # 获取最近的运行记录（限制10条）
            runs = list(client.list_runs(limit=10))
            
            # 计算基本统计
            total_runs = len(runs)
            successful_runs = sum(1 for run in runs if run.status == "success")
            failed_runs = sum(1 for run in runs if run.status == "error")
            
            # 计算平均延迟（如果有执行时间数据）
            latencies = []
            for run in runs:
                if hasattr(run, 'execution_time') and run.execution_time:
                    latencies.append(run.execution_time)
                elif hasattr(run, 'end_time') and hasattr(run, 'start_time'):
                    if run.end_time and run.start_time:
                        latencies.append((run.end_time - run.start_time).total_seconds())
            
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            
            return {
                "status": "success",
                "stats": {
                    "project": project_name,
                    "total_runs": total_runs,
                    "successful_runs": successful_runs,
                    "failed_runs": failed_runs,
                    "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                    "avg_latency_seconds": round(avg_latency, 2),
                    "recent_runs": [
                        {
                            "id": run.id,
                            "name": run.name or "unnamed",
                            "status": run.status,
                            "start_time": run.start_time.isoformat() if hasattr(run, 'start_time') and run.start_time else None,
                            "end_time": run.end_time.isoformat() if hasattr(run, 'end_time') and run.end_time else None,
                            "execution_time": run.execution_time if hasattr(run, 'execution_time') else None
                        }
                        for run in runs[:5]  # 返回最近5条运行记录
                    ]
                }
            }
            
        except ImportError:
            return {
                "status": "error",
                "message": "langsmith包未安装，请运行: pip install langsmith"
            }
        except Exception as e:
            logger.error(f"获取LangSmith统计信息失败: {e}")
            return {
                "status": "error",
                "message": f"获取LangSmith统计信息失败: {str(e)}"
            }

    async def analyze_logs(self, log_path: str = "backend/logs/app.log") -> Dict[str, Any]:
        """分析系统日志并返回结构化结果"""
        import os
        
        # 检查日志文件是否存在
        if not os.path.exists(log_path):
            return {
                "status": "error", 
                "message": f"日志文件不存在: {log_path}"
            }
        
        try:
            # 尝试导入LangChain组件，处理Windows兼容性问题
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                from langchain_community.vectorstores import FAISS
                from langchain_community.embeddings import OpenAIEmbeddings
                from langchain.chains import RetrievalQA
                from langchain.llms import OpenAI
                
                # 尝试导入TextLoader，处理pwd模块的Windows兼容性问题
                try:
                    from langchain.document_loaders import TextLoader
                    loader = TextLoader(log_path)
                    documents = loader.load()
                except ModuleNotFoundError as e:
                    if "pwd" in str(e):
                        # Windows上pwd模块不可用，使用自定义加载器
                        logger.warning("TextLoader失败（Windows pwd兼容性问题），使用自定义加载器")
                        from langchain.schema import Document
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        documents = [Document(page_content=content, metadata={"source": log_path})]
                    else:
                        raise
                        
            except ImportError as e:
                return {
                    "status": "error", 
                    "message": f"LangChain组件导入失败: {str(e)}。请确保已安装langchain和相关依赖。"
                }
            
            # 检查OpenAI API密钥
            if not os.environ.get("OPENAI_API_KEY"):
                return {
                    "status": "error",
                    "message": "OpenAI API密钥未设置。请设置OPENAI_API_KEY环境变量。"
                }
            
            # 2. 分割文本（保留日志行完整性）
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n"]  # 按行分割
            )
            texts = text_splitter.split_documents(documents)
            
            if len(texts) == 0:
                return {
                    "status": "error",
                    "message": "日志文件为空或无法解析内容。"
                }
            
            logger.info(f"日志分析: 加载了 {len(texts)} 个文本块，总字符数: {sum(len(t.page_content) for t in texts)}")
            
            # 3. 创建向量存储
            embeddings = OpenAIEmbeddings()
            db = FAISS.from_documents(texts, embeddings)
            
            # 4. 构建检索链
            qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(temperature=0),
                chain_type="map_reduce",  # 适合长文档分析
                retriever=db.as_retriever(search_kwargs={"k": 5})
            )
            
            # 示例查询
            queries = [
                "列出最近10条ERROR级别的日志",
                "统计各类错误出现的频率",
                "找出API注册失败的根本原因"
            ]
            results = {}
            for query in queries:
                try:
                    results[query] = qa_chain.run(query)
                except Exception as e:
                    results[query] = f"查询失败: {str(e)}"
            
            return {
                "status": "success", 
                "results": results,
                "metadata": {
                    "log_file": log_path,
                    "file_size": os.path.getsize(log_path),
                    "text_chunks": len(texts),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"日志分析失败: {e}", exc_info=True)
            return {
                "status": "error", 
                "message": f"日志分析失败: {str(e)}"
            }
    
    async def register_agent(self, agent_instance: BaseAgent, config: AgentConfig) -> str:
        """注册智能体"""
        agent_id = str(uuid.uuid4())
        
        managed_agent = ManagedAgent(agent_id, agent_instance, config)
        self.agents[agent_id] = managed_agent
        
        # 触发注册事件
        await self._emit_event("agent_registered", {
            "agent_id": agent_id,
            "name": config.name,
            "type": config.agent_type.value,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"智能体注册成功: {agent_id} ({config.name})")
        return agent_id
    
    async def unregister_agent(self, agent_id: str):
        """注销智能体"""
        if agent_id not in self.agents:
            raise ValueError(f"智能体 {agent_id} 不存在")
        
        agent = self.agents[agent_id]
        
        # 停止智能体
        if agent.status != AgentStatus.STOPPED:
            await agent.stop()
        
        # 从管理器中移除
        del self.agents[agent_id]
        
        # 触发注销事件
        await self._emit_event("agent_unregistered", {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"智能体注销成功: {agent_id}")
    
    async def start_agent(self, agent_id: str):
        """启动智能体"""
        if agent_id not in self.agents:
            raise ValueError(f"智能体 {agent_id} 不存在")
        
        agent = self.agents[agent_id]
        await agent.start()
        
        # 触发状态变更事件
        await self._emit_event("agent_status_changed", {
            "agent_id": agent_id,
            "status": agent.status.value,
            "timestamp": datetime.now().isoformat()
        })
    
    async def stop_agent(self, agent_id: str):
        """停止智能体"""
        if agent_id not in self.agents:
            raise ValueError(f"智能体 {agent_id} 不存在")
        
        agent = self.agents[agent_id]
        await agent.stop()
        
        # 触发状态变更事件
        await self._emit_event("agent_status_changed", {
            "agent_id": agent_id,
            "status": agent.status.value,
            "timestamp": datetime.now().isoformat()
        })
    
    async def execute_agent(self, agent_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体任务"""
        if agent_id not in self.agents:
            raise ValueError(f"智能体 {agent_id} 不存在")
        
        agent = self.agents[agent_id]
        result = await agent.execute(context)
        
        # 触发执行完成事件
        await self._emit_event("agent_execution_completed", {
            "agent_id": agent_id,
            "success": True,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体状态"""
        if agent_id not in self.agents:
            raise ValueError(f"智能体 {agent_id} 不存在")
        
        return self.agents[agent_id].get_info()
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有智能体"""
        return [agent.get_info() for agent in self.agents.values()]
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """广播消息到所有WebSocket连接"""
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件"""
        # 通知事件监听器
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    await listener(data)
                except Exception as e:
                    logger.error(f"事件监听器执行失败: {e}")
        
        # 广播到WebSocket
        await self.broadcast_message({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_event_listener(self, event_type: str, listener: Callable):
        """添加事件监听器"""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)
    
    def remove_event_listener(self, event_type: str, listener: Callable):
        """移除事件监听器"""
        if event_type in self.event_listeners:
            if listener in self.event_listeners[event_type]:
                self.event_listeners[event_type].remove(listener)
    
    async def shutdown(self):
        """关闭管理器"""
        logger.info("正在关闭智能体管理器...")
        
        # 停止所有智能体
        for agent_id in list(self.agents.keys()):
            try:
                await self.stop_agent(agent_id)
            except Exception as e:
                logger.error(f"停止智能体 {agent_id} 失败: {e}")
        
        logger.info("智能体管理器关闭完成")


# 全局管理器实例
_global_manager: Optional[AgentManager] = None


def get_agent_manager(langchain_service: Optional[LangChainService] = None) -> AgentManager:
    """获取全局智能体管理器"""
    global _global_manager
    
    if _global_manager is None:
        _global_manager = AgentManager(langchain_service)
    
    return _global_manager


def reset_agent_manager():
    """重置全局智能体管理器"""
    global _global_manager
    
    if _global_manager:
        asyncio.create_task(_global_manager.shutdown())
        _global_manager = None