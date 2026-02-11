#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端路由规范检查脚本
用于检查前端路由配置是否符合项目规范
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class FrontendRouteChecker:
    """前端路由检查器"""
    
    def __init__(self):
        self.frontend_path = project_root / "frontend"
        self.routes = []
        self.route_issues = []
        self.specifications = {
            "allowed_prefixes": ["/admin", "/login", "/dashboard", "/api"],
            "disallowed_patterns": [r"\.\./", r"\.\.\\", r"__pycache__"],
            "required_components": ["Login", "Dashboard", "Layout"],
            "path_alias_usage": ["@", "@/components", "@/views", "@/api", "@/utils"]
        }
    
    def extract_vue_routes(self) -> List[Dict]:
        """从Vue路由配置中提取路由"""
        routes = []
        router_path = self.frontend_path / "src" / "router" / "index.js"
        
        if not router_path.exists():
            logger.error(f"路由配置文件不存在: {router_path}")
            return routes
        
        with open(router_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找Vue路由定义
        # 匹配 { path: '...', component: ..., meta: {...} } 格式的路由
        route_pattern = r"path:\s*'([^']+)'.*?,\s*name:\s*'([^']+)'"
        matches = re.findall(route_pattern, content, re.DOTALL)
        
        for path, name in matches:
            routes.append({
                'path': path,
                'name': name,
                'file': 'router/index.js'
            })
        
        # 查找import语句，确认组件导入是否正确
        import_pattern = r"import\s+.*\s+from\s+['\"](@/.*|\.\/.*|\.\.\/.*)['\"]"
        imports = re.findall(import_pattern, content)
        
        logger.info(f"从{router_path}中提取到 {len(routes)} 个路由定义")
        logger.info(f"发现 {len(imports)} 个导入语句")
        
        return routes
    
    def scan_vue_views(self) -> List[str]:
        """扫描Vue视图组件"""
        views_path = self.frontend_path / "src" / "views"
        vue_files = []
        
        for root, dirs, files in os.walk(views_path):
            for file in files:
                if file.endswith('.vue'):
                    vue_files.append(os.path.join(root, file))
        
        logger.info(f"扫描到 {len(vue_files)} 个Vue视图文件")
        return vue_files
    
    def check_path_alias_usage(self):
        """检查路径别名使用情况"""
        issues = []
        
        # 检查router/index.js
        router_path = self.frontend_path / "src" / "router" / "index.js"
        if router_path.exists():
            with open(router_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查是否使用了相对路径而不是路径别名
            relative_path_pattern = r"from\s+['\"].*(\.\.\/|\.\.\\\\).*['\"]"
            relative_matches = re.findall(relative_path_pattern, content)
            
            if relative_matches:
                issues.append({
                    'file': 'router/index.js',
                    'issue': '发现使用相对路径而非路径别名',
                    'details': relative_matches
                })
        
        # 检查views目录下的.vue文件
        for root, dirs, files in os.walk(self.frontend_path / "src" / "views"):
            for file in files:
                if file.endswith('.vue'):
                    file_path = Path(root) / file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 检查是否使用了相对路径
                    relative_matches = re.findall(relative_path_pattern, content)
                    if relative_matches:
                        issues.append({
                            'file': str(file_path.relative_to(self.frontend_path)),
                            'issue': '发现使用相对路径而非路径别名',
                            'details': relative_matches
                        })
        
        self.route_issues.extend(issues)
        logger.info(f"发现 {len(issues)} 个路径别名使用问题")
    
    def validate_route_paths(self):
        """验证路由路径是否符合规范"""
        routes = self.extract_vue_routes()
        issues = []
        
        for route in routes:
            path = route['path']
            
            # 检查路径是否以斜杠开头
            if not path.startswith('/'):
                issues.append({
                    'route': path,
                    'issue': '路径应以斜杠(/)开头',
                    'file': route['file']
                })
            
            # 检查路径是否包含不允许的模式
            for pattern in self.specifications['disallowed_patterns']:
                if re.search(pattern, path):
                    issues.append({
                        'route': path,
                        'issue': f'路径包含不允许的模式: {pattern}',
                        'file': route['file']
                    })
        
        self.route_issues.extend(issues)
        logger.info(f"发现 {len(issues)} 个路径规范问题")
    
    def check_component_imports(self):
        """检查组件导入是否正确"""
        issues = []
        
        # 检查router/index.js中的组件导入
        router_path = self.frontend_path / "src" / "router" / "index.js"
        if router_path.exists():
            with open(router_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否使用了正确的路径别名
            for alias in self.specifications['path_alias_usage']:
                if f"from '{alias}" in content or f'from "{alias}' in content:
                    continue  # 使用了正确的路径别名
                    
            # 检查是否有未使用的必需组件
            for comp in self.specifications['required_components']:
                if f"{comp}.vue" not in content and f"{comp} from" not in content:
                    issues.append({
                        'file': 'router/index.js',
                        'issue': f'可能缺少必需组件: {comp}',
                        'details': '检查是否正确导入了必需的组件'
                    })
        
        self.route_issues.extend(issues)
        logger.info(f"发现 {len(issues)} 个组件导入问题")
    
    def generate_report(self) -> str:
        """生成检查报告"""
        report_lines = [
            "=" * 70,
            "前端路由规范检查报告",
            "=" * 70,
            "",
            f"检查时间: {self.get_current_time()}",
            f"项目路径: {self.frontend_path}",
            ""
        ]
        
        # 路由统计
        routes = self.extract_vue_routes()
        vue_files = self.scan_vue_views()
        
        report_lines.extend([
            "📊 路由统计:",
            f"- 定义的路由数量: {len(routes)}",
            f"- 发现的Vue文件数量: {len(vue_files)}",
            ""
        ])
        
        # 显示路由信息
        if routes:
            report_lines.append("📋 已定义路由:")
            for i, route in enumerate(routes, 1):
                report_lines.append(f"  {i}. 路径: {route['path']}, 名称: {route['name']}")
            report_lines.append("")
        
        # 显示问题
        if self.route_issues:
            report_lines.extend([
                "⚠️  发现的问题:",
            ])
            for i, issue in enumerate(self.route_issues, 1):
                report_lines.append(f"  {i}. 文件: {issue['file']}")
                report_lines.append(f"     问题: {issue['issue']}")
                if 'details' in issue:
                    report_lines.append(f"     详情: {issue['details']}")
                report_lines.append("")
        else:
            report_lines.extend([
                "✅ 未发现路由规范问题",
                ""
            ])
        
        # 修复建议
        report_lines.extend([
            "💡 修复建议:",
            "- 确保所有导入使用路径别名 (@/components, @/views, 等)",
            "- 路由路径应以斜杠(/)开头",
            "- 避免使用相对路径 (../ 或 ./)",
            "- 确保必需的组件已正确导入",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def run_full_check(self):
        """运行完整的路由检查"""
        # 执行各项检查
        self.check_path_alias_usage()
        self.validate_route_paths()
        self.check_component_imports()
        
        # 生成并打印报告
        report = self.generate_report()
        print(report)
        
        return len(self.route_issues) == 0


def run_frontend_route_check():
    """运行前端路由检查"""
    checker = FrontendRouteChecker()
    success = checker.run_full_check()
    return success


if __name__ == "__main__":
    success = run_frontend_route_check()
    sys.exit(0 if success else 1)