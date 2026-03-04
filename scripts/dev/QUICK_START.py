#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫优化快速参考卡

三行代码使用增强爬虫:
"""

import asyncio
from app.scrapers.sporttery_enhanced import EnhancedSportteryScraper

async def quick_start():
    """最快的开始方式"""
    
    # 1️⃣ 创建爬虫
    async with EnhancedSportteryScraper() as scraper:
        
        # 2️⃣ 获取数据
        matches = await scraper.get_recent_matches(days_ahead=3)
        
        # 3️⃣ 使用数据
        for match in matches[:3]:
            print(f"{match['home_team']} vs {match['away_team']} ({match['match_date']})")


# ============================================================================
# 常用命令速查表
# ============================================================================

COMMANDS = """
┌─────────────────────────────────────────────────────────────────┐
│                   爬虫优化常用命令                                │
└─────────────────────────────────────────────────────────────────┘

📋 快速测试
  python test_scraper_quick.py
  └─ 测试爬虫是否工作

🔀 对比测试
  python test_scraper_comparison.py
  └─ 对比基础爬虫 vs 增强爬虫

🔍 诊断工具
  python debug_scraper.py
  └─ 找出真实API端点（打开浏览器）

📖 查看优化指南
  python SCRAPER_OPTIMIZATION_GUIDE.py
  └─ 显示完整的优化和集成指南

📄 查看本快速参考
  python QUICK_START.py
  └─ 显示这个快速参考

┌─────────────────────────────────────────────────────────────────┐
│                     代码片段速查表                                 │
└─────────────────────────────────────────────────────────────────┘

1️⃣ 基础使用 - 获取3天内的比赛
   
   from app.scrapers.sporttery_enhanced import EnhancedSportteryScraper
   
   async with EnhancedSportteryScraper() as scraper:
       matches = await scraper.get_recent_matches(days_ahead=3)
       print(f"获取了 {len(matches)} 场比赛")


2️⃣ 获取热门比赛 - 按热度排序
   
   async with EnhancedSportteryScraper() as scraper:
       popular = await scraper.get_popular_matches(limit=10)
       for i, match in enumerate(popular, 1):
           print(f"{i}. {match['home_team']} vs {match['away_team']} "
                 f"热度: {match['popularity']}/100")


3️⃣ 在FastAPI中使用
   
   from fastapi import FastAPI
   from app.scrapers.sporttery_enhanced import EnhancedSportteryScraper
   
   app = FastAPI()
   
   @app.get("/api/matches")
   async def get_matches(days: int = 3):
       async with EnhancedSportteryScraper() as scraper:
           matches = await scraper.get_recent_matches(days_ahead=days)
           return {"count": len(matches), "matches": matches}


4️⃣ 带错误处理的使用
   
   async with EnhancedSportteryScraper() as scraper:
       try:
           matches = await scraper.get_recent_matches(days_ahead=3)
       except Exception as e:
           print(f"获取失败: {e}")
           # 自动回退到模拟数据


5️⃣ 自定义参数
   
   scraper = EnhancedSportteryScraper()
   
   # 修改API端点
   scraper.api_endpoints = [
       "https://真实API1",
       "https://真实API2",
   ]
   
   # 修改User-Agent
   scraper.user_agents = [
       "你的User-Agent1",
       "你的User-Agent2",
   ]


┌─────────────────────────────────────────────────────────────────┐
│                   数据格式速查表                                  │
└─────────────────────────────────────────────────────────────────┘

返回的比赛数据结构:

{
    'id': 'match_001',                    # 比赛ID
    'match_id': 'id_001',                 # 内部ID
    'home_team': '曼城',                  # 主队
    'away_team': '阿森纳',                # 客队
    'league': '英超',                     # 联赛名称
    'match_date': '2026-01-16 19:00',     # 比赛时间
    'match_time': '2026-01-16 19:00',     # 比赛时间
    'odds_home_win': 2.5,                 # 主胜赔率
    'odds_draw': 3.2,                     # 平局赔率
    'odds_away_win': 2.8,                 # 客胜赔率
    'status': 'scheduled',                # 状态: scheduled/playing/finished
    'popularity': 85                      # 热度: 1-100
}


