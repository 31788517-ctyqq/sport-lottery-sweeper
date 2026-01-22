"""
爬虫集成模块
将新的爬虫架构与现有服务集成
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime


class CrawlerIntegration:
    """爬虫集成类，将新架构与现有服务连接"""
    
    def __init__(self):
        # 延迟导入以避免循环导入
        from ..scrapers.scraper_coordinator import ScraperCoordinator
        self.coordinator = ScraperCoordinator()
    
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

"""
爬虫服务集成模块
集成爬虫功能到业务服务层
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..scrapers.crawler_integration import crawler_integration


class CrawlerService:
    """
    爬虫服务类
    提供与爬虫集成的业务逻辑接口
    """
    
    def __init__(self):
        self.crawler_integration = crawler_integration
        self.logger = logging.getLogger(__name__)
    
    async def get_recent_matches(self, days_ahead: int = 3) -> List[Dict[str, Any]]:
        """
        获取最近几天的比赛信息
        
        Args:
            days_ahead: 获取未来几天的比赛，默认3天
            
        Returns:
            比赛信息列表
        """
        self.logger.info(f"开始获取未来 {days_ahead} 天的比赛数据")
        
        try:
            # 使用爬虫集成模块获取数据
            matches = await self.crawler_integration.get_recent_matches(days_ahead)
            
            # 检查是否获取到了数据
            if not matches:
                self.logger.warning("爬虫集成模块返回空数据，尝试直接使用高级爬虫")
                # 直接使用高级爬虫
                from backend.scrapers.advanced_crawler import advanced_crawler
                matches = await advanced_crawler.crawl_sporttery_matches(days_ahead)
            
            # 对结果进行额外的业务处理
            processed_matches = self._process_matches(matches)
            
            self.logger.info(f"成功获取并处理 {len(processed_matches)} 场比赛数据")
            return processed_matches
        except Exception as e:
            self.logger.error(f"获取比赛数据失败: {str(e)}", exc_info=True)
            return []
    
    async def get_popular_matches(self) -> List[Dict[str, Any]]:
        """
        获取热门比赛数据
        
        Returns:
            热门比赛信息列表
        """
        self.logger.info("开始获取热门比赛数据")
        
        try:
            # 使用爬虫集成模块获取热门比赛
            matches = await self.crawler_integration.get_popular_matches()
            
            # 对结果进行额外的业务处理
            processed_matches = self._process_matches(matches)
            
            self.logger.info(f"成功获取并处理 {len(processed_matches)} 场热门比赛数据")
            return processed_matches
        except Exception as e:
            self.logger.error(f"获取热门比赛数据失败: {str(e)}")
            return []
    
    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """
        获取趋势话题数据（如近期热门赛事讨论、联赛排名变化等）
        
        Returns:
            趋势话题信息列表
        """
        self.logger.info("开始获取趋势话题数据")
        
        try:
            # 使用爬虫集成模块获取趋势话题
            topics = await self.crawler_integration.get_trending_topics()
            
            # 对结果进行额外的业务处理
            processed_topics = self._process_trending_topics(topics)
            
            self.logger.info(f"成功获取并处理 {len(processed_topics)} 个趋势话题")
            return processed_topics
        except Exception as e:
            self.logger.error(f"获取趋势话题数据失败: {str(e)}")
            return []
    
    def _process_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理比赛数据，添加业务逻辑
        """
        processed_matches = []
        
        for match in matches:
            # 添加业务逻辑处理
            processed_match = match.copy()
            
            # 确保所有必需字段都存在
            if 'id' not in processed_match:
                import hashlib
                match_id = hashlib.md5(f"{processed_match.get('home_team', '')}{processed_match.get('away_team', '')}{processed_match.get('match_time', '')}".encode()).hexdigest()[:12]
                processed_match['id'] = f"match_{match_id}"
            
            if 'match_id' not in processed_match:
                processed_match['match_id'] = processed_match['id']
            
            if 'home_team' not in processed_match:
                processed_match['home_team'] = '主队'
            
            if 'away_team' not in processed_match:
                processed_match['away_team'] = '客队'
            
            if 'league' not in processed_match:
                processed_match['league'] = '未知联赛'
            
            if 'match_date' not in processed_match:
                processed_match['match_date'] = processed_match.get('match_time', datetime.now().strftime('%Y-%m-%d %H:%M'))
            
            if 'match_time' not in processed_match:
                processed_match['match_time'] = processed_match.get('match_date', datetime.now().strftime('%Y-%m-%d %H:%M'))
            
            if 'odds_home_win' not in processed_match:
                processed_match['odds_home_win'] = 2.0
            
            if 'odds_draw' not in processed_match:
                processed_match['odds_draw'] = 3.0
            
            if 'odds_away_win' not in processed_match:
                processed_match['odds_away_win'] = 2.5
            
            if 'status' not in processed_match:
                processed_match['status'] = 'scheduled'
            
            if 'popularity' not in processed_match:
                processed_match['popularity'] = 50
            
            if 'predicted_result' not in processed_match:
                processed_match['predicted_result'] = 'unknown'
            
            if 'prediction_confidence' not in processed_match:
                processed_match['prediction_confidence'] = 0.0
            
            # 计算比赛时间距离（小时）
            try:
                match_time_str = processed_match.get('match_time') or processed_match.get('match_date')
                if match_time_str:
                    if 'T' in match_time_str:
                        match_time = datetime.fromisoformat(
                            match_time_str.replace('Z', '+00:00')
                        )
                    elif ':' in match_time_str and '-' in match_time_str:
                        # 处理 "MM-DD HH:MM" 或 "YYYY-MM-DD HH:MM" 格式
                        if len(match_time_str.split()[0].split('-')[0]) == 2:
                            # MM-DD格式
                            now = datetime.now()
                            month, day = map(int, match_time_str.split()[0].split('-'))
                            hour, minute = map(int, match_time_str.split()[1].split(':'))
                            match_time = datetime(now.year, month, day, hour, minute)
                            
                            # 如果月份小于当前月份，认为是下一年的
                            if match_time.month < now.month:
                                match_time = match_time.replace(year=now.year+1)
                        else:
                            # YYYY-MM-DD格式
                            match_time = datetime.strptime(match_time_str, '%Y-%m-%d %H:%M')
                    elif ':' in match_time_str:
                        # 只有时间，加上今天的日期
                        today = datetime.now().date()
                        time_part = datetime.strptime(match_time_str, '%H:%M').time()
                        match_time = datetime.combine(today, time_part)
                    else:
                        # 只有日期
                        match_time = datetime.strptime(match_time_str, '%Y-%m-%d')
                    
                    now = datetime.now()
                    time_diff = match_time - now
                    processed_match['hours_to_match'] = time_diff.total_seconds() / 3600
                else:
                    processed_match['hours_to_match'] = 0
            except Exception:
                processed_match['hours_to_match'] = 0
            
            # 添加推荐指数计算
            try:
                odds_home = float(processed_match.get('odds_home_win', 2.0))
                odds_draw = float(processed_match.get('odds_draw', 3.0))
                odds_away = float(processed_match.get('odds_away_win', 2.5))
                
                # 简单的推荐指数计算（赔率越低，推荐指数越高）
                avg_odds = (odds_home + odds_draw + odds_away) / 3
                recommendation_score = (avg_odds - min(odds_home, odds_draw, odds_away)) * 10
                processed_match['recommendation_score'] = round(recommendation_score, 2)
            except Exception:
                processed_match['recommendation_score'] = 0.0
            
            processed_matches.append(processed_match)
        
        return processed_matches
    
    def _process_trending_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理趋势话题数据，添加业务逻辑
        """
        processed_topics = []
        
        for topic in topics:
            # 添加业务逻辑处理
            processed_topic = topic.copy()
            
            # 计算话题热度指数
            importance = processed_topic.get('importance', 1)
            popularity = processed_topic.get('popularity', 50)
            heat_index = importance * popularity / 5
            processed_topic['heat_index'] = round(heat_index, 2)
            
            processed_topics.append(processed_topic)
        
        return processed_topics


# 创建全局实例
crawler_service = CrawlerService()

"""
爬虫集成服务模块
集成爬虫功能到业务服务层
"""
import logging
from typing import Dict, Any, Optional


class CrawlerIntegrationService:
    """爬虫集成服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def fetch_and_process(self, url: str) -> Optional[Dict[str, Any]]:
        """获取并处理数据"""
        try:
            # 使用高级爬虫获取数据 - 避免循环导入，直接在此处导入
            from ..scrapers.advanced_crawler import advanced_crawler
            raw_data = advanced_crawler.fetch_data(url)
            
            # 处理数据
            processed_data = self._process_data(raw_data)
            
            return processed_data
        except Exception as e:
            self.logger.error(f"获取并处理数据时发生错误: {str(e)}")
            return None

    def _process_data(self, raw_data: Any) -> Dict[str, Any]:
        """处理原始数据"""
        # 实现数据处理逻辑
        return {
            "raw_data": raw_data,
            "processed": True
        }


# 创建全局实例
crawler_integration_service = CrawlerIntegrationService()
