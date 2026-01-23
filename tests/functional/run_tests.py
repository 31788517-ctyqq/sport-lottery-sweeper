"""
测试运行脚本
用于运行不同类型和级别的测试
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_unit_tests():
    """运行单元测试"""
    print("🧪 开始运行单元测试...")
    cmd = [sys.executable, "-m", "pytest", "tests/backend/unit/", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_integration_tests():
    """运行集成测试"""
    print("🔗 开始运行集成测试...")
    cmd = [sys.executable, "-m", "pytest", "tests/backend/integration/", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_e2e_tests():
    """运行端到端测试"""
    print("🌐 开始运行端到端测试...")
    cmd = [sys.executable, "-m", "pytest", "tests/backend/e2e/", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    
    results = {}
    results['unit'] = run_unit_tests()
    results['integration'] = run_integration_tests()
    results['e2e'] = run_e2e_tests()
    
    print("\n📊 测试结果汇总:")
    for test_type, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_type.capitalize()} 测试: {status}")
    
    all_passed = all(results.values())
    overall_status = "✅ 全部测试通过" if all_passed else "❌ 部分测试失败"
    print(f"\n🎉 总体结果: {overall_status}")
    
    return all_passed


def run_tests_with_coverage():
    """运行带覆盖率的测试"""
    print("📏 开始运行带覆盖率的测试...")
    
    # 安装 coverage，如果尚未安装
    try:
        import coverage
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage"])
    
    cmd = [
        sys.executable, "-m", "coverage", "run",
        "-m", "pytest", "tests/backend/", "--tb=short"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Pytest 输出:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print("❌ 测试执行失败")
        return False
    
    # 生成覆盖率报告
    report_cmd = [sys.executable, "-m", "coverage", "report", "--show-missing"]
    report_result = subprocess.run(report_cmd, capture_output=True, text=True)
    print("\n覆盖率报告:")
    print(report_result.stdout)
    if report_result.stderr:
        print("STDERR:", report_result.stderr)
    
    # 生成HTML覆盖率报告
    html_cmd = [sys.executable, "-m", "coverage", "html", "-d", "htmlcov"]
    html_result = subprocess.run(html_cmd, capture_output=True, text=True)
    if html_result.stderr:
        print("HTML报告生成错误:", html_result.stderr)
    
    print("📊 HTML覆盖率报告已生成到 htmlcov/ 目录")
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行项目测试")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "e2e", "all", "coverage"],
        nargs="?",
        default="all",
        help="要运行的测试类型"
    )
    
    args = parser.parse_args()
    
    print(f"🎯 正在运行 {args.test_type} 测试...")
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "e2e":
        success = run_e2e_tests()
    elif args.test_type == "coverage":
        success = run_tests_with_coverage()
    elif args.test_type == "all":
        success = run_all_tests()
    else:
        print(f"未知的测试类型: {args.test_type}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)