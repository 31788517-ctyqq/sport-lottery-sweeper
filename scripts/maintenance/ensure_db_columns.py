import sqlite3
import os
from pathlib import Path

def ensure_data_sources_columns():
    """确保data_sources表包含所有必需的列"""
    # 项目根目录
    project_root = Path(__file__).parent
    db_path = project_root / "backend" / "sport_lottery.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False
        
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_sources';")
        if not cursor.fetchone():
            print("data_sources表不存在，需要初始化数据库")
            return False
            
        # 获取现有列
        cursor.execute("PRAGMA table_info(data_sources);")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"当前data_sources表的列: {existing_columns}")
        
        # 检查缺失的列并添加
        required_columns = {
            'last_error': 'TEXT',
            'last_error_time': 'DATETIME'
        }
        
        modified = False
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                print(f"正在添加列: {col_name} ({col_type})")
                cursor.execute(f"ALTER TABLE data_sources ADD COLUMN {col_name} {col_type};")
                modified = True
                
        if modified:
            conn.commit()
            print("数据库表结构已更新")
        else:
            print("数据库表结构已经完整，无需更新")
            
        return True
        
    except Exception as e:
        print(f"更新数据库表结构时出错: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("开始检查并修复数据库表结构...")
    ensure_data_sources_columns()
    print("检查完成")