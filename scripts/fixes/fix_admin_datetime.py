import sqlite3
import datetime

conn = sqlite3.connect('sport_lottery.db')
c = conn.cursor()

# 获取当前时间
now = datetime.datetime.now().isoformat()
print(f"当前时间: {now}")

# 更新admin用户的created_at和updated_at
c.execute("UPDATE users SET created_at = ?, updated_at = ? WHERE username = 'admin'", (now, now))
print(f"更新了 {c.rowcount} 行")

# 验证更新
c.execute("SELECT username, created_at, updated_at FROM users WHERE username='admin'")
admin = c.fetchone()
if admin:
    print(f"更新后:")
    print(f"  用户名: {admin[0]}")
    print(f"  created_at: {admin[1]}")
    print(f"  updated_at: {admin[2]}")

conn.commit()
conn.close()
print("✅ 修复完成")