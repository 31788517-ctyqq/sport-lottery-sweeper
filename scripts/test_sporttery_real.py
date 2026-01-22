#!/usr/bin/env python
"""
测试从竞彩官网真实爬取数据
"""
import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_real_crawl():
    """测试真实爬取竞彩官网数据"""
    print("\n" + "="*80)
    print("🎯 测试从竞彩官网爬取近三天比赛数据")
    print("="*80)
    
    from backend.scrapers.sources.sporttery import SportteryScraper
    from backend.scrapers.core.engine import ScraperEngine
    
    # 创建引擎和爬虫
    async with ScraperEngine() as engine:
        scraper = SportteryScraper(engine)
        
        print("\n🌐 数据源: 中国竞彩网 (www.lottery.gov.cn)")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 抓取范围: 近3天比赛数据\n")
        
        # 测试各个获取方式
        print("="*80)
        print("步骤1: 尝试通过API接口获取数据")
        print("="*80)
        
        try:
            # 先测试竞彩网首页是否可访问
            print("\n📡 测试竞彩网连接性...")
            response = await engine.fetch(
                scraper.JCZQ_URL,
                method='GET',
                timeout=10
            )
            
            if response['status'] == 200:
                print(f"✅ 竞彩网可访问 (状态码: {response['status']})")
                print(f"📄 页面大小: {len(response.get('text', ''))} 字符")
                
                # 保存HTML用于分析
                html_file = Path(__file__).parent.parent / "debug" / "sporttery_page.html"
                html_file.parent.mkdir(exist_ok=True)
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.get('text', ''))
                print(f"💾 HTML已保存到: {html_file}")
            else:
                print(f"⚠️  竞彩网返回状态码: {response['status']}")
                
        except Exception as e:
            print(f"❌ 连接失败: {e}")
        
        print("\n" + "="*80)
        print("步骤2: 获取比赛数据（使用多层回退策略）")
        print("="*80)
        
        try:
            matches = await scraper.get_matches(days=3)
            
            print(f"\n✅ 成功获取 {len(matches)} 场比赛数据")
            
            # 检查是否是模拟数据
            is_mock = matches[0].get('is_mock', False) if matches else False
            if is_mock:
                print("⚠️  当前使用的是模拟数据（真实数据源暂不可用）")
                print("\n💡 原因:")
                print("   1. 竞彩网可能需要特殊的认证或cookie")
                print("   2. API端点可能不存在或已变更")
                print("   3. 页面HTML结构可能与预期不符")
            else:
                print("✅ 获取到真实数据！")
            
            # 显示比赛详情
            print("\n" + "="*80)
            print("比赛数据详情")
            print("="*80)
            
            # 按联赛分组统计
            leagues = {}
            for match in matches:
                league = match.get('league', '未知')
                leagues[league] = leagues.get(league, 0) + 1
            
            print(f"\n📊 联赛分布 (共{len(leagues)}个联赛):")
            for league, count in sorted(leagues.items(), key=lambda x: -x[1]):
                print(f"   {league}: {count}场")
            
            # 显示前5场比赛
            print(f"\n⚽ 前5场比赛详情:")
            print("-"*80)
            for i, match in enumerate(matches[:5], 1):
                print(f"\n{i}. {match['home_team']} vs {match['away_team']}")
                print(f"   联赛: {match['league']}")
                print(f"   时间: {match['match_time']}")
                print(f"   赔率(胜/平/负): {match['odds_home_win']:.2f} / {match['odds_draw']:.2f} / {match['odds_away_win']:.2f}")
                print(f"   比分: {match.get('score', '-:-')}")
                print(f"   状态: {match.get('status', 'scheduled')}")
                if match.get('is_mock'):
                    print(f"   [模拟数据]")
            
            # 保存完整数据到JSON
            output_file = Path(__file__).parent.parent / "debug" / "crawled_matches.json"
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)
            print(f"\n💾 完整数据已保存到: {output_file}")
            
            # 测试获取单场比赛详情
            if matches:
                print("\n" + "="*80)
                print("步骤3: 测试获取比赛详情")
                print("="*80)
                
                match_id = matches[0]['match_id']
                print(f"\n📝 获取比赛ID: {match_id} 的详细信息...")
                
                detail = await scraper.get_match_detail(match_id)
                if detail:
                    print("✅ 成功获取比赛详情")
                    print(f"   数据字段: {list(detail.keys())}")
                else:
                    print("⚠️  获取详情失败")
                
                # 测试获取赔率历史
                print(f"\n📈 获取比赛ID: {match_id} 的赔率历史...")
                history = await scraper.get_odds_history(match_id)
                if history:
                    print(f"✅ 成功获取 {len(history)} 条赔率历史记录")
                    if len(history) > 0:
                        print(f"   最新赔率: {history[0]}")
                else:
                    print("⚠️  获取赔率历史失败")
            
        except Exception as e:
            logger.error(f"❌ 获取数据失败: {e}", exc_info=True)
        
        # 显示统计信息
        print("\n" + "="*80)
        print("爬虫引擎统计")
        print("="*80)
        
        stats = engine.get_stats()
        print(f"\n📊 性能指标:")
        print(f"   总请求数: {stats['total_requests']}")
        print(f"   成功请求: {stats['successful_requests']}")
        print(f"   失败请求: {stats['failed_requests']}")
        print(f"   成功率: {stats.get('success_rate', 0):.1f}%")
        print(f"   平均响应时间: {stats.get('avg_response_time', 0):.2f}秒")
        print(f"   缓存命中: {stats.get('cache_hits', 0)}")
        print(f"   缓存命中率: {stats.get('cache_hit_rate', 0):.1f}%")


