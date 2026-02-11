import sqlite3
conn = sqlite3.connect('sport_lottery.db')
c = conn.cursor()
c.execute('UPDATE llm_providers SET provider_type = ''OPENAI'' WHERE provider_type = ''openai''')
updated_openai = c.rowcount
c.execute('UPDATE llm_providers SET provider_type = ''ALIBABA'' WHERE provider_type = ''alibaba''')
updated_alibaba = c.rowcount
conn.commit()
print(f'修复了 {updated_openai} 个 OPENAI 记录和 {updated_alibaba} 个 ALIBABA 记录')
conn.close()
