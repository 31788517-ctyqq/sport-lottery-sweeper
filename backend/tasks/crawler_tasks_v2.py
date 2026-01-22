"""
爬虫任务模块（重构版）
优化了并发性能和错误处理
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import shared_task

from backend.tasks import DatabaseTask
from backend.scrapers.coordinator import get_coordinator, close_coordinator

logger = logging.getLogger(__name__)


@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks_v2.crawl_all_leagues_concurrent")
def crawl_all_leagues_concurrent(self, days_ahead: int = 3):
    """
    并发爬取所有联赛的比赛数据任务（优化版）
    
    改进:
    - 使用 asyncio.gather 并发执行
    - 更好的错误处理
    - 任务超时控制
    
    Args:
        days_ahead: 爬取未来几天的比赛
    """
    logger.info(f"开始并发爬取所有联赛数据，未来 {days_ahead} 天")
    
    try:
        # 运行异步任务
        result = asyncio.run(_crawl_leagues_async(self.db, days_ahead))
        
        logger.info(
            f"所有联赛数据爬取完成: "
            f"成功={result['crawled']}, "
            f"失败={result['errors']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"并发爬取任务失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "crawled": 0,
            "errors": 1
        }
    finally:
        # 清理资源
        asyncio.run(close_coordinator())


async def _crawl_leagues_async(db, days_ahead: int) -> Dict[str, Any]:
    """
    异步爬取联赛数据
    
    并发策略:
    - 使用 asyncio.gather 同时爬取多个联赛
    - 设置超时以防止单个联赛阻塞整个任务
    """
    from backend.services.match_service import MatchService
    
    match_service = MatchService(db)
    coordinator = await get_coordinator()
    
    # 获取所有活跃联赛
    leagues = match_service.get_active_leagues()
    
    if not leagues:
        logger.warning("没有活跃的联赛")
        return {
            "success": True,
            "message": "没有活跃的联赛",
            "crawled": 0,
            "errors": 0
        }
    
    # 创建并发任务
    tasks = [
        _crawl_single_league(coordinator, match_service, league, days_ahead)
        for league in leagues
    ]
    
    # 并发执行，设置超时
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=300  # 5分钟总超时
        )
    except asyncio.TimeoutError:
        logger.error("爬取任务超时")
        results = []
    
    # 汇总结果
    total_crawled = 0
    total_errors = 0
    error_messages = []
    
    for result in results:
        if isinstance(result, Exception):
            total_errors += 1
            error_messages.append(str(result))
        elif isinstance(result, dict):
            total_crawled += result.get('crawled', 0)
            total_errors += result.get('errors', 0)
            error_messages.extend(result.get('error_messages', []))
    
    return {
        "success": True,
        "message": "联赛数据爬取完成",
        "crawled": total_crawled,
        "errors": total_errors,
        "error_messages": error_messages[:10],  # 只保留前10个错误
        "leagues_processed": len(leagues)
    }


async def _crawl_single_league(
    coordinator,
    match_service,
    league,
    days_ahead: int
) -> Dict[str, Any]:
    """
    爬取单个联赛的数据
    
    Args:
        coordinator: 爬虫协调器
        match_service: 比赛服务
        league: 联赛对象
        days_ahead: 未来天数
        
    Returns:
        爬取结果统计
    """
    try:
        logger.info(f"开始爬取联赛: {league.name}")
        
        # 获取比赛数据
        matches_data = await coordinator.get_matches(days=days_ahead)
        
        # 过滤出当前联赛的比赛
        league_matches = [
            match for match in matches_data
            if match.get('league') == league.name or league.code in match.get('league', '')
        ]
        
        crawled = 0
        errors = 0
        error_messages = []
        
        # 处理比赛数据
        for match_data in league_matches:
            try:
                result = match_service.create_or_update_match(match_data)
                if result.get("created") or result.get("updated"):
                    crawled += 1
            except Exception as e:
                errors += 1
                error_messages.append(f"处理比赛数据失败: {str(e)}")
        
        logger.info(f"联赛 {league.name} 爬取完成: 新增/更新={crawled}")
        
        return {
            "league": league.name,
            "crawled": crawled,
            "errors": errors,
            "error_messages": error_messages
        }
        
    except Exception as e:
        logger.error(f"爬取联赛 {league.name} 失败: {e}")
        return {
            "league": league.name,
            "crawled": 0,
            "errors": 1,
            "error_messages": [str(e)]
        }


@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks_v2.crawl_matches_batch")
def crawl_matches_batch(self, match_ids: List[int], days_ahead: int = 3):
    """
    批量爬取指定比赛的详细数据
    
    Args:
        match_ids: 比赛ID列表
        days_ahead: 未来天数（用于获取赔率历史）
    """
    logger.info(f"开始批量爬取 {len(match_ids)} 场比赛的详细数据")
    
    try:
        result = asyncio.run(_crawl_matches_batch_async(self.db, match_ids))
        
        logger.info(
            f"批量爬取完成: "
            f"成功={result['success_count']}, "
            f"失败={result['failed_count']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"批量爬取任务失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "success_count": 0,
            "failed_count": len(match_ids)
        }
    finally:
        asyncio.run(close_coordinator())


async def _crawl_matches_batch_async(db, match_ids: List[int]) -> Dict[str, Any]:
    """异步批量爬取比赛详情"""
    from backend.services.match_service import MatchService
    
    match_service = MatchService(db)
    coordinator = await get_coordinator()
    
    # 创建并发任务
    tasks = [
        _crawl_single_match(coordinator, match_service, match_id)
        for match_id in match_ids
    ]
    
    # 并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 统计结果
    success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    failed_count = len(results) - success_count
    
    return {
        "success": True,
        "message": "批量爬取完成",
        "success_count": success_count,
        "failed_count": failed_count,
        "total": len(match_ids)
    }


async def _crawl_single_match(
    coordinator,
    match_service,
    match_id: int
) -> Dict[str, Any]:
    """爬取单场比赛的详细数据"""
    try:
        # 获取比赛信息
        match = match_service.get_match_by_id(match_id)
        if not match:
            return {"success": False, "error": "比赛不存在"}
        
        # 获取比赛详情
        detail = await coordinator.get_match_detail(match.external_id)
        
        # 获取赔率历史
        odds_history = await coordinator.get_odds_history(match.external_id)
        
        # 更新数据库
        if detail:
            match_service.update_match_detail(match_id, detail)
        
        if odds_history:
            match_service.update_match_odds_history(match_id, odds_history)
        
        return {"success": True, "match_id": match_id}
        
    except Exception as e:
        logger.error(f"爬取比赛 {match_id} 失败: {e}")
        return {"success": False, "error": str(e)}


@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks_v2.health_check_sources")
def health_check_sources(self):
    """
    检查所有爬虫数据源的健康状态
    
    定期任务，用于监控爬虫状态
    """
    logger.info("开始检查爬虫数据源健康状态")
    
    try:
        result = asyncio.run(_health_check_async())
        
        logger.info(f"健康检查完成: {result['summary']}")
        
        return result
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"健康检查失败: {str(e)}"
        }
    finally:
        asyncio.run(close_coordinator())


async def _health_check_async() -> Dict[str, Any]:
    """异步执行健康检查"""
    coordinator = await get_coordinator()
    
    # 检查所有数据源
    health_status = await coordinator.health_check_all()
    
    # 获取统计信息
    stats = coordinator.get_stats()
    
    # 汇总结果
    healthy_count = sum(
        1 for status in health_status.values()
        if status.get('healthy', False)
    )
    total_count = len(health_status)
    
    return {
        "success": True,
        "message": "健康检查完成",
        "summary": f"{healthy_count}/{total_count} 数据源健康",
        "health_status": health_status,
        "stats": stats,
        "checked_at": datetime.now().isoformat()
    }


@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks_v2.crawl_upcoming_matches")
def crawl_upcoming_matches(self, hours: int = 24):
    """
    爬取即将开始的比赛
    
    用于高频更新（如每小时执行一次）
    
    Args:
        hours: 未来几小时内的比赛
    """
    logger.info(f"开始爬取未来 {hours} 小时内的比赛")
    
    try:
        result = asyncio.run(_crawl_upcoming_async(self.db, hours))
        
        logger.info(f"即将开始的比赛爬取完成: 更新={result['updated']}")
        
        return result
        
    except Exception as e:
        logger.error(f"爬取即将开始的比赛失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "updated": 0
        }
    finally:
        asyncio.run(close_coordinator())


async def _crawl_upcoming_async(db, hours: int) -> Dict[str, Any]:
    """异步爬取即将开始的比赛"""
    from backend.services.match_service import MatchService
    
    match_service = MatchService(db)
    coordinator = await get_coordinator()
    
    # 获取时间范围内的比赛
    from_time = datetime.utcnow()
    to_time = from_time + timedelta(hours=hours)
    
    matches = match_service.get_matches_by_time_range(from_time, to_time)
    
    if not matches:
        return {
            "success": True,
            "message": "没有即将开始的比赛",
            "updated": 0
        }
    
    # 并发更新比赛数据
    tasks = [
        _update_match_data(coordinator, match_service, match)
        for match in matches
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    updated = sum(1 for r in results if isinstance(r, dict) and r.get('updated'))
    
    return {
        "success": True,
        "message": "即将开始的比赛更新完成",
        "updated": updated,
        "total": len(matches)
    }


async def _update_match_data(coordinator, match_service, match) -> Dict[str, Any]:
    """更新单场比赛的数据"""
    try:
        # 获取最新赔率
        odds_history = await coordinator.get_odds_history(match.external_id)
        
        if odds_history and len(odds_history) > 0:
            latest_odds = odds_history[-1]
            match_service.update_match_odds(match.id, latest_odds)
            return {"updated": True, "match_id": match.id}
        
        return {"updated": False, "match_id": match.id}
        
    except Exception as e:
        logger.error(f"更新比赛 {match.id} 数据失败: {e}")
        return {"updated": False, "error": str(e)}
