"""
智能体API数据模式定义
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """智能体基础模式"""
    name: str = Field(..., description="智能体名称", max_length=100)
    display_name: Optional[str] = Field(None, description="显示名称", max_length=200)
    description: Optional[str] = Field(None, description="智能体描述")
    agent_type: str = Field(..., description="智能体类型")
    
    # 配置信息
    config: Dict[str, Any] = Field(default_factory=dict, description="智能体配置")
    langchain_config: Dict[str, Any] = Field(default_factory=dict, description="LangChain配置")
    
    # 执行配置
    max_concurrent: int = Field(default=1, description="最大并发数", ge=1)
    timeout: int = Field(default=300, description="执行超时时间(秒)", ge=1)
    retry_count: int = Field(default=3, description="重试次数", ge=0)
    
    # 调度配置
    schedule_enabled: bool = Field(default=False, description="是否启用调度")
    schedule_config: Dict[str, Any] = Field(default_factory=dict, description="调度配置")
    
    # 监控配置
    health_check_interval: int = Field(default=60, description="健康检查间隔(秒)", ge=0)
    
    # 状态信息
    enabled: bool = Field(default=True, description="是否启用")


class AgentCreate(AgentBase):
    """创建智能体模式"""
    pass


class AgentUpdate(BaseModel):
    """更新智能体模式"""
    name: Optional[str] = Field(None, description="智能体名称", max_length=100)
    display_name: Optional[str] = Field(None, description="显示名称", max_length=200)
    description: Optional[str] = Field(None, description="智能体描述")
    config: Optional[Dict[str, Any]] = Field(None, description="智能体配置")
    langchain_config: Optional[Dict[str, Any]] = Field(None, description="LangChain配置")
    max_concurrent: Optional[int] = Field(None, description="最大并发数", ge=1)
    timeout: Optional[int] = Field(None, description="执行超时时间(秒)", ge=1)
    retry_count: Optional[int] = Field(None, description="重试次数", ge=0)
    schedule_enabled: Optional[bool] = Field(None, description="是否启用调度")
    schedule_config: Optional[Dict[str, Any]] = Field(None, description="调度配置")
    health_check_interval: Optional[int] = Field(None, description="健康检查间隔(秒)", ge=0)
    enabled: Optional[bool] = Field(None, description="是否启用")


class AgentResponse(AgentBase):
    """智能体响应模式"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentControlRequest(BaseModel):
    """智能体控制请求模式"""
    action: str = Field(..., description="控制动作: start, stop, restart, pause, resume")
    force: bool = Field(default=False, description="是否强制操作")


class AgentTaskRequest(BaseModel):
    """智能体任务请求模式"""
    task_type: str = Field(..., description="任务类型")
    task_data: Dict[str, Any] = Field(default_factory=dict, description="任务数据")
    priority: int = Field(default=1, description="优先级", ge=1, le=10)
    timeout: Optional[int] = Field(None, description="任务超时时间(秒)")


class AgentTaskResponse(BaseModel):
    """智能体任务响应模式"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    agent_id: int
    task_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class AgentMetricsResponse(BaseModel):
    """智能体指标响应模式"""
    agent_id: int
    executions: int
    errors: int
    avg_response_time: float
    success_rate: float
    last_execution: Optional[datetime]
    active_tasks: int
    
    # 时间窗口指标
    executions_1h: int = 0
    executions_24h: int = 0
    avg_response_time_1h: float = 0.0
    success_rate_1h: float = 0.0


class AgentExecutionLogResponse(BaseModel):
    """智能体执行日志响应模式"""
    id: int
    agent_id: int
    task_type: Optional[str]
    success: bool
    execution_time: Optional[float]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AgentAlertResponse(BaseModel):
    """智能体告警响应模式"""
    id: int
    agent_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """智能体列表响应模式"""
    agents: List[AgentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AgentBulkControlRequest(BaseModel):
    """批量控制智能体请求模式"""
    agent_ids: List[int] = Field(..., description="智能体ID列表")
    action: str = Field(..., description="控制动作: start, stop, restart")
    force: bool = Field(default=False, description="是否强制操作")


class AgentBulkControlResponse(BaseModel):
    """批量控制智能体响应模式"""
    success: List[int] = Field(default_factory=list, description="成功操作的智能体ID")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="失败操作的智能体信息")
    message: str


class AgentBulkUpdateRequest(BaseModel):
    """批量更新智能体请求模式"""
    agent_ids: List[int] = Field(..., description="智能体ID列表")
    update_data: AgentUpdate = Field(..., description="更新数据")
    force: bool = Field(default=False, description="是否强制更新")


class AgentBulkUpdateResponse(BaseModel):
    """批量更新智能体响应模式"""
    success: List[int] = Field(default_factory=list, description="成功更新的智能体ID")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="失败更新的智能体信息")
    message: str


class AgentBulkDeleteRequest(BaseModel):
    """批量删除智能体请求模式"""
    agent_ids: List[int] = Field(..., description="智能体ID列表")
    force: bool = Field(default=False, description="是否强制删除")


class AgentBulkDeleteResponse(BaseModel):
    """批量删除智能体响应模式"""
    success: List[int] = Field(default_factory=list, description="成功删除的智能体ID")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="失败删除的智能体信息")
    message: str


class AgentBulkExportRequest(BaseModel):
    """批量导出智能体请求模式"""
    agent_ids: List[int] = Field(..., description="智能体ID列表")
    export_format: str = Field(default="json", description="导出格式")
    include_config: bool = Field(default=True, description="是否包含配置")
    include_logs: bool = Field(default=False, description="是否包含日志")


class AgentBulkExportResponse(BaseModel):
    """批量导出智能体响应模式"""
    export_id: str = Field(..., description="导出ID")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小(字节)")
    download_url: str = Field(..., description="下载URL")


class AgentBulkImportRequest(BaseModel):
    """批量导入智能体请求模式"""
    import_data: Dict[str, Any] = Field(..., description="导入数据")
    conflict_resolution: str = Field(default="skip", description="冲突解决策略: skip, overwrite, rename")
    dry_run: bool = Field(default=False, description="是否试运行")


class AgentBulkImportResponse(BaseModel):
    """批量导入智能体响应模式"""
    imported: List[int] = Field(default_factory=list, description="成功导入的智能体ID")
    skipped: List[Dict[str, Any]] = Field(default_factory=list, description="跳过的智能体信息")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="导入失败的智能体信息")
    message: str


# LangChain相关模式
class LangChainRunRequest(BaseModel):
    """LangChain运行请求模式"""
    chain_name: str = Field(..., description="链名称")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    run_config: Dict[str, Any] = Field(default_factory=dict, description="运行配置")


class LangChainRunResponse(BaseModel):
    """LangChain运行响应模式"""
    run_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    execution_time: float
    error_message: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None
    cost_estimation: Optional[float] = None
    intermediate_steps: Optional[List[Dict[str, Any]]] = None


class LangChainStatsResponse(BaseModel):
    """LangChain统计响应模式"""
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_execution_time: float
    total_tokens: int
    total_cost: float
    runs_last_hour: int
    runs_last_24h: int


# 智能体类型和状态常量
class AgentTypes:
    """智能体类型常量"""
    BUSINESS = "business"
    OPERATIONAL = "operational" 
    DATA_PROCESSING = "data_processing"
    USER_SERVICE = "user_service"


class AgentStatuses:
    """智能体状态常量"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    PAUSED = "paused"


