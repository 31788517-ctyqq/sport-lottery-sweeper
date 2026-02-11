#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
后端服务诊断工具 - 直接检查问题
"""
import subprocess
import time
import requests
import json
import sys

def check_backend_logs():
    """检查后端日志"""
    print("=" * 60)
    print("检查后端日志")
    print("=" * 60)
    
    # 尝试获取lottery API的错误信息
    try:
        response = requests.get('http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10', timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 500:
            print(f"错误响应: {response.text[:500]}")
        elif response.status_code == 200:
            print("✓ API返回200，数据正常！")
            data = response.json()
            print(f"数据条数: {len(data.get('data', []))}")
            return True
    except Exception as e:
        print(f"无法连接后端: {e}")
        return False
    
    return False

def test_direct_import():
    """测试直接导入lottery模块"""
    print("\n" + "=" * 60)
    print("测试直接导入lottery模块")
    print("=" * 60)
    
    # 切换到backend目录
    import os
    os.chdir('backend')
    
    # 创建测试脚本
    test_script = """
import sys
sys.path.insert(0, '.')

# 测试导入
try:
    from api.v1.lottery import load_500_com_data
    print("✓ 导入成功")
    
    # 测试函数
    result = load_500_com_data()
    print(f"✓ 函数执行成功，返回 {len(result)} 条数据")
    
    if result:
        print(f"✓ 第一条: {result[0].get('match_id')}")
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
"""
    
    with open('test_import.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    # 运行测试
    try:
        result = subprocess.run([sys.executable, 'test_import.py'], 
                              capture_output=True, text=True, timeout=10)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
    except Exception as e:
        print(f"运行失败: {e}")
    
    # 清理
    if os.path.exists('test_import.py'):
        os.remove('test_import.py')

def check_backend_running():
    """检查后段是否运行"""
    print("\n" + "=" * 60)
    print("检查后段服务状态")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8000/docs', timeout=3)
        if response.status_code == 200:
            print("✓ 后端服务正在运行")
            return True
        else:
            print(f"✗ 后端返回状态码: {response.status_code}")
            return False
    except:
        print("✗ 后端服务未启动")
        print("  请在backend目录下运行: python main.py")
        return False

def main():
    print("\n" + "=" * 60)
    print("后端服务诊断工具")
    print("=" * 60)
    
    # 检查后端是否运行
    running = check_backend_running()
    
    if running:
        # 检查API
        api_ok = check_backend_logs()
        
        if not api_ok:
            # 测试直接导入
            test_direct_import()
        
        print("\n" + "=" * 60)
        print("诊断完成")
        print("=" * 60)
        
        if api_ok:
            print("✓ API正常工作，数据可以访问！")
            print("\n请在浏览器中测试:")
            print("http://localhost:8000/api/v1/lottery/matches?source=500&page=1&size=10")
        else:
            print("✗ API有问题，请查看上面的错误信息")
            print("\n建议:")
            print("1. 重启后端服务")
            print("2. 检查backend/api/v1/lottery.py文件")
            print("3. 确保debug目录存在且有数据文件")
    else:
        print("\n请先启动后端服务:")
        print("cd backend && python main.py")

if __name__ == '__main__':
    main()
