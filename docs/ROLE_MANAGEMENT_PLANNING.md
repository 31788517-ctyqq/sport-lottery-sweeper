# 角色管理系统规划方案

**更新时间**: 2026年3月2日  
**适用对象**: 运营管理团队、系统管理员  
**文档状态**: 完整规划方案  

## 概述

本文档为后台管理系统的角色和权限管理体系提供完整规划建议。基于当前系统架构（采用枚举角色+权限树的混合模式），本方案既保留现有设计的简洁性，又为后续细粒度权限控制预留扩展空间。

---

## 一、角色体系设计（5层推荐）

### 角色定义与职责

| 角色 | 权限等级 | 定位 | 主要职责 |
|------|:--------:|------|--------|
| **超级管理员** | L5 | 系统所有者 | 系统配置、权限管理、审计监督、重大决策 |
| **管理员** | L4 | 部门带头人 | 数据源管理、任务分配、部门协调、报表审批 |
| **审计员** | L3 | 合规监督者 | 查看操作日志、生成审计报表、问题转办 |
| **运营员** | L2 | 日常执行者 | 数据维护、爬虫任务执行、内容审核、数据录入 |
| **观察者** | L1 | 只读用户 | 查看报表、查看数据、制度学习（**无任何修改权限**） |

### 角色层级说明

- **权限继承原则**：上级角色权限子集 ⊇ 下级角色权限子集
- **系统角色**：超级管理员和管理员为系统内置角色，不可删除
- **自定义角色**：可在管理员以上权限下创建自定义角色
- **变更记录**：角色变更需在操作日志中详细记录

---

## 二、权限架构（模块化设计）

### 2.1 权限分类体系

权限按模块划分，每个模块包含不同粒度的操作权限。

```
系统权限总览（权限树结构）
├─ 用户系统管理
│  ├─ admin:user:view           查看用户列表
│  ├─ admin:user:create         新建用户
│  ├─ admin:user:edit           编辑用户信息
│  ├─ admin:user:delete         删除用户账号
│  ├─ admin:user:reset_pwd      重置用户密码
│  ├─ admin:user:lock           锁定/解锁用户
│  ├─ admin:role:view           查看角色列表
│  ├─ admin:role:edit           编辑角色权限
│  ├─ admin:role:create         创建新角色
│  ├─ admin:role:delete         删除自定义角色
│  ├─ admin:department:view     查看部门结构
│  ├─ admin:department:edit     编辑部门信息
│  └─ admin:department:manage   部门组织变更
│
├─ 数据源管理系统
│  ├─ datasource:view           查看数据源列表
│  ├─ datasource:create         创建数据源
│  ├─ datasource:edit           编辑数据源配置
│  ├─ datasource:delete         删除数据源
│  ├─ task:view                 查看爬虫任务
│  ├─ task:create               创建新任务
│  ├─ task:execute              执行任务（启动/停止）
│  ├─ task:logs                 查看任务执行日志
│  ├─ monitor:crawler           查看爬虫监控
│  ├─ monitor:health            查看系统健康数据
│  ├─ ippool:view               查看IP池
│  ├─ ippool:edit               编辑IP池配置
│  ├─ headers:view              查看请求头模板
│  └─ headers:edit              编辑请求头配置
│
├─ 数据中心
│  ├─ data:query                数据查询权限
│  ├─ data:export               导出数据
│  ├─ data:edit                 编辑数据记录
│  ├─ data:delete               删除数据记录
│  ├─ match:view                查看比赛数据
│  ├─ match:import              导入比赛数据
│  ├─ odds:view                 查看赔率数据
│  └─ lottery:view              查看彩票数据
│
├─ 分析工具
│  ├─ analysis:beidan           北单三维筛选器
│  ├─ analysis:draw             平局预测分析
│  ├─ analysis:hedging          套利分析工具
│  └─ analysis:multi_strategy   多策略分析
│
└─ 系统配置与审计
   ├─ system:config             系统基础配置
   ├─ system:backup             数据备份操作
   ├─ system:restore            数据恢复操作
   ├─ log:view                  查看系统日志
   ├─ log:export                导出日志数据
   ├─ audit:view                查看审计报表
   ├─ security:2fa              双因素认证管理
   └─ security:ip_whitelist     IP白名单管理
```

