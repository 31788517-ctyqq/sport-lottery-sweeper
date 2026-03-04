# 体育彩票业务LLM集成架构设计文档

## 1. 项目概述

### 1.1 LLM集成背景
随着大语言模型（LLM）技术的快速发展，GPT、Gemini、DeepSeek、千问、豆包等先进模型为体育彩票业务带来了新的机遇。本项目旨在将这些LLM技术融入现有AI原生架构，利用其强大的自然语言理解、推理和生成能力，进一步提升业务智能化水平。

### 1.2 集成目标
- **智能对话系统**：实现自然语言交互的客服和咨询功能
- **文本分析能力**：利用LLM强大的NLP能力分析比赛评论、新闻等非结构化数据
- **智能决策支持**：利用LLM的推理能力辅助制定策略
- **自动化内容生成**：生成分析报告、预测解释等

## 2. LLM集成架构设计

### 2.1 整体架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面层     │    │   API网关层     │    │   业务逻辑层     │
│  (Vue3 + TS)   │◄──►│  (FastAPI)     │◄──►│   AI服务层      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据存储层     │    │   任务调度层     │    │   LLM服务层     │
│ (PostgreSQL/    │◄──►│  (Celery/RQ)   │◄──►│  (OpenAI API/   │
│   SQLite)      │    │                 │    │   Gemini API/   │
└─────────────────┘    └─────────────────┘    │   Qwen API等)   │
                                              └─────────────────┘
```

### 2.2 LLM服务层设计
- **统一LLM接口**：抽象不同供应商的API差异
- **模型选择策略**：根据任务类型选择最适合的LLM
- **成本控制机制**：监控API调用成本，优化使用效率
- **缓存机制**：缓存常见查询结果，减少API调用

## 3. LLM集成模块设计

### 3.1 LLM抽象服务层

创建`backend/services/llm_service.py`：

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import logging
import time
import openai
import google.generativeai as genai
from zhipuai import ZhipuAI
import requests

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

class DeepSeekLLM(LLMProvider):
    """DeepSeek模型"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"DeepSeek API调用失败: {result}")
                return ""
        except Exception as e:
            logger.error(f"DeepSeek API调用异常: {e}")
            return ""
    
    def get_embeddings(self, text: str) -> List[float]:
        # DeepSeek目前可能不支持embeddings，返回空列表
        logger.warning("DeepSeek目前可能不支持embeddings功能")
        return []

class DoubaoLLM(LLMProvider):
    """字节跳动豆包模型"""
    
    def __init__(self, api_key: str, model: str = "doubao-pro"):
        self.api_key = api_key
        self.model = model
        # 豆包API的具体实现可能需要根据官方文档调整
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        # 豆包API调用实现 - 这里是示意代码，实际需根据官方API文档实现
        try:
            # 实现豆包API调用逻辑
            logger.info(f"调用豆包模型: {self.model}")
            # 返回模拟响应，实际应调用豆包API
            return f"豆包模型 {self.model} 对输入 '{prompt[:20]}...' 的响应"
        except Exception as e:
            logger.error(f"Doubao API调用异常: {e}")
            return ""
    
    def get_embeddings(self, text: str) -> List[float]:
        # 豆包embeddings实现
        logger.warning("豆包embeddings功能实现待补充")
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

### 3.2 智能情报分析集成

在`backend/services/intelligence_service.py`中增强LLM能力：

```python
from ..services.llm_service import LLMService

