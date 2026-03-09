"""
认证分析器
用于检测API中的401（未认证）和403（权限不足）问题
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class AuthAnalyzer:
    """认证分析器类"""
    
    def __init__(self, backend_dir: str = "backend"):
        """
        初始化认证分析器
        
        Args:
            backend_dir: backend目录路径
        """
        self.backend_dir = Path(backend_dir).resolve()
        self.auth_issues: List[Dict] = []
        
    def analyze_routes(self, routes: List[Dict]) -> List[Dict]:
        """
        分析路由列表，检测认证问题
        
        Args:
            routes: 路由信息列表
            
        Returns:
            List[Dict]: 认证问题列表
        """
        issues = []
        
        for route in routes:
            # 检测敏感接口是否缺少认证
            if self._is_sensitive_route(route):
                if not route.get("requires_auth") and not route.get("requires_admin"):
                    issues.append({
                        "type": "missing_auth",
                        "severity": "high",
                        "route": route["path"],
                        "method": route["method"],
                        "file": route["file_path"],
                        "description": "敏感接口缺少认证保护",
                        "recommendation": "添加Depends(get_current_user)或Depends(get_current_admin_user)",
                    })
            
            # 检测需要管理员权限的接口是否缺少管理员检查
            if self._is_admin_route(route):
                if not route.get("requires_admin"):
                    issues.append({
                        "type": "missing_admin_check",
                        "severity": "high",
                        "route": route["path"],
                        "method": route["method"],
                        "file": route["file_path"],
                        "description": "管理员接口缺少管理员权限检查",
                        "recommendation": "添加Depends(get_current_admin)或检查用户角色",
                    })
            
            # 检测公共接口是否错误地添加了认证
            if self._is_public_route(route):
                if route.get("requires_auth") or route.get("requires_admin"):
                    issues.append({
                        "type": "unnecessary_auth",
                        "severity": "low",
                        "route": route["path"],
                        "method": route["method"],
                        "file": route["file_path"],
                        "description": "公共接口添加了不必要的认证",
                        "recommendation": "移除Depends依赖，或确认是否需要认证",
                    })
        
        self.auth_issues = issues
        return issues
    
    def analyze_directory(self, api_dir: str = "api/v1") -> List[Dict]:
        """
        分析目录中的API文件，检测认证问题
        
        Args:
            api_dir: API目录相对路径
            
        Returns:
            List[Dict]: 认证问题列表
        """
        api_path = self.backend_dir / api_dir
        issues = []
        
        if not api_path.exists():
            logger.warning(f"API目录不存在: {api_path}")
            return issues
        
        # 递归扫描Python文件
        for py_file in api_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            file_issues = self._analyze_auth_in_file(py_file)
            issues.extend(file_issues)
        
        self.auth_issues = issues
        return issues
    
    def _analyze_auth_in_file(self, file_path: Path) -> List[Dict]:
        """
        分析单个Python文件中的认证问题
        
        Args:
            file_path: Python文件路径
            
        Returns:
            List[Dict]: 认证问题列表
        """
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 查找所有函数定义
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否是路由函数（有路由装饰器）
                    is_route = False
                    route_path = ""
                    route_method = ""
                    
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            func_name = ""
                            if isinstance(decorator.func, ast.Attribute):
                                func_name = decorator.func.attr
                            elif isinstance(decorator.func, ast.Name):
                                func_name = decorator.func.id
                            
                            if func_name in ["get", "post", "put", "delete", "patch"]:
                                is_route = True
                                route_method = func_name.upper()
                                
                                # 提取路径
                                if decorator.args:
                                    first_arg = decorator.args[0]
                                    if isinstance(first_arg, ast.Constant):
                                        route_path = str(first_arg.value)
                    
                    if is_route and route_path:
                        # 分析函数的认证依赖
                        auth_issues = self._analyze_function_auth(node, route_path, route_method, file_path)
                        issues.extend(auth_issues)
        
        except Exception as e:
            logger.error(f"分析认证问题失败 {file_path}: {e}")
        
        return issues
    
    def _analyze_function_auth(
        self, func_node: ast.FunctionDef, route_path: str, route_method: str, file_path: Path
    ) -> List[Dict]:
        """
        分析单个路由函数的认证问题
        
        Args:
            func_node: 函数AST节点
            route_path: 路由路径
            route_method: HTTP方法
            file_path: 文件路径
            
        Returns:
            List[Dict]: 认证问题列表
        """
        issues = []
        
        # 检查函数参数中的Depends
        requires_auth = False
        requires_admin = False
        
        for arg in func_node.args.args:
            if arg.annotation:
                ann_str = ast.unparse(arg.annotation)
                if "Depends" in ann_str:
                    if "get_current_user" in ann_str:
                        requires_auth = True
                    if "get_current_admin" in ann_str or "get_current_admin_user" in ann_str:
                        requires_admin = True
        
        # 检查是否是敏感接口
        if self._is_sensitive_route_by_path(route_path):
            if not requires_auth and not requires_admin:
                issues.append({
                    "type": "missing_auth",
                    "severity": "high",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "description": "敏感接口缺少认证保护",
                    "recommendation": "添加Depends(get_current_user)或Depends(get_current_admin_user)",
                })
        
        # 检查是否是管理员接口
        if self._is_admin_route_by_path(route_path):
            if not requires_admin:
                issues.append({
                    "type": "missing_admin_check",
                    "severity": "high",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "description": "管理员接口缺少管理员权限检查",
                    "recommendation": "添加Depends(get_current_admin)或检查用户角色",
                })
        
        # 检查是否是公共接口
        if self._is_public_route_by_path(route_path):
            if requires_auth or requires_admin:
                issues.append({
                    "type": "unnecessary_auth",
                    "severity": "low",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "description": "公共接口添加了不必要的认证",
                    "recommendation": "移除Depends依赖，或确认是否需要认证",
                })
        
        return issues
    
    def _is_sensitive_route(self, route: Dict) -> bool:
        """判断是否是敏感接口"""
        path = route.get("path", "").lower()
        
        # 敏感接口模式
        sensitive_patterns = [
            r"/users?/.*",
            r"/profile.*",
            r"/admin.*",
            r"/data.*",
            r"/config.*",
            r"/settings.*",
            r"/payment.*",
            r"/wallet.*",
            r"/balance.*",
            r"/transaction.*",
            r"/api/.*",  # 除公共接口外的API
        ]
        
        # 排除公共接口
        public_patterns = [
            r"/auth/login.*",
            r"/auth/register.*",
            r"/public/.*",
            r"/health.*",
            r"/docs.*",
            r"/openapi\.json",
        ]
        
        # 检查是否是公共接口
        for pattern in public_patterns:
            if re.match(pattern, path):
                return False
        
        # 检查是否是敏感接口
        for pattern in sensitive_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def _is_sensitive_route_by_path(self, path: str) -> bool:
        """根据路径判断是否是敏感接口"""
        path_lower = path.lower()
        
        sensitive_patterns = [
            r"/users?/.*",
            r"/profile.*", 
            r"/admin.*",
            r"/data.*",
            r"/config.*",
            r"/settings.*",
            r"/payment.*",
            r"/wallet.*",
            r"/balance.*",
            r"/transaction.*",
            r"/api/.*",
        ]
        
        public_patterns = [
            r"/auth/login.*",
            r"/auth/register.*",
            r"/public/.*",
            r"/health.*",
            r"/docs.*",
            r"/openapi\.json",
        ]
        
        for pattern in public_patterns:
            if re.match(pattern, path_lower):
                return False
        
        for pattern in sensitive_patterns:
            if re.match(pattern, path_lower):
                return True
        
        return False
    
    def _is_admin_route(self, route: Dict) -> bool:
        """判断是否是管理员接口"""
        path = route.get("path", "").lower()
        
        admin_patterns = [
            r"/admin/.*",
            r"/users/admin.*",
            r"/system/.*",
            r"/config/.*",
            r"/settings/.*",
        ]
        
        for pattern in admin_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def _is_admin_route_by_path(self, path: str) -> bool:
        """根据路径判断是否是管理员接口"""
        path_lower = path.lower()
        
        admin_patterns = [
            r"/admin/.*",
            r"/users/admin.*",
            r"/system/.*",
            r"/config/.*",
            r"/settings/.*",
        ]
        
        for pattern in admin_patterns:
            if re.match(pattern, path_lower):
                return True
        
        return False
    
    def _is_public_route(self, route: Dict) -> bool:
        """判断是否是公共接口"""
        path = route.get("path", "").lower()
        
        public_patterns = [
            r"/auth/login.*",
            r"/auth/register.*",
            r"/public/.*",
            r"/health.*",
            r"/docs.*",
            r"/openapi\.json",
        ]
        
        for pattern in public_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def _is_public_route_by_path(self, path: str) -> bool:
        """根据路径判断是否是公共接口"""
        path_lower = path.lower()
        
        public_patterns = [
            r"/auth/login.*",
            r"/auth/register.*",
            r"/public/.*",
            r"/health.*",
            r"/docs.*",
            r"/openapi\.json",
        ]
        
        for pattern in public_patterns:
            if re.match(pattern, path_lower):
                return True
        
        return False
    
    def generate_auth_report(self) -> Dict:
        """生成认证分析报告"""
        if not self.auth_issues:
            return {
                "summary": {
                    "total_issues": 0,
                    "by_type": {},
                    "by_severity": {},
                },
                "issues": []
            }
        
        # 按类型统计
        by_type = {}
        by_severity = {}
        
        for issue in self.auth_issues:
            issue_type = issue["type"]
            severity = issue["severity"]
            
            by_type[issue_type] = by_type.get(issue_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        report = {
            "summary": {
                "total_issues": len(self.auth_issues),
                "by_type": by_type,
                "by_severity": by_severity,
            },
            "issues": self.auth_issues
        }
        
        return report
    
    def get_high_priority_issues(self) -> List[Dict]:
        """获取高优先级问题"""
        return [issue for issue in self.auth_issues if issue["severity"] == "high"]
    
    def get_missing_auth_issues(self) -> List[Dict]:
        """获取缺少认证的问题"""
        return [issue for issue in self.auth_issues if issue["type"] == "missing_auth"]
    
    def get_missing_admin_issues(self) -> List[Dict]:
        """获取缺少管理员权限检查的问题"""
        return [issue for issue in self.auth_issues if issue["type"] == "missing_admin_check"]