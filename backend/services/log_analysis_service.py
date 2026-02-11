"""
日志分析和性能监控服务
使用Qwen LLM提供商进行日志分析和性能监控
"""

import logging
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI  # 使用兼容OpenAI格式的模型
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

from ..services.llm_service import LLMService
from ..utils.llm_monitor import LLMUsageMonitor

logger = logging.getLogger(__name__)


class LogAnalysisService:
    """使用Qwen LLM提供商的系统日志分析服务"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.qwen_provider = llm_service.providers.get('qwen')
        if not self.qwen_provider:
            raise ValueError("Qwen提供商未注册")
        
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # 初始化嵌入模型（使用OpenAI兼容的嵌入）
        try:
            self.embeddings = OpenAIEmbeddings()
        except Exception:
            # 如果OpenAI嵌入不可用，使用简化版本
            self.embeddings = None
    
    async def analyze_logs_with_retrieval_qa(self, log_path: str, query: str = None) -> Dict[str, Any]:
        """
        使用RetrievalQA分析系统日志
        """
        if not os.path.exists(log_path):
            return {"error": f"日志文件不存在: {log_path}"}
        
        try:
            # 读取日志文件
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            if not log_content.strip():
                return {"error": "日志文件为空"}
            
            # 分割日志内容
            chunks = self.text_splitter.split_text(log_content)
            
            # 创建文档对象
            documents = [Document(page_content=chunk) for chunk in chunks]
            
            # 如果没有嵌入模型，返回分割后的日志内容
            if not self.embeddings:
                return {
                    "status": "warning",
                    "message": "嵌入模型不可用，仅返回日志内容分析",
                    "chunks_count": len(chunks),
                    "total_chars": len(log_content)
                }
            
            # 创建向量存储
            vector_store = FAISS.from_documents(documents, self.embeddings)
            
            # 创建兼容OpenAI格式的Qwen模型实例
            llm = ChatOpenAI(
                model="qwen-max",
                openai_api_key=self.qwen_provider.api_key,
                openai_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.3
            )
            
            # 创建检索QA链
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",  # 适合较短的日志内容
                retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            # 执行查询
            if not query:
                query = "分析此日志文件中的错误、警告和异常模式"
            
            result = qa_chain({"query": query})
            
            return {
                "status": "success",
                "answer": result.get("result", ""),
                "source_documents": [doc.page_content for doc in result.get("source_documents", [])],
                "log_file": log_path,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"日志分析失败: {e}")
            return {"error": f"日志分析失败: {str(e)}"}


class PerformanceMonitoringService:
    """性能监控与LangSmith数据集成服务"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.qwen_provider = llm_service.providers.get('qwen')
        if not self.qwen_provider:
            raise ValueError("Qwen提供商未注册")
        
        self.langsmith_client = None
        self._init_langsmith()
    
    def _init_langsmith(self):
        """初始化LangSmith客户端"""
        try:
            # 检查是否已设置LangSmith环境变量
            langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
            if langsmith_api_key:
                from langsmith import Client
                self.langsmith_client = Client(api_key=langsmith_api_key)
                logger.info("LangSmith客户端已初始化")
            else:
                logger.warning("未设置LANGSMITH_API_KEY环境变量，LangSmith功能将不可用")
        except ImportError:
            logger.warning("langsmith包未安装，LangSmith功能将不可用")
        except Exception as e:
            logger.error(f"LangSmith初始化失败: {e}")
    
    async def get_langsmith_performance_data(self) -> Dict[str, Any]:
        """获取LangSmith性能数据"""
        if not self.langsmith_client:
            return {
                "status": "error",
                "message": "LangSmith未配置或不可用"
            }
        
        try:
            # 获取最近的运行记录
            runs = list(self.langsmith_client.list_runs(
                limit=20,  # 限制获取的数量
                project_name=os.getenv("LANGSMITH_PROJECT", "sport-lottery-agents")
            ))
            
            # 计算基本统计
            total_runs = len(runs)
            successful_runs = sum(1 for run in runs if run.status == "success")
            failed_runs = sum(1 for run in runs if run.status == "error")
            
            # 计算平均延迟
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
                    "total_runs": total_runs,
                    "successful_runs": successful_runs,
                    "failed_runs": failed_runs,
                    "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                    "avg_latency_seconds": round(avg_latency, 2),
                    "runs": [
                        {
                            "id": run.id,
                            "name": run.name or "unnamed",
                            "status": run.status,
                            "start_time": run.start_time.isoformat() if hasattr(run, 'start_time') and run.start_time else None,
                            "end_time": run.end_time.isoformat() if hasattr(run, 'end_time') and run.end_time else None,
                            "execution_time": run.execution_time if hasattr(run, 'execution_time') else None
                        }
                        for run in runs
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"获取LangSmith数据失败: {e}")
            return {
                "status": "error",
                "message": f"获取LangSmith数据失败: {str(e)}"
            }
    
    async def analyze_performance_with_qwen(self, additional_context: str = "") -> Dict[str, Any]:
        """使用Qwen分析性能数据"""
        # 首先获取LangSmith性能数据
        perf_data = await self.get_langsmith_performance_data()
        
        if perf_data["status"] != "success":
            return perf_data
        
        try:
            # 准备性能数据摘要
            stats = perf_data["stats"]
            perf_summary = f"""
            LangSmith性能数据摘要:
            - 总运行次数: {stats['total_runs']}
            - 成功运行: {stats['successful_runs']}
            - 失败运行: {stats['failed_runs']}
            - 成功率: {stats['success_rate']:.2f}%
            - 平均延迟: {stats['avg_latency_seconds']}秒
            
            最近运行详情:
            {chr(10).join([f"- {run['name']}: {run['status']} ({run.get('execution_time', 'N/A')}s)" 
                          for run in stats['runs'][:5]])}
            """
            
            # 结合额外上下文和性能摘要，使用Qwen进行分析
            analysis_prompt = f"""
            请分析以下系统性能数据并提供见解和改进建议:
            
            {perf_summary}
            
            {additional_context}
            
            请提供:
            1. 性能趋势分析
            2. 主要瓶颈识别
            3. 具体优化建议
            4. 风险预警
            """
            
            # 调用Qwen进行分析
            analysis = self.llm_service.generate_response(
                prompt=analysis_prompt,
                provider="qwen",
                model="qwen-max",
                temperature=0.5,
                max_tokens=1000
            )
            
            return {
                "status": "success",
                "performance_summary": perf_summary,
                "qwen_analysis": analysis,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Qwen性能分析失败: {e}")
            return {
                "status": "error",
                "message": f"Qwen性能分析失败: {str(e)}"
            }


# 辅助函数，用于创建使用Qwen的分析服务
def create_log_analysis_service(llm_service: LLMService) -> LogAnalysisService:
    """创建日志分析服务实例"""
    return LogAnalysisService(llm_service)


def create_performance_monitoring_service(llm_service: LLMService) -> PerformanceMonitoringService:
    """创建性能监控服务实例"""
    return PerformanceMonitoringService(llm_service)