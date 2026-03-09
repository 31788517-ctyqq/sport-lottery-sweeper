#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术债务扫描工具
自动识别代码中的技术债务并生成报告
"""
import os
import re
import json
import ast
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class TechnicalDebtScanner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.debt_items = []
        self.scan_timestamp = datetime.now().isoformat()
        
    def scan_python_complexity(self):
        """扫描Python代码复杂度"""
        print("[SCAN] 扫描Python代码复杂度...")
        
        for py_file in self.project_root.rglob("*.py"):
            # 跳过一些目录
            if any(part in str(py_file) for part in [
                ".git", "__pycache__", ".pytest_cache", ".venv", "venv",
                "node_modules", "build", "dist", ".coverage", "alembic/versions"
            ]):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 计算圈复杂度（简化版）
                complexity = self._calculate_complexity(content)
                lines = len(content.split('\n'))
                
                # 检查函数长度
                long_functions = self._find_long_functions(content)
                
                # 检查嵌套深度
                max_nesting = self._find_max_nesting_depth(content)
                
                # 记录债务
                if complexity > 10:
                    self.debt_items.append({
                        "id": f"TD-{datetime.now().strftime('%Y%m%d')}-{len(self.debt_items)+1:04d}",
                        "file": str(py_file.relative_to(self.project_root)),
                        "type": "代码质量",
                        "severity": "P2" if complexity <= 15 else "P1",
                        "category": "高复杂度",
                        "description": f"函数圈复杂度过高: {complexity}",
                        "details": f"总行数: {lines}, 最大嵌套深度: {max_nesting}",
                        "discovered_date": self.scan_timestamp,
                        "estimated_effort": "2-4小时"
                    })
                    
                if long_functions:
                    for func_name, line_count in long_functions[:3]:  # 只记录前3个
                        if line_count > 50:
                            self.debt_items.append({
                                "id": f"TD-{datetime.now().strftime('%Y%m%d')}-{len(self.debt_items)+1:04d}",
                                "file": str(py_file.relative_to(self.project_root)),
                                "type": "代码质量",
                                "severity": "P2",
                                "category": "长函数",
                                "description": f"函数过长: {func_name} ({line_count} 行)",
                                "details": f"建议拆分为多个小函数",
                                "discovered_date": self.scan_timestamp,
                                "estimated_effort": "1-2小时"
                            })
                            
            except Exception as e:
                print(f"[WARNING] 无法分析文件 {py_file}: {e}")
    
    def _calculate_complexity(self, code):
        """计算简化圈复杂度"""
        # 简单计数控制结构
        control_structures = len(re.findall(r'\b(if|elif|else|for|while|except|with)\b', code))
        logical_ops = len(re.findall(r'\b(and|or)\b', code))
        return control_structures + logical_ops + 1
    
    def _find_long_functions(self, code):
        """查找长函数"""
        long_funcs = []
        lines = code.split('\n')
        
        current_func = None
        current_start = None
        
        for i, line in enumerate(lines):
            # 检测函数定义
            func_match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
            if func_match:
                if current_func and current_start:
                    func_length = i - current_start
                    if func_length > 30:  # 超过30行视为长函数
                        long_funcs.append((current_func, func_length))
                
                current_func = func_match.group(1)
                current_start = i
            
            # 检测类定义
            class_match = re.match(r'^\s*class\s+(\w+)\s*[\(:]', line)
            if class_match:
                current_func = None
                current_start = None
        
        return long_funcs
    
    def _find_max_nesting_depth(self, code):
        """查找最大嵌套深度"""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            indent = len(line) - len(line.lstrip())
            depth = indent // 4  # 假设4空格缩进
            max_depth = max(max_depth, depth)
            current_depth = depth
            
        return max_depth
    
    def scan_duplicate_code(self):
        """扫描重复代码（简化版）"""
        print("[SCAN] 扫描重复代码...")
        # 这里可以实现更复杂的重复代码检测逻辑
        # 目前只做简单的TODO/FIXME检测
        
        for py_file in self.project_root.rglob("*.py"):
            if any(part in str(py_file) for part in [".git", "__pycache__"]):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                        self.debt_items.append({
                            "id": f"TD-{datetime.now().strftime('%Y%m%d')}-{len(self.debt_items)+1:04d}",
                            "file": str(py_file.relative_to(self.project_root)),
                            "type": "代码质量",
                            "severity": "P3",
                            "category": "待办事项",
                            "description": f"发现待办注释: {line.strip()}",
                            "line_number": i,
                            "discovered_date": self.scan_timestamp,
                            "estimated_effort": "0.5小时"
                        })
            except Exception:
                continue
    
    def scan_dependencies(self):
        """扫描依赖问题"""
        print("[SCAN] 扫描依赖问题...")
        
        # 检查requirements.txt中的过期依赖
        req_files = [
            self.project_root / "backend" / "requirements.txt",
            self.project_root / "backend" / "requirements-dev.txt",
            self.project_root / "requirements.txt"
        ]
        
        for req_file in req_files:
            if req_file.exists():
                try:
                    result = subprocess.run(
                        ["pip", "list", "--outdated", "--format=json"],
                        capture_output=True, text=True, cwd=self.project_root
                    )
                    
                    if result.stdout:
                        outdated = json.loads(result.stdout)
                        for pkg in outdated[:10]:  # 只报告前10个
                            self.debt_items.append({
                                "id": f"TD-{datetime.now().strftime('%Y%m%d')}-{len(self.debt_items)+1:04d}",
                                "file": str(req_file.relative_to(self.project_root)),
                                "type": "依赖",
                                "severity": "P2",
                                "category": "过期依赖",
                                "description": f"依赖包过期: {pkg['name']} ({pkg['version']} -> {pkg['latest_version']})",
                                "discovered_date": self.scan_timestamp,
                                "estimated_effort": "1小时"
                            })
                except Exception as e:
                    print(f"[WARNING] 无法检查依赖: {e}")
    
    def scan_test_coverage(self):
        """扫描测试覆盖率（如果可用）"""
        print("[SCAN] 检查测试覆盖率...")
        
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    
                if 'totals' in coverage_data:
                    coverage_pct = coverage_data['totals'].get('percent_covered', 0)
                    
                    if coverage_pct < 80:
                        self.debt_items.append({
                            "id": f"TD-{datetime.now().strftime('%Y%m%d')}-{len(self.debt_items)+1:04d}",
                            "file": "测试覆盖率报告",
                            "type": "测试",
                            "severity": "P1" if coverage_pct < 60 else "P2",
                            "category": "低测试覆盖率",
                            "description": f"测试覆盖率过低: {coverage_pct:.1f}%",
                            "details": "建议增加测试用例以提高覆盖率至80%以上",
                            "discovered_date": self.scan_timestamp,
                            "estimated_effort": "4-8小时"
                        })
            except Exception:
                pass
    
    def generate_report(self, output_format="json"):
        """生成技术债务报告"""
        # 统计信息
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for debt in self.debt_items:
            severity_counts[debt["severity"]] += 1
            type_counts[debt["type"]] += 1
            category_counts[debt["category"]] += 1
        
        report = {
            "scan_timestamp": self.scan_timestamp,
            "summary": {
                "total_items": len(self.debt_items),
                "by_severity": dict(severity_counts),
                "by_type": dict(type_counts),
                "by_category": dict(category_counts)
            },
            "items": self.debt_items
        }
        
        if output_format == "json":
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif output_format == "markdown":
            return self._generate_markdown_report(report)
        else:
            return report
    
    def _generate_markdown_report(self, report):
        """生成Markdown格式报告"""
        md = f"""# 技术债务扫描报告

