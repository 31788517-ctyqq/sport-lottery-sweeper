import requests
import sys

try:
    r = requests.get('http://localhost:8000/api/v1/', timeout=5)
    print('Port 8000 status:', r.status_code)
except Exception as e:
    print('Port 8000 error:', e)

try:
    r = requests.get('http://localhost:8001/api/v1/', timeout=5)
    print('Port 8001 status:', r.status_code)
except Exception as e:
    print('Port 8001 error:', e)