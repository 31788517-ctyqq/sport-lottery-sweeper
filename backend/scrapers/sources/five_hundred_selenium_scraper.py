"""
500彩票网竞彩足球爬虫 (Selenium版)
用于爬取竞彩足球比赛赛程，使用Selenium处理JavaScript渲染内容
"""
import logging
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import random

logger = logging.getLogger(__name__)


class FiveHundredSeleniumScraper:
    """
    500彩票网竞彩足球爬虫 (Selenium版)
    
    数据源: https://trade.500.com/jczq/
    
    实现策略:
    1. 使用Selenium访问500彩票网竞彩足球页面
    2. 等待JavaScript内容加载完成
    3. 解析页面中的比赛数据
    4. 提取比赛时间、对阵双方、赔率等信息
    """
    
    BASE_URL = "https://trade.500.com/jczq/"
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """设置Chrome浏览器选项"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置随机User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # 执行脚本隐藏webdriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.error(f"初始化Chrome驱动失败: {e}")
            raise
    
    def get_source_name(self) -> str:
        return "500彩票网竞彩足球(Selenium版)"
    
    def get_matches(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        获取比赛列表
        
        Args:
            days: 获取未来几天的比赛，默认3天
            
        Returns:
            List[Dict]: 比赛数据列表
        """
        try:
            logger.info(f"正在访问 {self.BASE_URL}")
            
            # 访问页面
            self.driver.get(self.BASE_URL)
            
            # 等待页面加载
            try:
                # 等待主要内容加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jczq_table"))
                )
            except TimeoutException:
                logger.warning("等待jczq_table元素超时，尝试其他选择器")
                try:
                    # 尝试等待其他比赛相关的元素
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='jingcai_']"))
                    )
                except TimeoutException:
                    logger.warning("等待比赛相关元素超时，继续处理页面")
            
            # 等待额外时间让JavaScript完全加载
            time.sleep(3)
            
            # 获取页面源码
            page_source = self.driver.page_source
            
            # 解析页面内容
            soup = BeautifulSoup(page_source, 'html.parser')
            matches = self._parse_match_data(soup, days)
            
            # 如果通过HTML解析没有获取到数据，尝试从页面的JavaScript中提取数据
            if not matches:
                matches = self._parse_js_data(soup, days)
            
            logger.info(f"Successfully scraped {len(matches)} matches from 500彩票网")
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping 500彩票网: {str(e)}")
            return []
    
    
    def _parse_match_data(self, soup: BeautifulSoup, days: int) -> List[Dict[str, Any]]:
        """
        解析比赛数据
        
        Args:
            soup: BeautifulSoup对象
            days: 获取未来几天的比赛
            
        Returns:
            List[Dict]: 解析后的比赛数据列表
        """
        matches = []
        
        # 尝试多种选择器来捕获比赛信息
        # 首先尝试查找比赛容器
        match_containers = soup.select('.jczq_table tbody tr')
        
        if not match_containers:
            # 尝试其他可能的选择器
            match_containers = soup.select('tr[style*="height"]') or \
                              soup.select('tr[id*="match"]') or \
                              soup.select('tr[class*="tr_"]') or \
                              soup.select('tr.t_tr') or \
                              soup.select('.jieguo_list tr')
        
        if match_containers:
            logger.info(f"Found {len(match_containers)} potential match rows")
            
            for container in match_containers:
                try:
                    # 提取比赛信息
                    match_info = self._extract_match_from_row(container)
                    if match_info:
                        # 检查比赛日期是否在指定范围内
                        match_date_str = match_info.get('match_date', '')
                        if self._is_date_in_range(match_date_str, days):
                            matches.append(match_info)
                except Exception as e:
                    logger.warning(f"Error parsing match row: {str(e)}")
                    continue
        
        return matches
    
    def _is_date_in_range(self, date_str: str, days: int) -> bool:
        """
        检查日期是否在指定范围内
        
        Args:
            date_str: 日期字符串
            days: 天数范围
            
        Returns:
            bool: 日期是否在范围内
        """
        try:
            if not date_str:
                return True
                
            # 尝试解析日期时间
            if ' ' in date_str:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            
            today = datetime.now()
            end_date = today + timedelta(days=days)
            
            return today.date() <= dt.date() <= end_date.date()
        except ValueError:
            # 如果日期格式不正确，返回True以确保数据不丢失
            return True
    
    def _extract_match_from_row(self, row) -> Optional[Dict[str, Any]]:
        """
        从表格行中提取比赛信息
        
        Args:
            row: BeautifulSoup标签对象，表示一行比赛数据
            
        Returns:
            Dict: 比赛信息字典
        """
        try:
            # 查找比赛编号
            match_num_elem = row.find('td', class_='td_league') or row.find('td', attrs={'align': 'center'})
            if match_num_elem:
                match_num = match_num_elem.get_text(strip=True)
            else:
                # 尝试其他可能的选择器
                first_td = row.find('td')
                if first_td:
                    match_num = first_td.get_text(strip=True)[:10]  # 取前10个字符作为比赛编号
                else:
                    match_num = f"未知_{hash(str(row)) % 10000}"
            
            # 查找联赛名称
            league_elem = row.find('span', class_='name_z')
            if not league_elem:
                # 尝试其他可能的联赛名称选择器
                league_elem = row.find('span', class_=lambda x: x and 'name' in x)
            league = league_elem.get_text(strip=True) if league_elem else "未知联赛"
            
            # 查找主队和客队
            team_elements = row.find_all('span', class_='name_vs')
            if len(team_elements) >= 2:
                home_team = team_elements[0].get_text(strip=True)
                away_team = team_elements[1].get_text(strip=True)
            else:
                # 尝试其他可能的队伍名称选择器
                team_spans = row.find_all('span', string=True)
                teams = [span.get_text(strip=True) for span in team_spans if len(span.get_text(strip=True)) > 1]
                if len(teams) >= 2:
                    home_team = teams[0]
                    away_team = teams[1]
                else:
                    home_team = "主队"
                    away_team = "客队"
            
            # 查找比赛时间
            time_elem = row.find('span', class_='timer')
            if not time_elem:
                # 尝试其他可能的时间选择器
                time_elem = row.find('td', class_=lambda x: x and 'time' in x)
            match_time_str = time_elem.get_text(strip=True) if time_elem else ""
            
            # 构造完整的日期时间字符串
            if match_time_str:
                # 获取当前日期
                today = datetime.now()
                match_date = f"{today.strftime('%Y-%m-%d')} {match_time_str}:00"
            else:
                match_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 查找赔率信息（如果有的话）
            # 尝试查找包含赔率的td元素
            odd_elements = row.find_all('td', class_=lambda x: x and ('sp' in x or 'odds' in x))
            if odd_elements:
                # 通常包含三个赔率值：主胜、平、客胜
                odd_spans = odd_elements[0].find_all('span')
                if len(odd_spans) >= 3:
                    try:
                        odds_home_win = float(odd_spans[0].get_text(strip=True))
                        odds_draw = float(odd_spans[1].get_text(strip=True))
                        odds_away_win = float(odd_spans[2].get_text(strip=True))
                    except (ValueError, IndexError):
                        odds_home_win = 2.0
                        odds_draw = 3.0
                        odds_away_win = 3.5
                else:
                    odds_home_win = 2.0
                    odds_draw = 3.0
                    odds_away_win = 3.5
            else:
                # 尝试从其他地方获取赔率
                all_numbers = row.find_all(string=re.compile(r'^\d+\.\d+$'))
                if len(all_numbers) >= 3:
                    try:
                        odds_home_win = float(all_numbers[0])
                        odds_draw = float(all_numbers[1])
                        odds_away_win = float(all_numbers[2])
                    except (ValueError, IndexError):
                        odds_home_win = 2.0
                        odds_draw = 3.0
                        odds_away_win = 3.5
                else:
                    odds_home_win = 2.0
                    odds_draw = 3.0
                    odds_away_win = 3.5
            
            # 构建比赛数据
            match_data = {
                "match_id": match_num,
                "league": league,
                "home_team": home_team,
                "away_team": away_team,
                "match_date": match_date,
                "match_time": match_time_str,
                "odds_home_win": odds_home_win,
                "odds_draw": odds_draw,
                "odds_away_win": odds_away_win,
                "status": "scheduled",
                "score": "-:-",
                "popularity": 50,
                "source": "500彩票网(Selenium)"
            }
            
            return match_data
        except Exception as e:
            logger.warning(f"Error extracting match from row: {str(e)}")
            return None
    
    def _parse_js_data(self, soup: BeautifulSoup, days: int) -> List[Dict[str, Any]]:
        """
        从页面的JavaScript中解析比赛数据
        """
        matches = []
        
        # 查找可能包含比赛数据的script标签
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 查找包含比赛数据的JavaScript变量
                # 常见的变量名包括 matchList, data, matches 等
                patterns = [
                    r'(?:var\s+|let\s+|const\s+)?(\w*)\s*=\s*(\[.*?\]);',
                    r'(?:var\s+|let\s+|const\s+)?(\w*)\s*=\s*(\{.*?\});',
                    r'(\[.*?\])',  # 通用模式
                ]
                
                for pattern in patterns:
                    matches_found = re.findall(pattern, script.string, re.DOTALL)
                    if matches_found:
                        for match_result in matches_found:
                            # 如果是元组（变量名，值），取第二个元素
                            if isinstance(match_result, tuple):
                                js_data = match_result[1] if len(match_result) > 1 else match_result[0]
                            else:
                                js_data = match_result
                            
                            # 尝试解析为JSON
                            try:
                                # 清理可能存在的注释和非法字符
                                cleaned_data = self._clean_js_object(js_data)
                                if cleaned_data:
                                    parsed_data = json.loads(cleaned_data)
                                    
                                    if isinstance(parsed_data, list):
                                        for item in parsed_data:
                                            if isinstance(item, dict):
                                                match_data = self._convert_match_item(item)
                                                if match_data:
                                                    # 检查比赛日期是否在指定范围内
                                                    match_date_str = match_data.get('match_date', '')
                                                    if self._is_date_in_range(match_date_str, days):
                                                        matches.append(match_data)
                                    elif isinstance(parsed_data, dict):
                                        # 如果是单个对象，检查是否是包含比赛列表的对象
                                        for key, value in parsed_data.items():
                                            if isinstance(value, list):
                                                for item in value:
                                                    if isinstance(item, dict):
                                                        match_data = self._convert_match_item(item)
                                                        if match_data:
                                                            match_date_str = match_data.get('match_date', '')
                                                            if self._is_date_in_range(match_date_str, days):
                                                                matches.append(match_data)
                            except json.JSONDecodeError:
                                # 如果解析失败，尝试其他模式
                                continue
                            except Exception as e:
                                logger.debug(f"Error processing JS data: {str(e)}")
                                continue
        
        return matches
    
    def _clean_js_object(self, js_str: str) -> Optional[str]:
        """
        清理JavaScript对象字符串，使其成为有效的JSON
        """
        try:
            # 移除注释
            js_str = re.sub(r'/\*.*?\*/|//.*', '', js_str, flags=re.DOTALL)
            
            # 替换单引号为双引号，但要小心处理字符串中的转义
            parts = []
            in_string = False
            escape_next = False
            i = 0
            
            while i < len(js_str):
                char = js_str[i]
                
                if escape_next:
                    parts.append(char)
                    escape_next = False
                elif char == '\\':
                    parts.append(char)
                    escape_next = True
                elif char in ['"', "'"] and not escape_next:
                    if not in_string:
                        in_string = char
                        parts.append('"')
                    elif char == in_string:
                        in_string = False
                        parts.append('"')
                    else:
                        parts.append(char)
                elif char == "'" and not in_string:
                    # 只替换不在字符串内的单引号
                    parts.append('"')
                else:
                    parts.append(char)
                
                i += 1
            
            cleaned = ''.join(parts)
            
            # 尝试修复一些常见的非标准JSON语法
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)  # 移除末尾多余的逗号
            cleaned = re.sub(r'(\w+):', r'"\1":', cleaned)    # 为键添加引号
            
            return cleaned
        except Exception:
            return js_str  # 如果清理失败，返回原始字符串
    
    def _convert_match_item(self, item: Any) -> Optional[Dict[str, Any]]:
        """
        将从JS获取的比赛项目转换为标准格式
        """
        try:
            match_data = {
                "match_id": str(item.get('id', item.get('matchNum', item.get('num', f"未知_{hash(str(item)) % 10000}")))),
                "league": item.get('league', item.get('competition', item.get('赛事', '未知联赛'))),
                "home_team": item.get('homeTeam', item.get('home', item.get('主队', '主队'))),
                "away_team": item.get('awayTeam', item.get('away', item.get('客队', '客队'))),
                "match_date": item.get('matchDate', item.get('date', item.get('比赛日期', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))),
                "match_time": item.get('matchTime', item.get('time', item.get('比赛时间', ''))),
                "odds_home_win": float(item.get('oddsHomeWin', item.get('homeOdds', item.get('主胜', 2.0)))),
                "odds_draw": float(item.get('oddsDraw', item.get('drawOdds', item.get('平', 3.0)))),
                "odds_away_win": float(item.get('oddsAwayWin', item.get('awayOdds', item.get('客胜', 3.5)))),
                "status": item.get('status', item.get('比赛状态', 'scheduled')),
                "score": item.get('score', item.get('比分', '-:-')),
                "popularity": item.get('popularity', item.get('热度', 50)),
                "source": "500彩票网(Selenium)"
            }
            return match_data
        except (ValueError, AttributeError, TypeError) as e:
            logger.warning(f"Error converting match item: {str(e)}, item: {item}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def scrape_five_hundred_jczq_selenium(days: int = 3) -> List[Dict[str, Any]]:
    """
    爬取500彩票网竞彩足球数据的便捷函数
    
    Args:
        days: 获取未来几天的比赛数据，默认3天
        
    Returns:
        List[Dict]: 比赛数据列表
    """
    scraper = FiveHundredSeleniumScraper()
    try:
        matches = scraper.get_matches(days)
        return matches
    finally:
        scraper.close()