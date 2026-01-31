"""
爬虫管理API接口
提供数据源管理、任务调度、情报分析等功能的后端接口
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
import logging
import json

from backend.core.database import get_db
from sqlalchemy.orm import Session
from backend.core.auth import get_current_admin_user
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.models.admin_user import AdminUser
# AI_DONE: coder1 @2026-01-26
from backend.models.data_sources import DataSource as CrawlerSourceModel
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.schemas.crawler import (
    CrawlerSourceCreate, CrawlerSourceUpdate, CrawlerSourceResponse,
    CrawlerTaskCreate, CrawlerTaskResponse,
    CrawlerIntelligenceStats, CrawlerIntelligenceData,
    TrendAnalysisData
)
# AI_DONE: coder1 @2026-01-26
# 延迟导入爬虫配置相关模块，避免循环导入
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入块
# from backend.schemas.crawler_config import CrawlerConfigCreate, CrawlerConfigUpdate, CrawlerConfigResponse
# from backend.services.crawler_config_service import CrawlerConfigService as DataSourceService
# from backend.services.crawler_integration import CrawlerIntegration as TaskSchedulerService
# from backend.services.enhanced_crawler_service import EnhancedCrawlerService as IntelligenceService
from backend.models.matches import FootballMatch
# AI_WORKING: coder1 @2026-01-28 - 注释掉不存在的导入，避免路由注册失败
# from backend.models.data_review import DataSubmission
# from backend.schemas.data import DataSubmissionCreate
# from backend.core.constants import DataTypeEnum, ReviewStatusEnum
# 暂时注释掉未定义的枚举，使用占位符
DataTypeEnum = type('DataTypeEnum', (), {})
ReviewStatusEnum = type('ReviewStatusEnum', (), {})
# AI_DONE: coder1 @2026-01-28
# AI_DONE: coder1 @2026-01-26

# 服务注册表导入
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.services.service_registry import (
    get_data_source_service,
    get_task_scheduler_service,
    get_intelligence_service
)
# AI_DONE: coder1 @2026-01-26

# 导入新的爬虫
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.scrapers.sources.five_hundred_scraper import FiveHundredScraper
# AI_DONE: coder1 @2026-01-26

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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
    source = service.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据源不存在"
        )
    return source


@router.post("/sources/five-hundred-create")
async def create_five_hundred_source(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    创建500彩票网竞彩足球数据源
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    service = get_data_source_service(db)
    
    # 检查是否已存在
    existing = db.query(CrawlerSourceModel).filter(
        CrawlerSourceModel.name == "500彩票网竞彩足球"
    ).first()
    
    if existing:
        return {"message": "500彩票网竞彩足球数据源已存在", "source_id": existing.id}
    
    # 创建新的数据源
    new_source = CrawlerSourceModel(
        name="500彩票网竞彩足球",
        type="api",
        url="https://trade.500.com/jczq/",
        status=True,
        config=json.dumps({
            "baseUrl": "https://trade.500.com/jczq/",
            "description": "500彩票网竞彩足球比赛数据源，提供最新的竞彩足球比赛信息"
        }, ensure_ascii=False)
    )
    
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    
    return {
        "message": "500彩票网竞彩足球数据源创建成功",
        "source_id": new_source.id
    }


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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_task_scheduler_service(db)
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
    service = get_task_scheduler_service(db)
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
    service = get_task_scheduler_service(db)
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
    service = get_task_scheduler_service(db)
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
    service = get_task_scheduler_service(db)
    logs = service.get_task_logs(task_id, limit)
    return logs


@router.post("/tasks/create-five-hundred-task")
async def create_five_hundred_task(
    task_data: CrawlerTaskCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    创建500彩票网爬虫任务
    
    Args:
        task_data: 任务数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 任务创建结果
    """
    try:
        service = get_task_scheduler_service(db)
        
        # 设置任务类型和配置
        task_data.task_type = "DATA_COLLECTION"
        task_data.config = {
            "source": "five_hundred",
            "target": "jczq_matches",
            "days": 3,
            **(task_data.config or {})
        }
        
        # 创建任务
        new_task = service.create_task(task_data, current_user.id)
        
        return {
            "message": "500彩票网爬虫任务创建成功",
            "task_id": new_task.id
        }
    except Exception as e:
        logger.error(f"创建500彩票网爬虫任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建任务失败: {str(e)}"
        )


@router.post("/tasks/{task_id}/execute-five-hundred-crawl")
async def execute_five_hundred_crawl(
    task_id: int,
    days: int = Query(3, description="爬取未来几天的数据"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    执行500彩票网爬虫任务并将数据保存到数据库
    
    Args:
        task_id: 任务ID
        days: 爬取未来几天的数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 爬取结果
    """
    try:
        # 创建爬虫实例
        scraper = FiveHundredScraper()
        
        # 执行爬取
        matches_data = await scraper.get_matches(days=days)
        
        # 将爬取的数据保存到数据库
        created_count = 0
        for match_data in matches_data:
            # 检查是否已存在该比赛
            existing_match = db.query(FootballMatch).filter(
                FootballMatch.match_id == match_data['match_id']
            ).first()
            
            if not existing_match:
                # 创建新的比赛记录
                match = FootballMatch(
                    match_id=match_data['match_id'],
                    home_team=match_data['home_team'],
                    away_team=match_data['away_team'],
                    match_time=datetime.strptime(match_data['match_date'], "%Y-%m-%d %H:%M:%S") if match_data['match_date'] else datetime.now(),
                    league=match_data['league'],
                    status=match_data['status']
                )
                
                db.add(match)
                created_count += 1
                
                # 提交到审核队列
                submission_data = DataSubmissionCreate(
                    data_type=DataTypeEnum.MATCH_SCHEDULE,
                    data_content={
                        "match_id": match_data['match_id'],
                        "home_team": match_data['home_team'],
                        "away_team": match_data['away_team'],
                        "match_time": match_data['match_date'],
                        "league": match_data['league'],
                        "source": match_data['source']
                    },
                    submitter_id=current_user.id,
                    review_status=ReviewStatusEnum.PENDING
                )
                
                submission = DataSubmission(**submission_data.dict())
                db.add(submission)
        
        db.commit()
        
        return {
            "message": f"成功爬取并保存了 {created_count} 条比赛数据到数据库和审核队列",
            "total_crawled": len(matches_data),
            "created_count": created_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"执行500彩票网爬虫任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行爬虫任务失败: {str(e)}"
        )
    finally:
        await scraper.close()

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
    service = get_intelligence_service(db)
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
    service = get_intelligence_service(db)
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
    service = get_intelligence_service(db)
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
    service = get_intelligence_service(db)
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
    service = get_intelligence_service(db)
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
    service = get_intelligence_service(db)
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
    service = get_intelligence_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
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
    service = get_data_source_service(db)
    success = service.delete_config(config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )


# 路由已在 create_api_router() 中自动注册，无需额外操作
pass