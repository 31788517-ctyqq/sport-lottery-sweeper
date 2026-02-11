"""
任务管理API
提供任务的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta
from sqlalchemy import func

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.models.data_sources import DataSource
from backend.services.task_scheduler_service import TaskSchedulerService

# 设置router前缀为"",因为我们将在main.py中指定完整路径
router = APIRouter(prefix="", tags=["task-management"])

def _normalize_config(value):
    if isinstance(value, (dict, list)):
        return value
    if value in (None, "", "{}"):
        return {}
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return {}

# 首先定义根路径路由，以确保它优先于带路径参数的路由

@router.get("")
async def get_crawler_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),  # 修改为str类型以匹配前端传入
    db: Session = Depends(get_db)
):
    """
    获取爬虫任务列表，支持分页和筛选
    """
    try:
        # 构建查询
        query = db.query(CrawlerTask)
        
        # 应用筛选条件
        if name:
            query = query.filter(CrawlerTask.name.contains(name))
        if task_type:
            # 处理大小写不敏感的任务类型筛选
            query = query.filter(func.lower(CrawlerTask.task_type) == func.lower(task_type))
        if status:
            # 处理大小写不敏感的状态筛选
            query = query.filter(func.lower(CrawlerTask.status) == func.lower(status))
        if source_id:  # 现在source_id是字符串类型，需要转换
            if source_id.isdigit():
                query = query.filter(CrawlerTask.source_id == int(source_id))
        
        # 按创建时间倒序排列，使新任务在前
        query = query.order_by(CrawlerTask.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * size
        tasks = query.offset(offset).limit(size).all()
        
        # 转换为字典格式并处理JSON字段
        items_data = []
        for task in tasks:
            task_dict = {
                'id': task.id,
                'name': task.name,
                'source_id': str(task.source_id),  # 将整型source_id转换为字符串
                'task_type': task.task_type,
                'cron_expression': task.cron_expression,
                'is_active': task.is_active,
                'status': task.status,
                'last_run_time': task.last_run_time.isoformat() if task.last_run_time else None,
                'next_run_time': task.next_run_time.isoformat() if task.next_run_time else None,
                'run_count': task.run_count,
                'success_count': task.success_count,
                'error_count': task.error_count,
                'config': _normalize_config(task.config),  # 将JSON字符串转换为字典
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            }
            items_data.append(task_dict)
        
        return {
            "success": True,
            "data": {
                "items": items_data,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "任务列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_crawler_task(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    创建爬虫任务
    """
    try:
        # 从请求体中提取数据
        name = request_data.get('name')
        source_id = request_data.get('source_id')
        task_type = request_data.get('task_type', 'crawl')
        cron_expression = request_data.get('cron_expression')
        config = request_data.get('config', '{}')
        
        if not name or not source_id or not cron_expression:
            raise HTTPException(status_code=400, detail="缺少必需字段: name, source_id, cron_expression")
        
        # 如果source_id是数字字符串，则转换为整数
        source_id_value = int(source_id) if str(source_id).isdigit() else source_id
        
        # 确保config是有效的JSON字符串，如果不是则使用默认值
        try:
            if config and config != "{}":
                json.loads(config)  # 验证是否为有效JSON
        except (TypeError, ValueError):
            config = "{}"
        
        # 创建任务对象
        new_task = CrawlerTask(
            name=name,
            source_id=source_id_value,
            task_type=task_type,
            cron_expression=cron_expression,
            config=config,
            is_active=True,
            status='stopped',
            run_count=0,
            success_count=0,
            error_count=0
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        # 转换为字典格式
        task_dict = {
            'id': new_task.id,
            'name': new_task.name,
            'source_id': new_task.source_id,
            'task_type': new_task.task_type,
            'cron_expression': new_task.cron_expression,
            'is_active': new_task.is_active,
            'status': new_task.status,
            'last_run_time': new_task.last_run_time.isoformat() if new_task.last_run_time else None,
            'next_run_time': new_task.next_run_time.isoformat() if new_task.next_run_time else None,
            'run_count': new_task.run_count,
            'success_count': new_task.success_count,
            'error_count': new_task.error_count,
            'config': _normalize_config(new_task.config),
            'created_at': new_task.created_at.isoformat() if new_task.created_at else None,
            'updated_at': new_task.updated_at.isoformat() if new_task.updated_at else None
        }
        
        return {
            "success": True,
            "data": task_dict,
            "message": "任务创建成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 然后定义具体路径路由

@router.get("/statistics")
async def get_task_statistics(db: Session = Depends(get_db)):
    """
    获取任务统计数据
    """
    try:
        print("开始获取统计数据...")
        
        # 总任务数
        total_tasks = db.query(CrawlerTask).count()
        print(f"总任务数: {total_tasks}")
        
        # 按状态统计，过滤掉NULL状态
        status_results = db.query(CrawlerTask.status, func.count(CrawlerTask.id)).\
            filter(CrawlerTask.status.isnot(None)).\
            group_by(CrawlerTask.status).all()
        
        # 将结果转换为字典，确保没有None键
        status_dict = {}
        for status, count in status_results:
            if status is not None:
                status_dict[str(status)] = int(count)  # 显式转换为基本类型
                
        print(f"状态统计: {status_dict}")
        
        # 按类型统计，过滤掉NULL类型
        type_results = db.query(CrawlerTask.task_type, func.count(CrawlerTask.id)).\
            filter(CrawlerTask.task_type.isnot(None)).\
            group_by(CrawlerTask.task_type).all()
        
        # 将结果转换为字典，确保没有None键
        type_dict = {}
        for task_type, count in type_results:
            if task_type is not None:
                type_dict[str(task_type)] = int(count)  # 显式转换为基本类型
                
        print(f"类型统计: {type_dict}")
        
        # 获取所有最近7天运行过的任务，手动按日期分组
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        print(f"查询最近7天的数据，从: {seven_days_ago}")
        
        recent_tasks = db.query(CrawlerTask).filter(
            CrawlerTask.last_run_time >= seven_days_ago,
            CrawlerTask.last_run_time.isnot(None)
        ).all()
        
        # 手动按日期分组统计
        date_counts = {}
        for task in recent_tasks:
            if task.last_run_time:
                date_key = task.last_run_time.strftime('%Y-%m-%d')
                date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        recent_executions_list = [
            {"date": date, "count": count}
            for date, count in sorted(date_counts.items())  # 按日期排序
        ]
        
        print(f"最近执行情况: {recent_executions_list}")
        
        return {
            "success": True,
            "data": {
                "totalTasks": int(total_tasks),  # 显式转换为基本类型
                "statusStats": status_dict,
                "typeStats": type_dict,
                "recentExecutions": recent_executions_list
            },
            "message": "统计数据获取成功"
        }
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")  # 添加打印错误信息
        import traceback
        traceback.print_exc()  # 打印完整的错误追踪
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.post("/batch-delete")
async def batch_delete_crawler_tasks(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    批量删除爬虫任务
    """
    try:
        print(f"DEBUG: 后端接收到的请求数据: {request_data}")
        
        # 从请求体中提取task_ids
        task_ids = request_data.get('task_ids', [])
        
        print(f"DEBUG: 提取的task_ids: {task_ids}, 类型: {type(task_ids)}")
        
        if not task_ids:
            raise HTTPException(status_code=400, detail="task_ids不能为空")
        
        if not isinstance(task_ids, list):
            raise HTTPException(status_code=400, detail="task_ids必须是一个数组")
        
        # 查询要删除的任务
        tasks = db.query(CrawlerTask).filter(CrawlerTask.id.in_(task_ids)).all()
        
        print(f"DEBUG: 查询到的任务: {len(tasks)} 个")
        
        if not tasks:
            raise HTTPException(status_code=404, detail="未找到任何要删除的任务")
        
        # 删除任务
        deleted_count = 0
        for task in tasks:
            db.delete(task)
            deleted_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "deleted_count": deleted_count,
                "deleted_ids": [task.id for task in tasks]
            },
            "message": f"成功删除 {deleted_count} 个任务"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"DEBUG: 批量删除任务时发生异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量删除任务失败: {str(e)}")

# 最后定义带路径参数的路由

# 获取单个任务详情
@router.get("/{task_id}")
async def get_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个任务详情
    """
    try:
        task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 转换为字典格式
        task_dict = {
            'id': task.id,
            'name': task.name,
            'source_id': task.source_id,
            'task_type': task.task_type,
            'cron_expression': task.cron_expression,
            'is_active': task.is_active,
            'status': task.status,
            'last_run_time': task.last_run_time.isoformat() if task.last_run_time else None,
            'next_run_time': task.next_run_time.isoformat() if task.next_run_time else None,
            'run_count': task.run_count,
            'success_count': task.success_count,
            'error_count': task.error_count,
            'config': _normalize_config(task.config),
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        }
        
        return {
            "success": True,
            "data": task_dict,
            "message": "任务详情获取成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}")
async def update_crawler_task(
    task_id: int,
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    更新爬虫任务
    """
    try:
        task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 从请求体中提取数据
        name = request_data.get('name')
        source_id = request_data.get('source_id')
        cron_expression = request_data.get('cron_expression')
        is_active = request_data.get('is_active')
        
        # 更新字段
        if name is not None:
            task.name = name
        if source_id is not None:
            # 如果source_id是数字字符串，则转换为整数
            task.source_id = int(source_id) if str(source_id).isdigit() else source_id
        if cron_expression is not None:
            task.cron_expression = cron_expression
        if is_active is not None:
            task.is_active = is_active
            
        db.commit()
        db.refresh(task)
        
        # 转换为字典格式
        task_dict = {
            'id': task.id,
            'name': task.name,
            'source_id': task.source_id,
            'task_type': task.task_type,
            'cron_expression': task.cron_expression,
            'is_active': task.is_active,
            'status': task.status,
            'last_run_time': task.last_run_time.isoformat() if task.last_run_time else None,
            'next_run_time': task.next_run_time.isoformat() if task.next_run_time else None,
            'run_count': task.run_count,
            'success_count': task.success_count,
            'error_count': task.error_count,
            'config': _normalize_config(task.config),
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        }
        
        return {
            "success": True,
            "data": task_dict,
            "message": "任务更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    删除爬虫任务
    """
    try:
        task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        db.delete(task)
        db.commit()
        
        return {
            "success": True,
            "data": {"id": task_id},
            "message": "任务删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/trigger")
async def trigger_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    立即触发爬虫任务执行
    """
    try:
        task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 使用任务调度服务来触发任务 - 传递db参数
        scheduler_service = TaskSchedulerService(db)
        result = scheduler_service.trigger_task(task_id, triggered_by=1)  # 假设触发者ID为1
        
        # 更新任务状态
        task.status = 'RUNNING'
        task.last_run_time = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "data": {
                "id": task.id,
                "status": task.status,
                "last_run_time": task.last_run_time.isoformat() if task.last_run_time else None
            },
            "message": "任务触发成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发任务失败: {str(e)}")

@router.post("/{task_id}/stop")
async def stop_crawler_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    停止爬虫任务执行
    """
    try:
        task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 使用任务调度服务来停止任务
        scheduler_service = TaskSchedulerService(db)
        result = scheduler_service.stop_task(task_id)
        
        # 更新任务状态
        task.status = 'STOPPED'
        task.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "data": {
                "id": task.id,
                "status": task.status,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            },
            "message": "任务停止成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止任务失败: {str(e)}")

@router.get("/{task_id}/logs")
async def get_crawler_task_logs(
    task_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取爬虫任务执行日志
    """
    try:
        from backend.models.crawler_logs import CrawlerTaskLog
        
        # 计算偏移量
        offset = (page - 1) * size
        
        # 查询任务的日志记录
        logs = db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.task_id == task_id
        ).order_by(CrawlerTaskLog.created_at.desc()).offset(offset).limit(size).all()
        
        # 查询总记录数
        total = db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.task_id == task_id
        ).count()
        
        # 转换日志数据格式
        logs_data = []
        for log in logs:
            # 构造消息内容
            message_parts = []
            if log.status:
                message_parts.append(log.status.upper())
            if log.error_message:
                message_parts.append(f"错误: {log.error_message}")
            else:
                message_parts.append(f"处理了{log.records_processed or 0}条记录，成功{log.records_success or 0}条，失败{log.records_failed or 0}条")
            
            log_dict = {
                'id': log.id,
                'task_id': log.task_id,
                'status': log.status,
                'message': ' - '.join(message_parts),
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'records_processed': log.records_processed or 0,
                'records_success': log.records_success or 0,
                'records_failed': log.records_failed or 0,
                'error_message': log.error_message
            }
            logs_data.append(log_dict)
        
        return {
            "success": True,
            "data": {
                "items": logs_data,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "日志获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务日志失败: {str(e)}")
