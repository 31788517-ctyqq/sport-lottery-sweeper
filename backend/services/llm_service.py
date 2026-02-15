import logging
import os
import time
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import requests

# 根据规范，google.generativeai已被废弃，已迁移到google.genai
import google.genai as genai
import openai
from zhipuai import ZhipuAI

from backend.utils.llm_monitor import LLMUsageMonitor

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """LLM供应商抽象基类 (更新为异步)"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass

class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI GPT系列模型 (更新为异步)"""
    
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        self.client = None
        self.monitor = monitor
        
        # 只有当API密钥非空且不是占位符时才尝试初始化
        if api_key and api_key.strip() and api_key != "your-openai-api-key-here":
            try:
                import socket
                socket.setdefaulttimeout(5)  # 设置超时避免阻塞
                
                self.client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI provider initialization failed (non-critical): {e}")
                self.client = None
        else:
            logger.info("OpenAI API key not configured, provider disabled")
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            content = response.choices[0].message.content
            
            # 计算成本并更新监控
            prompt_tokens = len(prompt.split())
            completion_tokens = len(content.split()) if content else 0
            estimated_tokens = prompt_tokens + completion_tokens
            cost = (estimated_tokens / 1000) * 0.002
            self.monitor.log_request("openai", prompt_tokens, completion_tokens, cost)
            
            response_time = time.time() - start_time
            logger.info(f"OpenAI API调用完成，耗时: {response_time:.2f}s")
            
            return content if content else ""
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
        
    def get_embeddings(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embeddings调用失败: {e}")
            return []

class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini模型 (更新为异步)"""
    
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        self.monitor = monitor
        self.model = None
        
        # 只有当API密钥非空且不是占位符时才尝试初始化
        if api_key and api_key.strip() and api_key != "your-gemini-api-key-here":
            try:
                import socket
                # 设置超时避免阻塞
                socket.setdefaulttimeout(5)
                
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini provider initialized successfully")
            except Exception as e:
                logger.warning(f"Gemini provider initialization failed (non-critical): {e}")
                # 不抛出异常，允许服务继续启动
                self.model = None
        else:
            logger.info("Gemini API key not configured, provider disabled")
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        if self.model is None:
            logger.warning("Gemini provider not initialized, returning empty response")
            return ""
            
        start_time = time.time()
        try:
            # Gemini API目前是同步的，我们用线程池来异步执行
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            def sync_generate():
                response = self.model.generate_content(prompt)
                return response.text
                
            content = await loop.run_in_executor(None, sync_generate)
            
            # 计算成本（估算）
            prompt_tokens = len(prompt.split())
            completion_tokens = len(content.split()) if content else 0
            estimated_tokens = prompt_tokens + completion_tokens
            cost = (estimated_tokens / 1000) * 0.0005
            self.monitor.log_request("gemini", prompt_tokens, completion_tokens, cost)
            
            response_time = time.time() - start_time
            logger.info(f"Gemini API调用完成，耗时: {response_time:.2f}s")
            
            return content if content else ""
        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            return ""
        
    def get_embeddings(self, text: str) -> List[float]:
        if self.model is None:
            logger.debug("Gemini provider not initialized, returning empty embeddings")
            return []
            
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="semantic_similarity"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Gemini embeddings调用失败: {e}")
            return []

class QwenLLMProvider(BaseLLMProvider):
    """阿里云通义千问模型 (更新为异步)"""
    
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        self.api_key = None
        # 使用OpenAI兼容模式API端点
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.monitor = monitor
        
        # 只有当API密钥非空且不是占位符时才接受
        if api_key and api_key.strip() and api_key != "your-qwen-api-key-here":
            self.api_key = api_key
            logger.info("Qwen provider initialized successfully")
        else:
            logger.info("Qwen API key not configured, provider disabled")
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 准备请求数据，符合OpenAI兼容模式API格式
        data = {
            "model": kwargs.get("model", "qwen-max"),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 计算成本（估算）
            prompt_tokens = len(prompt.split())
            completion_tokens = len(content.split()) if content else 0
            estimated_tokens = prompt_tokens + completion_tokens
            cost = (estimated_tokens / 1000) * 0.001
            self.monitor.log_request("qwen", prompt_tokens, completion_tokens, cost)
            
            response_time = time.time() - start_time
            logger.info(f"Qwen API调用完成，耗时: {response_time:.2f}s")
            
            return content if content else ""
        except Exception as e:
            logger.error(f"Qwen API调用失败: {e}")
            raise
        
    def get_embeddings(self, text: str) -> List[float]:
        # 通义千问Embedding API调用实现
        try:
            url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "text-embedding-v1",
                "input": {
                    "texts": [text]
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                return result['output']['embeddings'][0]['embedding']
            else:
                logger.error(f"Qwen embeddings调用失败: {result}")
                return []
        except Exception as e:
            logger.error(f"Qwen embeddings调用异常: {e}")
            return []

class ZhipuAILLMProvider(BaseLLMProvider):
    """智谱AI GLM系列模型 (更新为异步)"""
    
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        self.client = ZhipuAI(api_key=api_key)
        self.monitor = monitor
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        start_time = time.time()
        try:
            # 智谱AI API是同步的，使用线程池异步执行
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            def sync_generate():
                response = self.client.chat.completions.create(
                    model=kwargs.get("model", "glm-4"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000)
                )
                return response.choices[0].message.content
                
            content = await loop.run_in_executor(None, sync_generate)
            
            # 计算成本（估算）
            prompt_tokens = len(prompt.split())
            completion_tokens = len(content.split()) if content else 0
            estimated_tokens = prompt_tokens + completion_tokens
            cost = (estimated_tokens / 1000) * 0.0015  # 智谱AI成本估算
            self.monitor.log_request("zhipuai", prompt_tokens, completion_tokens, cost)
            
            response_time = time.time() - start_time
            logger.info(f"ZhipuAI API调用完成，耗时: {response_time:.2f}s")
            
            return content if content else ""
        except Exception as e:
            logger.error(f"ZhipuAI API调用失败: {e}")
            raise
        
    def get_embeddings(self, text: str) -> List[float]:
        # 智谱AI Embedding API调用实现
        try:
            response = self.client.embeddings.create(
                model="embedding-2",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"ZhipuAI embeddings调用失败: {e}")
            return []

class LLMService:
    """LLM服务统一接口 (更新为异步)"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.monitor = LLMUsageMonitor()
        
    def register_provider(self, name: str, api_key: str):
        """注册LLM提供商"""
        # 规范化提供商名称：将'alibaba'映射为'qwen'以保持一致性
        normalized_name = name
        if name == "alibaba":
            normalized_name = "qwen"
        elif name == "zhipuai":
            normalized_name = "zhipuai"
            
        if normalized_name == "openai":
            provider = OpenAILLMProvider(api_key, self.monitor)
        elif normalized_name == "gemini":
            provider = GeminiLLMProvider(api_key, self.monitor)
        elif normalized_name == "qwen":
            provider = QwenLLMProvider(api_key, self.monitor)
        elif normalized_name == "zhipuai":
            provider = ZhipuAILLMProvider(api_key, self.monitor)
        else:
            raise ValueError(f"Unsupported provider: {name}")
        
        self.providers[normalized_name] = provider
        logger.info(f"LLM提供商 {name} (规范化: {normalized_name}) 已注册")
        
        if self.default_provider is None:
            self.default_provider = normalized_name
            
    def set_default_provider(self, name: str):
        """设置默认提供商"""
        # 规范化提供商名称：将'alibaba'映射为'qwen'以保持一致性
        normalized_name = name
        if name == "alibaba":
            normalized_name = "qwen"
        elif name == "zhipuai":
            normalized_name = "zhipuai"
            
        if normalized_name not in self.providers:
            raise ValueError(f"Provider {name} not registered")
        self.default_provider = normalized_name
        logger.info(f"默认LLM提供商已设置为 {name} (规范化: {normalized_name})")
        
    async def generate_response(self, prompt: str, provider: str = None, **kwargs) -> str:
        """生成响应"""
        if provider is None:
            provider = self.default_provider
        
        # 规范化提供商名称：将'alibaba'映射为'qwen'以保持一致性
        normalized_provider = provider
        if provider == "alibaba":
            normalized_provider = "qwen"
        elif provider == "zhipuai":
            normalized_provider = "zhipuai"
            
        if normalized_provider not in self.providers:
            raise ValueError(f"Provider {provider} not registered")
        
        provider = normalized_provider
            
        start_time = time.time()
        try:
            response = await self.providers[provider].generate_response(prompt, **kwargs)
            response_time = time.time() - start_time
            
            logger.info(f"LLM服务响应完成，提供商: {provider}, 耗时: {response_time:.2f}s")
            return response
        except Exception as e:
            logger.error(f"LLM服务调用失败: {e}")
            raise
            
    @property
    def request_cost(self) -> float:
        """获取累计成本"""
        return sum(v.get('cost', 0) for v in self.monitor.current_daily_usage.values())
        
    def get_cost_breakdown(self) -> Dict[str, float]:
        """获取成本明细"""
        breakdown = {}
        for key, value in self.monitor.current_daily_usage.items():
            provider = key.split(':', 1)[0]
            breakdown[provider] = breakdown.get(provider, 0) + value.get('cost', 0)
        return breakdown