┌─────────────────────────────────────────────────────────────────┐
│                   故障排除速查表                                  │
└─────────────────────────────────────────────────────────────────┘

问题                         解决方案
────────────────────────────────────────────────────────────────
无法获取真实数据             1. 运行 python debug_scraper.py
                            2. 检查DevTools Network标签
                            3. 更新api_endpoints

爬虫太慢                      1. 检查网络连接
                            2. 减少超时时间
                            3. 使用代理IP

被网站封IP                   1. 使用residential proxy
                            2. 降低请求频率
                            3. 添加随机延时

返回模拟数据                 网站数据不可用，尝试:
                            1. 检查网站是否在线
                            2. 更新反爬虫策略
                            3. 联系获取官方API


┌─────────────────────────────────────────────────────────────────┐
│                   关键概念解释                                    │
└─────────────────────────────────────────────────────────────────┘

🔵 网络拦截 (Network Intercept)
   = 在浏览器加载页面时拦截网络请求
   = 优点: 直接获取API数据，速度快
   = 缺点: 需要正确的路由规则

🟢 直接API调用 (Direct API)
   = 直接访问API端点，不加载页面
   = 优点: 速度最快，减少带宽
   = 缺点: 需要知道正确的API端点

🟡 增强Playwright爬取
   = 使用浏览器自动化 + 反检测脚本
   = 优点: 通过大多数反爬虫机制
   = 缺点: 速度慢，资源占用多

🟠 高级HTTP爬取
   = 使用自定义HTTP头和User-Agent
   = 优点: 轻量级，速度快
   = 缺点: 容易被检测

🔴 模拟数据备选
   = 生成虚假但有效的数据
   = 优点: 保证系统可用性
   = 缺点: 不是真实数据


┌─────────────────────────────────────────────────────────────────┐
│                   相关文件导航                                    │
└─────────────────────────────────────────────────────────────────┘

核心爬虫
  📄 app/scrapers/sporttery_enhanced.py   (增强爬虫)
  📄 app/scrapers/sporttery_scraper.py    (基础爬虫)

测试和诊断
  🧪 test_scraper_quick.py                (快速测试)
  🔄 test_scraper_comparison.py           (对比测试)
  🔍 debug_scraper.py                     (诊断工具)

文档和指南
  📖 SCRAPER_OPTIMIZATION_GUIDE.py        (完整指南)
  📋 SCRAPER_OPTIMIZATION_SUMMARY.md      (总结文档)
  ⚡ QUICK_START.py                       (本文件)

集成示例
  🎯 api.py                               (主API文件)
  🚀 main.py                              (应用入口)


┌─────────────────────────────────────────────────────────────────┐
│                   最佳实践                                        │
└─────────────────────────────────────────────────────────────────┘

✅ DO:
  ✓ 定期运行诊断检查网站变化
  ✓ 添加错误日志和监控
  ✓ 使用缓存减少爬虫压力
  ✓ 遵守网站robots.txt
  ✓ 添加请求延时模拟真实用户

❌ DON'T:
  ✗ 不要高频率大量爬取
  ✗ 不要忽视robots.txt
  ✗ 不要在生产环境进行侵略性爬取
  ✗ 不要跳过错误处理
  ✗ 不要违反法律和政策


┌─────────────────────────────────────────────────────────────────┐
│                   快速开始 (3步)                                 │
└─────────────────────────────────────────────────────────────────┘

Step 1: 测试现有爬虫
  $ python test_scraper_quick.py

Step 2: 运行诊断找出真实API
  $ python debug_scraper.py
  (按照输出提示在浏览器检查)

Step 3: 集成到应用
  在 api.py 中使用 EnhancedSportteryScraper
  然后测试 API 端点

完成！🎉
"""

if __name__ == "__main__":
    print(COMMANDS)
