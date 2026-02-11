import requests
import json

response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=1')
print(f'Status Code: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    if data and len(data) > 0:
        print('API日志数据结构（修复后）：')
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
        print()
        print('字段列表：', list(data[0].keys()))
        
        # 检查特定字段是否包含有意义的数据
        log_entry = data[0]
        print('\n详细字段验证：')
        print(f'- 时间戳: {log_entry.get("timestamp")}')
        print(f'- 级别: {log_entry.get("level")}')
        print(f'- 模块: {log_entry.get("module")}')
        print(f'- 消息: {log_entry.get("message")}')
        print(f'- 请求路径: {log_entry.get("request_path")}')
        print(f'- 响应状态: {log_entry.get("response_status")}')
        print(f'- 耗时(毫秒): {log_entry.get("duration_ms")}')
        print(f'- 额外数据: {log_entry.get("extra_data")}')
    else:
        print('没有获取到数据或数据为空')
        print('Response:', response.text[:500])
else:
    print('API请求失败')
    print('Response:', response.text[:500])