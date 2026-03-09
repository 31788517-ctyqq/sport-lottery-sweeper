"""
报告生成器
用于生成扫描结果报告
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_comprehensive_report(
        self,
        route_report: Dict,
        auth_issues: List[Dict],
        validation_issues: List[Dict],
        scan_config: Optional[Dict] = None
    ) -> Dict:
        """
        生成综合扫描报告
        
        Args:
            route_report: 路由分析报告
            auth_issues: 认证问题列表
            validation_issues: 验证问题列表
            scan_config: 扫描配置
            
        Returns:
            Dict: 综合报告
        """
        timestamp = datetime.now().isoformat()
        
        # 统计信息
        total_auth_issues = len(auth_issues)
        total_validation_issues = len(validation_issues)
        total_routes = route_report.get("total_routes", 0)
        
        # 按严重程度分类
        auth_by_severity = {}
        for issue in auth_issues:
            severity = issue.get("severity", "unknown")
            auth_by_severity[severity] = auth_by_severity.get(severity, 0) + 1
        
        validation_by_severity = {}
        for issue in validation_issues:
            severity = issue.get("severity", "unknown")
            validation_by_severity[severity] = validation_by_severity.get(severity, 0) + 1
        
        # 生成报告
        report = {
            "metadata": {
                "scan_timestamp": timestamp,
                "scan_config": scan_config or {},
                "summary": {
                    "total_routes": total_routes,
                    "total_auth_issues": total_auth_issues,
                    "total_validation_issues": total_validation_issues,
                    "auth_issues_by_severity": auth_by_severity,
                    "validation_issues_by_severity": validation_by_severity,
                }
            },
            "route_analysis": route_report,
            "auth_issues": auth_issues,
            "validation_issues": validation_issues,
            "recommendations": self._generate_recommendations(
                auth_issues, validation_issues, total_routes
            ),
        }
        
        return report
    
    def save_report(self, report: Dict, report_name: Optional[str] = None) -> str:
        """
        保存报告到文件
        
        Args:
            report: 报告数据
            report_name: 报告文件名（可选）
            
        Returns:
            str: 报告文件路径
        """
        if report_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"api_scan_report_{timestamp}"
        
        # 确保扩展名正确
        if not report_name.endswith(".json"):
            report_name = f"{report_name}.json"
        
        report_path = self.output_dir / report_name
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"报告已保存到: {report_path}")
            
            # 同时生成Markdown格式的报告
            md_path = self.output_dir / f"{Path(report_name).stem}.md"
            self._generate_markdown_report(report, md_path)
            
            return str(report_path)
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            raise
    
    def _generate_recommendations(
        self, auth_issues: List[Dict], validation_issues: List[Dict], total_routes: int
    ) -> Dict[str, Any]:
        """
        生成修复建议
        
        Returns:
            Dict: 修复建议
        """
        recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "preventive_measures": [],
        }
        
        # 高优先级建议
        high_auth_issues = [issue for issue in auth_issues if issue.get("severity") == "high"]
        high_validation_issues = [issue for issue in validation_issues if issue.get("severity") == "high"]
        
        if high_auth_issues:
            recommendations["high_priority"].append({
                "title": "修复敏感接口的认证缺失",
                "description": f"发现 {len(high_auth_issues)} 个敏感接口缺少认证保护",
                "action_items": [
                    "检查缺少认证的接口，添加合适的Depends依赖",
                    "重新测试接口，确保未认证访问返回401",
                    "更新API文档，标注接口认证要求",
                ]
            })
        
        if high_validation_issues:
            recommendations["high_priority"].append({
                "title": "修复数据创建接口的参数验证",
                "description": f"发现 {len(high_validation_issues)} 个数据创建接口缺少参数验证",
                "action_items": [
                    "为数据创建接口创建Pydantic模型",
                    "添加必要的字段验证规则",
                    "测试接口，确保无效参数返回422",
                ]
            })
        
        # 中优先级建议
        medium_auth_issues = [issue for issue in auth_issues if issue.get("severity") == "medium"]
        medium_validation_issues = [issue for issue in validation_issues if issue.get("severity") == "medium"]
        
        if medium_auth_issues:
            recommendations["medium_priority"].append({
                "title": "修复管理员接口的权限检查",
                "description": f"发现 {len(medium_auth_issues)} 个管理员接口缺少权限检查",
                "action_items": [
                    "为管理员接口添加Depends(get_current_admin)",
                    "实现角色检查逻辑",
                    "测试接口，确保权限不足返回403",
                ]
            })
        
        if medium_validation_issues:
            recommendations["medium_priority"].append({
                "title": "修复路径参数验证",
                "description": f"发现 {len(medium_validation_issues)} 个路径参数缺少验证规则",
                "action_items": [
                    "为路径参数添加Path(..., gt=0)等验证规则",
                    "添加输入边界检查",
                    "测试接口，确保无效路径参数返回422",
                ]
            })
        
        # 低优先级建议
        low_auth_issues = [issue for issue in auth_issues if issue.get("severity") == "low"]
        low_validation_issues = [issue for issue in validation_issues if issue.get("severity") == "low"]
        
        if low_auth_issues:
            recommendations["low_priority"].append({
                "title": "优化公共接口的认证设置",
                "description": f"发现 {len(low_auth_issues)} 个公共接口存在不必要的认证",
                "action_items": [
                    "检查公共接口的认证必要性",
                    "移除不必要的Depends依赖",
                    "更新接口文档，明确认证要求",
                ]
            })
        
        # 预防措施
        if total_routes > 0:
            issues_percentage = ((len(auth_issues) + len(validation_issues)) / total_routes) * 100
            
            recommendations["preventive_measures"] = [
                {
                    "title": "建立API开发规范",
                    "description": "制定统一的认证和参数验证标准",
                    "action_items": [
                        "为不同接口类型定义认证要求",
                        "建立Pydantic模型使用规范",
                        "制定路径参数和查询参数验证规则",
                    ]
                },
                {
                    "title": "实施代码审查流程",
                    "description": "在合并前检查认证和验证实现",
                    "action_items": [
                        "添加认证检查到代码审查清单",
                        "建立验证规则检查机制",
                        "实施自动化测试要求",
                    ]
                },
                {
                    "title": "集成自动化扫描",
                    "description": "在CI/CD流程中加入定期扫描",
                    "action_items": [
                        "设置每日自动扫描任务",
                        "配置扫描结果告警",
                        "建立问题跟踪和修复流程",
                    ]
                },
                {
                    "title": "提升测试覆盖率",
                    "description": f"当前问题占比: {issues_percentage:.1f}%",
                    "action_items": [
                        "为所有接口添加认证测试",
                        "实现参数验证测试用例",
                        "建立端到端测试覆盖关键流程",
                    ]
                }
            ]
        
        return recommendations
    
    def _generate_markdown_report(self, report: Dict, output_path: Path) -> None:
        """
        生成Markdown格式的报告
        
        Args:
            report: 报告数据
            output_path: 输出文件路径
        """
        try:
            metadata = report["metadata"]
            summary = metadata["summary"]
            
            with open(output_path, "w", encoding="utf-8") as f:
                # 报告标题
                f.write(f"# API扫描报告\n\n")
                f.write(f"扫描时间: {metadata['scan_timestamp']}\n\n")
                
                # 摘要统计
                f.write(f"## 📊 摘要统计\n\n")
                f.write(f"- **总路由数**: {summary['total_routes']}\n")
                f.write(f"- **认证问题**: {summary['total_auth_issues']} 个\n")
                f.write(f"- **验证问题**: {summary['total_validation_issues']} 个\n")
                f.write(f"- **总问题数**: {summary['total_auth_issues'] + summary['total_validation_issues']} 个\n\n")
                
                # 认证问题详情
                if report["auth_issues"]:
                    f.write(f"## 🔐 认证问题 ({len(report['auth_issues'])} 个)\n\n")
                    f.write("| 严重程度 | 路径 | 方法 | 描述 | 建议 |\n")
                    f.write("|----------|------|------|------|------|\n")
                    
                    for issue in report["auth_issues"]:
                        f.write(f"| {issue['severity']} | `{issue['route']}` | {issue['method']} | {issue['description']} | {issue['recommendation']} |\n")
                    
                    f.write("\n")
                
                # 验证问题详情
                if report["validation_issues"]:
                    f.write(f"## 📝 验证问题 ({len(report['validation_issues'])} 个)\n\n")
                    f.write("| 严重程度 | 路径 | 方法 | 描述 | 建议 |\n")
                    f.write("|----------|------|------|------|------|\n")
                    
                    for issue in report["validation_issues"]:
                        f.write(f"| {issue['severity']} | `{issue['route']}` | {issue['method']} | {issue['description']} | {issue['recommendation']} |\n")
                    
                    f.write("\n")
                
                # 修复建议
                if report["recommendations"]:
                    f.write(f"## 🛠️ 修复建议\n\n")
                    
                    for priority_level, issues in report["recommendations"].items():
                        if issues:
                            f.write(f"### {priority_level.replace('_', ' ').title()}\n\n")
                            
                            for issue in issues:
                                f.write(f"**{issue['title']}**\n\n")
                                f.write(f"{issue['description']}\n\n")
                                
                                if issue.get("action_items"):
                                    f.write("**行动项**:\n")
                                    for action in issue["action_items"]:
                                        f.write(f"- {action}\n")
                                    f.write("\n")
                
                # 预防措施
                if report["recommendations"].get("preventive_measures"):
                    f.write(f"## 🛡️ 预防措施\n\n")
                    
                    for measure in report["recommendations"]["preventive_measures"]:
                        f.write(f"### {measure['title']}\n\n")
                        f.write(f"{measure['description']}\n\n")
                        
                        if measure.get("action_items"):
                            f.write("**具体措施**:\n")
                            for action in measure["action_items"]:
                                f.write(f"- {action}\n")
                            f.write("\n")
            
            logger.info(f"Markdown报告已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
    
    def generate_issue_summary_csv(self, report: Dict, output_path: Optional[Path] = None) -> str:
        """
        生成问题摘要CSV文件
        
        Args:
            report: 报告数据
            output_path: 输出文件路径（可选）
            
        Returns:
            str: 输出文件路径
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"issues_summary_{timestamp}.csv"
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                # CSV头部
                f.write("issue_type,severity,route,method,file,description,recommendation\n")
                
                # 写入认证问题
                for issue in report.get("auth_issues", []):
                    f.write(f"\"{issue['type']}\",")
                    f.write(f"\"{issue['severity']}\",")
                    f.write(f"\"{issue['route']}\",")
                    f.write(f"\"{issue['method']}\",")
                    f.write(f"\"{issue['file']}\",")
                    f.write(f"\"{issue['description']}\",")
                    f.write(f"\"{issue['recommendation']}\"\n")
                
                # 写入验证问题
                for issue in report.get("validation_issues", []):
                    f.write(f"\"{issue['type']}\",")
                    f.write(f"\"{issue['severity']}\",")
                    f.write(f"\"{issue['route']}\",")
                    f.write(f"\"{issue['method']}\",")
                    f.write(f"\"{issue['file']}\",")
                    f.write(f"\"{issue['description']}\",")
                    f.write(f"\"{issue['recommendation']}\"\n")
            
            logger.info(f"CSV摘要已保存到: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"生成CSV摘要失败: {e}")
            raise
    
    def print_report_summary(self, report: Dict) -> None:
        """
        打印报告摘要到控制台
        
        Args:
            report: 报告数据
        """
        metadata = report["metadata"]
        summary = metadata["summary"]
        
        print("\n" + "="*60)
        print("📊 API扫描报告摘要")
        print("="*60)
        print(f"扫描时间: {metadata['scan_timestamp']}")
        print(f"总路由数: {summary['total_routes']}")
        print(f"认证问题: {summary['total_auth_issues']} 个")
        print(f"验证问题: {summary['total_validation_issues']} 个")
        print(f"总问题数: {summary['total_auth_issues'] + summary['total_validation_issues']} 个")
        
        if summary.get("auth_issues_by_severity"):
            print("\n🔐 认证问题严重程度分布:")
            for severity, count in summary["auth_issues_by_severity"].items():
                print(f"  {severity}: {count} 个")
        
        if summary.get("validation_issues_by_severity"):
            print("\n📝 验证问题严重程度分布:")
            for severity, count in summary["validation_issues_by_severity"].items():
                print(f"  {severity}: {count} 个")
        
        print("\n🛠️ 修复建议:")
        for priority_level, issues in report["recommendations"].items():
            if issues and priority_level != "preventive_measures":
                print(f"  {priority_level.replace('_', ' ').title()}: {len(issues)} 项")
        
        print("="*60 + "\n")