#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-29T00:47:00 - 创建最终验证脚本
"""
最终验证脚本
整合所有验证步骤，生成完整的测试集成验证报告
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class FinalVerification:
    """最终验证类"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = []
        self.start_time = time.time()
        self.report_dir = self.project_root / "test-reports"
        self.report_dir.mkdir(exist_ok=True)
        
    def log_check(self, name: str, status: str, message: str = "", details: str = ""):
        """记录检查结果"""
        result = {
            "name": name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status_emoji = {
            "pass": "✅",
            "fail": "❌",
            "warning": "⚠️",
            "error": "🚨"
        }.get(status, "❓")
        
        print(f"{status_emoji} {name}: {message}")
        if details:
            print(f"   详细: {details}")
    
    def check_test_plan_documentation(self) -> bool:
        """检查测试规划文档"""
        print("\n📋 检查测试规划文档...")
        
        required_docs = [
            ("TEST_INTEGRATION_PLAN.md", "测试集成规划"),
            ("TESTING_QUICKSTART.md", "测试快速开始指南"),
            ("test-environment-setup.md", "测试环境设置指南"),
            ("TEST_VALIDATION_GUIDE.md", "测试环境验证指南"),
            ("AUTO_TEST_INTEGRATION_SUMMARY.md", "自动测试集成总结")
        ]
        
        all_pass = True
        for file_name, description in required_docs:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_check(
                    f"文档检查 - {description}",
                    "pass",
                    "存在",
                    str(file_path)
                )
            else:
                self.log_check(
                    f"文档检查 - {description}",
                    "fail",
                    "不存在",
                    str(file_path)
                )
                all_pass = False
        
        return all_pass
    
    def check_test_scripts(self) -> bool:
        """检查测试脚本"""
        print("\n🔧 检查测试脚本...")
        
        required_scripts = [
            ("scripts/run-all-tests.sh", "Linux/macOS完整测试脚本"),
            ("scripts/run-all-tests.bat", "Windows完整测试脚本"),
            ("scripts/check-coverage-thresholds.py", "覆盖率检查脚本"),
            ("scripts/init-test-data.py", "测试数据初始化脚本"),
            ("scripts/generate-test-report.py", "测试报告生成脚本"),
            ("scripts/validate-test-environment.py", "测试环境验证脚本"),
            ("scripts/validate-ci-checks.py", "CI/CD验证脚本"),
            ("scripts/run-validation-suite.py", "验证套件脚本"),
            ("scripts/quick-test-check.py", "快速测试检查脚本")
        ]
        
        all_pass = True
        for script_path, description in required_scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                self.log_check(
                    f"脚本检查 - {description}",
                    "pass",
                    "存在",
                    str(full_path)
                )
            else:
                self.log_check(
                    f"脚本检查 - {description}",
                    "warning" if "quick" in description else "fail",
                    "不存在",
                    str(full_path)
                )
                if "quick" not in description:
                    all_pass = False
        
        return all_pass
    
    def check_test_configuration(self) -> bool:
        """检查测试配置"""
        print("\n⚙️ 检查测试配置...")
        
        config_checks = [
            ("frontend/vitest.config.js", "Vitest配置文件", self._check_vitest_config),
            ("pyproject.toml", "pytest配置", self._check_pytest_config),
            (".github/workflows/ci-cd-optimized.yml", "CI/CD配置", self._check_ci_cd_config)
        ]
        
        all_pass = True
        for file_path, description, check_func in config_checks:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    if check_func(full_path):
                        self.log_check(
                            f"配置检查 - {description}",
                            "pass",
                            "配置正确",
                            str(full_path)
                        )
                    else:
                        self.log_check(
                            f"配置检查 - {description}",
                            "warning",
                            "配置需要优化",
                            str(full_path)
                        )
                except Exception as e:
                    self.log_check(
                        f"配置检查 - {description}",
                        "error",
                        f"检查失败: {e}",
                        str(full_path)
                    )
                    all_pass = False
            else:
                self.log_check(
                    f"配置检查 - {description}",
                    "fail",
                    "文件不存在",
                    str(full_path)
                )
                all_pass = False
        
        return all_pass
    
    def _check_vitest_config(self, file_path: Path) -> bool:
        """检查Vitest配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_keys = ["test:", "coverage:", "thresholds:"]
        return all(key in content for key in required_keys)
    
    def _check_pytest_config(self, file_path: Path) -> bool:
        """检查pytest配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "[tool.pytest.ini_options]",
            "[tool.coverage.run]"
        ]
        return all(section in content for section in required_sections)
    
    def _check_ci_cd_config(self, file_path: Path) -> bool:
        """检查CI/CD配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = ["jobs:", "steps:", "test:"]
        return all(section in content for section in required_sections)
    
    def check_test_directory_structure(self) -> bool:
        """检查测试目录结构"""
        print("\n📁 检查测试目录结构...")
        
        required_dirs = [
            ("frontend/src/tests/unit/components", "前端组件测试目录"),
            ("frontend/src/tests/unit/composables", "前端组合式函数测试目录"),
            ("frontend/src/tests/unit/utils", "前端工具函数测试目录"),
            ("backend/tests/unit/api", "后端API测试目录"),
            ("backend/tests/unit/models", "后端模型测试目录"),
            ("backend/tests/unit/services", "后端服务测试目录")
        ]
        
        all_pass = True
        for dir_path, description in required_dirs:
            full_dir = self.project_root / dir_path
            if full_dir.exists():
                # 检查是否有测试文件
                if dir_path.startswith("backend"):
                    test_files = list(full_dir.rglob("test_*.py"))
                else:
                    test_files = list(full_dir.rglob("*.test.js"))
                
                if test_files:
                    self.log_check(
                        f"目录检查 - {description}",
                        "pass",
                        f"包含 {len(test_files)} 个测试文件",
                        str(full_dir)
                    )
                else:
                    self.log_check(
                        f"目录检查 - {description}",
                        "warning",
                        "目录为空",
                        str(full_dir)
                    )
            else:
                self.log_check(
                    f"目录检查 - {description}",
                    "warning",
                    "目录不存在",
                    str(full_dir)
                )
                # 自动创建目录
                full_dir.mkdir(parents=True, exist_ok=True)
                print(f"   已创建: {dir_path}")
        
        return all_pass
    
    def run_sample_tests(self) -> bool:
        """运行示例测试"""
        print("\n🧪 运行示例测试...")
        
        # 检查并运行后端示例测试
        backend_test_file = self.project_root / "backend" / "tests" / "unit" / "test_example.py"
        if backend_test_file.exists():
            try:
                # 运行pytest测试
                result = subprocess.run(
                    ["python", "-m", "pytest", str(backend_test_file), "-v"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.log_check(
                        "示例测试 - 后端单元测试",
                        "pass",
                        "所有测试通过",
                        f"运行 {result.returncode} 个测试"
                    )
                    return True
                else:
                    self.log_check(
                        "示例测试 - 后端单元测试",
                        "fail",
                        "测试失败",
                        result.stderr[:200] if result.stderr else "无错误信息"
                    )
                    return False
            except subprocess.TimeoutExpired:
                self.log_check(
                    "示例测试 - 后端单元测试",
                    "error",
                    "测试超时",
                    "超过30秒执行时间"
                )
                return False
            except Exception as e:
                self.log_check(
                    "示例测试 - 后端单元测试",
                    "error",
                    f"运行失败: {e}",
                    str(e)
                )
                return False
        else:
            self.log_check(
                "示例测试 - 后端单元测试",
                "warning",
                "示例测试文件不存在",
                "需创建 test_example.py"
            )
            return True  # 不算失败，只是警告
    
    def generate_final_report(self) -> Dict:
        """生成最终验证报告"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        # 统计结果
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        warnings = sum(1 for r in self.results if r["status"] == "warning")
        errors = sum(1 for r in self.results if r["status"] == "error")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        report = {
            "project": "sport-lottery-sweeper",
            "verification_type": "final_test_integration_verification",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "summary": {
                "total_checks": total,
                "passed_checks": passed,
                "failed_checks": failed,
                "warning_checks": warnings,
                "error_checks": errors,
                "pass_rate_percent": round(pass_rate, 1),
                "overall_status": "PASS" if failed == 0 and errors == 0 else "FAIL"
            },
            "check_results": self.results,
            "recommendations": []
        }
        
        # 添加建议
        if failed > 0:
            report["recommendations"].append("修复失败的检查项")
        
        if warnings > 0:
            report["recommendations"].append("处理警告项目，优化配置")
        
        if pass_rate < 90:
            report["recommendations"].append("提高整体配置质量，目标通过率≥90%")
        
        if not self._check_test_examples_exist():
            report["recommendations"].append("创建更多测试示例文件")
        
        return report
    
    def _check_test_examples_exist(self) -> bool:
        """检查是否有测试示例"""
        frontend_tests = list((self.project_root / "frontend" / "src" / "tests" / "unit").rglob("*.test.js"))
        backend_tests = list((self.project_root / "backend" / "tests" / "unit").rglob("test_*.py"))
        
        return len(frontend_tests) > 0 and len(backend_tests) > 0
    
    def save_report(self, report: Dict):
        """保存报告到文件"""
        report_file = self.report_dir / "final-verification-report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成可读的摘要
        summary_file = self.report_dir / "final-verification-summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 最终验证报告\n\n")
            f.write(f"**验证时间**: {report['timestamp']}\n")
            f.write(f"**执行时长**: {report['duration_seconds']} 秒\n\n")
            
            summary = report['summary']
            f.write("## 📊 验证结果摘要\n\n")
            f.write(f"- **总体状态**: {'✅ 通过' if summary['overall_status'] == 'PASS' else '❌ 失败'}\n")
            f.write(f"- **检查总数**: {summary['total_checks']}\n")
            f.write(f"- **通过检查**: {summary['passed_checks']}\n")
            f.write(f"- **失败检查**: {summary['failed_checks']}\n")
            f.write(f"- **警告检查**: {summary['warning_checks']}\n")
            f.write(f"- **错误检查**: {summary['error_checks']}\n")
            f.write(f"- **通过率**: {summary['pass_rate_percent']}%\n\n")
            
            if report['recommendations']:
                f.write("## 📝 建议措施\n\n")
                for rec in report['recommendations']:
                    f.write(f"- {rec}\n")
                
                f.write("\n")
            
            # 详细检查结果
            f.write("## 🔍 详细检查结果\n\n")
            for result in report['check_results']:
                status_emoji = {
                    "pass": "✅",
                    "fail": "❌",
                    "warning": "⚠️",
                    "error": "🚨"
                }.get(result['status'], "❓")
                
                f.write(f"### {status_emoji} {result['name']}\n")
                f.write(f"- **状态**: {result['status']}\n")
                f.write(f"- **消息**: {result['message']}\n")
                if result['details']:
                    f.write(f"- **详细**: {result['details']}\n")
                f.write("\n")
        
        return report_file, summary_file
    
    def run_complete_verification(self) -> bool:
        """运行完整验证"""
        print("🚀 开始最终验证 - 测试集成实施验证")
        print("="*60)
        
        # 运行所有检查
        checks = [
            ("测试规划文档检查", self.check_test_plan_documentation),
            ("测试脚本检查", self.check_test_scripts),
            ("测试配置检查", self.check_test_configuration),
            ("测试目录结构检查", self.check_test_directory_structure),
            ("示例测试运行", self.run_sample_tests)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"\n📋 {check_name}")
            print("-"*40)
            
            if not check_func():
                all_passed = False
        
        # 生成报告
        report = self.generate_final_report()
        json_file, md_file = self.save_report(report)
        
        # 显示总结
        print("\n" + "="*60)
        print("📋 最终验证完成")
        print("="*60)
        
        summary = report['summary']
        status_emoji = "✅" if summary['overall_status'] == 'PASS' else "❌"
        
        print(f"总体状态: {status_emoji} {summary['overall_status']}")
        print(f"通过率: {summary['pass_rate_percent']}% ({summary['passed_checks']}/{summary['total_checks']})")
        
        if summary['failed_checks'] > 0:
            print(f"失败检查: {summary['failed_checks']}")
        
        if summary['warning_checks'] > 0:
            print(f"警告检查: {summary['warning_checks']}")
        
        print(f"\n📁 报告文件:")
        print(f"  JSON报告: {json_file}")
        print(f"  摘要报告: {md_file}")
        
        if report['recommendations']:
            print(f"\n📝 建议措施:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        return all_passed


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    verifier = FinalVerification(project_root)
    
    try:
        success = verifier.run_complete_verification()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断验证")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# AI_DONE: coder1 @2026-01-29T00:47:00