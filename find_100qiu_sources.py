import sqlite3

def find_100qiu_sources():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url FROM data_sources WHERE url LIKE '%100qiu%'")
    rows = cursor.fetchall()
    print('100qiu数据源:', rows)
    conn.close()

if __name__ == "__main__":
    find_100qiu_sources()