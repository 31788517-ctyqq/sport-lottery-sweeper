#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由完整性检查脚本
用于检查API路由注册完整性、路径规范性以及文档一致性
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
import ast
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class APIRouteChecker:
    """API路由检查器"""
    
    def __init__(self):
        self.backend_path = project_root / "backend"
        self.api_routes = []
        self.route_patterns = []
        self.missing_routes = []
        
    def extract_routes_from_main(self) -> List[Dict]:
        """从main.py中提取已注册的路由"""
        routes = []
        main_file = self.backend_path / "main.py"
        
        if not main_file.exists():
            logger.error(f"主文件不存在: {main_file}")
            return routes
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有app.include_router调用
        pattern = r'app\.include_router\(\s*(\w+)\s*,\s*prefix="([^"]+)"[^)]*\)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            router_name, prefix = match
            routes.append({
                'router': router_name,
                'prefix': prefix,
                'file': 'main.py'
            })
        
        # 查找所有@app装饰器定义的路由
        route_decorators = re.findall(r'@(app\.(?:get|post|put|delete|patch)\("([^"]+)"|\w+\("([^"]+)"\))', content)
        for decorator in route_decorators:
            path = decorator[1] or decorator[2]  # 取第二个或第三个捕获组
            if path:
                routes.append({
                    'router': 'direct_route',
                    'prefix': path,
                    'file': 'main.py'
                })
        
        logger.info(f"从main.py中提取到 {len(routes)} 个路由")
        return routes
    
    def scan_api_directory(self) -> List[str]:
        """扫描API目录，找出所有可能的路由模块"""
        api_path = self.backend_path / "api"
        router_files = []
        
        for root, dirs, files in os.walk(api_path):
            for file in files:
                if file.endswith('.py') and ('router' in file or 'api' in file or 'endpoint' in file):
                    router_files.append(os.path.join(root, file))
        
        # 搜索所有包含router定义的Python文件
        for root, dirs, files in os.walk(api_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'router = APIRouter()' in content or 'router = Router()' in content:
                            if file_path not in router_files:
                                router_files.append(file_path)
        
        logger.info(f"扫描到 {len(router_files)} 个可能的路由文件")
        return router_files
    
    def check_route_consistency(self):
        """检查路由注册的一致性"""
        registered_routes = self.extract_routes_from_main()
        available_routes = self.scan_api_directory()
        
        logger.info("检查路由注册一致性...")
        
        # 分析每个API目录中的模块
        unregistered_modules = []
        for route_file in available_routes:
            # 提取文件名作为可能的模块名
            module_name = Path(route_file).stem
            file_rel_path = Path(route_file).relative_to(self.backend_path)
            
            # 检查这个模块是否在main.py中注册
            is_registered = False
            for route in registered_routes:
                if module_name in route['router'] or module_name.replace('_', '-') in route['prefix']:
                    is_registered = True
                    break
            
            if not is_registered:
                unregistered_modules.append({
                    'module': module_name,
                    'path': str(file_rel_path),
                    'full_path': route_file
                })
        
        self.missing_routes = unregistered_modules
        logger.info(f"发现 {len(unregistered_modules)} 个未注册的模块")
        
        for mod in unregistered_modules:
            logger.warning(f"未注册模块: {mod['module']} at {mod['path']}")
    
    def validate_api_paths(self):
        """验证API路径规范"""
        registered_routes = self.extract_routes_from_main()
        
        logger.info("验证API路径规范...")
        
        # 检查API路径是否符合规范
        for route in registered_routes:
            prefix = route['prefix']
            
            # 检查是否以/api/v1开头
            if not prefix.startswith('/api/v1'):
                logger.warning(f"API路径不符合规范: {prefix} (应该以/api/v1开头)")
            
            # 检查是否有适当的管理端前缀
            if '/admin' in prefix and not any(x in prefix for x in ['/api/v1/admin', '/admin']):
                logger.warning(f"管理端API路径可能不规范: {prefix}")
    
    def generate_fix_suggestions(self) -> List[str]:
        """生成修复建议"""
        suggestions = []
        
        for mod in self.missing_routes:
            # 生成注册代码建议
            module_path = mod['path'].replace('\\', '/').replace('/', '.')
            # 移除.py后缀
            module_path = '.'.join(module_path.split('.')[:-1])
            
            # 构造导入语句
            router_name = f"{mod['module']}_router"
            import_stmt = f"from backend.{module_path} import router as {router_name}"
            register_stmt = f"app.include_router({router_name}, prefix=\"/api/v1/admin\", tags=[\"{mod['module']}\""
            
            suggestions.append({
                'module': mod['module'],
                'import': import_stmt,
                'register': f"app.include_router({router_name}, prefix=\"/api/v1/admin\", tags=[\"{mod['module']}\"], ...)",
                'file_path': mod['full_path']
            })
        
        return suggestions
    
    def run_full_check(self):
        """运行完整的路由检查"""
        print("=" * 70)
        print("API路由完整性检查")
        print("=" * 70)
        
        # 检查路由一致性
        self.check_route_consistency()
        
        # 验证API路径规范
        self.validate_api_paths()
        
        # 生成修复建议
        suggestions = self.generate_fix_suggestions()
        
        print(f"\n📊 检查结果:")
        print(f"- 已注册路由数: {len(self.extract_routes_from_main())}")
        print(f"- 发现模块数: {len(self.scan_api_directory())}")
        print(f"- 未注册模块数: {len(self.missing_routes)}")
        
        if suggestions:
            print(f"\n💡 修复建议:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. 模块: {suggestion['module']}")
                print(f"     文件: {suggestion['file_path']}")
                print(f"     导入: {suggestion['import']}")
                print(f"     注册: {suggestion['register']}")
        
        if not self.missing_routes:
            print("\n✅ 所有API路由均已正确注册")
        
        print(f"\n📝 报告生成时间: {self.get_current_time()}")
        
        return len(self.missing_routes) == 0
    
    def get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def run_api_route_check():
    """运行API路由检查"""
    checker = APIRouteChecker()
    success = checker.run_full_check()
    return success


if __name__ == "__main__":
    success = run_api_route_check()
    sys.exit(0 if success else 1)