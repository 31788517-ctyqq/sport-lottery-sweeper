"""详细测试竞彩网爬虫"""
import asyncio
import sys
import io
import json
from pathlib import Path
from datetime import datetime

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.scrapers.sources.sporttery import SportteryScraper
from backend.scrapers.core.engine import ScraperEngine
import aiohttp


async def test_urls():
    """测试不同的竞彩网URL"""
    print("="*80)
    print("测试竞彩网URL可访问性")
    print("="*80)
    
    # 可能的竞彩网URL
    urls = [
        "https://www.lottery.gov.cn",
        "https://www.lottery.gov.cn/football/jczq",
        "https://www.lottery.gov.cn/kj/kjlb.html",
        "http://www.lottery.gov.cn",
        "https://www.zhcw.com/",  # 中国体彩网
        "https://www.sporttery.cn/",  # 竞彩官网
        "https://i.sporttery.cn/api/fb_match_info/get_pool_rs/",  # 可能的API
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                print(f"\n测试: {url}")
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(url, timeout=timeout, allow_redirects=True) as resp:
                    print(f"  状态码: {resp.status}")
                    print(f"  实际URL: {resp.url}")
                    print(f"  内容类型: {resp.headers.get('Content-Type', 'unknown')}")
                    content_length = resp.headers.get('Content-Length', 'unknown')
                    print(f"  内容长度: {content_length}")
                    
                    if resp.status == 200:
                        print(f"  ✅ 成功访问！")
                        
                        # 保存HTML用于分析
                        if 'html' in resp.headers.get('Content-Type', ''):
                            text = await resp.text()
                            filename = url.replace('https://', '').replace('http://', '').replace('/', '_') + '.html'
                            output_file = Path('debug') / filename
                            output_file.parent.mkdir(exist_ok=True)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(text)
                            print(f"  💾 HTML已保存: {output_file}")
                    else:
                        print(f"  ⚠️  状态码异常")
                        
            except aiohttp.ClientResponseError as e:
                print(f"  ❌ 响应错误: {e.status} - {e.message}")
            except aiohttp.ClientConnectorError as e:
                print(f"  ❌ 连接错误: {e}")
            except asyncio.TimeoutError:
                print(f"  ❌ 超时")
            except Exception as e:
                print(f"  ❌ 其他错误: {e}")


async def test_sporttery_api():
    """测试竞彩网可能的API接口"""
    print("\n" + "="*80)
    print("测试竞彩网API接口")
    print("="*80)
    
    # 可能的API端点
    api_endpoints = [
        "https://i.sporttery.cn/api/fb_match_info/get_pool_rs/",
        "https://i.sporttery.cn/api/fb_match_info/get_pool/",
        "https://i.sporttery.cn/api/fb_match_info/fbmatch/",
        "https://www.lottery.gov.cn/api/football/jczq/match-list",
    ]
    
    async with aiohttp.ClientSession() as session:
        for api in api_endpoints:
            try:
                print(f"\n测试API: {api}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(api, headers=headers, timeout=timeout) as resp:
                    print(f"  状态码: {resp.status}")
                    
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            print(f"  ✅ JSON响应成功")
                            print(f"  数据键: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                            
                            # 保存JSON
                            filename = api.replace('https://', '').replace('http://', '').replace('/', '_') + '.json'
                            output_file = Path('debug') / filename
                            output_file.parent.mkdir(exist_ok=True)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            print(f"  💾 JSON已保存: {output_file}")
                            
                        except json.JSONDecodeError:
                            text = await resp.text()
                            print(f"  ⚠️  非JSON响应 (长度: {len(text)})")
                    else:
                        print(f"  ❌ 状态码: {resp.status}")
                        
            except Exception as e:
                print(f"  ❌ 错误: {type(e).__name__}: {e}")


async def test_with_scraper():
    """使用爬虫测试"""
    print("\n" + "="*80)
    print("使用重构爬虫测试")
    print("="*80)
    
    async with ScraperEngine() as engine:
        scraper = SportteryScraper(engine)
        
        print(f"\n数据源: {scraper.get_source_name()}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取比赛数据
        print("\n获取近3天比赛数据...")
        matches = await scraper.get_matches(days=3)
        
        print(f"\n✅ 获取到 {len(matches)} 场比赛")
        
        # 检查数据来源
        if matches:
            is_mock = matches[0].get('is_mock', False)
            if is_mock:
                print("⚠️  数据来源: 模拟数据")
                print("\n原因分析:")
                print("  1. API接口不存在或已变更")
                print("  2. HTML页面结构与预期不符")
                print("  3. 网站可能有反爬虫限制")
                print("  4. 需要特殊的认证或cookie")
            else:
                print("✅ 数据来源: 真实数据")
            
            # 显示统计
            print(f"\n比赛统计:")
            leagues = {}
            for match in matches:
                league = match['league']
                leagues[league] = leagues.get(league, 0) + 1
            
            print(f"  联赛数: {len(leagues)}")
            print(f"  比赛数: {len(matches)}")
            
            # 显示前3场
            print(f"\n前3场比赛:")
            for i, match in enumerate(matches[:3], 1):
                print(f"  {i}. {match['home_team']} vs {match['away_team']}")
                print(f"     {match['league']} | {match['match_time']}")
                print(f"     赔率: {match['odds_home_win']:.2f}/{match['odds_draw']:.2f}/{match['odds_away_win']:.2f}")
            
            # 保存数据
            output_file = Path('debug') / 'crawled_matches.json'
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)
            print(f"\n💾 完整数据已保存: {output_file}")
        
        # 引擎统计
        stats = engine.get_stats()
        print(f"\n引擎统计:")
        print(f"  总请求: {stats['total_requests']}")
        print(f"  成功: {stats['successful_requests']}")
        print(f"  失败: {stats['failed_requests']}")
        print(f"  成功率: {stats.get('success_rate', 0):.1f}%")


async def main():
    """主函数"""
    print("\n" + "🚀"*40)
    print("竞彩网爬虫详细测试")
    print("🚀"*40 + "\n")
    
    try:
        # 测试URL可访问性
        await test_urls()
        
        # 测试API接口
        await test_sporttery_api()
        
        # 使用爬虫测试
        await test_with_scraper()
        
        print("\n" + "="*80)
        print("✅ 测试完成")
        print("="*80)
        
        print("\n📝 总结:")
        print("  1. 查看 debug/ 目录下保存的HTML和JSON文件")
        print("  2. 分析哪些URL可以访问")
        print("  3. 找到包含比赛数据的真实API")
        print("  4. 更新 backend/scrapers/sources/sporttery.py 中的URL")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
