"""
比赛数据处理任务
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import Task
from backend.tasks import DatabaseTask, celery_app
from backend.services.match_service import MatchService
from backend.services.crawler_service import CrawlerService
from backend.core.database import SessionLocal


class MatchTask(Task):
    def __init__(self):
        self.match_service = MatchService()
        self.crawler_service = CrawlerService()


@celery_app.task(base=MatchTask, bind=True)
def sync_matches_task(self):
    """同步比赛数据任务"""
    result = self.match_service.sync_matches()
    return result


@shared_task(base=DatabaseTask, bind=True, name="app.tasks.match_tasks.update_matches_daily")
def update_matches_daily(self):
    """
    每日更新比赛数据任务
    
    每天自动执行，更新未来7天的比赛数据
    """
    logger.info("开始执行每日比赛数据更新任务")
    
    try:
        db = self.db
        match_service = MatchService(db)
        crawler_service = CrawlerService(db)
        
        # 获取需要更新的联赛
        leagues = match_service.get_active_leagues()
        
        total_updated = 0
        total_created = 0
        errors = []
        
        for league in leagues:
            try:
                # 爬取该联赛的未来比赛数据
                matches_data = crawler_service.crawl_matches_by_league(
                    league.code,
                    days_ahead=7
                )
                
                # 处理爬取的数据
                for match_data in matches_data:
                    try:
                        result = match_service.create_or_update_match(match_data)
                        if result["created"]:
                            total_created += 1
                        else:
                            total_updated += 1
                    except Exception as e:
                        errors.append(f"处理比赛数据失败: {str(e)}")
                
            except Exception as e:
                errors.append(f"爬取联赛 {league.name} 失败: {str(e)}")
        
        # 更新比赛状态（将过期的比赛标记为已结束）
        expired_updated = match_service.update_expired_matches()
        
        logger.info(f"每日比赛数据更新完成: 新增={total_created}, 更新={total_updated}, 过期处理={expired_updated}")
        
        return {
            "success": True,
            "message": "比赛数据更新完成",
            "stats": {
                "created": total_created,
                "updated": total_updated,
                "expired_updated": expired_updated,
                "errors": len(errors)
            },
            "errors": errors[:10]  # 只返回前10个错误
        }
        
    except Exception as e:
        logger.error(f"每日比赛数据更新任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "stats": {
                "created": 0,
                "updated": 0,
                "expired_updated": 0,
                "errors": 1
            }
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.match_tasks.update_live_matches")
def update_live_matches(self):
    """
    更新实时比赛数据任务
    
    每5分钟执行一次，更新进行中的比赛数据
    """
    logger.info("开始执行实时比赛数据更新任务")
    
    try:
        db = self.db
        match_service = MatchService(db)
        crawler_service = CrawlerService(db)
        
        # 获取进行中的比赛
        live_matches = match_service.get_live_matches()
        
        updated = 0
        errors = []
        
        for match in live_matches:
            try:
                # 爬取实时比赛数据
                live_data = crawler_service.crawl_live_match_data(match.external_id)
                
                if live_data:
                    # 更新比赛数据
                    match_service.update_match_live_data(match.id, live_data)
                    updated += 1
                    
                    # 如果比赛结束，触发赛后分析
                    if live_data.get("status") == "finished":
                        # 异步执行赛后分析任务
                        from . import intelligence_tasks
                        intelligence_tasks.analyze_match_after_finished.delay(match.id)
                        
            except Exception as e:
                errors.append(f"更新实时比赛 {match.id} 失败: {str(e)}")
        
        logger.info(f"实时比赛数据更新完成: 更新={updated}")
        
        return {
            "success": True,
            "message": "实时比赛数据更新完成",
            "updated": updated,
            "errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"实时比赛数据更新任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "updated": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.match_tasks.process_match_batch")
def process_match_batch(self, match_ids: List[int]):
    """
    批量处理比赛数据任务
    
    Args:
        match_ids: 比赛ID列表
    """
    logger.info(f"开始批量处理比赛数据，数量: {len(match_ids)}")
    
    try:
        db = self.db
        match_service = MatchService(db)
        
        processed = 0
        errors = []
        
        for match_id in match_ids:
            try:
                # 获取比赛详情
                match = match_service.get_match_by_id(match_id)
                if not match:
                    errors.append(f"比赛不存在: {match_id}")
                    continue
                
                # 更新比赛统计信息
                match_service.update_match_statistics(match_id)
                
                # 计算比赛热门度
                match_service.calculate_match_popularity(match_id)
                
                processed += 1
                
                # 每处理10个比赛提交一次
                if processed % 10 == 0:
                    db.commit()
                
            except Exception as e:
                errors.append(f"处理比赛 {match_id} 失败: {str(e)}")
        
        db.commit()
        
        logger.info(f"批量处理比赛数据完成: 处理={processed}, 错误={len(errors)}")
        
        return {
            "success": True,
            "message": "批量处理完成",
            "processed": processed,
            "errors": len(errors),
            "error_messages": errors[:20]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"批量处理比赛数据任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "processed": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.match_tasks.sync_teams_data")
def sync_teams_data(self, league_id: Optional[int] = None):
    """
    同步球队数据任务
    
    同步联赛的球队数据，包括基本信息、球员、统计数据等
    
    Args:
        league_id: 联赛ID，为None时同步所有联赛
    """
    logger.info("开始同步球队数据任务")
    
    try:
        db = self.db
        match_service = MatchService(db)
        crawler_service = CrawlerService(db)
        
        # 获取需要同步的联赛
        if league_id:
            leagues = [match_service.get_league_by_id(league_id)]
        else:
            leagues = match_service.get_active_leagues()
        
        total_synced = 0
        errors = []
        
        for league in leagues:
            if not league:
                continue
                
            try:
                # 爬取联赛球队数据
                teams_data = crawler_service.crawl_teams_by_league(league.code)
                
                for team_data in teams_data:
                    try:
                        # 创建或更新球队
                        result = match_service.create_or_update_team(team_data)
                        if result["created"] or result["updated"]:
                            total_synced += 1
                            
                            # 如果创建了新球队，同步球员数据
                            if result["created"]:
                                team_id = result["team"].id
                                sync_team_players.delay(team_id)
                            
                    except Exception as e:
                        errors.append(f"处理球队数据失败: {str(e)}")
                
            except Exception as e:
                errors.append(f"同步联赛 {league.name} 球队数据失败: {str(e)}")
        
        logger.info(f"球队数据同步完成: 同步={total_synced}")
        
        return {
            "success": True,
            "message": "球队数据同步完成",
            "synced": total_synced,
            "errors": len(errors),
            "error_messages": errors[:10]
        }
        
    except Exception as e:
        logger.error(f"球队数据同步任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "synced": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.match_tasks.sync_team_players")
def sync_team_players(self, team_id: int):
    """
    同步球队球员数据任务
    
    Args:
        team_id: 球队ID
    """
    logger.info(f"开始同步球队球员数据，球队ID: {team_id}")
    
    try:
        db = self.db
        match_service = MatchService(db)
        crawler_service = CrawlerService(db)
        
        # 获取球队
        team = match_service.get_team_by_id(team_id)
        if not team:
            return {
                "success": False,
                "message": f"球队不存在: {team_id}"
            }
        
        # 爬取球员数据
        players_data = crawler_service.crawl_team_players(team.external_id)
        
        synced = 0
        errors = []
        
        for player_data in players_data:
            try:
                # 创建或更新球员
                result = match_service.create_or_update_player(player_data)
                if result["created"] or result["updated"]:
                    synced += 1
            except Exception as e:
                errors.append(f"处理球员数据失败: {str(e)}")
        
        logger.info(f"球队球员数据同步完成: 球队={team.name}, 同步={synced}")
        
        return {
            "success": True,
            "message": "球员数据同步完成",
            "team": team.name,
            "synced": synced,
            "errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"球队球员数据同步任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "synced": 0,
            "errors": 1
        }