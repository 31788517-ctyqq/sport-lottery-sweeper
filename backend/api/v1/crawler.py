"""
爬虫管理API接口
提供数据源管理、任务调度、情报分析等功能的后端接口
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ...core.database import get_db
from ...core.auth import get_current_admin_user
from ...models.admin_user import AdminUser
from ...models.crawler_config import CrawlerConfig
from ...schemas.crawler import (
    CrawlerSourceCreate, CrawlerSourceUpdate, CrawlerSourceResponse,
    CrawlerTaskCreate, CrawlerTaskUpdate, CrawlerTaskResponse,
    CrawlerIntelligenceStats, CrawlerIntelligenceData, CrawlerIntelligenceResponse,
    CrawlerConfigCreate, CrawlerConfigUpdate, CrawlerConfigResponse,
    TrendAnalysisData, ErrorDistributionData
)
from ...services.crawler_config_service import CrawlerService
from ...services.crawler_service import BaseCrawlerService as DataSourceService
from ...services.crawler_service import BaseCrawlerService as TaskSchedulerService
from ...services.crawler_service import BaseCrawlerService as IntelligenceService

# 创建爬虫路由
router = APIRouter(tags=["crawler"])

# ==================== 数据源管理 APIs ====================

@router.get("/sources", response_model=List[CrawlerSourceResponse])
async def get_crawler_sources(
    status: Optional[str] = Query(None, description="数据源状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取数据源列表
    
    Args:
        status: 状态筛选（online/offline）
        search: 搜索关键词
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[CrawlerSourceResponse]: 数据源列表
    """
    service = DataSourceService(db)
    sources = service.get_sources(
        status=status,
        search=search,
        page=page,
        page_size=page_size
    )
    return sources


