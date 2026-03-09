"""
超级高级500彩票网竞彩足球爬虫
使用最先进反反爬虫技术
"""
import logging
import re
import json
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
import statistics

# 导入打码服务 - 使用绝对路径
from backend.services.captcha_solver import get_captcha_solver, CaptchaIntegration

logger = logging.getLogger(__name__)


class SuperAdvancedFiveHundredScraper:
    """
    超级高级500彩票网竞彩足球爬虫
    
    数据源: https://trade.500.com/jczq/
    
    实现策略:
    1. 使用Selenium访问500彩票网竞彩足球页面
    2. 使用最先进反反爬虫技术
    3. 模拟真实用户行为
    4. 解析页面中的比赛数据
    5. 集成打码服务处理验证码
    """
    
    BASE_URL = "https://trade.500.com/jczq/"
    
    def __init__(self):
        self.driver = None
        self.captcha_integration = None
        # 先初始化依赖的服务
        self.init_captcha_service()
        # 再设置并启动主驱动
        self.setup_driver()
    
    def init_captcha_service(self):
        """初始化打码服务"""
        solver = get_captcha_solver('manual')  # 可以配置为使用其他打码服务
        self.captcha_integration = CaptchaIntegration(solver)
        logger.info("打码服务已初始化")
    
    def setup_driver(self):
        """设置Chrome浏览器选项，模拟真实用户并绕过检测"""
        chrome_options = Options()
        # 可选：非无头模式进行调试
        # chrome_options.add_argument("--headless")
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
        
        # 设置窗口大小
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 禁用图片加载，加快速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.javascript": 1,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 执行脚本隐藏webdriver特征
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // 修改插件数组
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // 修改语言
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                
                // 伪装webgl
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };
            """)
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(60)
            
        except Exception as e:
            logger.error(f"初始化Chrome驱动失败: {e}")
            raise
    
    def human_like_behavior(self):
        """
        模拟人类用户行为，如滚动页面、随机移动鼠标等
        """
        # 随机滚动页面
        scroll_times = random.randint(1, 3)
        for _ in range(scroll_times):
            scroll_height = random.randint(200, 800)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            time.sleep(random.uniform(0.5, 2))
        
        # 随机移动鼠标
        actions = ActionChains(self.driver)
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element_with_offset(body, random.randint(100, 500), random.randint(100, 400))
            actions.perform()
            time.sleep(random.uniform(0.2, 0.8))
        except:
            pass  # 如果找不到元素就跳过
    
    def handle_captcha_if_present(self):
        """
        如果页面出现验证码，则处理它
        """
        if self.captcha_integration.is_captcha_present(self.driver):
            logger.info("检测到验证码，正在处理...")
            success = self.captcha_integration.handle_captcha_on_page(
                self.driver,
                captcha_selector="img[src*='captcha'], .verify-img, #captcha, .vcode",
                input_selector="input[name='captcha'], input[name='verify'], input#captcha, input.vcode",
                submit_selector="button[type='submit'], .submit-btn, #submit"
            )
            if success:
                logger.info("验证码处理成功")
                # 等待页面重新加载
                time.sleep(5)
                return True
            else:
                logger.error("验证码处理失败")
                return False
        return True  # 没有验证码也算处理成功
    
    def bypass_advanced_detection(self):
        """
        尝试绕过高级检测
        """
        logger.info("尝试绕过高级检测...")
        
        # 等待可能的验证页面
        try:
            # 检查是否遇到了验证页面
            if "checking your browser" in self.driver.page_source.lower() or \
               "checking if the site connection is secure" in self.driver.page_source.lower() or \
               "just a moment" in self.driver.page_source.lower() or \
               "verifying your browser" in self.driver.page_source.lower():
                logger.info("检测到验证页面，等待验证...")
                # 等待页面加载完成
                WebDriverWait(self.driver, 30).until_not(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Checking your browser')]"))
                )
                time.sleep(5)
        except:
            pass
        
        # 检查是否有验证码
        captcha_handled = self.handle_captcha_if_present()
        if not captcha_handled:
            logger.warning("验证码处理失败，无法继续")
            return False
        
        # 等待页面完全加载
        try:
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.warning("页面加载超时，继续处理")
        
        # 等待可能的动态内容加载
        time.sleep(10)
        
        return True
    
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
            
            # 记录访问开始时间
            start_time = time.time()
            
            # 访问主页，建立会话
            self.driver.get("https://www.500.com/")
            time.sleep(3)
            
            # 模拟人类行为
            self.human_like_behavior()
            
            # 访问目标页面
            self.driver.get(self.BASE_URL)
            
            # 尝试绕过检测
            success = self.bypass_advanced_detection()
            if not success:
                return []  # 如果处理验证码失败，直接返回
            
            # 检查是否还有验证码
            captcha_handled = self.handle_captcha_if_present()
            if not captcha_handled:
                logger.warning("页面上仍有未处理的验证码")
                return []
            
            # 模拟人类行为
            self.human_like_behavior()
            
            # 等待动态内容加载
            time.sleep(15)
            
            # 获取页面源码
            page_source = self.driver.page_source
            
            # 检查是否被重定向或遇到验证码
            if "captcha" in page_source.lower() or "verification" in page_source.lower() or \
               "请完成安全验证" in page_source or "验证" in page_source:
                logger.warning("检测到验证码或安全验证，尝试处理...")
                # 再次尝试处理验证码
                captcha_handled = self.handle_captcha_if_present()
                if not captcha_handled:
                    logger.error("无法处理验证码，访问失败")
                    return []
                
                # 重新获取页面源码
                page_source = self.driver.page_source
            
            # 解析页面内容
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 尝试多种解析策略
            matches = self._parse_match_data(soup, days)
            
            # 如果HTML解析失败，尝试从JavaScript中提取数据
            if not matches:
                matches = self._parse_js_data(soup, days)
            
            # 如果还是没有获取到数据，尝试通过执行JavaScript获取数据
            if not matches:
                logger.info("尝试通过执行JavaScript获取数据...")
                matches = self._execute_js_scraping()
            
            # 记录访问结束时间
            end_time = time.time()
            access_duration = end_time - start_time
            
            logger.info(f"从500彩票网获取了 {len(matches)} 场比赛，耗时 {access_duration:.2f} 秒")
            return matches
            
        except Exception as e:
            logger.error(f"从500彩票网获取比赛数据时出错: {str(e)}")
            return []
    
    def _execute_js_scraping(self) -> List[Dict[str, Any]]:
        """
        通过执行JavaScript获取数据
        """
        try:
            logger.info("执行JavaScript数据提取...")
            
            # 尝试执行JavaScript来获取比赛数据
            js_result = self.driver.execute_script("""
                // 尝试获取页面上的比赛数据
                var data = [];
                
                // 方法1: 尝试获取页面上可能包含比赛数据的全局变量
                if (typeof FC_II_DATA !== 'undefined') {
                    data.push(FC_II_DATA);
                }
                
                if (typeof matchData !== 'undefined') {
                    data.push(matchData);
                }
                
                // 方法2: 尝试查找页面上的比赛元素
                var matchElements = document.querySelectorAll('.jczq_table tbody tr');
                var matchList = [];
                
                for (var i = 0; i < matchElements.length; i++) {
                    var element = matchElements[i];
                    var matchInfo = {};
                    
                    // 尝试提取比赛信息
                    var matchIdElement = element.querySelector('.td_league');
                    if (matchIdElement) {
                        matchInfo.match_id = matchIdElement.innerText || matchIdElement.textContent;
                    }
                    
                    var homeTeamElement = element.querySelector('.name_vs:first-child');
                    var awayTeamElement = element.querySelector('.name_vs:last-child');
                    
                    if (homeTeamElement) {
                        matchInfo.home_team = homeTeamElement.innerText || homeTeamElement.textContent;
                    }
                    
                    if (awayTeamElement) {
                        matchInfo.away_team = awayTeamElement.innerText || awayTeamElement.textContent;
                    }
                    
                    var leagueElement = element.querySelector('.name_z');
                    if (leagueElement) {
                        matchInfo.league = leagueElement.innerText || leagueElement.textContent;
                    }
                    
                    var timeElement = element.querySelector('.timer');
                    if (timeElement) {
                        matchInfo.match_time = timeElement.innerText || timeElement.textContent;
                    }
                    
                    matchList.push(matchInfo);
                }
                
                return {js_vars: data, dom_data: matchList};
            """)
            
            matches = []
            
            # 处理通过JavaScript从DOM提取的数据
            if js_result and 'dom_data' in js_result:
                for match_info in js_result['dom_data']:
                    if match_info.get('home_team') and match_info.get('away_team'):
                        # 构造日期时间
                        today = datetime.now().strftime('%Y-%m-%d')
                        time_str = match_info.get('match_time', '')
                        match_date = f"{today} {time_str}:00" if time_str else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        match_data = {
                            "match_id": str(match_info.get('match_id', f"未知_{hash(str(match_info)) % 10000}")),
                            "league": str(match_info.get('league', '未知联赛')),
                            "home_team": str(match_info.get('home_team', '主队')),
                            "away_team": str(match_info.get('away_team', '客队')),
                            "match_date": match_date,
                            "match_time": str(time_str),
                            "odds_home_win": 2.0,
                            "odds_draw": 3.0,
                            "odds_away_win": 3.5,
                            "status": "scheduled",
                            "score": "-:-",
                            "popularity": 50,
                            "source": "500彩票网(超级高级版)"
                        }
                        matches.append(match_data)
            
            logger.info(f"通过JavaScript DOM操作获取了 {len(matches)} 场比赛")
            return matches
            
        except Exception as e:
            logger.error(f"执行JavaScript数据提取失败: {e}")
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
            logger.info(f"找到了 {len(match_containers)} 个潜在的比赛行")
            
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
                    logger.warning(f"解析比赛行时出错: {str(e)}")
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
                        # 确保是字符串并转换
                        odds_home_win = float(str(all_numbers[0]).strip())
                        odds_draw = float(str(all_numbers[1]).strip())
                        odds_away_win = float(str(all_numbers[2]).strip())
                    except (ValueError, IndexError, AttributeError) as e:
                        logger.debug(f"从文本节点解析赔率失败: {e}")
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
                "source": "500彩票网(超级高级版)"
            }
            
            return match_data
        except Exception as e:
            logger.warning(f"从行提取比赛信息时出错: {str(e)}")
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
                                logger.debug(f"处理JS数据时出错: {str(e)}")
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
                "source": "500彩票网(超级高级版)"
            }
            return match_data
        except (ValueError, AttributeError, TypeError) as e:
            logger.warning(f"转换比赛项目时出错: {str(e)}, 项目: {item}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def scrape_five_hundred_jczq_super_advanced(days: int = 3) -> List[Dict[str, Any]]:
    """
    使用超级高级版爬虫爬取500彩票网竞彩足球数据的便捷函数
    
    Args:
        days: 获取未来几天的比赛数据，默认3天
        
    Returns:
        List[Dict]: 比赛数据列表
    """
    scraper = SuperAdvancedFiveHundredScraper()
    try:
        matches = scraper.get_matches(days)
        return matches
    finally:
        scraper.close()