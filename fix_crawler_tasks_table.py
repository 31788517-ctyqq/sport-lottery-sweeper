#!/usr/bin/env python
"""
修复缺失的crawler_tasks表
"""

import sqlite3
import os

def check_and_create_tables():
    db_path = 'data/sport_lottery.db'
    print(f"📊 检查数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # 暂时禁用外键约束
    cursor = conn.cursor()
    
    # 检查crawler_configs表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_configs'")
    if cursor.fetchone():
        print("✅ crawler_configs表存在")
    else:
        print("❌ crawler_configs表不存在，无法创建crawler_tasks（外键约束）")
        return False
    
    # 检查crawler_tasks表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_tasks'")
    if cursor.fetchone():
        print("✅ crawler_tasks表已存在")
        conn.close()
        return True
    
    # 创建crawler_tasks表
    print("🛠️  创建crawler_tasks表...")
    
    create_table_sql = '''
    CREATE TABLE crawler_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        source_id INTEGER NOT NULL,
        task_type VARCHAR(50) NOT NULL DEFAULT 'crawl',
        cron_expression VARCHAR(100),
        is_active BOOLEAN NOT NULL DEFAULT 1,
        status VARCHAR(20) NOT NULL DEFAULT 'stopped',
        last_run_time DATETIME,
        next_run_time DATETIME,
        run_count INTEGER NOT NULL DEFAULT 0,
        success_count INTEGER NOT NULL DEFAULT 0,
        error_count INTEGER NOT NULL DEFAULT 0,
        config TEXT,
        created_by INTEGER,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_id) REFERENCES crawler_configs(id) ON DELETE CASCADE
    )
    '''
    
    try:
        cursor.execute(create_table_sql)
        
        # 创建索引
        cursor.execute("CREATE INDEX idx_crawler_tasks_source_id ON crawler_tasks(source_id)")
        cursor.execute("CREATE INDEX idx_crawler_tasks_status ON crawler_tasks(status)")
        cursor.execute("CREATE INDEX idx_crawler_tasks_is_active ON crawler_tasks(is_active)")
        cursor.execute("CREATE INDEX idx_crawler_tasks_next_run_time ON crawler_tasks(next_run_time)")
        cursor.execute("CREATE INDEX idx_crawler_tasks_created_at ON crawler_tasks(created_at)")
        
        conn.commit()
        print("✅ crawler_tasks表创建成功")
        
        # 验证表结构
        cursor.execute("PRAGMA table_info(crawler_tasks)")
        columns = cursor.fetchall()
        print(f"📋 表结构 ({len(columns)} 列):")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    success = check_and_create_tables()
    if success:
        print("\n🎉 表修复完成")
    else:
        print("\n⚠️  表修复失败")