@router.get("/sources/{source_id}", response_model=CrawlerSourceResponse)
async def get_crawler_source(
    source_id: int = Path(..., description="数据源ID"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取数据源详情
    
    Args:
        source_id: 数据源ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerSourceResponse: 数据源详情
    """
    service = DataSourceService(db)
    source = service.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )
    return source


@router.post("/sources", response_model=CrawlerSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_crawler_source(
    source_data: CrawlerSourceCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    创建数据源
    
    Args:
        source_data: 数据源创建数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerSourceResponse: 创建的数据源
    """
    service = DataSourceService(db)
    try:
        source = service.create_source(source_data, current_user.id)
        return source
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/sources/{source_id}", response_model=CrawlerSourceResponse)
async def update_crawler_source(
    source_id: int,
    source_data: CrawlerSourceUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    更新数据源
    
    Args:
        source_id: 数据源ID
        source_data: 数据源更新数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerSourceResponse: 更新后的数据源
    """
    service = DataSourceService(db)
    source = service.update_source(source_id, source_data, current_user.id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )
    return source


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crawler_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    删除数据源
    
    Args:
        source_id: 数据源ID
        db: 数据库会话
        current_user: 当前管理员用户
    """
    service = DataSourceService(db)
    success = service.delete_source(source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )


@router.post("/sources/{source_id}/health", response_model=dict)
async def check_source_health(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    检查数据源健康状态
    
    Args:
        source_id: 数据源ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 健康检查结果
    """
    service = DataSourceService(db)
    health_result = service.check_health(source_id)
    return health_result


@router.put("/sources/{source_id}/status")
async def update_source_status(
    source_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    更新数据源状态
    
    Args:
        source_id: 数据源ID
        status_data: 状态数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = DataSourceService(db)
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态参数不能为空"
        )
    
    success = service.update_status(source_id, new_status, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )
    
    return {"message": f"数据源状态已更新为 {new_status}"}


@router.put("/sources/batch/enable")
async def batch_enable_sources(
    source_ids: List[int],
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    批量启用数据源
    
    Args:
        source_ids: 数据源ID列表
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = DataSourceService(db)
    count = service.batch_update_status(source_ids, "online", current_user.id)
    return {"message": f"成功启用 {count} 个数据源"}


@router.put("/sources/batch/disable")
async def batch_disable_sources(
    source_ids: List[int],
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    批量停用数据源
    
    Args:
        source_ids: 数据源ID列表
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = DataSourceService(db)
    count = service.batch_update_status(source_ids, "offline", current_user.id)
    return {"message": f"成功停用 {count} 个数据源"}


@router.post("/sources/batch/test")
async def batch_test_sources(
    source_ids: List[int],
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    批量测试数据源连接
    
    Args:
        source_ids: 数据源ID列表
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 测试结果
    """
    service = DataSourceService(db)
    results = service.batch_test_connections(source_ids)
    return results


@router.get("/sources/export")
async def export_source_report(
    format: str = Query("csv", description="导出格式"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    导出数据源报告
    
    Args:
        format: 导出格式
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        StreamingResponse: 文件流
    """
    service = DataSourceService(db)
    report_data = service.export_report(format)
    
    # TODO: 实现文件导出逻辑
    return {"message": "导出功能开发中", "data": report_data}


# ==================== 任务调度 APIs ====================

@router.get("/tasks", response_model=List[CrawlerTaskResponse])
async def get_crawler_tasks(
    status: Optional[str] = Query(None, description="任务状态筛选"),
    source_id: Optional[int] = Query(None, description="数据源ID筛选"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取任务列表
    
    Args:
        status: 状态筛选
        source_id: 数据源ID筛选
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[CrawlerTaskResponse]: 任务列表
    """
    service = TaskSchedulerService(db)
    tasks = service.get_tasks(
        status=status,
        source_id=source_id,
        page=page,
        page_size=page_size
    )
    return tasks


@router.post("/tasks", response_model=CrawlerTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_crawler_task(
    task_data: CrawlerTaskCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    创建爬虫任务
    
    Args:
        task_data: 任务创建数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerTaskResponse: 创建的任务
    """
    service = TaskSchedulerService(db)
    try:
        task = service.create_task(task_data, current_user.id)
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    更新任务状态
    
    Args:
        task_id: 任务ID
        status_data: 状态数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = TaskSchedulerService(db)
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态参数不能为空"
        )
    
    success = service.update_task_status(task_id, new_status, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    return {"message": f"任务状态已更新为 {new_status}"}


@router.post("/tasks/{task_id}/trigger")
async def trigger_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    手动触发任务执行
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 执行结果
    """
    service = TaskSchedulerService(db)
    result = service.trigger_task(task_id, current_user.id)
    return result


@router.get("/tasks/{task_id}/logs")
async def get_task_logs(
    task_id: int,
    limit: int = Query(100, description="日志条数限制"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取任务执行日志
    
    Args:
        task_id: 任务ID
        limit: 日志条数限制
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[dict]: 日志列表
    """
    service = TaskSchedulerService(db)
    logs = service.get_task_logs(task_id, limit)
    return logs


# ==================== 数据情报 APIs ====================

@router.get("/intelligence/stats", response_model=CrawlerIntelligenceStats)
async def get_intelligence_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取数据情报统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerIntelligenceStats: 统计信息
    """
    service = IntelligenceService(db)
    stats = service.get_stats()
    return stats


@router.get("/intelligence/data", response_model=List[CrawlerIntelligenceData])
async def get_intelligence_data(
    source_id: Optional[int] = Query(None, description="数据源ID筛选"),
    category: Optional[str] = Query(None, description="情报分类筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取数据情报列表
    
    Args:
        source_id: 数据源ID筛选
        category: 情报分类筛选
        status: 状态筛选
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[CrawlerIntelligenceData]: 情报数据列表
    """
    service = IntelligenceService(db)
    data = service.get_intelligence_data(
        source_id=source_id,
        category=category,
        status=status,
        page=page,
        page_size=page_size
    )
    return data


@router.get("/intelligence/trend", response_model=TrendAnalysisData)
async def get_trend_analysis(
    days: int = Query(7, description="分析天数", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取趋势分析数据
    
    Args:
        days: 分析天数
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        TrendAnalysisData: 趋势分析数据
    """
    service = IntelligenceService(db)
    trend_data = service.get_trend_analysis(days)
    return trend_data


@router.put("/intelligence/{intelligence_id}/mark-invalid")
async def mark_intelligence_invalid(
    intelligence_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    标记情报为无效
    
    Args:
        intelligence_id: 情报ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = IntelligenceService(db)
    success = service.mark_as_invalid(intelligence_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="情报不存在"
        )
    return {"message": "情报已标记为无效"}


@router.post("/intelligence/{intelligence_id}/recrawl")
async def recrawl_intelligence(
    intelligence_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    重新抓取指定情报数据
    
    Args:
        intelligence_id: 情报ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = IntelligenceService(db)
    result = service.recrawl_data(intelligence_id, current_user.id)
    return result


@router.put("/intelligence/batch-mark")
async def batch_mark_intelligence(
    mark_data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    批量标记情报数据
    
    Args:
        mark_data: 标记数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = IntelligenceService(db)
    ids = mark_data.get("ids", [])
    status = mark_data.get("status")
    
    if not ids or not status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="参数不完整"
        )
    
    count = service.batch_mark_data(ids, status, current_user.id)
    return {"message": f"成功标记 {count} 条情报数据"}


@router.get("/intelligence/export")
async def export_intelligence_data(
    format: str = Query("csv", description="导出格式"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    导出数据情报
    
    Args:
        format: 导出格式
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        StreamingResponse: 文件流
    """
    service = IntelligenceService(db)
    export_data = service.export_data(format)
    
    # TODO: 实现文件导出逻辑
    return {"message": "导出功能开发中", "data": export_data}


# ==================== 爬虫配置 APIs ====================

@router.get("/configs", response_model=List[CrawlerConfigResponse])
async def get_crawler_configs(
    config_type: Optional[str] = Query(None, description="配置类型筛选"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取爬虫配置列表
    
    Args:
        config_type: 配置类型筛选
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[CrawlerConfigResponse]: 配置列表
    """
    service = CrawlerService(db)
    configs = service.get_configs(config_type)
    return configs


@router.post("/configs", response_model=CrawlerConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_crawler_config(
    config_data: CrawlerConfigCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    创建爬虫配置
    
    Args:
        config_data: 配置创建数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerConfigResponse: 创建的配置
    """
    service = CrawlerService(db)
    try:
        config = service.create_config(config_data, current_user.id)
        return config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/configs/{config_id}", response_model=CrawlerConfigResponse)
async def update_crawler_config(
    config_id: int,
    config_data: CrawlerConfigUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    更新爬虫配置
    
    Args:
        config_id: 配置ID
        config_data: 配置更新数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        CrawlerConfigResponse: 更新后的配置
    """
    service = CrawlerService(db)
    config = service.update_config(config_id, config_data, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    return config


@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crawler_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    删除爬虫配置
    
    Args:
        config_id: 配置ID
        db: 数据库会话
        current_user: 当前管理员用户
    """
    service = CrawlerService(db)
    success = service.delete_config(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )


# 路由已在 create_api_router() 中自动注册，无需额外操作
pass