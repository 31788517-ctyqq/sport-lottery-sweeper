import sqlite3
import os

def migrate_llm_providers_table():
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
        
        # Check if deleted_by column exists
        cursor.execute("PRAGMA table_info(llm_providers)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'deleted_by' not in column_names:
            print("Adding deleted_by column to llm_providers table...")
            cursor.execute("ALTER TABLE llm_providers ADD COLUMN deleted_by INTEGER")
            conn.commit()
            print("deleted_by column added successfully!")
        else:
            print("deleted_by column already exists.")
            
        # Also check if is_deleted and deleted_at columns exist (from SoftDeleteMixin)
        if 'is_deleted' not in column_names:
            print("Adding is_deleted column to llm_providers table...")
            cursor.execute("ALTER TABLE llm_providers ADD COLUMN is_deleted BOOLEAN DEFAULT 0")
            conn.commit()
            print("is_deleted column added successfully!")
        else:
            print("is_deleted column already exists.")
            
        if 'deleted_at' not in column_names:
            print("Adding deleted_at column to llm_providers table...")
            cursor.execute("ALTER TABLE llm_providers ADD COLUMN deleted_at DATETIME")
            conn.commit()
            print("deleted_at column added successfully!")
        else:
            print("deleted_at column already exists.")
        
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f'Error migrating LLM providers table: {e}')

if __name__ == '__main__':
    migrate_llm_providers_table()