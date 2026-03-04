"""
LLM供应商管理API路由
"""
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
import logging

from backend.database import get_db
from backend.crud.llm_provider import llm_provider as crud_llm_provider
from backend.schemas.llm_provider import (
    LLMProviderCreate,
    LLMProviderUpdate,
    LLMProviderResponse,
    LLMProviderTestRequest,
    LLMProviderBatchRequest,
    LLMProviderStatsResponse
)
from backend.models.llm_provider import LLMProviderTypeEnum, LLMProviderStatusEnum
from backend.api.deps import get_current_user, get_current_admin_user
from backend.models.user import User
from backend.utils.llm_monitor import LLMUsageMonitor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm-providers", tags=["llm-providers"])


def _resolve_test_provider_name(provider) -> str:
    """
    Resolve provider runtime name for connection test.
    Keep compatibility with historical records where zhipu/qwen providers
    were stored as `custom`.
    """
    provider_name = str(getattr(getattr(provider, "provider_type", None), "value", "") or "").lower().strip()
    if provider_name == "alibaba":
        return "qwen"
    if provider_name != "custom":
        return provider_name

    merged_text = " ".join(
        [
            str(getattr(provider, "name", "") or "").lower(),
            str(getattr(provider, "base_url", "") or "").lower(),
            str(getattr(provider, "default_model", "") or "").lower(),
            str(getattr(provider, "description", "") or "").lower(),
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


@router.get("/", response_model=List[LLMProviderResponse])
async def get_llm_providers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    enabled: Optional[bool] = Query(None, description="是否启用"),
    provider_type: Optional[LLMProviderTypeEnum] = Query(None, description="供应商类型"),
    health_status: Optional[LLMProviderStatusEnum] = Query(None, description="健康状态"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    order_by: str = Query("priority", description="排序字段"),
    order_desc: bool = Query(False, description="是否降序"),
    current_user: User = Depends(get_current_user),
):
    """
    获取LLM供应商列表
    """
    try:
        providers = crud_llm_provider.get_multi(
            db,
            skip=skip,
            limit=limit,
            enabled=enabled,
            provider_type=provider_type,
            health_status=health_status,
            search=search,
            order_by=order_by,
            order_desc=order_desc
        )
        return providers
    except Exception as e:
        logger.error(f"获取LLM供应商列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取供应商列表失败"
        )


@router.get("/count", response_model=Dict[str, int])
async def get_llm_providers_count(
    db: Session = Depends(get_db),
    enabled: Optional[bool] = Query(None, description="是否启用"),
    provider_type: Optional[LLMProviderTypeEnum] = Query(None, description="供应商类型"),
    health_status: Optional[LLMProviderStatusEnum] = Query(None, description="健康状态"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
):
    """
    获取LLM供应商数量
    """
    try:
        count = crud_llm_provider.get_count(
            db,
            enabled=enabled,
            provider_type=provider_type,
            health_status=health_status,
            search=search
        )
        return {"count": count}
    except Exception as e:
        logger.error(f"获取LLM供应商数量失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取供应商数量失败"
        )


@router.get("/{provider_id}", response_model=LLMProviderResponse)
async def get_llm_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    根据ID获取LLM供应商详情
    """
    provider = crud_llm_provider.get(db, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在"
        )
    return provider


@router.post("/", response_model=LLMProviderResponse, status_code=status.HTTP_201_CREATED)
def create_llm_provider(
    provider_in: LLMProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    创建新的LLM供应商（需要管理员权限）
    """
    # 检查名称是否已存在
    existing = crud_llm_provider.get_by_name(db, provider_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="供应商名称已存在"
        )
    
    # 修复：current_user是字典，使用['id']而不是.id
    provider = crud_llm_provider.create(db, obj_in=provider_in, created_by=current_user["id"])
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建供应商失败"
        )
    
    logger.info(f"管理员 {current_user['username']} 创建了LLM供应商: {provider.name}")
    return provider


@router.put("/{provider_id}", response_model=LLMProviderResponse)
async def update_llm_provider(
    provider_id: int,
    provider_in: LLMProviderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    更新LLM供应商信息（需要管理员权限）
    """
    provider = crud_llm_provider.get(db, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在"
        )
    
    # 修复：current_user是字典，使用['id']而不是.id
    updated_provider = crud_llm_provider.update(
        db, db_obj=provider, obj_in=provider_in, updated_by=current_user["id"]
    )
    if not updated_provider:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新供应商失败"
        )
    
    logger.info(f"管理员 {current_user['username']} 更新了LLM供应商: {provider.name}")
    return updated_provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_llm_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    删除LLM供应商（需要管理员权限）
    """
    success = crud_llm_provider.delete(db, provider_id=provider_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在或删除失败"
        )
    
    logger.info(f"管理员 {current_user['username']} 删除了LLM供应商 ID: {provider_id}")


@router.post("/{provider_id}/enable", response_model=LLMProviderResponse)
async def enable_llm_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    启用LLM供应商（需要管理员权限）
    """
    success = crud_llm_provider.enable(db, provider_id=provider_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在或启用失败"
        )
    
    provider = crud_llm_provider.get(db, provider_id)
    logger.info(f"管理员 {current_user['username']} 启用了LLM供应商: {provider.name}")
    return provider


@router.post("/{provider_id}/disable", response_model=LLMProviderResponse)
async def disable_llm_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    禁用LLM供应商（需要管理员权限）
    """
    success = crud_llm_provider.disable(db, provider_id=provider_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在或禁用失败"
        )
    
    provider = crud_llm_provider.get(db, provider_id)
    logger.info(f"管理员 {current_user['username']} 禁用了LLM供应商: {provider.name}")
    return provider


@router.post("/{provider_id}/test", response_model=Dict[str, Any])
async def test_llm_provider_connection(
    provider_id: int,
    test_data: LLMProviderTestRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    测试LLM供应商连接
    """
    provider = crud_llm_provider.get(db, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在"
        )
    
    # 获取解密的API密钥
    decrypted_api_key = crud_llm_provider.get_decrypted_api_key(db, provider_id)
    if not decrypted_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法解密API密钥"
        )
    
    # 根据供应商类型进行实际连接测试
    import time
    start_time = time.time()
    is_successful = False
    response_time_ms = 0
    error_message = ""
    tested_model = ""
    
    try:
        # 根据提供商类型创建测试实例
        from backend.services.llm_service import LLMUsageMonitor
        
        monitor = LLMUsageMonitor()
        provider_name = provider.provider_type.value.lower()
        
        # 规范化提供商名称：将'alibaba'映射为'qwen'以保持一致性
        normalized_name = _resolve_test_provider_name(provider)
        test_model = test_data.model or provider.default_model
        tested_model = test_model or ""
        test_prompt = test_data.test_prompt if test_data.test_prompt else "Hello, this is a connection test."
        requested_timeout_ms = int(getattr(test_data, "timeout_ms", 5000) or 5000)
        requested_timeout_ms = max(1000, min(requested_timeout_ms, 30000))
        per_model_timeout_sec = requested_timeout_ms / 1000.0
        
        # 创建对应的提供商实例
        if normalized_name == "openai":
            from backend.services.llm_service import OpenAILLMProvider
            provider_instance = OpenAILLMProvider(
                decrypted_api_key,
                monitor,
                base_url=(provider.base_url or "").strip() or None
            )
            # 发送一个简单的测试请求
            response = await asyncio.wait_for(
                provider_instance.generate_response(
                    test_prompt,
                    model=test_model or "gpt-3.5-turbo",
                    max_tokens=10
                ),
                timeout=per_model_timeout_sec
            )
            tested_model = test_model or "gpt-3.5-turbo"
            response_text = response.strip() if isinstance(response, str) else str(response or "").strip()
            is_successful = bool(response_text)
            if not is_successful:
                error_message = f"模型 {tested_model} 返回空内容"
            
        elif normalized_name == "gemini":
            from backend.services.llm_service import GeminiLLMProvider
            provider_instance = GeminiLLMProvider(decrypted_api_key, monitor)
            response = await asyncio.wait_for(
                provider_instance.generate_response(test_prompt, max_tokens=10),
                timeout=per_model_timeout_sec
            )
            tested_model = test_model or "gemini-pro"
            response_text = response.strip() if isinstance(response, str) else str(response or "").strip()
            is_successful = bool(response_text)
            if not is_successful:
                error_message = f"模型 {tested_model} 返回空内容"
            
        elif normalized_name == "qwen":
            from backend.services.llm_service import QwenLLMProvider
            provider_instance = QwenLLMProvider(decrypted_api_key, monitor)
            response = await asyncio.wait_for(
                provider_instance.generate_response(
                    test_prompt,
                    model=test_model or "qwen-turbo",
                    max_tokens=10
                ),
                timeout=per_model_timeout_sec
            )
            tested_model = test_model or "qwen-turbo"
            response_text = response.strip() if isinstance(response, str) else str(response or "").strip()
            is_successful = bool(response_text)
            if not is_successful:
                error_message = f"模型 {tested_model} 返回空内容"
            
        elif normalized_name == "zhipuai":
            from backend.services.llm_service import ZhipuAILLMProvider
            provider_instance = ZhipuAILLMProvider(decrypted_api_key, monitor)
            candidate_models: List[str] = []
            if test_data.model:
                candidate_models = [test_data.model]
            else:
                # Prefer available/stable models first; fallback to default model last.
                raw_models: List[Any] = []
                if isinstance(provider.available_models, list):
                    raw_models.extend(provider.available_models)
                raw_models.extend(["glm-4", "glm-4-flash"])
                raw_models.append(provider.default_model)

                seen_models = set()
                for model_name in raw_models:
                    model_str = str(model_name or "").strip()
                    if not model_str or model_str in seen_models:
                        continue
                    seen_models.add(model_str)
                    candidate_models.append(model_str)

            for model_name in candidate_models:
                tested_model = model_name
                try:
                    response = await asyncio.wait_for(
                        provider_instance.generate_response(
                            test_prompt,
                            model=model_name,
                            max_tokens=10
                        ),
                        timeout=per_model_timeout_sec
                    )
                    response_text = response.strip() if isinstance(response, str) else str(response or "").strip()
                    if response_text:
                        is_successful = True
                        break
                except asyncio.TimeoutError:
                    error_message = f"model {model_name} timeout ({requested_timeout_ms}ms)"
                except Exception as model_err:
                    error_message = f"模型 {model_name} 测试异常: {model_err}"

            if not is_successful and not error_message:
                if candidate_models:
                    error_message = f"模型 {', '.join(candidate_models)} 返回空内容"
                else:
                    error_message = "未找到可用测试模型"
            
        else:
            # 不支持的其他提供商类型
            error_message = f"不支持的提供商类型: {provider_name}"
            is_successful = False
            
        response_time_ms = int((time.time() - start_time) * 1000)
        
    except Exception as e:
        error_message = str(e)
        is_successful = False
        response_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"LLM供应商连接测试失败 (ID: {provider_id}): {error_message}")
    
    # 更新健康状态
    crud_llm_provider.update_health_status(
        db,
        provider_id=provider_id,
        is_healthy=is_successful,
        response_time_ms=response_time_ms
    )
    
    # 构建响应消息
    if is_successful:
        message = f"连接测试成功，响应时间: {response_time_ms}ms"
    else:
        message = f"连接测试失败: {error_message}" if error_message else "连接测试失败"
    
    return {
        "success": is_successful,
        "response_time_ms": response_time_ms,
        "message": message,
        "provider_id": provider_id,
        "provider_name": provider.name,
        "provider_type": provider_name,
        "tested_provider_type": normalized_name,
        "tested_model": tested_model
    }


@router.get("/{provider_id}/decrypted-api-key", response_model=Dict[str, str])
async def get_decrypted_api_key(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    获取解密后的API密钥（需要管理员权限）
    """
    api_key = crud_llm_provider.get_decrypted_api_key(db, provider_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在或API密钥解密失败"
        )
    
    # 只返回部分密钥（安全考虑）
    masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:] if len(api_key) > 12 else "***"
    return {
        "provider_id": provider_id,
        "api_key_masked": masked_key,
        "api_key_length": len(api_key)
    }


@router.get("/stats/overview", response_model=LLMProviderStatsResponse)
async def get_llm_providers_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取LLM供应商统计概览
    """
    stats = crud_llm_provider.get_stats(db)
    return stats


@router.get("/available/list", response_model=List[LLMProviderResponse])
async def get_available_llm_providers(
    db: Session = Depends(get_db),
    provider_type: Optional[LLMProviderTypeEnum] = Query(None, description="供应商类型"),
    min_priority: int = Query(1, ge=1, le=10, description="最低优先级"),
    max_priority: int = Query(10, ge=1, le=10, description="最高优先级"),
    current_user: User = Depends(get_current_user),
):
    """
    获取可用的LLM供应商列表（启用且健康）
    """
    providers = crud_llm_provider.get_available_providers(
        db,
        provider_type=provider_type,
        min_priority=min_priority,
        max_priority=max_priority
    )
    return providers


@router.post("/batch/update-status", response_model=Dict[str, int])
async def batch_update_llm_providers_status(
    batch_data: LLMProviderBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    批量更新LLM供应商状态（需要管理员权限）
    """
    success_count = 0
    failed_ids = []
    
    for provider_id in batch_data.provider_ids:
        if batch_data.action == "enable":
            success = crud_llm_provider.enable(db, provider_id=provider_id)
        elif batch_data.action == "disable":
            success = crud_llm_provider.disable(db, provider_id=provider_id)
        else:
            success = False
        
        if success:
            success_count += 1
        else:
            failed_ids.append(provider_id)
    
    logger.info(f"管理员 {current_user['username']} 批量更新了LLM供应商状态: {batch_data.action}, 成功: {success_count}, 失败: {len(failed_ids)}")
    return {
        "total": len(batch_data.provider_ids),
        "success": success_count,
        "failed": len(failed_ids),
        "failed_ids": failed_ids
    }


@router.post("/{provider_id}/increment-cost", response_model=Dict[str, Any])
async def increment_llm_provider_cost(
    provider_id: int,
    cost_cents: int = Body(..., gt=0, le=1000000, description="成本（分）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    增加LLM供应商使用成本
    """
    success = crud_llm_provider.increment_cost(
        db, provider_id=provider_id, cost_cents=cost_cents
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM供应商不存在或增加成本失败"
        )
    
    provider = crud_llm_provider.get(db, provider_id)
    return {
        "success": True,
        "provider_id": provider_id,
        "provider_name": provider.name,
        "total_cost": provider.total_cost / 100.0,  # 转换为元
        "monthly_cost": provider.monthly_cost / 100.0  # 转换为元
    }
