"""
展示从竞彩网获取的数据
"""
import asyncio
import logging
logger = logging.getLogger(__name__)
import json
from backend.scrapers.advanced_crawler import advanced_crawler


def show_data():
    """展示数据"""
    logger.debug("获取数据...")
    data = advanced_crawler.fetch_data("https://example.com")
    logger.debug(f"数据: {data}")
    return data


if __name__ == "__main__":
    show_data()
