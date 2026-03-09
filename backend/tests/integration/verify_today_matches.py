"""
验证爬虫是否获取到从今天开始的三天比赛数据
"""
import asyncio
import logging
logger = logging.getLogger(__name__)
import json
from datetime import datetime, timedelta
from backend.scrapers.advanced_crawler import advanced_crawler


def verify_today_matches():
    """验证今日比赛"""
    logger.debug("验证今日比赛...")
    # 示例用法
    result = advanced_crawler.verify_matches()
    logger.debug(f"验证结果: {result}")
    return result


if __name__ == "__main__":
    verify_today_matches()
