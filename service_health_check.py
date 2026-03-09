#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务健康检查脚本
验证API服务是否正常运行
"""

import requests
import json
import time

def check_service_health():
    base_url = "http://localhost:8001"
    
    print("=== 后端服务健康检查 ===")
    print(f"目标地址: {base_url}")
    print()
    
    # 检查项目
    checks = [
        ("根路径", "/"),
        ("健康检查", "/health/live"),
        ("数据源API", "/api/admin/v1/sources"),
        ("情报数据API", "/api/admin/v1/intelligence/data"),
        ("统计信息API", "/api/admin/v1/intelligence/stats"),
        ("系统健康API", "/api/admin/v1/system/health"),
    ]
    
    results = []
    
    for name, endpoint in checks:
        url = f"{base_url}{endpoint}"
        print(f"🔍 检查 {name}: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ 响应成功")
                    if isinstance(data, dict):
                        if 'code' in data:
                            print(f"   业务码: {data['code']}")
                        if 'message' in data:
                            print(f"   消息: {data['message']}")
                        if 'data' in data:
                            if isinstance(data['data'], list):
                                print(f"   数据条目: {len(data['data'])} 条")
                                # 显示第一条数据的关键信息
                                if data['data']:
                                    first_item = data['data'][0]
                                    if 'name' in first_item:
                                        print(f"   示例数据: {first_item['name']}")
                            else:
                                print(f"   数据类型: {type(data['data']).__name__}")
                    results.append((name, True, "OK"))
                except json.JSONDecodeError:
                    print(f"   ⚠️  响应不是JSON格式")
                    results.append((name, False, "Invalid JSON"))
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                results.append((name, False, f"HTTP {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败 - 服务未启动或端口错误")
            results.append((name, False, "Connection Error"))
        except requests.exceptions.Timeout:
            print(f"   ❌ 请求超时")
            results.append((name, False, "Timeout"))
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
            results.append((name, False, str(e)))
        
        print()
        time.sleep(0.5)  # 避免请求过快
    
    # 汇总结果
    print("=" * 50)
    print("📊 检查结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, status in results:
        icon = "✅" if success else "❌"
        print(f"{icon} {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有API服务正常！可以开始前端测试")
        return True
    elif passed > 0:
        print(f"⚠️  {passed}/{total} 个API可用，部分功能可能受限")
        return True
    else:
        print("❌ 所有API都无法访问")
        print("💡 请检查：")
        print("   1. 后端服务是否已启动")
        print("   2. 端口8000是否被占用")
        print("   3. 防火墙是否阻止连接")
        return False

if __name__ == "__main__":
    success = check_service_health()
    if not success:
        print("\n按回车键退出...")
        input()