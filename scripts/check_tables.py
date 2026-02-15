import sqlite3
import os

# 数据库文件路径
db_path = os.path.join('data', 'data/sport_lottery.db')

def check_tables():
    """检查数据库中的所有表"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
            
        conn.close()
    except Exception as e:
        print(f"查询出错: {e}")

if __name__ == "__main__":
    check_tables()