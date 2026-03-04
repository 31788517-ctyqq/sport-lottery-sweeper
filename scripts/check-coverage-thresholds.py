#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-28T14:31:00 - 创建覆盖率阈值检查脚本
"""
测试覆盖率阈值检查脚本
检查前后端测试覆盖率是否满足最低要求
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple

# 覆盖率阈值配置
COVERAGE_THRESHOLDS = {
    "frontend": {
        "statements": 80,
        "branches": 75,
        "functions": 80,
        "lines": 80
    },
    "backend": {
        "statements": 80,
        "branches": 70,
        "functions": 80,
        "lines": 80
    }
}

class CoverageChecker:
    """覆盖率检查器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = {
            "frontend": {"passed": False, "metrics": {}, "message": ""},
            "backend": {"passed": False, "metrics": {}, "message": ""}
        }
    
    def check_frontend_coverage(self) -> bool:
        """检查前端覆盖率"""
        print("📊 检查前端覆盖率...")
        
        coverage_file = self.project_root / "frontend" / "coverage" / "coverage-summary.json"
        lcov_file = self.project_root / "frontend" / "coverage" / "lcov.info"
        
        metrics = {}
        
        # 尝试从 coverage-summary.json 读取
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "total" in data:
                        total = data["total"]
                        metrics = {
                            "statements": total.get("statements", {}).get("pct", 0),
                            "branches": total.get("branches", {}).get("pct", 0),
                            "functions": total.get("functions", {}).get("pct", 0),
                            "lines": total.get("lines", {}).get("pct", 0)
                        }
            except Exception as e:
                print(f"⚠️  读取前端覆盖率文件失败: {e}")
        
        # 如果从JSON读取失败，尝试从lcov.info读取
        if not metrics and lcov_file.exists():
            try:
                with open(lcov_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 解析lcov格式（简化版）
                    total_lines = 0
                    covered_lines = 0
                    for line in lines:
                        if line.startswith("LF:"):
                            total_lines = int(line.split(":")[1])
                        elif line.startswith("LH:"):
                            covered_lines = int(line.split(":")[1])
                    
                    if total_lines > 0:
                        line_coverage = (covered_lines / total_lines) * 100
                        metrics = {
                            "statements": line_coverage,
                            "branches": line_coverage,
                            "functions": line_coverage,
                            "lines": line_coverage
                        }
            except Exception as e:
                print(f"⚠️  解析lcov文件失败: {e}")
        
        if not metrics:
            print("❌ 无法获取前端覆盖率数据")
            self.results["frontend"]["message"] = "无法获取覆盖率数据"
            return False
        
        # 检查阈值
        thresholds = COVERAGE_THRESHOLDS["frontend"]
        passed = True
        messages = []
        
        print(f"📈 前端覆盖率指标:")
        for metric, value in metrics.items():
            threshold = thresholds.get(metric, 0)
            status = "✅" if value >= threshold else "❌"
            print(f"  - {metric}: {value:.1f}% ({status} >= {threshold}%)")
            
            if value < threshold:
                passed = False
                messages.append(f"{metric}覆盖率不足: {value:.1f}% < {threshold}%")
        
        self.results["frontend"]["metrics"] = metrics
        self.results["frontend"]["passed"] = passed
        self.results["frontend"]["message"] = "; ".join(messages) if messages else "通过"
        
        return passed
    
    def check_backend_coverage(self) -> bool:
        """检查后端覆盖率"""
        print("📊 检查后端覆盖率...")
        
        coverage_xml = self.project_root / "backend" / "coverage.xml"
        htmlcov_dir = self.project_root / "backend" / "htmlcov"
        
        metrics = {}
        
        # 从 coverage.xml 读取
        if coverage_xml.exists():
            try:
                tree = ET.parse(coverage_xml)
                root = tree.getroot()
                
                # 解析coverage.xml格式
                for elem in root.iter("coverage"):
                    line_rate = float(elem.attrib.get("line-rate", 0)) * 100
                    branch_rate = float(elem.attrib.get("branch-rate", 0)) * 100
                    
                    metrics = {
                        "statements": line_rate,
                        "branches": branch_rate,
                        "functions": line_rate,  # 简化处理
                        "lines": line_rate
                    }
                    
                # 如果没有找到，尝试从其他格式解析
                if not metrics:
                    for elem in root.iter("total"):
                        for child in elem:
                            if child.tag == "lines":
                                line_rate = float(child.attrib.get("percentage", 0))
                                metrics = {
                                    "statements": line_rate,
                                    "branches": line_rate,
                                    "functions": line_rate,
                                    "lines": line_rate
                                }
            except Exception as e:
                print(f"⚠️  解析后端覆盖率XML失败: {e}")
        
        # 如果从XML读取失败，检查htmlcov目录是否存在
        if not metrics and htmlcov_dir.exists():
            print("ℹ️  后端HTML覆盖率报告存在，但无法解析详细指标")
            metrics = {
                "statements": 0,
                "branches": 0,
                "functions": 0,
                "lines": 0
            }
        
        if not metrics:
            print("❌ 无法获取后端覆盖率数据")
            self.results["backend"]["message"] = "无法获取覆盖率数据"
            return False
        
        # 检查阈值
        thresholds = COVERAGE_THRESHOLDS["backend"]
        passed = True
        messages = []
        
        print(f"📈 后端覆盖率指标:")
        for metric, value in metrics.items():
            threshold = thresholds.get(metric, 0)
            status = "✅" if value >= threshold else "❌"
            print(f"  - {metric}: {value:.1f}% ({status} >= {threshold}%)")
            
            if value < threshold:
                passed = False
                messages.append(f"{metric}覆盖率不足: {value:.1f}% < {threshold}%")
        
        self.results["backend"]["metrics"] = metrics
        self.results["backend"]["passed"] = passed
        self.results["backend"]["message"] = "; ".join(messages) if messages else "通过"
        
        return passed
    
    def generate_report(self) -> Dict:
        """生成检查报告"""
        print("\n" + "="*50)
        print("📋 覆盖率检查报告")
        print("="*50)
        
        total_passed = 0
        total_tests = 0
        
        for component, result in self.results.items():
            total_tests += 1
            if result["passed"]:
                total_passed += 1
            
            status = "✅ 通过" if result["passed"] else "❌ 失败"
            print(f"\n{component.upper()}: {status}")
            
            if result["metrics"]:
                for metric, value in result["metrics"].items():
                    print(f"  - {metric}: {value:.1f}%")
            
            if result["message"]:
                print(f"  📝 {result['message']}")
        
        print("\n" + "="*50)
        overall_passed = total_passed == total_tests
        overall_status = "✅ 所有覆盖率检查通过" if overall_passed else "❌ 覆盖率检查失败"
        print(f"总体状态: {overall_status} ({total_passed}/{total_tests})")
        print("="*50)
        
        return {
            "overall_passed": overall_passed,
            "components": self.results,
            "summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_tests - total_passed
            }
        }
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("🚀 开始运行覆盖率阈值检查")
        print("="*50)
        
        frontend_passed = self.check_frontend_coverage()
        print()
        backend_passed = self.check_backend_coverage()
        
        report = self.generate_report()
        
        return report["overall_passed"]

def main():
    """主函数"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    checker = CoverageChecker(project_root)
    
    try:
        passed = checker.run_all_checks()
        sys.exit(0 if passed else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断检查")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# AI_DONE: coder1 @2026-01-28T14:31:00