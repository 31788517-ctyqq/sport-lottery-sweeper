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