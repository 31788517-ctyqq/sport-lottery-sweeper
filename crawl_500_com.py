"""从500彩票网爬取竞彩足球赛程"""
import asyncio
import sys
import io
import json
from datetime import datetime
from pathlib import Path
import re

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import aiohttp
from bs4 import BeautifulSoup


async def fetch_500_com():
    """从500彩票网获取比赛数据"""
    print("="*80)
    print("🎯 从500彩票网爬取今天的竞彩足球赛程")
    print("="*80)
    
    url = "https://trade.500.com/jczq/"
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📅 日期: {today}")
    print(f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🌐 目标网址: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.500.com/',
    }
    
    try:
        print("⚡ 正在访问页面...")
        timeout = aiohttp.ClientTimeout(total=15)
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=timeout) as response:
                print(f"   状态码: {response.status}")
                
                if response.status != 200:
                    print(f"❌ 访问失败: HTTP {response.status}")
                    return []
                
                # 获取页面内容（使用gb2312编码）
                content = await response.read()
                html = content.decode('gb2312', errors='ignore')
                print(f"   ✅ 页面大小: {len(html)} 字符\n")
                
                # 保存HTML用于分析
                debug_file = Path('debug') / '500_com_page.html'
                debug_file.parent.mkdir(exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"💾 HTML已保存: {debug_file}\n")
                
                # 解析HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                print("🔍 开始解析比赛数据...\n")
                
                # 查找比赛数据
                matches = []
                
                # 方法1: 查找比赛表格
                match_tables = soup.find_all('table', class_=re.compile('.*match.*|.*game.*|.*table.*'))
                print(f"   找到 {len(match_tables)} 个可能的比赛表格")
                
                # 方法2: 查找比赛行
                match_rows = soup.find_all('tr', class_=re.compile('.*match.*|.*game.*|.*row.*'))
                print(f"   找到 {len(match_rows)} 个可能的比赛行")
                
                # 方法3: 查找包含比赛数据的div
                match_divs = soup.find_all('div', class_=re.compile('.*match.*|.*game.*|.*item.*'))
                print(f"   找到 {len(match_divs)} 个可能的比赛div\n")
                
                # 方法4: 从JavaScript中提取数据
                print("🔍 查找JavaScript中的数据...")
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('match' in script.string.lower() or 'game' in script.string.lower()):
                        # 尝试提取JSON数据
                        try:
                            # 查找类似 var matchData = {...} 的模式
                            json_pattern = r'var\s+\w+\s*=\s*(\[.*?\]|\{.*?\});'
                            json_matches = re.findall(json_pattern, script.string, re.DOTALL)
                            
                            if json_matches:
                                print(f"   找到 {len(json_matches)} 个可能的JSON数据块")
                                
                                for json_str in json_matches[:3]:  # 只尝试前3个
                                    try:
                                        data = json.loads(json_str)
                                        if isinstance(data, (list, dict)):
                                            print(f"   ✅ 成功解析JSON数据")
                                            # 保存原始数据
                                            with open('debug/500_com_data.json', 'w', encoding='utf-8') as f:
                                                json.dump(data, f, ensure_ascii=False, indent=2)
                                            print(f"   💾 数据已保存: debug/500_com_data.json")
                                            
                                            # 尝试解析为比赛数据
                                            matches = parse_json_data(data)
                                            if matches:
                                                break
                                    except:
                                        continue
                        except Exception as e:
                            continue
                
                # 如果没有找到数据，尝试解析HTML表格
                if not matches:
                    print("\n🔄 尝试解析HTML表格...")
                    matches = parse_html_table(soup)
                
                return matches
                
    except asyncio.TimeoutError:
        print("❌ 请求超时")
        return []
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_json_data(data):
    """解析JSON数据"""
    matches = []
    
    try:
        # 如果是列表
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    match = extract_match_from_dict(item)
                    if match:
                        matches.append(match)
        
        # 如果是字典
        elif isinstance(data, dict):
            # 查找可能包含比赛列表的键
            for key in ['matches', 'list', 'data', 'games', 'items']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict):
                            match = extract_match_from_dict(item)
                            if match:
                                matches.append(match)
                    break
    except Exception as e:
        print(f"   解析JSON失败: {e}")
    
    return matches


def extract_match_from_dict(item):
    """从字典中提取比赛信息"""
    try:
        match = {
            'match_id': item.get('id', item.get('matchId', item.get('num', ''))),
            'league': item.get('league', item.get('leagueName', item.get('联赛', '未知联赛'))),
            'home_team': item.get('homeTeam', item.get('home', item.get('主队', ''))),
            'away_team': item.get('awayTeam', item.get('away', item.get('客队', ''))),
            'match_time': item.get('matchTime', item.get('time', item.get('时间', ''))),
            'odds_home_win': float(item.get('homeWin', item.get('oddsH', item.get('主胜', 0)))),
            'odds_draw': float(item.get('draw', item.get('oddsD', item.get('平', 0)))),
            'odds_away_win': float(item.get('awayWin', item.get('oddsA', item.get('客胜', 0)))),
            'status': item.get('status', item.get('状态', 'scheduled')),
            'score': item.get('score', item.get('比分', '-:-')),
        }
        
        # 验证必要字段
        if match['home_team'] and match['away_team']:
            return match
        
    except Exception as e:
        pass
    
    return None


