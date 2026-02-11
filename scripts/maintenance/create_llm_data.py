import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 插入OpenAI提供商
cursor.execute("""
INSERT INTO llm_providers (
    name, provider_type, api_key, base_url, default_model,
    enabled, priority, max_requests_per_minute, timeout_seconds, 
    health_status, total_requests, successful_requests, failed_requests, 
    total_cost, monthly_cost, rate_limit_strategy, created_at, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'OpenAI',
    'openai',
    'sk-test-key',
    'https://api.openai.com/v1',
    'gpt-4',
    1,
    1,
    100,
    30,
    'healthy',
    0,
    0,
    0,
    0,
    0,
    'default',
    now,
    now
))

conn.commit()
cursor.execute('SELECT COUNT(*) FROM llm_providers')
count = cursor.fetchone()[0]
print(f'LLM Providers created: {count}')

conn.close()