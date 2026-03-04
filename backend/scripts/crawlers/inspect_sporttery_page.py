"""
检查竞彩网页面结构，寻找比赛数据
"""
import asyncio
from playwright.async_api import async_playwright
import re
import json


async def inspect_sporttery_page():
    """
    检查竞彩网页面结构
    """
    print("🔍 检查竞彩网页面结构...")
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=False,  # 设为False以更好地绕过检测
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-ipc-flooding-protection',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--no-zygote',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--lang=zh-CN',
                    '--enable-automation',
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors',
                    '--allow-running-insecure-content',
                    '--disable-webgl',
                    '--disable-popup-blocking'
                ]
            )
            
            # 创建上下文并设置真实环境
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
                extra_http_headers={
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                }
            )
            
            # 隐藏webdriver特征
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                // 模拟chrome属性
                Object.defineProperty(window, 'chrome', {
                    writable: true,
                    value: {
                        runtime: {}
                    }
                });
                // 移除自动化检测
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                });
                // 删除自动化标志
                delete navigator.__proto__.webdriver;
            """)
            
            page = await context.new_page()
            
            # 设置页面超时时间
            page.set_default_timeout(20000)  # 增加超时时间
            
            # 访问竞彩网足球赛程页面
            print("🌐 正在访问竞彩网页面...")
            await page.goto("https://www.sporttery.cn/jc/zqszsc/", wait_until="domcontentloaded")
            
            # 等待页面加载
            await page.wait_for_timeout(8000)  # 等待更长时间
            
            # 获取页面内容
            content = await page.content()
            
            print(f"📄 页面长度: {len(content)} 字符")
            
            # 查找可能包含比赛数据的关键词
            keywords = ['match', 'Match', 'MATCH', 'team', 'home', 'away', 'vs', 'VS', 'game', 'schedule', 'data', 'fixture', '竞猜', '对阵', '比赛', '主队', '客队']
            
            for keyword in keywords:
                occurrences = len(re.findall(keyword, content, re.IGNORECASE))
                if occurrences > 0:
                    print(f"🔍 找到关键词 '{keyword}': {occurrences} 次")
            
            # 查找可能的JSON数据
            json_patterns = [
                r'(\{[^{}]*(?:match|team|home|away|vs|game|schedule)[^{}]*\})',
                r'(\[[^\[\]]*(?:match|team|home|away|vs|game|schedule)[^\[\]]*\])',
                r'(\{[^{}]*(?:竞猜|对阵|比赛|主队|客队)[^{}]*\})',
                r'(\[[^\[\]]*(?:竞猜|对阵|比赛|主队|客队)[^\[\]]*\])'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    print(f"🔍 找到 {len(matches)} 个可能的JSON数据块")
                    for i, match in enumerate(matches[:3]):  # 只打印前3个
                        print(f"   JSON数据块 {i+1}: {match[:200]}...")
            
            # 查找script标签中的数据
            script_pattern = r'<script[^>]*>(.*?)</script>'
            script_matches = re.findall(script_pattern, content, re.DOTALL)
            
            for script in script_matches:
                if len(script.strip()) > 100:  # 只处理较长的脚本
                    for keyword in keywords:
                        if keyword.lower() in script.lower():
                            print(f"🔍 在script标签中找到关键词 '{keyword}'")
                            
                            # 查找可能的JSON对象
                            json_matches = re.findall(r'(\{[^{}]*\})', script)
                            if json_matches:
                                print(f"   在script中找到 {len(json_matches)} 个JSON对象")
                                for j, json_obj in enumerate(json_matches[:2]):
                                    print(f"     JSON对象 {j+1}: {json_obj[:200]}...")
                            
                            # 查找可能的数组
                            array_matches = re.findall(r'(\[[^\[\]]*\])', script)
                            if array_matches:
                                print(f"   在script中找到 {len(array_matches)} 个数组")
                                for k, arr in enumerate(array_matches[:2]):
                                    print(f"     数组 {k+1}: {arr[:200]}...")
            
            # 查找特定的class或id
            class_patterns = [
                r'class="([^"]*match[^"]*)"',
                r'id="([^"]*match[^"]*)"',
                r'class="([^"]*game[^"]*)"',
                r'id="([^"]*game[^"]*)"',
                r'class="([^"]*schedule[^"]*)"',
                r'id="([^"]*schedule[^"]*)"',
                r'class="([^"]*竞猜[^"]*)"',
                r'id="([^"]*竞猜[^"]*)"'
            ]
            
            for pattern in class_patterns:
                class_matches = re.findall(pattern, content)
                if class_matches:
                    print(f"🔍 找到 {len(class_matches)} 个匹配的class/id: {class_matches[:5]}")
            
            # 尝试通过JavaScript获取页面中的数据
            try:
                print("\n🔍 尝试通过JavaScript获取页面数据...")
                
                # 获取页面上的所有属性
                js_data = await page.evaluate('''() => {
                    const result = {};
                    
                    // 获取页面上的所有数据属性
                    const dataElements = document.querySelectorAll('[data-match], [data-game], [data-id]');
                    result.dataElementsCount = dataElements.length;
                    
                    // 获取所有表格行
                    const tableRows = document.querySelectorAll('tr');
                    result.tableRowsCount = tableRows.length;
                    
                    // 获取所有表格单元格
                    const tableCells = document.querySelectorAll('td');
                    result.tableCellsCount = tableCells.length;
                    
                    // 尝试查找包含比赛信息的元素
                    const matchElements = Array.from(document.querySelectorAll('*'))
                        .filter(el => el.textContent && (
                            el.textContent.toLowerCase().includes('vs') ||
                            el.textContent.toLowerCase().includes('主场') ||
                            el.textContent.toLowerCase().includes('客场') ||
                            el.textContent.includes('主队') ||
                            el.textContent.includes('客队') ||
                            el.textContent.includes('胜平负')
                        ));
                    
                    result.matchElementsCount = matchElements.length;
                    
                    // 如果找到了比赛元素，提取一些信息
                    if (matchElements.length > 0) {
                        result.sampleMatchElements = matchElements.slice(0, 5).map(el => ({
                            tagName: el.tagName,
                            className: el.className,
                            id: el.id,
                            text: el.textContent.substring(0, 100)
                        }));
                    }
                    
                    // 查找所有表格
                    const tables = document.querySelectorAll('table');
                    result.tablesCount = tables.length;
                    
                    // 查找可能的竞彩网数据容器
                    const containers = document.querySelectorAll('.tz_table_wrap, .match-list, .game-container, .schedule-table');
                    result.containersCount = containers.length;
                    
                    return result;
                }''')
                
                print(f"📊 JavaScript数据统计:")
                for key, value in js_data.items():
                    print(f"   {key}: {value}")
                
            except Exception as e:
                print(f"❌ JavaScript执行失败: {str(e)}")
            
            # 关闭浏览器
            await page.close()
            await context.close()
            await browser.close()
            
    except Exception as e:
        print(f"❌ 检查页面时出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(inspect_sporttery_page())