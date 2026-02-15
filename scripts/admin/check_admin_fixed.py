import sqlite3
import datetime

conn = sqlite3.connect('data/sport_lottery.db')
c = conn.cursor()

# 先尝试修复
now = datetime.datetime.now().isoformat()
print(f"当前时间: {now}")

c.execute("UPDATE users SET created_at = ?, updated_at = ? WHERE username = 'admin'", (now, now))
conn.commit()
print(f"更新了 {c.rowcount} 行")

# 验证
c.execute("SELECT username, created_at, updated_at FROM users WHERE username='admin'")
admin = c.fetchone()
if admin:
    print(f"用户名: {admin[0]}")
    print(f"created_at: {admin[1]}")
    print(f"updated_at: {admin[2]}")
    
    # 尝试解析
    try:
        dt_created = datetime.datetime.fromisoformat(admin[1])
        print(f"created_at 可以解析: {dt_created}")
    except Exception as e:
        print(f"created_at 解析错误: {e}")
        
    try:
        dt_updated = datetime.datetime.fromisoformat(admin[2])
        print(f"updated_at 可以解析: {dt_updated}")
    except Exception as e:
        print(f"updated_at 解析错误: {e}")

conn.close()
print("完成")