import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import asc
from sqlalchemy.orm import Session

from ...crud.llm_provider import llm_provider as crud_llm_provider
from ...database import get_db
from ...models.llm_provider import LLMProvider, LLMProviderStatusEnum

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])


SUPPORTED_RUNTIME_PROVIDERS = {"openai", "gemini", "qwen", "zhipuai"}


def _get_llm_service():
    svc = None
    try:
        from ... import main as main_module

        svc = getattr(main_module, "llm_service", None)
        if not svc and hasattr(main_module, "init_llm_service"):
            try:
                main_module.init_llm_service()
                svc = getattr(main_module, "llm_service", None)
            except Exception:
                svc = None
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


def _normalize_provider_alias(provider: Optional[str]) -> str:
    text = (provider or "").strip().lower()
    if text == "alibaba":
        return "qwen"
    return text


def _resolve_runtime_provider_name(provider_row: LLMProvider) -> str:
    provider_name = _normalize_provider_alias(
        str(getattr(getattr(provider_row, "provider_type", None), "value", "") or "")
    )
    if provider_name and provider_name != "custom":
        return provider_name

    merged_text = " ".join(
        [
            str(getattr(provider_row, "name", "") or "").lower(),
            str(getattr(provider_row, "base_url", "") or "").lower(),
            str(getattr(provider_row, "default_model", "") or "").lower(),
            str(getattr(provider_row, "description", "") or "").lower(),
        ]
    )
    if any(token in merged_text for token in ("open.bigmodel.cn", "bigmodel", "zhipu", "glm")):
        return "zhipuai"
    if any(token in merged_text for token in ("dashscope", "qwen", "tongyi")):
        return "qwen"
    if any(token in merged_text for token in ("openai", "gpt", "ark.cn", "volces", "doubao", "volcengine")):
        return "openai"
    if any(token in merged_text for token in ("gemini", "google")):
        return "gemini"
    return provider_name


def _extract_provider_models(provider_row: LLMProvider) -> List[str]:
    models: List[str] = []
    raw = getattr(provider_row, "available_models", None)
    if isinstance(raw, list):
        models.extend([str(item).strip() for item in raw if str(item).strip()])
    elif isinstance(raw, str):
        raw_text = raw.strip()
        if raw_text:
            if raw_text.startswith("[") and raw_text.endswith("]"):
                try:
                    payload = json.loads(raw_text)
                    if isinstance(payload, list):
                        models.extend([str(item).strip() for item in payload if str(item).strip()])
                except Exception:
                    pass
            if not models:
                models.extend([item.strip() for item in raw_text.split(",") if item.strip()])

    default_model = str(getattr(provider_row, "default_model", "") or "").strip()
    if default_model:
        models.append(default_model)

    deduped: List[str] = []
    seen = set()
    for model in models:
        key = model.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(model)
    return deduped


def _pick_provider_from_db(
    db: Session,
    requested_provider: Optional[str],
    requested_model: Optional[str],
) -> Tuple[Optional[LLMProvider], Optional[str], Optional[str], str]:
    # 优先拿启用+健康；若没有健康项，降级到“仅启用”。
    providers = (
        db.query(LLMProvider)
        .filter(LLMProvider.enabled == True, LLMProvider.health_status == LLMProviderStatusEnum.HEALTHY)
        .order_by(asc(LLMProvider.priority), asc(LLMProvider.id))
        .all()
    )
    source = "db_healthy"
    if not providers:
        providers = (
            db.query(LLMProvider)
            .filter(LLMProvider.enabled == True)
            .order_by(asc(LLMProvider.priority), asc(LLMProvider.id))
            .all()
        )
        source = "db_enabled"

    if not providers:
        return None, None, None, "none"

    req_provider = _normalize_provider_alias(requested_provider)
    req_model = (requested_model or "").strip()
    req_model_lower = req_model.lower()

    scored: List[Tuple[Tuple[int, int, int, int], LLMProvider, str, List[str]]] = []
    for row in providers:
        runtime_name = _resolve_runtime_provider_name(row)
        if runtime_name not in SUPPORTED_RUNTIME_PROVIDERS:
            continue

        models = _extract_provider_models(row)
        models_lower = {m.lower() for m in models}
        model_match = int(bool(req_model and req_model_lower in models_lower))
        provider_match = int(bool(req_provider and req_provider == runtime_name))
        health_match = int(getattr(row, "health_status", None) == LLMProviderStatusEnum.HEALTHY)
        priority_score = -int(getattr(row, "priority", 10) or 10)

        score = (model_match, provider_match, health_match, priority_score)
        scored.append((score, row, runtime_name, models))

    if not scored:
        return None, None, None, "none"

    scored.sort(key=lambda item: item[0], reverse=True)
    _, best_row, best_runtime, best_models = scored[0]

    selected_model: Optional[str] = None
    if req_model:
        if req_model_lower in {m.lower() for m in best_models}:
            selected_model = req_model
        elif best_runtime == req_provider:
            # 对于同供应商且用户显式指定模型，允许透传模型名（即使未列在 available_models）。
            selected_model = req_model
        else:
            selected_model = str(getattr(best_row, "default_model", "") or "").strip() or None
    else:
        selected_model = str(getattr(best_row, "default_model", "") or "").strip() or None

    return best_row, best_runtime, selected_model, source


