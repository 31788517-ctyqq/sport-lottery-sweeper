#!/usr/bin/env python3
import sqlite3
import sys

def main():
    db_path = "sport_lottery.db"
    print(f"Checking database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if roles table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        tables = cursor.fetchall()
        print(f"Roles table exists: {tables}")
        
        if tables:
            cursor.execute("SELECT * FROM roles LIMIT 5")
            rows = cursor.fetchall()
            print(f"Rows in roles table: {rows}")
            if not rows:
                print("Table is empty.")
        else:
            print("Roles table does NOT exist.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()