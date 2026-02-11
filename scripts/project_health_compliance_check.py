#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目健康度和合规性综合检查脚本
用于检查项目是否符合开发规范和最佳实践
"""

import os
import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ProjectHealthComplianceChecker:
    """项目健康度和合规性检查器"""
    
    def __init__(self):
        self.project_root = project_root
        self.backend_path = project_root / "backend"
        self.frontend_path = project_root / "frontend"
        self.scripts_path = project_root / "scripts"
        self.docs_path = project_root / "docs"
        self.codebuddy_path = project_root / ".codebuddy"
        
        self.check_results = {
            "project_structure": {},
            "file_encoding": {},
            "path_aliases": {},
            "api_routes": {},
            "environment_config": {},
            "documentation": {},
            "ai_compliance": {}
        }
    
    def check_project_structure(self) -> Dict:
        """检查项目结构是否符合规范"""
        logger.info("检查项目结构...")
        
        structure_issues = []
        
        # 检查关键目录是否存在
        required_dirs = [
            self.backend_path,
            self.frontend_path,
            self.scripts_path,
            self.docs_path,
            self.codebuddy_path
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                structure_issues.append(f"缺少目录: {dir_path}")
        
        # 检查关键文件是否存在
        required_files = [
            self.backend_path / "main.py",
            self.frontend_path / "package.json",
            self.frontend_path / "vite.config.js",
            self.project_root / ".env.example",
            self.project_root / "README.md"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                structure_issues.append(f"缺少文件: {file_path}")
        
        # 检查backend目录结构
        backend_subdirs = ["api", "models", "database_utils", "core", "utils"]
        for subdir in backend_subdirs:
            sub_path = self.backend_path / subdir
            if not sub_path.exists():
                structure_issues.append(f"Backend缺少子目录: {subdir}")
        
        result = {
            "status": "fail" if structure_issues else "pass",
            "issues": structure_issues,
            "checked_at": datetime.now().isoformat()
        }
        
        self.check_results["project_structure"] = result
        logger.info(f"项目结构检查完成，发现 {len(structure_issues)} 个问题")
        return result
    
    def check_file_encodings(self) -> Dict:
        """检查关键文件编码是否为UTF-8"""
        logger.info("检查文件编码...")
        
        encoding_issues = []
        
        # 检查Python文件
        python_files = list(self.backend_path.rglob("*.py"))
        python_files.extend(list(self.scripts_path.rglob("*.py")))
        
        for file_path in python_files[:20]:  # 限制检查数量以提高性能
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # 读取前100个字符检查编码
            except UnicodeDecodeError:
                encoding_issues.append(f"编码错误 (非UTF-8): {file_path}")
            except Exception as e:
                encoding_issues.append(f"读取错误: {file_path} - {str(e)}")
        
        # 检查JavaScript/Vue文件
        js_files = list(self.frontend_path.rglob("*.js"))
        js_files.extend(list(self.frontend_path.rglob("*.vue")))
        js_files.extend(list(self.frontend_path.rglob("*.ts")))
        
        for file_path in js_files[:20]:  # 限制检查数量以提高性能
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # 读取前100个字符检查编码
            except UnicodeDecodeError:
                encoding_issues.append(f"编码错误 (非UTF-8): {file_path}")
            except Exception as e:
                encoding_issues.append(f"读取错误: {file_path} - {str(e)}")
        
        result = {
            "status": "fail" if encoding_issues else "pass",
            "issues": encoding_issues,
            "checked_at": datetime.now().isoformat()
        }
        
        self.check_results["file_encoding"] = result
        logger.info(f"文件编码检查完成，发现 {len(encoding_issues)} 个问题")
        return result
    
    def check_path_aliases(self) -> Dict:
        """检查路径别名使用是否符合规范"""
        logger.info("检查路径别名使用...")
        
        alias_issues = []
        
        # 检查前端vite.config.js中的路径别名配置
        vite_config_path = self.frontend_path / "vite.config.js"
        if vite_config_path.exists():
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查是否包含路径别名配置
            if '@' not in content:
                alias_issues.append("vite.config.js中缺少'@'路径别名配置")
        else:
            alias_issues.append("vite.config.js文件不存在")
        
        # 检查前端代码中是否使用了相对路径而非路径别名
        js_vue_files = list(self.frontend_path.rglob("*.js")) + list(self.frontend_path.rglob("*.vue"))
        
        relative_path_pattern = r"from\s+['\"].*(\.\.\/|\.\.\\\\).*['\"]"
        for file_path in js_vue_files[:30]:  # 限制检查数量以提高性能
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            relative_matches = re.findall(relative_path_pattern, content)
            if relative_matches:
                alias_issues.append(f"{file_path.relative_to(self.frontend_path)}: 发现 {len(relative_matches)} 处相对路径使用")
        
        result = {
            "status": "fail" if alias_issues else "pass",
            "issues": alias_issues,
            "checked_at": datetime.now().isoformat()
        }
        
        self.check_results["path_aliases"] = result
        logger.info(f"路径别名检查完成，发现 {len(alias_issues)} 个问题")
        return result
    
    def check_environment_config(self) -> Dict:
        """检查环境配置是否符合规范"""
        logger.info("检查环境配置...")
        
        env_issues = []
        
        # 检查是否存在.env.example
        env_example_path = self.project_root / ".env.example"
        if not env_example_path.exists():
            env_issues.append(".env.example文件不存在")
        else:
            with open(env_example_path, 'r', encoding='utf-8') as f:
                env_content = f.read()
                
            # 检查是否包含关键环境变量
            required_vars = ["SECRET_KEY", "DATABASE_URL", "PORT"]
            for var in required_vars:
                if var not in env_content:
                    env_issues.append(f".env.example中缺少关键变量: {var}")
        
        # 检查是否意外提交了真实.env文件
        env_path = self.project_root / ".env"
        if env_path.exists():
            env_issues.append("警告: .env文件存在于版本控制中，这可能存在安全风险")
        
        result = {
            "status": "fail" if env_issues else "pass",
            "issues": env_issues,
            "checked_at": datetime.now().isoformat()
        }
        
        self.check_results["environment_config"] = result
        logger.info(f"环境配置检查完成，发现 {len(env_issues)} 个问题")
        return result
    
    def check_documentation(self) -> Dict:
        """检查文档完整性"""
        logger.info("检查文档完整性...")
        
        doc_issues = []
        
        # 检查关键文档是否存在
        required_docs = [
            self.project_root / "README.md",
            self.project_root / "PROJECT_STANDARDS.md",
            self.project_root / "PATH_ALIASES.md",
            self.project_root / "STARTUP_GUIDE.md"
        ]
        
        for doc_path in required_docs:
            if not doc_path.exists():
                doc_issues.append(f"缺少文档: {doc_path.name}")
        
        # 检查文档是否包含必要章节
        if (self.project_root / "PROJECT_STANDARDS.md").exists():
            with open(self.project_root / "PROJECT_STANDARDS.md", 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_sections = ["启动文件规范", "路由映射规范", "环境变量规范", "AI协同开发规范"]
            for section in required_sections:
                if section not in content:
                    doc_issues.append(f"PROJECT_STANDARDS.md中缺少章节: {section}")
        
        result = {
            "status": "fail" if doc_issues else "pass",
            "issues": doc_issues,
            "checked_at": datetime.now().isoformat()
        }
        
        self.check_results["documentation"] = result
        logger.info(f"文档检查完成，发现 {len(doc_issues)} 个问题")
        return result
    
    def check_ai_compliance(self) -> Dict:
        """检查AI协同开发合规性"""
        logger.info("检查AI协同开发合规性...")
        
        ai_issues = []
        
        # 检查.codebuddy目录结构
        required_codebuddy_dirs = [
            self.codebuddy_path / "locks",
            self.codebuddy_path / "status",
            self.codebuddy_path / "compliance_reports"
        ]
        
        for dir_path in required_codebuddy_dirs:
            if not dir_path.exists():
                ai_issues.append(f"缺少.codebuddy子目录: {dir_path.name}")
        
        # 检查是否存在协调协议文档
        coordination_doc = self.codebuddy_path / "coordination.md"
        if not coordination_doc.exists():
            ai_issues.append("缺少AI协同协议文档: coordination.md")
        
        # 检查Python文件中是否包含AI工作标记
        python_files = list(self.backend_path.rglob("*.py"))[:20]  # 限制数量
        ai_work_markers_found = 0
        
        for file_path in python_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "# AI_WORKING:" in content:
                ai_work_markers_found += 1
        
        if ai_work_markers_found == 0:
            ai_issues.append("未发现AI工作标记，建议在修改文件时使用# AI_WORKING:注释")
        
        result = {
            "status": "fail" if ai_issues else "pass",
            "issues": ai_issues,
            "ai_work_markers_found": ai_work_markers_found,
            "checked_at": datetime.now().isoformat()
        }
        
        self.check_results["ai_compliance"] = result
        logger.info(f"AI合规性检查完成，发现 {len(ai_issues)} 个问题")
        return result
    
    def run_full_check(self) -> Dict:
        """运行完整的健康度和合规性检查"""
        print("=" * 70)
        print("项目健康度和合规性综合检查")
        print("=" * 70)
        print(f"项目路径: {self.project_root}")
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # 执行所有检查
        self.check_project_structure()
        self.check_file_encodings()
        self.check_path_aliases()
        self.check_environment_config()
        self.check_documentation()
        self.check_ai_compliance()
        
        # 汇总结果
        total_issues = 0
        for category, result in self.check_results.items():
            if 'issues' in result:
                total_issues += len(result['issues'])
        
        print("📋 检查结果汇总:")
        print("-" * 40)
        
        for category, result in self.check_results.items():
            status_icon = "✅" if result['status'] == 'pass' else "❌"
            issues_count = len(result.get('issues', []))
            print(f"{status_icon} {category.replace('_', ' ').title()}: {result['status'].upper()} ({issues_count} issues)")
        
        print("")
        print(f"📊 总体统计:")
        print(f"- 总问题数: {total_issues}")
        print(f"- 检查类别数: {len(self.check_results)}")
        print(f"- 通过检查数: {sum(1 for r in self.check_results.values() if r['status'] == 'pass')}")
        
        print("")
        if total_issues > 0:
            print("⚠️  详细问题列表:")
            print("-" * 20)
            for category, result in self.check_results.items():
                if result.get('issues'):
                    print(f"\n{category.replace('_', ' ').title()}:")
                    for i, issue in enumerate(result['issues'], 1):
                        print(f"  {i}. {issue}")
        
        print("")
        overall_status = "✅ 项目健康度良好" if total_issues == 0 else "⚠️ 项目需要修复问题"
        print(overall_status)
        
        # 保存检查结果到JSON文件
        report_path = self.project_root / "health_compliance_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.check_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 检查报告已保存至: {report_path}")
        
        return total_issues == 0
    
    def generate_fix_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        for category, result in self.check_results.items():
            if result['status'] == 'fail':
                if category == 'project_structure':
                    recommendations.append("重建缺失的项目目录结构")
                elif category == 'file_encoding':
                    recommendations.append("确保所有源文件使用UTF-8编码")
                elif category == 'path_aliases':
                    recommendations.append("统一使用路径别名而非相对路径")
                elif category == 'environment_config':
                    recommendations.append("完善环境配置文件")
                elif category == 'documentation':
                    recommendations.append("补充缺失的文档")
                elif category == 'ai_compliance':
                    recommendations.append("遵循AI协同开发规范")
        
        return recommendations


def run_project_health_check():
    """运行项目健康度检查"""
    checker = ProjectHealthComplianceChecker()
    success = checker.run_full_check()
    
    # 输出修复建议
    recommendations = checker.generate_fix_recommendations()
    if recommendations:
        print("\n💡 修复建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    return success


if __name__ == "__main__":
    success = run_project_health_check()
    sys.exit(0 if success else 1)