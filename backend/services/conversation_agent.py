from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ConversationAgent:
    """智能对话助手。"""

    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm_service = llm_service
        self.context_history: Dict[str, List[Dict[str, str]]] = {}

    async def respond_to_user(
        self,
        user_input: str,
        user_id: str = "default",
        provider: str = "zhipuai",
        model: Optional[str] = None,
    ) -> str:
        """响应用户输入。"""
        try:
            if not self.llm_service or not self.llm_service.providers:
                logger.warning("No available LLM providers configured")
                return "抱歉，AI 服务未配置可用供应商，请联系管理员检查 API Key 配置。"

            history = self.context_history.get(user_id, [])
            context_prompt = f"""
你是体育彩票智能助手，专门协助用户了解彩票数据、分析和预测。
请根据用户问题提供专业、准确且克制的回答。

当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请遵循以下原则：
1. 只给出可验证的信息；
2. 涉及预测要明确不确定性；
3. 鼓励理性投注；
4. 如涉及数据，请说明时效性与来源。

历史对话：
{self._format_history(history)}

用户问题: {user_input}
"""

            response, used_provider, used_model, degraded = await self._generate_with_fallback(
                prompt=context_prompt,
                preferred_provider=provider or "zhipuai",
                preferred_model=model,
            )

            if degraded:
                readable_model = used_model or "default"
                response = f"（指定模型暂不可用，已自动切换到 {used_provider}/{readable_model}）\n\n{response}"

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            if len(history) > 10:
                history = history[-10:]
            self.context_history[user_id] = history

            return response
        except Exception as e:
            logger.error("Failed to generate response: %s", e)
            return "抱歉，AI 服务暂时不可用，请稍后再试。"

    async def _generate_with_fallback(
        self,
        prompt: str,
        preferred_provider: str,
        preferred_model: Optional[str],
    ) -> Tuple[str, str, Optional[str], bool]:
        providers = self.llm_service.providers
        default_provider = self.llm_service.default_provider

        active_provider = preferred_provider
        active_model = preferred_model
        degraded = False

        if active_provider not in providers:
            logger.warning(
                "Requested provider '%s' is not registered, fallback to default '%s'",
                active_provider,
                default_provider,
            )
            if not default_provider or default_provider not in providers:
                raise ValueError(f"Provider {active_provider} not registered and no default provider available")
            active_provider = default_provider
            active_model = None
            degraded = True

        try:
            response = await self._call_provider(prompt, active_provider, active_model)
            return response, active_provider, active_model, degraded
        except Exception as primary_error:
            logger.warning(
                "Primary LLM call failed provider=%s model=%s err=%s",
                active_provider,
                active_model,
                primary_error,
            )

            # 兜底1：如果是智谱自定义模型失败，回退到 glm-4
            if active_provider == "zhipuai" and active_model and active_model != "glm-4":
                try:
                    fallback_model = "glm-4"
                    response = await self._call_provider(prompt, "zhipuai", fallback_model)
                    return response, "zhipuai", fallback_model, True
                except Exception as glm4_error:
                    logger.warning("Fallback to zhipuai/glm-4 failed: %s", glm4_error)

            # 兜底2：回退到默认供应商（不指定模型）
            if default_provider and default_provider in providers and default_provider != active_provider:
                try:
                    response = await self._call_provider(prompt, default_provider, None)
                    return response, default_provider, None, True
                except Exception as default_error:
                    logger.warning("Fallback to default provider failed: %s", default_error)

            raise primary_error

    async def _call_provider(self, prompt: str, provider: str, model: Optional[str]) -> str:
        kwargs = {
            "provider": provider,
            "temperature": 0.7,
            "max_tokens": 400,
        }
        if model:
            kwargs["model"] = model
        return await self.llm_service.generate_response(prompt, **kwargs)

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史。"""
        if not history:
            return "无历史对话"

        formatted: List[str] = []
        for item in history[-5:]:
            role = "用户" if item["role"] == "user" else "助手"
            formatted.append(f"{role}: {item['content']}")
        return "\n".join(formatted)

    def _update_history(self, user_id: str, user_input: str, response: str):
        """更新对话历史（保留旧调用兼容）。"""
        if user_id not in self.context_history:
            self.context_history[user_id] = []

        self.context_history[user_id].append(
            {
                "user_input": user_input,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if len(self.context_history[user_id]) > 10:
            self.context_history[user_id] = self.context_history[user_id][-10:]
