"""
测试字符编码修复
"""
import asyncio
from backend.app.scrapers.advanced_crawler import advanced_crawler

async def test_encoding():
    print("测试字符编码修复...")
    
    # 获取数据
    matches = await advanced_crawler.crawl_sporttery_matches(2)
    
    print(f"获取到 {len(matches)} 条比赛数据")
    
    for idx, match in enumerate(matches[:5], 1):  # 只显示前5条
        print(f"\n比赛 {idx}:")
        print(f"  ID: {match.get('id', 'N/A')}")
        print(f"  主队: {match.get('home_team', 'N/A')}")
        print(f"  客队: {match.get('away_team', 'N/A')}")
        print(f"  联赛: {match.get('league', 'N/A')}")
        print(f"  比赛时间: {match.get('match_time', 'N/A')}")
        print(f"  主胜赔率: {match.get('odds_home_win', 'N/A')}")
        print(f"  平局赔率: {match.get('odds_draw', 'N/A')}")
        print(f"  客胜赔率: {match.get('odds_away_win', 'N/A')}")
        print(f"  热门程度: {match.get('popularity', 'N/A')}")
        
        # 检查是否存在乱码字符
        for key, value in match.items():
            if isinstance(value, str):
                # 检查是否包含乱码字符
                if any(ord(c) < 32 or 127 < ord(c) < 160 for c in value):
                    print(f"  警告: {key} 字段可能包含乱码: {repr(value)}")

if __name__ == "__main__":
    asyncio.run(test_encoding())