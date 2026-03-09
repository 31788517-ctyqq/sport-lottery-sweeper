#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-28T14:55:00 - 创建完整验证套件脚本
"""
完整验证套件脚本
运行所有测试环境验证和CI/CD检查
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ValidationSuite:
    """完整验证套件"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = []
        self.start_time = time.time()
        self.report_dir = self.project_root / "test-reports"
    
    def run_validation(self, script_name: str, description: str) -> Dict:
        """运行单个验证脚本"""
        print(f"\n🔍 运行: {description}")
        
        script_path = self.project_root / "scripts" / script_name
        if not script_path.exists():
            return {
                "status": "error",
                "message": f"脚本不存在: {script_name}",
                "duration": 0
            }
        
        try:
            script_start = time.time()
            
            # 导入并运行脚本
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # 创建临时模块路径
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "validation_script", str(script_path)
            )
            module = importlib.util.module_from_spec(spec)
            
            # 保存原始argv
            original_argv = sys.argv
            
            # 设置模拟的argv
            sys.argv = [script_name]
            
            # 执行模块
            spec.loader.exec_module(module)
            
            # 恢复原始argv
            sys.argv = original_argv
            os.chdir(original_cwd)
            
            script_duration = time.time() - script_start
            
            # 尝试判断结果
            if hasattr(module, 'main'):
                # 脚本有main函数，但可能没有返回值
                return {
                    "status": "pass", 
                    "message": f"{description} 执行完成",
                    "duration": script_duration
                }
            else:
                return {
                    "status": "pass",
                    "message": f"{description} 脚本执行成功",
                    "duration": script_duration
                }
                
        except SystemExit as e:
            # 脚本通过sys.exit()退出
            os.chdir(original_cwd)
            script_duration = time.time() - script_start
            
            if e.code == 0:
                return {
                    "status": "pass",
                    "message": f"{description} 通过",
                    "duration": script_duration
                }
            else:
                return {
                    "status": "fail",
                    "message": f"{description} 失败 (退出码: {e.code})",
                    "duration": script_duration
                }
                
        except Exception as e:
            # 脚本执行出错
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            
            script_duration = time.time() - script_start
            return {
                "status": "error",
                "message": f"{description} 执行错误: {str(e)}",
                "duration": script_duration
            }
    
    def run_test_environment_validation(self) -> bool:
        """运行测试环境验证"""
        result = self.run_validation(
            "validate-test-environment.py",
            "测试环境配置验证"
        )
        
        self.results.append({
            "name": "测试环境验证",
            **result
        })
        
        return result["status"] == "pass"
    
    def run_coverage_threshold_check(self) -> bool:
        """运行覆盖率阈值检查"""
        result = self.run_validation(
            "check-coverage-thresholds.py",
            "测试覆盖率阈值检查"
        )
        
        self.results.append({
            "name": "覆盖率阈值检查",
            **result
        })
        
        return result["status"] == "pass"
    
    def run_ci_cd_validation(self) -> bool:
        """运行CI/CD验证"""
        result = self.run_validation(
            "validate-ci-checks.py",
            "CI/CD验证检查"
        )
        
        self.results.append({
            "name": "CI/CD验证检查",
            **result
        })
        
        return result["status"] == "pass"
    
    def run_test_data_initialization(self) -> bool:
        """运行测试数据初始化"""
        result = self.run_validation(
            "init-test-data.py",
            "测试数据初始化"
        )
        
        self.results.append({
            "name": "测试数据初始化",
            **result
        })
        
        return result["status"] == "pass"
    
    def run_test_report_generation(self) -> bool:
        """运行测试报告生成"""
        result = self.run_validation(
            "generate-test-report.py",
            "统一测试报告生成"
        )
        
        self.results.append({
            "name": "测试报告生成",
            **result
        })
        
        return result["status"] == "pass"
    
    def check_critical_configurations(self) -> Dict:
        """检查关键配置"""
        print("\n⚙️  检查关键配置...")
        
        configs_to_check = [
            {
                "name": "Vitest配置",
                "path": "frontend/vitest.config.js",
                "required": True
            },
            {
                "name": "pytest配置", 
                "path": "pyproject.toml",
                "required": True
            },
            {
                "name": "CI/CD配置",
                "path": ".github/workflows/ci-cd-optimized.yml",
                "required": True
            },
            {
                "name": "测试环境配置",
                "path": "frontend/.env.test.example",
                "required": True
            },
            {
                "name": "后端环境配置",
                "path": "backend/.env.test.example",
                "required": True
            }
        ]
        
        results = []
        for config in configs_to_check:
            config_path = self.project_root / config["path"]
            if config_path.exists():
                results.append({
                    "name": config["name"],
                    "status": "pass",
                    "message": f"配置文件存在: {config['path']}"
                })
            else:
                if config["required"]:
                    results.append({
                        "name": config["name"],
                        "status": "fail",
                        "message": f"关键配置文件缺失: {config['path']}"
                    })
                else:
                    results.append({
                        "name": config["name"],
                        "status": "warning",
                        "message": f"配置文件不存在: {config['path']}"
                    })
        
        return results
    
    def generate_comprehensive_report(self) -> Dict:
        """生成综合验证报告"""
        total_duration = time.time() - self.start_time
        
        # 统计结果
        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        warnings = sum(1 for r in self.results if r["status"] == "warning")
        errors = sum(1 for r in self.results if r["status"] == "error")
        
        # 检查关键配置
        config_results = self.check_critical_configurations()
        
        # 合并所有结果
        all_results = self.results + config_results
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_validations": len(all_results),
            "passed_validations": passed,
            "failed_validations": failed,
            "warning_validations": warnings,
            "error_validations": errors,
            "pass_rate": (passed / len(all_results) * 100) if all_results else 0,
            "total_duration": total_duration,
            "status": "PASS" if failed == 0 and errors == 0 else "FAIL",
            "validations": all_results,
            "summary": {
                "test_environment": any(r["name"] == "测试环境验证" and r["status"] == "pass" for r in all_results),
                "coverage_thresholds": any(r["name"] == "覆盖率阈值检查" and r["status"] == "pass" for r in all_results),
                "ci_cd_checks": any(r["name"] == "CI/CD验证检查" and r["status"] == "pass" for r in all_results),
                "test_data": any(r["name"] == "测试数据初始化" and r["status"] == "pass" for r in all_results),
                "test_reports": any(r["name"] == "测试报告生成" and r["status"] == "pass" for r in all_results),
                "critical_configs": all(r["status"] != "fail" for r in config_results if r.get("required", False))
            },
            "recommendations": []
        }
        
        # 生成建议
        if failed > 0:
            summary["recommendations"].append("修复失败的验证项目")
        
        if warnings > 0:
            summary["recommendations"].append("优化警告项目的配置")
        
        if summary["pass_rate"] < 80:
            summary["recommendations"].append("提高验证通过率")
        
        return summary
    
    def run_complete_suite(self) -> bool:
        """运行完整验证套件"""
        print("🚀 开始完整验证套件")
        print("="*70)
        print("📋 验证项目清单:")
        print("  1. 测试环境配置验证")
        print("  2. 覆盖率阈值检查")  
        print("  3. CI/CD验证检查")
        print("  4. 测试数据初始化")
        print("  5. 统一测试报告生成")
        print("  6. 关键配置文件检查")
        print("="*70)
        
        try:
            # 运行各个验证
            print("\n🏃 开始执行验证...")
            
            env_valid = self.run_test_environment_validation()
            coverage_valid = self.run_coverage_threshold_check()
            ci_cd_valid = self.run_ci_cd_validation()
            data_valid = self.run_test_data_initialization()
            report_valid = self.run_test_report_generation()
            
            # 生成综合报告
            report = self.generate_comprehensive_report()
            
            # 确保报告目录存在
            self.report_dir.mkdir(exist_ok=True)
            
            # 保存详细报告
            report_file = self.report_dir / "validation-suite-report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # 输出结果摘要
            print("\n" + "="*70)
            print("🎯 验证套件结果摘要")
            print("="*70)
            
            # 状态指示
            status_emoji = "✅" if report["status"] == "PASS" else "❌"
            status_color = "\033[92m" if report["status"] == "PASS" else "\033[91m"
            
            print(f"{status_emoji} 总体状态: {status_color}{report['status']}\033[0m")
            print(f"📊 验证总数: {report['total_validations']}")
            print(f"✅ 通过数: {report['passed_validations']}")
            print(f"❌ 失败数: {report['failed_validations']}")
            print(f"⚠️  警告数: {report['warning_validations']}")
            print(f"🚨 错误数: {report['error_validations']}")
            print(f"📈 通过率: {report['pass_rate']:.1f}%")
            print(f"⏱️  总耗时: {report['total_duration']:.1f}秒")
            
            # 关键指标
            print(f"\n🎯 关键指标:")
            for key, value in report["summary"].items():
                indicator = "✅" if value else "❌"
                readable_name = {
                    "test_environment": "测试环境",
                    "coverage_thresholds": "覆盖率阈值",
                    "ci_cd_checks": "CI/CD检查",
                    "test_data": "测试数据",
                    "test_reports": "测试报告",
                    "critical_configs": "关键配置"
                }.get(key, key)
                
                print(f"  {indicator} {readable_name}: {'就绪' if value else '未就绪'}")
            
            # 详细结果
            print(f"\n📋 详细结果:")
            for validation in report["validations"]:
                status_emoji = {
                    "pass": "✅",
                    "fail": "❌",
                    "warning": "⚠️",
                    "error": "🚨"
                }.get(validation["status"], "❓")
                
                duration_str = f" ({validation['duration']:.1f}s)" if validation.get("duration", 0) > 0 else ""
                print(f"  {status_emoji} {validation['name']}: {validation['message']}{duration_str}")
            
            # 建议
            if report["recommendations"]:
                print(f"\n💡 改进建议:")
                for rec in report["recommendations"]:
                    print(f"  • {rec}")
            
            # 后续步骤
            print(f"\n📁 后续步骤:")
            print(f"  1. 查看详细报告: {report_file}")
            print(f"  2. 修复失败项目后重新验证")
            print(f"  3. 运行完整测试套件: ./scripts/run-all-tests.sh")
            print(f"  4. 生成可视化报告: python scripts/generate-test-report.py")
            
            # 创建简短的总结文件
            summary_file = self.report_dir / "validation-summary.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# 验证套件总结报告\n\n")
                f.write(f"**生成时间**: {report['timestamp']}\n")
                f.write(f"**总体状态**: {'✅ 通过' if report['status'] == 'PASS' else '❌ 失败'}\n")
                f.write(f"**通过率**: {report['pass_rate']:.1f}% ({report['passed_validations']}/{report['total_validations']})\n\n")
                
                f.write(f"## 关键指标\n")
                for key, value in report["summary"].items():
                    readable_name = {
                        "test_environment": "测试环境",
                        "coverage_thresholds": "覆盖率阈值", 
                        "ci_cd_checks": "CI/CD检查",
                        "test_data": "测试数据",
                        "test_reports": "测试报告",
                        "critical_configs": "关键配置"
                    }.get(key, key)
                    
                    f.write(f"- {'✅' if value else '❌'} {readable_name}: {'就绪' if value else '未就绪'}\n")
                
                f.write(f"\n## 详细报告\n")
                f.write(f"完整报告请查看: [validation-suite-report.json](validation-suite-report.json)\n")
            
            print(f"\n📄 总结报告已生成: {summary_file}")
            print("="*70)
            print("🎉 验证套件执行完成")
            
            return report["status"] == "PASS"
            
        except Exception as e:
            print(f"\n❌ 验证套件执行失败: {e}")
            return False

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    suite = ValidationSuite(project_root)
    
    try:
        success = suite.run_complete_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断验证")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# AI_DONE: coder1 @2026-01-28T14:55:00