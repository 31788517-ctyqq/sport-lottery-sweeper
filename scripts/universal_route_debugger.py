#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用路由调试框架 - 可适配不同项目和框架
"""
import sys
import os
import argparse
from pathlib import Path

def detect_framework(project_path):
    """检测项目使用的Web框架"""
    indicators = {
        'fastapi': ['fastapi', 'APIRouter', 'FastAPI'],
        'django': ['django', 'urls.py', 'urlpatterns'],
        'flask': ['flask', 'Flask', 'Blueprint'],
        'express': ['express', 'app.get', 'app.post'],
    }
    
    framework_scores = {}
    
    # 搜索关键文件
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for framework, keywords in indicators.items():
                            score = sum(1 for kw in keywords if kw.lower() in content)
                            framework_scores[framework] = framework_scores.get(framework, 0) + score
                except:
                    pass
    
    detected = max(framework_scores.items(), key=lambda x: x[1]) if framework_scores else ('unknown', 0)
    return detected[0] if detected[1] > 0 else 'unknown'

def get_fastapi_routes(project_path):
    """FastAPI项目路由检查"""
    sys.path.insert(0, project_path)
    
    try:
        # 尝试不同的导入路径
        possible_imports = [
            'backend.api.v1',
            'app.api.v1', 
            'api.v1',
            'main'
        ]
        
        for import_path in possible_imports:
            try:
                module = __import__(import_path, fromlist=['router'])
                if hasattr(module, 'router'):
                    routes = []
                    for route in module.router.routes:
                        if hasattr(route, 'path'):
                            methods = getattr(route, 'methods', set())
                            path = getattr(route, 'path', '')
                            routes.append({'methods': methods, 'path': path})
                    return routes, import_path
            except:
                continue
                
        return [], None
    except Exception as e:
        print(f"FastAPI路由检查失败: {e}")
        return [], None

def analyze_project_structure(project_path):
    """分析项目结构并提供针对性建议"""
    print(f"🔍 分析项目: {project_path}\n")
    
    # 检测框架
    framework = detect_framework(project_path)
    print(f"📋 检测到框架: {framework.upper()}")
    
    # 分析项目结构
    structure_indicators = {
        'modular_api': 'api' in str(project_path),
        'has_backend': 'backend' in str(project_path),
        'has_src': 'src' in str(project_path),
        'has_app': 'app' in str(project_path),
    }
    
    print("\n🏗️ 项目结构特征:")
    for feature, present in structure_indicators.items():
        status = "✅" if present else "❌"
        print(f"  {status} {feature}")
    
    # 框架特定建议
    recommendations = {
        'fastapi': {
            'debug_commands': [
                "python -c 'from backend.api.v1 import router; print([r.path for r in router.routes])'",
                "netstat -ano | findstr :8000",
                "taskkill /f /im python.exe && python backend/main.py"
            ],
            'common_issues': [
                "路由前缀重复定义",
                "导入路径错误", 
                "服务未重启"
            ],
            'best_practices': [
                "在__init__.py中统一定义前缀",
                "路由文件使用prefix=''",
                "修改后必须重启服务"
            ]
        },
        'django': {
            'debug_commands': [
                "python manage.py show_urls",
                "python manage.py check",
                "systemctl status gunicorn"
            ],
            'common_issues': [
                "urls.py配置错误",
                "应用未注册",
                "静态文件配置"
            ]
        },
        'flask': {
            'debug_commands': [
                "flask routes",
                "python app.py",
                "netstat -tulpn | grep :5000"
            ]
        },
        'unknown': {
            'debug_commands': [
                "find . -name '*.py' -exec grep -l 'route\|path\|url' {} \;",
                "ls -la",
                "tree ."
            ],
            'suggestion': "无法确定框架，请手动检查项目结构"
        }
    }
    
    rec = recommendations.get(framework, recommendations['unknown'])
    
    print(f"\n💡 {framework.upper()} 专用建议:")
    if 'debug_commands' in rec:
        print("  调试命令:")
        for cmd in rec['debug_commands']:
            print(f"    • {cmd}")
    
    if 'common_issues' in rec:
        print("  常见问题:")
        for issue in rec['common_issues']:
            print(f"    • {issue}")
    
    if 'best_practices' in rec:
        print("  最佳实践:")
        for practice in rec['best_practices']:
            print(f"    • {practice}")
    
    # 如果是FastAPI，进一步检查路由
    if framework == 'fastapi':
        print("\n🔧 详细路由检查:")
        routes, import_path = get_fastapi_routes(project_path)
        if routes:
            print(f"  成功导入: {import_path}")
            print(f"  找到 {len(routes)} 个路由:")
            for route in routes[:10]:  # 只显示前10个
                print(f"    {route['methods']} {route['path']}")
            if len(routes) > 10:
                print(f"    ... 还有 {len(routes)-10} 个路由")
        else:
            print("  ❌ 无法找到路由定义")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='通用路由调试工具')
    parser.add_argument('--path', default='.', help='项目路径')
    args = parser.parse_args()
    
    project_path = Path(args.path).absolute()
    analyze_project_structure(str(project_path))