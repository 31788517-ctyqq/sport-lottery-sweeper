#!/usr/bin/env python3
"""
原始SQL插入数据源
"""
import sqlite3
import json
from datetime import datetime, timedelta

def insert_data_source():
    conn = sqlite3.connect('data/sport_lottery.db')
    c = conn.cursor()
    
    # 检查表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_sources'")
    if not c.fetchone():
        print("表 data_sources 不存在")
        conn.close()
        return False
    
    # 检查是否已有记录
    c.execute("SELECT id, name FROM data_sources WHERE name = ?", ("500万彩票",))
    existing = c.fetchone()
    if existing:
        print(f"数据源已存在: ID={existing[0]}, 名称={existing[1]}")
        conn.close()
        return existing[0]
    
    # 插入新记录
    now = datetime.utcnow()
    config = json.dumps({
        "crawler_type": "500_com",
        "enabled": True,
        "priority": 1,
        "timeout": 30,
        "retry_times": 3
    })
    c.execute("""
        INSERT INTO data_sources 
        (name, type, status, url, config, last_update, error_rate, created_at, updated_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "500万彩票", "api", 1, "https://trade.500.com/jczq/", config, now, 0.0, now, now, 1
    ))
    source_id = c.lastrowid
    conn.commit()
    print(f"数据源插入成功: ID={source_id}")
    
    # 尝试插入 crawler_tasks 表（如果存在）
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_tasks'")
    if c.fetchone():
        task_config = json.dumps({
            "days": 3,
            "category": "竞彩赛程",
            "priority": "high"
        })
        c.execute("""
            INSERT INTO crawler_tasks 
            (name, source_id, task_type, cron_expression, is_active, status, last_run_time, next_run_time, run_count, success_count, error_count, config, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "抓取近三天比赛赛程", source_id, "crawl", "0 */2 * * *", 1, "stopped", None, None, 0, 0, 0, task_config, 1, now
        ))
        task_id = c.lastrowid
        print(f"任务插入成功: ID={task_id}")
    
    conn.close()
    return source_id

if __name__ == "__main__":
    insert_data_source()