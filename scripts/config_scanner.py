#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置扫描器 - AI可读的项目结构分析
AI_WORKING: analyzer1 @2026-01-25T00:00:00 - 创建配置扫描器，生成AI可读的项目配置信息
"""

import os
import ast
import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

class ConfigScanner:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.scan_results = {
            'timestamp': datetime.now().isoformat(),
            'project_structure': {},
            'entry_points': {},
            'dependencies': {},
            'api_routes': [],
            'path_aliases': {},
            'ai_coordination': {}
        }
    
    def scan_project_structure(self) -> Dict[str, Any]:
        """扫描项目目录结构"""
        structure = {
            'directories': [],
            'key_files': [],
            'file_counts': {}
        }
        
        # 扫描主要目录
        key_dirs = ['backend', 'frontend', 'scripts', '.codebuddy', 'docs']
        for dir_name in key_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob('*')))
                structure['directories'].append({
                    'name': dir_name,
                    'path': str(dir_path),
                    'file_count': file_count
                })
        
        # 查找关键文件
        key_files = [
            'package.json', 'pyproject.toml', 'requirements.txt',
            'frontend/vite.config.js', 'backend/main.py',
            'frontend/src/router/index.js', '.env.example'
        ]
        
        for file_pattern in key_files:
            file_path = self.project_root / file_pattern
            if file_path.exists():
                structure['key_files'].append(str(file_path))
        
        self.scan_results['project_structure'] = structure
        return structure
    
    def scan_entry_points(self) -> Dict[str, Any]:
        """识别项目入口文件"""
        entry_points = {
            'backend': {},
            'frontend': {},
            'scripts': {}
        }
        
        # 后端入口
        backend_main = self.project_root / 'backend' / 'main.py'
        if backend_main.exists():
            entry_points['backend'] = {
                'main_file': str(backend_main),
                'port': 8000,
                'framework': 'FastAPI',
                'docs_url': 'http://localhost:8000/docs'
            }
        
        # 前端入口
        frontend_package = self.project_root / 'frontend' / 'package.json'
        if frontend_package.exists():
            try:
                with open(frontend_package, 'r', encoding='utf-8') as f:
                    pkg_data = json.load(f)
                    entry_points['frontend'] = {
                        'main_file': 'frontend/src/main.js',
                        'dev_script': pkg_data.get('scripts', {}).get('dev'),
                        'port': 3000,
                        'framework': 'Vue 3 + Vite',
                        'homepage': pkg_data.get('homepage', 'http://localhost:3000')
                    }
            except Exception as e:
                entry_points['frontend']['error'] = str(e)
        
        # 脚本入口
        scripts_dir = self.project_root / 'scripts'
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob('*.py'))
            entry_points['scripts'] = {
                'directory': str(scripts_dir),
                'scripts': [f.name for f in script_files[:10]]  # 限制显示数量
            }
        
        self.scan_results['entry_points'] = entry_points
        return entry_points
    
    def scan_dependencies(self) -> Dict[str, Any]:
        """扫描项目依赖"""
        dependencies = {
            'node': {},
            'python': {}
        }
        
        # Node.js依赖
        frontend_package = self.project_root / 'frontend' / 'package.json'
        if frontend_package.exists():
            try:
                with open(frontend_package, 'r', encoding='utf-8') as f:
                    pkg_data = json.load(f)
                    dependencies['node'] = {
                        'dependencies': pkg_data.get('dependencies', {}),
                        'devDependencies': pkg_data.get('devDependencies', {}),
                        'engines': pkg_data.get('engines', {})
                    }
            except Exception as e:
                dependencies['node']['error'] = str(e)
        
        # Python依赖
        requirements = self.project_root / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements, 'r', encoding='utf-8') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    dependencies['python']['requirements'] = deps
            except Exception as e:
                dependencies['python']['error'] = str(e)
        
        pyproject = self.project_root / 'pyproject.toml'
        if pyproject.exists():
            try:
                # 简单的TOML解析（实际项目中应使用toml库）
                with open(pyproject, 'r', encoding='utf-8') as f:
                    content = f.read()
                    dependencies['python']['pyproject'] = 'present'
            except Exception as e:
                dependencies['python']['pyproject_error'] = str(e)
        
        self.scan_results['dependencies'] = dependencies
        return dependencies
    
    def scan_api_routes(self) -> List[Dict[str, str]]:
        """扫描API路由配置"""
        routes = []
        
        # 扫描前端路由
        frontend_router = self.project_root / 'frontend' / 'src' / 'router' / 'index.js'
        if frontend_router.exists():
            try:
                with open(frontend_router, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单的路由提取（实际应使用AST解析）
                    if 'path:' in content:
                        routes.append({
                            'type': 'frontend',
                            'file': str(frontend_router),
                            'note': '包含路由配置'
                        })
            except Exception as e:
                routes.append({'type': 'error', 'file': str(frontend_router), 'error': str(e)})
        
        # 扫描后端API路由
        backend_api = self.project_root / 'backend' / 'api'
        if backend_api.exists():
            api_files = list(backend_api.rglob('*.py'))
            routes.extend([
                {
                    'type': 'backend_api',
                    'file': str(f),
                    'module': str(f.relative_to(self.project_root))
                }
                for f in api_files
            ])
        
        self.scan_results['api_routes'] = routes
        return routes
    
    def scan_path_aliases(self) -> Dict[str, Any]:
        """扫描路径别名配置"""
        aliases = {
            'frontend': {},
            'backend': {}
        }
        
        # 前端Vite别名
        vite_config = self.project_root / 'frontend' / 'vite.config.js'
        if vite_config.exists():
            try:
                with open(vite_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'alias' in content:
                        aliases['frontend'] = {
                            'config_file': str(vite_config),
                            'has_aliases': True,
                            'note': '使用@别名系统'
                        }
            except Exception as e:
                aliases['frontend']['error'] = str(e)
        
        # 检查PATH_ALIASES.md文档
        path_doc = self.project_root / 'PATH_ALIASES.md'
        if path_doc.exists():
            aliases['documentation'] = str(path_doc)
        
        self.scan_results['path_aliases'] = aliases
        return aliases
    
    def scan_ai_coordination(self) -> Dict[str, Any]:
        """扫描AI协同配置"""
        coordination = {}
        
        # 检查锁系统
        locks_dir = self.project_root / '.codebuddy' / 'locks'
        if locks_dir.exists():
            lock_files = list(locks_dir.glob('*.lock'))
            coordination['lock_system'] = {
                'directory': str(locks_dir),
                'active_locks': len(lock_files),
                'lock_files': [f.name for f in lock_files]
            }
        
        # 检查插件配置
        plugin_config = self.project_root / '.codebuddy' / 'plugin_identities.json'
        if plugin_config.exists():
            try:
                with open(plugin_config, 'r', encoding='utf-8') as f:
                    coordination['plugin_config'] = json.load(f)
            except Exception as e:
                coordination['plugin_config_error'] = str(e)
        
        # 检查状态文件
        status_file = self.project_root / '.codebuddy' / 'status' / 'active_plugins.json'
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    coordination['active_plugins'] = json.load(f)
            except Exception as e:
                coordination['active_plugins_error'] = str(e)
        
        self.scan_results['ai_coordination'] = coordination
        return coordination
    
    def generate_ai_readable_config(self) -> str:
        """生成AI可读的配置信息"""
        self.scan_project_structure()
        self.scan_entry_points()
        self.scan_dependencies()
        self.scan_api_routes()
        self.scan_path_aliases()
        self.scan_ai_coordination()
        
        config_text = f"""
