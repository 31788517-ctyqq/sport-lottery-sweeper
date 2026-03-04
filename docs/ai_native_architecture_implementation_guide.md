# 体育彩票业务AI原生架构实施开发指南

## 1. 项目概述

### 1.1 实施目标
本项目旨在将综合AI原生架构方案逐步实施到现有体育彩票业务系统中，通过分阶段、可执行的技术任务，将传统AI能力与LLM技术有机融合，提升系统智能化水平。

### 1.2 当前状态分析
- **技术栈**：Python 3.11 + FastAPI + Vue3 + PostgreSQL/SQLite
- **现有AI模块**：基础预测、爬虫、对冲服务
- **系统架构**：前后端分离，支持Docker部署
- **待集成能力**：LLM服务、智能分析、预测解释器等

### 1.3 实施原则
- 保持现有功能稳定
- 渐进式引入AI能力
- 保障系统安全性
- 控制API成本

## 2. 实施路线图

### 2.1 Phase 1: LLM基础设施搭建 (Week 1-2)
- [ ] 创建LLM服务抽象层
- [ ] 集成OpenAI/Gemini/Qwen提供商
- [ ] 实现基础LLM功能测试
- [ ] 配置API密钥管理

### 2.2 Phase 2: 智能预测解释器 (Week 3)
- [ ] 开发预测结果解释器
- [ ] 集成到现有预测服务
- [ ] 实现LLM解释API
- [ ] 添加用户界面展示

### 2.3 Phase 3: 智能情报分析 (Week 4)
- [ ] 增强情报分析服务
- [ ] 集成LLM分析能力
- [ ] 实现趋势总结功能
- [ ] 添加情报分析API

### 2.4 Phase 4: 智能对话助手 (Week 5)
- [ ] 开发对话助手服务
- [ ] 实现上下文管理
- [ ] 添加对话API
- [ ] 集成到前端界面

### 2.5 Phase 5: 系统优化与监控 (Week 6)
- [ ] 实现成本监控
- [ ] 添加性能指标
- [ ] 优化API调用
- [ ] 完善错误处理

## 3. 详细技术任务

### 3.1 任务1: 创建LLM服务抽象层

**目标**: 创建统一的LLM服务层，支持多提供商

**步骤**:
1. 在`backend/services/`目录创建`llm_service.py`
2. 实现`LLMProvider`抽象基类
3. 实现主流提供商的具体实现
4. 创建统一的`LLMService`接口

**实现代码**:

```python
# backend/services/llm_service.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import logging
import time
import openai
import google.generativeai as genai
import requests
import os

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """LLM供应商抽象基类"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass
    
    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """获取嵌入向量"""
        pass

class OpenAILLM(LLMProvider):
    """OpenAI GPT系列模型"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return ""
    
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

class GeminiLLM(LLMProvider):
    """Google Gemini模型"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            return ""
    
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

class QwenLLM(LLMProvider):
    """阿里云通义千问模型"""
    
    def __init__(self, api_key: str, model: str = "qwen-max"):
        self.api_key = api_key
        self.model = model
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": {
                    "prompt": prompt
                },
                "parameters": kwargs
            }
            
            response = requests.post(self.url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                return result['output']['text']
            else:
                logger.error(f"Qwen API调用失败: {result}")
                return ""
        except Exception as e:
            logger.error(f"Qwen API调用异常: {e}")
            return ""
    
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
    """LLM服务统一接口"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.request_cost = 0  # 跟踪API调用成本
    
    def register_provider(self, name: str, provider: LLMProvider):
        """注册LLM供应商"""
        self.providers[name] = provider
        if self.default_provider is None:
            self.default_provider = name
    
    def set_default_provider(self, name: str):
        """设置默认供应商"""
        if name in self.providers:
            self.default_provider = name
    
    def generate_response(
        self, 
        prompt: str, 
        provider: Optional[str] = None, 
        **kwargs
    ) -> str:
        """生成响应"""
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            raise ValueError(f"未找到供应商: {provider_name}")
        
        start_time = time.time()
        response = self.providers[provider_name].generate_response(prompt, **kwargs)
        elapsed_time = time.time() - start_time
        
        # 记录成本和性能指标
        self._log_request(provider_name, len(prompt), len(response), elapsed_time)
        
        return response
    
    def get_embeddings(self, text: str, provider: Optional[str] = None) -> List[float]:
        """获取嵌入向量"""
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            raise ValueError(f"未找到供应商: {provider_name}")
        
        return self.providers[provider_name].get_embeddings(text)
    
    def _log_request(self, provider: str, input_tokens: int, output_tokens: int, elapsed_time: float):
        """记录请求信息用于成本跟踪"""
        # 简化的成本计算（实际应根据各服务商定价模型调整）
        cost_estimate = (input_tokens + output_tokens) * 0.00001  # 示例计算
        self.request_cost += cost_estimate
        logger.info(f"LLM请求 - Provider: {provider}, "
                   f"Input: {input_tokens} tokens, Output: {output_tokens} tokens, "
                   f"Time: {elapsed_time:.2f}s, Cost estimate: ${cost_estimate:.4f}")
```

