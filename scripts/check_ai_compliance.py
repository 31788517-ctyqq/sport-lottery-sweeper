#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI合规检查器 - 确保AI遵循开发规范
AI_WORKING: reviewer1 @2026-01-25T00:00:00 - 创建AI合规检查器，验证编码规范和协同协议
"""

import os
import re
import ast
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class AICheckCompliance:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.compliance_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'violations': [],
            'recommendations': [],
            'score': 0
        }
        
        # 编码规范规则
        self.rules = {
            'utf8_encoding': {
                'description': 'Python/JS文件必须使用UTF-8编码',
                'severity': 'high'
            },
            'path_aliases': {
                'description': '必须使用路径别名，禁止硬编码相对路径',
                'severity': 'high'
            },
            'ai_comments': {
                'description': 'AI修改代码必须添加规范注释',
                'severity': 'medium'
            },
            'file_locks': {
                'description': '修改文件前必须检查文件锁',
                'severity': 'high'
            },
            'naming_convention': {
                'description': '遵循项目命名规范',
                'severity': 'medium'
            }
        }
    
    def check_utf8_encoding(self) -> Dict[str, Any]:
        """检查文件编码规范"""
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        # 检查Python文件
        python_files = list(self.project_root.rglob('*.py'))
        for py_file in python_files[:50]:  # 限制检查数量
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查是否有UTF-8声明
                    if '# -*- coding: utf-8 -*-' not in content and '# coding=utf-8' not in content:
                        # 尝试用UTF-8读取，如果失败则说明编码有问题
                        result['issues'].append({
                            'file': str(py_file),
                            'issue': '缺少UTF-8编码声明',
                            'severity': 'medium'
                        })
                        result['failed'] += 1
                    else:
                        result['passed'] += 1
            except UnicodeDecodeError:
                result['issues'].append({
                    'file': str(py_file),
                    'issue': '文件不是有效的UTF-8编码',
                    'severity': 'high'
                })
                result['failed'] += 1
            except Exception as e:
                result['issues'].append({
                    'file': str(py_file),
                    'issue': f'检查失败: {str(e)}',
                    'severity': 'low'
                })
        
        # 检查JavaScript/TypeScript文件
        js_files = list(self.project_root.rglob('*.js')) + list(self.project_root.rglob('*.ts')) + list(self.project_root.rglob('*.vue'))
        for js_file in js_files[:30]:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    result['passed'] += 1
            except UnicodeDecodeError:
                result['issues'].append({
                    'file': str(js_file),
                    'issue': '文件不是有效的UTF-8编码',
                    'severity': 'high'
                })
                result['failed'] += 1
        
        self.compliance_results['checks']['utf8_encoding'] = result
        return result
    
    def check_path_aliases(self) -> Dict[str, Any]:
        """检查路径别名使用情况"""
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        # 检查前端文件中的路径使用
        frontend_src = self.project_root / 'frontend' / 'src'
        if frontend_src.exists():
            js_vue_files = list(frontend_src.rglob('*.js')) + list(frontend_src.rglob('*.vue')) + list(frontend_src.rglob('*.ts'))
            
            for file_path in js_vue_files[:20]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 检查是否使用了相对路径导入
                        relative_imports = re.findall(r"from\s+['\"]\.\./", content)
                        relative_imports.extend(re.findall(r'import\s+.*\s+from\s+["\'].\./', content))
                        
                        if relative_imports:
                            result['issues'].append({
                                'file': str(file_path),
                                'issue': f'发现相对路径导入: {len(relative_imports)} 处',
                                'details': relative_imports[:3],  # 只显示前3个例子
                                'severity': 'high'
                            })
                            result['failed'] += 1
                        else:
                            result['passed'] += 1
                            
                        # 检查是否使用了@别名
                        if '@/' in content:
                            result['passed'] += 1
                            
                except Exception as e:
                    result['issues'].append({
                        'file': str(file_path),
                        'issue': f'检查失败: {str(e)}',
                        'severity': 'low'
                    })
        
        # 检查后端Python文件的导入
        backend_files = list((self.project_root / 'backend').rglob('*.py'))
        for py_file in backend_files[:20]:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 检查相对导入
                    if re.search(r'from\s+\.+', content) or re.search(r'import\s+\.+', content):
                        result['issues'].append({
                            'file': str(py_file),
                            'issue': '发现相对导入语句',
                            'severity': 'high'
                        })
                        result['failed'] += 1
                    else:
                        result['passed'] += 1
                        
            except Exception as e:
                result['issues'].append({
                    'file': str(py_file),
                    'issue': f'检查失败: {str(e)}',
                    'severity': 'low'
                })
        
        self.compliance_results['checks']['path_aliases'] = result
        return result
    
    def check_ai_comments(self) -> Dict[str, Any]:
        """检查AI代码注释规范"""
        result = {'passed': 0, 'failed': 0, 'issues': [], 'found_comments': []}
        
        # 查找AI注释模式
        ai_patterns = [
            r'# AI_WORKING:\s*\[(\w+)\]\s*@(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}).*?(?=\n#|$)',
            r'# AI_DONE:\s*\[(\w+)\]\s*@(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})',
            r'# AI_CONFLICT:\s*(.*)'
        ]
        
        # 检查最近修改的Python文件
        python_files = list(self.project_root.rglob('*.py'))
        recent_files = python_files[:10]  # 检查最新的10个文件
        
        for py_file in recent_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    found_ai_comments = False
                    for pattern in ai_patterns:
                        matches = re.findall(pattern, content, re.DOTALL)
                        if matches:
                            found_ai_comments = True
                            for match in matches:
                                result['found_comments'].append({
                                    'file': str(py_file),
                                    'type': 'AI_WORKING' if 'AI_WORKING' in pattern else 'AI_DONE' if 'AI_DONE' in pattern else 'AI_CONFLICT',
                                    'match': match
                                })
                    
                    if found_ai_comments:
                        result['passed'] += 1
                    else:
                        # 检查是否是AI可能修改的文件但没有注释
                        if any(keyword in content.lower() for keyword in ['def ', 'class ', 'import ']):
                            result['issues'].append({
                                'file': str(py_file),
                                'issue': '可能是AI修改的文件但缺少AI注释',
                                'severity': 'medium'
                            })
                            result['failed'] += 1
                        else:
                            result['passed'] += 1
                            
            except Exception as e:
                result['issues'].append({
                    'file': str(py_file),
                    'issue': f'检查失败: {str(e)}',
                    'severity': 'low'
                })
        
        self.compliance_results['checks']['ai_comments'] = result
        return result
    
    def check_file_locks(self) -> Dict[str, Any]:
        """检查文件锁状态"""
        result = {'active_locks': 0, 'stale_locks': 0, 'issues': []}
        
        locks_dir = self.project_root / '.codebuddy' / 'locks'
        if locks_dir.exists():
            lock_files = list(locks_dir.glob('*.lock'))
            result['active_locks'] = len(lock_files)
            
            # 这里可以添加检查锁是否过期的逻辑
            # 目前只是统计活跃锁数量
            
            if len(lock_files) > 5:  # 假设超过5个锁可能有问题
                result['issues'].append({
                    'issue': f'发现过多活跃锁文件: {len(lock_files)} 个',
                    'severity': 'medium',
                    'recommendation': '检查是否有僵尸锁需要清理'
                })
        else:
            result['issues'].append({
                'issue': '未找到锁系统目录',
                'severity': 'high',
                'recommendation': '初始化AI协同锁系统'
            })
        
        self.compliance_results['checks']['file_locks'] = result
        return result
    
    def check_project_structure(self) -> Dict[str, Any]:
        """检查项目结构规范性"""
        result = {'passed': 0, 'failed': 0, 'issues': []}
        
        # 检查必需的目录结构
        required_dirs = [
            'backend',
            'frontend',
            'scripts',
            '.codebuddy',
            '.codebuddy/locks',
            '.codebuddy/status'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                result['passed'] += 1
            else:
                result['issues'].append({
                    'item': dir_name,
                    'issue': f'缺少必需目录: {dir_name}',
                    'severity': 'high'
                })
                result['failed'] += 1
        
        # 检查必需的文件
        required_files = [
            'STARTUP_GUIDE.md',
            'PATH_ALIASES.md',
            '.codebuddy/plugin_identities.json',
            'package.json'
        ]
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                result['passed'] += 1
            else:
                result['issues'].append({
                    'item': file_name,
                    'issue': f'缺少必需文件: {file_name}',
                    'severity': 'high'
                })
                result['failed'] += 1
        
        self.compliance_results['checks']['project_structure'] = result
        return result
    
    def calculate_score(self) -> float:
        """计算合规分数"""
        total_checks = 0
        passed_checks = 0
        
        for check_name, check_result in self.compliance_results['checks'].items():
            if isinstance(check_result, dict):
                if 'passed' in check_result and 'failed' in check_result:
                    total_checks += check_result['passed'] + check_result['failed']
                    passed_checks += check_result['passed']
                elif 'active_locks' in check_result:
                    # 对于锁检查，只要没有严重问题就给分
                    if not check_result.get('issues', []):
                        passed_checks += 1
                    total_checks += 1
        
        if total_checks == 0:
            return 0.0
        
        score = (passed_checks / total_checks) * 100
        self.compliance_results['score'] = round(score, 2)
        return score
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有合规检查"""
        print("🔍 开始AI合规检查...")
        
        # 执行各项检查
        self.check_utf8_encoding()
        self.check_path_aliases()
        self.check_ai_comments()
        self.check_file_locks()
        self.check_project_structure()
        
        # 计算分数
        score = self.calculate_score()
        
        # 生成建议
        self._generate_recommendations()
        
        return self.compliance_results
    
    def _generate_recommendations(self):
        """生成改进建议"""
        recommendations = []
        
        # 基于检查结果生成建议
        checks = self.compliance_results['checks']
        
        if checks.get('utf8_encoding', {}).get('failed', 0) > 0:
            recommendations.append({
                'category': '编码规范',
                'priority': 'high',
                'suggestion': '为所有Python/JS文件添加UTF-8编码声明，确保文件使用UTF-8编码保存'
            })
        
        if checks.get('path_aliases', {}).get('failed', 0) > 0:
            recommendations.append({
                'category': '路径规范',
                'priority': 'high',
                'suggestion': '将所有相对路径导入改为使用@别名，参考PATH_ALIASES.md规范'
            })
        
        if checks.get('ai_comments', {}).get('failed', 0) > 0:
            recommendations.append({
                'category': 'AI协作',
                'priority': 'medium',
                'suggestion': 'AI修改代码时必须添加AI_WORKING和AI_DONE注释标记'
            })
        
        if checks.get('file_locks', {}).get('issues', []):
            recommendations.append({
                'category': '协同机制',
                'priority': 'high',
                'suggestion': '检查并修复文件锁系统问题，确保AI协同正常工作'
            })
        
        if self.compliance_results['score'] >= 90:
            recommendations.append({
                'category': '总体评价',
                'priority': 'info',
                'suggestion': '✅ 项目AI合规性优秀，继续保持！'
            })
        elif self.compliance_results['score'] >= 70:
            recommendations.append({
                'category': '总体评价',
                'priority': 'warning',
                'suggestion': '⚠️ 项目AI合规性良好，但还有改进空间'
            })
        else:
            recommendations.append({
                'category': '总体评价',
                'priority': 'critical',
                'suggestion': '❌ 项目AI合规性需要大幅改进，请优先处理高优先级问题'
            })
        
        self.compliance_results['recommendations'] = recommendations
    
    def print_report(self):
        """打印合规报告"""
        results = self.compliance_results
        
        print(f"\n📊 AI合规检查报告")
        print(f"生成时间: {results['timestamp']}")
        print(f"合规分数: {results['score']}/100")
        print("-" * 50)
        
        # 各项检查结果
        for check_name, check_result in results['checks'].items():
            print(f"\n🔸 {check_name.upper().replace('_', ' ')}")
            if isinstance(check_result, dict):
                if 'passed' in check_result and 'failed' in check_result:
                    print(f"  通过: {check_result['passed']}, 失败: {check_result['failed']}")
                elif 'active_locks' in check_result:
                    print(f"  活跃锁: {check_result['active_locks']}")
                
                # 显示问题
                issues = check_result.get('issues', [])
                if issues:
                    print(f"  发现问题: {len(issues)} 个")
                    for issue in issues[:3]:  # 只显示前3个问题
                        severity_icon = {'high': '🚨', 'medium': '⚠️', 'low': 'ℹ️'}.get(issue.get('severity', 'low'), '•')
                        print(f"    {severity_icon} {issue.get('issue', '')}")
        
        # 建议
        print(f"\n💡 改进建议:")
        for rec in results['recommendations']:
            priority_icon = {'critical': '🚨', 'high': '⚠️', 'medium': '💡', 'low': 'ℹ️', 'info': '✅'}.get(rec['priority'], '•')
            print(f"  {priority_icon} [{rec['category']}] {rec['suggestion']}")
        
        # 发现的AI注释
        ai_comments = results['checks'].get('ai_comments', {}).get('found_comments', [])
        if ai_comments:
            print(f"\n🤖 发现的AI注释: {len(ai_comments)} 个")
            for comment in ai_comments[:5]:
                print(f"  - {comment['file']}: {comment['type']}")

def main():
    checker = AICheckCompliance()
    results = checker.run_all_checks()
    checker.print_report()
    
    # 保存结果
    output_file = Path(__file__).parent.parent / '.codebuddy' / 'compliance_reports' / f'compliance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存到: {output_file}")

if __name__ == '__main__':
    main()