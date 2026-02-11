from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ...database import get_db
from ...services.prediction_explainer import PredictionExplainer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])


def _get_llm_service():
    svc = None
    try:
        from ... import main as main_module
        svc = getattr(main_module, "llm_service", None)
    except Exception:
        svc = None
    if not svc:
        try:
            import __main__ as main_module
            svc = getattr(main_module, "llm_service", None)
        except Exception:
            svc = None
    if not svc:
        raise HTTPException(status_code=503, detail="LLM service not initialized")
    return svc


class ChatRequest(BaseModel):
    user_input: str
    user_id: str = "default"
    provider: str = "qwen"

@router.post("/chat")
async def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """与智能助手对话"""
    import time
    start_time = time.time()
    try:
        from ...services.conversation_agent import ConversationAgent
        agent = ConversationAgent(db, _get_llm_service())
        response = await agent.respond_to_user(request.user_input, request.user_id)
        
        # 记录成功日志
        from ...models.log_entry import LogEntry
        from datetime import datetime
        import json
        
        duration_ms = int((time.time() - start_time) * 1000)
        extra_data = json.dumps({
            "user_id": request.user_id,
            "provider": request.provider,
            "input_length": len(request.user_input),
            "response_length": len(response),
            "success": True
        })
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level="INFO",
            module="llm",
            message=f"AI对话请求: 用户 '{request.user_id}' 通过 '{request.provider}' 请求成功，响应长度 {len(response)} 字符",
            user_id=None,  # 如果不是后端用户，可以为空
            ip_address=None,
            user_agent=None,
            session_id=None,
            request_path="/api/v1/llm/chat",
            response_status=200,
            duration_ms=duration_ms,
            extra_data=extra_data
        )
        db.add(log_entry)
        db.commit()
        
        return {"response": response, "provider": request.provider}
    except Exception as e:
        # 记录错误日志
        from ...models.log_entry import LogEntry
        from datetime import datetime
        import json
        
        duration_ms = int((time.time() - start_time) * 1000)
        extra_data = json.dumps({
            "user_id": request.user_id,
            "provider": request.provider,
            "input_length": len(request.user_input),
            "error": str(e),
            "success": False
        })
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level="ERROR",
            module="llm",
            message=f"AI对话请求失败: 用户 '{request.user_id}' 通过 '{request.provider}' 请求失败，错误: {str(e)}",
            user_id=None,
            ip_address=None,
            user_agent=None,
            session_id=None,
            request_path="/api/v1/llm/chat",
            response_status=500,
            duration_ms=duration_ms,
            extra_data=extra_data
        )
        db.add(log_entry)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")