#!/usr/bin/env python3
"""
手动插入数据源和任务
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.data_sources import DataSource
from backend.models.crawler_tasks import CrawlerTask
from datetime import datetime, timedelta
import json

# 使用现有数据库配置
DATABASE_URL = "sqlite:///./sport_lottery.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_data_source():
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(DataSource).filter(DataSource.name == "500万彩票").first()
        if existing:
            print(f"数据源已存在，ID: {existing.id}")
            return existing.id
        
        # 创建新数据源
        new_source = DataSource(
            name="500万彩票",
            type="api",
            status=True,
            url="https://trade.500.com/jczq/",
            config=json.dumps({
                "crawler_type": "500_com",
                "enabled": True,
                "priority": 1,
                "timeout": 30,
                "retry_times": 3
            }),
            last_update=datetime.utcnow(),
            error_rate=0.0,
            created_by=1  # 假设管理员ID为1
        )
        db.add(new_source)
        db.commit()
        db.refresh(new_source)
        print(f"数据源创建成功，ID: {new_source.id}")
        return new_source.id
    except Exception as e:
        print(f"插入数据源失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def insert_crawler_task(source_id):
    db = SessionLocal()
    try:
        existing = db.query(CrawlerTask).filter(CrawlerTask.task_name == "抓取近三天比赛赛程").first()
        if existing:
            print(f"任务已存在，ID: {existing.id}")
            return existing.id
        
        new_task = CrawlerTask(
            task_name="抓取近三天比赛赛程",
            source="500wan",
            schedule="0 */2 * * *",
            enabled=True,
            config=json.dumps({
                "days": 3,
                "category": "竞彩赛程",
                "priority": "high",
                "last_run": None
            }),
            created_by=1
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        print(f"任务创建成功，ID: {new_task.id}")
        return new_task.id
    except Exception as e:
        print(f"插入任务失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def main():
    print("=== 手动插入数据源和任务 ===")
    source_id = insert_data_source()
    if source_id:
        task_id = insert_crawler_task(source_id)
    else:
        print("数据源插入失败，跳过任务插入")
    
    print("=== 完成 ===")
    print("请刷新数据源管理页面和任务台管理页面查看数据")

if __name__ == "__main__":
    main()