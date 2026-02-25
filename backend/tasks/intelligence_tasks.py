"""
鎯呮姤鏁版嵁澶勭悊浠诲姟
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
        # Lazy initialization to avoid import-time constructor errors.
        self.intelligence_service = None
        self.crawler_service = None
        self.match_service = None

@celery_app.task(base=IntelligenceTask, bind=True)
def run_intelligence_analysis(self, data):
    """Execute intelligence analysis task."""
    if self.intelligence_service is None:
        db = getattr(self, "db", None)
        if db is None:
            return {"success": False, "message": "database session not available"}
        self.intelligence_service = IntelligenceService(db)
    result = self.intelligence_service.analyze(data)
    return result


logger = logging.getLogger(__name__)

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.crawl_intelligence_periodic")
def crawl_intelligence_periodic(self):
    """
    瀹氭湡鐖彇鎯呮姤鏁版嵁浠诲姟
    
    姣?0鍒嗛挓鎵ц涓€娆★紝鐖彇鏈€鏂扮殑鎯呮姤鏁版嵁
    """
    logger.info("寮€濮嬫墽琛屽畾鏈熸儏鎶ユ暟鎹埇鍙栦换鍔?)
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        crawler_service = CrawlerService(db)
        match_service = MatchService(db)
        
        # 鑾峰彇鏈€杩?4灏忔椂鍐呭嵆灏嗗紑濮嬬殑姣旇禌
        from_time = datetime.utcnow()
        to_time = from_time + timedelta(hours=24)
        
        upcoming_matches = match_service.get_matches_by_time_range(from_time, to_time)
        
        total_crawled = 0
        errors = []
        
        for match in upcoming_matches:
            try:
                # 鐖彇姣旇禌鐩稿叧鎯呮姤
                intelligence_items = crawler_service.crawl_match_intelligence(
                    match.external_id,
                    match.league.code if match.league else None
                )
                
                for item_data in intelligence_items:
                    try:
                        # 澶勭悊鎯呮姤鏁版嵁
                        result = intelligence_service.create_or_update_intelligence(item_data)
                        if result["created"] or result["updated"]:
                            total_crawled += 1
                    except Exception as e:
                        errors.append(f"澶勭悊鎯呮姤鏁版嵁澶辫触: {str(e)}")
                
            except Exception as e:
                errors.append(f"鐖彇姣旇禌 {match.id} 鎯呮姤澶辫触: {str(e)}")
        
        logger.info(f"瀹氭湡鎯呮姤鏁版嵁鐖彇瀹屾垚: 鐖彇={total_crawled}")
        
        return {
            "success": True,
            "message": "鎯呮姤鏁版嵁鐖彇瀹屾垚",
            "crawled": total_crawled,
            "errors": len(errors),
            "error_messages": errors[:10]
        }
        
    except Exception as e:
        logger.error(f"瀹氭湡鎯呮姤鏁版嵁鐖彇浠诲姟澶辫触: {str(e)}")
        return {
            "success": False,
            "message": f"浠诲姟澶辫触: {str(e)}",
            "crawled": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.update_intelligence_weights")
def update_intelligence_weights(self):
    """
    鏇存柊鎯呮姤鏉冮噸浠诲姟
    
    姣忓皬鏃舵墽琛屼竴娆★紝閲嶆柊璁＄畻鎵€鏈夋儏鎶ョ殑鏉冮噸
    """
    logger.info("寮€濮嬫墽琛屾儏鎶ユ潈閲嶆洿鏂颁换鍔?)
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        
        # 鑾峰彇鏈€杩?澶╁唴鐨勬椿璺冩儏鎶?        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        intelligence_items = intelligence_service.get_intelligence_by_date_range(
            cutoff_date, 
            datetime.utcnow()
        )
        
        updated = 0
        errors = []
        
        for item in intelligence_items:
            try:
                # 閲嶆柊璁＄畻鏉冮噸
                old_weight = item.calculated_weight
                new_weight = item.calculate_weight()
                
                if abs(new_weight - old_weight) > 0.01:  # 鍙湁鍙樺寲瓒呰繃1%鎵嶆洿鏂?                    item.calculated_weight = new_weight
                    item.updated_at = datetime.utcnow()
                    updated += 1
                
                # 姣忔洿鏂?00鏉℃彁浜や竴娆?                if updated % 100 == 0:
                    db.commit()
                
            except Exception as e:
                errors.append(f"鏇存柊鎯呮姤 {item.id} 鏉冮噸澶辫触: {str(e)}")
        
        db.commit()
        
        logger.info(f"鎯呮姤鏉冮噸鏇存柊瀹屾垚: 鏇存柊={updated}")
        
        return {
            "success": True,
            "message": "鎯呮姤鏉冮噸鏇存柊瀹屾垚",
            "updated": updated,
            "errors": len(errors)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"鎯呮姤鏉冮噸鏇存柊浠诲姟澶辫触: {str(e)}")
        return {
            "success": False,
            "message": f"浠诲姟澶辫触: {str(e)}",
            "updated": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.analyze_match_after_finished")
def analyze_match_after_finished(self, match_id: int):
    """
    姣旇禌缁撴潫鍚庡垎鏋愪换鍔?    
    姣旇禌缁撴潫鍚庤嚜鍔ㄦ墽琛岋紝鐢熸垚璧涘悗鍒嗘瀽鍜岀粺璁?    
    Args:
        match_id: 姣旇禌ID
    """
    logger.info(f"寮€濮嬫墽琛屾瘮璧涚粨鏉熷悗鍒嗘瀽浠诲姟锛屾瘮璧汭D: {match_id}")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        match_service = MatchService(db)
        
        # 鑾峰彇姣旇禌
        match = match_service.get_match_by_id(match_id)
        if not match:
            return {
                "success": False,
                "message": f"姣旇禌涓嶅瓨鍦? {match_id}"
            }
        
        # 妫€鏌ユ瘮璧涙槸鍚﹀凡缁撴潫
        if match.status != "finished":
            return {
                "success": False,
                "message": f"姣旇禌鏈粨鏉? {match_id}"
            }
        
        # 鐢熸垚璧涘悗鍥為【鎯呮姤
        review_data = {
            "match_id": match_id,
            "type": "review",
            "source": "system_analysis",
            "title": f"{match.home_team.name} vs {match.away_team.name} 璧涘悗鍥為【",
            "content": intelligence_service.generate_match_review(match),
            "importance": "high",
            "confidence": "high",
            "published_at": datetime.utcnow()
        }
        
        # 鍒涘缓璧涘悗鍥為【鎯呮姤
        review_result = intelligence_service.create_or_update_intelligence(review_data)
        
        # 鏇存柊鐩稿叧鎯呮姤鐨勭姸鎬侊紙鏍囪涓鸿繃鏈燂級
        outdated_count = intelligence_service.mark_intelligence_outdated(match_id)
        
        # 鏇存柊姣旇禌缁熻鏁版嵁
        match_service.update_match_statistics(match_id)
        
        logger.info(f"姣旇禌缁撴潫鍚庡垎鏋愬畬鎴? 姣旇禌={match_id}, 璧涘悗鍥為【={review_result.get('created', False)}, 杩囨湡鎯呮姤={outdated_count}")
        
        return {
            "success": True,
            "message": "璧涘悗鍒嗘瀽瀹屾垚",
            "match_id": match_id,
            "review_created": review_result.get("created", False),
            "outdated_intelligence": outdated_count
        }
        
    except Exception as e:
        logger.error(f"姣旇禌缁撴潫鍚庡垎鏋愪换鍔″け璐? {str(e)}")
        return {
            "success": False,
            "message": f"浠诲姟澶辫触: {str(e)}",
            "match_id": match_id
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.process_intelligence_batch")
def process_intelligence_batch(self, intelligence_ids: List[int]):
    """
    鎵归噺澶勭悊鎯呮姤鏁版嵁浠诲姟
    
    Args:
        intelligence_ids: 鎯呮姤ID鍒楄〃
    """
    logger.info(f"寮€濮嬫壒閲忓鐞嗘儏鎶ユ暟鎹紝鏁伴噺: {len(intelligence_ids)}")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        
        processed = 0
        errors = []
        
        for intel_id in intelligence_ids:
            try:
                # 鑾峰彇鎯呮姤
                intelligence = intelligence_service.get_intelligence_by_id(intel_id)
                if not intelligence:
                    errors.append(f"鎯呮姤涓嶅瓨鍦? {intel_id}")
                    continue
                
                # 澶勭悊鎯呮姤
                intelligence_service.process_intelligence(intelligence)
                
                # 鏇存柊鐑棬搴?                intelligence.update_popularity()
                
                processed += 1
                
                # 姣忓鐞?0鏉℃彁浜や竴娆?                if processed % 50 == 0:
                    db.commit()
                
            except Exception as e:
                errors.append(f"澶勭悊鎯呮姤 {intel_id} 澶辫触: {str(e)}")
        
        db.commit()
        
        if len(errors) > 0:
            logger.warning(f"鎵归噺澶勭悊鎯呮姤鏁版嵁瀹屾垚: 澶勭悊={processed}, 閿欒={len(errors)}")
        else:
            logger.info(f"鎵归噺澶勭悊鎯呮姤鏁版嵁瀹屾垚: 澶勭悊={processed}, 閿欒={len(errors)}")
        
        return {
            "success": True,
            "message": "鎵归噺澶勭悊瀹屾垚",
            "processed": processed,
            "errors": len(errors),
            "error_messages": errors[:20]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"鎵归噺澶勭悊鎯呮姤鏁版嵁浠诲姟澶辫触: {str(e)}")
        return {
            "success": False,
            "message": f"浠诲姟澶辫触: {str(e)}",
            "processed": 0,
            "errors": 1
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.intelligence_tasks.deduplicate_intelligence")
def deduplicate_intelligence(self, hours_back: int = 24):
    """
    鎯呮姤鍘婚噸浠诲姟
    
    妫€娴嬪拰鍚堝苟閲嶅鐨勬儏鎶?    
    Args:
        hours_back: 妫€鏌ュ灏戝皬鏃跺唴鐨勬儏鎶?    """
    logger.info(f"寮€濮嬫墽琛屾儏鎶ュ幓閲嶄换鍔★紝妫€鏌ユ渶杩?{hours_back} 灏忔椂鍐呯殑鎯呮姤")
    
    try:
        db = self.db
        intelligence_service = IntelligenceService(db)
        
        # 鑾峰彇鎸囧畾鏃堕棿鑼冨洿鍐呯殑鎯呮姤
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # 鏌ユ壘閲嶅鎯呮姤
        duplicates = intelligence_service.find_duplicate_intelligence(cutoff_time)
        
        merged = 0
        errors = []
        
        for duplicate_group in duplicates:
            try:
                # 鍚堝苟閲嶅鎯呮姤
                result = intelligence_service.merge_duplicate_intelligence(duplicate_group)
                if result["merged"]:
                    merged += result["count"]
            except Exception as e:
                errors.append(f"鍚堝苟閲嶅鎯呮姤澶辫触: {str(e)}")
        
        logger.info(f"鎯呮姤鍘婚噸瀹屾垚: 鍚堝苟={merged} 缁勯噸澶嶆儏鎶?)
        
        return {
            "success": True,
            "message": "鎯呮姤鍘婚噸瀹屾垚",
            "merged_groups": merged,
            "errors": len(errors)
        }
        
    except Exception as e:
        logger.error(f"鎯呮姤鍘婚噸浠诲姟澶辫触: {str(e)}")
        return {
            "success": False,
            "message": f"浠诲姟澶辫触: {str(e)}",
            "merged_groups": 0,
            "errors": 1
        }
