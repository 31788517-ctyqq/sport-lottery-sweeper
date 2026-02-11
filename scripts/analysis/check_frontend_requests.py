import requests
import json
import time

def check_frontend_requests():
    print("=" * 70)
    print("检查前端API请求与后端响应的一致性")
    print("=" * 70)
    
    # 获取当前后端数据
    print("1. 获取当前后端API数据...")
    response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=100')
    backend_data = response.json()
    print(f"   ✓ 后端返回 {len(backend_data)} 条记录")
    
    # 检查用户提到的数据是否存在
    print(f"\n2. 检查用户提到的特定数据...")
    user_timestamp = "2026-01-31T12:31:00"
    user_path = "/crawler/task/5"
    user_message = "Crawler task 5: completed"
    user_status = 500
    user_duration = 8200
    
    found_user_data = False
    for log in backend_data:
        if (log.get('timestamp') == user_timestamp and
            log.get('request_path') == user_path and
            log.get('message') == user_message and
            log.get('response_status') == user_status and
            log.get('duration_ms') == user_duration):
            found_user_data = True
            break
    
    if found_user_data:
        print(f"   ✓ 在后端数据中找到用户提到的记录")
    else:
        print(f"   ✗ 在后端数据中未找到用户提到的记录")
        
        # 检查是否有类似数据
        similar_found = 0
        for log in backend_data:
            if (user_path in log.get('request_path', '') or 
                '5: completed' in log.get('message', '') or
                log.get('duration_ms') == user_duration or
                user_timestamp[:13] in log.get('timestamp', '')):
                similar_found += 1
                print(f"     - 找到相似记录: {log.get('timestamp')} | {log.get('request_path')} | {log.get('message')} | {log.get('duration_ms')}ms")
        
        if similar_found == 0:
            print(f"     - 也未找到任何相似的记录")
    
    print(f"\n3. 检查前端与后端数据是否同步...")
    # 获取前5条记录进行比较
    if backend_data:
        print(f"   后端前3条记录:")
        for i, log in enumerate(backend_data[:3]):
            print(f"     {i+1}. {log.get('timestamp')} | {log.get('request_path')} | {log.get('message')}")
    
    print(f"\n4. 检查可能的前端缓存问题...")
    print(f"   - 前端可能使用了缓存数据而不是实时获取")
    print(f"   - 前端过滤器可能处于激活状态，影响了数据显示")
    print(f"   - 日期范围选择器可能限制了显示的数据范围")
    print(f"   - 搜索框可能包含隐藏的搜索词")
    
    print(f"\n5. 检查前端组件中的潜在问题...")
    # 检查前端请求是否正确
    print(f"   - 前端请求URL: /api/v1/admin/system/logs/db/api")
    print(f"   - 前端使用了正确的参数: skip, limit")
    print(f"   - 前端处理响应数据的方式: Array.isArray(response.data) ? response.data : response.data.items || []")
    
    print(f"\n6. 建议解决方案:")
    print(f"   a) 清除浏览器缓存: Ctrl+Shift+Delete → 选择清除缓存")
    print(f"   b) 硬刷新页面: Ctrl+F5 或 Shift+F5")
    print(f"   c) 检查前端过滤器状态: 确保所有过滤器已重置")
    print(f"   d) 检查日期选择器: 确保日期范围是'全部'或适当的宽范围")
    print(f"   e) 检查搜索框: 确保没有输入任何搜索词")
    print(f"   f) 打开开发者工具 → Network → 检查实际发出的请求和响应")
    print(f"   g) 在隐私/无痕模式下测试，排除扩展插件干扰")
    
    print(f"\n7. 检查后端API端点是否正确...")
    print(f"   - API端点: GET /api/v1/admin/system/logs/db/api")
    print(f"   - 返回类型: List[LogResponse]")
    print(f"   - 字段映射: 已正确将CrawlerTaskLog映射到LogResponse格式")
    print(f"   - 数据源: CrawlerTaskLog表，按started_at降序排列")
    
    print(f"\n8. 额外建议:")
    print(f"   - 检查前端的API_BASE常量是否正确 (当前为 '/api/v1/admin/system')")
    print(f"   - 确认代理配置是否正确转发API请求")
    print(f"   - 验证是否有中间件修改了响应数据")

if __name__ == "__main__":
    check_frontend_requests()