### 2.2 权限粒度说明

每个权限点通常需要支持以下操作：

| 操作 | 说明 | 示例 |
|------|------|------|
| **view** | 查看/列表 | `datasource:view` - 查看所有数据源 |
| **create** | 新建 | `datasource:create` - 创建新数据源 |
| **edit** | 修改 | `datasource:edit` - 修改配置 |
| **delete** | 删除 | `datasource:delete` - 删除记录 |
| **execute** | 执行 | `task:execute` - 运行任务 |
| **export** | 导出 | `data:export` - 导出数据 |
| **approve** | 审批 | 需要审批的操作 |

---

## 三、角色权限授权矩阵

### 3.1 标准授权方案

| 权限点 | 超级管理员 | 管理员 | 审计员 | 运营员 | 观察者 |
|--------|:--------:|:-----:|:-----:|:-----:|:-----:|
| **用户系统** |
| admin:user:view | ✓ | ✓ | ✓ | ✗ | ✗ |
| admin:user:create | ✓ | ✓ | ✗ | ✗ | ✗ |
| admin:user:edit | ✓ | ✓ | ✗ | ✗ | ✗ |
| admin:user:delete | ✓ | ✗ | ✗ | ✗ | ✗ |
| admin:user:reset_pwd | ✓ | ✓ | ✗ | ✗ | ✗ |
| admin:user:lock | ✓ | ✓ | ✗ | ✗ | ✗ |
| **角色权限** |
| admin:role:view | ✓ | ✓ | ✓ | ✗ | ✗ |
| admin:role:edit | ✓ | ✗ | ✗ | ✗ | ✗ |
| admin:role:create | ✓ | ✗ | ✗ | ✗ | ✗ |
| admin:role:delete | ✓ | ✗ | ✗ | ✗ | ✗ |
| **部门管理** |
| admin:department:view | ✓ | ✓ | ✓ | ✓ | ✗ |
| admin:department:edit | ✓ | ✓ | ✗ | ✗ | ✗ |
| **数据源管理** |
| datasource:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| datasource:create | ✓ | ✓ | ✗ | ✓ | ✗ |
| datasource:edit | ✓ | ✓ | ✗ | ✓ | ✗ |
| datasource:delete | ✓ | ✓ | ✗ | ✗ | ✗ |
| **任务管理** |
| task:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| task:create | ✓ | ✓ | ✗ | ✓ | ✗ |
| task:execute | ✓ | ✓ | ✗ | ✓ | ✗ |
| task:logs | ✓ | ✓ | ✓ | ✓ | ✓ |
| **监控系统** |
| monitor:crawler | ✓ | ✓ | ✓ | ✓ | ✓ |
| monitor:health | ✓ | ✓ | ✓ | ✗ | ✗ |
| **数据管理** |
| data:query | ✓ | ✓ | ✓ | ✓ | ✓ |
| data:export | ✓ | ✓ | ✓ | ✓ | ✗ |
| data:edit | ✓ | ✓ | ✗ | ✓ | ✗ |
| **IP池/请求头** |
| ippool:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| ippool:edit | ✓ | ✓ | ✗ | ✓ | ✗ |
| headers:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| headers:edit | ✓ | ✓ | ✗ | ✓ | ✗ |
| **日志与审计** |
| log:view | ✓ | ✓ | ✓✓ | ✗ | ✗ |
| log:export | ✓ | ✓ | ✓✓ | ✗ | ✗ |
| audit:view | ✓ | ✓ | ✓✓ | ✗ | ✗ |
| **系统配置** |
| system:config | ✓✓ | ✗ | ✗ | ✗ | ✗ |
| system:backup | ✓✓ | ✗ | ✗ | ✗ | ✗ |

