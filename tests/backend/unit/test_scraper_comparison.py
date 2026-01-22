#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫优化对比测试 - 基础版 vs 增强版
"""

import asyncio
import json
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入爬虫
from backend.app.scrapers.sporttery_scraper import SportteryScraper
from backend.app.scrapers.sporttery_enhanced import EnhancedSportteryScraper


async def test_basic_scraper():
    """测试基础爬虫"""
    print("\n" + "="*70)
    print("测试1: 基础爬虫 (SportteryScraper)")
    print("="*70)
    
    start_time = time.time()
    
    async with SportteryScraper() as scraper:
        matches = await scraper.get_recent_matches(days_ahead=3)
        elapsed = time.time() - start_time
        
        print(f"\n✓ 获取了 {len(matches)} 场比赛")
        print(f"⏱️  耗时: {elapsed:.2f} 秒")
        
        if matches:
            print("\n前3场比赛:")
            for i, match in enumerate(matches[:3], 1):
                print(f"  {i}. {match.get('home_team')} vs {match.get('away_team')} "
                      f"({match.get('match_date')})")
        
        return len(matches), elapsed


async def test_enhanced_scraper():
    """测试增强爬虫"""
    print("\n" + "="*70)
    print("测试2: 增强爬虫 (EnhancedSportteryScraper)")
    print("="*70)
    
    start_time = time.time()
    
    async with EnhancedSportteryScraper() as scraper:
        matches = await scraper.get_recent_matches(days_ahead=3)
        elapsed = time.time() - start_time
        
        print(f"\n✓ 获取了 {len(matches)} 场比赛")
        print(f"⏱️  耗时: {elapsed:.2f} 秒")
        
        if matches:
            print("\n前3场比赛:")
            for i, match in enumerate(matches[:3], 1):
                print(f"  {i}. {match.get('home_team')} vs {match.get('away_team')} "
                      f"({match.get('match_date')})")
        
        return len(matches), elapsed


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  爬虫优化对比测试".center(68) + "║")
    print("║" + "  运行时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S").center(56) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # 测试基础爬虫
        basic_count, basic_time = await test_basic_scraper()
        
        # 测试增强爬虫
        enhanced_count, enhanced_time = await test_enhanced_scraper()
        
        # 对比分析
        print("\n" + "="*70)
        print("对比分析")
        print("="*70)
        print(f"\n📊 数据获取:")
        print(f"  基础爬虫: {basic_count} 场比赛 ({basic_time:.2f}s)")
        print(f"  增强爬虫: {enhanced_count} 场比赛 ({enhanced_time:.2f}s)")
        
        print(f"\n⏱️  性能对比:")
        if enhanced_time > 0:
            speedup = basic_time / enhanced_time
            print(f"  增强爬虫相对速度: {speedup:.2f}x")
        
        print(f"\n🎯 增强爬虫的改进策略:")
        print(f"  1. 网络拦截 (Network Intercept) - 捕获API请求")
        print(f"  2. 直接API调用 - 绕过页面渲染")
        print(f"  3. 增强Playwright - 更好的反检测")
        print(f"  4. 高级HTTP - User-Agent轮换")
        print(f"  5. 模拟数据回退 - 保证可用性")
        
        print(f"\n📌 建议:")
        print(f"  - 生产环境推荐使用 EnhancedSportteryScraper")
        print(f"  - 定期检查网站API端点变化")
        print(f"  - 监控爬虫成功率和数据质量")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