# 体育彩票扫盘系统 - AI配置信息
# 生成时间: {self.scan_results['timestamp']}

## 🎯 项目概览
- 项目名称: sport-lottery-sweeper
- 技术栈: Vue 3 + FastAPI + TypeScript
- 项目根目录: {self.project_root}

## 🚀 入口文件
"""
        
        # 添加入口信息
        entry_points = self.scan_results['entry_points']
        if entry_points.get('backend'):
            backend = entry_points['backend']
            config_text += f"""- 后端入口: {backend['main_file']}
  - 端口: {backend['port']}
  - 框架: {backend['framework']}
  - API文档: {backend['docs_url']}\n"""
        
        if entry_points.get('frontend'):
            frontend = entry_points['frontend']
            config_text += f"""- 前端入口: {frontend.get('main_file', 'N/A')}
  - 端口: {frontend['port']}
  - 框架: {frontend['framework']}
  - 启动命令: {frontend.get('dev_script', 'N/A')}\n"""
        
        # 添加依赖信息
        config_text += "\n## 📦 核心依赖\n"
        deps = self.scan_results['dependencies']
        
        if deps.get('node', {}).get('dependencies'):
            config_text += "### 前端依赖 (关键)\n"
            for dep, version in list(deps['node']['dependencies'].items())[:10]:
                config_text += f"- {dep}: {version}\n"
        
        if deps.get('python', {}).get('requirements'):
            config_text += "\n### 后端依赖 (部分)\n"
            for req in deps['python']['requirements'][:10]:
                config_text += f"- {req}\n"
        
        # 添加AI协同信息
        config_text += "\n## 🤖 AI协同配置\n"
        ai_coord = self.scan_results['ai_coordination']
        
        if ai_coord.get('lock_system'):
            locks = ai_coord['lock_system']
            config_text += f"- 锁系统: 活跃锁数量 {locks['active_locks']}\n"
        
        if ai_coord.get('plugin_config'):
            plugins = ai_coord['plugin_config']
            config_text += f"- 注册插件: {len(plugins.get('plugins', {}))} 个\n"
            for plugin_id, plugin_info in plugins.get('plugins', {}).items():
                config_text += f"  - {plugin_info['name']} ({plugin_id}): 优先级 {plugin_info['priority']}\n"
        
        config_text += "\n## 📋 快速启动命令\n"
        config_text += "```bash\n"
        config_text += "# 一键启动\nnpm run smart-start\n\n"
        config_text += "# 分别启动\nnpm run backend:dev\nnpm run frontend:dev\n\n"
        config_text += "# 健康检查\nnpm run health\n\n"
        config_text += "# AI合规检查\nnpm run compliance\n"
        config_text += "```\n"
        
        return config_text
    
    def save_scan_results(self, output_file: str = None):
        """保存扫描结果"""
        if not output_file:
            output_file = self.project_root / '.codebuddy' / 'status' / 'scan_results.json'
        
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
        
        return str(output_file)

def main():
    scanner = ConfigScanner()
    
    print("[SCAN] 开始扫描项目配置...")
    
    # 生成AI可读配置
    config_text = scanner.generate_ai_readable_config()
    print(config_text)
    
    # 保存详细结果
    results_file = scanner.save_scan_results()
    print(f"\n[SCAN] 详细结果已保存到: {results_file}")
    
    # 输出快速摘要
    print("\n[SCAN] 扫描摘要:")
    print(f"- 项目结构: {len(scanner.scan_results['project_structure']['directories'])} 个主要目录")
    print(f"- 入口文件: {'✓' if scanner.scan_results['entry_points'] else '✗'}")
    print(f"- API路由: {len(scanner.scan_results['api_routes'])} 个文件")
    print(f"- AI协同: {'✓' if scanner.scan_results['ai_coordination'] else '✗'}")

if __name__ == '__main__':
    main()