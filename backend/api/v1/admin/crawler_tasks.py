"""
FastAPI版本的任务管理路由
替代原有的Flask路由实现
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database_async import get_async_db
from backend.models.crawler_tasks import CrawlerTask as CrawlerTaskModel
from backend.models.crawler_logs import CrawlerTaskLog as CrawlerLogModel
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/crawler/tasks", tags=["crawler-tasks"])

# API端点实现
@router.get("", response_model=dict)
async def list_tasks(
    db: AsyncSession = Depends(get_async_db),
    page: int = 0,
    size: int = 20,
    name: str = None,
    task_type: str = None,
    status: str = None,
    source_id: str = None
):
    """获取任务列表"""
    try:
        # 构建查询
        query = select(CrawlerTaskModel)
        count_query = select(func.count(CrawlerTaskModel.id))
        
        # 应用过滤器
        if name:
            query = query.where(CrawlerTaskModel.name.contains(name))
            count_query = count_query.where(CrawlerTaskModel.name.contains(name))
        if task_type:
            query = query.where(CrawlerTaskModel.task_type == task_type)
            count_query = count_query.where(CrawlerTaskModel.task_type == task_type)
        if status:
            query = query.where(CrawlerTaskModel.status == status)
            count_query = count_query.where(CrawlerTaskModel.status == status)
        if source_id:
            # 如果source_id是数字字符串，则转换为整数进行过滤
            if source_id.isdigit():
                source_id_int = int(source_id)
                query = query.where(CrawlerTaskModel.source_id == source_id_int)
                count_query = count_query.where(CrawlerTaskModel.source_id == source_id_int)
            # 如果source_id不是数字字符串，忽略过滤（可能是空值或无效输入）
        
        # 应用分页
        query = query.offset(page * size).limit(size)
        
        # 执行查询
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # 计算总数
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 转换为前端需要的格式
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'name': task.name,
                'source_id': task.source_id,
                'task_type': task.task_type,
                'cron_expression': task.cron_expression,
                'is_active': task.is_active,
                'status': task.status,
                'last_run_time': task.last_run_time.isoformat() if task.last_run_time else None,
                'next_run_time': task.next_run_time.isoformat() if task.next_run_time else None,
                'run_count': task.run_count or 0,
                'success_count': task.success_count or 0,
                'error_count': task.error_count or 0,
                'config': task.config or {},
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'progress': int((task.success_count or 0) / max(task.run_count or 1, 1) * 100) if task.run_count and task.run_count > 0 else 0
            })
        
        return {
            "success": True,
            "data": {
                "items": task_list,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "任务列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.post("", response_model=dict)
async def create_task(
    name: str,
    source_id: str,
    task_type: str = "crawl",
    cron_expression: str = "* * * * *",
    config: Optional[dict] = {},
    db: AsyncSession = Depends(get_async_db)
):
    """创建任务"""
    try:
        # 验证source_id是否为数字
        if not source_id.isdigit():
            raise HTTPException(status_code=400, detail="source_id必须是数字")
        source_id_int = int(source_id)
        
        # 创建新任务对象
        new_task = CrawlerTaskModel(
            name=name,
            source_id=source_id_int,
            task_type=task_type,
            cron_expression=cron_expression,
            is_active=True,
            status='stopped',  # 默认状态
            run_count=0,
            success_count=0,
            error_count=0,
            config=config,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 添加到数据库
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        
        return {'message': 'created', 'id': new_task.id}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="任务创建失败：可能存在重复或无效的数据")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: int,
    name: Optional[str] = None,
    source_id: Optional[str] = None,
    task_type: Optional[str] = None,
    cron_expression: Optional[str] = None,
    is_active: Optional[bool] = None,
    config: Optional[dict] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """更新任务"""
    try:
        # 查询任务
        result = await db.execute(select(CrawlerTaskModel).where(CrawlerTaskModel.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务未找到")
        
        # 更新任务属性
        if name is not None:
            task.name = name
        if source_id is not None:
            # 验证source_id是否为数字
            if not source_id.isdigit():
                raise HTTPException(status_code=400, detail="source_id必须是数字")
            task.source_id = int(source_id)
        if task_type is not None:
            task.task_type = task_type
        if cron_expression is not None:
            task.cron_expression = cron_expression
        if is_active is not None:
            task.is_active = is_active
        if config is not None:
            task.config = config
        
        task.updated_at = datetime.utcnow()
        
        # 提交更改
        await db.commit()
        await db.refresh(task)
        
        return {'message': 'updated', 'id': task_id}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="任务更新失败：可能存在重复或无效的数据")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新任务失败: {str(e)}")


@router.post("/{task_id}/trigger", response_model=dict)
async def trigger_task(task_id: int, db: AsyncSession = Depends(get_async_db)):
    """手动触发任务"""
    try:
        # 查询任务
        result = await db.execute(select(CrawlerTaskModel).where(CrawlerTaskModel.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务未找到")
        
        # 更新任务状态为运行中
        task.status = 'running'
        task.last_run_time = datetime.utcnow()
        task.run_count = (task.run_count or 0) + 1
        task.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(task)
        
        # 这里应该启动实际的爬虫任务，但为了简化，我们只是模拟
        # 在实际实现中，这里会调用Celery或其他任务队列
        
        return {'message': 'triggered', 'id': task_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"触发任务失败: {str(e)}")


@router.get("/{task_id}/logs", response_model=List[dict])
async def get_logs(task_id: int, db: AsyncSession = Depends(get_async_db)):
    """获取任务执行日志"""
    try:
        # 查询任务日志
        result = await db.execute(
            select(CrawlerLogModel)
            .where(CrawlerLogModel.task_id == task_id)
            .order_by(CrawlerLogModel.created_at.desc())
        )
        logs = result.scalars().all()
        
        # 转换为前端需要的格式
        log_list = []
        for log in logs:
            log_list.append({
                'id': log.id,
                'task_id': log.task_id,
                'status': log.status,
                'records_processed': log.records_processed or 0,
                'records_success': log.records_success or 0,
                'records_failed': log.records_failed or 0,
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'error_msg': log.error_msg
            })
        
        return log_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")


@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_db)):
    """删除任务"""
    try:
        # 查询任务
        result = await db.execute(select(CrawlerTaskModel).where(CrawlerTaskModel.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务未找到")
        
        # 删除任务
        await db.delete(task)
        await db.commit()
        
        return {'message': 'deleted', 'id': task_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get("/statistics", response_model=dict)
async def get_statistics(db: AsyncSession = Depends(get_async_db)):
    """获取任务统计信息"""
    try:
        # 查询所有任务
        result = await db.execute(select(CrawlerTaskModel))
        tasks = result.scalars().all()
        
        # 统计信息
        total_tasks = len(tasks)
        running_tasks = sum(1 for t in tasks if t.status == 'running')
        success_tasks = sum(t.success_count or 0 for t in tasks)
        failed_tasks = sum(t.error_count or 0 for t in tasks)
        
        return {
            'totalTasks': total_tasks,
            'runningTasks': running_tasks,
            'successTasks': success_tasks,
            'failedTasks': failed_tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/batch-delete", response_model=dict)
async def batch_delete_tasks(ids: List[int], db: AsyncSession = Depends(get_async_db)):
    """批量删除任务"""
    try:
        # 删除所有指定ID的任务
        stmt = delete(CrawlerTaskModel).where(CrawlerTaskModel.id.in_(ids))
        result = await db.execute(stmt)
        
        await db.commit()
        
        return {'message': 'batch deleted', 'count': result.rowcount}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除任务失败: {str(e)}")