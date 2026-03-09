import requests
import json

def test_task_monitor_api():
    base_url = "http://localhost:8000"
    
    print("Testing Task Monitor API...")
    
    # 测试获取任务执行列表
    try:
        response = requests.get(f"{base_url}/api/v1/task-monitor/executions?page=1&page_size=10")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")  # 只打印前500个字符
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ API is responding correctly with JSON data")
                print(f"  Total items: {data.get('data', {}).get('total', 'N/A')}")
            except:
                print("✗ Response is not valid JSON")
        else:
            print("✗ API returned non-200 status")
    except Exception as e:
        print(f"✗ Error connecting to API: {str(e)}")
        
    # 测试获取实时概览
    try:
        response = requests.get(f"{base_url}/api/v1/task-monitor/realtime/overview")
        print(f"\nRealtime Overview Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ Realtime Overview API is working")
            except:
                print("✗ Realtime Overview Response is not valid JSON")
        else:
            print("✗ Realtime Overview API returned non-200 status")
    except Exception as e:
        print(f"✗ Error connecting to Realtime Overview API: {str(e)}")


if __name__ == "__main__":
    test_task_monitor_api()