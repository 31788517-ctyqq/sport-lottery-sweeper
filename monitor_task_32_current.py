import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.models.crawler_logs import CrawlerTaskLog
from backend.models.matches import FootballMatch

def monitor_task():
    db = next(get_db())
    try:
        # 查询最新的任务
        latest_task = db.query(CrawlerTask).order_by(CrawlerTask.id.desc()).first()
        if not latest_task:
            print("未找到任何任务")
            return
            
        print(f"监控任务ID: {latest_task.id}")
        print(f"任务名称: {latest_task.name}")
        print(f"当前状态: {latest_task.status}")
        print(f"最后运行时间: {latest_task.last_run_time}")
        print(f"运行次数: {latest_task.run_count}")
        print(f"成功次数: {latest_task.success_count}")
        print(f"错误次数: {latest_task.error_count}")
        
        # 查询任务日志
        logs = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.task_id == latest_task.id).order_by(CrawlerTaskLog.created_at.desc()).limit(10).all()
        print("\n最近的日志记录:")
        for log in logs:
            print(f"- 日志ID: {log.id}, 状态: {log.status}, 开始时间: {log.started_at}, 完成时间: {log.completed_at}")
            print(f"  处理记录数: {log.records_processed}, 成功: {log.records_success}, 失败: {log.records_failed}")
            print(f"  错误信息: {log.error_message}")
            print(f"  创建时间: {log.created_at}")
            print("")
        
        # 查询比赛数据表中的记录数
        match_count = db.query(FootballMatch).count()
        print(f"数据库中比赛记录总数: {match_count}")
        
        if match_count > 0:
            recent_matches = db.query(FootballMatch).order_by(FootballMatch.created_at.desc()).limit(5).all()
            print(f"\n最近插入的 {min(5, match_count)} 条比赛记录:")
            for match in recent_matches:
                print(f"- ID: {match.id}, Match ID: {match.match_id}, {match.home_team} vs {match.away_team}, 联赛: {match.league}")
        
        print("\n" + "="*50)
        print("监控要点检查:")
        print("1. 任务是否自动停止并改变状态: ", "是" if latest_task.status in ["SUCCESS", "FAILED"] else "否")
        print("2. 日志中是否显示处理的记录数: ", "是" if logs and any(log.records_processed > 0 for log in logs) else "否")
        print("3. 是否显示数据存储到数据库: ", "是" if match_count > 0 else "否")
        print("4. 数据存储表: football_matches")
        print("5. 存储的数据条数: ", match_count)
        
    finally:
        db.close()

if __name__ == '__main__':
    monitor_task()