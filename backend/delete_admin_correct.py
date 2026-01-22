import sqlite3

def delete_admin_user():
    """删除admin用户"""
    # 连接到数据库
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 删除admin用户
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} admin user(s)")
        
        # 提交更改
        conn.commit()
        
    except Exception as e:
        print(f"Error deleting admin user: {e}")
        conn.rollback()
    finally:
        # 关闭连接
        conn.close()

if __name__ == "__main__":
    delete_admin_user()