**依赖安装**:
```bash
pip install openai google-generativeai requests
```

### 3.2 任务2: 初始化LLM服务

**目标**: 在应用启动时初始化LLM服务

**步骤**:
1. 修改`backend/main.py`，在应用启动时初始化LLM服务
2. 从环境变量加载API密钥
3. 注册可用的提供商

**实现代码**:

```python
# 在backend/main.py中添加LLM服务初始化
import os
from .services.llm_service import LLMService, OpenAILLM, GeminiLLM, QwenLLM

# 全局LLM服务实例
llm_service = LLMService()

def init_llm_service():
    """初始化LLM服务"""
    # 从环境变量获取API密钥
    api_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'gemini': os.getenv('GEMINI_API_KEY'),
        'qwen': os.getenv('QWEN_API_KEY'),
    }
    
    # 注册可用的提供商
    if api_keys['openai']:
        llm_service.register_provider('openai', OpenAILLM(api_keys['openai']))
        logger.info("OpenAI提供商已注册")
    
    if api_keys['gemini']:
        llm_service.register_provider('gemini', GeminiLLM(api_keys['gemini']))
        logger.info("Gemini提供商已注册")
    
    if api_keys['qwen']:
        llm_service.register_provider('qwen', QwenLLM(api_keys['qwen']))
        logger.info("Qwen提供商已注册")
    
    # 设置默认提供商
    if llm_service.providers:
        llm_service.set_default_provider(next(iter(llm_service.providers)))
        logger.info(f"默认LLM提供商: {llm_service.default_provider}")

# 在应用启动时调用
@app.on_event("startup")
async def startup_event():
    # ... 现有代码 ...
    init_llm_service()
    logger.info("LLM服务初始化完成")
```

### 3.3 任务3: 开发预测解释器

**目标**: 创建使用LLM解释预测结果的服务

**步骤**:
1. 创建`backend/services/prediction_explainer.py`
2. 实现解释功能
3. 集成到现有预测服务

**实现代码**:

```python
# backend/services/prediction_explainer.py
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)

class PredictionExplainer:
    """预测结果解释器 - 使用LLM提供人类可理解的解释"""
    
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
    
    def explain_prediction(self, match_id: int, prediction_result: Dict[str, Any]) -> str:
        """解释预测结果"""
        try:
            # 获取比赛相关信息
            from ..models.match import Match
            match = self.db.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return "无法获取比赛信息，无法生成解释"
            
            # 构造解释提示
            prompt = f"""
            请解释以下足球比赛的预测结果，使其易于理解：
            
            比赛信息:
            - 主队: {getattr(match, 'home_team', '未知')}
            - 客队: {getattr(match, 'away_team', '未知')}
            - 联赛: {getattr(match, 'league', '未知')}
            - 比赛时间: {match.match_date if hasattr(match, 'match_date') else '未知'}
            
            预测结果:
            - 主胜概率: {prediction_result.get('probabilities', {}).get('home_win', 0):.2%}
            - 平局概率: {prediction_result.get('probabilities', {}).get('draw', 0):.2%}
            - 客胜概率: {prediction_result.get('probabilities', {}).get('away_win', 0):.2%}
            - 预测信心: {prediction_result.get('confidence', 0):.2%}
            
            请提供以下方面的解释：
            1. 预测的主要依据
            2. 关键影响因素
            3. 预测的可信度分析
            4. 潜在不确定性因素
            5. 对投注策略的建议（如有）
            
            请注意保持客观和科学的态度，强调预测结果的不确定性。
            """
            
            explanation = self.llm_service.generate_response(
                prompt,
                provider="openai",  # 使用OpenAI作为默认解释提供商
                temperature=0.5,
                max_tokens=500
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"预测解释生成失败: {e}")
            return "预测结果解释生成失败，请稍后重试"
```

