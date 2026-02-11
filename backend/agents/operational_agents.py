"""
运维智能体试点实现
包含日志分析智能体和健康检测智能体
"""

import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import psutil
import os

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from .enhanced_base_agent import OperationalAgent, AgentCapability
from ..services.langchain_service import LangChainService

logger = logging.getLogger(__name__)


class LogAnalysisAgent(OperationalAgent):
    """日志分析智能体"""
    
    def __init__(
        self,
        langchain_service: Optional[LangChainService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name="log_analysis_agent",
            description="智能日志分析系统，自动识别异常模式和潜在问题",
            langchain_service=langchain_service,
            config=config or {}
        )
        
        # 日志文件配置
        self.log_paths = self.config.get("log_paths", [
            "logs/app.log",
            "logs/error.log", 
            "logs/system.log"
        ])
        
        # 分析配置
        self.analysis_interval = self.config.get("analysis_interval", 300)  # 5分钟
        self.max_log_size = self.config.get("max_log_size", 100 * 1024 * 1024)  # 100MB
        
        # 告警阈值
        self.error_threshold = self.config.get("error_threshold", 10)
        self.warning_threshold = self.config.get("warning_threshold", 50)
        
        # 初始化日志分析链
        self._setup_log_analysis_chains()
    
    def _setup_log_analysis_chains(self):
        """设置日志分析链"""
        if not self.langchain_service:
            return
        
        # 错误模式识别链
        self._chains["error_pattern"] = self.langchain_service.create_simple_chain(
            "log_error_pattern",
            """分析以下日志内容，识别错误模式和潜在问题：

日志内容：
{log_content}

请按以下格式分析：
1. 错误类型分类
2. 错误频率统计
3. 影响范围评估
4. 建议解决方案

分析报告：""",
            input_variables=["log_content"]
        )
        
        # 性能问题识别链
        self._chains["performance_issue"] = self.langchain_service.create_simple_chain(
            "log_performance_issue",
            """分析以下日志内容，识别性能问题和优化建议：

日志内容：
{log_content}

请重点关注：
1. 响应时间异常
2. 资源使用高峰
3. 数据库查询性能
4. 缓存命中率

分析报告：""",
            input_variables=["log_content"]
        )
        
        # 安全事件识别链
        self._chains["security_event"] = self.langchain_service.create_simple_chain(
            "log_security_event",
            """分析以下日志内容，识别安全事件和潜在威胁：

日志内容：
{log_content}

请重点关注：
1. 异常访问模式
2. 认证失败尝试
3. SQL注入迹象
4. 文件系统异常操作

安全分析报告：""",
            input_variables=["log_content"]
        )
    
    async def _execute_operational_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行日志分析逻辑"""
        try:
            analysis_results = []
            alerts_generated = []
            
            # 收集日志数据
            log_data = await self._collect_log_data()
            
            if not log_data:
                return {
                    "success": True,
                    "message": "没有找到可分析的日志数据",
                    "analysis_results": [],
                    "alerts": []
                }
            
            # 分析每个日志文件
            for log_path, log_content in log_data.items():
                if not log_content:
                    continue
                
                # 基础分析
                basic_analysis = await self._basic_log_analysis(log_content)
                analysis_results.append({
                    "log_file": log_path,
                    "basic_analysis": basic_analysis
                })
                
                # 高级分析（使用LangChain）
                if self.langchain_service:
                    advanced_analysis = await self._advanced_log_analysis(log_content)
                    analysis_results[-1]["advanced_analysis"] = advanced_analysis
                    
                    # 检查是否需要生成告警
                    alerts = await self._generate_alerts(log_path, basic_analysis, advanced_analysis)
                    alerts_generated.extend(alerts)
            
            return {
                "success": True,
                "message": "日志分析完成",
                "analysis_results": analysis_results,
                "alerts": alerts_generated,
                "timestamp": datetime.now().isoformat(),
                "analyzed_files": len(log_data)
            }
            
        except Exception as e:
            logger.error(f"日志分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_results": [],
                "alerts": []
            }
    
    async def _collect_log_data(self) -> Dict[str, str]:
        """收集日志数据"""
        log_data = {}
        
        for log_path in self.log_paths:
            path = Path(log_path)
            
            if not path.exists():
                logger.warning(f"日志文件不存在: {log_path}")
                continue
            
            # 检查文件大小
            file_size = path.stat().st_size
            if file_size > self.max_log_size:
                logger.warning(f"日志文件过大，跳过分析: {log_path} ({file_size} bytes)")
                continue
            
            try:
                # 读取最近的内容（最后1000行）
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-1000:]  # 读取最后1000行
                    log_content = ''.join(recent_lines)
                    
                    if log_content.strip():
                        log_data[str(log_path)] = log_content
                        
            except Exception as e:
                logger.error(f"读取日志文件失败 {log_path}: {e}")
        
        return log_data
    
    async def _basic_log_analysis(self, log_content: str) -> Dict[str, Any]:
        """基础日志分析"""
        # 错误统计
        error_patterns = [
            (r'ERROR', 'ERROR'),
            (r'WARNING', 'WARNING'),
            (r'CRITICAL', 'CRITICAL'),
            (r'Exception', 'EXCEPTION'),
            (r'Traceback', 'TRACEBACK')
        ]
        
        stats = {}
        for pattern, level in error_patterns:
            count = len(re.findall(pattern, log_content, re.IGNORECASE))
            stats[level] = count
        
        # 时间范围分析
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        timestamps = re.findall(time_pattern, log_content)
        
        time_range = {
            "first_timestamp": timestamps[0] if timestamps else None,
            "last_timestamp": timestamps[-1] if timestamps else None,
            "total_entries": len(timestamps)
        }
        
        # 严重程度评估
        total_errors = sum(stats.values())
        severity = "LOW"
        
        if total_errors > self.error_threshold:
            severity = "HIGH"
        elif total_errors > self.warning_threshold:
            severity = "MEDIUM"
        
        return {
            "error_statistics": stats,
            "time_analysis": time_range,
            "severity": severity,
            "total_errors": total_errors
        }
    
    async def _advanced_log_analysis(self, log_content: str) -> Dict[str, Any]:
        """高级日志分析（使用LangChain）"""
        if not self.langchain_service:
            return {"message": "LangChain服务未启用"}
        
        try:
            # 使用错误模式识别链
            error_analysis = await self.execute_with_langchain(
                "error_pattern", 
                {"log_content": log_content[:5000]}  # 限制输入长度
            )
            
            # 使用性能问题识别链
            performance_analysis = await self.execute_with_langchain(
                "performance_issue",
                {"log_content": log_content[:5000]}
            )
            
            return {
                "error_analysis": error_analysis,
                "performance_analysis": performance_analysis,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"高级日志分析失败: {e}")
            return {"error": str(e)}
    
    async def _generate_alerts(self, log_path: str, basic_analysis: Dict[str, Any], 
                             advanced_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成告警"""
        alerts = []
        
        # 基于基础分析的告警
        if basic_analysis["severity"] == "HIGH":
            alerts.append({
                "type": "ERROR_THRESHOLD_EXCEEDED",
                "severity": "HIGH",
                "title": f"日志错误阈值超过限制: {log_path}",
                "message": f"检测到 {basic_analysis['total_errors']} 个错误，超过阈值 {self.error_threshold}",
                "data": basic_analysis
            })
        
        elif basic_analysis["severity"] == "MEDIUM":
            alerts.append({
                "type": "WARNING_THRESHOLD_EXCEEDED", 
                "severity": "MEDIUM",
                "title": f"日志警告阈值超过限制: {log_path}",
                "message": f"检测到 {basic_analysis['total_errors']} 个警告/错误",
                "data": basic_analysis
            })
        
        # 基于高级分析的告警
        if "error_analysis" in advanced_analysis and advanced_analysis["error_analysis"].get("success"):
            result = advanced_analysis["error_analysis"]["result"]
            if "严重" in result or "紧急" in result:
                alerts.append({
                    "type": "CRITICAL_PATTERN_DETECTED",
                    "severity": "CRITICAL", 
                    "title": f"检测到严重错误模式: {log_path}",
                    "message": "AI分析发现严重错误模式，需要立即关注",
                    "data": advanced_analysis["error_analysis"]
                })
        
        return alerts


class HealthCheckAgent(OperationalAgent):
    """系统健康检测智能体"""
    
    def __init__(
        self,
        langchain_service: Optional[LangChainService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name="health_check_agent",
            description="系统健康状态监控和预警系统",
            langchain_service=langchain_service,
            config=config or {}
        )
        
        # 健康检查配置
        self.check_interval = self.config.get("check_interval", 60)  # 1分钟
        self.thresholds = self.config.get("thresholds", {
            "cpu_usage": 80.0,      # CPU使用率阈值
            "memory_usage": 85.0,   # 内存使用率阈值
            "disk_usage": 90.0,     # 磁盘使用率阈值
            "response_time": 5.0,   # 响应时间阈值（秒）
        })
        
        # 服务检查配置
        self.services_to_check = self.config.get("services", [
            "backend", "frontend", "database", "redis"
        ])
    
    async def _execute_operational_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行健康检查逻辑"""
        try:
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "HEALTHY",
                "components": {},
                "alerts": []
            }
            
            # 系统资源检查
            system_health = await self._check_system_resources()
            health_report["components"]["system"] = system_health
            
            # 服务状态检查
            service_health = await self._check_services()
            health_report["components"]["services"] = service_health
            
            # 应用健康检查
            app_health = await self._check_application()
            health_report["components"]["application"] = app_health
            
            # 数据库健康检查
            db_health = await self._check_database()
            health_report["components"]["database"] = db_health
            
            # 综合健康评估
            overall_health = await self._assess_overall_health(health_report["components"])
            health_report["overall_health"] = overall_health["status"]
            health_report["alerts"] = overall_health["alerts"]
            
            # 使用LangChain进行智能分析
            if self.langchain_service:
                intelligent_analysis = await self._intelligent_health_analysis(health_report)
                health_report["intelligent_analysis"] = intelligent_analysis
            
            return {
                "success": True,
                "health_report": health_report,
                "message": "健康检查完成"
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "health_report": {}
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 系统负载
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            # 网络连接
            net_io = psutil.net_io_counters()
            
            health_status = "HEALTHY"
            alerts = []
            
            # 检查阈值
            if cpu_percent > self.thresholds["cpu_usage"]:
                health_status = "WARNING"
                alerts.append({
                    "type": "HIGH_CPU_USAGE",
                    "severity": "MEDIUM",
                    "message": f"CPU使用率过高: {cpu_percent:.1f}%"
                })
            
            if memory_percent > self.thresholds["memory_usage"]:
                health_status = "WARNING"
                alerts.append({
                    "type": "HIGH_MEMORY_USAGE",
                    "severity": "MEDIUM", 
                    "message": f"内存使用率过高: {memory_percent:.1f}%"
                })
            
            if disk_percent > self.thresholds["disk_usage"]:
                health_status = "CRITICAL"
                alerts.append({
                    "type": "HIGH_DISK_USAGE",
                    "severity": "HIGH",
                    "message": f"磁盘使用率过高: {disk_percent:.1f}%"
                })
            
            return {
                "status": health_status,
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory_percent,
                    "disk_usage": disk_percent,
                    "load_average": load_avg,
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv
                },
                "alerts": alerts
            }
            
        except Exception as e:
            logger.error(f"系统资源检查失败: {e}")
            return {
                "status": "UNKNOWN",
                "error": str(e),
                "metrics": {},
                "alerts": [{
                    "type": "SYSTEM_CHECK_FAILED",
                    "severity": "HIGH",
                    "message": f"系统资源检查失败: {e}"
                }]
            }
    
    async def _check_services(self) -> Dict[str, Any]:
        """检查服务状态"""
        service_status = {}
        alerts = []
        
        for service in self.services_to_check:
            try:
                # 这里实现具体的服务检查逻辑
                # 暂时模拟检查结果
                is_running = await self._check_service_status(service)
                
                service_status[service] = {
                    "status": "RUNNING" if is_running else "STOPPED",
                    "last_check": datetime.now().isoformat()
                }
                
                if not is_running:
                    alerts.append({
                        "type": "SERVICE_DOWN",
                        "severity": "HIGH",
                        "message": f"服务 {service} 未运行",
                        "service": service
                    })
                    
            except Exception as e:
                service_status[service] = {
                    "status": "UNKNOWN",
                    "error": str(e)
                }
                alerts.append({
                    "type": "SERVICE_CHECK_FAILED",
                    "severity": "MEDIUM",
                    "message": f"服务 {service} 检查失败: {e}",
                    "service": service
                })
        
        # 总体状态
        running_services = sum(1 for s in service_status.values() if s.get("status") == "RUNNING")
        total_services = len(self.services_to_check)
        
        overall_status = "HEALTHY"
        if running_services < total_services:
            overall_status = "WARNING"
        if running_services == 0:
            overall_status = "CRITICAL"
        
        return {
            "status": overall_status,
            "services": service_status,
            "running_count": running_services,
            "total_count": total_services,
            "alerts": alerts
        }
    
    async def _check_service_status(self, service_name: str) -> bool:
        """检查单个服务状态（模拟实现）"""
        # 这里应该实现具体的服务检查逻辑
        # 暂时返回True模拟服务正常运行
        
        # 模拟不同服务的检查逻辑
        if service_name == "backend":
            # 检查后端API是否可达
            return True
        elif service_name == "database":
            # 检查数据库连接
            return True
        elif service_name == "redis":
            # 检查Redis连接
            return True
        else:
            # 默认返回运行中
            return True
    
    async def _check_application(self) -> Dict[str, Any]:
        """检查应用状态"""
        try:
            # 这里实现应用级别的健康检查
            # 暂时返回模拟数据
            
            return {
                "status": "HEALTHY",
                "metrics": {
                    "uptime": "2 days 5 hours",
                    "active_sessions": 15,
                    "request_rate": 120.5,
                    "error_rate": 0.5
                },
                "alerts": []
            }
            
        except Exception as e:
            return {
                "status": "UNKNOWN",
                "error": str(e),
                "alerts": [{
                    "type": "APP_CHECK_FAILED",
                    "severity": "MEDIUM",
                    "message": f"应用检查失败: {e}"
                }]
            }
    
    async def _check_database(self) -> Dict[str, Any]:
        """检查数据库状态"""
        try:
            # 这里实现数据库健康检查
            # 暂时返回模拟数据
            
            return {
                "status": "HEALTHY",
                "metrics": {
                    "connections": 8,
                    "query_per_second": 45.2,
                    "cache_hit_rate": 95.7
                },
                "alerts": []
            }
            
        except Exception as e:
            return {
                "status": "UNKNOWN", 
                "error": str(e),
                "alerts": [{
                    "type": "DB_CHECK_FAILED",
                    "severity": "HIGH",
                    "message": f"数据库检查失败: {e}"
                }]
            }
    
    async def _assess_overall_health(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """综合健康评估"""
        status_priority = {
            "CRITICAL": 4,
            "WARNING": 3, 
            "UNKNOWN": 2,
            "HEALTHY": 1
        }
        
        # 找出最严重的状态
        worst_status = "HEALTHY"
        alerts = []
        
        for component_name, component_data in components.items():
            status = component_data.get("status", "UNKNOWN")
            
            if status_priority[status] > status_priority[worst_status]:
                worst_status = status
            
            # 收集所有告警
            alerts.extend(component_data.get("alerts", []))
        
        return {
            "status": worst_status,
            "alerts": alerts,
            "component_count": len(components),
            "assessment_timestamp": datetime.now().isoformat()
        }
    
    async def _intelligent_health_analysis(self, health_report: Dict[str, Any]) -> Dict[str, Any]:
        """智能健康分析（使用LangChain）"""
        if not self.langchain_service:
            return {"message": "LangChain服务未启用"}
        
        try:
            # 准备分析数据
            analysis_data = {
                "overall_health": health_report["overall_health"],
                "components": health_report["components"],
                "alerts_count": len(health_report["alerts"])
            }
            
            # 创建健康分析链
            analysis_chain = self.langchain_service.create_simple_chain(
                "health_analysis",
                """基于以下系统健康数据，提供专业分析建议：

系统健康报告：
{health_data}

请提供：
1. 系统健康度评估
2. 潜在风险识别
3. 优化建议
4. 预防性维护建议

专业分析报告：""",
                input_variables=["health_data"]
            )
            
            # 执行分析
            result = await self.langchain_service.run_chain(
                "health_analysis",
                {"health_data": str(analysis_data)}
            )
            
            return {
                "analysis_result": result,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"智能健康分析失败: {e}")
            return {"error": str(e)}


# 运维智能体工厂函数
def create_operational_agent(
    agent_type: str,
    langchain_service: Optional[LangChainService] = None,
    config: Optional[Dict[str, Any]] = None
) -> OperationalAgent:
    """创建运维智能体"""
    
    if agent_type == "log_analysis":
        return LogAnalysisAgent(langchain_service, config)
    
    elif agent_type == "health_check":
        return HealthCheckAgent(langchain_service, config)
    
    else:
        raise ValueError(f"未知的运维智能体类型: {agent_type}")


# 预定义的运维智能体配置
OPERATIONAL_AGENT_CONFIGS = {
    "log_analysis": {
        "name": "日志分析智能体",
        "type": "log_analysis",
        "description": "自动分析系统日志，识别异常和性能问题",
        "config": {
            "log_paths": ["logs/app.log", "logs/error.log"],
            "analysis_interval": 300,
            "error_threshold": 10,
            "warning_threshold": 50
        }
    },
    "health_check": {
        "name": "健康检测智能体", 
        "type": "health_check",
        "description": "监控系统资源和服务状态，及时发现问题",
        "config": {
            "check_interval": 60,
            "thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0
            },
            "services": ["backend", "database", "redis"]
        }
    }
}