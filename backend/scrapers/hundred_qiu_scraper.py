"""
100qiu爬虫实现
用于抓取 https://m.100qiu.com/api/dcListBasic?dateTime=26011 的数据
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from .core.base_scraper import BaseScraper
from ..models.matches import FootballMatch
from ..models.data_sources import DataSource


class HundredQiuScraper(BaseScraper):
    """100qiu爬虫实现"""
    
    def __init__(self, engine=None):
        super().__init__(engine)
        self.name = "hundred_qiu"  # 设置爬虫名称
        self.base_url = "https://m.100qiu.com/api/dcListBasic"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://m.100qiu.com/"
        }
    
    async def get_matches(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        获取比赛数据
        
        Args:
            days: 获取未来几天的比赛，这里我们使用固定的dateTime参数
            
        Returns:
            比赛数据列表
        """
        # 将days参数转换为对应的dateTime格式
        # 由于API使用特定的dateTime格式，我们暂时使用固定的"26011"
        date_time = "26011"  # 示例值，实际应根据days计算
        
        try:
            params = {"dateTime": date_time}
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get('data', [])  # 直接获取data数组
            
            processed_matches = []
            for match_data in matches:
                processed_match = self._process_match_data(match_data)
                if processed_match:
                    processed_matches.append(processed_match)
                    
            return processed_matches
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求100qiu API失败: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"解析100qiu API响应失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"获取100qiu比赛数据失败: {e}")
            return []
    
    def _process_match_data(self, match_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理单个比赛数据，转换为统一格式
        
        Args:
            match_data: 原始比赛数据
            
        Returns:
            处理后的比赛数据
        """
        try:
            # 根据实际API响应结构调整字段映射
            processed = {
                'match_id': match_data.get('lineId'),  # 使用lineId作为比赛ID
                'league': match_data.get('gameShortName', ''),  # 联赛名称
                'home_team': match_data.get('homeTeam', ''),  # 主队
                'away_team': match_data.get('guestTeam', ''),  # 客队 (注意：API中叫guestTeam)
                'match_time': match_data.get('matchTimeStr', ''),  # 比赛时间
                'status': 'scheduled',  # 默认状态，可以根据需要调整
                'home_power': match_data.get('homePower', 0),  # 主队实力值
                'away_power': match_data.get('guestPower', 0),  # 客队实力值
                'home_win_pan': match_data.get('homeWinPan', 0.0),  # 主胜盘口
                'away_win_pan': match_data.get('guestWinPan', 0.0),  # 客胜盘口
                'home_odds': match_data.get('homeWinAward', 0.0),  # 主胜赔率
                'away_odds': match_data.get('guestWinAward', 0.0),  # 客胜赔率
                'draw_odds': match_data.get('drawAward', 0.0),  # 平局赔率
                'handicap': match_data.get('rq', 0),  # 让球数
                'features': {  # 特征数据
                    'home_feature': match_data.get('homeFeature', ''),
                    'away_feature': match_data.get('guestFeature', '')
                },
                'raw_data': match_data,  # 保存原始数据
            }
            
            return processed
        except Exception as e:
            self.logger.error(f"处理比赛数据失败: {e}, 数据: {match_data}")
            return None
    
    async def get_match_detail(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取比赛详情（如果API支持的话）"""
        # 目前API只提供列表，暂不实现
        return None
    
    async def get_odds_history(self, match_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取赔率历史数据"""
        # 目前API不支持单个比赛的赔率历史，返回空
        return []
    
    def get_source_name(self) -> str:
        """获取数据源名称"""
        return "hundred_qiu"
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试请求最近的数据
            sample_data = await self.get_matches(days=1)
            return {
                'healthy': len(sample_data) > 0,
                'message': f"获取到 {len(sample_data)} 条比赛数据" if sample_data else "未能获取到数据",
                'latency': 0  # 响应时间待实现
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        return {
            'name': self.name,
            'type': 'api',
            'last_run': getattr(self, '_last_run', None),
            'last_result_count': getattr(self, '_last_result_count', 0)
        }
    
    def save_to_database(self, db: Session, date_time: str = "26011"):
        """
        从API获取数据并保存到数据库
        
        Args:
            db: 数据库会话
            date_time: 日期时间参数
        """
        try:
            # 由于get_matches是异步方法，我们需要使用适当的异步方式调用
            import asyncio
            
            async def fetch_matches():
                return await self.get_matches(days=1)  # 调用时使用days参数
            
            # 运行异步函数获取数据
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            matches_data = loop.run_until_complete(fetch_matches())
            loop.close()
            
            self._last_result_count = len(matches_data)
            self._last_run = datetime.now()
            
            for match_info in matches_data:
                # 检查是否已存在该比赛
                existing_match = db.query(FootballMatch).filter(
                    FootballMatch.source_id == match_info['match_id']
                ).first()
                
                if existing_match:
                    # 如果存在，则更新
                    existing_match.league = match_info['league']
                    existing_match.home_team = match_info['home_team']
                    existing_match.away_team = match_info['away_team']
                    existing_match.match_time = match_info['match_time']
                    existing_match.status = match_info['status']
                    existing_match.updated_at = datetime.now()
                    existing_match.raw_data = json.dumps(match_info['raw_data'], ensure_ascii=False)
                else:
                    # 如果不存在，则创建
                    new_match = FootballMatch(
                        match_id=f"hundred_qiu_{match_info['match_id']}",
                        source='hundred_qiu',
                        source_id=match_info['match_id'],
                        league=match_info['league'],
                        home_team=match_info['home_team'],
                        away_team=match_info['away_team'],
                        match_time=match_info['match_time'],
                        status=match_info['status'],
                        round=match_info.get('round', ''),
                        group=match_info.get('group', ''),
                        odds_info=json.dumps(match_info.get('odds_info', {}), ensure_ascii=False),
                        score=json.dumps(match_info.get('score', {}), ensure_ascii=False),
                        raw_data=json.dumps(match_info['raw_data'], ensure_ascii=False),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.add(new_match)
            
            db.commit()
            self.logger.info(f"成功保存 {len(matches_data)} 条比赛数据到数据库")
            return len(matches_data)
        except Exception as e:
            db.rollback()
            self.logger.error(f"保存数据到数据库失败: {e}")
            raise