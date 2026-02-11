"""
验证分析器
用于检测API中的422（参数验证）问题
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class ValidationAnalyzer:
    """验证分析器类"""
    
    def __init__(self, backend_dir: str = "backend"):
        """
        初始化验证分析器
        
        Args:
            backend_dir: backend目录路径
        """
        self.backend_dir = Path(backend_dir).resolve()
        self.validation_issues: List[Dict] = []
        
    def analyze_routes(self, routes: List[Dict]) -> List[Dict]:
        """
        分析路由列表，检测参数验证问题
        
        Args:
            routes: 路由信息列表
            
        Returns:
            List[Dict]: 验证问题列表
        """
        issues = []
        
        for route in routes:
            route_issues = self._analyze_route_validation(route)
            issues.extend(route_issues)
        
        self.validation_issues = issues
        return issues
    
    def analyze_directory(self, api_dir: str = "api/v1") -> List[Dict]:
        """
        分析目录中的API文件，检测参数验证问题
        
        Args:
            api_dir: API目录相对路径
            
        Returns:
            List[Dict]: 验证问题列表
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
                
            file_issues = self._analyze_validation_in_file(py_file)
            issues.extend(file_issues)
        
        self.validation_issues = issues
        return issues
    
    def _analyze_validation_in_file(self, file_path: Path) -> List[Dict]:
        """
        分析单个Python文件中的参数验证问题
        
        Args:
            file_path: Python文件路径
            
        Returns:
            List[Dict]: 验证问题列表
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
                        # 分析函数的参数验证
                        validation_issues = self._analyze_function_validation(
                            node, route_path, route_method, file_path
                        )
                        issues.extend(validation_issues)
        
        except Exception as e:
            logger.error(f"分析验证问题失败 {file_path}: {e}")
        
        return issues
    
    def _analyze_function_validation(
        self, func_node: ast.FunctionDef, route_path: str, route_method: str, file_path: Path
    ) -> List[Dict]:
        """
        分析单个路由函数的参数验证问题
        
        Args:
            func_node: 函数AST节点
            route_path: 路由路径
            route_method: HTTP方法
            file_path: 文件路径
            
        Returns:
            List[Dict]: 验证问题列表
        """
        issues = []
        
        # 提取函数参数信息
        parameters = self._extract_function_parameters(func_node)
        
        # 检查每个参数的验证
        for param in parameters:
            param_issues = self._analyze_parameter_validation(param, route_path, route_method, file_path)
            issues.extend(param_issues)
        
        # 检查请求体验证
        if route_method in ["POST", "PUT", "PATCH"]:
            body_issues = self._analyze_request_body_validation(func_node, route_path, route_method, file_path)
            issues.extend(body_issues)
        
        # 检查路径参数验证
        path_param_issues = self._analyze_path_parameter_validation(route_path, route_method, file_path)
        issues.extend(path_param_issues)
        
        return issues
    
    def _extract_function_parameters(self, func_node: ast.FunctionDef) -> List[Dict]:
        """提取函数参数信息"""
        parameters = []
        
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
                "type": self._extract_parameter_type(arg.annotation),
                "has_validation": False,
                "validation_rules": [],
            }
            
            # 检查是否有验证规则
            if arg.annotation:
                ann_str = ast.unparse(arg.annotation)
                param_info["has_validation"] = self._has_validation_rules(ann_str)
                param_info["validation_rules"] = self._extract_validation_rules(ann_str)
            
            parameters.append(param_info)
        
        return parameters
    
    def _extract_parameter_type(self, annotation: Optional[ast.AST]) -> str:
        """提取参数类型"""
        if not annotation:
            return "Any"
        
        ann_str = ast.unparse(annotation)
        
        # 解析Pydantic模型
        if "schemas." in ann_str:
            # 提取模型名
            match = re.search(r"schemas\.(\w+)", ann_str)
            if match:
                return f"PydanticModel:{match.group(1)}"
        
        # 解析基础类型
        type_mapping = {
            "int": "int",
            "float": "float", 
            "str": "str",
            "bool": "bool",
            "list": "list",
            "dict": "dict",
            "Optional": "Optional",
            "Query": "QueryParam",
            "Path": "PathParam",
            "Body": "RequestBody",
            "Depends": "Dependency",
        }
        
        for key, value in type_mapping.items():
            if key in ann_str:
                return value
        
        return "Unknown"
    
    def _has_validation_rules(self, annotation_str: str) -> bool:
        """检查是否有验证规则"""
        validation_patterns = [
            r"Query\(.*\)",
            r"Path\(.*\)", 
            r"Body\(.*\)",
            r"Field\(.*\)",
            r"ge=",
            r"gt=",
            r"le=",
            r"lt=",
            r"min_length=",
            r"max_length=",
            r"regex=",
            r"pattern=",
        ]
        
        for pattern in validation_patterns:
            if re.search(pattern, annotation_str):
                return True
        
        return False
    
    def _extract_validation_rules(self, annotation_str: str) -> List[str]:
        """提取验证规则"""
        rules = []
        
        # 提取Query/Path参数验证
        query_patterns = [
            (r"ge=(\d+)", "最小值: {}"),
            (r"gt=(\d+)", "大于: {}"),
            (r"le=(\d+)", "最大值: {}"),
            (r"lt=(\d+)", "小于: {}"),
            (r"min_length=(\d+)", "最小长度: {}"),
            (r"max_length=(\d+)", "最大长度: {}"),
            (r"regex=['\"]([^'\"]+)['\"]", "正则表达式: {}"),
        ]
        
        for pattern, desc in query_patterns:
            match = re.search(pattern, annotation_str)
            if match:
                rules.append(desc.format(match.group(1)))
        
        return rules
    
    def _analyze_parameter_validation(
        self, param: Dict, route_path: str, route_method: str, file_path: Path
    ) -> List[Dict]:
        """分析单个参数的验证问题"""
        issues = []
        
        param_name = param["name"]
        param_type = param["type"]
        has_validation = param["has_validation"]
        
        # 检查必需参数的验证
        if param_type in ["QueryParam", "PathParam"] and not has_validation:
            # 识别潜在风险
            if self._is_sensitive_parameter(param_name):
                issues.append({
                    "type": "missing_parameter_validation",
                    "severity": "medium",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "parameter": param_name,
                    "parameter_type": param_type,
                    "description": f"敏感参数 '{param_name}' 缺少验证规则",
                    "recommendation": f"为 {param_type} 参数添加验证规则，如 ge=1, min_length=1 等",
                })
            elif param_name in ["id", "user_id", "page", "size"]:
                issues.append({
                    "type": "missing_parameter_validation",
                    "severity": "low",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "parameter": param_name,
                    "parameter_type": param_type,
                    "description": f"常用参数 '{param_name}' 缺少验证规则",
                    "recommendation": f"为 {param_type} 参数添加适当的验证规则",
                })
        
        return issues
    
    def _analyze_request_body_validation(
        self, func_node: ast.FunctionDef, route_path: str, route_method: str, file_path: Path
    ) -> List[Dict]:
        """分析请求体验证问题"""
        issues = []
        
        # 检查函数是否有Pydantic模型参数
        has_pydantic_model = False
        
        for arg in func_node.args.args:
            if arg.annotation:
                ann_str = ast.unparse(arg.annotation)
                if "schemas." in ann_str or "Pydantic" in ann_str:
                    has_pydantic_model = True
                    break
        
        # 对于POST/PUT/PATCH请求，建议使用Pydantic模型
        if not has_pydantic_model and route_method in ["POST", "PUT", "PATCH"]:
            if self._is_data_creation_route(route_path):
                issues.append({
                    "type": "missing_request_body_validation",
                    "severity": "high",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "description": "数据创建接口缺少Pydantic模型验证",
                    "recommendation": "创建并使用Pydantic模型来验证请求体数据",
                })
        
        return issues
    
    def _analyze_path_parameter_validation(
        self, route_path: str, route_method: str, file_path: Path
    ) -> List[Dict]:
        """分析路径参数验证问题"""
        issues = []
        
        # 提取路径参数
        path_params = re.findall(r"\{(\w+)\}", route_path)
        
        for param in path_params:
            # 检查常见路径参数是否需要验证
            if param in ["id", "user_id", "source_id", "task_id"]:
                issues.append({
                    "type": "missing_path_parameter_validation",
                    "severity": "medium",
                    "route": route_path,
                    "method": route_method,
                    "file": str(file_path.relative_to(self.backend_dir)),
                    "parameter": param,
                    "description": f"路径参数 '{param}' 缺少验证规则",
                    "recommendation": f"使用 Path(..., gt=0) 或其他验证规则",
                })
        
        return issues
    
    def _is_sensitive_parameter(self, param_name: str) -> bool:
        """判断是否是敏感参数"""
        sensitive_params = [
            "password",
            "token", 
            "secret",
            "key",
            "credit_card",
            "ssn",
            "phone",
            "email",
        ]
        
        return param_name.lower() in sensitive_params
    
    def _is_data_creation_route(self, route_path: str) -> bool:
        """判断是否是数据创建接口"""
        creation_patterns = [
            r"/create.*",
            r"/register.*",
            r"/add.*",
            r"/insert.*",
            r"/new.*",
            r"/save.*",
        ]
        
        route_lower = route_path.lower()
        
        for pattern in creation_patterns:
            if re.match(pattern, route_lower):
                return True
        
        # 根据HTTP方法和路径模式判断
        if any(keyword in route_lower for keyword in ["/users", "/data", "/source", "/task"]):
            return True
        
        return False
    
    def _analyze_route_validation(self, route: Dict) -> List[Dict]:
        """分析单个路由的验证问题"""
        issues = []
        
        # 规范化参数结构
        normalized_params = []
        for param in route.get("parameters", []):
            # 确保参数有必要的字段
            norm_param = {
                "name": param.get("name", ""),
                "type": param.get("type", "Any"),
                "has_validation": param.get("has_validation", False),
                "validation_rules": param.get("validation_rules", [])
            }
            # 如果缺少validation信息，尝试从类型字符串推断
            if not norm_param["has_validation"] and "type" in param:
                ann_str = str(param["type"])
                norm_param["has_validation"] = self._has_validation_rules(ann_str)
                if norm_param["has_validation"]:
                    norm_param["validation_rules"] = self._extract_validation_rules(ann_str)
            normalized_params.append(norm_param)
        
        # 检查路由参数
        for param in normalized_params:
            param_issues = self._analyze_parameter_validation(
                param, route["path"], route["method"], Path(route["file_path"])
            )
            issues.extend(param_issues)
        
        # 检查请求体验证
        if route["method"] in ["POST", "PUT", "PATCH"]:
            if self._is_data_creation_route(route["path"]):
                issues.append({
                    "type": "missing_request_body_validation",
                    "severity": "high",
                    "route": route["path"],
                    "method": route["method"],
                    "file": route["file_path"],
                    "description": "数据创建接口缺少Pydantic模型验证",
                    "recommendation": "创建并使用Pydantic模型来验证请求体数据",
                })
        
        # 检查路径参数验证
        path_params = re.findall(r"\{(\w+)\}", route["path"])
        for param in path_params:
            if param in ["id", "user_id", "source_id", "task_id"]:
                issues.append({
                    "type": "missing_path_parameter_validation",
                    "severity": "medium",
                    "route": route["path"],
                    "method": route["method"],
                    "file": route["file_path"],
                    "parameter": param,
                    "description": f"路径参数 '{param}' 缺少验证规则",
                    "recommendation": f"使用 Path(..., gt=0) 或其他验证规则",
                })
        
        return issues
    
    def generate_validation_report(self) -> Dict:
        """生成验证分析报告"""
        if not self.validation_issues:
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
        
        for issue in self.validation_issues:
            issue_type = issue["type"]
            severity = issue["severity"]
            
            by_type[issue_type] = by_type.get(issue_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        report = {
            "summary": {
                "total_issues": len(self.validation_issues),
                "by_type": by_type,
                "by_severity": by_severity,
            },
            "issues": self.validation_issues
        }
        
        return report
    
    def get_high_priority_validation_issues(self) -> List[Dict]:
        """获取高优先级验证问题"""
        return [issue for issue in self.validation_issues if issue["severity"] == "high"]
    
    def get_missing_request_body_issues(self) -> List[Dict]:
        """获取缺少请求体验证的问题"""
        return [issue for issue in self.validation_issues if issue["type"] == "missing_request_body_validation"]