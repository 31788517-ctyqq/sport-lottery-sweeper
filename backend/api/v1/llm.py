from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ...database import get_db
from ...services.prediction_explainer import PredictionExplainer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])

@router.post("/explain-prediction")
async def explain_prediction(
    match_id: int,
    prediction_data: Dict[str, Any],
    provider: str = "openai",
    db: Session = Depends(get_db)
):
    """解释预测结果"""
    try:
        from ...main import llm_service
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