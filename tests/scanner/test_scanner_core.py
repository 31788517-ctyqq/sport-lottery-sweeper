"""
扫描器核心功能测试
"""
import pytest
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from scanner.core.router_analyzer import RouterAnalyzer
from scanner.core.auth_analyzer import AuthAnalyzer
from scanner.core.validation_analyzer import ValidationAnalyzer


class TestRouterAnalyzer:
    """路由分析器测试"""
    
    def setup_method(self):
        """测试设置"""
        self.backend_dir = str(Path(__file__).parent.parent.parent / "backend")
        self.analyzer = RouterAnalyzer(self.backend_dir)
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        assert self.analyzer.backend_dir == Path(self.backend_dir).resolve()
        assert self.analyzer.api_routes == []
        assert self.analyzer.route_patterns == set()
    
    def test_analyze_directory_structure(self):
        """测试目录分析结构"""
        routes = self.analyzer.analyze_directory("api/v1")
        
        # 检查返回类型
        assert isinstance(routes, list)
        
        # 检查路由信息结构
        if routes:
            route = routes[0]
            assert "path" in route
            assert "method" in route
            assert "file_path" in route
            assert "function_name" in route
    
    def test_generate_route_report(self):
        """测试路由报告生成"""
        # 先分析目录
        self.analyzer.analyze_directory("api/v1")
        
        # 生成报告
        report = self.analyzer.generate_route_report()
        
        # 检查报告结构
        assert isinstance(report, dict)
        assert "total_routes" in report
        assert "routes" in report
        assert "route_patterns" in report
        assert "analysis_summary" in report
    
    def test_route_patterns_collection(self):
        """测试路由模式收集"""
        # 分析目录
        self.analyzer.analyze_directory("api/v1")
        
        # 获取路由模式
        patterns = self.analyzer.get_route_patterns()
        
        assert isinstance(patterns, set)


class TestAuthAnalyzer:
    """认证分析器测试"""
    
    def setup_method(self):
        """测试设置"""
        self.backend_dir = str(Path(__file__).parent.parent.parent / "backend")
        self.analyzer = AuthAnalyzer(self.backend_dir)
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        assert self.analyzer.backend_dir == Path(self.backend_dir).resolve()
        assert self.analyzer.auth_issues == []
    
    def test_analyze_sensitive_routes(self):
        """测试敏感路由分析"""
        # 创建一个模拟的路由列表
        test_routes = [
            {
                "path": "/api/v1/users/profile",
                "method": "GET",
                "file_path": "api/v1/users.py",
                "requires_auth": False,
                "requires_admin": False,
            },
            {
                "path": "/api/v1/auth/login",
                "method": "POST",
                "file_path": "api/v1/auth.py",
                "requires_auth": False,
                "requires_admin": False,
            },
            {
                "path": "/api/v1/admin/users",
                "method": "GET",
                "file_path": "api/v1/admin.py",
                "requires_auth": True,
                "requires_admin": True,
            },
        ]
        
        # 分析路由
        issues = self.analyzer.analyze_routes(test_routes)
        
        # 检查分析结果
        assert isinstance(issues, list)
        
        # 应该检测到用户资料接口缺少认证
        user_profile_issue = None
        for issue in issues:
            if "/api/v1/users/profile" in issue.get("route", ""):
                user_profile_issue = issue
                break
        
        # 断言: 用户资料接口应该有认证缺失问题
        if user_profile_issue:
            assert user_profile_issue["type"] == "missing_auth"
            assert user_profile_issue["severity"] == "high"
    
    def test_generate_auth_report(self):
        """测试认证报告生成"""
        # 创建一些测试问题
        test_issues = [
            {
                "type": "missing_auth",
                "severity": "high",
                "route": "/api/v1/users/profile",
                "method": "GET",
                "file": "api/v1/users.py",
                "description": "敏感接口缺少认证保护",
                "recommendation": "添加Depends(get_current_user)",
            }
        ]
        
        self.analyzer.auth_issues = test_issues
        report = self.analyzer.generate_auth_report()
        
        # 检查报告结构
        assert isinstance(report, dict)
        assert "summary" in report
        assert "issues" in report
        
        summary = report["summary"]
        assert "total_issues" in summary
        assert summary["total_issues"] == 1


class TestValidationAnalyzer:
    """验证分析器测试"""
    
    def setup_method(self):
        """测试设置"""
        self.backend_dir = str(Path(__file__).parent.parent.parent / "backend")
        self.analyzer = ValidationAnalyzer(self.backend_dir)
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        assert self.analyzer.backend_dir == Path(self.backend_dir).resolve()
        assert self.analyzer.validation_issues == []
    
    def test_analyze_route_validation(self):
        """测试路由验证分析"""
        # 创建一个模拟的路由列表
        test_routes = [
            {
                "path": "/api/v1/users/{user_id}",
                "method": "GET",
                "file_path": "api/v1/users.py",
                "parameters": [
                    {
                        "name": "user_id",
                        "type": "PathParam",
                        "has_validation": False,
                    }
                ],
            },
            {
                "path": "/api/v1/users",
                "method": "POST",
                "file_path": "api/v1/users.py",
                "parameters": [],
            },
        ]
        
        # 分析路由
        issues = self.analyzer.analyze_routes(test_routes)
        
        # 检查分析结果
        assert isinstance(issues, list)
        
        # 应该检测到路径参数缺少验证
        path_param_issue = None
        for issue in issues:
            if "missing_path_parameter_validation" in issue.get("type", ""):
                path_param_issue = issue
                break
        
        # 断言: 路径参数应该有验证缺失问题
        if path_param_issue:
            assert path_param_issue["type"] == "missing_path_parameter_validation"
            assert path_param_issue["severity"] == "medium"
    
    def test_generate_validation_report(self):
        """测试验证报告生成"""
        # 创建一些测试问题
        test_issues = [
            {
                "type": "missing_path_parameter_validation",
                "severity": "medium",
                "route": "/api/v1/users/{user_id}",
                "method": "GET",
                "file": "api/v1/users.py",
                "parameter": "user_id",
                "description": "路径参数缺少验证规则",
                "recommendation": "使用 Path(..., gt=0)",
            }
        ]
        
        self.analyzer.validation_issues = test_issues
        report = self.analyzer.generate_validation_report()
        
        # 检查报告结构
        assert isinstance(report, dict)
        assert "summary" in report
        assert "issues" in report
        
        summary = report["summary"]
        assert "total_issues" in summary
        assert summary["total_issues"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])