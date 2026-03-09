import sqlite3
import os

def check_admin_user_full():
    """检查admin用户的完整信息"""
    db_path = 'data/sport_lottery.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取admin用户的完整信息
        cursor.execute("SELECT * FROM users WHERE username = 'admin';")
        columns = [description[0] for description in cursor.description]
        result = cursor.fetchone()
        
        if result:
            print("admin用户完整信息:")
            for i, col in enumerate(columns):
                print(f"  {col}: {result[i]}")
        else:
            print("users表中没有找到admin用户")
            
        conn.close()
        
    except Exception as e:
        print(f"检查admin用户时出错: {e}")

if __name__ == "__main__":
    check_admin_user_full()