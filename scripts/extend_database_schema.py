"""
数据库扩展脚本
添加智能体相关表和用户画像表
"""

import sqlite3
import os
from pathlib import Path

def extend_database():
    # 获取数据库路径
    db_path = Path("../sport_lottery.db")  # 根据实际项目结构调整
    
    # 如果数据库不存在，提示用户
    if not db_path.exists():
        print(f"警告: 数据库文件 {db_path} 不存在，将创建新数据库")
    
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建智能体日志表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name VARCHAR(100),
        task_type VARCHAR(100),
        input_data TEXT,
        output_data TEXT,
        execution_time REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 创建用户画像表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        risk_tolerance FLOAT,
        preferred_teams TEXT,
        betting_patterns TEXT,
        success_rate FLOAT,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 提交更改
    conn.commit()
    
    # 验证表是否创建成功
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表:", [table[0] for table in tables])
    
    # 关闭连接
    conn.close()
    
    print("数据库扩展完成！")


if __name__ == "__main__":
    extend_database()