import requests
import time

# 等待后端服务启动
print("Waiting for backend to start...")
time.sleep(8)

# 测试API
print("Testing API endpoint...")
try:
    response = requests.get('http://localhost:8000/api/v1/caipiao-data/?skip=0&limit=20')
    print('Status Code:', response.status_code)
    print('Response:', response.text[:500])
    
    if response.status_code == 200:
        print("✅ API is working correctly!")
    else:
        print("❌ API is not working as expected.")
        
except Exception as e:
    print(f"❌ Error occurred: {e}")