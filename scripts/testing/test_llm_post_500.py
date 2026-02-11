import requests
import json
import sys

url = 'http://localhost:8000/api/v1/llm-providers/'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NzA2NTk5ODgsInR5cGUiOiJhY2Nlc3MifQ.NZBCv1xwKcpWE-GvHlol-e-sa0T-xDYr_sESW_SI7Wg'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
data = {
    'name': 'Test Provider',
    'provider_type': 'openai',
    'api_key': 'sk-test1234567890',
    'description': 'Test description',
    'enabled': True,
    'priority': 5,
    'max_requests_per_minute': 60,
    'timeout_seconds': 30,
    'rate_limit_strategy': 'fixed_window'
}

try:
    print(f'POST {url}')
    response = requests.post(url, headers=headers, json=data)
    print(f'Status: {response.status_code}')
    print(f'Response headers: {dict(response.headers)}')
    print(f'Response body: {response.text}')
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)