import requests
import json

def test_task_monitor_api():
    base_url = "http://localhost:8000"
    
    print("详细测试任务监控API...")
    
    # 测试获取任务执行列表
    try:
        print("\n1. 测试获取任务执行列表...")
        response = requests.get(f"{base_url}/api/v1/task-monitor/executions?page=1&page_size=10")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头部: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                
                # 检查响应格式
                if 'code' in data and data['code'] == 200:
                    print("   ✓ 响应格式正确: 包含code字段且值为200")
                elif 'success' in data and data['success'] is True:
                    print("   ⚠️ 响应格式为success字段，与预期略有不同")
                else:
                    print(f"   ✗ 响应格式不符合预期: {data.keys()}")
                    
                if 'data' in data:
                    print(f"   ✓ 包含data字段，总数: {data['data'].get('total', 'N/A')}")
                else:
                    print("   ✗ 缺少data字段")
            except ValueError as e:
                print(f"   ✗ 响应不是有效的JSON: {e}")
                print(f"   原始响应: {response.text[:300]}...")
        else:
            print(f"   ✗ API返回非200状态: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ✗ 请求异常: {str(e)}")
        
    # 测试获取实时概览
    try:
        print("\n2. 测试获取实时概览...")
        response = requests.get(f"{base_url}/api/v1/task-monitor/realtime/overview")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                
                if 'code' in data and data['code'] == 200:
                    print("   ✓ 响应格式正确: 包含code字段且值为200")
                elif 'success' in data and data['success'] is True:
                    print("   ⚠️ 响应格式为success字段，与预期略有不同")
                else:
                    print(f"   ✗ 响应格式不符合预期: {data.keys()}")
            except ValueError as e:
                print(f"   ✗ 响应不是有效的JSON: {e}")
        else:
            print(f"   ✗ API返回非200状态: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ✗ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_task_monitor_api()