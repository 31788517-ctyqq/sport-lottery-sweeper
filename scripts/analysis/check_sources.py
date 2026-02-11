import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.crawler_config import CrawlerConfig
from backend.models.data_sources import DataSource

def check_sources():
    db = next(get_db())
    try:
        print("=== 数据源 (data_sources) ===")
        # 查询数据源表
        sources = db.query(DataSource).all()
        for source in sources:
            print(f"ID: {source.id}, 名称: {source.name}, 类型: {source.type}, URL: {source.url}")
        
        print("\n=== 爬虫配置 (crawler_configs) ===")
        # 查询爬虫配置表
        configs = db.query(CrawlerConfig).all()
        for config in configs:
            print(f"ID: {config.id}, 源ID: {config.source_id}, 名称: {config.name}, URL: {config.url}")
            
    finally:
        db.close()

if __name__ == '__main__':
    check_sources()