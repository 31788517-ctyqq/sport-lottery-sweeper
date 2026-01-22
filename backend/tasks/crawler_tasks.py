"""
数据爬取任务
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import Task
from backend.tasks import DatabaseTask, celery_app
from backend.services.crawler_service import CrawlerService
from backend.services.match_service import MatchService
from backend.core.database import SessionLocal


class CrawlerTask(Task):
    def __init__(self):
        self.crawler_service = CrawlerService()
        self.match_service = MatchService()


@celery_app.task(base=CrawlerTask, bind=True)
def run_crawling_task(self, source_type: str, params: dict = None):
    """执行爬取任务"""
    result = self.crawler_service.crawl(source_type, params)
    return result


logger = logging.getLogger(__name__)

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks.crawl_all_leagues")
def crawl_all_leagues(self, days_ahead: int = 3):
    """
    爬取所有联赛的比赛数据任务
    
    Args:
        days_ahead: 爬取未来几天的比赛
    """
    logger.info(f"开始爬取所有联赛的比赛数据，未来{days_ahead}天")
    
    try:
        db = self.db
        crawler_service = CrawlerService(db)
        match_service = MatchService(db)
        
        # 获取所有活跃联赛
        leagues = match_service.get_active_leagues()
        
        total_crawled = 0
        errors = []
        
        for league in leagues:
            try:
                # 异步爬取联赛数据
                matches_data = asyncio.run(
                    crawler_service.async_crawl_matches(league.code, days_ahead)
                )
                
                for match_data in matches_data:
                    try:
                        # 处理比赛数据
                        result = match_service.create_or_update_match(match_data)
                        if result["created"] or result["updated"]:
                            total_crawled += 1
                    except Exception as e:
                        errors.append(f"处理比赛数据失败: {str(e)}")
                
            except Exception as e:
                errors.append(f"爬取联赛 {league.name} 失败: {str(e)}")
        
        logger.info(f"所有联赛数据爬取完成: 爬取={total_crawled}")
        
        return {
            "success": True,
            "message": "联赛数据爬取完成",
            "crawled": total_crawled,
            "errors": len(errors),
            "error_messages": errors[:10]
        }
        
    except Exception as e:
        logger.error(f"所有联赛数据爬取任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "crawled": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks.crawl_specific_source")
def crawl_specific_source(self, source_code: str, match_id: Optional[int] = None):
    """
    爬取特定来源的数据任务
    
    Args:
        source_code: 来源代码
        match_id: 比赛ID（可选，为None时爬取所有相关比赛）
    """
    logger.info(f"开始爬取特定来源的数据，来源: {source_code}")
    
    try:
        db = self.db
        crawler_service = CrawlerService(db)
        match_service = MatchService(db)
        
        if match_id:
            # 爬取特定比赛的数据
            match = match_service.get_match_by_id(match_id)
            if not match:
                return {
                    "success": False,
                    "message": f"比赛不存在: {match_id}"
                }
            
            # 爬取该比赛的数据
            data = crawler_service.crawl_from_source(source_code, match.external_id)
            
            # 处理数据
            processed = crawler_service.process_crawled_data(data, source_code, match.id)
            
            logger.info(f"特定比赛数据爬取完成: 来源={source_code}, 比赛={match_id}, 处理={processed}")
            
            return {
                "success": True,
                "message": "比赛数据爬取完成",
                "source": source_code,
                "match_id": match_id,
                "processed": processed
            }
        else:
            # 爬取所有相关比赛的数据
            # 获取最近24小时内即将开始的比赛
            from_time = datetime.utcnow()
            to_time = from_time + timedelta(hours=24)
            
            matches = match_service.get_matches_by_time_range(from_time, to_time)
            
            total_processed = 0
            errors = []
            
            for match in matches:
                try:
                    # 爬取数据
                    data = crawler_service.crawl_from_source(source_code, match.external_id)
                    
                    # 处理数据
                    processed = crawler_service.process_crawled_data(data, source_code, match.id)
                    total_processed += processed
                    
                except Exception as e:
                    errors.append(f"爬取比赛 {match.id} 数据失败: {str(e)}")
            
            logger.info(f"特定来源数据爬取完成: 来源={source_code}, 处理={total_processed}")
            
            return {
                "success": True,
                "message": "来源数据爬取完成",
                "source": source_code,
                "processed": total_processed,
                "errors": len(errors)
            }
        
    except Exception as e:
        logger.error(f"特定来源数据爬取任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "source": source_code,
            "processed": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks.crawl_odds_data")
def crawl_odds_data(self, match_id: Optional[int] = None):
    """
    爬取赔率数据任务
    
    Args:
        match_id: 比赛ID（可选，为None时爬取所有即将开始的比赛）
    """
    logger.info("开始爬取赔率数据")
    
    try:
        db = self.db
        crawler_service = CrawlerService(db)
        match_service = MatchService(db)
        
        if match_id:
            # 爬取特定比赛的赔率
            match = match_service.get_match_by_id(match_id)
            if not match:
                return {
                    "success": False,
                    "message": f"比赛不存在: {match_id}"
                }
            
            # 爬取赔率数据
            odds_data = crawler_service.crawl_odds_data(match.external_id)
            
            # 更新比赛赔率数据
            if odds_data:
                match_service.update_match_odds(match_id, odds_data)
                logger.info(f"赔率数据爬取完成: 比赛={match_id}, 赔率源={len(odds_data)}")
                
                return {
                    "success": True,
                    "message": "赔率数据爬取完成",
                    "match_id": match_id,
                    "odds_sources": len(odds_data)
                }
            else:
                return {
                    "success": False,
                    "message": "未获取到赔率数据",
                    "match_id": match_id
                }
        else:
            # 爬取所有即将开始比赛的赔率
            # 获取未来24小时内即将开始的比赛
            from_time = datetime.utcnow()
            to_time = from_time + timedelta(hours=24)
            
            matches = match_service.get_matches_by_time_range(from_time, to_time)
            
            updated = 0
            errors = []
            
            for match in matches:
                try:
                    # 爬取赔率数据
                    odds_data = crawler_service.crawl_odds_data(match.external_id)
                    
                    # 更新比赛赔率数据
                    if odds_data:
                        match_service.update_match_odds(match.id, odds_data)
                        updated += 1
                        
                except Exception as e:
                    errors.append(f"爬取比赛 {match.id} 赔率失败: {str(e)}")
            
            logger.info(f"赔率数据爬取完成: 更新={updated}")
            
            return {
                "success": True,
                "message": "赔率数据爬取完成",
                "updated": updated,
                "errors": len(errors)
            }
        
    except Exception as e:
        logger.error(f"赔率数据爬取任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "updated": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks.test_crawler_source")
def test_crawler_source(self, source_code: str):
    """
    测试爬虫来源任务
    
    测试特定来源的爬虫是否正常工作
    
    Args:
        source_code: 来源代码
    """
    logger.info(f"开始测试爬虫来源: {source_code}")
    
    try:
        db = self.db
        crawler_service = CrawlerService(db)
        
        # 测试爬虫
        result = crawler_service.test_crawler_source(source_code)
        
        logger.info(f"爬虫来源测试完成: 来源={source_code}, 成功={result.get('success', False)}")
        
        return result
        
    except Exception as e:
        logger.error(f"爬虫来源测试任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "source": source_code
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.crawler_tasks.monitor_crawler_health")
def monitor_crawler_health(self):
    """
    监控爬虫健康状态任务
    
    检查所有爬虫来源的健康状态
    """
    logger.info("开始监控爬虫健康状态")
    
    try:
        db = self.db
        crawler_service = CrawlerService(db)
        
        # 检查所有来源的健康状态
        health_status = crawler_service.check_all_sources_health()
        
        healthy_count = sum(1 for status in health_status.values() if status.get("healthy", False))
        total_count = len(health_status)
        
        logger.info(f"爬虫健康状态监控完成: 健康={healthy_count}/{total_count}")
        
        return {
            "success": True,
            "message": "爬虫健康状态监控完成",
            "total_sources": total_count,
            "healthy_sources": healthy_count,
            "health_status": health_status
        }
        
    except Exception as e:
        logger.error(f"爬虫健康状态监控任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "total_sources": 0,
            "healthy_sources": 0,
            "health_status": {}
        }