"""
同步数据源到爬虫配置并创建任务
确保数据源和任务在后台系统中都有显示
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.data_sources import DataSource
from backend.models.crawler_config import CrawlerConfig
from backend.models.crawler_tasks import CrawlerTask
from sqlalchemy.exc import IntegrityError


def sync_data_source_to_task():
    """同步数据源到爬虫配置并创建任务"""
    print("="*60)
    print("开始同步数据源到爬虫配置并创建任务")
    print("="*60)
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 查找100qiu数据源
        data_source = db.query(DataSource).filter(
            DataSource.name == '100qiu竞彩基础数据'
        ).first()
        
        if not data_source:
            print("❌ 未找到100qiu竞彩基础数据源")
            return
        
        print(f"✓ 找到数据源: {data_source.name} (ID: {data_source.id})")
        
        # 检查是否已存在对应的爬虫配置
        crawler_config = db.query(CrawlerConfig).filter(
            CrawlerConfig.name == '100qiu竞彩基础数据'
        ).first()
        
        if crawler_config:
            print(f"✓ 爬虫配置已存在: {crawler_config.name} (ID: {crawler_config.id})")
        else:
            # 创建爬虫配置
            crawler_config = CrawlerConfig(
                name="100qiu竞彩基础数据",
                description="100qiu竞彩基础数据源的爬虫配置",
                url=data_source.url,
                frequency=3600,  # 每小时执行一次
                is_active=True,
                config_data=json.dumps(data_source.config) if hasattr(data_source, 'config') else '{}',
                created_by=1  # 系统管理员ID
            )
            
            db.add(crawler_config)
            db.commit()
            db.refresh(crawler_config)
            
            print(f"✓ 成功创建爬虫配置: {crawler_config.name} (ID: {crawler_config.id})")
        
        # 检查是否已存在对应的任务
        crawler_task = db.query(CrawlerTask).filter(
            CrawlerTask.source_id == crawler_config.id,
            CrawlerTask.name == '100qiu数据抓取任务'
        ).first()
        
        if crawler_task:
            print(f"✓ 任务已存在: {crawler_task.name} (ID: {crawler_task.id})")
        else:
            # 创建爬虫任务
            crawler_task = CrawlerTask(
                name="100qiu数据抓取任务",
                source_id=crawler_config.id,  # 关联爬虫配置ID
                task_type="crawl",
                cron_expression="0 */2 * * *",  # 每2小时执行一次
                is_active=True,
                status="stopped",  # 初始状态为停止
                config={
                    "data_source_type": "hundred_qiu",
                    "params": {
                        "dateTime": "26011"
                    }
                },
                created_by=1
            )
            
            db.add(crawler_task)
            db.commit()
            db.refresh(crawler_task)
            
            print(f"✓ 成功创建任务: {crawler_task.name} (ID: {crawler_task.id})")
        
        print("\n" + "="*60)
        print("同步完成！现在可以在以下页面查看数据：")
        print("1. 数据源配置页面: 显示数据源信息")
        print("2. 任务控制台页面: 显示任务信息")
        print("="*60)
        
    except Exception as e:
        print(f"同步过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import json
    sync_data_source_to_task()