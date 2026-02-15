import sqlite3
import datetime
import json

conn = sqlite3.connect('data/sport_lottery.db')
c = conn.cursor()

print("修复admin用户...")

# 修复created_at和updated_at
now = datetime.datetime.now().isoformat()
c.execute("UPDATE users SET created_at = ?, updated_at = ? WHERE username = 'admin'", (now, now))
print(f"更新datetime字段: {now}")

# 修复notification_preferences
c.execute("UPDATE users SET notification_preferences = '{}' WHERE username = 'admin'")
print("设置notification_preferences为{}")

conn.commit()

# 验证
c.execute("SELECT username, created_at, updated_at, notification_preferences FROM users WHERE username='admin'")
row = c.fetchone()
print(f"验证: 用户名={row[0]}, created_at={row[1]}, updated_at={row[2]}, notification_preferences={row[3]}")

conn.close()
print("✅ 修复完成")