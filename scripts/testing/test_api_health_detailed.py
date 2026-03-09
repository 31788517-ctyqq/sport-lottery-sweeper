import requests
import time

def test_api_health():
    # 测试API健康状态
    task_url = "http://localhost:3000/api/admin/crawler/tasks/32"
    
    print("测试API健康状态...")
    print("="*60)
    
    try:
        print("正在获取任务详情...")
        response = requests.get(task_url)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ API正常运行")
        else:
            print("❌ API存在问题")
            
    except Exception as e:
        print(f"❌ API请求失败: {e}")
    
    print("="*60)

if __name__ == "__main__":
    test_api_health()