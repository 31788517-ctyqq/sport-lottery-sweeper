"""
爬虫任务适配器API
用于将 /api/admin/crawler/tasks 请求转发到实际的管理API
"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import logging
from backend.database import get_db
from backend.api.v1.admin.task_management import get_crawler_tasks, get_task_statistics

router = APIRouter()

# 适配器：将原来的路径映射到实际的API
@router.get("/tasks")
async def adapter_get_crawler_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),  # 改为Optional[str]，因为前端可能传递空字符串
    db: Session = Depends(get_db)
):
    """
    适配器：获取爬虫任务列表
    """
    # 将source_id转换为整数，如果它是有效的数字字符串
    source_id_int = None
    if source_id and source_id.isdigit():
        source_id_int = int(source_id)
    
    # 直接返回后端函数的调用结果
    return await get_crawler_tasks(
        page=page, 
        size=size, 
        name=name, 
        task_type=task_type, 
        status=status, 
        source_id=source_id_int, 
        db=db
    )


@router.get("/tasks/statistics")
async def adapter_get_task_statistics(
    db: Session = Depends(get_db)
):
    """
    适配器：获取任务统计信息
    """
    return await get_task_statistics(db=db)


# 添加Pydantic模型定义
from pydantic import BaseModel
from typing import Union

class CreateTaskRequest(BaseModel):
    name: str
    source_id: str
    task_type: str = "crawl"
    cron_expression: str
    config: Union[str, dict] = "{}"

# 添加创建任务的路由，支持Body参数
@router.post("/tasks")
async def adapter_create_crawler_task(
    request_data: CreateTaskRequest,
    db: Session = Depends(get_db)
):
    """
    适配器：创建爬虫任务
    """
    from backend.api.v1.admin.task_management import create_crawler_task
    
    # 确保config是字符串格式
    config_str = request_data.config
    if isinstance(config_str, dict):
        config_str = json.dumps(config_str, ensure_ascii=False)
    elif not isinstance(config_str, str):
        config_str = "{}"
    
    return await create_crawler_task(
        name=request_data.name,
        source_id=request_data.source_id,
        task_type=request_data.task_type,
        cron_expression=request_data.cron_expression,
        config=config_str,
        db=db
    )

# 保留旧路径兼容（临时）
@router.post("/crawler/tasks")
async def legacy_create_crawler_task(
    request_data: CreateTaskRequest,
    db: Session = Depends(get_db)
):
    """旧路径兼容接口（将被弃用）"""
    logging.warning("检测到使用旧版API路径 /crawler/tasks，请尽快迁移到 /tasks")
    return await adapter_create_crawler_task(request_data, db)

# 添加更新任务的路由
@router.put("/tasks/{task_id}")
async def adapter_update_crawler_task(
    task_id: int,
    name: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),
    cron_expression: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    config: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    适配器：更新爬虫任务
    """
    from backend.api.v1.admin.task_management import update_crawler_task
    
    return await update_crawler_task(
        task_id=task_id,
        name=name,
        source_id=source_id,
        cron_expression=cron_expression,
        is_active=is_active,
        config=config,
        db=db
    )

# 保留旧路径更新兼容（临时）
@router.put("/crawler/tasks/{task_id}")
async def legacy_update_crawler_task(
    task_id: int,
    name: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),
    cron_expression: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    config: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """旧路径更新兼容接口（将被弃用）"""
    logging.warning(f"检测到使用旧版API路径 /crawler/tasks/{task_id}，请尽快迁移到 /tasks/{task_id}")
    return await adapter_update_crawler_task(
        task_id=task_id,
        name=name,
        source_id=source_id,
        cron_expression=cron_expression,
        is_active=is_active,
        config=config,
        db=db
    )

# 获取单个任务
@router.get("/tasks/{task_id}")
async def adapter_get_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    适配器：获取单个爬虫任务
    """
    from backend.api.v1.admin.task_management import get_crawler_task
    
    return await get_crawler_task(task_id=task_id, db=db)

# 删除任务
@router.delete("/tasks/{task_id}")
async def adapter_delete_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    适配器：删除爬虫任务
    """
    from backend.api.v1.admin.task_management import delete_crawler_task
    
    return await delete_crawler_task(task_id=task_id, db=db)

# 触发任务
@router.post("/tasks/{task_id}/trigger")
async def adapter_trigger_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    适配器：触发爬虫任务
    """
    from backend.api.v1.admin.task_management import trigger_crawler_task
    
    return await trigger_crawler_task(task_id=task_id, db=db)

# 停止任务
@router.post("/tasks/{task_id}/stop")
async def adapter_stop_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    适配器：停止爬虫任务
    """
    from backend.api.v1.admin.task_management import stop_crawler_task
    
    return await stop_crawler_task(task_id=task_id, db=db)

# 获取任务日志
@router.get("/tasks/{task_id}/logs")
async def adapter_get_crawler_task_logs(
    task_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    适配器：获取爬虫任务日志
    """
    from backend.api.v1.admin.task_management import get_crawler_task_logs
    
    return await get_crawler_task_logs(task_id=task_id, page=page, size=size, db=db)


# 批量删除任务
@router.post("/tasks/batch-delete")
async def adapter_batch_delete_crawler_tasks(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    适配器：批量删除爬虫任务
    """
    # 添加调试日志
    print(f"DEBUG: 适配器接收到的请求数据: {request_data}")
    
    # 获取任务ID列表
    task_ids = None
    
    # 检查请求数据中是否包含ids或task_ids
    if 'ids' in request_data:
        task_ids = request_data['ids']
        print(f"DEBUG: 从 'ids' 字段获取到任务ID: {task_ids}")
    elif 'task_ids' in request_data:
        task_ids = request_data['task_ids']
        print(f"DEBUG: 从 'task_ids' 字段获取到任务ID: {task_ids}")
    
    # 验证task_ids是否有效
    if not task_ids or not isinstance(task_ids, list) or len(task_ids) == 0:
        print(f"DEBUG: 无效的task_ids: {task_ids}")
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="task_ids不能为空")
    
    # 确保所有ID都是整数
    try:
        task_ids = [int(tid) for tid in task_ids]
        print(f"DEBUG: 验证后的任务ID: {task_ids}")
    except (ValueError, TypeError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="任务ID必须为整数")
    
    # 导入CrawlerTask模型并直接执行删除
    from backend.models.crawler_tasks import CrawlerTask
    
    # 查询要删除的任务
    tasks = db.query(CrawlerTask).filter(CrawlerTask.id.in_(task_ids)).all()
    
    print(f"DEBUG: 查询到 {len(tasks)} 个待删除任务")
    
    if not tasks:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="未找到任何要删除的任务")
    
    # 删除任务
    deleted_count = 0
    for task in tasks:
        db.delete(task)
        deleted_count += 1
    
    db.commit()
    
    result = {
        "success": True,
        "data": {
            "deleted_count": deleted_count,
            "deleted_ids": [task.id for task in tasks]
        },
        "message": f"成功删除 {deleted_count} 个任务"
    }
    
    print(f"DEBUG: 批量删除结果: {result}")
    return result
