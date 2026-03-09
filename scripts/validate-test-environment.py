#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-28T14:45:00 - 创建测试环境验证脚本
"""
测试环境验证脚本
验证前后端测试环境是否配置正确
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

class TestEnvironmentValidator:
    """测试环境验证器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.checks_passed = 0
        self.checks_total = 0
        self.results = []
    
    def run_check(self, name: str, check_func) -> bool:
        """运行单个检查"""
        self.checks_total += 1
        print(f"\n🔍 检查: {name}")
        
        try:
            result = check_func()
            if result:
                print(f"   ✅ 通过")
                self.checks_passed += 1
                self.results.append({"name": name, "status": "pass", "message": ""})
            else:
                print(f"   ❌ 失败")
                self.results.append({"name": name, "status": "fail", "message": "检查失败"})
            return result
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            self.results.append({"name": name, "status": "error", "message": str(e)})
            return False
    
    def check_frontend_dependencies(self) -> bool:
        """检查前端依赖"""
        package_json = self.project_root / "frontend" / "package.json"
        if not package_json.exists():
            print("   ❌ frontend/package.json 不存在")
            return False
        
        package_lock = self.project_root / "frontend" / "package-lock.json"
        if not package_lock.exists():
            print("   ⚠️  frontend/package-lock.json 不存在")
        
        # 检查关键测试依赖
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                
            dev_deps = data.get("devDependencies", {})
            required = ["vitest", "@vitest/ui", "@vue/test-utils", "jsdom", "playwright"]
            
            missing = []
            for dep in required:
                if dep not in dev_deps:
                    missing.append(dep)
            
            if missing:
                print(f"   ⚠️  缺少测试依赖: {', '.join(missing)}")
                return False
                
            return True
        except Exception as e:
            print(f"   ❌ 解析package.json失败: {e}")
            return False
    
    def check_backend_dependencies(self) -> bool:
        """检查后端依赖"""
        # AI_WORKING: coder1 @2026-01-29T06:00:00 - 修复requirements-dev.txt路径
        requirements_dev = self.project_root / "requirements-dev.txt"
        if not requirements_dev.exists():
            print("   ❌ requirements-dev.txt 不存在")
            return False
        
        # 检查关键测试依赖
        try:
            with open(requirements_dev, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required = ["pytest", "pytest-cov", "pytest-asyncio"]
            missing = []
            
            for dep in required:
                if dep not in content.lower():
                    missing.append(dep)
            
            if missing:
                print(f"   ⚠️  缺少测试依赖: {', '.join(missing)}")
                return False
                
            return True
        except Exception as e:
            print(f"   ❌ 读取requirements-dev.txt失败: {e}")
            return False
    
    def check_vitest_config(self) -> bool:
        """检查Vitest配置"""
        config_file = self.project_root / "frontend" / "vitest.config.js"
        if not config_file.exists():
            print("   ❌ frontend/vitest.config.js 不存在")
            return False
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "test" not in content or "coverage" not in content:
                print("   ⚠️  Vitest配置不完整")
                return False
                
            return True
        except Exception as e:
            print(f"   ❌ 读取vitest.config.js失败: {e}")
            return False
    
    def check_pytest_config(self) -> bool:
        """检查pytest配置"""
        pyproject_toml = self.project_root / "pyproject.toml"
        if not pyproject_toml.exists():
            print("   ❌ pyproject.toml 不存在")
            return False
        
        try:
            with open(pyproject_toml, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "[tool.pytest.ini_options]" not in content or "[tool.coverage.run]" not in content:
                print("   ⚠️  pytest配置不完整")
                return False
                
            return True
        except Exception as e:
            print(f"   ❌ 读取pyproject.toml失败: {e}")
            return False
    
    def check_test_directories(self) -> bool:
        """检查测试目录结构"""
        directories = [
            "frontend/src/tests/unit/components",
            "frontend/src/tests/unit/composables",
            "frontend/src/tests/unit/utils",
            "backend/tests/unit/api",
            "backend/tests/unit/models",
            "backend/tests/unit/services",
            "backend/tests/integration"
        ]
        
        missing = []
        for dir_path in directories:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing.append(dir_path)
        
        if missing:
            print(f"   ⚠️  缺少测试目录: {', '.join(missing[:3])}")
            for dir_path in missing:
                Path(self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
                print(f"      已创建: {dir_path}")
        
        return True
    
    def check_test_examples(self) -> bool:
        """检查测试示例"""
        # 检查是否有测试文件
        frontend_test_files = list((self.project_root / "frontend" / "src" / "tests" / "unit").glob("*.test.js"))
        backend_test_files = list((self.project_root / "backend" / "tests" / "unit").rglob("test_*.py"))
        
        if not frontend_test_files:
            print("   ⚠️  前端单元测试文件不存在，将创建示例")
            self.create_frontend_test_example()
        
        if not backend_test_files:
            print("   ⚠️  后端单元测试文件不存在，将创建示例")
            self.create_backend_test_example()
        
        return True
    
    def create_frontend_test_example(self):
        """创建前端测试示例"""
        example_file = self.project_root / "frontend" / "src" / "tests" / "unit" / "example.test.js"
        
        content = """// 示例前端单元测试
import { describe, it, expect } from 'vitest'

describe('示例测试套件', () => {
  it('基本断言测试', () => {
    expect(1 + 1).toBe(2)
  })
  
  it('对象相等测试', () => {
    const obj = { name: 'test', value: 42 }
    expect(obj).toEqual({ name: 'test', value: 42 })
  })
  
  it('异步测试', async () => {
    const result = await Promise.resolve('success')
    expect(result).toBe('success')
  })
})
"""
        
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"      已创建示例测试文件: {example_file}")
    
    def create_backend_test_example(self):
        """创建后端测试示例"""
        example_file = self.project_root / "backend" / "tests" / "unit" / "test_example.py"
        
        content = '''"""示例后端单元测试"""
import pytest


def test_addition():
    """测试基本加法"""
    assert 1 + 1 == 2


def test_string_concatenation():
    """测试字符串拼接"""
    result = "hello" + " " + "world"
    assert result == "hello world"


def test_list_operations():
    """测试列表操作"""
    numbers = [1, 2, 3]
    numbers.append(4)
    assert len(numbers) == 4
    assert numbers[-1] == 4


class TestExampleClass:
    """示例测试类"""
    
    def test_class_method(self):
        """测试类方法"""
        assert True
    
    def test_with_fixture(self, example_fixture):
        """使用fixture的测试"""
        assert example_fixture == "fixture_data"


@pytest.fixture
def example_fixture():
    """示例fixture"""
    return "fixture_data"


@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await async_example()
    assert result == "async_data"


async def async_example():
    """示例异步函数"""
    return "async_data"
'''
        
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"      已创建示例测试文件: {example_file}")
    
    def check_ci_cd_config(self) -> bool:
        """检查CI/CD配置"""
        ci_file = self.project_root / ".github" / "workflows" / "ci-cd-optimized.yml"
        if not ci_file.exists():
            print("   ❌ .github/workflows/ci-cd-optimized.yml 不存在")
            return False
        
        # 检查是否有基本的配置
        try:
            with open(ci_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "jobs:" not in content or "steps:" not in content:
                print("   ⚠️  CI/CD配置不完整")
                return False
                
            return True
        except Exception as e:
            print(f"   ❌ 读取CI/CD配置失败: {e}")
            return False
    
    def check_test_scripts(self) -> bool:
        """检查测试脚本"""
        scripts = [
            "scripts/run-all-tests.sh",
            "scripts/run-all-tests.bat",
            "scripts/check-coverage-thresholds.py",
            "scripts/init-test-data.py",
            "scripts/generate-test-report.py"
        ]
        
        missing = []
        for script in scripts:
            if not (self.project_root / script).exists():
                missing.append(script)
        
        if missing:
            print(f"   ⚠️  缺少测试脚本: {', '.join(missing[:2])}")
            return False
        
        # 检查脚本是否有执行权限
        sh_script = self.project_root / "scripts" / "run-all-tests.sh"
        if sh_script.exists():
            try:
                subprocess.run(["chmod", "+x", str(sh_script)], check=False)
                print(f"      已设置执行权限: {sh_script}")
            except Exception:
                pass
        
        return True
    
    def generate_report(self) -> Dict:
        """生成验证报告"""
        pass_rate = (self.checks_passed / self.checks_total * 100) if self.checks_total > 0 else 0
        
        report = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "summary": {
                "total_checks": self.checks_total,
                "passed_checks": self.checks_passed,
                "failed_checks": self.checks_total - self.checks_passed,
                "pass_rate": pass_rate,
                "status": "PASS" if self.checks_passed == self.checks_total else "FAIL"
            },
            "checks": self.results,
            "recommendations": []
        }
        
        # 添加建议
        if pass_rate < 100:
            report["recommendations"].append("修复失败的检查项")
        
        if self.checks_passed < 5:
            report["recommendations"].append("检查测试依赖是否安装正确")
        
        return report
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("🚀 开始验证测试环境配置")
        print("="*60)
        
        checks = [
            ("前端依赖配置", self.check_frontend_dependencies),
            ("后端依赖配置", self.check_backend_dependencies),
            ("Vitest配置检查", self.check_vitest_config),
            ("pytest配置检查", self.check_pytest_config),
            ("测试目录结构", self.check_test_directories),
            ("测试示例文件", self.check_test_examples),
            ("CI/CD配置检查", self.check_ci_cd_config),
            ("测试脚本检查", self.check_test_scripts)
        ]
        
        for name, check_func in checks:
            self.run_check(name, check_func)
        
        # 生成报告
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📋 验证报告")
        print("="*60)
        
        status_emoji = "✅" if report["summary"]["status"] == "PASS" else "❌"
        print(f"总体状态: {status_emoji} {report['summary']['status']}")
        print(f"通过率: {report['summary']['pass_rate']:.1f}% ({self.checks_passed}/{self.checks_total})")
        
        if report["recommendations"]:
            print(f"\n📝 建议:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("\n📁 下一步:")
        print("   1. 运行完整测试: python scripts/init-test-data.py && ./scripts/run-all-tests.sh")
        print("   2. 检查覆盖率: python scripts/check-coverage-thresholds.py")
        print("   3. 生成报告: python scripts/generate-test-report.py")
        
        return report["summary"]["status"] == "PASS"

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    validator = TestEnvironmentValidator(project_root)
    
    try:
        success = validator.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断验证")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# AI_DONE: coder1 @2026-01-28T14:45:00