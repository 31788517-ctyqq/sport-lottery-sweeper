import sys
import os
from datetime import datetime
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.services.task_scheduler_service import TaskSchedulerService

def create_and_monitor_task():
    db = next(get_db())
    try:
        # 获取最新的爬虫配置ID
        from backend.models.crawler_config import CrawlerConfig
        latest_config = db.query(CrawlerConfig).order_by(CrawlerConfig.id.desc()).first()
        if not latest_config:
            print("没有找到任何爬虫配置")
            return
        
        # 创建一个新的爬虫任务
        task = CrawlerTask(
            name="Final Monitoring Test Task",
            source_id=latest_config.id,  # 使用爬虫配置的ID
            task_type='crawl',
            cron_expression=None,
            is_active=True,
            status='stopped',  # 初始状态为停止
            config={"timeout": 30, "retry": 3, "days": 1}
        )
        
        db.add(task)
        db.commit()
        
        task_id = task.id
        print(f"创建的新任务ID: {task_id}")
        
        # 使用任务调度服务启动任务
        service = TaskSchedulerService(db)
        result = service.trigger_task(task_id, triggered_by=1)  # 假设用户ID为1
        
        print(f"任务启动结果: {result}")
        
        # 等待几秒钟让任务执行
        print("等待任务执行...")
        time.sleep(10)
        
        # 再次查询任务状态
        updated_task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
        print(f"任务ID: {updated_task.id}")
        print(f"任务名称: {updated_task.name}")
        print(f"当前状态: {updated_task.status}")
        print(f"成功次数: {updated_task.success_count}")
        print(f"错误次数: {updated_task.error_count}")
        
        # 查询任务日志
        from backend.models.crawler_logs import CrawlerTaskLog
        logs = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.task_id == task_id).order_by(CrawlerTaskLog.created_at.desc()).limit(5).all()
        print(f"\n任务日志:")
        for log in logs:
            print(f"- 状态: {log.status}")
            print(f"  处理记录数: {log.records_processed}, 成功: {log.records_success}, 失败: {log.records_failed}")
            print(f"  开始时间: {log.started_at}, 完成时间: {log.completed_at}")
            if log.error_message:
                print(f"  错误信息: {log.error_message}")
        
        # 检查数据库中的比赛记录
        from backend.models.matches import FootballMatch
        match_count = db.query(FootballMatch).count()
        print(f"\n数据库中比赛记录总数: {match_count}")
        
        if match_count > 0:
            recent_matches = db.query(FootballMatch).order_by(FootballMatch.created_at.desc()).limit(5).all()
            print(f"最近插入的 {min(5, match_count)} 条比赛记录:")
            for match in recent_matches:
                print(f"- ID: {match.id}, Match ID: {match.match_id}, {match.home_team} vs {match.away_team}, 联赛: {match.league}")
        
        print("\n" + "="*50)
        print("任务完成检查结果:")
        print("1. 任务是否自动停止并改变状态: ", "是" if updated_task.status in ["SUCCESS", "FAILED", "STOPPED"] else "否")
        
        final_log = db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.task_id == task_id
        ).order_by(CrawlerTaskLog.id.desc()).first()
        
        print("2. 日志中是否显示处理的记录数: ", "是" if final_log and final_log.records_processed > 0 else "否")
        print("3. 是否显示数据存储到数据库: ", "是" if match_count > 0 else "否")
        print("4. 数据存储表: football_matches")
        print("5. 存储的数据条数: ", match_count)
        
    except Exception as e:
        print(f"创建或监控任务时发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    create_and_monitor_task()