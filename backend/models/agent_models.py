"""
智能体相关数据库模型
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseModel, TimestampMixin, SoftDeleteMixin


class AgentModel(BaseModel, SoftDeleteMixin):
    """智能体模型"""
    __tablename__ = "agents"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True, comment="智能体名称")
    display_name = Column(String(200), nullable=True, comment="显示名称")
    description = Column(Text, nullable=True, comment="智能体描述")
    agent_type = Column(String(50), nullable=False, index=True, comment="智能体类型")
    
    # 配置信息
    config = Column(JSON, default={}, comment="智能体配置")
    langchain_config = Column(JSON, default={}, comment="LangChain配置")
    
    # 状态信息
    status = Column(String(20), default="stopped", index=True, comment="智能体状态")
    enabled = Column(Boolean, default=True, index=True, comment="是否启用")
    
    # 执行配置
    max_concurrent = Column(Integer, default=1, comment="最大并发数")
    timeout = Column(Integer, default=300, comment="执行超时时间(秒)")
    retry_count = Column(Integer, default=3, comment="重试次数")
    
    # 调度配置
    schedule_enabled = Column(Boolean, default=False, comment="是否启用调度")
    schedule_config = Column(JSON, default={}, comment="调度配置")
    
    # 监控配置
    health_check_interval = Column(Integer, default=60, comment="健康检查间隔(秒)")
    metrics_retention = Column(Integer, default=86400, comment="指标保留时间(秒)")
    
    # 关系
    executions = relationship("AgentExecutionLog", back_populates="agent", cascade="all, delete-orphan")
    alerts = relationship("AgentAlert", back_populates="agent", cascade="all, delete-orphan")
    metrics = relationship("AgentMetric", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgentModel(id={self.id}, name='{self.name}', type='{self.agent_type}', status='{self.status}')>"


class AgentExecutionLog(BaseModel):
    """智能体执行日志"""
    __tablename__ = "agent_execution_logs"
    
    # 关联信息
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True, comment="智能体ID")
    
    # 执行信息
    task_type = Column(String(50), nullable=True, index=True, comment="任务类型")
    task_data = Column(JSON, default={}, comment="任务数据")
    input_data = Column(JSON, default={}, comment="输入数据")
    output_data = Column(JSON, default={}, comment="输出数据")
    
    # 执行结果
    success = Column(Boolean, default=True, index=True, comment="是否成功")
    execution_time = Column(Float, comment="执行时间(秒)")
    error_message = Column(Text, comment="错误信息")
    error_details = Column(JSON, default={}, comment="错误详情")
    
    # 资源使用
    memory_usage = Column(Float, comment="内存使用(MB)")
    cpu_usage = Column(Float, comment="CPU使用率(%)")
    
    # 时间戳
    started_at = Column(DateTime(timezone=True), nullable=False, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    
    # 关系
    agent = relationship("AgentModel", back_populates="executions")
    
    def __repr__(self):
        return f"<AgentExecutionLog(id={self.id}, agent_id={self.agent_id}, success={self.success}, time={self.execution_time}s)>"


class AgentAlert(BaseModel, SoftDeleteMixin):
    """智能体告警记录"""
    __tablename__ = "agent_alerts"
    
    # 关联信息
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True, comment="智能体ID")
    
    # 告警信息
    alert_type = Column(String(50), nullable=False, index=True, comment="告警类型")
    severity = Column(String(20), nullable=False, index=True, comment="严重程度")
    title = Column(String(200), nullable=False, comment="告警标题")
    message = Column(Text, nullable=False, comment="告警消息")
    
    # 告警数据
    alert_data = Column(JSON, default={}, comment="告警相关数据")
    trigger_conditions = Column(JSON, default={}, comment="触发条件")
    
    # 处理信息
    resolved = Column(Boolean, default=False, index=True, comment="是否已解决")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="解决时间")
    resolved_by = Column(String(50), nullable=True, comment="解决人")
    resolution_notes = Column(Text, comment="解决说明")
    
    # 关系
    agent = relationship("AgentModel", back_populates="alerts")
    
    def __repr__(self):
        return f"<AgentAlert(id={self.id}, agent_id={self.agent_id}, type='{self.alert_type}', severity='{self.severity}')>"


class AgentMetric(BaseModel):
    """智能体指标数据"""
    __tablename__ = "agent_metrics"
    
    # 关联信息
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True, comment="智能体ID")
    
    # 指标信息
    metric_type = Column(String(50), nullable=False, index=True, comment="指标类型")
    metric_name = Column(String(100), nullable=False, index=True, comment="指标名称")
    metric_value = Column(Float, nullable=False, comment="指标值")
    
    # 时间窗口
    time_window = Column(Integer, default=0, comment="时间窗口(秒)")
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="指标时间戳")
    
    # 标签
    tags = Column(JSON, default={}, comment="指标标签")
    
    # 关系
    agent = relationship("AgentModel", back_populates="metrics")
    
    def __repr__(self):
        return f"<AgentMetric(id={self.id}, agent_id={self.agent_id}, name='{self.metric_name}', value={self.metric_value})>"


class AgentChain(BaseModel):
    """智能体链配置"""
    __tablename__ = "agent_chains"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True, comment="链名称")
    description = Column(Text, nullable=True, comment="链描述")
    chain_type = Column(String(50), nullable=False, index=True, comment="链类型")
    
    # 配置信息
    chain_config = Column(JSON, nullable=False, comment="链配置")
    input_schema = Column(JSON, default={}, comment="输入模式")
    output_schema = Column(JSON, default={}, comment="输出模式")
    
    # 执行配置
    timeout = Column(Integer, default=300, comment="超时时间(秒)")
    max_retries = Column(Integer, default=3, comment="最大重试次数")
    
    # 状态信息
    enabled = Column(Boolean, default=True, index=True, comment="是否启用")
    version = Column(String(20), default="1.0.0", comment="版本号")
    
    def __repr__(self):
        return f"<AgentChain(id={self.id}, name='{self.name}', type='{self.chain_type}')>"


class AgentTool(BaseModel):
    """智能体工具配置"""
    __tablename__ = "agent_tools"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True, comment="工具名称")
    display_name = Column(String(200), nullable=True, comment="显示名称")
    description = Column(Text, nullable=False, comment="工具描述")
    tool_type = Column(String(50), nullable=False, index=True, comment="工具类型")
    
    # 配置信息
    tool_config = Column(JSON, nullable=False, comment="工具配置")
    input_schema = Column(JSON, default={}, comment="输入模式")
    output_schema = Column(JSON, default={}, comment="输出模式")
    
    # 执行配置
    timeout = Column(Integer, default=30, comment="超时时间(秒)")
    requires_auth = Column(Boolean, default=False, comment="是否需要认证")
    
    # 状态信息
    enabled = Column(Boolean, default=True, index=True, comment="是否启用")
    version = Column(String(20), default="1.0.0", comment="版本号")
    
    def __repr__(self):
        return f"<AgentTool(id={self.id}, name='{self.name}', type='{self.tool_type}')>"


class AgentWorkflow(BaseModel):
    """智能体工作流配置"""
    __tablename__ = "agent_workflows"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True, comment="工作流名称")
    description = Column(Text, nullable=True, comment="工作流描述")
    workflow_type = Column(String(50), nullable=False, index=True, comment="工作流类型")
    
    # 配置信息
    workflow_config = Column(JSON, nullable=False, comment="工作流配置")
    nodes = Column(JSON, nullable=False, comment="节点配置")
    edges = Column(JSON, nullable=False, comment="边配置")
    
    # 执行配置
    timeout = Column(Integer, default=1800, comment="超时时间(秒)")
    max_concurrent = Column(Integer, default=5, comment="最大并发数")
    
    # 状态信息
    enabled = Column(Boolean, default=True, index=True, comment="是否启用")
    version = Column(String(20), default="1.0.0", comment="版本号")
    
    def __repr__(self):
        return f"<AgentWorkflow(id={self.id}, name='{self.name}', type='{self.workflow_type}')>"


class AgentTemplate(BaseModel, SoftDeleteMixin):
    """智能体模板"""
    __tablename__ = "agent_templates"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    template_type = Column(String(50), nullable=False, index=True, comment="模板类型")
    
    # 模板配置
    template_config = Column(JSON, nullable=False, comment="模板配置")
    agent_config = Column(JSON, nullable=False, comment="智能体配置")
    chain_config = Column(JSON, default={}, comment="链配置")
    tool_config = Column(JSON, default={}, comment="工具配置")
    
    # 元数据
    tags = Column(JSON, default=[], comment="标签")
    category = Column(String(50), nullable=True, index=True, comment="分类")
    difficulty = Column(String(20), default="medium", comment="难度级别")
    
    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    success_rate = Column(Float, default=0.0, comment="成功率")
    avg_execution_time = Column(Float, default=0.0, comment="平均执行时间")
    
    # 状态信息
    published = Column(Boolean, default=False, index=True, comment="是否发布")
    version = Column(String(20), default="1.0.0", comment="版本号")
    
    def __repr__(self):
        return f"<AgentTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"


class LangChainRun(BaseModel):
    """LangChain运行记录"""
    __tablename__ = "langchain_runs"
    
    # 运行信息
    run_id = Column(String(100), nullable=False, unique=True, index=True, comment="运行ID")
    session_id = Column(String(100), nullable=True, index=True, comment="会话ID")
    
    # 关联信息
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True, comment="智能体ID")
    chain_id = Column(Integer, ForeignKey("agent_chains.id"), nullable=True, index=True, comment="链ID")
    
    # 运行配置
    run_type = Column(String(50), nullable=False, index=True, comment="运行类型")
    run_config = Column(JSON, default={}, comment="运行配置")
    
    # 输入输出
    input_data = Column(JSON, default={}, comment="输入数据")
    output_data = Column(JSON, default={}, comment="输出数据")
    intermediate_steps = Column(JSON, default={}, comment="中间步骤")
    
    # 执行结果
    success = Column(Boolean, default=True, index=True, comment="是否成功")
    execution_time = Column(Float, comment="执行时间(秒)")
    error_message = Column(Text, comment="错误信息")
    
    # 资源使用
    token_usage = Column(JSON, default={}, comment="令牌使用情况")
    cost_estimation = Column(Float, default=0.0, comment="成本估算")
    
    # 时间戳
    started_at = Column(DateTime(timezone=True), nullable=False, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    
    def __repr__(self):
        return f"<LangChainRun(id={self.id}, run_id='{self.run_id}', type='{self.run_type}', success={self.success})>"


# 智能体类型常量
class AgentTypes:
    """智能体类型常量"""
    BUSINESS = "business"  # 业务智能体
    OPERATIONAL = "operational"  # 运维智能体
    DATA_PROCESSING = "data_processing"  # 数据处理智能体
    USER_SERVICE = "user_service"  # 用户服务智能体


# 智能体状态常量
class AgentStatuses:
    """智能体状态常量"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    PAUSED = "paused"


# 告警严重程度常量
class AlertSeverities:
    """告警严重程度常量"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# 指标类型常量
class MetricTypes:
    """指标类型常量"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    BUSINESS = "business"
    QUALITY = "quality"