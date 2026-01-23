import sqlite3

def check_database_tables():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('数据库中的表:')
    for table in tables:
        print(f"- {table[0]}")
    conn.close()

if __name__ == "__main__":
    check_database_tables()