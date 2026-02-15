import sqlite3
import json
import os

def check_llm_providers_detailed():
    db_path = 'data/sport_lottery.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='llm_providers'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Table 'llm_providers' does not exist!")
            return
        
        # Get all columns and data
        cursor.execute('PRAGMA table_info(llm_providers)')
        columns = cursor.fetchall()
        print("Table columns:")
        for col in columns:
            print(f"  {col}")
        
        # Count records
        cursor.execute('SELECT COUNT(*) FROM llm_providers')
        count = cursor.fetchone()[0]
        print(f'\nLLM Providers count: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM llm_providers')
            rows = cursor.fetchall()
            print('\nAll data:')
            for i, row in enumerate(rows):
                print(f'Record {i+1}:')
                for j, col in enumerate(columns):
                    col_name = col[1]
                    col_value = row[j]
                    print(f'  {col_name}: {col_value}')
                print()
        else:
            print('No LLM provider records found.')
            
        conn.close()
        
    except Exception as e:
        print(f'Error checking LLM providers: {e}')

if __name__ == '__main__':
    check_llm_providers_detailed()