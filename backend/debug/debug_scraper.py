#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫调试诊断工具 - 帮助诊断为什么无法获取真实数据
"""

import asyncio
import logging
import json
from datetime import datetime
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def diagnose_website():
    """诊断竞彩网站的结构和数据"""
    print("\n" + "="*70)
    print("竞彩网诊断工具 - 分析网站结构和数据获取")
    print("="*70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器窗口便于调试
        page = await browser.new_page()
        
        try:
            print("\n[1/5] 访问竞彩足球页面...")
            await page.goto("https://www.sporttery.cn/jczq/", wait_until="networkidle", timeout=30000)
            print("✓ 页面加载成功")
            
            # 获取页面标题
            title = await page.title()
            print(f"\n[2/5] 页面信息:")
            print(f"  标题: {title}")
            
            # 获取所有script标签
            print(f"\n[3/5] 分析页面数据...")
            scripts = await page.query_selector_all('script')
            print(f"  找到 {len(scripts)} 个script标签")
            
            # 分析script标签内容
            data_found = False
            for i, script in enumerate(scripts):
                try:
                    content = await script.text_content()
                    if content and len(content) > 100:
                        # 检查是否包含关键词
                        if any(keyword in content for keyword in ['match', 'fixture', 'schedule', 'team', 'jczq']):
                            print(f"\n  [脚本{i}] 包含可能的比赛数据 (长度: {len(content)})")
                            if 'match' in content.lower():
                                data_found = True
                                # 显示前500字符
                                preview = content[:500]
                                print(f"    预览: {preview}...")
                except:
                    pass
            
            # 检查全局变量
            print(f"\n[4/5] 检查JavaScript全局变量...")
            globals_info = await page.evaluate("""
                () => {
                    const info = {
                        hasInitialState: !!window.__INITIAL_STATE__,
                        hasData: !!window.__DATA__,
                        hasSsrData: !!window.__SSR_DATA__,
                        hasMatchList: !!window.matchList,
                        hasMatches: !!window.matches,
                    };
                    
                    // 检查所有包含'match'的全局变量
                    const matchVars = [];
                    for (const key in window) {
                        if (key.toLowerCase().includes('match')) {
                            matchVars.push(key);
                        }
                    }
                    
                    info.matchVariables = matchVars;
                    return info;
                }
            """)
            
            for key, value in globals_info.items():
                print(f"  {key}: {value}")
            
            # 获取DOM结构分析
            print(f"\n[5/5] 分析DOM结构...")
            dom_info = await page.evaluate("""
                () => {
                    const info = {
                        tables: document.querySelectorAll('table').length,
                        divs: document.querySelectorAll('[class*="match"]').length,
                        matchDivs: document.querySelectorAll('[class*="jczq"]').length,
                        dataAttributes: Array.from(document.querySelectorAll('[data-match*], [data-fixture*]')).length,
                    };
                    
                    // 查找包含'vs'或'对阵'的文本节点
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null
                    );
                    
                    let matchCount = 0;
                    let node;
                    while (node = walker.nextNode()) {
                        if (node.textContent.includes('vs') || node.textContent.includes('对阵')) {
                            matchCount++;
                        }
                    }
                    
                    info.vsMatches = matchCount;
                    return info;
                }
            """)
            
            for key, value in dom_info.items():
                print(f"  {key}: {value}")
            
            # 拦截网络请求找到API
            print(f"\n[检查] 监听网络请求30秒...")
            
            api_requests = []
            
            def handle_response(response):
                url = response.url
                if any(kw in url for kw in ['api', 'match', 'fixture', 'schedule']):
                    api_requests.append({
                        'url': url,
                        'status': response.status,
                    })
                    print(f"  找到API: {url}")
            
            page.on('response', handle_response)
            
            # 等待并触发数据加载
            await page.wait_for_timeout(5000)
            
            if api_requests:
                print(f"\n✓ 发现 {len(api_requests)} 个API请求")
                for req in api_requests[:5]:
                    print(f"  - {req['url']}")
            else:
                print(f"\n⚠️  未发现API请求，可能使用了其他数据加载方式")
            
            # 生成诊断报告
            print("\n" + "="*70)
            print("诊断总结")
            print("="*70)
            print(f"""
✓ 网站可以访问
{'✓' if data_found else '⚠'} 页面包含比赛数据
{'✓' if api_requests else '⚠'} 发现API请求
{'✓' if globals_info['matchVariables'] else '⚠'} 页面定义了全局变量

建议措施:
1. 网络拦截策略 - 捕获API请求 {'✓' if api_requests else '⚠'}
2. 全局变量提取 - 从window对象获取数据 {'✓' if globals_info['matchVariables'] else '⚠'}
3. DOM解析策略 - 从HTML结构提取数据 {'✓' if dom_info['matchDivs'] > 0 else '⚠'}
4. 模拟数据备选 - 作为最后的回退方案 ✓
""")
            
        except Exception as e:
            print(f"\n❌ 诊断过程出错: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


async def test_api_endpoints():
    """测试可能的API端点"""
    print("\n" + "="*70)
    print("API端点检测")
    print("="*70)
    
    endpoints = [
        "https://www.sporttery.cn/api/jczq/matches",
        "https://www.sporttery.cn/api/matches",
        "https://www.sporttery.cn/api/schedule",
        "https://www.sporttery.cn/jczq/api",
        "https://api.sporttery.cn/jczq",
        "https://api.sporttery.cn/matches",
    ]
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.text()
                        print(f"✓ {endpoint}")
                        print(f"  状态码: {resp.status}")
                        print(f"  响应大小: {len(data)} 字节")
                    else:
                        print(f"✗ {endpoint} (状态码: {resp.status})")
            except Exception as e:
                print(f"✗ {endpoint} ({str(e)[:50]})")


async def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  爬虫诊断工具".center(68) + "║")
    print("║" + "  帮助找出无法获取真实数据的原因".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # 运行诊断
    await diagnose_website()
    
    # 测试API
    await test_api_endpoints()
    
    print("\n" + "="*70)
    print("诊断完成")
    print("="*70)
    print("""
根据诊断结果，你可以:
1. 查看浏览器窗口中哪些网络请求包含比赛数据
2. 更新爬虫代码中的API端点和选择器
3. 添加新的数据提取策略
4. 增强反爬虫对策（更好的User-Agent、延时、重试等）

注意: 如果网站加强了反爬虫，可能需要:
- 使用residential proxies
- 模拟真实用户行为
- 降低请求频率
- 考虑使用官方API或数据源
""")


if __name__ == "__main__":
    asyncio.run(main())
