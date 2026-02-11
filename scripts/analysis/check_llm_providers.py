import sqlite3
import os

def check_llm_providers():
    db_path = 'sport_lottery.db'
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
        
        # Count records
        cursor.execute('SELECT COUNT(*) FROM llm_providers')
        count = cursor.fetchone()[0]
        print(f'LLM Providers count: {count}')
        
        if count > 0:
            cursor.execute('SELECT id, name, provider_type FROM llm_providers LIMIT 5')
            rows = cursor.fetchall()
            print('Sample data:')
            for row in rows:
                print(f'  {row}')
        else:
            print('No LLM provider records found.')
            
        conn.close()
        
    except Exception as e:
        print(f'Error checking LLM providers: {e}')

if __name__ == '__main__':
    check_llm_providers()