### 3.4 任务4: 创建LLM API端点

**目标**: 提供LLM功能的API接口

**步骤**:
1. 创建`backend/api/v1/llm.py`
2. 实现聊天、解释、分析等功能API
3. 注册到主路由

**实现代码**:

```python
# backend/api/v1/llm.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ...database import get_db
from ...services.llm_service import LLMService
from ...services.prediction_explainer import PredictionExplainer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])

# 从全局服务获取LLM服务实例
from ...main import llm_service

@router.post("/explain-prediction")
async def explain_prediction(
    match_id: int,
    prediction_data: Dict[str, Any],
    provider: str = "openai",
    db: Session = Depends(get_db)
):
    """解释预测结果"""
    try:
        explainer = PredictionExplainer(db, llm_service)
        explanation = explainer.explain_prediction(match_id, prediction_data)
        return {"explanation": explanation, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测解释失败: {str(e)}")

@router.get("/providers")
async def get_available_providers():
    """获取可用的LLM提供商"""
    providers = list(llm_service.providers.keys())
    return {"providers": providers, "default": llm_service.default_provider}

@router.get("/cost-metrics")
async def get_cost_metrics():
    """获取成本指标"""
    return {
        "total_cost_estimate": llm_service.request_cost,
        "providers_count": len(llm_service.providers)
    }
```

**注册到主路由**:

```python
# 在backend/api/v1/__init__.py中添加
from .llm import router as llm_router

# 在现有路由注册代码后添加
try:
    from .llm import router as llm_router
    router.include_router(llm_router, prefix="/llm", tags=["llm"])
    logger.info("API v1 - LLM 路由已注册")
except Exception as e:
    logger.error(f"API v1 - LLM 路由注册失败: {e}")
```

### 3.5 任务5: 增强情报分析服务

**目标**: 在现有情报服务中集成LLM能力

**步骤**:
1. 修改`backend/services/intelligence_service.py`
2. 添加LLM分析功能
3. 创建智能分析API

**实现代码**:

```python
# 修改backend/services/intelligence_service.py，添加LLM分析功能
from ..services.llm_service import LLMService

class IntelligenceService:
    """数据情报服务类（增强版）"""
    
    def __init__(self, db: Session):
        self.db = db
        # ... 现有初始化代码 ...
    
    def analyze_intelligence_with_llm(self, intelligence_item, llm_service: LLMService) -> Dict[str, Any]:
        """使用LLM分析情报内容"""
        try:
            # 构造分析提示
            prompt = f"""
            请分析以下体育情报信息，评估其对相关比赛的影响程度：
            
            情报类型: {intelligence_item.type}
            情报内容: {intelligence_item.content}
            情报来源: {intelligence_item.source}
            情报置信度: {intelligence_item.confidence.value}
            
            请从以下几个方面进行分析：
            1. 对比赛结果的可能影响
            2. 影响的可信度评估
            3. 关键影响因素
            4. 潜在风险提示
            
            请以JSON格式返回分析结果，包含以下字段：
            - impact_level: 影响级别 (critical/high/medium/low/minimal)
            - impact_reasoning: 影响推理
            - credibility_score: 可信度分数 (0-1)
            - key_factors: 关键因素列表
            - risk_warnings: 风险提示列表
            - overall_assessment: 总体评估
            """
            
            # 调用LLM获取分析结果
            response_text = llm_service.generate_response(
                prompt, 
                provider="openai",
                temperature=0.3,
                max_tokens=800
            )
            
            # 解析LLM返回的JSON
            import json
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # 如果LLM未返回有效JSON，使用备用分析
                analysis_result = {
                    "impact_level": "medium",
                    "impact_reasoning": "LLM分析结果解析失败，使用备用评估",
                    "credibility_score": 0.5,
                    "key_factors": ["解析失败"],
                    "risk_warnings": ["需人工核实"],
                    "overall_assessment": "需进一步验证"
                }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"LLM情报分析失败: {e}")
            # 返回基于规则的分析作为备选
            return self._rule_based_intelligence_analysis(intelligence_item)
```

### 3.6 任务6: 实现对话助手

**目标**: 创建智能对话助手服务

**步骤**:
1. 创建`backend/services/conversation_agent.py`
2. 实现对话管理功能
3. 添加对话API端点

**实现代码**:

