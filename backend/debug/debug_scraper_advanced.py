#!/usr/bin/env python3
"""
高级诊断工具 - 使用浏览器持久化 Cookies 和真实用户行为
目的：获取竞彩足球网站的真实API端点
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedScratchDiagnostics:
    """高级诊断工具 - 使用真实浏览器行为和持久化存储"""
    
    def __init__(self):
        self.user_data_dir = Path("./browser_cache")
        self.user_data_dir.mkdir(exist_ok=True)
        self.api_calls = []
        self.console_logs = []
        self.network_responses = {}
        
    async def diagnose_with_real_browser(self):
        """使用真实浏览器进行诊断"""
        print("\n" + "="*70)
        print("高级诊断工具 - 使用真实浏览器行为")
        print("="*70 + "\n")
        
        async with async_playwright() as p:
            # 使用持久化用户数据目录
            context = await p.chromium.launch_persistent_context(
                str(self.user_data_dir),
                headless=False,  # 非headless模式
                viewport={'width': 1920, 'height': 1080},
                # 真实的User-Agent
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                # 禁用web驱动标志
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-background-networking',
                    '--disable-sync',
                ]
            )
            
            # 添加初始化脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                window.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en-US', 'en'],
                });
            """)
            
            try:
                page = await context.new_page()
                
                # 设置请求拦截和日志
                await self._setup_listeners(page)
                
                print("[1/7] 设置浏览器监听器...")
                print("✓ 监听器已设置")
                
                print("\n[2/7] 访问竞彩足球页面...")
                response = await page.goto('https://www.sporttery.cn/jczq/', 
                                         wait_until='networkidle',
                                         timeout=30000)
                
                if response:
                    print(f"✓ 页面加载成功 (状态码: {response.status})")
                else:
                    print("⚠ 页面加载完成但无响应对象")
                
                print("\n[3/7] 页面信息:")
                title = await page.title()
                url = page.url
                print(f"  标题: {title}")
                print(f"  URL: {url}")
                
                # 等待页面完全加载
                await asyncio.sleep(3)
                
                print("\n[4/7] 执行JavaScript检查...")
                
                # 检查全局变量
                globals_check = await page.evaluate("""
                    () => {
                        const checks = {
                            __INITIAL_STATE__: typeof window.__INITIAL_STATE__,
                            __APP_DATA__: typeof window.__APP_DATA__,
                            __INITIAL_DATA__: typeof window.__INITIAL_DATA__,
                            __STATE__: typeof window.__STATE__,
                            INITIAL_DATA: typeof window.INITIAL_DATA,
                            store: typeof window.store,
                            redux: typeof window.redux,
                            matchData: typeof window.matchData,
                            matches: typeof window.matches,
                            games: typeof window.games,
                            competitions: typeof window.competitions,
                        };
                        return Object.entries(checks)
                            .filter(([k, v]) => v !== 'undefined')
                            .map(([k, v]) => `${k}: ${v}`);
                    }
                """)
                
                if globals_check:
                    print(f"  找到的全局变量: {globals_check}")
                else:
                    print("  未找到预期的全局变量")
                
                # 检查document中的scripts
                scripts_info = await page.evaluate("""
                    () => {
                        const scripts = document.querySelectorAll('script');
                        return {
                            total: scripts.length,
                            withSrc: Array.from(scripts).filter(s => s.src).length,
                            withContent: Array.from(scripts).filter(s => s.textContent).length,
                            srcs: Array.from(scripts)
                                .filter(s => s.src && (s.src.includes('api') || s.src.includes('data')))
                                .map(s => s.src)
                        };
                    }
                """)
                
                print(f"\n[5/7] 脚本标签分析:")
                print(f"  总数: {scripts_info['total']}")
                print(f"  有src属性: {scripts_info['withSrc']}")
                print(f"  有内容: {scripts_info['withContent']}")
                if scripts_info['srcs']:
                    print(f"  API相关脚本: {scripts_info['srcs']}")
                
                # 检查DOM结构
                dom_info = await page.evaluate("""
                    () => {
                        return {
                            bodyClasses: document.body.className,
                            mainDivs: document.querySelectorAll('[class*="main"], [id*="main"]').length,
                            contentDivs: document.querySelectorAll('[class*="content"], [id*="content"]').length,
                            tables: document.querySelectorAll('table').length,
                            iframes: document.querySelectorAll('iframe').length,
                            apiInHtml: document.documentElement.innerHTML.includes('api') ? 'Yes' : 'No',
                            matchesInHtml: document.documentElement.innerHTML.includes('matches') ? 'Yes' : 'No',
                        };
                    }
                """)
                
                print(f"\n[6/7] DOM结构分析:")
                print(f"  Body Classes: {dom_info['bodyClasses'][:50]}...")
                print(f"  Main元素: {dom_info['mainDivs']}")
                print(f"  Content元素: {dom_info['contentDivs']}")
                print(f"  表格元素: {dom_info['tables']}")
                print(f"  iFrame元素: {dom_info['iframes']}")
                print(f"  HTML中有'api'关键词: {dom_info['apiInHtml']}")
                print(f"  HTML中有'matches'关键词: {dom_info['matchesInHtml']}")
                
                # 执行用户行为 - 点击按钮等
                print(f"\n[7/7] 模拟用户行为...")
                
                # 尝试滚动
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(1)
                
                # 查找并点击可能的按钮
                buttons = await page.query_selector_all('button')
                print(f"  找到{len(buttons)}个按钮")
                
                for i, btn in enumerate(buttons[:3]):  # 只点击前3个
                    try:
                        text = await btn.text_content()
                        if text and len(text.strip()) > 0:
                            print(f"    点击按钮: {text.strip()[:30]}")
                            await btn.click()
                            await asyncio.sleep(1)
                    except:
                        pass
                
                # 最后再等待一次
                await asyncio.sleep(2)
                
                print("\n" + "="*70)
                print("📊 诊断总结")
                print("="*70)
                
                print(f"\n🔍 捕获的API调用: {len(self.api_calls)}")
                if self.api_calls:
                    print("\n成功的请求:")
                    for call in self.api_calls:
                        if call.get('status') in [200, 201]:
                            print(f"  ✓ {call['url'][:80]}")
                            print(f"    状态: {call['status']}")
                else:
                    print("  未捕获到API请求")
                
                print(f"\n📝 控制台日志: {len(self.console_logs)}")
                if self.console_logs:
                    for log in self.console_logs[:5]:
                        print(f"  {log['type']}: {log['message'][:60]}")
                
                print("\n" + "="*70)
                print("⏳ 浏览器窗口保持打开 - 请手动检查:")
                print("="*70)
                print("\n1. 按 F12 打开开发者工具")
                print("2. 切换到 Network 标签")
                print("3. 查找包含以下关键词的请求:")
                print("   - 'api'")
                print("   - 'match', 'jczq', 'schedule'")
                print("   - '.json'")
                print("4. 查看响应数据 (Response标签)")
                print("5. 记下成功返回数据的API端点")
                print("\n按 Enter 关闭浏览器...")
                
                # 等待用户输入
                await asyncio.get_event_loop().run_in_executor(None, input)
                
            finally:
                await context.close()
    
    async def _setup_listeners(self, page: Page):
        """设置页面监听器"""
        
        # 监听响应
        async def handle_response(response):
            try:
                url = response.url
                status = response.status
                
                # 只记录API相关的请求
                if any(keyword in url for keyword in ['api', 'data', 'match', 'schedule', 'fixture']):
                    self.api_calls.append({
                        'url': url,
                        'status': status,
                        'timestamp': datetime.now().isoformat(),
                        'method': response.request.method,
                    })
                    
                    logger.info(f"[响应] {status} - {url[:80]}")
            except Exception as e:
                logger.debug(f"响应处理错误: {e}")
        
        # 监听请求
        async def handle_request(request):
            try:
                url = request.url
                if any(keyword in url for keyword in ['api', 'data', 'match', 'schedule', 'fixture']):
                    logger.debug(f"[请求] {request.method} - {url[:80]}")
            except Exception as e:
                logger.debug(f"请求处理错误: {e}")
        
        # 监听控制台消息
        async def handle_console(msg):
            try:
                self.console_logs.append({
                    'type': msg.type,
                    'message': msg.text,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.debug(f"控制台处理错误: {e}")
        
        page.on('response', handle_response)
        page.on('request', handle_request)
        page.on('console', handle_console)

async def main():
    """主程序"""
    try:
        diag = AdvancedScratchDiagnostics()
        await diag.diagnose_with_real_browser()
        
        print("\n✅ 诊断完成！")
        print("\n接下来的步骤:")
        print("1. 查看上面记录的API调用")
        print("2. 如果找到了API端点，在 sporttery_enhanced.py 中更新")
        print("3. 重新运行爬虫进行测试")
        
    except Exception as e:
        logger.error(f"诊断过程出错: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
