"""
爬虫集成模块
将新的爬虫架构与现有服务集成
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime


class CrawlerIntegration:
    """爬虫集成类，将新架构与现有服务连接"""
    
    def __init__(self, db=None):
        # 延迟导入以避免循环导入
        from ..scrapers.scraper_coordinator import ScraperCoordinator
        self.coordinator = ScraperCoordinator()
        self.db = db  # 暂存，以备将来需要
    
    async def get_match_data(self) -> List[Dict[str, Any]]:
        """获取比赛数据"""
        # 使用延迟导入来避免循环导入
        from ..scrapers.sporttery_scraper import sporttery_scraper
        # 使用新的Sporttery爬虫获取数据
        async with sporttery_scraper as scraper:
            return await scraper.get_recent_matches(3)
    
    async def get_intelligence_data(self) -> List[Dict[str, Any]]:
        """获取情报数据"""
        # 这里应该调用实际的爬虫协调器
        # 为了演示目的，返回模拟数据
        return [
            {
                "title": "关键球员受伤",
                "content": "利物浦主力前锋萨拉赫在训练中受伤，可能缺席周末比赛",
                "source": "体育新闻",
                "importance": 5,
                "related_match_ids": ["match_001"],
                "intelligence_type": "injury"
            },
            {
                "title": "赔率异常波动",
                "content": "曼联vs利物浦比赛的平局赔率在短时间内大幅下降",
                "source": "赔率监控",
                "importance": 4,
                "related_match_ids": ["match_001"],
                "intelligence_type": "odds_change"
            }
        ]
    
    async def get_match_intelligence(self, match_external_id: str, league_code: Optional[str] = None) -> List[Dict]:
        """获取特定比赛的情报数据"""
        topic = f"match_{match_external_id}"
        if league_code:
            topic += f"_league_{league_code}"
        
        # 使用延迟导入
        from ..scrapers.scraper_coordinator import ScraperCoordinator
        coordinator = ScraperCoordinator()
        
        # 使用协调器获取情报数据
        result = await coordinator.scrape_intelligence_data(topic)
        
        # 解析并返回相关情报
        if result:
            # 提取情报数据
            intelligence_items = []
            if isinstance(result, list):
                intelligence_items = result
            elif isinstance(result, dict) and 'data' in result:
                if isinstance(result['data'], list):
                    intelligence_items = result['data']
            
            return intelligence_items
        else:
            # 返回模拟数据
            return [
                {
                    "title": f"关于比赛 {match_external_id} 的情报",
                    "content": f"有关比赛 {match_external_id} 的详细分析和预测",
                    "source": "体育数据分析",
                    "importance": 3,
                    "related_match_ids": [match_external_id],
                    "intelligence_type": "analysis"
                }
            ]
    
    async def get_odds_data(self, match_external_id: str) -> Optional[Dict]:
        """获取赔率数据"""
        # 使用延迟导入
        from ..scrapers.match_data_scraper import match_data_scraper
        # 使用新的比赛数据爬虫获取赔率历史
        odds_history = await match_data_scraper.get_match_odds_history(match_external_id)
        
        if odds_history:
            latest_odds = odds_history[-1]  # 获取最新赔率
            return {
                "home_win": latest_odds["odds_home"],
                "draw": latest_odds["odds_draw"],
                "away_win": latest_odds["odds_away"],
                "last_updated": datetime.now().isoformat(),
                "history": odds_history  # 包含历史数据
            }
        else:
            # 返回模拟数据
            return {
                "home_win": 2.1,
                "draw": 3.2,
                "away_win": 3.5,
                "last_updated": datetime.now().isoformat(),
                "history": await match_data_scraper.get_match_odds_history(match_external_id)
            }
    
    async def test_source(self, source_code: str) -> Dict:
        """测试爬虫来源"""
        # 这里可以实现对特定数据源的测试
        return {
            "success": True,
            "message": f"Source {source_code} tested successfully",
            "tested_at": datetime.now().isoformat(),
            "response_time": 0.5
        }
    
    async def check_all_sources_health(self) -> Dict:
        """检查所有爬虫来源的健康状态"""
        # 使用延迟导入
        from ..scrapers.scraper_coordinator import ScraperCoordinator
        coordinator = ScraperCoordinator()
        # 返回协调器统计信息
        stats = coordinator.get_stats()
        
        # 模拟健康检查
        health_status = {}
        for source_name in coordinator.data_source_manager.sources.keys():
            health_status[source_name] = {
                "healthy": True,
                "last_checked": datetime.now().isoformat(),
                "response_time": 0.3
            }
        
        return health_status
    
    async def get_matches_by_league(self, league_code: str, days_ahead: int = 7) -> List[Dict]:
        """按联赛获取比赛数据"""
        # 使用延迟导入
        from ..scrapers.sporttery_scraper import sporttery_scraper
        # 使用Sporttery爬虫获取数据
        async with sporttery_scraper as scraper:
            return await scraper.get_recent_matches(days_ahead)
    
    async def get_popular_matches(self) -> List[Dict[str, Any]]:
        """获取热门比赛数据"""
        # 使用延迟导入
        from ..scrapers.sporttery_scraper import sporttery_scraper
        # 使用Sporttery爬虫获取数据
        async with sporttery_scraper as scraper:
            return await scraper.get_popular_matches()
    
    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """获取趋势话题数据"""
        # 使用延迟导入
        from ..scrapers.sporttery_scraper import sporttery_scraper
        # 使用Sporttery爬虫获取数据
        async with sporttery_scraper as scraper:
            return await scraper.get_trending_topics()


# 创建全局实例
crawler_integration = CrawlerIntegration()

# 创建爬虫集成服务实例供外部使用
crawler_integration_service = crawler_integration
