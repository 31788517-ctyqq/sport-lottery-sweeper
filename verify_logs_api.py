import urllib.request
import json

def test_log_endpoint(path, description):
    try:
        req = urllib.request.Request(f'http://localhost:3000{path}')
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req)
        print(f'{description}: {response.getcode()} - SUCCESS')
        return True
    except Exception as e:
        print(f'{description}: ERROR - {e}')
        return False

test_log_endpoint('/admin/logs', 'Frontend logs page')
test_log_endpoint('/api/v1/admin/system/logs/db/statistics', 'Log statistics API')