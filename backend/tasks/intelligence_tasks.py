"""
情报数据处理任务
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import Task, shared_task
from backend.tasks import DatabaseTask, celery_app
from backend.services.intelligence_service import IntelligenceService
from backend.services.crawler_service import CrawlerService
from backend.services.match_service import MatchService


class IntelligenceTask(Task):
    def __init__(self):
        self.intelligence_service = IntelligenceService()
        self.crawler_service = CrawlerService()
        self.match_service = MatchService()


@celery_app.task(base=IntelligenceTask, bind=True)
def run_intelligence_analysis(self, data):
    """执行智能分析任务"""
    result = self.intelligence_service.analyze(data)
    return result


logger = logging.getLogger(__name__)

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.crawl_intelligence_periodic")
def crawl_intelligence_periodic(self):
    """
    定期爬取情报数据任务
    
    每30分钟执行一次，爬取最新的情报数据
    """
    logger.info("开始执行定期情报数据爬取任务")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        crawler_service = CrawlerService(db)
        match_service = MatchService(db)
        
        # 获取最近24小时内即将开始的比赛
        from_time = datetime.utcnow()
        to_time = from_time + timedelta(hours=24)
        
        upcoming_matches = match_service.get_matches_by_time_range(from_time, to_time)
        
        total_crawled = 0
        errors = []
        
        for match in upcoming_matches:
            try:
                # 爬取比赛相关情报
                intelligence_items = crawler_service.crawl_match_intelligence(
                    match.external_id,
                    match.league.code if match.league else None
                )
                
                for item_data in intelligence_items:
                    try:
                        # 处理情报数据
                        result = intelligence_service.create_or_update_intelligence(item_data)
                        if result["created"] or result["updated"]:
                            total_crawled += 1
                    except Exception as e:
                        errors.append(f"处理情报数据失败: {str(e)}")
                
            except Exception as e:
                errors.append(f"爬取比赛 {match.id} 情报失败: {str(e)}")
        
        logger.info(f"定期情报数据爬取完成: 爬取={total_crawled}")
        
        return {
            "success": True,
            "message": "情报数据爬取完成",
            "crawled": total_crawled,
            "errors": len(errors),
            "error_messages": errors[:10]
        }
        
    except Exception as e:
        logger.error(f"定期情报数据爬取任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "crawled": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.update_intelligence_weights")
def update_intelligence_weights(self):
    """
    更新情报权重任务
    
    每小时执行一次，重新计算所有情报的权重
    """
    logger.info("开始执行情报权重更新任务")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        
        # 获取最近7天内的活跃情报
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        intelligence_items = intelligence_service.get_intelligence_by_date_range(
            cutoff_date, 
            datetime.utcnow()
        )
        
        updated = 0
        errors = []
        
        for item in intelligence_items:
            try:
                # 重新计算权重
                old_weight = item.calculated_weight
                new_weight = item.calculate_weight()
                
                if abs(new_weight - old_weight) > 0.01:  # 只有变化超过1%才更新
                    item.calculated_weight = new_weight
                    item.updated_at = datetime.utcnow()
                    updated += 1
                
                # 每更新100条提交一次
                if updated % 100 == 0:
                    db.commit()
                
            except Exception as e:
                errors.append(f"更新情报 {item.id} 权重失败: {str(e)}")
        
        db.commit()
        
        logger.info(f"情报权重更新完成: 更新={updated}")
        
        return {
            "success": True,
            "message": "情报权重更新完成",
            "updated": updated,
            "errors": len(errors)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"情报权重更新任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "updated": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.analyze_match_after_finished")
def analyze_match_after_finished(self, match_id: int):
    """
    比赛结束后分析任务
    
    比赛结束后自动执行，生成赛后分析和统计
    
    Args:
        match_id: 比赛ID
    """
    logger.info(f"开始执行比赛结束后分析任务，比赛ID: {match_id}")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        match_service = MatchService(db)
        
        # 获取比赛
        match = match_service.get_match_by_id(match_id)
        if not match:
            return {
                "success": False,
                "message": f"比赛不存在: {match_id}"
            }
        
        # 检查比赛是否已结束
        if match.status != "finished":
            return {
                "success": False,
                "message": f"比赛未结束: {match_id}"
            }
        
        # 生成赛后回顾情报
        review_data = {
            "match_id": match_id,
            "type": "review",
            "source": "system_analysis",
            "title": f"{match.home_team.name} vs {match.away_team.name} 赛后回顾",
            "content": intelligence_service.generate_match_review(match),
            "importance": "high",
            "confidence": "high",
            "published_at": datetime.utcnow()
        }
        
        # 创建赛后回顾情报
        review_result = intelligence_service.create_or_update_intelligence(review_data)
        
        # 更新相关情报的状态（标记为过期）
        outdated_count = intelligence_service.mark_intelligence_outdated(match_id)
        
        # 更新比赛统计数据
        match_service.update_match_statistics(match_id)
        
        logger.info(f"比赛结束后分析完成: 比赛={match_id}, 赛后回顾={review_result.get('created', False)}, 过期情报={outdated_count}")
        
        return {
            "success": True,
            "message": "赛后分析完成",
            "match_id": match_id,
            "review_created": review_result.get("created", False),
            "outdated_intelligence": outdated_count
        }
        
    except Exception as e:
        logger.error(f"比赛结束后分析任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "match_id": match_id
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.process_intelligence_batch")
def process_intelligence_batch(self, intelligence_ids: List[int]):
    """
    批量处理情报数据任务
    
    Args:
        intelligence_ids: 情报ID列表
    """
    logger.info(f"开始批量处理情报数据，数量: {len(intelligence_ids)}")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        
        processed = 0
        errors = []
        
        for intel_id in intelligence_ids:
            try:
                # 获取情报
                intelligence = intelligence_service.get_intelligence_by_id(intel_id)
                if not intelligence:
                    errors.append(f"情报不存在: {intel_id}")
                    continue
                
                # 处理情报
                intelligence_service.process_intelligence(intelligence)
                
                # 更新热门度
                intelligence.update_popularity()
                
                processed += 1
                
                # 每处理50条提交一次
                if processed % 50 == 0:
                    db.commit()
                
            except Exception as e:
                errors.append(f"处理情报 {intel_id} 失败: {str(e)}")
        
        db.commit()
        
        if len(errors) > 0:
            logger.warning(f"批量处理情报数据完成: 处理={processed}, 错误={len(errors)}")
        else:
            logger.info(f"批量处理情报数据完成: 处理={processed}, 错误={len(errors)}")
        
        return {
            "success": True,
            "message": "批量处理完成",
            "processed": processed,
            "errors": len(errors),
            "error_messages": errors[:20]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"批量处理情报数据任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "processed": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.deduplicate_intelligence")
def deduplicate_intelligence(self, hours_back: int = 24):
    """
    情报去重任务
    
    检测和合并重复的情报
    
    Args:
        hours_back: 检查多少小时内的情报
    """
    logger.info(f"开始执行情报去重任务，检查最近 {hours_back} 小时内的情报")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        
        # 获取指定时间范围内的情报
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # 查找重复情报
        duplicates = intelligence_service.find_duplicate_intelligence(cutoff_time)
        
        merged = 0
        errors = []
        
        for duplicate_group in duplicates:
            try:
                # 合并重复情报
                result = intelligence_service.merge_duplicate_intelligence(duplicate_group)
                if result["merged"]:
                    merged += result["count"]
            except Exception as e:
                errors.append(f"合并重复情报失败: {str(e)}")
        
        logger.info(f"情报去重完成: 合并={merged} 组重复情报")
        
        return {
            "success": True,
            "message": "情报去重完成",
            "merged_groups": merged,
            "errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"情报去重任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "merged_groups": 0,
            "errors": 1
        }