import logging
logger = logging.getLogger(__name__)
"""
运行爬虫脚本
用于手动触发爬虫任务
"""


def run_scrape():
    """运行爬虫"""
    from backend.scrapers.sporttery_scraper import sporttery_scraper
    
    logger.debug("开始运行爬虫...")
    result = sporttery_scraper.get_recent_matches(3)
    logger.debug(f"爬取到 {len(result)} 条数据")
    return result


if __name__ == "__main__":
    run_scrape()
