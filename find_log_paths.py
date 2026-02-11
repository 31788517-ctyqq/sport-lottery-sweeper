import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:8001/openapi.json', timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    
    # 查找日志相关的路径
    log_paths = []
    for path in data['paths'].keys():
        if 'log' in path.lower() or 'Log' in path:
            log_paths.append(path)
    
    print('发现的日志相关路径:')
    for path in sorted(log_paths):
        print(f'  {path}')
        
    if not log_paths:
        print('  未发现日志相关路径')
        
    # 也检查是否有system路径
    system_paths = []
    for path in data['paths'].keys():
        if '/system/' in path:
            system_paths.append(path)
            
    print('\n发现的系统相关路径:')
    for path in sorted(system_paths):
        print(f'  {path}')
        
    # 检查是否有admin路径
    admin_paths = []
    for path in data['paths'].keys():
        if '/admin/' in path and ('log' in path.lower() or 'Log' in path):
            admin_paths.append(path)
            
    print('\n发现的管理日志相关路径:')
    for path in sorted(admin_paths):
        print(f'  {path}')
        
except Exception as e:
    print(f'获取OpenAPI定义失败: {e}')