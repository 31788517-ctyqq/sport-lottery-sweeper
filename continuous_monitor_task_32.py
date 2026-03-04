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

def continuous_monitor():
    db = next(get_db())
    try:
        # 获取最新任务
        latest_task = db.query(CrawlerTask).order_by(CrawlerTask.id.desc()).first()
        if not latest_task:
            print("未找到任何任务")
            return
            
        task_id = latest_task.id
        print(f"开始监控任务ID: {task_id}")
        print(f"任务名称: {latest_task.name}")
        print(f"初始状态: {latest_task.status}")
        
        attempts = 0
        max_attempts = 60  # 最多等待300秒
        
        while attempts < max_attempts:
            # 刷新任务状态
            db.refresh(latest_task)
            
            print(f"\n第 {attempts+1} 次检查 - {datetime.now().strftime('%H:%M:%S')}")
            print(f"任务状态: {latest_task.status}")
            
            # 查询最新的日志
            latest_log = db.query(CrawlerTaskLog).filter(
                CrawlerTaskLog.task_id == task_id
            ).order_by(CrawlerTaskLog.id.desc()).first()
            
            if latest_log:
                print(f"日志状态: {latest_log.status}")
                print(f"处理记录数: {latest_log.records_processed}, 成功: {latest_log.records_success}, 失败: {latest_log.records_failed}")
                if latest_log.error_message:
                    print(f"错误信息: {latest_log.error_message}")
            
            # 检查任务是否完成
            if latest_task.status in ['SUCCESS', 'FAILED', 'STOPPED']:
                print(f"\n任务已完成，最终状态: {latest_task.status}")
                
                # 检查数据库中的比赛记录
                match_count = db.query(FootballMatch).count()
                print(f"数据库中比赛记录总数: {match_count}")
                
                if match_count > 0:
                    recent_matches = db.query(FootballMatch).order_by(FootballMatch.created_at.desc()).limit(5).all()
                    print(f"\n最近插入的 {min(5, match_count)} 条比赛记录:")
                    for match in recent_matches:
                        print(f"- ID: {match.id}, Match ID: {match.match_id}, {match.home_team} vs {match.away_team}, 联赛: {match.league}")
                
                print("\n" + "="*50)
                print("任务完成检查结果:")
                print("1. 任务是否自动停止并改变状态: ", "是" if latest_task.status in ["SUCCESS", "FAILED", "STOPPED"] else "否")
                
                final_log = db.query(CrawlerTaskLog).filter(
                    CrawlerTaskLog.task_id == task_id
                ).order_by(CrawlerTaskLog.id.desc()).first()
                
                print("2. 日志中是否显示处理的记录数: ", "是" if final_log and final_log.records_processed > 0 else "否")
                print("3. 是否显示数据存储到数据库: ", "是" if match_count > 0 else "否")
                print("4. 数据存储表: football_matches")
                print("5. 存储的数据条数: ", match_count)
                
                return
            
            time.sleep(5)  # 等待5秒后再次检查
            attempts += 1
        
        print(f"\n已达到最大等待次数({max_attempts})，任务仍未完成")
        
    except KeyboardInterrupt:
        print("\n监控被用户中断")
    except Exception as e:
        print(f"监控过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    continuous_monitor()