"""
检查爬虫数据格式的脚本
"""
import asyncio
import sys
import os
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.scrapers.zqszsc_scraper import zqszsc_scraper


async def check_data_format():
    """检查数据格式"""
    print("开始检查爬虫数据格式...")
    
    try:
        async with zqszsc_scraper as scraper:
            print("正在获取近3天的比赛数据...")
            matches = await scraper.get_recent_matches(3)
            
            print(f"总共获取到 {len(matches)} 场比赛数据")
            
            print("\n前5条数据的详细格式检查:")
            for i, match in enumerate(matches[:5]):
                print(f"\n--- 比赛 {i+1} ---")
                for key, value in match.items():
                    print(f"  {key}: {repr(value)}")
                
            print("\n数据字段统计:")
            all_keys = set()
            for match in matches:
                all_keys.update(match.keys())
            
            print(f"所有可能的字段: {list(all_keys)}")
            
            # 检查特定字段的格式
            print(f"\n格式问题检查:")
            issues = []
            for i, match in enumerate(matches):
                # 检查是否有乱码
                for key, value in match.items():
                    if isinstance(value, str):
                        if 'é' in value or 'ä' in value or '¸' in value or 'ç' in value:  # 常见乱码字符
                            issues.append(f"比赛 {i+1} {key}: {value} (疑似乱码)")
                        elif value.startswith('周') and len(value) < 3:  # 可能是错误提取的占位符
                            issues.append(f"比赛 {i+1} {key}: {value} (疑似占位符)")
            
            if issues:
                print("发现以下格式问题:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("未发现明显的格式问题")
                
    except Exception as e:
        print(f"检查数据格式失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_data_format())