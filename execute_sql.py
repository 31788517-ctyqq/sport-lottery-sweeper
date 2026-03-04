import sqlite3

def execute_sql_script():
    """执行SQL脚本创建log_entries表"""
    sql_commands = '''
-- 创建log_entries表
CREATE TABLE IF NOT EXISTS log_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20),
    module VARCHAR(100),
    message TEXT,
    user_id INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100),
    request_path VARCHAR(500),
    response_status INTEGER,
    duration_ms INTEGER,
    extra_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 为常用查询字段创建索引
CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries(level);
CREATE INDEX IF NOT EXISTS idx_log_entries_module ON log_entries(module);
CREATE INDEX IF NOT EXISTS idx_log_entries_user_id ON log_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_log_entries_ip_address ON log_entries(ip_address);
CREATE INDEX IF NOT EXISTS idx_timestamp_level ON log_entries(timestamp, level);
CREATE INDEX IF NOT EXISTS idx_user_timestamp ON log_entries(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_module_level ON log_entries(module, level);
'''
    
    try:
        # 连接到数据库
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        # 执行SQL命令
        cursor.executescript(sql_commands)
        
        # 提交更改
        conn.commit()
        
        print("log_entries表及相关索引创建成功！")
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_entries';")
        result = cursor.fetchone()
        if result:
            print("✓ log_entries表已成功创建")
            
            # 检查表结构
            cursor.execute('PRAGMA table_info(log_entries);')
            columns = cursor.fetchall()
            print(f"✓ log_entries表结构 ({len(columns)} 列):")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''} {'NOT NULL' if col[3] else 'NULLABLE'}")
        else:
            print("✗ log_entries表创建失败")
        
        conn.close()
        
    except Exception as e:
        print(f"执行SQL脚本时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    execute_sql_script()