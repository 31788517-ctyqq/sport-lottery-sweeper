#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
500彩票网定时抓取任务
配置定期自动抓取足球竞彩数据
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 添加路径
sys.path.append(str(BASE_DIR))

from datetime import datetime, timedelta
from celery import Celery

# 直接导入爬虫服务，避免循环导入
sys.path.append(str(BASE_DIR))
from crawl_500_com import SportteryCrawler

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Celery实例
celery = Celery('500wang_scheduler')
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'

@celery.task(name='tasks.500wang.fetch_daily_matches')
def fetch_daily_matches():
    """每日抓取500彩票网比赛数据"""
    logger.info(f"🔄 开始执行500彩票网定时抓取任务 - {datetime.now()}")
    
    try:
        # 直接使用现有的爬虫脚本
        import subprocess
        result = subprocess.run(
            ['python', str(BASE_DIR / 'crawl_500_com.py')],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0:
            logger.info("✅ 500彩票网抓取任务执行成功")
            logger.info(result.stdout)
            return {'status': 'success', 'output': result.stdout}
        else:
            logger.error(f"❌ 抓取失败: {result.stderr}")
            return {'status': 'failed', 'error': result.stderr}
            
    except Exception as e:
        logger.error(f"❌ 定时任务执行异常: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@celery.task(name='tasks.500wang.fetch_hourly_update')
def fetch_hourly_update():
    """每小时更新最新比赛数据"""
    logger.info(f"🔄 执行500彩票网小时更新任务 - {datetime.now()}")
    
    try:
        # 直接使用现有的爬虫脚本，限制为1天
        import subprocess
        result = subprocess.run(
            ['python', str(BASE_DIR / 'crawl_500_com.py')],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0:
            logger.info("✅ 500彩票网小时更新任务执行成功")
            logger.info(result.stdout)
            return {'status': 'success', 'output': result.stdout}
        else:
            logger.error(f"❌ 小时更新失败: {result.stderr}")
            return {'status': 'failed', 'error': result.stderr}
            
    except Exception as e:
        logger.error(f"❌ 小时更新失败: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@celery.task(name='tasks.500wang.health_check')
def health_check():
    """健康检查任务"""
    logger.info(f"🔍 执行500彩票网健康检查 - {datetime.now()}")
    
    try:
        import requests
        
        # 检查网站可达性
        response = requests.get('https://trade.500.com/jczq/', timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ 500彩票网连接正常")
            return {'status': 'healthy', 'website_accessible': True}
        else:
            logger.warning(f"⚠️ 500彩票网返回状态码: {response.status_code}")
            return {'status': 'unhealthy', 'website_accessible': False, 'status_code': response.status_code}
            
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {str(e)}")
        return {'status': 'error', 'error': str(e)}