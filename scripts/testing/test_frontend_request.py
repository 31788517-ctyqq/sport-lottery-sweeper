import requests
import json

def test_frontend_request():
    print("=" * 70)
    print("测试前端API请求")
    print("=" * 70)
    
    # 模拟前端请求参数
    params = {
        'skip': 0,
        'limit': 50
    }
    
    # 测试API端点
    print("1. 测试API端点连通性...")
    try:
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api', params=params)
        print(f"   API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   返回记录数: {len(data)}")
            
            if data:
                print(f"   第一条记录示例:")
                first_record = data[0]
                print(f"     时间戳: {first_record.get('timestamp')}")
                print(f"     级别: {first_record.get('level')}")
                print(f"     请求路径: {first_record.get('request_path')}")
                print(f"     状态码: {first_record.get('response_status')}")
                print(f"     耗时: {first_record.get('duration_ms')}")
                print(f"     IP地址: {first_record.get('ip_address')}")
                print(f"     消息: {first_record.get('message')}")
            else:
                print("   没有返回任何数据")
        else:
            print(f"   API请求失败: {response.text}")
    except Exception as e:
        print(f"   API请求异常: {e}")
    
    print(f"\n2. 检查前端代理配置...")
    # 测试通过前端代理访问（如果前端代理配置正确）
    try:
        # 前端运行在3000端口，代理API请求到后端
        response = requests.get('http://localhost:3000/api/v1/admin/system/logs/db/api', params=params)
        print(f"   前端代理响应状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   通过前端代理返回记录数: {len(data)}")
        else:
            print(f"   前端代理请求失败，可能前端服务器未运行或代理配置错误")
    except Exception as e:
        print(f"   前端代理请求异常: {e}")
    
    print(f"\n3. 分析可能的问题:")
    print(f"   a) 前端可能有JavaScript错误导致页面渲染失败")
    print(f"   b) 前端代理配置可能仍然指向错误的后端端口")
    print(f"   c) 组件可能因为数据结构变化而无法正确渲染")
    print(f"   d) 前端可能需要清除缓存后重新加载")
    
    print(f"\n4. 建议排查步骤:")
    print(f"   a) 打开浏览器开发者工具(F12)，检查Console是否有JavaScript错误")
    print(f"   b) 检查Network选项卡，查看API请求是否成功")
    print(f"   c) 确认前端服务器已重启并应用了最新的更改")
    print(f"   d) 清除浏览器缓存并硬刷新页面(Ctrl+F5)")

if __name__ == "__main__":
    test_frontend_request()