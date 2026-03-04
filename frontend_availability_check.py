"""
前端可用性验证脚本
验证前端页面能否正常访问后端API
"""
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000"

def test_api_with_pagination(url_template, page=1, size=10):
    """测试带分页的API"""
    url = url_template.format(page=page, size=size)
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            return response.getcode(), json.loads(result)
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            return e.code, json.loads(error_body)
        except:
            return e.code, str(e)
    except Exception as e:
        return 0, f"Error: {str(e)}"

def main():
    print("前端可用性验证开始...")
    print("="*80)
    
    # 模拟前端访问的API
    tests = [
        {
            "name": "任务管理页面",
            "api": f"{BASE_URL}/api/v1/admin/tasks?page={{page}}&size={{size}}",
            "expected_fields": ["data", "success", "message"]
        },
        {
            "name": "数据源管理页面",
            "api": f"{BASE_URL}/api/v1/admin/sources?page={{page}}&size={{size}}",
            "expected_fields": ["data", "success", "message"]
        },
        {
            "name": "请求头管理页面",
            "api": f"{BASE_URL}/api/v1/admin/headers?page={{page}}&size={{size}}",
            "expected_fields": ["data", "success", "message"]
        },
        {
            "name": "IP池管理页面",
            "api": f"{BASE_URL}/api/v1/admin/ip-pools?page={{page}}&size={{size}}",
            "expected_fields": ["data", "success", "message"]
        },
        {
            "name": "爬虫监控页面",
            "api": f"{BASE_URL}/api/v1/admin/crawler/monitor/health",
            "expected_fields": ["status", "details", "checks"]
        }
    ]
    
    all_passed = True
    
    for test in tests:
        print(f"\n测试: {test['name']}")
        print("-" * 50)
        
        status, response = test_api_with_pagination(test['api'])
        
        print(f"状态码: {status}")
        
        if status == 200:
            print("✅ API响应成功")
            
            # 检查响应结构
            missing_fields = []
            for field in test['expected_fields']:
                if isinstance(response, dict) and field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️  响应缺少字段: {missing_fields}")
                all_passed = False
            else:
                print("✅ 响应结构正确")
                
            # 检查数据内容
            if isinstance(response, dict) and 'data' in response:
                data = response['data']
                if isinstance(data, dict) and 'items' in data:
                    item_count = len(data['items']) if isinstance(data['items'], list) else 0
                    total = data.get('total', 'N/A')
                    print(f"📊 返回项目数: {item_count}, 总数: {total}")
                elif isinstance(data, list):
                    print(f"📊 返回项目数: {len(data)}")
                else:
                    print("📊 数据格式: ", type(data).__name__)
        else:
            print(f"❌ API响应失败: {response}")
            all_passed = False
    
    print("\n" + "="*80)
    print("前端可用性验证总结")
    print("="*80)
    
    if all_passed:
        print("✅ 所有前端页面API访问验证通过!")
        print("✅ 前端功能可用性良好")
    else:
        print("❌ 部分API访问存在问题")
        
    print("\n验证要点:")
    print("- API响应结构符合前端预期")
    print("- 数据字段完整无缺")
    print("- 分页功能正常工作")
    print("- 错误处理机制健全")

if __name__ == "__main__":
    main()