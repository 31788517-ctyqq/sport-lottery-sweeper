"""
测试运行脚本 - 适配新的测试目录结构
"""
import subprocess
import sys
import os
from pathlib import Path

def run_unit_tests():
    """运行单元测试"""
    print("🏃‍♂️ 开始运行单元测试...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/unit/", 
            "-v", "--tb=short", "-x"
        ], check=True)
        print("✅ 单元测试运行完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 单元测试运行失败: {e}")
        return False

def run_integration_tests():
    """运行集成测试"""
    print("🏃‍♂️ 开始运行集成测试...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/integration/", 
            "-v", "--tb=short", "-x"
        ], check=True)
        print("✅ 集成测试运行完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 集成测试运行失败: {e}")
        return False

def run_e2e_tests():
    """运行端到端测试"""
    print("🏃‍♂️ 开始运行端到端测试...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/e2e/", 
            "-v", "--tb=short", "-x"
        ], check=True)
        print("✅ 端到端测试运行完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 端到端测试运行失败: {e}")
        return False

def run_functional_tests():
    """运行功能测试"""
    print("🏃‍♂️ 开始运行功能测试...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/functional/", 
            "-v", "--tb=short", "-k 'not temp_test'"
        ], check=True)
        print("✅ 功能测试运行完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 功能测试运行失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🏃‍♂️ 开始运行所有测试...")
    
    tests = [
        ("单元测试", run_unit_tests),
        ("集成测试", run_integration_tests),
        ("功能测试", run_functional_tests),
        ("端到端测试", run_e2e_tests)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        results[test_name] = test_func()
    
    print("\n📊 测试运行结果汇总:")
    all_passed = True
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    return all_passed

def run_tests_with_coverage():
    """运行带覆盖率的测试"""
    print("覆盖率测试运行中...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/",
            "--cov=.", "--cov-report=html", "--cov-report=term",
            "-k 'not temp_test'"
        ], check=True)
        print("✅ 覆盖率测试完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 覆盖率测试失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python run_tests.py [unit|integration|e2e|functional|all|coverage]")
        print("  unit       - 运行单元测试")
        print("  integration - 运行集成测试")
        print("  e2e        - 运行端到端测试")
        print("  functional - 运行功能测试")
        print("  all        - 运行所有测试")
        print("  coverage   - 运行带覆盖率的测试")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "unit":
        success = run_unit_tests()
    elif command == "integration":
        success = run_integration_tests()
    elif command == "e2e":
        success = run_e2e_tests()
    elif command == "functional":
        success = run_functional_tests()
    elif command == "all":
        success = run_all_tests()
    elif command == "coverage":
        success = run_tests_with_coverage()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
    
    if not success:
        print(f"\n⚠️  {command} 测试未全部通过")
        sys.exit(1)
    else:
        print(f"\n🎉 {command} 测试全部通过!")

if __name__ == "__main__":
    main()