def parse_html_table(soup):
    """解析HTML表格"""
    matches = []
    
    try:
        # 查找所有表格
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                # 尝试从单元格中提取比赛信息
                if len(cells) >= 4:  # 至少需要4列
                    try:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # 检查是否包含比赛编号和VS
                        if len(cell_texts) >= 4 and 'VS' in cell_texts[3]:
                            match_num = cell_texts[0]  # 编号
                            league = cell_texts[1]     # 联赛
                            match_time = cell_texts[2] # 时间
                            teams_text = cell_texts[3] # 主队VS客队
                            
                            # 解析主客队
                            if 'VS' in teams_text:
                                # 移除方括号中的排名
                                teams_text = re.sub(r'\[\d+\]', '', teams_text)
                                parts = teams_text.split('VS')
                                
                                if len(parts) == 2:
                                    home_team = parts[0].strip()
                                    away_team = parts[1].strip()
                                    
                                    # 提取赔率（如果有）
                                    odds_home = 0
                                    odds_draw = 0
                                    odds_away = 0
                                    
                                    # 从后续单元格提取赔率
                                    for i, cell in enumerate(cells[4:], 4):
                                        text = cell.get_text(strip=True)
                                        # 查找赔率值
                                        odds_match = re.findall(r'\d+\.\d+', text)
                                        if odds_match and i-4 < 3:
                                            if i-4 == 0:
                                                odds_home = float(odds_match[0])
                                            elif i-4 == 1:
                                                odds_draw = float(odds_match[0])
                                            elif i-4 == 2:
                                                odds_away = float(odds_match[0])
                                    
                                    match = {
                                        'match_id': match_num,
                                        'league': league if league else '未知联赛',
                                        'home_team': home_team,
                                        'away_team': away_team,
                                        'match_time': match_time,
                                        'odds_home_win': odds_home,
                                        'odds_draw': odds_draw,
                                        'odds_away_win': odds_away,
                                        'status': 'scheduled',
                                        'score': '-:-',
                                        'source': '500彩票网',
                                    }
                                    
                                    matches.append(match)
                                    print(f"   ✅ 解析: {match_num} {home_team} vs {away_team}")
                            
                    except Exception as e:
                        continue
        
    except Exception as e:
        print(f"   解析HTML表格失败: {e}")
    
    return matches


def display_matches(matches):
    """显示比赛数据"""
    if not matches:
        print("\n❌ 未能解析到比赛数据")
        print("\n💡 建议:")
        print("   1. 查看 debug/500_com_page.html 分析页面结构")
        print("   2. 使用浏览器开发者工具查看网络请求")
        print("   3. 网站可能需要JavaScript渲染或有反爬虫机制")
        return
    
    print("="*80)
    print(f"✅ 成功解析 {len(matches)} 场比赛")
    print("="*80)
    
    # 按联赛分组
    leagues = {}
    for match in matches:
        league = match['league']
        if league not in leagues:
            leagues[league] = []
        leagues[league].append(match)
    
    print(f"\n📊 联赛统计:")
    print(f"   总联赛数: {len(leagues)}")
    print(f"   总比赛数: {len(matches)}\n")
    
    # 显示比赛
    print("="*80)
    print("📋 比赛详情")
    print("="*80)
    
    match_num = 1
    for league, league_matches in sorted(leagues.items()):
        print(f"\n🏆 {league} ({len(league_matches)}场)")
        print("-"*80)
        
        for match in league_matches:
            print(f"\n{match_num}. {match['home_team']} vs {match['away_team']}")
            print(f"   时间: {match['match_time']}")
            
            if match['odds_home_win'] > 0:
                print(f"   赔率: 胜{match['odds_home_win']:.2f} 平{match['odds_draw']:.2f} 负{match['odds_away_win']:.2f}")
            
            if match.get('score'):
                print(f"   比分: {match['score']}")
            
            match_num += 1
    
    # 保存数据
    output_file = Path('debug') / f'500_com_matches_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print(f"💾 数据已保存: {output_file}")
    print("="*80)


async def main():
    print("\n" + "⚽"*40)
    print("500彩票网竞彩足球爬虫")
    print("⚽"*40 + "\n")
    
    try:
        matches = await fetch_500_com()
        display_matches(matches)
        
        print("\n" + "="*80)
        print("✅ 爬取完成")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
