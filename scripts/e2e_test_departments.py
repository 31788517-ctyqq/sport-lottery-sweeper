#!/usr/bin/env python3
"""
Simple end-to-end API test for departments endpoints.
Run after the backend is running on http://127.0.0.1:8000
"""
import time
import json
import urllib.request
import urllib.error
from datetime import datetime

BASE = 'http://127.0.0.1:8000/api/v1'
HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}
TOKEN = None


def request(method, path, data=None, params=None):
    url = BASE + path
    if params:
        qs = '&'.join(f"{k}={v}" for k, v in params.items())
        url = url + ('?' + qs)
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode('utf-8')
            if not raw:
                return None
            try:
                return json.loads(raw)
            except Exception:
                return raw
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
            print('HTTPError', e.code, body)
        except Exception:
            print('HTTPError', e.code)
        raise
    except Exception as e:
        raise


def wait_for_api(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            # check health endpoint to determine if server is ready
            r = request('GET', '/health/ready')
            print('API reachable')
            return True
        except Exception:
            print('Waiting for API...')
            time.sleep(1)
    return False


def get_tree():
    return request('GET', '/admin/departments', params={'tree': 'true'})


def login_and_set_token(username, password):
    global TOKEN, HEADERS
    try:
        resp = request('POST', '/auth/login', data={'username': username, 'password': password})
        # resp may be wrapped in {data: {...}} or direct
        if isinstance(resp, dict) and 'data' in resp:
            token = resp['data'].get('access_token')
        else:
            token = resp.get('access_token')
        if not token:
            raise RuntimeError('no access_token in login response')
        TOKEN = token
        HEADERS['Authorization'] = f'Bearer {TOKEN}'
        print('Logged in, token set')
        return True
    except Exception as e:
        print('Login failed:', e)
        return False


def create_dept(name):
    payload = {
        'name': name,
        'parent_id': None,
        'description': 'e2e test',
        'leader_id': None,
        'sort_order': 100,
        'status': True
    }
    return request('POST', '/admin/departments', data=payload)


def update_dept(dept_id, data):
    return request('PUT', f'/admin/departments/{dept_id}', data=data)


def delete_dept(dept_id):
    return request('DELETE', f'/admin/departments/{dept_id}')


if __name__ == '__main__':
    ok = wait_for_api(timeout=45)
    if not ok:
        print('API did not become available within timeout')
        raise SystemExit(2)

    # login with provided test credentials
    if not login_and_set_token('admin', 'admin123'):
        print('Login failed, aborting E2E')
        raise SystemExit(3)

    print('\n-- GET tree (before) --')
    try:
        tree = get_tree()
        print(json.dumps(tree, ensure_ascii=False, indent=2))
    except Exception as e:
        print('GET tree failed:', e)

    name = f'e2e-test-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
    print(f'\n-- CREATE department: {name} --')
    try:
        created = create_dept(name)
        print(json.dumps(created, ensure_ascii=False, indent=2))
        # try to find id
        if isinstance(created, dict) and 'data' in created:
            payload = created['data']
        else:
            payload = created
        dept_id = payload.get('id') or payload.get('data', {}).get('id') or None
    except Exception as e:
        print('CREATE failed:', e)
        raise

    if not dept_id:
        # try to locate newly created by listing
        try:
            tree2 = get_tree()
            flat = []
            def walk(nodes):
                for n in nodes:
                    flat.append(n)
                    if n.get('children'):
                        walk(n['children'])
            if isinstance(tree2, dict) and 'data' in tree2:
                nodes = tree2['data']
            else:
                nodes = tree2
            walk(nodes or [])
            for n in flat:
                if n.get('name') == name:
                    dept_id = n.get('id')
                    break
        except Exception:
            pass

    print('Created id =', dept_id)

    if not dept_id:
        print('Failed to determine created department id; aborting update/delete steps')
    else:
        print(f'\n-- UPDATE department {dept_id} --')
        try:
            upd = update_dept(dept_id, {'name': name + '-updated', 'description': 'updated by e2e'})
            print(json.dumps(upd, ensure_ascii=False, indent=2))
        except Exception as e:
            print('UPDATE failed:', e)

        print(f'\n-- DELETE department {dept_id} --')
        try:
            d = delete_dept(dept_id)
            print(json.dumps(d, ensure_ascii=False, indent=2))
        except Exception as e:
            print('DELETE failed:', e)

    print('\n-- GET tree (after) --')
    try:
        tree_after = get_tree()
        print(json.dumps(tree_after, ensure_ascii=False, indent=2))
    except Exception as e:
        print('GET tree failed:', e)

    print('\nE2E script complete')