def _bootstrap_runtime_provider(
    db: Session,
    llm_service: Any,
    requested_provider: Optional[str],
    requested_model: Optional[str],
) -> Tuple[Optional[str], Optional[str], str]:
    row, runtime_provider, selected_model, source = _pick_provider_from_db(
        db=db,
        requested_provider=requested_provider,
        requested_model=requested_model,
    )
    if not row or not runtime_provider:
        return None, None, "none"

    api_key = crud_llm_provider.get_decrypted_api_key(db, row.id)
    if not api_key:
        logger.warning("Provider %s selected from DB but api_key decrypt failed", row.id)
        return None, None, "none"

    try:
        llm_service.register_provider(runtime_provider, api_key)
        if not llm_service.default_provider:
            llm_service.set_default_provider(runtime_provider)
        return runtime_provider, selected_model, source
    except Exception as e:
        logger.warning("Failed to bootstrap runtime provider from DB, id=%s err=%s", row.id, e)
        return None, None, "none"


class ChatRequest(BaseModel):
    user_input: str
    user_id: str = "default"
    provider: str = "qwen"
    model: Optional[str] = None


@router.post("/chat")
async def chat_with_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    """对话助手接口：优先使用远程服务页配置的供应商。"""
    start_time = time.time()
    from ...models.log_entry import LogEntry
    from ...services.conversation_agent import ConversationAgent

    resolved_provider = request.provider
    resolved_model = request.model
    resolved_source = "request"

    try:
        llm_service = _get_llm_service()

        db_provider, db_model, db_source = _bootstrap_runtime_provider(
            db=db,
            llm_service=llm_service,
            requested_provider=request.provider,
            requested_model=request.model,
        )
        if db_provider:
            resolved_provider = db_provider
            resolved_model = db_model
            resolved_source = db_source

        agent = ConversationAgent(db, llm_service)
        response = await agent.respond_to_user(
            request.user_input,
            request.user_id,
            resolved_provider,
            resolved_model,
        )

        duration_ms = int((time.time() - start_time) * 1000)
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level="INFO",
            module="llm",
            message=(
                f"AI对话请求成功: user={request.user_id}, "
                f"requested={request.provider}/{request.model or '-'}, "
                f"resolved={resolved_provider}/{resolved_model or '-'}, source={resolved_source}"
            ),
            user_id=None,
            ip_address=None,
            user_agent=None,
            session_id=None,
            request_path="/api/v1/llm/chat",
            response_status=200,
            duration_ms=duration_ms,
            extra_data=json.dumps(
                {
                    "user_id": request.user_id,
                    "requested_provider": request.provider,
                    "requested_model": request.model,
                    "resolved_provider": resolved_provider,
                    "resolved_model": resolved_model,
                    "resolved_source": resolved_source,
                    "input_length": len(request.user_input or ""),
                    "response_length": len(response or ""),
                    "success": True,
                },
                ensure_ascii=False,
            ),
        )
        db.add(log_entry)
        db.commit()

        return {
            "response": response,
            "provider": resolved_provider,
            "model": resolved_model,
            "resolved_source": resolved_source,
        }
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level="ERROR",
            module="llm",
            message=(
                f"AI对话请求失败: user={request.user_id}, "
                f"requested={request.provider}/{request.model or '-'}, "
                f"resolved={resolved_provider}/{resolved_model or '-'}, source={resolved_source}, err={e}"
            ),
            user_id=None,
            ip_address=None,
            user_agent=None,
            session_id=None,
            request_path="/api/v1/llm/chat",
            response_status=500,
            duration_ms=duration_ms,
            extra_data=json.dumps(
                {
                    "user_id": request.user_id,
                    "requested_provider": request.provider,
                    "requested_model": request.model,
                    "resolved_provider": resolved_provider,
                    "resolved_model": resolved_model,
                    "resolved_source": resolved_source,
                    "input_length": len(request.user_input or ""),
                    "error": str(e),
                    "success": False,
                },
                ensure_ascii=False,
            ),
        )
        db.add(log_entry)
        db.commit()
        raise HTTPException(status_code=500, detail=f"对话处理失败: {e}")
