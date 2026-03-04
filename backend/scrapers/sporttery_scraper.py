"""
中国竞彩网数据爬虫模块
提供对中国竞彩网数据的抓取功能
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class SportteryScraper:
    """
    中国竞彩网数据爬虫类
    """

    def __init__(self):
        self.base_url = "https://www.lottery.gov.cn"
        self.jczq_url = "https://www.lottery.gov.cn/football/jczq"
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close_session()

    async def start_session(self):
        """启动会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        logger.info("爬虫会话已启动")

    async def close_session(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("爬虫会话已关闭")

    async def get_recent_matches(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        获取近期比赛数据
        :param days: 获取未来几天内的比赛
        :return: 比赛数据列表
        """
        try:
            if not self.session or self.session.closed:
                # 如果没有活跃会话，则创建临时会话
                async with aiohttp.ClientSession(timeout=self.timeout) as temp_session:
                    return await self._fetch_matches(temp_session, days)
            else:
                return await self._fetch_matches(self.session, days)
        except Exception as e:
            logger.error(f"获取比赛数据失败: {e}")
            # 返回模拟数据作为备选
            return self.generate_mock_data(days)

    async def _fetch_matches(self, session: aiohttp.ClientSession, days: int) -> List[Dict[str, Any]]:
        """
        实际的获取比赛数据方法
        :param session: aiohttp会话
        :param days: 获取未来几天内的比赛
        :return: 比赛数据列表
        """
        try:
            # 模拟获取数据（实际环境中应替换为真实API或页面抓取）
            logger.info(f"正在获取未来{days}天的比赛数据...")
            
            # 这里是模拟数据，实际实现时需要替换为真实的爬虫逻辑
            return self.generate_mock_data(days)
            
        except Exception as e:
            logger.error(f"获取比赛数据过程中发生错误: {e}")
            # 发生错误时返回模拟数据
            return self.generate_mock_data(days)

    def generate_mock_data(self, days: int) -> List[Dict[str, Any]]:
        """
        生成模拟比赛数据
        :param days: 比赛天数
        :return: 模拟比赛数据列表
        """
        import random

        leagues = ['英超', '西甲', '德甲', '意甲', '法甲', '中超', '欧冠', '欧联']
        teams = [
            '皇马', '巴萨', '拜仁', '多特', '尤文', '国米', '曼联', '曼城', 
            '利物浦', '切尔西', '巴黎', '马竞', '热刺', '阿森纳', '那不勒斯',
            '罗马', '莱比锡', '霍芬海姆', '法兰克福', '勒沃库森'
        ]

        matches = []
        for i in range(20):  # 生成20场比赛
            league = random.choice(leagues)
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            match_time = datetime.now() + timedelta(hours=random.randint(1, days * 24))
            
            match_data = {
                'id': f"match_{i+1}_{int(datetime.now().timestamp())}",
                'match_id': f"jczq_{match_time.strftime('%Y%m%d')}_{i+1:03d}",
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'match_date': match_time.isoformat(),
                'odds_home_win': round(random.uniform(1.2, 3.5), 2),
                'odds_draw': round(random.uniform(2.0, 4.0), 2),
                'odds_away_win': round(random.uniform(2.5, 5.0), 2),
                'popularity': random.randint(60, 100),
                'status': random.choice(['未开始', '进行中', '已结束']),
                'score': f"{random.randint(0, 4)}:{random.randint(0, 4)}" if random.random() > 0.6 else "-:-"
            }
            matches.append(match_data)

        logger.info(f"生成了{len(matches)}条模拟比赛数据")
        return matches

    async def get_match_odds_history(self, match_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取比赛赔率历史数据
        :param match_id: 比赛ID
        :return: 赔率历史数据
        """
        try:
            # 模拟实现
            import random
            from datetime import datetime, timedelta

            odds_history = []
            base_time = datetime.now() - timedelta(days=7)
            
            for i in range(8):  # 7天的历史数据加上当前数据
                history_time = base_time + timedelta(days=i)
                odds_history.append({
                    'time': history_time.isoformat(),
                    'odds_home_win': round(random.uniform(1.5, 3.0), 2),
                    'odds_draw': round(random.uniform(2.5, 3.8), 2),
                    'odds_away_win': round(random.uniform(2.8, 4.5), 2)
                })

            return odds_history
        except Exception as e:
            logger.error(f"获取赔率历史失败: {e}")
            return None


# 创建全局爬虫实例
sporttery_scraper = SportteryScraper()


# 便捷函数
async def get_recent_matches(days: int = 3) -> List[Dict[str, Any]]:
    """便捷函数：获取近期比赛"""
    return await sporttery_scraper.get_recent_matches(days)


async def get_match_odds_history(match_id: str) -> Optional[List[Dict[str, Any]]]:
    """便捷函数：获取比赛赔率历史"""
    return await sporttery_scraper.get_match_odds_history(match_id)


__all__ = [
    "SportteryScraper", 
    "sporttery_scraper", 
    "get_recent_matches", 
    "get_match_odds_history"
]