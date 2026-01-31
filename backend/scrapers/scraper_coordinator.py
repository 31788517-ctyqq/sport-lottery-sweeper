"""
爬虫协调器模块
负责协调多个爬虫模块的工作
"""
from enum import Enum
import logging
logger = logging.getLogger(__name__)
from typing import List, Dict, Any
from .zqszsc_scraper import zqszsc_scraper


class ScrapingPriorityEnum(Enum):
    """爬取优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class DataSourceTypeEnum(Enum):
    """数据源类型枚举"""
    ZQSZSC = "zqszsc"  # 中文足球数据中心
    JCSMM = "jcsmm"    # 竞彩数据市场
    TIPSPORT = "tipsport"  # Tipsport数据源
    BET365 = "bet365"  # Bet365数据源


class ScraperCoordinator:
    """爬虫协调器"""
    
    def __init__(self):
        self.scrapers = {
            DataSourceTypeEnum.ZQSZSC.value: zqszsc_scraper,
            # 可以在这里添加更多的爬虫实例
        }

    async def get_all_matches(self, days_ahead: int = 3) -> List[Dict[str, Any]]:
        """获取所有爬虫源的比赛数据"""
        all_matches = []
        
        for source, scraper in self.scrapers.items():
            try:
                matches = await scraper.get_matches_within_days(days_ahead)
                for match in matches:
                    match['source'] = source
                all_matches.extend(matches)
            except Exception as e:
                logger.debug(f"获取 {source} 数据时出错: {e}")
                
        return all_matches

    def get_matches_by_source(self, source: str, days_ahead: int = 3) -> List[Dict[str, Any]]:
        """根据数据源获取比赛数据"""
        if source not in self.scrapers:
            raise ValueError(f"未知的数据源: {source}")
        
        try:
            return self.scrapers[source].get_matches_within_days(days_ahead)
        except Exception as e:
            logger.debug(f"获取 {source} 数据时出错: {e}")
            return []


# 创建全局实例
scraper_coordinator = ScraperCoordinator()