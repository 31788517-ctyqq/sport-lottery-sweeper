#!/usr/bin/env python3
"""
淇backend鏁版嵁搴撶粨鏋?"""
import sqlite3
import os
import sys

def fix_roles_table():
    """淇backend鏁版嵁搴撲腑鐨剅oles琛ㄧ粨鏋?""
    print("=" * 60)
    print("淇backend鏁版嵁搴搑oles琛ㄧ粨鏋?)
    print("=" * 60)
    
    db_file = 'data/sport_lottery.db'
    
    if not os.path.exists(db_file):
        print(f"[ERROR] 鏁版嵁搴撴枃浠朵笉瀛樺湪: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"淇鏁版嵁搴? {db_file}")
        
        # 鑾峰彇褰撳墠琛ㄧ粨鏋?        cursor.execute('PRAGMA table_info(roles)')
        current_columns = cursor.fetchall()
        current_column_names = [col[1] for col in current_columns]
        
        print(f"褰撳墠roles琛ㄧ粨鏋?({len(current_columns)} 鍒?:")
        for col in current_columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 鏈熸湜鐨勮〃缁撴瀯锛堟牴鎹ā鍨嬪畾涔夛級
        expected_columns = [
            ('id', 'INTEGER', 'PRIMARY KEY'),
            ('name', 'VARCHAR(100)', 'NOT NULL'),
            ('description', 'TEXT', ''),
            ('permissions', 'TEXT', ''),
            ('status', 'BOOLEAN', 'DEFAULT 1'),
            ('sort_order', 'INTEGER', 'DEFAULT 0'),
            ('created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP'),
            ('deleted_at', 'DATETIME', '')
        ]
        
        print(f"\n鏈熸湜鐨剅oles琛ㄧ粨鏋?({len(expected_columns)} 鍒?:")
        for name, type_, extra in expected_columns:
            print(f"  {name} ({type_}) {extra}")
        
        # 妫€鏌ョ己澶辩殑鍒?        missing_columns = []
        for name, type_, extra in expected_columns:
            if name not in current_column_names:
                missing_columns.append((name, type_, extra))
        
        if not missing_columns:
            print(f"\nSUCCESS roles琛ㄧ粨鏋勬纭紝鏃犻渶淇")
            conn.close()
            return True
        
        print(f"\n缂哄け {len(missing_columns)} 鍒?")
        for name, type_, extra in missing_columns:
            print(f"  {name} ({type_})")
        
        # 鍒涘缓鏂拌〃骞惰縼绉绘暟鎹?        print(f"\n寮€濮嬩慨澶嶈〃缁撴瀯...")
        
        # 鍒涘缓涓存椂琛?        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            permissions TEXT,
            status BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME
        )
        ''')
        
        # 杩佺Щ鐜版湁鏁版嵁
        cursor.execute('''
        INSERT INTO roles_new (id, name, description, status, sort_order, created_at, updated_at)
        SELECT id, name, description, CASE WHEN is_active = 1 THEN 1 ELSE 0 END, 0, created_at, updated_at
        FROM roles
        ''')
        
        # 鍒犻櫎鏃ц〃
        cursor.execute('DROP TABLE roles')
        
        # 閲嶅懡鍚嶆柊琛?        cursor.execute('ALTER TABLE roles_new RENAME TO roles')
        
        conn.commit()
        
        print(f"\nSUCCESS roles琛ㄧ粨鏋勪慨澶嶅畬鎴?)
        
        # 楠岃瘉淇缁撴灉
        cursor.execute('PRAGMA table_info(roles)')
        fixed_columns = cursor.fetchall()
        
        print(f"\n淇鍚庣殑roles琛ㄧ粨鏋?({len(fixed_columns)} 鍒?:")
        for col in fixed_columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] 淇澶辫触: {e}")
        import traceback
        traceback.print_exc()
        return False

def fill_roles_data():
    """濉厖roles琛ㄦ暟鎹?""
    print("\n" + "=" * 60)
    print("濉厖roles琛ㄦ暟鎹?)
    print("=" * 60)
    
    db_file = 'data/sport_lottery.db'
    
    if not os.path.exists(db_file):
        print(f"[ERROR] 鏁版嵁搴撴枃浠朵笉瀛樺湪: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 榛樿瑙掕壊鏁版嵁
        default_roles = [
            ("admin", "绯荤粺绠＄悊鍛橈紝鎷ユ湁鏈€楂樻潈闄?, None, 1, 1),
            ("user", "鏅€氱敤鎴凤紝鎷ユ湁鍩烘湰鏉冮檺", None, 1, 2),
            ("analyst", "鏁版嵁鍒嗘瀽甯堬紝鍙互鏌ョ湅鍜屽垎鏋愭暟鎹?, None, 1, 3),
            ("operator", "鎿嶄綔鍛橈紝鍙互鎵ц鏃ュ父鎿嶄綔", None, 1, 4)
        ]
        
        inserted_count = 0
        for role_name, description, permissions, status, sort_order in default_roles:
            # 妫€鏌ユ槸鍚﹀凡瀛樺湪
            cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"  [INFO] 瑙掕壊 '{role_name}' 宸插瓨鍦紝璺宠繃")
            else:
                cursor.execute('''
                INSERT INTO roles (name, description, permissions, status, sort_order)
                VALUES (?, ?, ?, ?, ?)
                ''', (role_name, description, permissions, status, sort_order))
                inserted_count += 1
                print(f"  SUCCESS 鎻掑叆瑙掕壊: '{role_name}'")
        
        conn.commit()
        
        if inserted_count > 0:
            print(f"\nSUCCESS 鎴愬姛鎻掑叆 {inserted_count} 涓柊瑙掕壊")
        else:
            print(f"\n[INFO] 鎵€鏈夐粯璁よ鑹插凡瀛樺湪锛屾棤闇€鎻掑叆")
        
        # 楠岃瘉缁撴灉
        cursor.execute('SELECT COUNT(*) FROM roles')
        final_count = cursor.fetchone()[0]
        print(f"roles琛ㄧ幇鍦ㄥ叡鏈?{final_count} 涓鑹?)
        
        cursor.execute('SELECT id, name, description, status FROM roles')
        rows = cursor.fetchall()
        for row in rows:
            status_text = "婵€娲? if row[3] else "绂佺敤"
            print(f"  ID: {row[0]}, 鍚嶇О: {row[1]}, 鎻忚堪: {row[2]}, 鐘舵€? {status_text}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] 濉厖鏁版嵁澶辫触: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("淇backend鏁版嵁搴?)
    print("=" * 60)
    
    # 淇roles琛ㄧ粨鏋?    if not fix_roles_table():
        print("\n[ERROR] 琛ㄧ粨鏋勪慨澶嶅け璐ワ紝閫€鍑?)
        return 1
    
    # 濉厖roles琛ㄦ暟鎹?    if not fill_roles_data():
        print("\n[ERROR] 鏁版嵁濉厖澶辫触锛岄€€鍑?)
        return 1
    
    print("\n" + "=" * 60)
    print("SUCCESS 鏁版嵁搴撲慨澶嶅畬鎴愶紒")
    print("=" * 60)
    print("\n寤鸿: 閲嶅惎鍚庣鏈嶅姟鍚庢祴璇曠櫥褰曞姛鑳?)
    print("娉ㄦ剰: 鍚庣浣跨敤鐨勬槸 data/sport_lottery.db 鏂囦欢")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
