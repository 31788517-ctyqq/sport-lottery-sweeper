import sqlite3
import datetime

conn = sqlite3.connect('sport_lottery.db')
c = conn.cursor()

# 检查admin用户
c.execute("SELECT username, created_at, updated_at FROM users WHERE username='admin'")
admin = c.fetchone()
if admin:
    print(f"用户名: {admin[0]}")
    print(f"created_at: {admin[1]}")
    print(f"updated_at: {admin[2]}")
    
    # 验证可以解析
    try:
        dt_created = datetime.datetime.fromisoformat(admin[1])
        print(f"✅ created_at 可以解析: {dt_created}")
    except Exception as e:
        print(f"❌ created_at 解析错误: {e}")
        
    try:
        dt_updated = datetime.datetime.fromisoformat(admin[2])
        print(f"✅ updated_at 可以解析: {dt_updated}")
    except Exception as e:
        print(f"❌ updated_at 解析错误: {e}")

# 检查密码哈希
c.execute("SELECT password_hash FROM users WHERE username='admin'")
hash_row = c.fetchone()
if hash_row:
    hash_val = hash_row[0]
    print(f"\n密码哈希: {hash_val[:60]}...")
    print(f"哈希长度: {len(hash_val)}")
    print(f"是否是bcrypt格式: {hash_val.startswith('$2')}")

conn.close()