class AIIntelligenceService:
    """AI增强型数据情报服务类（集成LLM能力）"""
    
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.text_pipeline = self._initialize_text_analyzer()
        self.llm_service = llm_service  # 集成LLM服务
    
    def analyze_intelligence_with_llm(self, intelligence_item: Intelligence) -> Dict[str, Any]:
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
            response_text = self.llm_service.generate_response(
                prompt, 
                provider="openai",  # 可根据需要选择不同的提供商
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
    
    def summarize_intelligence_trends(self, days: int = 7) -> str:
        """使用LLM总结情报趋势"""
        try:
            # 获取最近几天的情报数据
            from datetime import datetime, timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            intelligence_list = self.db.query(Intelligence).filter(
                Intelligence.created_at >= start_date
            ).all()
            
            if not intelligence_list:
                return "近期无情报数据"
            
            # 构造总结提示
            intelligence_summary = "\n".join([
                f"- 类型: {item.type}, 内容: {item.content[:100]}..."
                for item in intelligence_list[:10]  # 限制数量避免提示太长
            ])
            
            prompt = f"""
            以下是过去{days}天的体育情报汇总，请分析其中的趋势和模式：
            
            {intelligence_summary}
            
            请提供以下方面的总结：
            1. 主要情报类型分布
            2. 显著趋势或模式
            3. 潜在影响较大的情报
            4. 需要关注的风险点
            5. 对未来比赛的预测意义
            
            请以简洁明了的方式呈现分析结果。
            """
            
            response = self.llm_service.generate_response(
                prompt,
                provider="gemini",
                temperature=0.4,
                max_tokens=600
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM情报趋势总结失败: {e}")
            return f"情报趋势总结失败: {e}"
    
    def _rule_based_intelligence_analysis(self, intelligence_item: Intelligence) -> Dict[str, Any]:
        """基于规则的情报分析（备选方案）"""
        # 使用之前的分析逻辑
        basic_analysis = self.analyze_intelligence_impact(intelligence_item)
        
        return {
            "impact_level": basic_analysis["significance_level"],
            "impact_reasoning": f"基于{intelligence_item.type}类型的规则分析",
            "credibility_score": 0.6,  # 默认可信度
            "key_factors": [intelligence_item.type],
            "risk_warnings": ["建议结合其他信息验证"],
            "overall_assessment": "需要进一步分析"
        }
```

### 3.3 智能预测解释器

创建`backend/services/prediction_explainer.py`：

```python
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService

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
                provider="openai",
                temperature=0.5,
                max_tokens=500
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"预测解释生成失败: {e}")
            return "预测结果解释生成失败，请稍后重试"
    
    def compare_models_explanation(self, match_id: int, model_results: Dict[str, Any]) -> str:
        """比较不同模型的预测结果并解释差异"""
        try:
            prompt = f"""
            以下是针对同一场比赛的不同AI模型的预测结果，请分析它们的差异和原因：
            
            模型预测结果:
            {str(model_results)}
            
            请提供以下方面的分析：
            1. 各模型预测结果的异同点
            2. 可能导致差异的因素
            3. 各模型的优势和局限性
            4. 综合判断和建议
            
            请以专业且易懂的语言进行分析。
            """
            
            explanation = self.llm_service.generate_response(
                prompt,
                provider="gemini",
                temperature=0.4,
                max_tokens=600
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"模型比较解释生成失败: {e}")
            return "模型比较解释生成失败"
```

### 3.4 智能对话助手

创建`backend/services/conversation_agent.py`：

```python
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..services.llm_service import LLMService

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
    
    def get_match_analysis(self, team1: str, team2: str) -> str:
        """获取比赛分析"""
        try:
            prompt = f"""
            请对 {team1} vs {team2} 的比赛进行专业分析，包括：
            1. 两队实力对比
            2. 历史交锋记录
            3. 近期状态分析
            4. 关键球员情况
            5. 战术风格对比
            6. 比赛预测（强调不确定性）
            
            请提供专业且平衡的分析。
            """
            
            response = self.llm_service.generate_response(
                prompt,
                provider="openai",
                temperature=0.6,
                max_tokens=800
            )
            
            return response
            
        except Exception as e:
            logger.error(f"比赛分析生成失败: {e}")
            return f"无法生成 {team1} vs {team2} 的分析，请稍后重试"
```

## 4. LLM集成API设计

### 4.1 LLM服务API

在`backend/api/v1/llm.py`中创建API：

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ...database import get_db
from ...services.llm_service import LLMService
from ...services.conversation_agent import ConversationAgent
from ...services.prediction_explainer import PredictionExplainer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])

# 全局LLM服务实例（在实际应用中应通过依赖注入管理）
llm_service = LLMService()

# 初始化各种LLM提供商（从环境变量获取API密钥）
import os
api_keys = {
    'openai': os.getenv('OPENAI_API_KEY'),
    'gemini': os.getenv('GEMINI_API_KEY'),
    'qwen': os.getenv('QWEN_API_KEY'),
    'deepseek': os.getenv('DEEPSEEK_API_KEY'),
    'doubao': os.getenv('DOUBAO_API_KEY')
}

# 注册提供商
if api_keys['openai']:
    from ...services.llm_service import OpenAILLM
    llm_service.register_provider('openai', OpenAILLM(api_keys['openai']))
    
if api_keys['gemini']:
    from ...services.llm_service import GeminiLLM
    llm_service.register_provider('gemini', GeminiLLM(api_keys['gemini']))
    
if api_keys['qwen']:
    from ...services.llm_service import QwenLLM
    llm_service.register_provider('qwen', QwenLLM(api_keys['qwen']))

@router.post("/chat")
async def chat_with_assistant(
    request: Request,
    user_input: str,
    user_id: str = "default",
    provider: str = "qwen",
    db: Session = Depends(get_db)
):
    """与智能助手对话"""
    try:
        agent = ConversationAgent(db, llm_service)
        response = agent.respond_to_user(user_input, user_id)
        return {"response": response, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")

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

@router.post("/analyze-intelligence")
async def analyze_intelligence_with_llm(
    intelligence_id: int,
    provider: str = "gemini",
    db: Session = Depends(get_db)
):
    """使用LLM分析情报"""
    try:
        from ...models.intelligence import Intelligence
        intelligence_item = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
        
        if not intelligence_item:
            raise HTTPException(status_code=404, detail="情报项未找到")
        
        from ...services.intelligence_service import AIIntelligenceService
        service = AIIntelligenceService(db, llm_service)
        analysis = service.analyze_intelligence_with_llm(intelligence_item)
        
        return {"analysis": analysis, "provider": provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情报分析失败: {str(e)}")

@router.get("/providers")
async def get_available_providers():
    """获取可用的LLM提供商"""
    providers = list(llm_service.providers.keys())
    return {"providers": providers, "default": llm_service.default_provider}
```

### 4.2 集成到主API路由器

在`backend/api/v1/__init__.py`中添加LLM路由：

```python
# ... existing imports ...
from .llm import router as llm_router  # 添加LLM路由导入


# 在API v1路由器注册LLM路由
try:
    from .llm import router as llm_router
    router.include_router(llm_router, prefix="/llm", tags=["llm"])
    logger.info("API v1 - LLM 路由已注册")
except Exception as e:
    logger.error(f"API v1 - LLM 路由注册失败: {e}")
```

## 5. 配置和部署

### 5.1 环境变量配置

创建`.env.llm`文件：

```bash
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
QWEN_API_KEY=your_qwen_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DOUBAO_API_KEY=your_doubao_api_key_here

# LLM Settings
DEFAULT_LLM_PROVIDER=qwen
LLM_REQUEST_TIMEOUT=30
LLM_MAX_RETRIES=3
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600
```

### 5.2 Docker配置增强

在`docker-compose.yml`中添加LLM相关配置：

```yaml
version: '3.8'

services:
  backend-llm:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./sport_lottery.db}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
      
      # LLM API Keys
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QWEN_API_KEY=${QWEN_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - DOUBAO_API_KEY=${DOUBAO_API_KEY}
      
      # LLM Settings
      - DEFAULT_LLM_PROVIDER=${DEFAULT_LLM_PROVIDER:-qwen}
      - LLM_REQUEST_TIMEOUT=${LLM_REQUEST_TIMEOUT:-30}
      - LLM_MAX_RETRIES=${LLM_MAX_RETRIES:-3}
      - LLM_CACHE_ENABLED=${LLM_CACHE_ENABLED:-true}
      - LLM_CACHE_TTL=${LLM_CACHE_TTL:-3600}
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'
```

## 6. 成本控制和性能优化

### 6.1 LLM使用监控

创建`backend/utils/llm_monitor.py`：

```python
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

### 6.2 智能缓存机制

创建`backend/utils/llm_cache.py`：

```python
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis
import logging

logger = logging.getLogger(__name__)

class LLMCache:
    """LLM响应缓存"""
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def _generate_key(self, prompt: str, provider: str, **kwargs) -> str:
        """生成缓存键"""
        cache_input = {
            'prompt': prompt,
            'provider': provider,
            'params': kwargs
        }
        cache_str = json.dumps(cache_input, sort_keys=True)
        hash_obj = hashlib.sha256(cache_str.encode('utf-8'))
        return f"llm_cache:{hash_obj.hexdigest()}"
    
    def get(self, prompt: str, provider: str = "default", **kwargs) -> Optional[str]:
        """获取缓存的响应"""
        try:
            key = self._generate_key(prompt, provider, **kwargs)
            cached_response = self.redis.get(key)
            if cached_response:
                logger.info(f"命中LLM缓存: {key[:16]}...")
                return cached_response.decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"获取LLM缓存失败: {e}")
            return None
    
    def set(self, prompt: str, response: str, provider: str = "default", 
            ttl: Optional[int] = None, **kwargs):
        """设置缓存"""
        try:
            key = self._generate_key(prompt, provider, **kwargs)
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, response.encode('utf-8'))
            logger.info(f"设置LLM缓存: {key[:16]}..., TTL: {ttl}s")
        except Exception as e:
            logger.error(f"设置LLM缓存失败: {e}")
    
    def invalidate(self, prompt: str, provider: str = "default", **kwargs):
        """清除特定缓存"""
        try:
            key = self._generate_key(prompt, provider, **kwargs)
            self.redis.delete(key)
            logger.info(f"清除LLM缓存: {key}")
        except Exception as e:
            logger.error(f"清除LLM缓存失败: {e}")
