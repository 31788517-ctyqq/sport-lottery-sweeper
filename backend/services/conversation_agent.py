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
    
    async def respond_to_user(self, user_input: str, user_id: str = "default") -> str:
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
            
            response = await self.llm_service.generate_response(
                context_prompt,
                provider="zhipuai",  # 使用智谱AI提供商
                temperature=0.7,
                max_tokens=400
            )
            
            # 更新对话历史 - 使用角色标记的格式
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            # 限制历史记录长度以避免上下文过长
            if len(history) > 10:
                history = history[-10:]
            self.context_history[user_id] = history
            
            return response
        except Exception as e:
            logger.error(f"生成响应失败: {str(e)}")
            return "抱歉，我暂时无法回答这个问题。请稍后再试。"
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        if not history:
            return "无历史对话"
        
        formatted = []
        for item in history[-5:]:  # 只保留最近5次对话
            role = "用户" if item["role"] == "user" else "助手"
            formatted.append(f"{role}: {item['content']}")
        
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