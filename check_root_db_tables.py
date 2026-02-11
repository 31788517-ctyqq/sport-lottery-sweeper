#!/usr/bin/env python3
import sqlite3
import sys

def main():
    db_path = "sport_lottery.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print(f"Existing tables in {db_path}:")
        for t in tables:
            print(f"  - {t[0]}")
        
        # Check specifically for roles table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        roles_table = cursor.fetchone()
        if roles_table:
            print("\n✓ 'roles' table exists")
            # Check its structure
            cursor.execute("PRAGMA table_info(roles)")
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"    {col[1]} ({col[2]})")
        else:
            print("\n✗ 'roles' table does NOT exist")
            
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()