```

## 7. 测试策略

### 7.1 LLM服务测试

创建`tests/unit/test_llm_service.py`：

```python
import pytest
from unittest.mock import Mock, patch
from backend.services.llm_service import LLMService, OpenAILLM

class TestLLMService:
    
    def test_register_provider(self):
        """测试注册提供商"""
        llm_service = LLMService()
        mock_provider = Mock()
        
        llm_service.register_provider("test_provider", mock_provider)
        
        assert "test_provider" in llm_service.providers
        assert llm_service.providers["test_provider"] == mock_provider
    
    @patch('backend.services.llm_service.openai.OpenAI')
    def test_openai_provider(self, mock_openai_client):
        """测试OpenAI提供商"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_openai_instance = Mock()
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance
        
        provider = OpenAILLM("test-key", "gpt-3.5-turbo")
        response = provider.generate_response("Hello")
        
        assert response == "Test response"
        mock_openai_instance.chat.completions.create.assert_called_once()
    
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

## 8. 总结

本架构设计文档详细描述了如何将主流的大语言模型（GPT、Gemini、千问、DeepSeek、豆包等）集成到体育彩票业务的AI原生架构中。通过以下关键设计：

1. **统一LLM接口**：抽象不同提供商的API差异，实现灵活切换
2. **智能情报分析**：利用LLM的NLP能力深度分析非结构化情报数据
3. **预测结果解释**：使用LLM生成人类可理解的预测解释
4. **智能对话助手**：提供自然语言交互界面
5. **成本控制机制**：监控和控制API调用成本
6. **缓存优化**：减少重复请求，提高响应速度

这套架构能够充分利用各LLM提供商的优势，为体育彩票业务带来更智能、更人性化的用户体验，同时保持系统的可扩展性和成本效益。