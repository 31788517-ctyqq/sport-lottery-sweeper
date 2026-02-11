import requests
import json

def check_api_schema():
    try:
        response = requests.get("http://localhost:8001/openapi.json", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            print("API端点包含 'tasks' 的路径:")
            for path, methods in paths.items():
                if "task" in path.lower():
                    print(f"  {path}: {list(methods.keys())}")
                    
            # 检查是否有PUT /api/admin/crawler/tasks/{task_id}端点
            target_path = "/api/v1/crawler/tasks/{task_id}"
            if target_path in paths:
                methods = paths[target_path]
                if "put" in [method.lower() for method in methods.keys()]:
                    print(f"\n找到更新任务端点: {target_path} (PUT)")
                else:
                    print(f"\n未找到PUT方法在: {target_path}, 方法: {list(methods.keys())}")
            else:
                print(f"\n未找到端点: {target_path}")
                
            # 检查实际注册的路径（可能是适配器路径）
            for path, methods in paths.items():
                if "tasks" in path and "{task_id}" in path:
                    for method, details in methods.items():
                        if method.lower() == "put":
                            print(f"发现PUT端点: {path}")
                            print(f"  操作ID: {details.get('operationId', 'N/A')}")
                            
        else:
            print(f"获取API schema失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"检查API schema时出错: {e}")

if __name__ == "__main__":
    check_api_schema()