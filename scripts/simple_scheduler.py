#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单定时调度器 - 避免使用复杂的Celery配置
直接调用爬虫脚本实现定时抓取
"""

import time
import schedule
import logging
import subprocess
from datetime import datetime
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def daily_crawl_500wang():
    """每日抓取500彩票网数据"""
    logger.info("🔄 开始执行每日500彩票网抓取任务")
    try:
        result = subprocess.run(
            ['python', 'crawl_500_com.py'],
            capture_output=True,
            text=True,
            cwd='c:/Users/11581/Downloads/sport-lottery-sweeper',
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            logger.info("✅ 每日抓取任务执行成功")
            logger.info(f"输出: {result.stdout}")
        else:
            logger.error(f"❌ 每日抓取任务失败: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ 每日抓取任务异常: {str(e)}")

def hourly_update_500wang():
    """每小时更新500彩票网数据"""
    logger.info("🔄 开始执行每小时500彩票网更新任务")
    try:
        # 每小时也执行完整抓取（简单起见）
        result = subprocess.run(
            ['python', 'crawl_500_com.py'],
            capture_output=True,
            text=True,
            cwd='c:/Users/11581/Downloads/sport-lottery-sweeper',
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            logger.info("✅ 每小时更新任务执行成功")
        else:
            logger.error(f"❌ 每小时更新任务失败: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ 每小时更新任务异常: {str(e)}")

def health_check_500wang():
    """健康检查"""
    logger.info("🔍 执行500彩票网健康检查")
    try:
        import requests
        response = requests.get('https://trade.500.com/jczq/', timeout=30)
        if response.status_code == 200:
            logger.info("✅ 500彩票网连接正常")
        else:
            logger.warning(f"⚠️ 500彩票网返回状态码: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {str(e)}")

def start_scheduler():
    """启动定时调度器"""
    logger.info("🚀 启动简单定时调度器")
    
    # 设置定时任务
    # 每天上午8点执行完整抓取
    schedule.every().day.at("08:00").do(daily_crawl_500wang)
    logger.info("✅ 已设置每日08:00抓取任务")
    
    # 每小时整点执行更新
    schedule.every().hour.at(":00").do(hourly_update_500wang)
    logger.info("✅ 已设置每小时整点更新任务")
    
    # 每30分钟健康检查
    schedule.every(30).minutes.do(health_check_500wang)
    logger.info("✅ 已设置每30分钟健康检查")
    
    # 启动时立即执行一次抓取（测试用）
    logger.info("🧪 启动时立即执行一次抓取测试")
    daily_crawl_500wang()
    
    logger.info("⏰ 定时调度器已启动，等待执行任务...")
    logger.info("📊 任务计划:")
    logger.info("   - 每日08:00: 完整抓取3天赛程")
    logger.info("   - 每小时整点: 更新最新数据")
    logger.info("   - 每30分钟: 健康检查")
    
    # 保持运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        logger.info("👋 定时调度器已停止")
    except Exception as e:
        logger.error(f"❌ 调度器异常退出: {str(e)}")