```python
# backend/services/conversation_agent.py
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConversationAgent:
    """智能对话助手 - 为用户提供自然语言交互"""
    
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
        self.context_history = {}  # 存储对话历史
    
    def respond_to_user(self, user_input: str, user_id: str = "default") -> str:
        """响应用户输入"""
        try:
            # 获取用户对话历史
            history = self.context_history.get(user_id, [])
            
            # 构造提示，包含上下文信息
            context_prompt = f"""
            你是体育彩票智能助手，专门协助用户了解彩票数据、分析和预测。
            请根据用户的问题提供专业、准确的回答。
            
            当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            请遵循以下原则：
            1. 提供准确的信息
            2. 对于预测结果，强调不确定性
            3. 鼓励理性购彩
            4. 如涉及具体数据，请说明数据来源和时效性
            
            历史对话:
            {self._format_history(history)}
            
            用户问题: {user_input}
            
            请提供专业、友好且信息丰富的回复。
            """
            
            response = self.llm_service.generate_response(
                context_prompt,
                provider="qwen",  # 对话场景使用通义千问
                temperature=0.7,
                max_tokens=400
            )
            
            # 更新对话历史
            self._update_history(user_id, user_input, response)
            
            return response
            
        except Exception as e:
            logger.error(f"对话助手响应失败: {e}")
            return "抱歉，我现在遇到了一些技术问题，请稍后再试。"
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        if not history:
            return "无历史对话"
        
        formatted = []
        for item in history[-5:]:  # 只保留最近5次对话
            formatted.append(f"用户: {item['user_input']}")
            formatted.append(f"助手: {item['response']}")
        
        return "\n".join(formatted)
    
    def _update_history(self, user_id: str, user_input: str, response: str):
        """更新对话历史"""
        if user_id not in self.context_history:
            self.context_history[user_id] = []
        
        self.context_history[user_id].append({
            "user_input": user_input,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(self.context_history[user_id]) > 10:
            self.context_history[user_id] = self.context_history[user_id][-10:]
```

**添加对话API**:

```python
# 在backend/api/v1/llm.py中添加
@router.post("/chat")
async def chat_with_assistant(
    user_input: str,
    user_id: str = "default",
    provider: str = "qwen",
    db: Session = Depends(get_db)
):
    """与智能助手对话"""
    try:
        from ...services.conversation_agent import ConversationAgent
        agent = ConversationAgent(db, llm_service)
        response = agent.respond_to_user(user_input, user_id)
        return {"response": response, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")
```

### 3.7 任务7: 添加成本监控

**目标**: 实现LLM使用成本监控

**步骤**:
1. 创建监控工具类
2. 集成到LLM服务
3. 添加监控API

**实现代码**:

```python
# backend/utils/llm_monitor.py
import time
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LLMUsageMonitor:
    """LLM使用监控器"""
    
    def __init__(self):
        self.requests_log = []
        self.provider_costs = {}  # 各提供商的成本模型
        self.daily_limits = {}    # 每日使用限额
        self.current_daily_usage = {}  # 当前每日使用量
    
    def log_request(self, provider: str, input_tokens: int, output_tokens: int, cost: float):
        """记录请求"""
        request_info = {
            'timestamp': datetime.now(),
            'provider': provider,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        }
        self.requests_log.append(request_info)
        
        # 更新当日使用量
        today = datetime.now().date()
        key = f"{provider}:{today}"
        if key not in self.current_daily_usage:
            self.current_daily_usage[key] = {'tokens': 0, 'cost': 0}
        
        self.current_daily_usage[key]['tokens'] += (input_tokens + output_tokens)
        self.current_daily_usage[key]['cost'] += cost
    
    def is_within_daily_limit(self, provider: str) -> bool:
        """检查是否超出每日限额"""
        today = datetime.now().date()
        key = f"{provider}:{today}"
        
        current_usage = self.current_daily_usage.get(key, {'cost': 0})
        daily_limit = self.daily_limits.get(provider, float('inf'))
        
        return current_usage['cost'] <= daily_limit
    
    def get_daily_usage(self, provider: str, date: datetime.date = None) -> Dict[str, any]:
        """获取某日使用情况"""
        if date is None:
            date = datetime.now().date()
        
        key = f"{provider}:{date}"
        return self.current_daily_usage.get(key, {'tokens': 0, 'cost': 0})
    
    def get_cost_estimate(self, provider: str, input_tokens: int, output_tokens: int) -> float:
        """估算请求成本"""
        cost_model = self.provider_costs.get(provider)
        if not cost_model:
            # 默认成本模型（示例）
            return (input_tokens * 0.00001) + (output_tokens * 0.00001)
        
        input_cost = (input_tokens / 1000) * cost_model['input_price_per_1k']
        output_cost = (output_tokens / 1000) * cost_model['output_price_per_1k']
        return input_cost + output_cost
```

