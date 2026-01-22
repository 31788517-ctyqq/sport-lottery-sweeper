"""
检查页面结构的脚本
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def inspect_page():
    """检查目标页面的结构"""
    url = "https://www.sporttery.cn/jc/jsq/zqhhgg/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": "1"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            
            print("页面标题:", soup.title.string if soup.title else "无标题")
            
            # 查找可能包含比赛信息的元素
            print("\n=== 查找表格元素 ===")
            tables = soup.find_all('table')
            print(f"找到 {len(tables)} 个表格")
            
            for i, table in enumerate(tables):
                print(f"\n表格 {i+1} 的内容:")
                rows = table.find_all('tr')
                for j, row in enumerate(rows[:5]):  # 只打印前5行
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"  行 {j+1}: {cell_texts}")
            
            print("\n=== 查找其他可能的元素 ===")
            # 查找包含特定类名的元素
            elements = soup.find_all(class_=lambda x: x and ('match' in x.lower() or 'game' in x.lower() or 'table' in x.lower()))
            for elem in elements[:10]:  # 只打印前10个
                print(f"元素: {elem.name}, 类名: {elem.get('class', [])}, 文本: {elem.get_text(strip=True)[:100]}...")
            
            print("\n=== 查找所有表格行 ===")
            all_rows = soup.find_all('tr')
            print(f"找到 {len(all_rows)} 个表格行")
            for i, row in enumerate(all_rows[:10]):  # 只打印前10行
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"行 {i+1}: {cell_texts}")


if __name__ == "__main__":
    asyncio.run(inspect_page())