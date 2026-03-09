"""
调试竞彩网页面内容
"""
import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def debug_sporttery_page():
    print("开始调试竞彩网页面内容...")
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 设置请求头，模拟真实浏览器
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            })
            
            # 访问竞彩网足球赛程页面
            print("正在访问竞彩网页面...")
            await page.goto("https://www.sporttery.cn/jc/zqszsc/", wait_until="networkidle", timeout=30000)
            
            # 等待页面加载完成
            await page.wait_for_timeout(5000)
            
            # 获取页面内容
            content = await page.content()
            
            print("页面加载完成，正在分析内容...")
            
            # 使用BeautifulSoup解析页面
            soup = BeautifulSoup(content, 'html.parser')
            
            # 尝试查找比赛相关元素
            print("\n--- 查找比赛相关元素 ---")
            
            # 查找可能包含比赛信息的元素
            match_selectors = [
                'table',  # 表格元素
                '[class*="match"]',  # 包含match的类
                '[class*="game"]',   # 包含game的类
                '[class*="event"]',  # 包含event的类
                '[data-match]',      # 包含data-match属性的元素
                '.jclq_table_wrap',  # 竞彩篮球表格包装器类（可能类似足球也有）
                '.jc_zq_table',      # 竞彩足球表格类
                '.match-list',       # 比赛列表
                '.schedule-table',   # 赛程表格
                '.match-item'        # 比赛项目
            ]
            
            for selector in match_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"找到 {len(elements)} 个 '{selector}' 元素")
                    # 输出第一个元素的HTML内容（限制长度）
                    first_el = str(elements[0])[:500]
                    print(f"  第一个元素内容: {first_el}...")
                    break
            else:
                print("未找到比赛相关元素，正在尝试通用搜索...")
                
                # 尝试查找包含比赛关键词的元素
                keywords = ['vs', 'VS', '对阵', '比赛', '足球', '胜平负']
                for keyword in keywords:
                    elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
                    if elements:
                        print(f"找到 {len(elements)} 个包含 '{keyword}' 的文本元素")
                        for i, el in enumerate(elements[:5]):  # 只显示前5个
                            parent = el.parent
                            print(f"  {i+1}. '{el.strip()}' (父元素: {parent.name})")
                        break
            
            # 检查页面标题
            title = soup.find('title')
            if title:
                print(f"\n页面标题: {title.get_text().strip()}")
            
            # 检查是否有错误或反爬虫提示
            error_indicators = ['访问过于频繁', '您的访问出现异常', '安全验证', '验证码', 'blocked', 'denied']
            content_lower = content.lower()
            for indicator in error_indicators:
                if indicator.lower() in content_lower:
                    print(f"\n⚠️  检测到可能的反爬虫提示: {indicator}")
            
            # 保存页面内容到文件以便进一步分析
            with open('debug_sporttery_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n页面内容已保存到 debug_sporttery_page.html")
            
            await browser.close()
            
    except Exception as e:
        print(f"调试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_sporttery_page())