import requests
import json
import time

def test_batch_delete_after_restart():
    print("等待服务重启完成...")
    time.sleep(5)  # 等待服务重启
    
    print("\n开始测试批量删除功能...")
    
    # 首先获取一些任务
    print("\n1. 获取任务列表...")
    try:
        response = requests.get('http://localhost:3000/api/admin/crawler/tasks?page=1&size=5')
        print(f"   任务列表获取状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   返回任务数量: {len(data.get('data', {}).get('items', []))}")
            print(f"   总任务数: {data.get('data', {}).get('total', 0)}")
            
            # 获取前几个任务ID进行测试
            items = data.get('data', {}).get('items', [])
            if len(items) > 0:
                test_ids = [item['id'] for item in items[:2]]  # 取前两个任务ID
                print(f"   选择任务ID进行批量删除测试: {test_ids}")
                
                # 测试批量删除API
                print("\n2. 测试批量删除API...")
                url = 'http://localhost:3000/api/admin/crawler/tasks/batch-delete'
                headers = {'Content-Type': 'application/json'}
                payload = {'ids': test_ids}
                
                print(f"   发送请求到: {url}")
                print(f"   请求头: {headers}")
                print(f"   请求体: {json.dumps(payload)}")
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                print(f"   响应状态码: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print("   ✓ 批量删除成功!")
                        print(f"   ✓ 删除了 {result['data']['deleted_count']} 个任务")
                    else:
                        print(f"   × 批量删除失败: {result.get('message')}")
                else:
                    print(f"   × 批量删除失败，状态码: {response.status_code}")
                    
                    # 检查是否仍是task_ids问题
                    if "task_ids不能为空" in response.text:
                        print("   × 错误: 服务可能仍未重启或适配器未正确处理参数")
            else:
                print("   没有找到任何任务进行删除测试")
        else:
            print(f"   获取任务列表失败: {response.text}")
    except Exception as e:
        print(f"   测试过程中出错: {e}")

def check_service_status():
    print("\n3. 检查服务状态...")
    try:
        response = requests.get('http://localhost:3000/api/admin/crawler/tasks/statistics')
        print(f"   统计API状态: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ 服务运行正常")
        else:
            print(f"   × 服务可能未运行，状态码: {response.status_code}")
    except Exception as e:
        print(f"   × 服务检查失败: {e}")

if __name__ == "__main__":
    test_batch_delete_after_restart()
    check_service_status()