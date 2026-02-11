import requests
import json

def check_field_types():
    try:
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=1')
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                log_entry = data[0]
                print('API日志字段类型详细验证：')
                print('='*50)
                
                # 检查LogResponse模型的所有字段
                expected_fields = [
                    ('id', int),
                    ('timestamp', str),
                    ('level', str),
                    ('module', str),
                    ('message', str),
                    ('user_id', (type(None), int)),
                    ('ip_address', (type(None), str)),
                    ('user_agent', (type(None), str)),
                    ('session_id', (type(None), str)),
                    ('request_path', (type(None), str)),
                    ('response_status', (type(None), int)),
                    ('duration_ms', (type(None), int)),
                    ('extra_data', (type(None), str)),
                    ('created_at', (type(None), str))
                ]
                
                all_correct = True
                for field_name, expected_type in expected_fields:
                    actual_value = log_entry.get(field_name)
                    actual_type = type(actual_value)
                    
                    is_correct = isinstance(actual_value, expected_type)
                    status = '✓' if is_correct else '✗'
                    
                    if not is_correct:
                        all_correct = False
                    
                    print(f'{status} {field_name}: {actual_type.__name__} (期望: {expected_type.__name__ if isinstance(expected_type, type) else str(expected_type)}) = {repr(actual_value)[:60]}')
                
                if all_correct:
                    print("\n所有字段类型都正确 ✓")
                else:
                    print("\n存在字段类型错误 ✗")
            else:
                print('没有获取到数据')
        else:
            print(f'API请求失败: {response.status_code}')
            print(response.text[:500])
    except Exception as e:
        print(f'请求异常: {e}')

if __name__ == "__main__":
    check_field_types()