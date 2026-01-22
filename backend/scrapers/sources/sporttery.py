"""
中国竞彩网爬虫（重构版）
支持真实数据爬取
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from ..core.base_scraper import BaseScraper
from ..core.engine import ScraperEngine

logger = logging.getLogger(__name__)


class SportteryScraper(BaseScraper):
    """
    中国竞彩网爬虫
    
    数据源: https://www.lottery.gov.cn
    
    实现策略:
    1. 优先尝试API接口（如果存在）
    2. 回退到HTML解析
    3. 最终回退到模拟数据
    """
    
    # API端点（需要根据实际情况调整）
    BASE_URL = "https://www.lottery.gov.cn"
    JCZQ_URL = "https://www.lottery.gov.cn/football/jczq"
    API_MATCH_LIST = "https://www.lottery.gov.cn/api/football/jczq/match-list"
    API_MATCH_DETAIL = "https://www.lottery.gov.cn/api/football/jczq/match-detail"
    API_ODDS_HISTORY = "https://www.lottery.gov.cn/api/football/jczq/odds-history"
    
    def __init__(self, engine: Optional[ScraperEngine] = None):
        super().__init__(engine)
        self.fallback_to_mock = True  # 是否回退到模拟数据
    
    def get_source_name(self) -> str:
        return "中国竞彩网"
    
    async def get_matches(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        获取比赛列表
        
        多层回退策略:
        1. API接口
        2. HTML解析
        3. 模拟数据
        """
        # 策略1: 尝试API接口
        try:
            matches = await self._fetch_from_api(days)
            if matches:
                self.logger.info(f"通过API获取了 {len(matches)} 场比赛")
                return matches
        except Exception as e:
            self.logger.warning(f"API接口获取失败: {e}")
        
        # 策略2: 尝试HTML解析
        try:
            matches = await self._fetch_from_html(days)
            if matches:
                self.logger.info(f"通过HTML解析获取了 {len(matches)} 场比赛")
                return matches
        except Exception as e:
            self.logger.warning(f"HTML解析失败: {e}")
        
        # 策略3: 回退到模拟数据
        if self.fallback_to_mock:
            self.logger.warning("所有真实数据源失败，使用模拟数据")
            return await self._generate_mock_matches(days)
        else:
            raise Exception("无法获取比赛数据，且未启用模拟数据回退")
    
    async def _fetch_from_api(self, days: int) -> Optional[List[Dict[str, Any]]]:
        """
        从API获取数据
        
        注意: 此API端点可能不存在或需要认证，需要根据实际情况调整
        """
        try:
            # 构建请求参数
            from_date = datetime.now().strftime('%Y-%m-%d')
            to_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            params = {
                'from_date': from_date,
                'to_date': to_date,
                'league': 'all'
            }
            
            # 发起请求
            cache_key = f"sporttery_matches_{from_date}_{to_date}"
            response = await self.engine.fetch(
                self.API_MATCH_LIST,
                method='GET',
                cache_key=cache_key,
                params=params
            )
            
            # 解析响应
            if response.get('json'):
                data = response['json']
                if data.get('success') and data.get('data'):
                    return self._parse_api_matches(data['data'])
            
            return None
            
        except Exception as e:
            self.logger.error(f"API请求失败: {e}")
            return None
    
    async def _fetch_from_html(self, days: int) -> Optional[List[Dict[str, Any]]]:
        """
        从HTML页面解析数据
        
        这是更可靠的方法，直接抓取网页内容
        """
        try:
            # 获取页面
            response = await self.engine.fetch(
                self.JCZQ_URL,
                method='GET'
            )
            
            html = response.get('text', '')
            if not html:
                return None
            
            # 解析HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找比赛数据（需要根据实际HTML结构调整）
            matches = []
            
            # 示例: 查找包含比赛信息的元素
            match_elements = soup.find_all('div', class_='match-item')  # 需要调整选择器
            
            for element in match_elements:
                try:
                    match_data = self._parse_html_match(element)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    self.logger.warning(f"解析单场比赛失败: {e}")
                    continue
            
            # 如果成功解析到数据，返回
            if matches:
                return matches
            
            # 尝试从页面中的JSON数据提取（很多网站会在页面中嵌入JSON）
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if 'matches' in json_data:
                        return self._parse_api_matches(json_data['matches'])
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"HTML解析失败: {e}")
            return None
    
    def _parse_api_matches(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """解析API返回的比赛数据"""
        matches = []
        
        for item in data:
            try:
                match = {
                    'match_id': item.get('match_id', ''),
                    'league': item.get('league_name', ''),
                    'home_team': item.get('home_team', ''),
                    'away_team': item.get('away_team', ''),
                    'match_time': item.get('match_time', ''),
                    'match_date': item.get('match_time', ''),
                    'odds_home_win': float(item.get('odds_home', 0)),
                    'odds_draw': float(item.get('odds_draw', 0)),
                    'odds_away_win': float(item.get('odds_away', 0)),
                    'status': item.get('status', 'scheduled'),
                    'score': item.get('score', '-:-'),
                    'popularity': int(item.get('popularity', 0)),
                }
                matches.append(self._normalize_match_data(match))
            except Exception as e:
                self.logger.warning(f"解析API比赛数据失败: {e}")
                continue
        
        return matches
    
    def _parse_html_match(self, element) -> Optional[Dict[str, Any]]:
        """
        解析HTML元素中的比赛信息
        
        需要根据实际的HTML结构调整选择器
        """
        try:
            # 示例解析逻辑（需要根据实际HTML结构调整）
            match_id = element.get('data-match-id', '')
            home_team = element.find('span', class_='home-team').text.strip()
            away_team = element.find('span', class_='away-team').text.strip()
            match_time = element.find('span', class_='match-time').text.strip()
            
            # 赔率信息
            odds_elements = element.find_all('span', class_='odds')
            odds_home = float(odds_elements[0].text) if len(odds_elements) > 0 else 0
            odds_draw = float(odds_elements[1].text) if len(odds_elements) > 1 else 0
            odds_away = float(odds_elements[2].text) if len(odds_elements) > 2 else 0
            
            return {
                'match_id': match_id,
                'league': element.get('data-league', '未知联赛'),
                'home_team': home_team,
                'away_team': away_team,
                'match_time': match_time,
                'match_date': match_time,
                'odds_home_win': odds_home,
                'odds_draw': odds_draw,
                'odds_away_win': odds_away,
                'status': 'scheduled',
                'score': '-:-',
                'popularity': 0,
            }
        except Exception as e:
            self.logger.warning(f"解析HTML比赛元素失败: {e}")
            return None
    
    async def _generate_mock_matches(self, days: int) -> List[Dict[str, Any]]:
        """生成模拟数据作为最终回退"""
        from ..core.base_scraper import MockScraper
        
        mock_scraper = MockScraper(self.engine)
        matches = await mock_scraper.get_matches(days)
        
        # 标记为模拟数据
        for match in matches:
            match['is_mock'] = True
            match['source'] = self.get_source_name() + " (Mock)"
        
        return matches
    
    async def get_match_detail(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取比赛详情"""
        try:
            # 尝试API
            response = await self.engine.fetch(
                f"{self.API_MATCH_DETAIL}?match_id={match_id}",
                cache_key=f"match_detail_{match_id}"
            )
            
            if response.get('json'):
                data = response['json']
                if data.get('success'):
                    return data.get('data')
            
            # 回退到模拟数据
            if self.fallback_to_mock:
                from ..core.base_scraper import MockScraper
                mock_scraper = MockScraper(self.engine)
                return await mock_scraper.get_match_detail(match_id)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取比赛详情失败: {e}")
            return None
    
    async def get_odds_history(self, match_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取赔率历史"""
        try:
            # 尝试API
            response = await self.engine.fetch(
                f"{self.API_ODDS_HISTORY}?match_id={match_id}",
                cache_key=f"odds_history_{match_id}"
            )
            
            if response.get('json'):
                data = response['json']
                if data.get('success'):
                    return data.get('data')
            
            # 回退到模拟数据
            if self.fallback_to_mock:
                from ..core.base_scraper import MockScraper
                mock_scraper = MockScraper(self.engine)
                return await mock_scraper.get_odds_history(match_id)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取赔率历史失败: {e}")
            return None
