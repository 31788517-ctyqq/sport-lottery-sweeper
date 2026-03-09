import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from backend.services.task_scheduler_service import TaskSchedulerService
from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.models.crawler_config import CrawlerConfig

def test_data_storage():
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建任务调度服务实例
        service = TaskSchedulerService(db)
        
        # 获取一个100qiu数据源
        source = db.query(CrawlerConfig).filter(
            CrawlerConfig.url.like('%100qiu%')
        ).first()
        
        if not source:
            print("未找到100qiu数据源")
            return
            
        print(f"找到数据源: {source.name}, URL: {source.url}")
        
        # 获取一个任务
        task = db.query(CrawlerTask).first()
        
        if not task:
            print("未找到任务")
            return
            
        print(f"使用任务: {task.name}, ID: {task.id}")
        
        # 执行真实任务逻辑
        result = service._execute_real_task_logic(task, source)
        
        print(f"任务执行结果: {result}")
        
        # 检查数据库中是否已保存数据
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            match_count = session.execute(text("SELECT COUNT(*) FROM football_matches")).fetchone()[0]
            print(f"\n现在数据库中有 {match_count} 条比赛记录")
            
            if match_count > 0:
                matches = session.execute(text("SELECT id, match_id, home_team, away_team, league FROM football_matches ORDER BY created_at DESC LIMIT 5")).fetchall()
                print("\n最近的比赛数据:")
                for match in matches:
                    print(f"  - ID: {match[0]}, Match ID: {match[1]}, {match[2]} vs {match[3]}, 联赛: {match[4]}")
        finally:
            session.close()
    
    finally:
        db.close()

if __name__ == '__main__':
    test_data_storage()