**图例说明**：
- ✓ = 有权限
- ✗ = 无权限  
- ✓✓ = 优先权限/重点关注

### 3.2 权限说明

#### 超级管理员 (L5)
- 全系统最高权位，拥有所有权限
- 负责系统安全、权限策略制定
- **数量限制**: 不超过2人，由不同部门负责人担任
- **离职流程**: 需完整交接和权限交割

#### 管理员 (L4)
- 拥有除系统配置外的所有管理权限
- 可创建和编辑用户账号
- 可管理数据源和任务
- 可查看（但不能修改）审计日志
- **部门职责**: 通常由部门经理或技术负责人担任

#### 审计员 (L3)
- 专注于监督和合规
- 可查看所有操作日志和审计报表
- **不能**修改任何数据或配置
- 生成合规审计报告
- **职责**: 由合规/风控部门人员担任

#### 运营员 (L2)
- 日常业务执行权限
- 可创建和执行爬虫任务
- 可对接的数据源执行CRUD操作
- **部门隔离**: 默认只能看到自己部门的数据
- 可导出和分析数据

#### 观察者 (L1)
- **只读权限**，无任何修改、执行、删除权限
- 用于只想了解系统历程的管理层
- 可查看报表、数据、日志
- 可用于审查、监督、知识转移的场景

---

## 四、数据隔离与部门管理

### 4.1 部门维度隔离

由于系统涉及多个部门的协作，需实现以下隔离策略：

#### 隔离级别

**L1 - 视图级隔离**（必实现）
```
运营员只能看到：
- 自己部门的爬虫任务
- 自己部门创建的数据源
- 自己部门的操作日志
```

**L2 - 数据级隔离**（推荐实现）
```
运营员查询时自动过滤：
SELECT * FROM datasources 
WHERE department_id = current_user.department_id
```

**L3 - API网关级隔离**（高安全场景）
```
请求在API网关层面验证，确保跨部门访问被阻止
```

### 4.2 部门管理模型

```
部门表字段建议：
- id: 部门ID
- name: 部门名称
- parent_id: 父部门ID（支持树形结构）
- manager_id: 部门经理（AdminUser外键）
- status: 激活状态
- created_at: 创建时间
- updated_at: 更新时间
- remarks: 备注

用户表关联：
- AdminUser.department_id -> Department.id
- 确保用户属于某个部门
```

### 4.3 跨部门权限

某些权限需要跨部门访问，建议如下：

```javascript
// 权限检查示例
if (requiredPermission === 'datasource:edit') {
  // 检查1: 用户是否有权限
  if (!userPermissions.includes('datasource:edit')) return Forbidden;
  
  // 检查2: 数据所有者验证
  if (resource.department_id !== userDepartmentId && !isAdmin()) {
    return Forbidden;
  }
  
  return Allowed;
}
```

---

## 五、权限应用场景与实现

### 5.1 前端权限控制

#### 菜单隐藏
```javascript
// 根据权限显示菜单项
const menuItems = [
  {
    label: '用户管理',
    path: '/admin/users',
    requirePermission: ['admin:user:view'],
    children: [
      {
        label: '用户列表',
        path: '/admin/users/list',
        requirePermission: ['admin:user:view']
      },
      {
        label: '角色与权限',
        path: '/admin/users/roles',
        requirePermission: ['admin:role:view']
      }
    ]
  }
];
```

#### 按钮权限
```vue
<template>
  <!-- 编辑按钮：只有管理员以上才能看 -->
  <el-button 
    v-if="hasPermission('datasource:edit')"
    @click="handleEdit"
  >
    编辑数据源
  </el-button>

  <!-- 删除按钮：只有超级管理员 -->
  <el-button 
    v-if="hasPermission('datasource:delete')"
    type="danger"
    @click="handleDelete"
  >
    删除
  </el-button>
</template>

<script setup>
function hasPermission(permissionCode) {
  return currentUser.permissions.includes(permissionCode);
}
</script>
```

### 5.2 后端权限验证

