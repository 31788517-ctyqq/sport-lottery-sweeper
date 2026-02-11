"""
API扫描器主入口
提供完整的API扫描功能
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

from .core.router_analyzer import RouterAnalyzer
from .core.auth_analyzer import AuthAnalyzer
from .core.validation_analyzer import ValidationAnalyzer
from .core.report_generator import ReportGenerator


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scanner.log")
    ]
)

logger = logging.getLogger(__name__)


class APIScanner:
    """API扫描器主类"""
    
    def __init__(self, backend_dir: str = "backend", output_dir: str = "reports"):
        """
        初始化API扫描器
        
        Args:
            backend_dir: backend目录路径
            output_dir: 报告输出目录
        """
        self.backend_dir = Path(backend_dir).resolve()
        self.output_dir = Path(output_dir)
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.router_analyzer = RouterAnalyzer(str(self.backend_dir))
        self.auth_analyzer = AuthAnalyzer(str(self.backend_dir))
        self.validation_analyzer = ValidationAnalyzer(str(self.backend_dir))
        self.report_generator = ReportGenerator(str(self.output_dir))
        
        # 扫描结果
        self.route_report: Optional[Dict] = None
        self.auth_issues: List[Dict] = []
        self.validation_issues: List[Dict] = []
        self.comprehensive_report: Optional[Dict] = None
        
    def scan_directory(self, api_dir: str = "api/v1") -> Dict:
        """
        扫描指定目录中的API
        
        Args:
            api_dir: API目录相对路径
            
        Returns:
            Dict: 扫描报告
        """
        logger.info(f"开始扫描API目录: {api_dir}")
        
        try:
            # 1. 分析路由
            routes = self.router_analyzer.analyze_directory(api_dir)
            self.route_report = self.router_analyzer.generate_route_report()
            
            logger.info(f"路由分析完成，共发现 {len(routes)} 个路由")
            
            # 2. 分析认证问题
            self.auth_issues = self.auth_analyzer.analyze_routes(routes)
            auth_report = self.auth_analyzer.generate_auth_report()
            
            logger.info(f"认证分析完成，共发现 {len(self.auth_issues)} 个问题")
            
            # 3. 分析验证问题
            self.validation_issues = self.validation_analyzer.analyze_routes(routes)
            validation_report = self.validation_analyzer.generate_validation_report()
            
            logger.info(f"验证分析完成，共发现 {len(self.validation_issues)} 个问题")
            
            # 4. 生成综合报告
            scan_config = {
                "api_dir": api_dir,
                "timestamp": self._get_timestamp(),
            }
            
            self.comprehensive_report = self.report_generator.generate_comprehensive_report(
                self.route_report,
                self.auth_issues,
                self.validation_issues,
                scan_config
            )
            
            # 5. 保存报告
            report_path = self.report_generator.save_report(self.comprehensive_report)
            
            # 6. 生成CSV摘要
            csv_path = self.report_generator.generate_issue_summary_csv(self.comprehensive_report)
            
            # 7. 打印摘要
            self.report_generator.print_report_summary(self.comprehensive_report)
            
            logger.info(f"扫描完成，报告已保存到: {report_path}")
            logger.info(f"CSV摘要已保存到: {csv_path}")
            
            return self.comprehensive_report
            
        except Exception as e:
            logger.error(f"扫描过程中发生错误: {e}")
            raise
    
    def scan_fastapi_app(self, app) -> Dict:
        """
        扫描FastAPI应用实例
        
        Args:
            app: FastAPI应用实例
            
        Returns:
            Dict: 扫描报告
        """
        logger.info("开始扫描FastAPI应用")
        
        try:
            # 1. 分析路由
            routes = self.router_analyzer.analyze_fastapi_app(app)
            self.route_report = self.router_analyzer.generate_route_report()
            
            logger.info(f"路由分析完成，共发现 {len(routes)} 个路由")
            
            # 2. 分析认证问题
            self.auth_issues = self.auth_analyzer.analyze_routes(routes)
            auth_report = self.auth_analyzer.generate_auth_report()
            
            logger.info(f"认证分析完成，共发现 {len(self.auth_issues)} 个问题")
            
            # 3. 分析验证问题
            self.validation_issues = self.validation_analyzer.analyze_routes(routes)
            validation_report = self.validation_analyzer.generate_validation_report()
            
            logger.info(f"验证分析完成，共发现 {len(self.validation_issues)} 个问题")
            
            # 4. 生成综合报告
            scan_config = {
                "scan_type": "fastapi_app",
                "timestamp": self._get_timestamp(),
            }
            
            self.comprehensive_report = self.report_generator.generate_comprehensive_report(
                self.route_report,
                self.auth_issues,
                self.validation_issues,
                scan_config
            )
            
            # 5. 保存报告
            report_path = self.report_generator.save_report(self.comprehensive_report)
            
            # 6. 生成CSV摘要
            csv_path = self.report_generator.generate_issue_summary_csv(self.comprehensive_report)
            
            # 7. 打印摘要
            self.report_generator.print_report_summary(self.comprehensive_report)
            
            logger.info(f"扫描完成，报告已保存到: {report_path}")
            logger.info(f"CSV摘要已保存到: {csv_path}")
            
            return self.comprehensive_report
            
        except Exception as e:
            logger.error(f"扫描过程中发生错误: {e}")
            raise
    
    def generate_test_cases(self, output_dir: str = "generated_tests") -> List[str]:
        """
        生成测试用例
        
        Args:
            output_dir: 测试用例输出目录
            
        Returns:
            List[str]: 生成的测试文件路径列表
        """
        test_dir = Path(output_dir)
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_files = []
        
        # 生成认证测试
        if self.auth_issues:
            auth_tests = self._generate_auth_test_cases()
            auth_test_file = test_dir / "test_auth_issues.py"
            
            with open(auth_test_file, "w", encoding="utf-8") as f:
                f.write(auth_tests)
            
            test_files.append(str(auth_test_file))
            logger.info(f"认证测试用例已生成: {auth_test_file}")
        
        # 生成验证测试
        if self.validation_issues:
            validation_tests = self._generate_validation_test_cases()
            validation_test_file = test_dir / "test_validation_issues.py"
            
            with open(validation_test_file, "w", encoding="utf-8") as f:
                f.write(validation_tests)
            
            test_files.append(str(validation_test_file))
            logger.info(f"验证测试用例已生成: {validation_test_file}")
        
        # 生成404测试
        if self.route_report:
            missing_routes = self._identify_missing_routes()
            if missing_routes:
                missing_route_tests = self._generate_missing_route_test_cases(missing_routes)
                missing_test_file = test_dir / "test_missing_routes.py"
                
                with open(missing_test_file, "w", encoding="utf-8") as f:
                    f.write(missing_route_tests)
                
                test_files.append(str(missing_test_file))
                logger.info(f"缺失路由测试用例已生成: {missing_test_file}")
        
        return test_files
    
    def _generate_auth_test_cases(self) -> str:
        """生成认证测试用例"""
        test_code = '''
"""
自动生成的认证测试用例
检测401/403问题
"""
import pytest
from fastapi.testclient import TestClient

# 注意: 需要导入你的FastAPI应用
# from backend.main import app
# client = TestClient(app)

class TestAuthIssues:
    """
    认证问题测试类
    """
    
    # 自动生成的测试用例
'''
        
        for i, issue in enumerate(self.auth_issues, 1):
            test_code += f'''
    def test_auth_issue_{i}(self):
        """测试: {issue['description']}"""
        # TODO: 实现具体的测试逻辑
        # 预期: 未认证访问应返回401或403
        pass
'''
        
        return test_code
    
    def _generate_validation_test_cases(self) -> str:
        """生成验证测试用例"""
        test_code = '''
"""
自动生成的验证测试用例
检测422问题
"""
import pytest
from fastapi.testclient import TestClient

# 注意: 需要导入你的FastAPI应用
# from backend.main import app
# client = TestClient(app)

class TestValidationIssues:
    """
    验证问题测试类
    """
    
    # 自动生成的测试用例
'''
        
        for i, issue in enumerate(self.validation_issues, 1):
            test_code += f'''
    def test_validation_issue_{i}(self):
        """测试: {issue['description']}"""
        # TODO: 实现具体的测试逻辑
        # 预期: 无效参数应返回422
        pass
'''
        
        return test_code
    
    def _identify_missing_routes(self) -> List[str]:
        """识别缺失的路由"""
        # 这里可以根据项目特点定义预期的路由模式
        expected_patterns = [
            "/api/v1/health",
            "/api/v1/info", 
            "/api/v1/users/profile",
            "/api/v1/admin/users",
        ]
        
        if self.route_report and self.route_report.get("route_patterns"):
            existing_patterns = set(self.route_report["route_patterns"])
            missing = [pattern for pattern in expected_patterns 
                      if pattern not in existing_patterns]
            return missing
        
        return []
    
    def _generate_missing_route_test_cases(self, missing_routes: List[str]) -> str:
        """生成缺失路由测试用例"""
        test_code = '''
"""
自动生成的缺失路由测试用例
检测404问题
"""
import pytest
from fastapi.testclient import TestClient

# 注意: 需要导入你的FastAPI应用
# from backend.main import app
# client = TestClient(app)

class TestMissingRoutes:
    """
    缺失路由测试类
    """
    
    # 自动生成的测试用例
'''
        
        for i, route in enumerate(missing_routes, 1):
            test_code += f'''
    def test_missing_route_{i}(self):
        """测试: 缺失路由 {route}"""
        # TODO: 实现具体的测试逻辑
        # 预期: 访问缺失路由应返回404
        pass
'''
        
        return test_code
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_summary(self) -> Dict:
        """获取扫描摘要"""
        if not self.comprehensive_report:
            return {"status": "未执行扫描"}
        
        metadata = self.comprehensive_report["metadata"]
        summary = metadata["summary"]
        
        return {
            "status": "扫描完成",
            "total_routes": summary["total_routes"],
            "total_issues": summary["total_auth_issues"] + summary["total_validation_issues"],
            "auth_issues": summary["total_auth_issues"],
            "validation_issues": summary["total_validation_issues"],
            "high_priority_issues": (
                summary.get("auth_issues_by_severity", {}).get("high", 0) +
                summary.get("validation_issues_by_severity", {}).get("high", 0)
            ),
            "timestamp": metadata["scan_timestamp"],
        }


# 命令行接口
def main():
    """命令行入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API扫描器 - 检测401/422/404/403问题")
    parser.add_argument("--backend-dir", default="backend", help="backend目录路径")
    parser.add_argument("--output-dir", default="reports", help="报告输出目录")
    parser.add_argument("--api-dir", default="api/v1", help="API目录路径")
    parser.add_argument("--generate-tests", action="store_true", help="生成测试用例")
    
    args = parser.parse_args()
    
    try:
        # 创建扫描器
        scanner = APIScanner(
            backend_dir=args.backend_dir,
            output_dir=args.output_dir
        )
        
        # 执行扫描
        report = scanner.scan_directory(args.api_dir)
        
        # 生成测试用例（如果指定）
        if args.generate_tests:
            test_files = scanner.generate_test_cases()
            print(f"✅ 已生成 {len(test_files)} 个测试文件")
        
        # 输出摘要
        summary = scanner.get_summary()
        print(f"\n📋 扫描摘要:")
        print(f"  总路由数: {summary['total_routes']}")
        print(f"  总问题数: {summary['total_issues']}")
        print(f"  认证问题: {summary['auth_issues']}")
        print(f"  验证问题: {summary['validation_issues']}")
        print(f"  高优先级问题: {summary['high_priority_issues']}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"扫描失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()