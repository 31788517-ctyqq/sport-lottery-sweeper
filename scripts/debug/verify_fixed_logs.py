import urllib.request
import json

def test_endpoint(url, name):
    try:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req)
        print(f'{name}: {response.getcode()} - SUCCESS')
        return True
    except Exception as e:
        print(f'{name}: ERROR - {e}')
        return False

test_endpoint('http://localhost:8001/api/v1/admin/system/logs/db/statistics', 'Log Statistics API')