#### 权限装饰器
```python
# FastAPI路由权限验证
from functools import wraps
from fastapi import HTTPException

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if permission not in current_user.permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足: 需要 {permission}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.delete("/datasources/{id}")
@require_permission("datasource:delete")
async def delete_datasource(id: int, current_user: AdminUser):
    # 删除逻辑
    pass
```

#### 行级权限检查
```python
@router.get("/tasks/{task_id}")
async def get_task(task_id: int, current_user: AdminUser):
    task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
    
    # 检查：非管理员只能看自己部门的任务
    if not is_admin(current_user):
        if task.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="无权限访问该任务")
    
    return task
```

---

## 六、特殊权限场景处理

### 6.1 高危操作双人认证

需要双人签名的操作：

| 操作 | 触发人员 | 审批人员 | 操作日志 |
|------|---------|--------|--------|
| 删除用户账号 | 管理员+ | 超级管理员 | 详细记录 |
| 删除大量数据源 | 管理员+ | 超级管理员 | 详细记录 |
| 导出敏感数据 | 审计员+ | 合规负责人 | 详细记录+报警 |
| 系统配置变更 | 超级管理员 | 另一超级管理员 | 详细记录 |
| 数据备份恢复 | 超级管理员 | 另一超级管理员 | 详细记录 |

### 6.2 临时权限提升

**场景**: 周末加班需临时提权

```javascript
// 临时权限记录表
interface TemporaryPermission {
  id: number;
  user_id: number;
  role_id: number;               // 临时提升到的角色
  reason: string;                // 申请原因
  approved_by: number;           // 批准人
  valid_from: datetime;          // 开始时间
  valid_until: datetime;         // 结束时间
  status: 'pending' | 'approved' | 'expired' | 'revoked';
  created_at: datetime;
}
```

### 6.3 特殊权限场景

**超期密码提醒**
```python
# 登录时检查密码是否超期
if user.password_expires_at and user.password_expires_at < datetime.now():
    return {
        'success': False,
        'error': 'PASSWORD_EXPIRED',
        'message': '密码已超期，需要重置'
    }
```

**首次登录强制修改密码**
```python
if user.must_change_password:
    return {
        'success': False,
        'error': 'MUST_CHANGE_PASSWORD',
        'redirect': '/admin/users/profile?action=change_password'
    }
```

---

## 七、审计与日志记录

### 7.1 必审计的操作

```python
# 需要记录的关键操作
AUDITABLE_OPERATIONS = {
    'user_create': '创建用户',
    'user_update': '修改用户信息',
    'user_delete': '删除用户',
    'user_role_change': '变更用户角色',
    'user_lock': '锁定用户',
    'user_unlock': '解锁用户',
    'role_create': '创建角色',
    'role_update': '修改角色权限',
    'role_delete': '删除角色',
    'datasource_create': '创建数据源',
    'datasource_delete': '删除数据源',
    'task_execute': '执行任务',
    'data_export': '导出数据',
    'system_config_change': '修改系统配置',
    'backup_restore': '数据备份/恢复',
    'permission_change': '权限变更',
}
```

### 7.2 审计日志记录字段

```python
class AuditLog(Base):
    id: int
    operator_id: int              # 操作人ID
    operator_name: str            # 操作人名称
    operator_department: str      # 操作人部门
    operation_type: str           # 操作类型 (user_create, etc.)
    operation_name: str           # 操作中文名称
    resource_type: str            # 资源类型 (user, role, datasource, etc.)
    resource_id: int              # 资源ID
    resource_name: str            # 资源名称
    changes: dict | JSON          # 变更前后的值
    status: str                   # 成功/失败
    error_message: str | null     # 失败原因
    ip_address: str               # 操作IP
    user_agent: str               # 浏览器信息
    created_at: datetime          # 操作时间
    remarks: str | null           # 备注
```

### 7.3 异常操作告警规则

