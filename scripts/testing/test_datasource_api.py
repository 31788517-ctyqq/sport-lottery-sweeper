"""
数据源API测试脚本
用于验证数据源管理API端点是否正常工作
"""
import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("正在测试数据源管理API端点...")
    
    # 测试获取数据源列表（预期返回401，因为我们没有认证）
    try:
        response = requests.get(f"{base_url}/api/admin/v1/sources", 
                               params={"page": 1, "size": 10})
        print(f"获取数据源列表: 状态码 {response.status_code}")
        if response.status_code == 401:
            print("✅ 正确返回401未授权错误（需要认证）")
        elif response.status_code == 200:
            print("✅ 成功获取数据源列表")
            print(f"响应内容预览: {response.text[:200]}...")
        else:
            print(f"⚠️  unexpected status: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试健康检查端点
    try:
        response = requests.get(f"{base_url}/api/v1/admin/metrics/health")
        print(f"健康检查端点: 状态码 {response.status_code}")
        if response.status_code == 200:
            print("✅ 健康检查端点正常")
        else:
            print(f"⚠️ 健康检查端点返回非200状态: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查请求失败: {e}")
    
    # 测试API文档端点
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"API文档端点: 状态码 {response.status_code}")
        if response.status_code == 200:
            print("✅ API文档端点正常")
        else:
            print(f"⚠️ API文档端点返回非200状态: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档请求失败: {e}")
    
    print("\nAPI端点测试完成！")
    print("注意：数据源管理端点需要认证，因此会返回401错误，这是正常的。")


if __name__ == "__main__":
    test_api_endpoints()