"""
测试解析逻辑
"""
import asyncio
import sys
import os
from bs4 import BeautifulSoup

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.scrapers.zqszsc_scraper import zqszsc_scraper


def test_parse_logic():
    """测试解析逻辑"""
    print("开始测试解析逻辑...")
    
    # 读取之前保存的页面内容
    try:
        with open('page_content.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("找不到 page_content.html 文件，先运行 inspect_content.py")
        return
    
    soup = BeautifulSoup(content, 'html.parser')
    tbody_elements = soup.find_all('tbody')
    
    print(f"找到 {len(tbody_elements)} 个tbody元素")
    
    # 创建爬虫实例以测试解析方法
    scraper = zqszsc_scraper
    
    matches = []
    
    for i, tbody in enumerate(tbody_elements[1:6]):  # 检查第2-6个tbody（跳过表头）
        print(f"\n--- 处理 tbody {i+2} ---")
        rows = tbody.find_all('tr')
        
        for j, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            print(f"  行 {j+1}: {cell_texts}")
            
            # 尝试解析这一行
            match_data = scraper._extract_match_from_element(row)
            if match_data:
                matches.append(match_data)
                print(f"    → 解析结果: {match_data}")
    
    print(f"\n总共解析出 {len(matches)} 场比赛")
    for i, match in enumerate(matches):
        print(f"{i+1}. {match.get('match_id', 'N/A')} - {match.get('league', 'N/A')} - "
              f"{match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} - "
              f"{match.get('match_time', 'N/A')}")


if __name__ == "__main__":
    test_parse_logic()