from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database_async import get_async_db
from pydantic import BaseModel

router = APIRouter(prefix="/permissions", tags=["permissions"])

# Pydantic模型定义
class Permission(BaseModel):
    id: int
    name: str
    code: str
    description: str
    parentId: Optional[int] = None
    children: List['Permission'] = []

    class Config:
        from_attributes = True

# 完整权限数据树（根据文档规划）
PERMISSIONS_DATA = [
    # 用户系统管理 (模块001)
    {"id": 101, "name": "用户系统管理", "code": "admin:user", "description": "用户管理系统", "parentId": None},
    {"id": 102, "name": "查看用户列表", "code": "admin:user:view", "description": "查看用户列表", "parentId": 101},
    {"id": 103, "name": "新建用户", "code": "admin:user:create", "description": "新建用户", "parentId": 101},
    {"id": 104, "name": "编辑用户信息", "code": "admin:user:edit", "description": "编辑用户信息", "parentId": 101},
    {"id": 105, "name": "删除用户账号", "code": "admin:user:delete", "description": "删除用户账号", "parentId": 101},
    {"id": 106, "name": "重置用户密码", "code": "admin:user:reset_pwd", "description": "重置用户密码", "parentId": 101},
    {"id": 107, "name": "锁定/解锁用户", "code": "admin:user:lock", "description": "锁定或解锁用户账户", "parentId": 101},
    
    # 角色权限管理 (模块002)
    {"id": 201, "name": "角色权限管理", "code": "admin:role", "description": "角色和权限管理", "parentId": None},
    {"id": 202, "name": "查看角色列表", "code": "admin:role:view", "description": "查看角色列表", "parentId": 201},
    {"id": 203, "name": "编辑角色权限", "code": "admin:role:edit", "description": "编辑角色权限", "parentId": 201},
    {"id": 204, "name": "创建新角色", "code": "admin:role:create", "description": "创建新角色", "parentId": 201},
    {"id": 205, "name": "删除自定义角色", "code": "admin:role:delete", "description": "删除自定义角色", "parentId": 201},
    
    # 部门管理 (模块003)
    {"id": 301, "name": "部门管理", "code": "admin:department", "description": "部门管理", "parentId": None},
    {"id": 302, "name": "查看部门结构", "code": "admin:department:view", "description": "查看部门结构", "parentId": 301},
    {"id": 303, "name": "编辑部门信息", "code": "admin:department:edit", "description": "编辑部门信息", "parentId": 301},
    {"id": 304, "name": "部门组织变更", "code": "admin:department:manage", "description": "部门组织变更", "parentId": 301},
    
    # 数据源管理系统 (模块004)
    {"id": 401, "name": "数据源管理", "code": "datasource", "description": "数据源管理系统", "parentId": None},
    {"id": 402, "name": "查看数据源列表", "code": "datasource:view", "description": "查看数据源列表", "parentId": 401},
    {"id": 403, "name": "创建数据源", "code": "datasource:create", "description": "创建数据源", "parentId": 401},
    {"id": 404, "name": "编辑数据源配置", "code": "datasource:edit", "description": "编辑数据源配置", "parentId": 401},
    {"id": 405, "name": "删除数据源", "code": "datasource:delete", "description": "删除数据源", "parentId": 401},
    
    # 爬虫任务管理 (模块005)
    {"id": 501, "name": "爬虫任务管理", "code": "task", "description": "爬虫任务管理", "parentId": None},
    {"id": 502, "name": "查看爬虫任务", "code": "task:view", "description": "查看爬虫任务", "parentId": 501},
    {"id": 503, "name": "创建新任务", "code": "task:create", "description": "创建新任务", "parentId": 501},
    {"id": 504, "name": "执行任务", "code": "task:execute", "description": "执行任务（启动/停止）", "parentId": 501},
    {"id": 505, "name": "查看任务执行日志", "code": "task:logs", "description": "查看任务执行日志", "parentId": 501},
    
    # 爬虫监控 (模块006)
    {"id": 601, "name": "爬虫监控", "code": "monitor", "description": "爬虫监控系统", "parentId": None},
    {"id": 602, "name": "查看爬虫监控", "code": "monitor:crawler", "description": "查看爬虫监控信息", "parentId": 601},
    {"id": 603, "name": "查看系统健康数据", "code": "monitor:health", "description": "查看系统健康数据", "parentId": 601},
    
    # 数据中心 (模块007)
    {"id": 701, "name": "数据中心", "code": "data", "description": "数据中心", "parentId": None},
    {"id": 702, "name": "数据查询权限", "code": "data:query", "description": "数据查询", "parentId": 701},
    {"id": 703, "name": "导出数据", "code": "data:export", "description": "导出数据", "parentId": 701},
    {"id": 704, "name": "编辑数据记录", "code": "data:edit", "description": "编辑数据记录", "parentId": 701},
    {"id": 705, "name": "删除数据记录", "code": "data:delete", "description": "删除数据记录", "parentId": 701},
    {"id": 706, "name": "查看比赛数据", "code": "match:view", "description": "查看比赛数据", "parentId": 701},
    {"id": 707, "name": "导入比赛数据", "code": "match:import", "description": "导入比赛数据", "parentId": 701},
    
    # IP池和请求头管理 (模块008)
    {"id": 801, "name": "IP池和请求头", "code": "pool_headers", "description": "IP池和请求头管理", "parentId": None},
    {"id": 802, "name": "查看IP池", "code": "ippool:view", "description": "查看IP池", "parentId": 801},
    {"id": 803, "name": "编辑IP池配置", "code": "ippool:edit", "description": "编辑IP池配置", "parentId": 801},
    {"id": 804, "name": "查看请求头模板", "code": "headers:view", "description": "查看请求头模板", "parentId": 801},
    {"id": 805, "name": "编辑请求头配置", "code": "headers:edit", "description": "编辑请求头配置", "parentId": 801},
    
    # 分析工具 (模块009)
    {"id": 901, "name": "分析工具", "code": "analysis", "description": "分析工具", "parentId": None},
    {"id": 902, "name": "北单三维筛选器", "code": "analysis:beidan", "description": "北单三维筛选器", "parentId": 901},
    {"id": 903, "name": "平局预测分析", "code": "analysis:draw", "description": "平局预测分析", "parentId": 901},
    {"id": 904, "name": "套利分析工具", "code": "analysis:hedging", "description": "套利分析工具", "parentId": 901},
    
    # 系统配置与审计 (模块010)
    {"id": 1001, "name": "系统配置与审计", "code": "system", "description": "系统配置与审计", "parentId": None},
    {"id": 1002, "name": "系统基础配置", "code": "system:config", "description": "系统基础配置", "parentId": 1001},
    {"id": 1003, "name": "数据备份操作", "code": "system:backup", "description": "数据备份操作", "parentId": 1001},
    {"id": 1004, "name": "数据恢复操作", "code": "system:restore", "description": "数据恢复操作", "parentId": 1001},
    {"id": 1005, "name": "查看系统日志", "code": "log:view", "description": "查看系统日志", "parentId": 1001},
    {"id": 1006, "name": "导出日志数据", "code": "log:export", "description": "导出日志数据", "parentId": 1001},
    {"id": 1007, "name": "查看审计报表", "code": "audit:view", "description": "查看审计报表", "parentId": 1001},
    {"id": 1008, "name": "双因素认证管理", "code": "security:2fa", "description": "双因素认证管理", "parentId": 1001},
    {"id": 1009, "name": "IP白名单管理", "code": "security:ip_whitelist", "description": "IP白名单管理", "parentId": 1001},
]

def build_permission_tree(permissions=None):
    """构建权限树形结构"""
    if permissions is None:
        permissions = PERMISSIONS_DATA
    
    permission_map = {perm["id"]: Permission(
        id=perm["id"],
        name=perm["name"],
        code=perm["code"],
        description=perm["description"],
        parentId=perm["parentId"],
        children=[]
    ) for perm in permissions}
    
    root_permissions = []
    for perm_data in permissions:
        perm = permission_map[perm_data["id"]]
        if perm_data["parentId"] is None:
            root_permissions.append(perm)
        else:
            parent = permission_map.get(perm_data["parentId"])
            if parent:
                parent.children.append(perm)
    
    return root_permissions

@router.get("/", response_model=List[Permission])
async def get_permissions():
    """
    获取权限列表
    """
    return build_permission_tree()

@router.get("/tree", response_model=List[Permission])
async def get_permission_tree():
    """
    获取权限树形结构
    """
    return build_permission_tree()

@router.get("/flat", response_model=List[dict])
async def get_permissions_flat():
    """
    获取权限扁平列表
    """
    return PERMISSIONS_DATA