```yaml
告警规则:
  - rule: '用户密码连续失败3次'
    action: '锁定账户30分钟'
    
  - rule: '短时间内多个用户被删除'
    action: '发送告警给超级管理员'
    
  - rule: '非工作时间导出大量数据'
    action: '发送告警+记录为可疑操作'
    
  - rule: '跨部门访问他人数据'
    action: '阻止操作+发送告警'
    
  - rule: '权限被异常提升'
    action: '立即通知被提升者+超级管理员确认'
```

---

## 八、权限角色迁移计划

### 第一阶段（第1-2周）：基础梳理

**任务**：
- [ ] 编制现有用户权限矩阵
- [ ] 统计各部门、各岗位人数
- [ ] 制定用户→角色的映射表
- [ ] 编制用户离职清单

**交付物**：
```
当前用户权限状态表格
├─ 工程部 (5人)
│  ├─ 张三 -> 管理员
│  ├─ 李四 -> 运营员
│  └─ ...
├─ 运营部 (8人)
└─ ...
```

### 第二阶段（第3-4周）：权限细化和系统完善

**任务**：
- [ ] 完善功能权限分类（细化权限树）
- [ ] 修改前端菜单/按钮权限控制逻辑
- [ ] 增强后端API权限校验
- [ ] 建立操作日志系统

**代码需求**：
```python
# 1. 在RolePermission.vue中补全权限树数据结构
# 2. 在后端route中添加@require_permission装饰器
# 3. 完善AdminUser.permissions字段的使用
# 4. 创建PermissionChecker或PermissionMiddleware
```

### 第三阶段（第5-6周）：功能测试与部门隔离

**任务**：
- [ ] 权限功能测试
- [ ] 部门数据隔离实现与测试
- [ ] 权限与部门的交叉场景测试
- [ ] 权限告警规则部署

**测试案例**：
```
TC-001: 运营员不能访问其他部门的数据源
TC-002: 超级管理员可以跨部门查看所有数据
TC-003: 权限变更立即生效且产生审计日志
TC-004: 高危操作被正确阻止
```

### 第四阶段（第7-8周）：正式上线

**任务**：
- [ ] 灰度发布到测试环境
- [ ] 用户培训与权限变更通知
- [ ] 正式迁移（可选：两阶段迁移）
- [ ] 监控与应急预案

**监控指标**：
```
- 权限校验成功率: > 99%
- 高危操作告警数
- 权限相关的支持工单数
- 用户权限提升申请处理时间
```

---

## 九、权限管理最佳实践

### 9.1 最小权限原则 (Principle of Least Privilege)

```javascript
// ❌ 错误做法
user.permissions = ['*'];  // 给所有权限

// ✓ 正确做法
user.permissions = [
  'datasource:view',
  'task:execute',
  'data:query'
];  // 只给必要的权限
```

### 9.2 权限过期管理

```python
# 季度权限审查
class PermissionAuditTask:
    """每季度自动进行权限审查"""
    
    def audit_permissions(self):
        # 1. 检查权限是否与岗位一致
        # 2. 检查权限是否超期（超过6个月未审查）
        # 3. 检查离职员工权限是否清理
        # 4. 生成权限审查报告
        pass
```

### 9.3 权限与部门同步

```python
# 当员工调动部门时
def transfer_employee(employee_id, new_department_id):
    employee = AdminUser.get(employee_id)
    
    # 1. 更新部门归属
    employee.department_id = new_department_id
    
    # 2. 自动调整部门隔离的权限
    if not is_admin(employee):
        # 清除旧部门的数据访问权
        employee.update_department_scope(new_department_id)
    
    # 3. 记录审计日志
    log_audit('employee_transfer', employee_id, {
        'old_department': old_dept,
        'new_department': new_department
    })
    
    db.commit()
```

### 9.4 权限文档与通知

```markdown
当权限变更时，需要：
1. 向用户发送变更通知邮件
2. 更新权限文档wiki
3. 在操作日志中详细记录
4. 管理员需确认权限变更
```

---

## 十、故障排查与问题解决

### 常见问题 (FAQ)

**Q1: 用户能否拥有多个角色？**
```
A: 当前设计中，一个用户只能有一个角色。
   如需多角色，需要扩展模型为多对多关系。
```

