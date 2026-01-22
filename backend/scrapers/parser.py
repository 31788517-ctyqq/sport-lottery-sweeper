import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup

class SportteryParser:
    """竞彩网数据解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_sporttery_data(self, html_content: str) -> List[Dict[str, Any]]:
        """解析竞彩网比赛数据"""
        matches = []
        
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找包含比赛信息的表格
            table = soup.find('table', class_='match-table') or soup.find('table', {'id': 'match-table'})
            
            if not table:
                # 如果找不到表格，尝试查找其他容器
                table = soup.find('div', class_='match-list') or soup.find('div', class_='game-container')
            
            if not table:
                self.logger.warning("未找到比赛数据表格")
                return matches
            
            # 查找所有比赛行
            match_rows = table.find_all('tr')
            
            for row in match_rows:
                # 跳过表头行
                if row.get('class') and 'header' in row.get('class'):
                    continue
                
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 6:  # 确保有足够的列
                    # 提取赛事编号
                    match_id_cell = cells[0]
                    match_id = match_id_cell.get_text(strip=True)
                    
                    # 提取联赛
                    league_cell = cells[1]
                    league_tag = league_cell.find('span', class_='league-name')
                    league = league_tag.get_text(strip=True) if league_tag else league_cell.get_text(strip=True)
                    
                    # 提取主队vs客队
                    team_cell = cells[2]
                    teams = team_cell.get_text(strip=True).split('VS')
                    home_team = teams[0].strip() if len(teams) > 0 else ""
                    away_team = teams[1].strip() if len(teams) > 1 else ""
                    
                    # 提取比赛开始时间
                    time_cell = cells[3]
                    match_time_str = time_cell.get_text(strip=True)
                    
                    # 提取比赛状态
                    status_cell = cells[4]
                    status = status_cell.get_text(strip=True)
                    
                    # 创建比赛数据字典
                    match = {
                        "id": match_id,
                        "match_id": match_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "league": league,
                        "match_time": match_time_str,
                        "status": status,
                        "source": "sporttery"
                    }
                    
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"解析竞彩网比赛数据失败: {str(e)}")
            return []

class ZQSZSCParser:
    """足球赛事数据解析器（简化版）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_zqszsc_data(self, html_content: str) -> List[Dict[str, Any]]:
        """解析足球赛事数据（返回空列表作为占位）"""
        return []