"""
爬虫基类
所有具体爬虫都应该继承此基类
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from .engine import ScraperEngine

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    爬虫基类
    
    定义统一的爬虫接口，所有具体爬虫必须实现这些方法
    """
    
    def __init__(self, engine: Optional[ScraperEngine] = None):
        """
        初始化爬虫
        
        Args:
            engine: 爬虫引擎实例，如果不提供则创建新的
        """
        self.engine = engine or ScraperEngine()
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.engine.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.engine.close()
    
    @abstractmethod
    async def get_matches(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        获取比赛数据
        
        Args:
            days: 获取未来几天的比赛
            
        Returns:
            比赛数据列表
        """
        pass
    
    @abstractmethod
    async def get_match_detail(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        获取比赛详情
        
        Args:
            match_id: 比赛ID
            
        Returns:
            比赛详情数据
        """
        pass
    
    @abstractmethod
    async def get_odds_history(self, match_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取赔率历史
        
        Args:
            match_id: 比赛ID
            
        Returns:
            赔率历史数据列表
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        获取数据源名称
        
        Returns:
            数据源名称
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        try:
            start_time = datetime.now()
            
            # 尝试获取一条测试数据
            test_data = await self.get_matches(days=1)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return {
                'source': self.get_source_name(),
                'healthy': True,
                'response_time': round(elapsed, 3),
                'data_available': len(test_data) > 0,
                'checked_at': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                'source': self.get_source_name(),
                'healthy': False,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    def _normalize_match_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化比赛数据格式
        
        Args:
            raw_data: 原始比赛数据
            
        Returns:
            标准化后的比赛数据
        """
        return {
            'source': self.get_source_name(),
            'match_id': raw_data.get('match_id', ''),
            'league': raw_data.get('league', ''),
            'home_team': raw_data.get('home_team', ''),
            'away_team': raw_data.get('away_team', ''),
            'match_time': raw_data.get('match_time', ''),
            'match_date': raw_data.get('match_date', raw_data.get('match_time', '')),
            'odds_home_win': raw_data.get('odds_home_win', 0.0),
            'odds_draw': raw_data.get('odds_draw', 0.0),
            'odds_away_win': raw_data.get('odds_away_win', 0.0),
            'status': raw_data.get('status', 'scheduled'),
            'score': raw_data.get('score', '-:-'),
            'popularity': raw_data.get('popularity', 0),
            'crawled_at': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        return self.engine.get_stats()


class MockScraper(BaseScraper):
    """
    模拟爬虫（用于测试和回退）
    
    当真实数据源不可用时，使用此爬虫生成模拟数据
    """
    
    def get_source_name(self) -> str:
        return "MockSource"
    
    async def get_matches(self, days: int = 3) -> List[Dict[str, Any]]:
        """生成模拟比赛数据"""
        import random
        from datetime import timedelta
        
        leagues = ['英超', '西甲', '德甲', '意甲', '法甲', '中超', '欧冠', '欧联']
        teams = [
            '皇马', '巴萨', '拜仁', '多特', '尤文', '国米', '曼联', '曼城',
            '利物浦', '切尔西', '巴黎', '马竞', '热刺', '阿森纳', '那不勒斯',
            '罗马', '莱比锡', '霍芬海姆', '法兰克福', '勒沃库森'
        ]
        
        matches = []
        for i in range(20):
            league = random.choice(leagues)
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            match_time = datetime.now() + timedelta(hours=random.randint(1, days * 24))
            
            match_data = {
                'match_id': f"mock_{match_time.strftime('%Y%m%d')}_{i+1:03d}",
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'match_date': match_time.isoformat(),
                'match_time': match_time.isoformat(),
                'odds_home_win': round(random.uniform(1.2, 3.5), 2),
                'odds_draw': round(random.uniform(2.0, 4.0), 2),
                'odds_away_win': round(random.uniform(2.5, 5.0), 2),
                'popularity': random.randint(60, 100),
                'status': random.choice(['scheduled', 'live', 'finished']),
                'score': f"{random.randint(0, 4)}:{random.randint(0, 4)}" if random.random() > 0.6 else "-:-"
            }
            matches.append(self._normalize_match_data(match_data))
        
        self.logger.info(f"生成了 {len(matches)} 条模拟数据")
        return matches
    
    async def get_match_detail(self, match_id: str) -> Optional[Dict[str, Any]]:
        """生成模拟比赛详情"""
        import random
        
        return {
            'match_id': match_id,
            'league': '英超',
            'home_team': '曼联',
            'away_team': '利物浦',
            'match_time': datetime.now().isoformat(),
            'odds_home_win': 2.1,
            'odds_draw': 3.2,
            'odds_away_win': 3.5,
            'status': 'scheduled',
            'venue': '老特拉福德球场',
            'referee': '迈克·迪恩',
            'weather': '晴',
            'temperature': '15°C',
            'home_recent_form': 'W-W-D-L-W',
            'away_recent_form': 'W-W-W-D-W',
        }
    
    async def get_odds_history(self, match_id: str) -> Optional[List[Dict[str, Any]]]:
        """生成模拟赔率历史"""
        import random
        from datetime import timedelta
        
        history = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(8):
            history_time = base_time + timedelta(days=i)
            history.append({
                'time': history_time.isoformat(),
                'odds_home_win': round(random.uniform(1.8, 2.5), 2),
                'odds_draw': round(random.uniform(2.8, 3.5), 2),
                'odds_away_win': round(random.uniform(3.0, 4.0), 2)
            })
        
        return history
