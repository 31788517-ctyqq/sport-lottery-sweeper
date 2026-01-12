# sources.py - 数据源连接与解析
import logging
import re
import json
import requests
from typing import Optional, List
from datetime import datetime, timedelta
from data_source import MatchInfo, MatchStatus, Strategy

logger = logging.getLogger(__name__)

def create_request_session() -> requests.Session:
    """创建请求会话"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://www.vipc.cn/live/jczq' # Referer 通常是必要的
    })
    return session

class VipcCnJsSource:
    """
    从 VIPC 的 JavaScript 文件获取竞彩足球数据
    """
    def __init__(self):
        self.js_url = "https://www.vipc.cn/js/app/live-index.js"
        self.session = create_request_session()

    def get_matches(self) -> List[MatchInfo]:
        """
        从 JS 文件中提取比赛信息
        """
        logger.info(f"尝试从 JS 文件获取比赛数据: {self.js_url}")
        matches = []
        try:
            response = self.session.get(self.js_url, timeout=15)
            response.raise_for_status()
            js_content = response.text

            # 尝试查找可能包含比赛数据的变量或函数调用
            # 常见的模式：var data = {...}; 或 const data = [...]; 或 初始化函数参数
            # 使用正则表达式查找 JSON 数组或对象
            # 这个正则比较宽松，寻找 [{...}] 或 {...} 的模式
            # 更精确地，我们寻找可能与 jczq 相关的数据
            # 尝试匹配 var liveJczqData = [...] 或类似结构
            # pattern = r'(?:var|let|const)\s+\w+\s*=\s*(\[.*?\]);'
            # 更针对性地查找包含 'jczq' 或 'match' 相关的变量
            # 例如，寻找可能的初始数据赋值
            # pattern = r'(\[\s*\{(?:[^{}]|(?R))*\}\s*\])'
            # 更简单的办法：寻找可能的数据初始化点
            # 例如：liveJczqData: function(e){e.data=...}
            # 或者直接搜索 JSON 数组模式

            # 尝试匹配 JS 文件中的大型 JSON 对象或数组
            # 由于 JS 文件可能很复杂，我们先找最可能的入口
            # 搜索类似 `jczqData = [...]` 或 `matchList: [...]` 的模式
            # pattern = r'(?:jczqData|matchList|initialData)\s*[:=]\s*(\[.*?\]);'
            # pattern = r'var\s+jczqData\s*=\s*(\[.*?\]);'
            # pattern = r'var\s+liveJczqData\s*=\s*(\[.*?\]);'
            # pattern = r'var\s+data\s*=\s*(\[.*?\]);'

            # 根据 JS 内容推测，寻找包含 matchId, h_cn, a_cn, l_cn 等字段的数组
            # pattern = r'(\[\s*\{[^}]*?"matchId"[^}]*?\}\s*\])'
            # pattern = r'(\[\s*\{[^}]*?"id"[^}]*?\}\s*\])'
            # 尝试查找可能的初始化数据，例如 `e.data = [...]`
            # pattern = r'e\.data\s*=\s*(\[.*?\]);'
            # 尝试查找可能的模块导出数据
            # pattern = r'(\[\s*\{[^}]*?"date"[^}]*?\}\s*\])'

            # 更简单粗暴的方式：尝试直接查找整个 JS 中的大型 JSON 数组
            # 找到第一个完整的 `[ { ... }, { ... } ]` 结构
            # 这个正则试图匹配一个数组，数组元素是对象
            # 注意：Python re 不支持递归，所以不能完美匹配嵌套
            # 我们尝试用贪婪模式匹配可能的数组
            # pattern = r'\[\s*\{.*?"id".*?\}.*?\]'
            # 为了更安全，我们尝试找到可能的赋值语句
            # 例如: var someVar = [...];
            # 寻找可能的变量名和其后的数组
            # pattern = r'(?:var|const|let)\s+(\w+)\s*=\s*(\[\s*\{.*?\}\s*\]);'
            # 为了简化，我们假设数据是某个变量赋值的结果
            # 尝试查找常见的变量名
            common_var_names = [
                r'liveJczqData', r'jczqData', r'data', r'listData', r'matchList',
                r'initialData', r'fixtures', r'scheduleData', r'futureMatches'
            ]
            pattern = r'(?:' + '|'.join(common_var_names) + r')\s*[:=]\s*(\[.*?\]);'

            matches_found = re.findall(pattern, js_content, re.DOTALL)
            if not matches_found:
                 # 如果没找到常见的变量名，尝试更通用的模式，寻找数组
                 # 尝试匹配 `someKey: [...]` 或 `someKey = [...]`
                 generic_pattern = r'[:=]\s*(\[.*?\{\s*["\'](?:id|matchId|date)["\'].*?\}\s*\]);'
                 generic_matches = re.findall(generic_pattern, js_content, re.DOTALL)
                 if generic_matches:
                     logger.info("在 JS 文件中找到了可能的数据结构（通用模式）")
                     # 假设第一个匹配的就是我们需要的
                     json_str = generic_matches[0].strip()
                 else:
                     logger.error("未能在 JS 文件中找到预期的数据结构。")
                     return []
            else:
                logger.info("在 JS 文件中找到了可能的数据结构（变量赋值模式）")
                # 假设最后一个匹配是我们需要的
                json_str = matches_found[-1].strip()

            # 尝试解析 JSON 字符串
            # JS 中的对象可能包含单引号，需要替换为双引号
            # 并且可能包含 trailing commas, unquoted keys 等 JS 特性
            # 最可靠的方法是尝试用 JS 引擎，但 Python 通常用正则或 ast.literal_eval 预处理
            # 这里我们先尝试简单的字符串替换，然后用 json.loads
            # 替换未加引号的键
            json_str = re.sub(r'([{,]\s*)(\w+?)\s*:', r'\1"\2":', json_str)
            # 替换单引号为双引号（注意边界情况，如字符串内的单引号）
            # 这一步风险较大，如果 JSON 结构复杂，可能会出错
            # 更稳妥的做法是使用 jsbeautifier 或类似工具，但这增加了依赖
            # 暂时先尝试简单替换
            # 首先处理字符串值内的引号转义
            # 一个相对安全的方法是使用正则替换字符串部分
            # 匹配 "key": 'value' 或 "key": value, 并处理 value 部分
            # 这非常复杂，最好的方式是让 JS 执行，但 Python 中不行
            # 尝试用 ast.literal_eval 预处理可能的 Python 字面量，但这不适用于 JS
            # 最终还是尝试 json.loads，但先进行一些预处理
            # 移除注释（虽然 JS 里的 JSON 通常不会有注释）
            # 替换常见的 JS 特殊字符
            # json_str = json_str.replace("'", '"') # 这个太暴力，不行
            # 尝试用 demjson3 库，或者自己写一个简单的转换器
            # 或者，如果结构固定，手动处理
            # 由于不确定 JS 数据的确切格式，我们先尝试原样加载
            # 如果失败，再考虑预处理
            # logger.debug(f"Parsing JSON string: {json_str[:200]}...") # 打印开头部分用于调试
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"解析 JS 提取的 JSON 数据失败: {e}")
                logger.debug(f"Failed JSON string part: {json_str[:500]}...") # 打印部分用于调试
                # 尝试进行简单的预处理
                # 1. 替换未加引号的键
                processed_json_str = re.sub(r'([{,]\s*)(\w+?)\s*:', r'\1"\2":', json_str)
                # 2. 尝试更智能地替换单引号，仅在值的边界（前后是 : 或 , 或 ] 或 }）
                # 这个正则非常复杂，容易出错
                # 一个简化方法是，如果 JS 中的字符串值都是用双引号，那么 json.loads 应该能工作
                # 如果 JS 中混用了单引号，且在字符串内部也有单引号，则非常难处理
                # 这里我们假设字符串值都用双引号，或者结构足够简单
                # 如果还是失败，可能需要引入第三方库如 py_mini_racer 来在 Python 中执行 JS
                # 为了暂时解决，我们假设数据是标准 JSON 格式（JS 中用双引号）
                # 如果不是，我们会在这里失败
                try:
                    data = json.loads(processed_json_str)
                except json.JSONDecodeError as e2:
                    logger.error(f"即使预处理后，解析 JS 提取的 JSON 数据仍失败: {e2}")
                    logger.debug(f"Processed JSON string part: {processed_json_str[:500]}...")
                    return []

            if not isinstance(data, list):
                logger.error(f"解析出的数据不是列表类型: {type(data)}")
                return []

            logger.info(f"从 JS 文件解析出 {len(data)} 条原始数据")

            for item in data:
                if not isinstance(item, dict):
                    logger.warning(f"数据项不是字典类型: {item}")
                    continue

                # 根据你提供的 JS 文件内容，字段可能像这样：
                # { id: "123", l_cn: "英超", h_cn: "曼联", a_cn: "切尔西", date: "2024-03-10", time: "20:00", ... }
                match_id = str(item.get('id', item.get('matchId', '')))
                if not match_id: # 如果没有 ID，跳过
                    logger.warning(f"数据项缺少 ID，跳过: {item}")
                    continue

                league = item.get('l_cn', item.get('league', '未知联赛'))
                home_team = item.get('h_cn', item.get('home', '主队'))
                away_team = item.get('a_cn', item.get('away', '客队'))
                date_str = item.get('date', item.get('matchDate', ''))
                time_str = item.get('time', item.get('matchTime', '00:00'))

                # 解析时间
                kickoff_time = None
                if date_str and time_str:
                    try:
                        full_time_str = f"{date_str} {time_str}"
                        kickoff_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
                    except ValueError as ve:
                        logger.warning(f"JS 时间解析失败 {full_time_str}: {ve}")
                        continue # 如果时间解析失败，跳过这场比赛
                else:
                    logger.warning(f"比赛 {match_id} 缺少日期或时间信息: {date_str}, {time_str}")
                    continue # 如果缺少日期或时间，跳过这场比赛

                # 判断比赛状态 (根据 JS 数据中可能存在的字段)
                status_str = item.get('status', item.get('state', '')).lower()
                status = MatchStatus.UPCOMING.value
                if 'finish' in status_str or 'end' in status_str or '完场' in status_str:
                    status = MatchStatus.FINISHED.value
                elif 'live' in status_str or 'playing' in status_str or '进行' in status_str:
                    status = MatchStatus.LIVE.value
                elif 'cancel' in status_str or '取消' in status_str:
                    status = MatchStatus.CANCELLED.value

                match_info = MatchInfo(
                    match_id=match_id,
                    league=league,
                    home_team=home_team,
                    away_team=away_team,
                    kickoff_time=kickoff_time,
                    source="vipc_js",
                    strategy=Strategy.ALTERNATIVE_API.value, # 从JS获取，算作一种API变体
                    status=status
                )
                matches.append(match_info)

            logger.info(f"从 JS 文件成功解析到 {len(matches)} 场比赛信息")
            return matches

        except requests.exceptions.RequestException as e:
            logger.error(f"请求 JS 文件失败: {e}")
        except Exception as e:
            logger.error(f"解析 JS 文件数据时发生未知错误: {e}", exc_info=True)
        return []

# --- 保留旧的 API 和 Selenium 类（可选，用于降级或对比） ---

class VipcCnApi:
    """ VIPC 竞彩足球 API 获取类 (保留，但主要逻辑移至 VipcCnPage) """
    def __init__(self):
        # 指定的 API 地址 (保留，但不作为主要数据源)
        self.base_url = "https://api2.vipc.cn/live/jczq"
        self.session = create_request_session()

    def get_matches(self) -> List[MatchInfo]:
        """ 从 VIPC API 获取赛程信息 (此方法现在主要作为备选或辅助)。 """
        logger.info(f"尝试从 VIPC API 获取赛程信息: {self.base_url}")
        matches = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                match_list = data['data']
            elif isinstance(data, list):
                match_list = data
            else:
                logger.error(f"API 返回的数据格式不符合预期: {type(data)}")
                return matches

            logger.info(f"API 返回了 {len(match_list)} 条原始数据")
            for item in match_list:
                if not isinstance(item, dict):
                    continue
                match_id = str(item.get('id', item.get('matchId', '')))
                date_str = item.get('date', item.get('matchDate', ''))
                time_str = item.get('time', item.get('matchTime', '00:00'))
                league = item.get('l_cn', item.get('leagueName', '未知联赛'))
                home_team = item.get('h_cn', item.get('homeTeam', '主队'))
                away_team = item.get('a_cn', item.get('awayTeam', '客队'))

                kickoff_time = datetime.now()
                try:
                    if date_str:
                        full_time_str = f"{date_str} {time_str}"
                        kickoff_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
                    else:
                        kickoff_time = datetime.strptime(time_str, "%H:%M").replace(
                            year=datetime.now().year,
                            month=datetime.now().month,
                            day=datetime.now().day
                        )
                except ValueError as e:
                    logger.warning(f"API 时间解析失败 {date_str} {time_str}: {e}")

                match_info = MatchInfo(
                    match_id=match_id,
                    league=league,
                    home_team=home_team,
                    away_team=away_team,
                    kickoff_time=kickoff_time,
                    source="vipc_api",
                    strategy=Strategy.DIRECT_REQUEST.value
                )
                matches.append(match_info)

            logger.info(f"从 API 成功解析到 {len(matches)} 场比赛信息")
            return matches
        except requests.exceptions.RequestException as e:
            logger.error(f"请求 VIPC API 失败: {e}")
        except Exception as e:
            logger.error(f"解析 VIPC API 数据时发生未知错误: {e}", exc_info=True)
        return []

class VipcCnPage:
    """ VIPC 竞彩足球 HTML 页面获取类 (使用 Selenium 获取动态内容) """
    def __init__(self, headless=True, wait_time=10):
        self.base_url = "https://www.vipc.cn/live/jczq"
        self.wait_time = wait_time # WebDriverWait 的等待时间
        self.headless = headless # 是否以无头模式运行

    def get_matches(self, days: int = 3) -> List[MatchInfo]:
        """ 从 VIPC HTML 页面获取比赛信息 (使用 Selenium)。 """
        logger.info(f"正在从 VIPC HTML 页面获取未来 {days} 天的比赛信息: {self.base_url}")
        logger.info(f"使用 Selenium 驱动浏览器 (Headless: {self.headless})")
        matches = []

        # --- Selenium 设置 ---
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        import os

        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("--remote-debugging-port=9222")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = None
        try:
            service = Service() # 如果 ChromeDriver 不在 PATH 中，需要指定 executable_path
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            driver.get(self.base_url)

            # 尝试点击“赛程”或“未来”按钮，如果存在
            # 需要根据实际页面结构调整
            # 例如，查找包含“赛程”或“未来”的按钮
            # locator = (By.XPATH, "//button[contains(text(), '赛程')] | //a[contains(text(), '赛程')]")
            # try:
            #     schedule_btn = WebDriverWait(driver, self.wait_time).until(
            #         EC.element_to_be_clickable(locator)
            #     )
            #     schedule_btn.click()
            #     logger.info("点击了‘赛程’按钮。")
            # except TimeoutException:
            #     logger.info("未找到‘赛程’按钮，可能默认显示。")

            # 等待 .match-list 元素出现 (使用旧的选择器，因为这是基于原始 HTML 的猜测)
            # 现在我们知道这可能不正确，但可以作为一个后备或用于测试
            # 我们需要你提供新的、正确的 CSS 选择器
            logger.info("等待比赛列表元素加载...")
            # 注意：这里的 ".match-list" 是旧的，很可能找不到
            # 需要替换为你通过检查元素找到的新选择器
            # 例如，如果检查到的是 <div class="new-match-list-class">
            # 则使用 ".new-match-list-class"
            # 或者如果是 <section id="match-schedule-section">
            # 则使用 "#match-schedule-section"
            # 假设你找到了新的选择器是 .new-container-class
            new_selector = ".match-list" # <-- 请替换为你找到的实际选择器
            try:
                WebDriverWait(driver, self.wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, new_selector))
                )
                logger.info(f"找到了元素: {new_selector}")
            except TimeoutException:
                logger.error(f"等待元素 '{new_selector}' 超时 ({self.wait_time} 秒)，页面源码可能是:")
                logger.debug(driver.page_source[:2000])
                return matches # 如果找不到，返回空

            # 获取渲染后的页面源码
            html_content = driver.page_source
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # 使用新的选择器查找比赛列表容器
            match_list_div = soup.find('div', class_='match-list') # <-- 也需要同步更新这里，如果选择器变了
            # 例如，如果选择器是 div.new-match-list-class
            # match_list_div = soup.find('div', class_='new-match-list-class')
            # 或者如果是 section#match-schedule-section
            # match_list_div = soup.find('section', id='match-schedule-section')
            # 或者使用通用 find
            # match_list_div = soup.select_one(new_selector)
            if not match_list_div:
                logger.error(f"在页面源码中未能找到指定的选择器 '{new_selector}' 对应的元素")
                return matches

            # --- 以下是之前解析 HTML 的逻辑 ---
            # ... (保持原有的解析逻辑不变，但应用到新的容器 match_list_div 上) ...
            # 获取未来几天的日期列表
            today = datetime.now()
            target_dates = [today + timedelta(days=i) for i in range(days)]
            target_date_strs = [d.strftime('%m/%d') for d in target_dates]

            # 查找所有 .date-group，这代表不同日期的比赛
            date_groups = match_list_div.find_all('div', class_='date-group')
            logger.info(f"找到 {len(date_groups)} 个日期分组")

            for group in date_groups:
                # 获取日期标签，例如 "今天" 或具体的 "01/09"
                # Selenium 解析可能更稳定，尝试多种定位方式
                date_label_elem = None
                # 尝试查找作为兄弟节点的 date-label
                prev_sibling = group.find_previous_sibling()
                if prev_sibling and 'date-label' in prev_sibling.get('class', []):
                    date_label_elem = prev_sibling
                # 如果没找到，尝试在 group 内部查找
                if not date_label_elem:
                    date_label_elem = group.find('div', class_='date-label')

                date_label_text = date_label_elem.get_text(strip=True) if date_label_elem else "未知日期"
                logger.debug(f"处理日期分组: {date_label_text}")

                # 尝试解析日期标签
                actual_date = None
                if "今天" in date_label_text:
                    actual_date = today.date()
                elif "明天" in date_label_text:
                    actual_date = (today + timedelta(days=1)).date()
                elif "昨天" in date_label_text:
                    actual_date = (today - timedelta(days=1)).date()
                else:
                    # 尝试匹配 MM/DD 格式
                    for date_str in target_date_strs:
                        if date_str.replace('/', '-') in date_label_text:
                            # 尝试匹配 01-09
                            actual_date = datetime.strptime(date_str, '%m/%d').date().replace(year=today.year)
                            break

                if not actual_date:
                    # 如果还是没找到，尝试更精确的匹配或跳过
                    logger.warning(f"无法解析日期标签 '{date_label_text}', 跳过此分组")
                    continue

                # 在当前日期分组下查找所有 .match-item
                match_items = group.find_all('div', class_='match-item')
                logger.info(f"在日期 {actual_date} 下找到 {len(match_items)} 场比赛")

                for item in match_items:
                    # 解析比赛信息
                    # <span class="match-number">周五002</span>
                    match_num_elem = item.find('span', class_='match-number')
                    match_number = match_num_elem.get_text(strip=True) if match_num_elem else ""

                    # <span class="league">沙特联</span>
                    league_elem = item.find('span', class_='league')
                    league = league_elem.get_text(strip=True) if league_elem else "未知联赛"

                    # <span class="teams">塞哈特海湾 VS 达马克</span>
                    teams_elem = item.find('span', class_='teams')
                    teams_text = teams_elem.get_text(strip=True) if teams_elem else ""

                    # 分离主客队 (通常用 " VS " 分隔)
                    if " VS " in teams_text:
                        home_team, away_team = teams_text.split(" VS ", 1)
                    else:
                        # 如果没有 " VS "，尝试其他可能的分隔符，如 "vs"
                        if " vs " in teams_text:
                            home_team, away_team = teams_text.split(" vs ", 1)
                        else:
                            # 如果还是没有分隔符，整体作为主队，客队为空
                            home_team = teams_text
                            away_team = "客队"

                    # <span class="time">01/09 01:00</span>
                    # 或者可能在其他地方，如 <a> 标签的 title
                    time_elem = item.find('span', class_='time')
                    time_text = time_elem.get_text(strip=True) if time_elem else ""
                    if not time_text:
                        # 尝试从 a 标签的 title 或其他可能的标签获取时间
                        time_link = item.find('a', href=True) # 假设时间在 a 标签里
                        if time_link:
                            time_text = time_link.get_text(strip=True)

                    # 如果时间文本是 "01/09 01:00" 这种格式，尝试解析
                    if '/' in time_text and ':' in time_text:
                        try:
                            parsed_time = datetime.strptime(f"{actual_date.year}/{time_text}", "%Y/%m/%d %H:%M")
                            kickoff_time = parsed_time
                        except ValueError:
                            logger.warning(f"无法解析时间文本 '{time_text}' 为 datetime 对象，跳过此场比赛")
                            continue
                    else:
                        # 如果时间格式不是 MM/DD HH:MM，则尝试只解析 HH:MM，并使用 actual_date
                        try:
                            time_only = datetime.strptime(time_text, "%H:%M").time()
                            kickoff_time = datetime.combine(actual_date, time_only)
                        except ValueError:
                            logger.warning(f"时间文本 '{time_text}' 格式不匹配，跳过此场比赛")
                            continue

                    # <span class="status">下半场 63'</span>
                    # 或者比分 <span class="score">3:0</span>
                    # 这里我们主要关心未开始的比赛，但也可以解析状态
                    status_elem = item.find('span', class_='status')
                    score_elem = item.find('span', class_='score')
                    status_text = status_elem.get_text(strip=True) if status_elem else ""
                    score_text = score_elem.get_text(strip=True) if score_elem else ""

                    # 简单判断比赛状态
                    status = MatchStatus.UPCOMING.value
                    if "完场" in status_text or ("VS" not in teams_text and score_text): # 如果已显示比分且非VS，则可能已结束
                        status = MatchStatus.FINISHED.value
                    elif "上半场" in status_text or "下半场" in status_text:
                        status = MatchStatus.LIVE.value

                    # 生成一个 match_id (如果页面没有直接提供，可以用组合ID)
                    # 使用比赛日期+联赛+对阵作为ID
                    match_id = f"{kickoff_time.strftime('%Y%m%d')}_{league}_{home_team}_{away_team}"

                    match_info = MatchInfo(
                        match_id=match_number, # 使用页面上的 match_number 作为 ID
                        league=league,
                        home_team=home_team.strip(),
                        away_team=away_team.strip(),
                        kickoff_time=kickoff_time,
                        source="vipc_page_selenium",
                        strategy=Strategy.SELENIUM.value, # 更新策略为 Selenium
                        status=status
                    )
                    matches.append(match_info)

            logger.info(f"从 HTML 页面成功解析到 {len(matches)} 场比赛信息")
            return matches
        except Exception as e:
            logger.error(f"使用 Selenium 解析 VIPC HTML 页面数据时发生未知错误: {e}", exc_info=True)
        finally:
            # 确保浏览器关闭
            if driver:
                driver.quit()
            logger.info("Selenium 浏览器已关闭。")
        return [] # 如果出错，返回空列表