import sys
sys.path.insert(0, '.')
from backend.config import settings
print(f'SECRET_KEY: {settings.SECRET_KEY}')
print(f'SECRET_KEY type: {type(settings.SECRET_KEY)}')
if settings.SECRET_KEY:
    print(f'SECRET_KEY length: {len(settings.SECRET_KEY)}')
    print(f'SECRET_KEY encoded: {settings.SECRET_KEY.encode()[:32]}')
else:
    print('SECRET_KEY is None or empty')