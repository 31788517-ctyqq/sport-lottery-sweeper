"""
添加日志表到数据库
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, inspect
from backend.models.base import Base
from backend.config import settings
from backend.core.database import engine

def add_log_table():
    """添加log_entries表到数据库"""
    try:
        # 检查表是否已存在
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"数据库中现有的表: {existing_tables}")
        
        if 'log_entries' in existing_tables:
            print("log_entries 表已存在")
            # 检查表中的记录数
            import sqlite3
            conn = sqlite3.connect('data/sport_lottery.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM log_entries;')
            count = cursor.fetchone()[0]
            print(f'  log_entries 表中有 {count} 条记录')
            conn.close()
            return
        
        print("log_entries 表不存在，正在创建...")
        
        # 导入LogEntry模型以确保它被注册到Base.metadata
        from backend.models.log_entry import LogEntry
        
        print(f"注册的表: {list(Base.metadata.tables.keys())}")
        
        # 创建所有表（因为可能有外键依赖）
        Base.metadata.create_all(engine)
        
        # 再次检查表是否已创建
        updated_tables = inspector.get_table_names()
        
        if 'log_entries' in updated_tables:
            print("✓ log_entries 表创建成功!")
            
            # 验证表结构
            columns = inspector.get_columns('log_entries')
            print(f"log_entries 表结构 ({len(columns)} 列):")
            for col in columns:
                print(f"  - {col['name']} ({col['type']}) {'PRIMARY KEY' if col['primary_key'] else ''} {'NOT NULL' if not col['nullable'] else 'NULLABLE'}")
            
            # 检查表中的记录数
            import sqlite3
            conn = sqlite3.connect('data/sport_lottery.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM log_entries;')
            count = cursor.fetchone()[0]
            print(f'  log_entries 表中有 {count} 条记录')
            conn.close()
        else:
            print("✗ log_entries 表创建失败!")
            print(f"当前可用的表: {updated_tables}")
        
    except Exception as e:
        print(f"创建日志表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_log_table()