**扫描时间**: {report['scan_timestamp']}  
**发现问题**: {report['summary']['total_items']} 个

## 📊 概览

### 按严重程度分布
"""
        
        for severity, count in report['summary']['by_severity'].items():
            md += f"- **{severity}**: {count} 个\n"
        
        md += "\n### 按类型分布\n"
        for deptype, count in report['summary']['by_type'].items():
            md += f"- **{deptype}**: {count} 个\n"
        
        md += "\n## 📋 详细问题列表\n\n"
        
        for debt in report['items']:
            md += f"""### {debt['id']}: {debt['description']}
- **文件**: {debt['file']}
- **类型**: {debt['type']} ({debt['category']})
- **严重程度**: {debt['severity']}
- **发现时间**: {debt['discovered_date']}
- **预估工作量**: {debt.get('estimated_effort', '待评估')}
"""
            if 'details' in debt:
                md += f"- **详情**: {debt['details']}\n"
            if 'line_number' in debt:
                md += f"- **行号**: {debt['line_number']}\n"
            md += "\n"
        
        return md

def main():
    """主函数"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    output_format = sys.argv[2] if len(sys.argv) > 2 else "json"
    
    scanner = TechnicalDebtScanner(project_root)
    
    print("🔍 开始技术债务扫描...")
    
    # 执行各种扫描
    scanner.scan_python_complexity()
    scanner.scan_duplicate_code()
    scanner.scan_dependencies()
    scanner.scan_test_coverage()
    
    # 生成报告
    report = scanner.generate_report(output_format)
    
    if output_format == "json":
        filename = f"technical_debt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 技术债务报告已生成: {filename}")
    else:
        filename = f"technical_debt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 技术债务报告已生成: {filename}")
    
    # 控制台输出摘要
    data = json.loads(scanner.generate_report("json")) if output_format != "json" else json.loads(report)
    print(f"\n📊 扫描摘要:")
    print(f"   总问题数: {data['summary']['total_items']}")
    print(f"   P0/P1级问题: {data['summary']['by_severity'].get('P0', 0) + data['summary']['by_severity'].get('P1', 0)}")
    print(f"   P2/P3级问题: {data['summary']['by_severity'].get('P2', 0) + data['summary']['by_severity'].get('P3', 0)}")

if __name__ == "__main__":
    main()