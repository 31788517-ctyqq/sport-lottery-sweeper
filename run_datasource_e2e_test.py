#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源管理模块端到端测试运行脚本
用于执行完整的端到端测试并验证功能完整性
"""

import subprocess
import sys
import os
import time
import requests
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_backend_health(base_url: str) -> bool:
    """检查后端服务是否健康"""
    try:
        # 尝试访问一个通用的健康检查端点
        response = requests.get(f"{base_url}/api/v1/admin/metrics/health", timeout=10)
        return response.status_code == 200
    except Exception:
        try:
            # 如果上面的端点不存在，尝试访问根路径
            response = requests.get(f"{base_url}/docs", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

def run_pytest_tests():
    """运行pytest测试"""
    try:
        # 执行端到端测试
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/e2e/test_datasource_management_e2e.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("=== Pytest 测试输出 ===")
        print(result.stdout)
        if result.stderr:
            print("=== Pytest 错误输出 ===")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"执行Pytest测试时出错: {e}")
        return False

def run_manual_tests():
    """运行手动测试函数"""
    try:
        # 导入并运行测试
        from tests.e2e.test_datasource_management_e2e import run_e2e_tests
        run_e2e_tests()
        return True
    except ImportError as e:
        print(f"导入测试模块失败: {e}")
        return False
    except Exception as e:
        print(f"执行测试时出错: {e}")
        return False

def main():
    """主函数"""
    print("="*70)
    print("数据源管理模块端到端测试运行器")
    print("="*70)
    
    # 获取基础URL
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    print(f"测试目标URL: {base_url}")
    
    # 检查后端服务是否运行
    print("\n正在检查后端服务状态...")
    if not check_backend_health(base_url):
        print(f"❌ 后端服务不可用，请确保服务在 {base_url} 上运行")
        print("提示: 您可以使用以下命令启动后端服务:")
        print(f"  cd {project_root}")
        print("  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return False
    
    print("✅ 后端服务健康")
    
    print("\n选择测试方式:")
    print("1. 使用pytest运行测试 (推荐)")
    print("2. 直接运行测试函数")
    print("3. 运行两种测试")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    success = False
    
    if choice == "1":
        print("\n开始运行Pytest测试...")
        success = run_pytest_tests()
    elif choice == "2":
        print("\n开始运行手动测试...")
        success = run_manual_tests()
    elif choice == "3":
        print("\n开始运行Pytest测试...")
        success1 = run_pytest_tests()
        print("\n开始运行手动测试...")
        success2 = run_manual_tests()
        success = success1 and success2
    else:
        print("无效选择，使用默认方式 (1)")
        print("\n开始运行Pytest测试...")
        success = run_pytest_tests()
    
    print("\n" + "="*70)
    if success:
        print("🎉 所有测试执行完成！")
        print("数据源管理模块端到端功能验证通过")
        print("模块已达到生产就绪状态")
    else:
        print("❌ 测试执行遇到问题")
        print("请检查错误信息并解决问题后重新测试")
    print("="*70)
    
    return success

if __name__ == "__main__":
    main()