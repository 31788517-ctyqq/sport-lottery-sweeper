from backend.config import Settings
s=Settings()
print('DB URL', s.DATABASE_URL)
print('Async DB', s.ASYNC_DATABASE_URL)
