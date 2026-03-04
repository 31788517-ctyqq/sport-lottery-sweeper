#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强型诊断工具 - 使用更强的反检测策略
"""

import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def diagnose_with_stronger_antidetection():
    """使用更强的反检测策略进行诊断"""
    print("\n" + "="*70)
    print("增强型诊断工具 - 使用更强的反检测策略")
    print("="*70)
    
    async with async_playwright() as p:
        # 使用非headless模式便于观察
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        
        page = await browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }
        )
        
        try:
            # 注入更强的反检测脚本
            print("\n[1/6] 注入反检测脚本...")
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'chrome', {
                    get: () => ({runtime: {}}),
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                window.chrome = {
                    runtime: {}
                };
                
                // 禁用 headless 标志检测
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            print("✓ 反检测脚本已注入")
            
            # 访问页面
            print("\n[2/6] 访问竞彩足球页面...")
            try:
                await page.goto("https://www.sporttery.cn/jczq/", wait_until="domcontentloaded", timeout=30000)
                print("✓ 页面加载成功")
            except Exception as e:
                print(f"⚠️ 页面加载异常: {e}")
            
            # 随机延时模拟真实用户
            await page.wait_for_timeout(3000)
            
            # 获取页面标题和URL
            print("\n[3/6] 页面信息:")
            title = await page.title()
            url = page.url
            print(f"  标题: {title}")
            print(f"  当前URL: {url}")
            
            # 检查页面内容
            content = await page.content()
            print(f"  页面大小: {len(content)} 字节")
            
            # 分析script标签
            print("\n[4/6] 分析script标签...")
            scripts_info = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.scripts);
                    const info = {
                        total: scripts.length,
                        withSrc: scripts.filter(s => s.src).length,
                        withContent: scripts.filter(s => s.textContent && s.textContent.length > 0).length,
                        largeScripts: []
                    };
                    
                    // 查找包含match/fixture的脚本
                    for (let i = 0; i < scripts.length; i++) {
                        const content = scripts[i].textContent || '';
                        if (content.includes('match') || content.includes('fixture') || 
                            content.includes('schedule') || content.includes('jczq')) {
                            info.largeScripts.push({
                                index: i,
                                size: content.length,
                                hasMatch: content.includes('match'),
                                hasFixture: content.includes('fixture'),
                                hasSchedule: content.includes('schedule'),
                                hasJczq: content.includes('jczq'),
                            });
                        }
                    }
                    
                    return info;
                }
            """)
            
            print(f"  总script数: {scripts_info['total']}")
            print(f"  有src属性: {scripts_info['withSrc']}")
            print(f"  有内容: {scripts_info['withContent']}")
            print(f"  包含关键词的脚本: {len(scripts_info['largeScripts'])}")
            
            for script in scripts_info['largeScripts'][:3]:
                print(f"    - 脚本{script['index']}: {script['size']}字节 "
                      f"(match:{script['hasMatch']}, fixture:{script['hasFixture']}, "
                      f"schedule:{script['hasSchedule']}, jczq:{script['hasJczq']})")
            
            # 检查全局变量
            print("\n[5/6] 检查全局变量和数据对象...")
            globals_check = await page.evaluate("""
                () => {
                    const found = {
                        variables: [],
                        dataObjects: {},
                        allKeys: []
                    };
                    
                    // 检查常见的全局变量 - 使用安全的方式访问
                    const varNames = [
                        '__INITIAL_STATE__', '__DATA__', '__SSR_DATA__', '__STORE__',
                        'matchList', 'matchData', 'matches', '__JCZQ__', 
                        'window.__pageData__', 'window.__data__',
                        '__NEXT_DATA__', '__NUXT__'
                    ];
                    
                    // 安全访问全局变量的辅助函数
                    function safeAccess(path) {
                        try {
                            return path.split('.').reduce((obj, prop) => obj && obj[prop], window);
                        } catch (e) {
                            return undefined;
                        }
                    }

                    for (const varName of varNames) {
                        let value;
                        
                        // 根据变量名构建访问路径
                        if (varName.startsWith('window.')) {
                            value = safeAccess(varName.substring(7)); // 移除'window.'前缀
                        } else {
                            value = window[varName];
                        }
                        
                        if (value !== undefined && value !== null) {
                            found.variables.push(varName);
                            if (typeof value === 'object') {
                                found.dataObjects[varName] = {
                                    type: Array.isArray(value) ? 'array' : 'object',
                                    keys: Array.isArray(value) ? value.length : Object.keys(value).length,
                                    hasMatch: JSON.stringify(value).includes('match')
                                };
                            }
                        }
                    }
                    
                    // 获取所有包含'data'、'match'的全局变量
                    for (const key in window) {
                        if ((key.toLowerCase().includes('data') || 
                             key.toLowerCase().includes('match') ||
                             key.toLowerCase().includes('fixture')) && 
                            typeof window[key] === 'object') {
                            found.allKeys.push(key);
                        }
                    }
                    
                    return found;
                }
            """)
            
            if globals_check['variables']:
                print(f"✓ 找到全局变量: {', '.join(globals_check['variables'])}")
                for varName, info in globals_check['dataObjects'].items():
                    print(f"    {varName}: {info['type']} ({info['keys']} 项) "
                          f"包含match数据: {info['hasMatch']}")
            else:
                print("✗ 未找到预期的全局变量")
            
            if globals_check['allKeys']:
                print(f"\n  其他包含'data'或'match'的变量:")
                for key in globals_check['allKeys'][:10]:
                    print(f"    - {key}")
            
            # 监听网络请求
            print("\n[6/6] 监听网络请求(15秒)...")
            
            api_requests = []
            
            def handle_response(response):
                url = response.url
                status = response.status
                if any(kw in url for kw in ['api', 'match', 'fixture', 'schedule', 'jczq', 'data']):
                    content_type = response.headers.get('content-type', '')
                    api_requests.append({
                        'url': url,
                        'status': status,
                        'type': content_type,
                    })
                    if status == 200:
                        print(f"  ✓ {url[:60]}... [{status}]")
                    else:
                        print(f"  ✗ {url[:60]}... [{status}]")
            
            page.on('response', handle_response)
            
            # 触发页面交互以加载数据
            print("  等待数据加载...")
            await page.wait_for_timeout(5000)
            
            # 尝试滚动页面
            try:
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
            except:
                pass
            
            # 尝试点击可能的加载按钮
            try:
                buttons = await page.query_selector_all('button, [role="button"]')
                if buttons:
                    print(f"  发现 {len(buttons)} 个按钮，尝试点击...")
                    for btn in buttons[:3]:
                        try:
                            await btn.click()
                            await page.wait_for_timeout(1000)
                        except:
                            pass
            except:
                pass
            
            # 输出诊断结果
            print("\n" + "="*70)
            print("📊 诊断总结")
            print("="*70)
            
            if api_requests:
                print(f"\n✓ 发现 {len(api_requests)} 个API请求:")
                for req in api_requests[:10]:
                    print(f"  {req['status']:3d} {req['url'][:65]}")
            else:
                print("\n⚠️ 未发现API请求")
            
            if globals_check['variables']:
                print(f"\n✓ 找到全局数据源: {', '.join(globals_check['variables'])}")
            else:
                print("\n⚠️ 未找到全局数据变量")
            
            # 建议
            print("\n" + "="*70)
            print("🎯 改进建议")
            print("="*70)
            print("""
1. 手动检查页面加载:
   - 观察浏览器窗口（已自动打开）
   - 检查页面是否正常加载
   - 查看是否有加载动画或错误提示

2. 检查DevTools Network标签:
   - 查找包含 'match', 'fixture', 'schedule' 的请求
   - 记下真实的API端点
   - 查看请求和响应头

3. 可能的原因和解决方案:
   ✓ 网站强制HTTPS - 已配置
   ✓ 网站检查User-Agent - 已配置真实UA
   ✓ 网站检查Referer - 自动处理
   ✓ 网站使用JavaScript动态加载 - 已等待加载
   ✓ 网站使用验证码 - 可能需要手动操作

4. 如果仍无法获取:
   - 尝试使用代理IP
   - 降低请求频率
   - 考虑使用官方API或数据源
""")
            
            # 保持浏览器窗口开放一段时间以便观察
            print("\n⏳ 浏览器窗口将在30秒后关闭，这给你时间检查页面和DevTools...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            logger.error(f"诊断过程出错: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


async def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  增强型诊断工具".center(68) + "║")
    print("║" + "  查找竞彩网真实API端点".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    await diagnose_with_stronger_antidetection()
    
    print("\n✅ 诊断完成！")


if __name__ == "__main__":
    asyncio.run(main())
