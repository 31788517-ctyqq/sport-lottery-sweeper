#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连通性测试脚本
测试爬虫管理API的连通性和响应
"""

import requests
import json
import sys
from urllib.parse import urljoin

def test_service_availability(base_url="http://localhost:8000"):
    """测试服务可用性"""
    print("=== API连通性测试 ===")
    print(f"测试目标: {base_url}")
    print()
    
    # 测试基本连通性
    endpoints = [
        ("根路径", "/"),
        ("健康检查", "/health/live"),
        ("数据源API", "/api/admin/v1/sources"),
        ("情报数据API", "/api/admin/v1/intelligence/data"),
        ("统计信息API", "/api/admin/v1/intelligence/stats"),
        ("系统健康API", "/api/admin/v1/system/health"),
    ]
    
    results = []
    
    for name, endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        print(f"[INSPECT] 测试 {name}: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   [OK] 响应成功")
                    if isinstance(data, dict):
                        if 'code' in data:
                            print(f"   业务码: {data['code']}")
                        if 'message' in data:
                            print(f"   消息: {data['message']}")
                        if 'data' in data:
                            if isinstance(data['data'], list):
                                print(f"   数据条目: {len(data['data'])}")
                            else:
                                print(f"   数据类型: {type(data['data'])}")
                    results.append((name, True, response.status_code))
                except json.JSONDecodeError:
                    print(f"   [WARNING]  响应不是JSON格式")
                    print(f"   响应内容: {response.text[:100]}")
                    results.append((name, False, "Invalid JSON"))
            else:
                print(f"   [ERROR] HTTP错误: {response.status_code}")
                print(f"   响应内容: {response.text[:100]}")
                results.append((name, False, response.status_code))
                
        except requests.exceptions.ConnectionError:
            print(f"   [ERROR] 连接失败 - 服务可能未启动")
            print(f"   [HINT] 提示: 请启动后端服务后再测试")
            results.append((name, False, "Connection Error"))
        except requests.exceptions.Timeout:
            print(f"   [ERROR] 请求超时")
            results.append((name, False, "Timeout"))
        except Exception as e:
            print(f"   [ERROR] 异常: {str(e)}")
            results.append((name, False, str(e)))
        
        print()
    
    # 输出测试结果汇总
    print("=" * 50)
    print("[ANALYTICS] 测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, status in results:
        status_icon = "[OK]" if success else "[ERROR]"
        print(f"{status_icon} {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("[SUCCESS] 所有API测试通过！")
        return True
    elif passed > 0:
        print(f"[WARNING]  {passed}/{total} 个API可用，{total-passed} 个需要检查")
        return True
    else:
        print("[ERROR] 所有API都无法访问，请检查服务状态")
        return False

def provide_manual_start_instructions():
    """提供手动启动服务的说明"""
    print("\n" + "=" * 50)
    print("[FIX] 手动启动后端服务指南")
    print("=" * 50)
    print()
    print("方法1: 使用Python直接启动")
    print("  1. 打开新的命令行窗口")
    print("  2. 执行命令:")
    print("     cd c:/Users/11581/Downloads/sport-lottery-sweeper")
    print("     python simple_test_server.py")
    print()
    print("方法2: 如果上面的不行，尝试:")
    print("  python -c \"exec(open('simple_test_server.py').read())\"")
    print()
    print("方法3: 使用现有后端文件")
    print("  cd backend")
    print("  python main.py.backup  # 使用备份文件")
    print()
    print("服务启动后，重新运行此测试脚本验证API")
    print("=" * 50)

def test_with_different_urls():
    """尝试不同的URL和端口"""
    print("\n[INSPECT] 尝试不同的服务地址...")
    
    urls_to_try = [
        "http://localhost:8000",
        "http://127.0.0.1:8000", 
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    working_urls = []
    
    for url in urls_to_try:
        print(f"\n尝试: {url}")
        try:
            response = requests.get(urljoin(url, "/health/live"), timeout=3)
            if response.status_code == 200:
                print(f"  [OK] {url} 可用")
                working_urls.append(url)
            else:
                print(f"  [ERROR] {url} 返回状态码: {response.status_code}")
        except:
            print(f"  [ERROR] {url} 无法连接")
    
    if working_urls:
        print(f"\n[SUCCESS] 发现可用服务: {working_urls[0]}")
        return working_urls[0]
    else:
        print("\n[ERROR] 未发现运行中的服务")
        return None

if __name__ == "__main__":
    print("[ROCKET] 爬虫管理API连通性测试工具")
    print()
    
    # 首先尝试不同的URL
    working_url = test_with_different_urls()
    
    if working_url:
        # 测试完整API
        test_service_availability(working_url)
    else:
        # 测试默认URL
        success = test_service_availability()
        
        if not success:
            provide_manual_start_instructions()
            
    input("\n按回车键退出...")