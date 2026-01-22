import sqlite3
import datetime
import json

def fix_admin_user():
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    print("检查admin用户...")
    
    # 1. 检查created_at和updated_at
    c.execute("SELECT username, created_at, updated_at FROM users WHERE username='admin'")
    admin = c.fetchone()
    if not admin:
        print("❌ admin用户不存在")
        return False
    
    username = admin[0]
    created_at = admin[1]
    updated_at = admin[2]
    
    print(f"用户名: {username}")
    print(f"created_at: {created_at}")
    print(f"updated_at: {updated_at}")
    
    # 修复datetime字段
    now = datetime.datetime.now().isoformat()
    if created_at == 'datetime("now")' or not created_at:
        c.execute("UPDATE users SET created_at = ? WHERE username = 'admin'", (now,))
        print(f"✅ 修复created_at: {created_at} -> {now}")
    else:
        try:
            datetime.datetime.fromisoformat(created_at)
            print(f"✅ created_at格式正确")
        except:
            c.execute("UPDATE users SET created_at = ? WHERE username = 'admin'", (now,))
            print(f"✅ 修复created_at: {created_at} -> {now}")
    
    if updated_at == 'datetime("now")' or not updated_at:
        c.execute("UPDATE users SET updated_at = ? WHERE username = 'admin'", (now,))
        print(f"✅ 修复updated_at: {updated_at} -> {now}")
    else:
        try:
            datetime.datetime.fromisoformat(updated_at)
            print(f"✅ updated_at格式正确")
        except:
            c.execute("UPDATE users SET updated_at = ? WHERE username = 'admin'", (now,))
            print(f"✅ 修复updated_at: {updated_at} -> {now}")
    
    # 2. 修复notification_preferences
    c.execute("SELECT notification_preferences FROM users WHERE username='admin'")
    pref_value = c.fetchone()[0]
    print(f"notification_preferences原值: {pref_value}")
    
    new_pref = "{}"
    if pref_value:
        try:
            parsed = json.loads(pref_value)
            new_pref = json.dumps(parsed)
            print(f"✅ notification_preferences是有效JSON")
        except json.JSONDecodeError:
            print(f"❌ notification_preferences不是有效JSON，设置为空字典")
            new_pref = "{}"
    else:
        print(f"notification_preferences为空，设置为空字典")
        new_pref = "{}"
    
    c.execute("UPDATE users SET notification_preferences = ? WHERE username = 'admin'", (new_pref,))
    
    # 3. 检查其他可能的datetime字段
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    datetime_cols = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        if 'DATE' in col_type or 'TIME' in col_type or 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
            datetime_cols.append(col_name)
    
    print(f"\n检查所有日期时间字段:")
    for col in datetime_cols:
        if col not in ['created_at', 'updated_at']:
            c.execute(f"SELECT {col} FROM users WHERE username='admin'")
            value = c.fetchone()[0]
            print(f"  {col}: {value}")
            if value:
                try:
                    dt = datetime.datetime.fromisoformat(value)
                    print(f"    ✅ 格式正确")
                except:
                    print(f"    ⚠️  格式可能有问题")
    
    conn.commit()
    
    # 验证修复
    print(f"\n验证修复结果:")
    c.execute("SELECT username, created_at, updated_at, notification_preferences FROM users WHERE username='admin'")
    fixed = c.fetchone()
    print(f"用户名: {fixed[0]}")
    print(f"created_at: {fixed[1]} (可解析: {datetime.datetime.fromisoformat(fixed[1])})")
    print(f"updated_at: {fixed[2]} (可解析: {datetime.datetime.fromisoformat(fixed[2])})")
    print(f"notification_preferences: {fixed[3]} (有效JSON: {json.loads(fixed[3])})")
    
    conn.close()
    print("\n✅ admin用户修复完成")
    return True

if __name__ == "__main__":
    fix_admin_user()