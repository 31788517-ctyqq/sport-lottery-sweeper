from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import time
import openai
import asyncio
import warnings
import requests
import json

# 根据规范，google.generativeai已被废弃，应使用google.genai
warnings.warn(
    "google.generativeai has been deprecated. Please migrate to google.genai when available.",
    DeprecationWarning
)
import google.generativeai as genai

from ..utils.llm_monitor import LLMUsageMonitor

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """LLM供应商抽象基类 (更新为异步)"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass

class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI GPT系列模型 (更新为异步)"""
    
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
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
    
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.monitor = monitor
        
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
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
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
            raise
            
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.monitor = monitor
        
    def get_embeddings(self, text: str) -> List[float]:
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
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
    async def generate_response(self, prompt: str, **kwargs) -> str:
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", "qwen-max"),
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": kwargs.get("temperature", 0.7)
            }
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result["output"]["text"]
            
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
            
    def __init__(self, api_key: str, monitor: LLMUsageMonitor):
        self.api_key = api_key
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.monitor = monitor
        
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

class LLMService:
    """LLM服务统一接口 (更新为异步)"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.monitor = LLMUsageMonitor()
        
    def register_provider(self, name: str, api_key: str):
        """注册LLM提供商"""
        if name == "openai":
            provider = OpenAILLMProvider(api_key, self.monitor)
        elif name == "gemini":
            provider = GeminiLLMProvider(api_key, self.monitor)
        elif name == "qwen":
            provider = QwenLLMProvider(api_key, self.monitor)
        else:
            raise ValueError(f"Unsupported provider: {name}")
        
        self.providers[name] = provider
        logger.info(f"LLM提供商 {name} 已注册")
        
        if self.default_provider is None:
            self.default_provider = name
            
    def set_default_provider(self, name: str):
        """设置默认提供商"""
        if name not in self.providers:
            raise ValueError(f"Provider {name} not registered")
        self.default_provider = name
        logger.info(f"默认LLM提供商已设置为 {name}")
        
    async def generate_response(self, prompt: str, provider: str = None, **kwargs) -> str:
        """生成响应"""
        if provider is None:
            provider = self.default_provider
            
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not registered")
            
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
        return self.cost_tracker.total_cost
        
    def get_cost_breakdown(self) -> Dict[str, float]:
        """获取成本明细"""
        return self.cost_tracker.get_provider_costs()