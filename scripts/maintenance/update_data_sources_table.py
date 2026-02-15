import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cur = conn.cursor()

# Add missing columns
try:
    cur.execute('ALTER TABLE data_sources ADD COLUMN source_id VARCHAR(10)')
    print('Added source_id')
except Exception as e:
    print(f'source_id exists or error: {e}')

try:
    cur.execute('ALTER TABLE data_sources ADD COLUMN field_mapping TEXT')
    print('Added field_mapping')
except Exception as e:
    print(f'field_mapping exists or error: {e}')

try:
    cur.execute('ALTER TABLE data_sources ADD COLUMN update_frequency INTEGER DEFAULT 60')
    print('Added update_frequency')
except Exception as e:
    print(f'update_frequency exists or error: {e}')

try:
    cur.execute('ALTER TABLE data_sources ADD COLUMN last_error TEXT')
    print('Added last_error')
except Exception as e:
    print(f'last_error exists or error: {e}')

try:
    cur.execute('ALTER TABLE data_sources ADD COLUMN last_error_time DATETIME')
    print('Added last_error_time')
except Exception as e:
    print(f'last_error_time exists or error: {e}')

conn.commit()
conn.close()
print('Database updated successfully!')
