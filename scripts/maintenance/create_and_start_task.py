import requests
import json
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.services.task_scheduler_service import TaskSchedulerService

def create_and_start_task():
    db = next(get_db())
    try:
        # 创建一个新的爬虫任务
        task = CrawlerTask(
            name="Monitoring Test Task",
            source_id=4,  # 使用100qiu数据源
            task_type='crawl',
            cron_expression=None,
            is_active=True,
            status='stopped',  # 初始状态为停止
            config={"timeout": 30, "retry": 3, "days": 1}
        )
        
        db.add(task)
        db.commit()
        
        print(f"创建的新任务ID: {task.id}")
        
        # 使用任务调度服务启动任务
        service = TaskSchedulerService(db)
        result = service.trigger_task(task.id, triggered_by=1)  # 假设用户ID为1
        
        print(f"任务启动结果: {result}")
        
        # 再次查询任务状态
        updated_task = db.query(CrawlerTask).filter(CrawlerTask.id == task.id).first()
        print(f"任务ID: {updated_task.id}, 状态: {updated_task.status}")
        
    except Exception as e:
        print(f"创建或启动任务时发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_and_start_task()