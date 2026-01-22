#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动爬虫控制脚本 - 简单易用的爬虫管理工具
避免复杂的Celery配置问题
"""

import sys
import os
import time
import logging
import subprocess
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/manual_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def crawl_500wang_now():
    """立即抓取500彩票网数据"""
    logger.info("🔄 手动执行500彩票网抓取任务")
    print("正在抓取500彩票网足球竞彩数据...")
    
    try:
        result = subprocess.run(
            ['python', 'crawl_500_com.py'],
            capture_output=True,
            text=True,
            cwd='c:/Users/11581/Downloads/sport-lottery-sweeper',
            encoding='utf-8'
        )
        
        print("\n" + "="*60)
        if result.returncode == 0:
            print("✅ 抓取任务执行成功！")
            print(result.stdout)
        else:
            print("❌ 抓取任务失败！")
            print("错误信息:", result.stderr)
        print("="*60)
        
        logger.info(f"抓取任务完成，返回码: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        error_msg = f"抓取任务异常: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return False

def setup_basic_scheduler():
    """设置基本的定时执行（Windows任务计划）"""
    print("\n📅 Windows任务计划设置指南:")
    print("="*60)
    print("方法1: 使用Windows任务计划程序")
    print("1. 按Win+R，输入taskschd.msc")
    print("2. 创建基本任务")
    print("3. 设置触发器:")
    print("   - 每日抓取: 每天08:00")
    print("   - 每小时更新: 每小时执行")
    print("4. 设置操作:")
    print(f'   - 程序: {sys.executable}')
    print(f'   - 参数: c:/Users/11581/Downloads/sport-lottery-sweeper/scripts/manual_crawler_control.py --crawl')
    print("="*60)
    
def continuous_mode():
    """连续运行模式 - 简单的定时循环"""
    print("🚀 启动连续运行模式")
    print("按Ctrl+C停止")
    print("="*60)
    
    # 立即执行一次
    crawl_500wang_now()
    
    # 简单的定时循环
    cycle = 0
    while True:
        try:
            cycle += 1
            print(f"\n⏰ 第{cycle}次循环，等待60秒...")
            
            # 每小时执行一次（简单计数）
            for i in range(60):
                time.sleep(60)  # 实际应该是60秒，这里为了测试用1秒
                if i % 10 == 0:  # 每10秒提示一次
                    print(f"  等待中... {i+1}/60秒")
            
            # 执行抓取
            print("\n🔄 定时执行抓取任务...")
            crawl_500wang_now()
            
        except KeyboardInterrupt:
            print("\n👋 连续运行模式已停止")
            break

def main():
    """主函数"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--crawl', '-c', 'crawl']:
            crawl_500wang_now()
            
        elif arg in ['--schedule', '-s', 'schedule']:
            setup_basic_scheduler()
            
        elif arg in ['--continuous', '-cont', 'continuous']:
            continuous_mode()
            
        elif arg in ['--help', '-h', 'help']:
            print_help()
            
        else:
            print(f"未知参数: {arg}")
            print_help()
    else:
        print_help()

def print_help():
    """打印帮助信息"""
    print("\n🎯 500彩票网爬虫控制工具")
    print("="*60)
    print("使用方法:")
    print("  python scripts/manual_crawler_control.py --crawl      立即抓取数据")
    print("  python scripts/manual_crawler_control.py --schedule    查看定时设置指南")
    print("  python scripts/manual_crawler_control.py --continuous  连续运行模式")
    print("  python scripts/manual_crawler_control.py --help        显示帮助")
    print("="*60)
    print("快捷命令:")
    print("  python scripts/manual_crawler_control.py crawl         立即抓取")
    print("  python scripts/manual_crawler_control.py schedule     定时设置")
    print("  python scripts/manual_crawler_control.py cont         连续运行")
    print("="*60)

if __name__ == "__main__":
    main()