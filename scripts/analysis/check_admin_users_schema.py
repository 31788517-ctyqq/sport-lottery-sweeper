"""
检查admin_users表的结构
"""
import sqlite3
import os

# 获取数据库路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "sport_lottery.db")

def check_admin_users_schema():
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询admin_users表的完整结构
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = cursor.fetchall()
        
        print("admin_users表结构详情:")
        print("序号 | 名称 | 类型 | 非空 | 默认值 | 主键")
        print("-" * 60)
        for i, col in enumerate(columns):
            cid, name, type_, notnull, default, pk = col
            print(f"{cid:2d}   | {name:20s} | {type_:10s} | {'是' if notnull else '否':2s} | {str(default):10s} | {'是' if pk else '否':1s}")
        
        print(f"\n总共有 {len(columns)} 个字段")
        
        # 查看表中是否已有数据
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        count = cursor.fetchone()[0]
        print(f"admin_users表中现有记录数: {count}")
        
        if count > 0:
            print("\n前几条记录的信息:")
            cursor.execute("SELECT * FROM admin_users LIMIT 5")
            records = cursor.fetchall()
            for i, record in enumerate(records):
                print(f"  记录 {i+1}: {record}")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_admin_users_schema()