async def analyze_html_structure():
    """分析竞彩网HTML结构"""
    print("\n" + "="*80)
    print("🔍 分析竞彩网页面结构")
    print("="*80)
    
    html_file = Path(__file__).parent.parent / "debug" / "sporttery_page.html"
    
    if not html_file.exists():
        print("⚠️  未找到保存的HTML文件，请先运行爬取测试")
        return
    
    from bs4 import BeautifulSoup
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\n📄 HTML文件大小: {len(html)} 字符")
    print(f"🏷️  页面标题: {soup.title.string if soup.title else '无标题'}")
    
    # 查找可能包含比赛数据的元素
    print("\n🔍 查找可能的比赛数据容器:")
    
    # 常见的比赛数据容器class名
    possible_classes = [
        'match', 'game', 'item', 'row', 'list', 
        'table', 'cell', 'content', 'data',
        'jczq', 'football', 'soccer'
    ]
    
    found_elements = {}
    for cls in possible_classes:
        elements = soup.find_all(class_=lambda x: x and cls in x.lower())
        if elements:
            found_elements[cls] = len(elements)
    
    if found_elements:
        print("\n找到的潜在元素:")
        for cls, count in sorted(found_elements.items(), key=lambda x: -x[1])[:10]:
            print(f"   包含'{cls}'的class: {count}个元素")
    else:
        print("   未找到常见的比赛数据容器")
    
    # 查找script标签中的JSON数据
    print("\n🔍 查找嵌入的JSON数据:")
    script_tags = soup.find_all('script')
    json_found = 0
    for i, script in enumerate(script_tags):
        if script.string and ('match' in script.string.lower() or 'data' in script.string.lower()):
            json_found += 1
            print(f"   Script #{i}: 可能包含数据 ({len(script.string)}字符)")
    
    if json_found == 0:
        print("   未找到包含比赛数据的script标签")
    
    print("\n💡 建议:")
    print("   1. 手动检查保存的HTML文件")
    print("   2. 在浏览器中查看页面的网络请求，找到真实的API端点")
    print("   3. 考虑使用浏览器自动化(playwright/selenium)绕过反爬虫")


async def main():
    """主函数"""
    print("\n" + "🚀"*40)
    print("竞彩网真实数据爬取测试")
    print("🚀"*40)
    
    try:
        # 运行爬取测试
        await test_real_crawl()
        
        # 分析HTML结构
        await analyze_html_structure()
        
        print("\n" + "="*80)
        print("✅ 测试完成")
        print("="*80)
        
        print("\n📚 下一步:")
        print("   1. 检查 debug/sporttery_page.html 了解页面结构")
        print("   2. 检查 debug/crawled_matches.json 查看爬取的数据")
        print("   3. 使用浏览器开发者工具找到真实的API端点")
        print("   4. 更新 backend/scrapers/sources/sporttery.py 中的解析逻辑")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
