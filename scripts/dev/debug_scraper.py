"""
调试爬虫脚本，检查是否能获取真实数据
"""
import asyncio
import sys
import os
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.scrapers.zqszsc_scraper import zqszsc_scraper

# 设置日志级别为DEBUG以查看更多信息
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def debug_scraper():
    """调试爬虫功能"""
    print("开始调试中国足球赛事赛程爬虫...")
    
    try:
        async with zqszsc_scraper as scraper:
            print(f"目标URL: {scraper.target_url}")
            print("正在获取近3天的比赛数据...")
            
            matches = await scraper.get_recent_matches(3)
            
            print(f"获取到 {len(matches)} 场比赛数据:")
            
            if len(matches) > 0 and 'source' in matches[0] and matches[0]['source'] == '模拟数据':
                print("注意: 正在使用模拟数据，说明真实数据获取失败")
            else:
                print("成功获取到真实数据")
                
            for i, match in enumerate(matches[:10]):  # 只打印前10个
                print(f"{i+1}. {match.get('league', '未知联赛')} - "
                      f"{match.get('home_team', '未知主队')} VS {match.get('away_team', '未知客队')} - "
                      f"{match.get('match_time', '未知时间')} - "
                      f"来源: {match.get('source', '未知')}")
            
            if len(matches) > 10:
                print(f"... 还有 {len(matches) - 10} 场比赛")
                
    except Exception as e:
        print(f"爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_scraper())