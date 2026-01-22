from backend.scrapers.sporttery_scraper_clean import sporttery_scraper


def run_scrape_clean():
    """运行干净的爬虫"""
    print("开始运行干净版爬虫...")
    result = sporttery_scraper.get_recent_matches(3)
    print(f"爬取到 {len(result)} 条数据")
    return result


if __name__ == "__main__":
    run_scrape_clean()