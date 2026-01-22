import sqlite3
import datetime

conn = sqlite3.connect('sport_lottery.db')
c = conn.cursor()

# 获取所有datetime/timestamp类型的列
c.execute("PRAGMA table_info(users)")
columns = c.fetchall()
datetime_cols = []
for col in columns:
    col_name = col[1]
    col_type = col[2].upper()
    if 'DATE' in col_type or 'TIME' in col_type or 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
        datetime_cols.append(col_name)

print(f"DateTime类型列: {datetime_cols}")

# 检查admin用户的这些列
c.execute(f"SELECT {', '.join(datetime_cols)} FROM users WHERE username='admin'")
admin_values = c.fetchone()

print("\nadmin用户的日期时间字段值:")
for i, col in enumerate(datetime_cols):
    value = admin_values[i]
    print(f"  {col}: {value}")
    if value:
        try:
            dt = datetime.datetime.fromisoformat(value)
            print(f"    ✅ 可以解析: {dt}")
        except Exception as e:
            print(f"    ❌ 解析错误: {e}")

conn.close()