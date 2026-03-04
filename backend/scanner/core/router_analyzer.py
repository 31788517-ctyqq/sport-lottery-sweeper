"""
路由分析器
用于收集和分析FastAPI应用中的所有路由信息
"""
import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class RouterAnalyzer:
    """路由分析器类"""
    
    def __init__(self, backend_dir: str = "backend"):
        """
        初始化路由分析器
        
        Args:
            backend_dir: backend目录路径
        """
        self.backend_dir = Path(backend_dir).resolve()
        self.api_routes: List[Dict] = []
        self.route_patterns: Set[str] = set()
        
    def analyze_fastapi_app(self, app) -> List[Dict]:
        """
        分析FastAPI应用实例，提取所有路由信息
        
        Args:
            app: FastAPI应用实例
            
        Returns:
            List[Dict]: 路由信息列表
        """
        routes = []
        
        for route in app.routes:
            route_info = {
                "path": route.path,
                "methods": getattr(route, "methods", []),
                "name": getattr(route, "name", ""),
                "endpoint": str(getattr(route, "endpoint", "")),
            }
            
            # 提取认证依赖信息
            if hasattr(route, "dependencies"):
                deps = []
                for dep in getattr(route, "dependencies", []):
                    dep_info = str(dep)
                    if "get_current_user" in dep_info:
                        route_info["requires_auth"] = True
                    if "get_current_admin" in dep_info or "get_current_admin_user" in dep_info:
                        route_info["requires_admin"] = True
                    deps.append(dep_info)
                route_info["dependencies"] = deps
            
            routes.append(route_info)
            self.route_patterns.add(route.path)
        
        self.api_routes = routes
        return routes
    
    def analyze_directory(self, api_dir: str = "api") -> List[Dict]:
        """
        分析目录中的Python文件，提取路由定义
        
        Args:
            api_dir: API目录相对路径
            
        Returns:
            List[Dict]: 路由信息列表
        """
        api_path = self.backend_dir / api_dir
        routes = []
        
        if not api_path.exists():
            logger.warning(f"API目录不存在: {api_path}")
            return routes
        
        # 递归扫描Python文件
        for py_file in api_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            routes.extend(self._analyze_python_file(py_file))
        
        self.api_routes = routes
        return routes
    
    def _analyze_python_file(self, file_path: Path) -> List[Dict]:
        """
        分析单个Python文件，提取路由定义
        
        Args:
            file_path: Python文件路径
            
        Returns:
            List[Dict]: 路由信息列表
        """
        routes = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 查找APIRouter定义
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.endswith("router"):
                            # 找到router变量赋值
                            routes.extend(self._extract_routes_from_node(node, file_path))
                
                # 查找装饰器定义的路由
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            func_name = ""
                            if isinstance(decorator.func, ast.Attribute):
                                func_name = decorator.func.attr
                            elif isinstance(decorator.func, ast.Name):
                                func_name = decorator.func.id
                            
                            if func_name in ["get", "post", "put", "delete", "patch"]:
                                route_info = self._extract_route_from_decorator(
                                    decorator, node, file_path
                                )
                                if route_info:
                                    routes.append(route_info)
        
        except Exception as e:
            logger.error(f"分析Python文件失败 {file_path}: {e}")
        
        return routes
    
    def _extract_routes_from_node(self, node: ast.Assign, file_path: Path) -> List[Dict]:
        """从AST节点提取路由信息"""
        routes = []
        
        # 查找APIRouter实例化
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "APIRouter":
                # 这是一个APIRouter实例
                router_name = node.targets[0].id if node.targets else "router"
                
                # 查找这个router的路由定义
                tree = ast.parse(ast.unparse(node.value))
                routes.extend(self._find_router_routes(tree, router_name, file_path))
        
        return routes
    
    def _find_router_routes(self, tree: ast.AST, router_name: str, file_path: Path) -> List[Dict]:
        """查找router中的所有路由定义"""
        routes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数是否被装饰为路由
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        # 检查是否是@router.get("/path")格式
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.value.id == router_name:
                                route_info = self._extract_route_from_decorator(
                                    decorator, node, file_path
                                )
                                if route_info:
                                    routes.append(route_info)
        
        return routes
    
    def _extract_route_from_decorator(
        self, decorator: ast.Call, func_node: ast.FunctionDef, file_path: Path
    ) -> Optional[Dict]:
        """从装饰器提取路由信息"""
        try:
            # 提取HTTP方法
            method = ""
            if isinstance(decorator.func, ast.Attribute):
                method = decorator.func.attr.upper()
            elif isinstance(decorator.func, ast.Name):
                method = decorator.func.id.upper()
            
            # 提取路径参数
            path = ""
            if decorator.args:
                first_arg = decorator.args[0]
                if isinstance(first_arg, ast.Constant):
                    path = str(first_arg.value)
            
            if not path:
                return None
            
            # 分析函数参数中的认证依赖
            requires_auth = False
            requires_admin = False
            
            # 检查函数参数中的Depends
            for arg in func_node.args.args:
                if arg.annotation:
                    ann_str = ast.unparse(arg.annotation)
                    if "Depends" in ann_str:
                        if "get_current_user" in ann_str:
                            requires_auth = True
                        if "get_current_admin" in ann_str or "get_current_admin_user" in ann_str:
                            requires_admin = True
            
            route_info = {
                "path": path,
                "method": method,
                "function_name": func_node.name,
                "file_path": str(file_path.relative_to(self.backend_dir)),
                "requires_auth": requires_auth,
                "requires_admin": requires_admin,
                "parameters": self._extract_function_parameters(func_node),
            }
            
            return route_info
            
        except Exception as e:
            logger.error(f"提取路由信息失败: {e}")
            return None
    
    def _extract_function_parameters(self, func_node: ast.FunctionDef) -> List[Dict]:
        """提取函数参数信息"""
        parameters = []
        
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": ast.unparse(arg.annotation) if arg.annotation else "Any",
            }
            parameters.append(param_info)
        
        return parameters
    
    def get_route_patterns(self) -> Set[str]:
        """获取所有路由模式"""
        return self.route_patterns
    
    def find_missing_routes(self, expected_patterns: List[str]) -> List[str]:
        """
        查找缺失的路由
        
        Args:
            expected_patterns: 期望存在的路由模式列表
            
        Returns:
            List[str]: 缺失的路由模式列表
        """
        missing = []
        
        for pattern in expected_patterns:
            found = False
            for route in self.route_patterns:
                # 简单的模式匹配
                if self._match_route_pattern(pattern, route):
                    found = True
                    break
            
            if not found:
                missing.append(pattern)
        
        return missing
    
    def _match_route_pattern(self, pattern: str, route: str) -> bool:
        """匹配路由模式"""
        # 简单的匹配逻辑，可以后续改进
        if pattern == route:
            return True
        
        # 处理路径参数差异
        pattern_parts = pattern.strip("/").split("/")
        route_parts = route.strip("/").split("/")
        
        if len(pattern_parts) != len(route_parts):
            return False
        
        for p_part, r_part in zip(pattern_parts, route_parts):
            if p_part.startswith("{") and p_part.endswith("}"):
                # 路径参数位置
                continue
            if p_part != r_part:
                return False
        
        return True
    
    def generate_route_report(self) -> Dict:
        """生成路由分析报告"""
        report = {
            "total_routes": len(self.api_routes),
            "routes": self.api_routes,
            "route_patterns": list(self.route_patterns),
            "analysis_summary": {
                "requires_auth": sum(1 for r in self.api_routes if r.get("requires_auth")),
                "requires_admin": sum(1 for r in self.api_routes if r.get("requires_admin")),
                "methods_distribution": self._get_methods_distribution(),
            }
        }
        
        return report
    
    def _get_methods_distribution(self) -> Dict[str, int]:
        """获取HTTP方法分布"""
        distribution = {}
        
        for route in self.api_routes:
            method = route.get("method", "")
            if method:
                distribution[method] = distribution.get(method, 0) + 1
        
        return distribution