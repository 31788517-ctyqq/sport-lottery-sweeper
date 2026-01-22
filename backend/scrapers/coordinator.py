"""
爬虫协调器（重构版）
负责管理多个数据源爬虫，提供统一接口
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum

from .core.base_scraper import BaseScraper, MockScraper
from .core.engine import ScraperEngine

logger = logging.getLogger(__name__)


class DataSourceEnum(Enum):
    """数据源枚举"""
    SPORTTERY = "sporttery"  # 中国竞彩网
    MOCK = "mock"  # 模拟数据源


class ScraperCoordinator:
    """
    爬虫协调器
    
    职责:
    - 管理多个数据源爬虫
    - 提供统一的数据获取接口
    - 实现数据源优先级和回退机制
    - 聚合多个数据源的结果
    """
    
    def __init__(self, engine: Optional[ScraperEngine] = None):
        """
        初始化协调器
        
        Args:
            engine: 共享的爬虫引擎实例
        """
        self.engine = engine or ScraperEngine()
        self.scrapers: Dict[str, BaseScraper] = {}
        self._init_scrapers()
    
    def _init_scrapers(self):
        """初始化所有爬虫"""
        # 延迟导入以避免循环依赖
        from .sources.sporttery import SportteryScraper
        
        # 注册爬虫（使用共享引擎）
        self.scrapers[DataSourceEnum.SPORTTERY.value] = SportteryScraper(self.engine)
        self.scrapers[DataSourceEnum.MOCK.value] = MockScraper(self.engine)
        
        logger.info(f"已初始化 {len(self.scrapers)} 个爬虫: {list(self.scrapers.keys())}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.engine.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.engine.close()
    
    async def get_matches(
        self,
        days: int = 3,
        sources: Optional[List[str]] = None,
        merge: bool = True
    ) -> List[Dict[str, Any]]:
        """
        从多个数据源获取比赛数据
        
        Args:
            days: 未来天数
            sources: 数据源列表，None表示使用所有可用源
            merge: 是否合并多个数据源的结果
            
        Returns:
            比赛数据列表
        """
        if sources is None:
            sources = [DataSourceEnum.SPORTTERY.value]  # 默认使用竞彩网
        
        # 并发获取多个数据源
        tasks = []
        for source_name in sources:
            scraper = self.scrapers.get(source_name)
            if scraper:
                tasks.append(self._safe_get_matches(scraper, days))
            else:
                logger.warning(f"未知数据源: {source_name}")
        
        if not tasks:
            logger.warning("没有可用的数据源，使用模拟数据")
            mock_scraper = self.scrapers[DataSourceEnum.MOCK.value]
            return await mock_scraper.get_matches(days)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"数据源 {sources[i]} 获取失败: {result}")
            elif result:
                valid_results.append(result)
        
        if not valid_results:
            logger.warning("所有数据源均失败，使用模拟数据")
            mock_scraper = self.scrapers[DataSourceEnum.MOCK.value]
            return await mock_scraper.get_matches(days)
        
        # 合并或返回第一个成功的结果
        if merge:
            return self._merge_matches(valid_results)
        else:
            return valid_results[0]
    
    async def _safe_get_matches(
        self,
        scraper: BaseScraper,
        days: int
    ) -> List[Dict[str, Any]]:
        """
        安全获取比赛数据（带异常处理）
        """
        try:
            return await scraper.get_matches(days)
        except Exception as e:
            logger.error(f"爬虫 {scraper.name} 获取数据失败: {e}")
            return []
    
    def _merge_matches(self, results: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个数据源的比赛数据
        
        去重逻辑: 基于 match_id 或 (home_team, away_team, match_time)
        """
        merged = {}
        
        for matches in results:
            for match in matches:
                # 生成唯一键
                key = match.get('match_id')
                if not key:
                    key = f"{match.get('home_team')}_{match.get('away_team')}_{match.get('match_time')}"
                
                # 如果已存在，选择更完整的数据
                if key in merged:
                    existing = merged[key]
                    # 优先选择非模拟数据
                    if match.get('is_mock') and not existing.get('is_mock'):
                        continue
                    elif not match.get('is_mock') and existing.get('is_mock'):
                        merged[key] = match
                    # 否则选择字段更完整的
                    elif len(match) > len(existing):
                        merged[key] = match
                else:
                    merged[key] = match
        
        return list(merged.values())
    
    async def get_match_detail(
        self,
        match_id: str,
        source: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取比赛详情
        
        Args:
            match_id: 比赛ID
            source: 指定数据源，None表示自动选择
            
        Returns:
            比赛详情数据
        """
        if source:
            scraper = self.scrapers.get(source)
            if scraper:
                return await scraper.get_match_detail(match_id)
            else:
                logger.warning(f"未知数据源: {source}")
                return None
        
        # 按优先级尝试所有数据源
        for source_name in [DataSourceEnum.SPORTTERY.value, DataSourceEnum.MOCK.value]:
            scraper = self.scrapers.get(source_name)
            if scraper:
                try:
                    detail = await scraper.get_match_detail(match_id)
                    if detail:
                        return detail
                except Exception as e:
                    logger.warning(f"数据源 {source_name} 获取详情失败: {e}")
                    continue
        
        return None
    
    async def get_odds_history(
        self,
        match_id: str,
        source: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取赔率历史
        
        Args:
            match_id: 比赛ID
            source: 指定数据源，None表示自动选择
            
        Returns:
            赔率历史数据列表
        """
        if source:
            scraper = self.scrapers.get(source)
            if scraper:
                return await scraper.get_odds_history(match_id)
            else:
                logger.warning(f"未知数据源: {source}")
                return None
        
        # 按优先级尝试所有数据源
        for source_name in [DataSourceEnum.SPORTTERY.value, DataSourceEnum.MOCK.value]:
            scraper = self.scrapers.get(source_name)
            if scraper:
                try:
                    history = await scraper.get_odds_history(match_id)
                    if history:
                        return history
                except Exception as e:
                    logger.warning(f"数据源 {source_name} 获取赔率历史失败: {e}")
                    continue
        
        return None
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        检查所有数据源的健康状态
        
        Returns:
            每个数据源的健康状态
        """
        tasks = []
        source_names = []
        
        for source_name, scraper in self.scrapers.items():
            tasks.append(scraper.health_check())
            source_names.append(source_name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_status = {}
        for source_name, result in zip(source_names, results):
            if isinstance(result, Exception):
                health_status[source_name] = {
                    'healthy': False,
                    'error': str(result)
                }
            else:
                health_status[source_name] = result
        
        return health_status
    
    def get_stats(self) -> Dict[str, Any]:
        """获取所有爬虫的统计信息"""
        return {
            'engine_stats': self.engine.get_stats(),
            'scrapers': {
                name: scraper.get_stats()
                for name, scraper in self.scrapers.items()
            }
        }


# 创建全局协调器实例
_global_coordinator: Optional[ScraperCoordinator] = None


async def get_coordinator() -> ScraperCoordinator:
    """获取全局协调器实例"""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = ScraperCoordinator()
        await _global_coordinator.engine.start()
    return _global_coordinator


async def close_coordinator():
    """关闭全局协调器"""
    global _global_coordinator
    if _global_coordinator:
        await _global_coordinator.engine.close()
        _global_coordinator = None
