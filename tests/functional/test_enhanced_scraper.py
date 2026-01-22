#!/usr/bin/env python3
"""
测试 EnhancedSportteryScraper 功能
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers import EnhancedSportteryScraper


async def test_enhanced_scraper():
    """测试增强爬虫功能"""
    print("开始测试 EnhancedSportteryScraper...")
    
    scraper = EnhancedSportteryScraper()
    try:
        result = await scraper.get_recent_matches(1)
        print(f"测试成功！获取到 {len(result) if result else 0} 条记录")
        if result:
            print(f"第一条记录示例: {result[0] if len(result) > 0 else '无数据'}")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.close_session()
    
    return result


if __name__ == "__main__":
    asyncio.run(test_enhanced_scraper())