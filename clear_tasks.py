import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# 动态添加项目路径以确保模块可以被找到
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, backend_dir)

from backend.models.crawler_tasks import CrawlerTask
from backend.config import Settings

def clear_all_tasks():
    """清除数据库中所有任务数据"""
    # 获取数据库配置
    settings = Settings()
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # 先统计现有任务数量
        task_count = db.query(CrawlerTask).count()
        print(f"当前共有 {task_count} 个任务")
        
        if task_count > 0:
            # 删除所有任务
            deleted_count = db.query(CrawlerTask).delete()
            db.commit()
            print(f"已删除 {deleted_count} 个任务")
        else:
            print("没有任务需要删除")
        
        # 再次确认任务数量
        remaining_count = db.query(CrawlerTask).count()
        print(f"删除后剩余任务数: {remaining_count}")
        
    except Exception as e:
        print(f"删除任务时发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_tasks()