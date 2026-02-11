"""
详细测试批量删除API功能
"""
import urllib.request
import urllib.error
import json

BACKEND_BASE_URL = "http://localhost:8000"

def test_batch_delete_api():
    """测试批量删除API"""
    print("测试批量删除API功能...")
    
    # 测试1: 使用正确格式的空数组
    url = f"{BACKEND_BASE_URL}/api/v1/admin/tasks/batch-delete"
    headers = {'Content-Type': 'application/json'}
    
    # 尝试删除空数组
    data = []
    req_data = json.dumps(data).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=req_data, method='POST', headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"空数组测试 - 状态码: {response.getcode()}")
            print(f"响应: {result[:200]}...")  # 只显示前200个字符
    except urllib.error.HTTPError as e:
        print(f"空数组测试 - 状态码: {e.code}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"错误响应: {error_body[:200]}...")
        except:
            print(f"错误详情: {e}")
    except Exception as e:
        print(f"空数组测试 - 错误: {e}")
    
    # 测试2: 使用正确格式的包含无效ID的数组
    data_with_ids = [1, 2, 3]
    req_data = json.dumps(data_with_ids).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=req_data, method='POST', headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"包含ID数组测试 - 状态码: {response.getcode()}")
            print(f"响应: {result[:200]}...")
    except urllib.error.HTTPError as e:
        print(f"包含ID数组测试 - 状态码: {e.code}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"错误响应: {error_body[:200]}...")
        except:
            print(f"错误详情: {e}")
    except Exception as e:
        print(f"包含ID数组测试 - 错误: {e}")

def test_api_routes():
    """测试API路由"""
    print("\n测试API路由注册...")
    
    # 获取API文档
    try:
        with urllib.request.urlopen(f"{BACKEND_BASE_URL}/docs", timeout=10) as response:
            if response.getcode() == 200:
                print("✅ API文档可访问")
                
                # 检查是否包含批量删除API
                content = response.read().decode('utf-8')
                if "batch-delete" in content.lower() or "batch delete" in content.lower():
                    print("✅ 批量删除API已注册")
                else:
                    print("ℹ️ 批量删除API可能未注册")
            else:
                print(f"❌ API文档不可访问，状态码: {response.getcode()}")
    except Exception as e:
        print(f"❌ 获取API文档失败: {e}")
    
    # 检查OpenAPI规范
    try:
        with urllib.request.urlopen(f"{BACKEND_BASE_URL}/openapi.json", timeout=10) as response:
            if response.getcode() == 200:
                openapi_spec = json.loads(response.read().decode('utf-8'))
                paths = openapi_spec.get('paths', {})
                
                batch_delete_found = False
                for path, methods in paths.items():
                    if 'batch-delete' in path:
                        print(f"✅ 批量删除API路径找到: {path}")
                        batch_delete_found = True
                        break
                
                if not batch_delete_found:
                    print("❌ 批量删除API路径未找到")
                    
                    # 输出所有任务相关的路径
                    print("🔍 任务相关路径:")
                    for path in sorted(paths.keys()):
                        if 'task' in path.lower():
                            print(f"  - {path}")
            else:
                print(f"❌ OpenAPI规范不可访问，状态码: {response.getcode()}")
    except Exception as e:
        print(f"❌ 获取OpenAPI规范失败: {e}")

if __name__ == "__main__":
    print("批量删除API详细测试")
    print("="*50)
    test_batch_delete_api()
    test_api_routes()
    print("="*50)
    print("测试完成!")