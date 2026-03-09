import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.models.crawler_logs import CrawlerTaskLog

def check_task_status():
    db = next(get_db())
    try:
        # 查询任务ID 32
        task = db.query(CrawlerTask).filter(CrawlerTask.id == 32).first()
        if task:
            print(f"任务ID: {task.id}")
            print(f"任务名称: {task.name}")
            print(f"当前状态: {task.status}")
            print(f"最后运行时间: {task.last_run_time}")
            print(f"下次运行时间: {task.next_run_time}")
            print(f"运行次数: {task.run_count}")
            print(f"成功次数: {task.success_count}")
            print(f"错误次数: {task.error_count}")
            print(f"配置: {task.config}")
            
            # 查询任务日志
            logs = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.task_id == 32).order_by(CrawlerTaskLog.created_at.desc()).limit(10).all()
            print("\n最近的日志记录:")
            for log in logs:
                print(f"- 日志ID: {log.id}, 状态: {log.status}, 开始时间: {log.started_at}, 完成时间: {log.completed_at}")
                print(f"  处理记录数: {log.records_processed}, 成功: {log.records_success}, 失败: {log.records_failed}")
                print(f"  错误信息: {log.error_message}")
                print(f"  创建时间: {log.created_at}")
                print("")
        else:
            print("未找到任务ID 32")
    finally:
        db.close()

if __name__ == '__main__':
    check_task_status()