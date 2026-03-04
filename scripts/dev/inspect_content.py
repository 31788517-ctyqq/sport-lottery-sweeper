"""
检查获取到的页面内容结构
"""
import asyncio
import sys
import os
import logging
from bs4 import BeautifulSoup

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.scrapers.zqszsc_scraper import zqszsc_scraper

# 设置日志级别为DEBUG以查看更多信息
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def inspect_content():
    """检查页面内容结构"""
    print("开始检查页面内容结构...")
    
    try:
        async with zqszsc_scraper as scraper:
            print(f"目标URL: {scraper.target_url}")
            print("正在获取页面内容...")
            
            # 我们需要修改爬虫，让它返回原始HTML内容而不是解析后的数据
            # 为此，我们将直接使用Playwright来获取页面内容
            from playwright.async_api import async_playwright
            import random
            
            async with async_playwright() as p:
                # 设置浏览器参数
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-setuid-sandbox',
                        '--disable-gpu',
                        '--window-size=1920,1080',
                        '--lang=zh-CN,zh;q=0.9,en;q=0.8',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--disable-ipc-flooding-protection',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-features=MediaRouterDialRegistration',
                        '--disable-features=TranslateUI',
                        '--disable-features=OutOfBlinkCors',
                        '--disable-component-extensions-with-background-pages',
                        '--disable-default-apps',
                        '--disable-features=NetworkService',
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-dev-shm-usage',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )
                
                # 创建浏览器上下文
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
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
                    },
                    bypass_csp=True,
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai'
                )
                
                # 添加 navigator.webdriver 属性处理
                page = await context.new_page()
                
                # 注入 JavaScript 代码以绕过检测
                await page.add_init_script("""
                    // 隐藏 webdriver 特征
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // 修改插件数组
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            { name: 'Chrome PDF Plugin' },
                            { name: 'Chrome PDF Viewer' },
                            { name: 'Native Client' }
                        ],
                    });
                    
                    // 修改语言
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en'],
                    });
                    
                    // 修改平台
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32',
                    });
                    
                    // 修改 userAgent
                    Object.defineProperty(navigator, 'userAgent', {
                        get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    });
                    
                    // 删除一些自动化检测属性
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    
                    // 隐藏 chrome 属性
                    Object.defineProperty(window, 'chrome', {
                        value: {
                            runtime: {}
                        },
                        writable: false
                    });
                    
                    // 隐藏 permissions API
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => {
                        return parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters);
                    };
                    
                    // 模拟真实行为
                    window.outerHeight = 907;
                    window.outerWidth = 1440;
                    window.innerHeight = 877;
                    window.innerWidth = 1440;
                """)
                
                # 访问目标页面
                await page.goto(scraper.target_url, wait_until='domcontentloaded', timeout=30000)
                
                # 等待页面加载
                await page.wait_for_timeout(5000)
                
                # 模拟滚动以触发懒加载
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await page.wait_for_timeout(3000)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
                
                # 获取整个页面内容
                content = await page.content()
                
                # 保存内容到文件，方便分析
                with open('page_content.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("页面内容已保存到 page_content.html")
                
                # 解析HTML并查找tbody元素
                soup = BeautifulSoup(content, 'html.parser')
                tbody_elements = soup.find_all('tbody')
                
                print(f"找到 {len(tbody_elements)} 个tbody元素")
                
                for i, tbody in enumerate(tbody_elements[:5]):  # 只查看前5个
                    print(f"\n--- tbody {i+1} ---")
                    rows = tbody.find_all('tr')
                    for j, row in enumerate(rows[:3]):  # 只查看前3行
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"  行 {j+1}: {cell_texts}")
                
                await page.close()
                await browser.close()
                
    except Exception as e:
        print(f"检查内容失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(inspect_content())