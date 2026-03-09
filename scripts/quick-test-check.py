#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-28T15:00:00 - 创建快速测试检查脚本
"""
快速测试检查脚本
快速验证测试环境的关键配置
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def check_file_exists(path: str, description: str) -> dict:
    """检查文件是否存在"""
    file_path = Path(path)
    if file_path.exists():
        return {
            "status": "pass",
            "message": f"{description} 存在",
            "details": str(file_path)
        }
    else:
        return {
            "status": "fail", 
            "message": f"{description} 不存在",
            "details": f"路径: {path}"
        }

def check_directory_exists(path: str, description: str) -> dict:
    """检查目录是否存在"""
    dir_path = Path(path)
    if dir_path.exists():
        return {
            "status": "pass",
            "message": f"{description} 存在",
            "details": str(dir_path)
        }
    else:
        return {
            "status": "warning",
            "message": f"{description} 不存在",
            "details": f"路径: {path}"
        }

def check_package_json() -> dict:
    """检查package.json中的测试依赖"""
    try:
        with open("frontend/package.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        dev_deps = data.get("devDependencies", {})
        required_deps = ["vitest", "@vitest/ui", "@vue/test-utils", "playwright"]
        
        missing = []
        for dep in required_deps:
            if dep not in dev_deps:
                missing.append(dep)
        
        if missing:
            return {
                "status": "warning",
                "message": f"缺少测试依赖: {', '.join(missing)}",
                "details": f"建议运行: npm install --save-dev {' '.join(missing)}"
            }
        else:
            return {
                "status": "pass",
                "message": "前端测试依赖完整",
                "details": f"包含: {', '.join(required_deps)}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"检查package.json失败: {e}",
            "details": "文件路径: frontend/package.json"
        }

def check_pyproject_toml() -> dict:
    """检查pyproject.toml中的测试配置"""
    try:
        with open("pyproject.toml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "[tool.pytest.ini_options]",
            "[tool.coverage.run]"
        ]
        
        missing = []
        for section in required_sections:
            if section not in content:
                missing.append(section)
        
        if missing:
            return {
                "status": "warning",
                "message": f"缺少测试配置: {', '.join(missing)}",
                "details": "请参考TEST_INTEGRATION_PLAN.md配置"
            }
        else:
            return {
                "status": "pass", 
                "message": "后端测试配置完整",
                "details": "pytest和coverage配置就绪"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"检查pyproject.toml失败: {e}",
            "details": "文件路径: pyproject.toml"
        }

def check_ci_cd_config() -> dict:
    """检查CI/CD配置"""
    try:
        configs = [
            ("ci-cd.yml", "基础CI/CD配置"),
            ("ci-cd-optimized.yml", "优化CI/CD配置")
        ]
        
        for file_name, description in configs:
            path = f".github/workflows/{file_name}"
            if Path(path).exists():
                return {
                    "status": "pass",
                    "message": f"CI/CD配置就绪: {description}",
                    "details": f"文件: {file_name}"
                }
        
        return {
            "status": "warning",
            "message": "CI/CD配置文件未找到",
            "details": "请创建.github/workflows/ci-cd-optimized.yml"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"检查CI/CD配置失败: {e}",
            "details": "目录: .github/workflows/"
        }

def run_quick_check():
    """运行快速检查"""
    print("🚀 开始快速测试环境检查")
    print("="*50)
    
    checks = [
        ("前端依赖配置", check_package_json),
        ("后端测试配置", check_pyproject_toml),
        ("CI/CD配置", check_ci_cd_config),
        ("Vitest配置文件", lambda: check_file_exists("frontend/vitest.config.js", "Vitest配置")),
        ("测试数据脚本", lambda: check_file_exists("scripts/init-test-data.py", "测试数据脚本")),
        ("覆盖率检查脚本", lambda: check_file_exists("scripts/check-coverage-thresholds.py", "覆盖率检查")),
        ("前端测试目录", lambda: check_directory_exists("frontend/src/tests/unit", "前端测试目录")),
        ("后端测试目录", lambda: check_directory_exists("backend/tests/unit", "后端测试目录")),
    ]
    
    results = []
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        result = check_func()
        results.append({
            "name": check_name,
            **result
        })
        
        status_emoji = {
            "pass": "✅",
            "fail": "❌", 
            "warning": "⚠️",
            "error": "🚨"
        }.get(result["status"], "❓")
        
        print(f"  {status_emoji} {result['message']}")
        if "details" in result:
            print(f"   详细: {result['details']}")
        
        if result["status"] in ["fail", "error"]:
            all_passed = False
    
    # 生成报告
    passed = sum(1 for r in results if r["status"] == "pass")
    warnings = sum(1 for r in results if r["status"] == "warning")
    failed = sum(1 for r in results if r["status"] in ["fail", "error"])
    
    print("\n" + "="*50)
    print("📋 快速检查报告")
    print("="*50)
    
    print(f"总检查数: {len(results)}")
    print(f"✅ 通过: {passed}")
    print(f"⚠️  警告: {warnings}")
    print(f"❌ 失败: {failed}")
    
    pass_rate = (passed / len(results) * 100) if results else 0
    print(f"📈 通过率: {pass_rate:.1f}%")
    
    # 输出建议
    if not all_passed:
        print(f"\n💡 建议措施:")
        
        if any(r["status"] == "fail" for r in results):
            print("  1. 修复失败的检查项")
        
        if any(r["status"] == "warning" for r in results):
            print("  2. 检查警告项目，优化配置")
        
        if pass_rate < 80:
            print("  3. 提高整体配置质量")
    
    print(f"\n📁 后续步骤:")
    print(f"  1. 完整验证: python scripts/validate-test-environment.py")
    print(f"  2. 初始化数据: python scripts/init-test-data.py")
    print(f"  3. 运行测试: ./scripts/run-all-tests.sh")
    
    return all_passed

def main():
    """主函数"""
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        success = run_quick_check()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断检查")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# AI_DONE: coder1 @2026-01-28T15:00:00