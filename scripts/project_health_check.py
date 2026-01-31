#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目健康检查器 - 全面检查项目状态和服务健康度
AI_WORKING: analyzer1 @2026-01-25T00:00:00 - 创建项目健康检查器，提供端口、服务、配置的全方位检查
"""

import os
import sys
import time
import json
import socket
import requests
import psutil
from pathlib import Path
from datetime import datetime

class ProjectHealthCheck:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.health_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'services': {},
            'ports': {},
            'files': {},
            'dependencies': {},
            'ai_coordination': {},
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 配置
        self.frontend_port = 3000
        self.backend_port = 8000
        self.required_files = [
            'STARTUP_GUIDE.md',
            'PATH_ALIASES.md',
            'package.json',
            '.codebuddy/plugin_identities.json',
            'scripts/smart_start.py',
            'scripts/config_scanner.py',
            'scripts/check_ai_compliance.py'
        ]
    
    def check_ports(self) -> Dict[str, Any]:
        """检查端口状态"""
        ports_status = {}
        
        def check_single_port(port, service_name):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                is_available = result != 0
                ports_status[service_name] = {
                    'port': port,
                    'status': 'available' if is_available else 'occupied',
                    'accessible': not is_available
                }
                return is_available
            except Exception as e:
                ports_status[service_name] = {
                    'port': port,
                    'status': 'error',
                    'error': str(e)
                }
                return False
        
        # 检查前端端口
        frontend_free = check_single_port(self.frontend_port, 'frontend')
        
        # 检查后端端口
        backend_free = check_single_port(self.backend_port, 'backend')
        
        self.health_results['ports'] = ports_status
        return ports_status
    
    def check_services(self) -> Dict[str, Any]:
        """检查服务健康状态"""
        services_status = {}
        
        # 检查后端服务
        try:
            response = requests.get(f'http://localhost:{self.backend_port}/health/live', timeout=5)
            if response.status_code == 200:
                services_status['backend'] = {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'details': '服务正常运行'
                }
            else:
                services_status['backend'] = {
                    'status': 'unhealthy',
                    'http_code': response.status_code,
                    'details': '服务响应异常'
                }
        except requests.exceptions.ConnectionError:
            services_status['backend'] = {
                'status': 'offline',
                'details': '服务未启动或端口被占用'
            }
        except Exception as e:
            services_status['backend'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 检查API文档
        try:
            response = requests.get(f'http://localhost:{self.backend_port}/docs', timeout=5)
            if response.status_code == 200:
                services_status['api_docs'] = {
                    'status': 'accessible',
                    'details': 'API文档可访问'
                }
            else:
                services_status['api_docs'] = {
                    'status': 'inaccessible',
                    'http_code': response.status_code
                }
        except Exception as e:
            services_status['api_docs'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 检查前端服务
        try:
            response = requests.get(f'http://localhost:{self.frontend_port}', timeout=5)
            if response.status_code == 200:
                services_status['frontend'] = {
                    'status': 'accessible',
                    'response_time': response.elapsed.total_seconds(),
                    'details': '前端服务可访问'
                }
            else:
                services_status['frontend'] = {
                    'status': 'inaccessible',
                    'http_code': response.status_code
                }
        except requests.exceptions.ConnectionError:
            services_status['frontend'] = {
                'status': 'offline',
                'details': '前端服务未启动'
            }
        except Exception as e:
            services_status['frontend'] = {
                'status': 'error',
                'error': str(e)
            }
        
        self.health_results['services'] = services_status
        return services_status
    
    def check_required_files(self) -> Dict[str, Any]:
        """检查必需文件是否存在"""
        files_status = {'present': [], 'missing': [], 'total': len(self.required_files)}
        
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                files_status['present'].append(file_path)
            else:
                files_status['missing'].append(file_path)
        
        files_status['present_count'] = len(files_status['present'])
        files_status['missing_count'] = len(files_status['missing'])
        files_status['completeness'] = (files_status['present_count'] / files_status['total']) * 100
        
        self.health_results['files'] = files_status
        return files_status
    
    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖配置"""
        deps_status = {'node': {}, 'python': {}, 'overall': 'unknown'}
        
        # 检查Node.js依赖
        frontend_package = self.project_root / 'frontend' / 'package.json'
        if frontend_package.exists():
            try:
                with open(frontend_package, 'r', encoding='utf-8') as f:
                    pkg_data = json.load(f)
                    deps_status['node'] = {
                        'status': 'configured',
                        'dependencies_count': len(pkg_data.get('dependencies', {})),
                        'dev_dependencies_count': len(pkg_data.get('devDependencies', {})),
                        'scripts_available': bool(pkg_data.get('scripts', {}).get('dev'))
                    }
            except Exception as e:
                deps_status['node'] = {'status': 'error', 'error': str(e)}
        else:
            deps_status['node'] = {'status': 'missing', 'error': 'package.json不存在'}
        
        # 检查Python依赖
        requirements = self.project_root / 'requirements.txt'
        pyproject = self.project_root / 'pyproject.toml'
        
        if requirements.exists() or pyproject.exists():
            deps_status['python'] = {'status': 'configured'}
            if requirements.exists():
                with open(requirements, 'r', encoding='utf-8') as f:
                    req_count = len([line for line in f if line.strip() and not line.startswith('#')])
                    deps_status['python']['requirements_count'] = req_count
            if pyproject.exists():
                deps_status['python']['pyproject'] = 'present'
        else:
            deps_status['python'] = {'status': 'missing', 'error': '未找到Python依赖配置'}
        
        # 整体评估
        node_ok = deps_status['node'].get('status') == 'configured'
        python_ok = deps_status['python'].get('status') == 'configured'
        deps_status['overall'] = 'ready' if (node_ok and python_ok) else 'incomplete'
        
        self.health_results['dependencies'] = deps_status
        return deps_status
    
    def check_ai_coordination(self) -> Dict[str, Any]:
        """检查AI协同机制状态"""
        ai_status = {'locks': {}, 'plugins': {}, 'active_plugins': {}, 'overall': 'unknown'}
        
        # 检查锁系统
        locks_dir = self.project_root / '.codebuddy' / 'locks'
        if locks_dir.exists():
            lock_files = list(locks_dir.glob('*.lock'))
            ai_status['locks'] = {
                'status': 'active',
                'active_locks': len(lock_files),
                'lock_files': [f.name for f in lock_files]
            }
        else:
            ai_status['locks'] = {'status': 'missing', 'error': '锁系统目录不存在'}
        
        # 检查插件配置
        plugin_config = self.project_root / '.codebuddy' / 'plugin_identities.json'
        if plugin_config.exists():
            try:
                with open(plugin_config, 'r', encoding='utf-8') as f:
                    plugin_data = json.load(f)
                    ai_status['plugins'] = {
                        'status': 'configured',
                        'registered_plugins': len(plugin_data.get('plugins', {})),
                        'plugin_types': list(plugin_data.get('plugins', {}).keys())
                    }
            except Exception as e:
                ai_status['plugins'] = {'status': 'error', 'error': str(e)}
        else:
            ai_status['plugins'] = {'status': 'missing', 'error': '插件配置文件不存在'}
        
        # 检查活动插件状态
        active_plugins = self.project_root / '.codebuddy' / 'status' / 'active_plugins.json'
        if active_plugins.exists():
            try:
                with open(active_plugins, 'r', encoding='utf-8') as f:
                    active_data = json.load(f)
                    ai_status['active_plugins'] = {
                        'status': 'active',
                        'registered': len(active_data.get('active_plugins', {})),
                        'system_metrics': active_data.get('system_metrics', {})
                    }
            except Exception as e:
                ai_status['active_plugins'] = {'status': 'error', 'error': str(e)}
        else:
            ai_status['active_plugins'] = {'status': 'missing', 'error': '活动插件状态文件不存在'}
        
        # 整体评估
        locks_ok = ai_status['locks'].get('status') == 'active'
        plugins_ok = ai_status['plugins'].get('status') == 'configured'
        active_ok = ai_status['active_plugins'].get('status') == 'active'
        
        if locks_ok and plugins_ok and active_ok:
            ai_status['overall'] = 'fully_functional'
        elif locks_ok or plugins_ok:
            ai_status['overall'] = 'partially_functional'
        else:
            ai_status['overall'] = 'not_functional'
        
        self.health_results['ai_coordination'] = ai_status
        return ai_status
    
    def calculate_health_score(self) -> float:
        """计算健康分数"""
        score = 0
        max_score = 100
        
        # 端口检查 (10分)
        ports = self.health_results['ports']
        if ports.get('backend', {}).get('status') == 'available':
            score += 5
        if ports.get('frontend', {}).get('status') == 'available':
            score += 5
        
        # 服务检查 (30分)
        services = self.health_results['services']
        if services.get('backend', {}).get('status') == 'healthy':
            score += 15
        if services.get('frontend', {}).get('status') == 'accessible':
            score += 10
        if services.get('api_docs', {}).get('status') == 'accessible':
            score += 5
        
        # 文件检查 (20分)
        files = self.health_results['files']
        score += (files.get('completeness', 0) / 100) * 20
        
        # 依赖检查 (20分)
        deps = self.health_results['dependencies']
        if deps.get('node', {}).get('status') == 'configured':
            score += 10
        if deps.get('python', {}).get('status') == 'configured':
            score += 10
        
        # AI协同检查 (20分)
        ai = self.health_results['ai_coordination']
        if ai.get('overall') == 'fully_functional':
            score += 20
        elif ai.get('overall') == 'partially_functional':
            score += 10
        elif ai.get('overall') == 'not_functional':
            score += 0
        
        self.health_results['score'] = min(round(score, 2), max_score)
        return self.health_results['score']
    
    def generate_recommendations(self):
        """生成改进建议"""
        recommendations = []
        
        # 基于健康分数生成建议
        score = self.health_results['score']
        if score >= 90:
            recommendations.append({'priority': 'info', 'text': '🎉 项目健康状况优秀！'})
        elif score >= 70:
            recommendations.append({'priority': 'warning', 'text': '⚠️ 项目健康状况良好，但还有改进空间'})
        else:
            recommendations.append({'priority': 'critical', 'text': '🚨 项目健康状况需要关注，建议立即处理问题'})
        
        # 具体建议
        services = self.health_results['services']
        if services.get('backend', {}).get('status') != 'healthy':
            recommendations.append({'priority': 'high', 'text': '启动后端服务: npm run backend:dev'})
        
        if services.get('frontend', {}).get('status') != 'accessible':
            recommendations.append({'priority': 'high', 'text': '启动前端服务: npm run frontend:dev'})
        
        files = self.health_results['files']
        if files.get('missing_count', 0) > 0:
            recommendations.append({'priority': 'medium', 'text': f'补充缺失文件: {files["missing_count"]} 个'})
        
        ai = self.health_results['ai_coordination']
        if ai.get('overall') != 'fully_functional':
            recommendations.append({'priority': 'medium', 'text': '检查AI协同机制配置'})
        
        self.health_results['recommendations'] = recommendations
    
    def run_full_check(self) -> Dict[str, Any]:
        """运行完整健康检查"""
        print("🏥 开始项目健康检查...")
        
        # 执行各项检查
        self.check_ports()
        self.check_services()
        self.check_required_files()
        self.check_dependencies()
        self.check_ai_coordination()
        
        # 计算分数
        score = self.calculate_health_score()
        
        # 生成建议
        self.generate_recommendations()
        
        # 确定整体状态
        if score >= 90:
            self.health_results['overall_status'] = 'excellent'
        elif score >= 70:
            self.health_results['overall_status'] = 'good'
        elif score >= 50:
            self.health_results['overall_status'] = 'fair'
        else:
            self.health_results['overall_status'] = 'poor'
        
        return self.health_results
    
    def print_health_report(self):
        """打印健康报告"""
        results = self.health_results
        
        status_icons = {
            'excellent': '🟢',
            'good': '🟡', 
            'fair': '🟠',
            'poor': '🔴',
            'unknown': '⚪'
        }
        
        print(f"\n🏥 项目健康报告")
        print(f"检查时间: {results['timestamp']}")
        print(f"整体状态: {status_icons.get(results['overall_status'], '⚪')} {results['overall_status'].upper()}")
        print(f"健康分数: {results['score']}/100")
        print("=" * 60)
        
        # 服务状态
        print(f"\n🌐 服务状态")
        services = results['services']
        for service_name, service_info in services.items():
            status_icon = {'healthy': '✅', 'accessible': '✅', 'offline': '❌', 'unhealthy': '⚠️', 'inaccessible': '❌', 'error': '🚨'}.get(service_info.get('status'), '❓')
            print(f"  {status_icon} {service_name}: {service_info.get('status', 'unknown')}")
            if 'details' in service_info:
                print(f"     {service_info['details']}")
        
        # 端口状态
        print(f"\n🔌 端口状态")
        ports = results['ports']
        for service_name, port_info in ports.items():
            status_icon = {'available': '✅', 'occupied': '⚠️', 'error': '🚨'}.get(port_info.get('status'), '❓')
            print(f"  {status_icon} {service_name} (:{port_info['port']}): {port_info.get('status', 'unknown')}")
        
        # 文件完整性
        print(f"\n📁 文件完整性")
        files = results['files']
        completeness = files.get('completeness', 0)
        print(f"  完整性: {completeness:.1f}% ({files.get('present_count', 0)}/{files.get('total', 0)})")
        if files.get('missing'):
            print(f"  缺失文件: {', '.join(files['missing'][:3])}{'...' if len(files['missing']) > 3 else ''}")
        
        # 依赖状态
        print(f"\n📦 依赖状态")
        deps = results['dependencies']
        node_status = deps.get('node', {}).get('status', 'unknown')
        python_status = deps.get('python', {}).get('status', 'unknown')
        print(f"  Node.js: {'✅' if node_status == 'configured' else '❌'} {node_status}")
        print(f"  Python: {'✅' if python_status == 'configured' else '❌'} {python_status}")
        
        # AI协同状态
        print(f"\n🤖 AI协同状态")
        ai = results['ai_coordination']
        ai_overall = ai.get('overall', 'unknown')
        ai_icon = {'fully_functional': '✅', 'partially_functional': '⚠️', 'not_functional': '❌'}.get(ai_overall, '❓')
        print(f"  整体状态: {ai_icon} {ai_overall}")
        print(f"  活跃锁: {ai.get('locks', {}).get('active_locks', 0)}")
        print(f"  注册插件: {ai.get('plugins', {}).get('registered_plugins', 0)}")
        
        # 建议
        print(f"\n💡 建议操作")
        for rec in results['recommendations']:
            priority_icon = {'critical': '🚨', 'high': '⚠️', 'medium': '💡', 'low': 'ℹ️', 'info': '✅'}.get(rec['priority'], '•')
            print(f"  {priority_icon} {rec['text']}")
        
        # 快速启动命令
        print(f"\n🚀 快速操作")
        print("  npm run smart-start    # 智能启动所有服务")
        print("  npm run health         # 重新健康检查")
        print("  npm run compliance     # AI合规检查")
        print("  npm run scan           # 项目配置扫描")

def main():
    checker = ProjectHealthCheck()
    results = checker.run_full_check()
    checker.print_health_report()
    
    # 保存结果
    reports_dir = Path(__file__).parent.parent / 'logs' / 'health_reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = reports_dir / f'health_check_{timestamp}.json'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == '__main__':
    main()