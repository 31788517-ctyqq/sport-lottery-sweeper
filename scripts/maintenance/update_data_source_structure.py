"""
更新数据源表结构，添加错误状态相关字段
"""
import sqlite3
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import engine
from backend.models.data_sources import DataSource

def update_data_source_structure():
    """更新数据源表结构"""
    print("正在更新数据源表结构...")
    
    # 使用统一的数据库路径
    from backend.database import DATABASE_PATH
    db_path = str(DATABASE_PATH)
    print(f"使用数据库文件: {db_path}")
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查last_error列是否存在
        cursor.execute("PRAGMA table_info(data_sources)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'last_error' not in columns:
            print("添加last_error列...")
            cursor.execute("ALTER TABLE data_sources ADD COLUMN last_error TEXT")
        
        if 'last_error_time' not in columns:
            print("添加last_error_time列...")
            cursor.execute("ALTER TABLE data_sources ADD COLUMN last_error_time DATETIME")
        
        # 检查status列的类型
        cursor.execute("""
            SELECT type FROM pragma_table_info('data_sources') 
            WHERE name = 'status'
        """)
        status_col_info = cursor.fetchone()
        
        print(f"当前status列类型: {status_col_info[0] if status_col_info else 'Unknown'}")
        
        conn.commit()
        print("数据源表结构更新完成!")
        
    except Exception as e:
        print(f"更新表结构时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_data_source_structure()