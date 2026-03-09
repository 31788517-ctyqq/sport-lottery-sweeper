import sqlite3
import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.append(str(Path(__file__).parent / 'backend'))

from backend.database import DATABASE_PATH

def update_status_column():
    # 使用统一的数据库路径
    db_path = str(DATABASE_PATH)
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 确保临时表不存在
        print("清理可能存在的临时表...")
        cursor.execute("DROP TABLE IF EXISTS data_sources_temp;")
        
        # 首先备份status列的数据
        print("正在备份status列的数据...")
        cursor.execute("SELECT id, status FROM data_sources;")
        rows = cursor.fetchall()
        
        # 创建临时表，包含修改后的结构
        print("创建临时表...")
        cursor.execute("""
            CREATE TABLE data_sources_temp (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'online',  -- 改为VARCHAR类型
                url VARCHAR(500),
                config TEXT,
                field_mapping TEXT,
                update_frequency INTEGER DEFAULT 60,  -- 添加默认值
                last_update DATETIME,
                error_rate FLOAT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                source_id VARCHAR(10),
                last_error TEXT,
                last_error_time DATETIME
            );
        """)
        
        # 复制原始数据，将status值转换为字符串
        print("转换并复制数据...")
        for row in rows:
            data_id, status_val = row
            # 将整数状态转换为字符串
            str_status = 'online' if status_val == 1 else 'offline'
            
            # 从原表获取一行数据
            cursor.execute("""
                SELECT name, type, url, config, field_mapping, update_frequency,
                       last_update, error_rate, created_at, updated_at, created_by, 
                       source_id, last_error, last_error_time
                FROM data_sources WHERE id = ?;
            """, (data_id,))
            orig_row = cursor.fetchone()
            
            # 插入到临时表
            cursor.execute("""
                INSERT INTO data_sources_temp 
                (id, name, type, status, url, config, field_mapping, update_frequency,
                 last_update, error_rate, created_at, updated_at, created_by, 
                 source_id, last_error, last_error_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (data_id, orig_row[0], orig_row[1], str_status, orig_row[2], orig_row[3], 
                  orig_row[4], orig_row[5] if orig_row[5] is not None else 60, 
                  orig_row[6], orig_row[7], orig_row[8], orig_row[9], orig_row[10], 
                  orig_row[11], orig_row[12], orig_row[13]))
        
        # 删除原表
        print("删除原表...")
        cursor.execute("DROP TABLE data_sources;")
        
        # 重命名临时表
        print("重命名临时表...")
        cursor.execute("ALTER TABLE data_sources_temp RENAME TO data_sources;")
        
        # 创建索引（如果有的话）
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_sources_name ON data_sources(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_sources_source_id ON data_sources(source_id);")
        
        conn.commit()
        print("✅ 数据库表结构更新完成!")
        
        # 验证更新结果
        print("\n验证更新结果:")
        cursor.execute("PRAGMA table_info(data_sources);")
        columns = cursor.fetchall()
        
        print("更新后的data_sources表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] == 1 else ''} - Default: {col[4]}")
        
        # 查询一些数据示例
        print("\n更新后的数据示例:")
        cursor.execute("SELECT id, name, status FROM data_sources LIMIT 5;")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID: {row[0]}, Name: {row[1]}, Status: {row[2]} (type: {type(row[2]).__name__})")
        
    except Exception as e:
        print(f"更新表结构失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_status_column()