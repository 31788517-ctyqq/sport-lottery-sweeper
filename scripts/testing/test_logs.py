import requests

# Login
login_response = requests.post('http://localhost:8000/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = login_response.json()['data']['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test security logs - corrected path
response = requests.get('http://localhost:8000/api/v1/admin/system/logs/db/security?skip=0&limit=5', headers=headers)
print('Status:', response.status_code)
if response.status_code == 200:
    data = response.json()
    print('Response keys:', list(data.keys()))
    print('Total logs:', data.get('total', 'N/A'))
    print('Items count:', len(data.get('items', [])))
    if data.get('items'):
        print('First log sample:', data['items'][0])
else:
    print('Error response:', response.text)