**Q2: 如何临时撤销某个权限？**
```
A: 通过创建权限黑名单(PermissionBlacklist)实现：
   user.permissions - blacklist.permissions = effective_permissions
```

**Q3: 权限变更多久生效？**
```
A: 建议在以下几个时间点生效：
   1. 立即生效（用户需要刷新后才能看到）
   2. 下次登录生效（需要重新加载权限）
   3. 24小时内生效（定时任务同步）
```

**Q4: 如何处理离职员工的权限？**
```
A: 建立离职员工权限清理流程：
   1. HR通知系统管理员
   2. 系统管理员禁用该账户（设置status=LOCKED）
   3. 其他权限逐步转移给指定人员
   4. 7天后完全删除账户数据（备份保留）
   5. 生成审计报告
```

### 调试技巧

```python
# 1. 查看用户当前权限
user = AdminUser.get(user_id)
print(f"用户权限: {user.permissions}")
print(f"用户角色: {user.role}")

# 2. 测试权限检查
from backend.services.permission_checker import PermissionChecker
checker = PermissionChecker(user)
has_perm = checker.has('datasource:edit')
print(f"有编辑数据源权限: {has_perm}")

# 3. 生成权限诊断报告
DiagnosticReport.generate_permission_report(user_id)
```

---

## 十一、附录：参考实现清单

### 后端实现清单

- [ ] `models/role.py` - 完善Role模型（已有）
- [ ] `models/permission.py` - 创建Permission权限表
- [ ] `models/admin_user.py` - 完善AdminUser与权限的关联
- [ ] `services/permission_checker.py` - 权限检查服务
- [ ] `middleware/permission_middleware.py` - 权限校验中间件
- [ ] `api/routes/permissions.py` - 权限管理API
- [ ] `api/routes/audit_logs.py` - 审计日志API

### 前端实现清单

- [ ] `stores/permission_store.js` - 权限状态存储
- [ ] `directives/v-permission.js` - 权限指令（隐藏元素）
- [ ] `composables/usePermission.js` - 权限检查组合函数
- [ ] `views/admin/users/RolePermission.vue` - 角色权限管理页面（已有基础）
- [ ] `components/admin/PermissionTree.vue` - 权限树组件
- [ ] `components/admin/RoleEditDialog.vue` - 角色编辑对话框
- [ ] `utils/permission_helper.js` - 权限工具函数

### 数据库脚本

```sql
-- 创建权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(100) UNIQUE NOT NULL,  -- 权限编码
    name VARCHAR(100) NOT NULL,         -- 权限名称
    description TEXT,
    resource_type VARCHAR(50),          -- 资源类型
    action_type VARCHAR(50),            -- 操作类型
    sort_order INT DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建角色-权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    operator_id INT NOT NULL,
    operator_name VARCHAR(100),
    operator_department VARCHAR(100),
    operation_type VARCHAR(100),
    operation_name VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id INT,
    resource_name VARCHAR(255),
    changes JSON,
    status VARCHAR(20),
    error_message TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES admin_users(id) ON DELETE SET NULL,
    INDEX idx_operator_id (operator_id),
    INDEX idx_created_at (created_at),
    INDEX idx_operation_type (operation_type)
);
```

---

## 十二、版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1.0 | 2026-03-02 | 运营管理建议 | 初版：完整的角色管理规划方案 |

---

## 十三、相关文档

- [ADMIN_PERMISSION_CONTROL.md](ADMIN_PERMISSION_CONTROL.md) - 权限控制技术方案
- [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md) - 用户管理手册
- [ADMIN_RBAC_OPTIMIZATION_ADVICE_v1.md](ADMIN_RBAC_OPTIMIZATION_ADVICE_v1.md) - RBAC优化建议
- [RolePermission.vue源码](../frontend/src/views/admin/users/RolePermission.vue) - 前端实现

---

**文档联系人**: 系统管理员  
**最后更新**: 2026-03-02  
**下次审查**: 2026-06-02
