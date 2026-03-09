"""
调试爬虫模块
用于测试和验证爬虫功能
"""
from backend.scrapers.advanced_crawler import advanced_crawler
import logging
logger = logging.getLogger(__name__)
from backend.scrapers.pipeline import pipeline


def debug_crawler():
    logger.debug("开始调试爬虫...")
    
    # 示例：使用高级爬虫
    result = advanced_crawler.fetch_data("https://example.com")
    logger.debug(f"爬取结果: {result}")
    
    # 示例：使用管道处理
    processed = pipeline.process(result)
    logger.debug(f"处理结果: {processed}")


if __name__ == "__main__":
    debug_crawler()
