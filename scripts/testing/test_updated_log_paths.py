import urllib.request
import json

# 测试不同路径组合
paths_to_test = [
    '/api/v1/admin/logs/system/logs/db/statistics',  # 如果注册到 /api/v1/admin 下，logs路由又有/system前缀
    '/api/v1/admin/system/logs/db/statistics',       # 前端当前使用的路径
    '/api/v1/admin/logs/db/statistics',              # 如果注册到 /api/v1/admin 下，logs路由直接处理 /db/statistics
    '/api/v1/admin/system/system/logs/db/statistics' # 之前的重复路径
]

print("正在测试更新后的日志API路径...")
print("="*60)

for path in paths_to_test:
    try:
        req = urllib.request.Request(f'http://localhost:8001{path}')
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req)
        print(f"{path:<50} -> {response.getcode()} (SUCCESS)")
        if path == '/api/v1/admin/logs/system/logs/db/statistics':
            # 尝试打印一些响应数据（但不一定会有很多数据）
            try:
                data = json.loads(response.read().decode('utf-8'))
                print(f"  Sample response keys: {list(data.keys())[:5]}")
            except:
                pass
    except urllib.error.HTTPError as e:
        print(f"{path:<50} -> {e.code} (FAILED)")
    except Exception as e:
        print(f"{path:<50} -> Error: {str(e)}")
    print("-" * 60)

print("\n测试完成")