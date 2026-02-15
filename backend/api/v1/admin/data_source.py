"""
数据源管理API
提供数据源的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from backend.database import get_db
# 临时绕过认证
# from backend.core.auth import get_current_admin_user
# from backend.models.user import User
from backend.models.data_sources import DataSource
from backend.models.sp_records import SPRecord
from backend.services.sp_management_service import SPManagementService
from backend.schemas.sp_management import DataSourceFilterParams, DataSourceCreate
from backend.core.response import APIResponse

# AI_WORKING: coder1 @2026-02-04 - 添加Null安全工具导入
from backend.utils.null_safety import (
    safe_get,
    ensure_not_null,
    normalize_null,
    null_safe,
    coalesce
)
from backend.core.exceptions import NullValueError, EmptyResultError

router = APIRouter()


def _safe_json_loads(value, default=None):
    if default is None:
        default = {}
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode()
        except Exception:
            return default
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
    try:
        return json.loads(value)
    except Exception:
        return default

# 批量操作路由需要在单个资源路由之前定义，以避免路由冲突
@router.delete("/sources/batch")
async def batch_delete_sources(
    request_data: dict = Body(...),
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量删除数据源
    """
    try:
        ids = request_data.get('ids', [])
        if not ids or not isinstance(ids, list) or len(ids) == 0:
            raise HTTPException(
                status_code=422,
                detail="缺少有效的IDs列表"
            )
        
        service = SPManagementService(db)
        deleted_count = service.batch_delete_data_sources(ids)
        
        return {
            "success": True,
            "data": {"deleted_count": deleted_count},
            "message": f"成功删除 {deleted_count} 个数据源"
        }
    except HTTPException:
        raise  # 重新抛出HTTP异常
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/batch/health")
async def batch_health_check(
    request_data: dict = Body(...),
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量健康检查
    """
    try:
        ids = request_data.get('ids', [])
        if not ids or not isinstance(ids, list) or len(ids) == 0:
            raise HTTPException(
                status_code=422,
                detail="缺少有效的IDs列表"
            )
        
        service = SPManagementService(db)
        results = []
        
        for source_id in ids:
            try:
                health_status = service.test_data_source(source_id)
                results.append({
                    "source_id": source_id,
                    "status": health_status.get("status", "unknown"),
                    "healthy": health_status.get("success", False),
                    "message": health_status.get("message", ""),
                    "health_status": health_status
                })
            except Exception as e:
                results.append({
                    "source_id": source_id,
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "data": results,
            "message": "批量健康检查完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/sources")
async def get_data_sources(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None, description="源ID"),
    category: Optional[str] = Query(None, description="内容分类"),
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取数据源列表，支持分页和筛选
    """
    try:
        service = SPManagementService(db)
        
        # 构建筛选参数
        params = DataSourceFilterParams(
            page=page,
            size=size,
            type=type,
            status=status,
            search=search,
            source_id=source_id,
            category=category
        )
        
        sources = service.get_data_sources(params)
        
        # 处理响应数据，提取分类信息并确保config格式正确
        items_data = []
        for item in sources.items:
            try:
                item_dict = item.dict()
                
                # 确保关键字段不为null
                ensure_not_null(item_dict.get('name'), "数据源名称")
                ensure_not_null(item_dict.get('type'), "数据源类型")
                
                # 处理config字段
                config = {}
                if isinstance(item_dict.get('config'), str):
                    try:
                        config = _safe_json_loads(item_dict.get('config'))
                    except:
                        config = {}
                elif isinstance(item_dict.get('config'), dict):
                    config = item_dict['config']
                
                # 提取分类信息到顶层
                if config and 'category' in config:
                    item_dict['category'] = config['category']
                
                # 确保返回的config是字典格式
                item_dict['config'] = config
                
                items_data.append(item_dict)
            except NullValueError as e:
                logger.warning(f"数据源 {item.id if hasattr(item, 'id') else 'unknown'} 存在null值问题: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"处理数据源时发生错误: {str(e)}")
                continue
        
        return {
            "success": True,
            "data": {
                "items": items_data,
                "total": sources.total,
                "page": sources.page,
                "size": sources.size,
                "pages": (sources.total + sources.size - 1) // sources.size
            },
            "message": "数据源获取成功"
        }
    except Exception as e:
        # 记录错误以便调试
        import traceback
        print(f"获取数据源错误: {str(e)}")
        logger.exception("获取数据源异常")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/{source_id}")
async def get_data_source(
    source_id: int,
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取单个数据源详情
    """
    try:
        service = SPManagementService(db)
        source = service.get_data_source(source_id)
        
        # 转换为字典并确保关键字段存在
        source_dict = source.dict()
        
        # 添加null安全检查
        ensure_not_null(source_dict.get('name'), "数据源名称")
        ensure_not_null(source_dict.get('type'), "数据源类型")
        
        # 处理config字段
        config = {}
        if isinstance(source_dict.get('config'), str):
            try:
                config = _safe_json_loads(source_dict.get('config'))
            except:
                config = {}
        elif isinstance(source_dict.get('config'), dict):
            config = source_dict['config']
        
        # 提取分类信息到顶层
        if config and 'category' in config:
            source_dict['category'] = config['category']
        
        # 确保返回的config是字典格式
        source_dict['config'] = config
        
        return {
            "success": True,
            "data": source_dict,
            "message": "数据源获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/sources")
async def create_data_source(
    request_data: dict = Body(...),  # 接受整个请求体
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建数据源
    """
    try:
        service = SPManagementService(db)
        
        # 从请求体中提取参数
        name = request_data.get("name")
        type = request_data.get("type")
        url = request_data.get("url")
        config = request_data.get("config", {})
        
        # 处理status字段，将布尔值转换为字符串
        raw_status = request_data.get("status", "online")
        if isinstance(raw_status, bool):
            status = "online" if raw_status else "offline"
        else:
            status = raw_status
        
        # AI_WORKING: coder1 @2026-02-04 - 添加null安全检查
        ensure_not_null(name, "数据源名称")
        ensure_not_null(type, "数据源类型")
        # url可以为空，但config需要确保是字典
        if config is None:
            config = {}
        # AI_DONE: coder1 @2026-02-04

        from backend.schemas.sp_management import DataSourceCreate
        create_data = DataSourceCreate(
            name=name,
            type=type,
            url=url,
            config=config,
            status=status
        )

        created_source = service.create_data_source(create_data, 1)  # 使用默认用户ID

        # 确保返回的响应中config字段是字典格式
        response_data = created_source.dict()
        if isinstance(response_data.get('config'), str):
            try:
                response_data['config'] = _safe_json_loads(response_data.get('config'))
            except:
                response_data['config'] = {}

        # 使用字典格式返回响应
        return {
            "success": True,
            "message": "创建成功",
            "data": response_data
        }
    except HTTPException as e:
        logger.error(f"创建数据源失败: {e.detail}")
        return {
            "success": False,
            "message": f"创建数据源失败: {e.detail}",
            "error": {
                "code": e.status_code,
                "message": e.detail
            }
        }
    except Exception as e:
        logger.exception("创建数据源异常")
        return {
            "success": False,
            "message": f"创建数据源失败: {str(e)}",
            "error": {
                "code": 500,
                "message": str(e)
            }
        }


@router.put("/sources/{source_id}")
async def update_data_source(
    source_id: int,
    request_data: dict = Body(...),  # 接收完整的请求体
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新数据源
    """
    try:
        from backend.schemas.sp_management import DataSourceUpdate
        
        # 构建更新数据
        update_data = {}
        
        # 处理基本字段
        if 'name' in request_data:
            name = request_data['name']
            if name is None or (isinstance(name, str) and name.strip() == ""):
                raise HTTPException(status_code=422, detail="数据源名称不能为空")
            update_data['name'] = name
        if 'type' in request_data:
            type = request_data['type']
            if type is None or (isinstance(type, str) and type.strip() == ""):
                raise HTTPException(status_code=422, detail="数据源类型不能为空")
            update_data['type'] = type
        if 'url' in request_data:
            url = request_data['url']
            if url is not None and isinstance(url, str) and url.strip() == "":
                url = None
            update_data['url'] = url
        if 'status' in request_data:
            raw_status = request_data['status']
            # 处理布尔类型的status值
            if isinstance(raw_status, bool):
                status = "online" if raw_status else "offline"
            else:
                status = raw_status
            if status is None or (isinstance(status, str) and status.strip() == ""):
                raise HTTPException(status_code=422, detail="状态不能为空")
            update_data['status'] = status
        
        # 处理配置字段和分类信息
        config = {}
        
        # 如果提供了config字段
        if 'config' in request_data:
            config_data = request_data['config']
            if config_data is None:
                config = {}
            elif isinstance(config_data, str):
                try:
                    config = _safe_json_loads(config_data)
                except:
                    config = {}
            elif isinstance(config_data, dict):
                config = config_data
        else:
            # 如果没有提供config但有category，需要获取现有配置
            if 'category' in request_data:
                service = SPManagementService(db)
                existing_source = service.get_data_source(source_id)
                if existing_source and existing_source.config:
                    try:
                        if isinstance(existing_source.config, str):
                            config = _safe_json_loads(existing_source.config)
                        else:
                            config = existing_source.config or {}
                    except:
                        config = {}
        
        # 如果请求中包含category字段，更新配置中的分类信息
        if 'category' in request_data:
            config['category'] = request_data['category']
        
        # 只有当config有变化或显式提供时才更新
        if config or 'config' in request_data:
            update_data['config'] = config

        # 创建DataSourceUpdate对象
        update_obj = DataSourceUpdate(**update_data)
        
        service = SPManagementService(db)
        updated_source = service.update_data_source(source_id, update_obj)

        # 处理返回数据，提取分类信息
        response_data = updated_source.dict()
        
        # 处理config字段
        response_config = {}
        if isinstance(response_data.get('config'), str):
            try:
                response_config = _safe_json_loads(response_data.get('config'))
            except:
                response_config = {}
        elif isinstance(response_data.get('config'), dict):
            response_config = response_data['config']
        
        # 提取分类信息到顶层
        if response_config and 'category' in response_config:
            response_data['category'] = response_config['category']
        
        # 确保返回的config是字典格式
        response_data['config'] = response_config

        return {
            "success": True,
            "data": response_data,
            "message": "更新成功"
        }
    except HTTPException as e:
        logger.error(f"更新数据源失败: {e.detail}")
        return {
            "success": False,
            "message": f"更新数据源失败: {e.detail}",
            "error": {
                "code": e.status_code,
                "message": e.detail
            }
        }
    except Exception as e:
        logger.exception("更新数据源异常")
        return {
            "success": False,
            "message": f"更新数据源失败: {str(e)}",
            "error": {
                "code": 500,
                "message": str(e)
            }
        }


@router.delete("/sources/{source_id}")
async def delete_data_source(
    source_id: int,
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除数据源
    """
    try:
        service = SPManagementService(db)
        result = service.delete_data_source(source_id)
        
        return {
            "success": True,
            "data": {"id": source_id},
            "message": "数据源删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/sources/{source_id}/test-connection")
async def test_data_source_connection(
    source_id: int,
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    测试数据源连接
    """
    try:
        service = SPManagementService(db)
        result = service.test_data_source(source_id)
        
        return {
            "success": True,
            "data": result,
            "message": "连接测试完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/sources/batch-update-status")
async def batch_update_status(
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量更新数据源状态
    """
    try:
        # 临时实现，返回成功
        return {
            "success": True,
            "data": {"message": "批量更新状态成功"},
            "message": "批量更新状态成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.api_route("/sources/{source_id}/health", methods=["GET", "POST"])
async def get_data_source_health(
    source_id: int,
    # current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取数据源健康状态（支持GET和POST方法）
    返回前端期望的格式，包含status、response_time_ms、status_code、message字段
    """
    try:
        service = SPManagementService(db)
        # 使用测试连接方法作为健康检查
        health_status = service.test_data_source(source_id)
        
        # 确保返回的数据包含前端期望的字段
        response_data = health_status.copy()
        
        # 映射字段到前端期望的格式
        response_data['response_time_ms'] = health_status.get('response_time')
        response_data['status_code'] = health_status.get('status_code')
        response_data['status'] = health_status.get('status', 'unknown')
        response_data['message'] = health_status.get('message', '')
        
        return {
            "success": True,
            "data": response_data,
            "message": "健康状态获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
