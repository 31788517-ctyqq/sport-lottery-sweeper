import requests
import json
from datetime import datetime
import time

def diagnose_api_logs():
    print("=" * 70)
    print("API日志页面问题诊断")
    print("=" * 70)
    
    # 1. 检查API端点是否可访问
    print("1. 检查API端点连通性...")
    try:
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=5')
        print(f"   ✓ API端点可访问，状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ API端点不可访问: {e}")
        return
    
    # 2. 获取API日志数据
    print("\n2. 获取API日志数据...")
    try:
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=5')
        backend_data = response.json()
        print(f"   ✓ 获取到 {len(backend_data)} 条日志记录")
    except Exception as e:
        print(f"   ✗ 获取API日志数据失败: {e}")
        return
    
    # 3. 分析第一条数据的字段格式
    if backend_data:
        first_log = backend_data[0]
        print(f"\n3. 分析第一条日志数据格式:")
        print(f"   ID: {first_log.get('id')} (类型: {type(first_log.get('id'))})")
        print(f"   时间戳: {first_log.get('timestamp')} (类型: {type(first_log.get('timestamp'))})")
        print(f"   级别: {first_log.get('level')} (类型: {type(first_log.get('level'))})")
        print(f"   模块: {first_log.get('module')} (类型: {type(first_log.get('module'))})")
        print(f"   消息: {first_log.get('message')} (类型: {type(first_log.get('message'))})")
        print(f"   请求路径: {first_log.get('request_path')} (类型: {type(first_log.get('request_path'))})")
        print(f"   状态码: {first_log.get('response_status')} (类型: {type(first_log.get('response_status'))})")
        print(f"   耗时: {first_log.get('duration_ms')} (类型: {type(first_log.get('duration_ms'))})")
        print(f"   额外数据: {first_log.get('extra_data')[:50]}... (类型: {type(first_log.get('extra_data'))})")
        
        # 验证时间格式
        try:
            timestamp = first_log.get('timestamp')
            if isinstance(timestamp, str):
                # 尝试解析ISO格式时间
                parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                print(f"   ✓ 时间戳格式正确: {parsed_time}")
            else:
                print(f"   ✗ 时间戳不是字符串格式: {type(timestamp)}")
        except Exception as e:
            print(f"   ✗ 时间戳格式错误: {e}")
    
    # 4. 检查分页参数是否生效
    print(f"\n4. 检查分页参数是否生效...")
    try:
        response1 = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=1')
        response2 = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=1&limit=1')
        
        data1 = response1.json()
        data2 = response2.json()
        
        if data1 and data2 and data1[0]['id'] != data2[0]['id']:
            print(f"   ✓ 分页参数生效，第1条(id:{data1[0]['id']})与第2条(id:{data2[0]['id']})不同")
        else:
            print(f"   ⚠ 分页参数可能未生效，第1条与第2条ID相同或数据不足")
    except Exception as e:
        print(f"   ✗ 分页参数测试失败: {e}")
    
    # 5. 模拟前端请求参数
    print(f"\n5. 模拟前端请求参数...")
    frontend_params = {
        'skip': (1 - 1) * 50,  # currentPage=1, pageSize=50
        'limit': 50
    }
    
    try:
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api', params=frontend_params)
        frontend_sim_data = response.json()
        print(f"   ✓ 模拟前端请求成功，获取到 {len(frontend_sim_data)} 条记录")
        
        if frontend_sim_data:
            first_record = frontend_sim_data[0]
            print(f"     第一条记录ID: {first_record['id']}, 消息: {first_record['message'][:50]}...")
    except Exception as e:
        print(f"   ✗ 模拟前端请求失败: {e}")
    
    # 6. 检查过滤参数是否生效
    print(f"\n6. 检查过滤参数是否生效...")
    try:
        # 尝试带级别过滤的请求
        response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=5&level=INFO')
        filtered_data = response.json()
        print(f"   ✓ 级别过滤请求成功，获取到 {len(filtered_data)} 条记录")
        
        # 检查所有返回记录是否都是INFO级别
        all_info = all(log.get('level') == 'INFO' for log in filtered_data)
        if all_info and filtered_data:
            print(f"   ✓ 级别过滤生效，所有记录都是INFO级别")
        elif not filtered_data:
            print(f"   ⚠ 级别过滤可能未生效，没有返回数据")
        else:
            print(f"   ⚠ 级别过滤可能未生效，返回了非INFO级别的数据")
    except Exception as e:
        print(f"   ✗ 过滤参数测试失败: {e}")
    
    # 7. 验证数据类型一致性
    print(f"\n7. 验证数据类型一致性...")
    if backend_data:
        sample_log = backend_data[0]
        issues = []
        
        # 验证ID是整数
        if not isinstance(sample_log.get('id'), int):
            issues.append(f"ID不是整数: {sample_log.get('id')} ({type(sample_log.get('id'))})")
        
        # 验证timestamp是字符串
        if not isinstance(sample_log.get('timestamp'), str):
            issues.append(f"timestamp不是字符串: {sample_log.get('timestamp')} ({type(sample_log.get('timestamp'))})")
        
        # 验证level是字符串
        if not isinstance(sample_log.get('level'), str):
            issues.append(f"level不是字符串: {sample_log.get('level')} ({type(sample_log.get('level'))})")
        
        # 验证request_path是字符串或None
        path_val = sample_log.get('request_path')
        if path_val is not None and not isinstance(path_val, str):
            issues.append(f"request_path不是字符串或None: {path_val} ({type(path_val)})")
        
        # 验证response_status是整数或None
        status_val = sample_log.get('response_status')
        if status_val is not None and not isinstance(status_val, int):
            issues.append(f"response_status不是整数或None: {status_val} ({type(status_val)})")
        
        # 验证duration_ms是整数或None
        duration_val = sample_log.get('duration_ms')
        if duration_val is not None and not isinstance(duration_val, int):
            issues.append(f"duration_ms不是整数或None: {duration_val} ({type(duration_val)})")
        
        # 验证extra_data是字符串或None
        extra_val = sample_log.get('extra_data')
        if extra_val is not None and not isinstance(extra_val, str):
            issues.append(f"extra_data不是字符串或None: {extra_val} ({type(extra_val)})")
        
        if issues:
            print(f"   ✗ 发现 {len(issues)} 个类型不一致问题:")
            for issue in issues:
                print(f"     - {issue}")
        else:
            print(f"   ✓ 所有字段类型都符合API模型定义")
    
    print(f"\n8. 总结可能的问题原因:")
    print(f"   a) 浏览器缓存: 前端可能缓存了旧数据，尝试硬刷新(Ctrl+F5)")
    print(f"   b) 前端过滤器: 检查前端界面上是否启用了隐藏的过滤条件")
    print(f"   c) 时间范围筛选: 检查日期选择器是否设置了特定时间范围")
    print(f"   d) 搜索关键词: 检查搜索框是否包含未注意到的搜索词")
    print(f"   e) API路径错误: 确认前端请求的是正确的API端点")
    print(f"   f) 数据更新延迟: 后端数据可能在请求时刻发生了变化")
    
    print(f"\n9. 建议的排查步骤:")
    print(f"   1) 打开浏览器开发者工具，检查网络选项卡中的实际请求和响应")
    print(f"   2) 确认请求的URL与预期的API端点一致")
    print(f"   3) 检查请求参数是否包含意外的过滤条件")
    print(f"   4) 清除浏览器缓存后重新加载页面")
    print(f"   5) 在不同浏览器或隐私模式下测试")

if __name__ == "__main__":
    diagnose_api_logs()