class AgentActions:
    """智能体动作常量"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    PAUSE = "pause"
    RESUME = "resume"


# 智能体模板相关模式
class AgentTemplateBase(BaseModel):
    """智能体模板基础模式"""
    name: str = Field(..., description="模板名称", max_length=100)
    description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., description="模板类型")
    
    # 模板配置
    template_config: Dict[str, Any] = Field(default_factory=dict, description="模板配置")
    agent_config: Dict[str, Any] = Field(default_factory=dict, description="智能体配置")
    chain_config: Dict[str, Any] = Field(default_factory=dict, description="链配置")
    tool_config: Dict[str, Any] = Field(default_factory=dict, description="工具配置")
    
    # 元数据
    tags: List[str] = Field(default_factory=list, description="标签")
    category: Optional[str] = Field(None, description="分类")
    difficulty: str = Field(default="medium", description="难度级别")
    
    # 状态信息
    published: bool = Field(default=False, description="是否发布")


class AgentTemplateCreate(AgentTemplateBase):
    """创建智能体模板模式"""
    pass


class AgentTemplateUpdate(BaseModel):
    """更新智能体模板模式"""
    name: Optional[str] = Field(None, description="模板名称", max_length=100)
    description: Optional[str] = Field(None, description="模板描述")
    template_config: Optional[Dict[str, Any]] = Field(None, description="模板配置")
    agent_config: Optional[Dict[str, Any]] = Field(None, description="智能体配置")
    chain_config: Optional[Dict[str, Any]] = Field(None, description="链配置")
    tool_config: Optional[Dict[str, Any]] = Field(None, description="工具配置")
    tags: Optional[List[str]] = Field(None, description="标签")
    category: Optional[str] = Field(None, description="分类")
    difficulty: Optional[str] = Field(None, description="难度级别")
    published: Optional[bool] = Field(None, description="是否发布")


class AgentTemplateResponse(AgentTemplateBase):
    """智能体模板响应模式"""
    id: int
    usage_count: int
    success_rate: float
    avg_execution_time: float
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AgentTemplateListResponse(BaseModel):
    """智能体模板列表响应模式"""
    templates: List[AgentTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AgentTemplateBulkCreateRequest(BaseModel):
    """批量创建智能体模板请求模式"""
    templates: List[AgentTemplateCreate] = Field(..., description="模板列表")


class AgentTemplateBulkCreateResponse(BaseModel):
    """批量创建智能体模板响应模式"""
    success: List[int] = Field(default_factory=list, description="成功创建的模板ID")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="创建失败的模板信息")
    message: str


class AgentTemplateImportRequest(BaseModel):
    """导入智能体模板请求模式"""
    import_data: Dict[str, Any] = Field(..., description="导入数据")
    conflict_resolution: str = Field(default="skip", description="冲突解决策略: skip, overwrite, rename")


class AgentTemplateImportResponse(BaseModel):
    """导入智能体模板响应模式"""
    imported: List[int] = Field(default_factory=list, description="成功导入的模板ID")
    skipped: List[Dict[str, Any]] = Field(default_factory=list, description="跳过的模板信息")
    failed: List[Dict[str, Any]] = Field(default_factory=list, description="导入失败的模板信息")
    message: str