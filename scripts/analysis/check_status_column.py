import sqlite3
import os

def check_status_column():
    # 检查数据库文件是否存在
    db_path = './data/sport_lottery.db'  # 使用正确的数据库路径
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询data_sources表结构
    try:
        cursor.execute("PRAGMA table_info(data_sources);")
        columns = cursor.fetchall()
        
        print("data_sources表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] == 1 else ''} - Default: {col[4]}")
        
        # 查询一些数据示例
        print("\n查询一些数据示例:")
        cursor.execute("SELECT id, name, status FROM data_sources LIMIT 5;")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID: {row[0]}, Name: {row[1]}, Status: {row[2]} (type: {type(row[2]).__name__})")
        
    except Exception as e:
        print(f"查询表结构失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_status_column()