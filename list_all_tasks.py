import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask

def list_all_tasks():
    db = next(get_db())
    try:
        # 查询所有任务
        tasks = db.query(CrawlerTask).all()
        print("数据库中所有任务:")
        for task in tasks:
            print(f"任务ID: {task.id}, 任务名称: {task.name}, 状态: {task.status}")
    finally:
        db.close()

if __name__ == '__main__':
    list_all_tasks()