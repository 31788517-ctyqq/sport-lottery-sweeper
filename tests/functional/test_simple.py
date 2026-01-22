import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    print("开始测试...")
    
    try:
        from backend.scrapers.sources.sporttery import SportteryScraper
        print("✅ 导入SportteryScraper成功")
        
        from backend.scrapers.core.engine import ScraperEngine
        print("✅ 导入ScraperEngine成功")
        
        # 创建引擎
        async with ScraperEngine() as engine:
            print("✅ 创建ScraperEngine成功")
            
            # 创建爬虫
            scraper = SportteryScraper(engine)
            print("✅ 创建SportteryScraper成功")
            
            # 获取比赛数据
            print("\n开始获取比赛数据...")
            matches = await scraper.get_matches(days=3)
            print(f"✅ 获取到 {len(matches)} 场比赛")
            
            if matches:
                print(f"\n第一场比赛:")
                match = matches[0]
                print(f"  {match['home_team']} vs {match['away_team']}")
                print(f"  联赛: {match['league']}")
                print(f"  时间: {match['match_time']}")
                if match.get('is_mock'):
                    print(f"  ⚠️ 模拟数据")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