### 3.8 任务8: 环境配置和部署

**目标**: 配置环境变量和部署选项

**步骤**:
1. 创建环境变量配置文件
2. 更新Docker配置
3. 添加启动脚本

**实现代码**:

```bash
# 创建.env.llm示例文件
# .env.llm
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
QWEN_API_KEY=your_qwen_api_key_here

# LLM Settings
DEFAULT_LLM_PROVIDER=qwen
LLM_REQUEST_TIMEOUT=30
LLM_MAX_RETRIES=3
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600
```

## 4. 测试验证

### 4.1 单元测试

为新增功能编写单元测试：

```python
# tests/unit/test_llm_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.llm_service import LLMService

class TestLLMService:
    
    def test_register_provider(self):
        """测试注册提供商"""
        llm_service = LLMService()
        mock_provider = Mock()
        
        llm_service.register_provider("test_provider", mock_provider)
        
        assert "test_provider" in llm_service.providers
        assert llm_service.providers["test_provider"] == mock_provider
    
    def test_generate_response_with_provider(self):
        """测试使用特定提供商生成响应"""
        llm_service = LLMService()
        mock_provider = Mock()
        mock_provider.generate_response.return_value = "Mock response"
        
        llm_service.register_provider("mock_provider", mock_provider)
        
        response = llm_service.generate_response(
            "Test prompt", 
            provider="mock_provider",
            temperature=0.7
        )
        
        assert response == "Mock response"
        mock_provider.generate_response.assert_called_once_with(
            "Test prompt", 
            temperature=0.7
        )
```

### 4.2 集成测试

```python
# tests/integration/test_llm_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_llm_explain_prediction(client):
    """测试LLM预测解释API"""
    response = client.post(
        "/api/v1/llm/explain-prediction",
        params={
            "match_id": 1,
            "provider": "openai"
        },
        json={
            "probabilities": {
                "home_win": 0.4,
                "draw": 0.3,
                "away_win": 0.3
            },
            "confidence": 0.75
        }
    )
    
    # 检查是否成功或返回适当的错误（如果没有API密钥）
    assert response.status_code in [200, 500]
```

## 5. 部署和上线

### 5.1 Docker部署配置

更新Docker配置以支持LLM功能：

```yaml
# docker-compose.llm.yml
version: '3.8'

services:
  backend-llm:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./sport_lottery.db}
      
      # LLM API Keys
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QWEN_API_KEY=${QWEN_API_KEY}
      
      # LLM Settings
      - DEFAULT_LLM_PROVIDER=${DEFAULT_LLM_PROVIDER:-qwen}
      - LLM_REQUEST_TIMEOUT=${LLM_REQUEST_TIMEOUT:-30}
    volumes:
      - ./logs:/app/logs
    depends_on:
      - db
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### 5.2 启动脚本

创建启动脚本以简化部署：

```bash
#!/bin/bash
# scripts/start-with-llm.sh

echo "启动支持LLM功能的体育彩票系统..."

# 检查必需的环境变量
if [ -z "$OPENAI_API_KEY" ] && [ -z "$GEMINI_API_KEY" ] && [ -z "$QWEN_API_KEY" ]; then
    echo "警告: 未设置任何LLM API密钥，LLM功能将不可用"
fi

# 启动后端服务
echo "启动后端服务..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

echo "服务启动完成!"
```

## 6. 监控和维护

### 6.1 监控指标

- API调用频率
- 成本消耗
- 响应时间
- 错误率

### 6.2 日志记录

确保所有LLM调用都被适当记录，包括:

- 请求内容（脱敏处理）
- 响应时间
- 成本估算
- 错误信息

## 7. 安全考虑

- API密钥安全存储
- 输入内容过滤
- 输出内容审核
- 访问频率限制

## 8. 总结

本实施指南提供了完整的步骤，将AI原生架构逐步集成到现有系统中。通过分阶段实施，可以在不影响现有功能的情况下，逐步增强系统的AI能力。每个任务都有明确的目标和实现步骤，确保开发过程可控且可验证。