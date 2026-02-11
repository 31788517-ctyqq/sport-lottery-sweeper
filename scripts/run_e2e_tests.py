#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端测试执行脚本
统一管理所有E2E测试的执行和报告生成
"""
import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """执行命令并输出结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def main():
    """主函数"""
    print("🚀 开始执行端到端测试套件")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    test_results = []
    
    # 1. 测试数据源管理
    success = run_command(
        "python -m pytest tests/e2e/test_datasource_management.py -v",
        "数据源管理E2E测试"
    )
    test_results.append(("数据源管理测试", success))
    
    # 2. 测试完整工作流程
    success = run_command(
        "python -m pytest tests/e2e/scenarios/test_complete_workflow.py -v",
        "完整工作流程测试"
    )
    test_results.append(("完整工作流程测试", success))
    
    # 3. 测试爬虫工作流程
    success = run_command(
        "python -m pytest tests/e2e/scenarios/test_crawler_workflow.py -v",
        "爬虫工作流程测试"
    )
    test_results.append(("爬虫工作流程测试", success))
    
    # 4. 测试新增的业务流程
    success = run_command(
        "python -m pytest tests/e2e/scenarios/test_missing_workflows.py::test_user_management_workflow -v",
        "用户管理工作流程测试"
    )
    test_results.append(("用户管理工作流程测试", success))
    
    success = run_command(
        "python -m pytest tests/e2e/scenarios/test_missing_workflows.py::test_crawler_task_execution_workflow -v",
        "爬虫任务执行工作流程测试"
    )
    test_results.append(("爬虫任务执行工作流程测试", success))
    
    success = run_command(
        "python -m pytest tests/e2e/scenarios/test_missing_workflows.py::test_data_prediction_workflow -v",
        "数据预测工作流程测试"
    )
    test_results.append(("数据预测工作流程测试", success))
    
    success = run_command(
        "python -m pytest tests/e2e/scenarios/test_missing_workflows.py::test_integrated_system_workflow -v",
        "系统集成工作流程测试"
    )
    test_results.append(("系统集成工作流程测试", success))
    
    # 生成测试报告
    print(f"\n{'='*60}")
    print("📊 测试结果汇总")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有端到端测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查并修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())