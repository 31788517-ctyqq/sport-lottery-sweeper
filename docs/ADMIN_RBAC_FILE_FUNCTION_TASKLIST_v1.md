# 后台用户管理 RBAC 改造实施任务单（按文件到函数级，v1）

> 来源：`docs/ADMIN_RBAC_OPTIMIZATION_ADVICE_v1.md`  
> 目标：把 RBAC 改造拆成可直接开发执行的“文件 + 函数”任务。  
> 约束：本任务单用于开发执行，不在本文写实现代码。

## 1. 实施范围与边界

- 范围：用户管理、角色管理、权限管理、部门管理、鉴权与会话、安全审计、前端权限入口统一。
- 本轮不做：服务端动态路由全量落地、完整审批流引擎、全业务域 data_scope 改造。

## 2. 统一契约基线（先执行）

统一使用如下主路径：
- 用户：`/api/v1/admin/admin-users/*`
- 角色：`/api/v1/admin/roles/*`
- 权限：`/api/v1/admin/permissions/*`
- 部门：`/api/v1/admin/departments/*`

历史路径（`/api/admin/*`）仅做兼容层，标注下线时间，不再新增调用。

## 3. 后端任务（文件到函数级）

## 3.1 鉴权与会话治理（P1）

| ID | 文件 | 函数/对象 | 改造任务 | 验收点 |
|---|---|---|---|---|
| B-AUTH-01 | `backend/models/admin_user.py` | `class AdminUser` | 增加 `token_version`（`Integer`, default=0, index）；预留 `data_scope` 字段（可选） | 模型字段可迁移、可读写 |
| B-AUTH-02 | `backend/alembic/versions/*.py` | `upgrade` / `downgrade` | 新增迁移：给 `admin_users` 增加 `token_version`（和 `data_scope` 如启用） | 迁移可正反执行 |
| B-AUTH-03 | `backend/core/security.py` | `create_access_token` | JWT payload 增加 `token_version` 声明 | 新签发 token 含版本号 |
| B-AUTH-04 | `backend/core/security.py` | `get_current_user` | 校验 token 内 `token_version` 与 DB 一致；不一致返回 401 | 改权后旧 token 失效 |
| B-AUTH-05 | `backend/crud/admin_user.py` | `update_status` / `reset_password` / `change_password` / 新增 `bump_token_version` | 用户禁用、重置密码、改密后自动 `token_version + 1` | 关键操作后旧 token 失效 |
| B-AUTH-06 | `backend/api/v1/admin_user_management.py` | `update_admin_user_status` / `reset_admin_user_password` / `change_current_password` | 调用 `crud.admin_user.bump_token_version`，并补充审计字段 | 操作后返回成功且审计完整 |

## 3.2 用户管理主链路（P1）

| ID | 文件 | 函数/对象 | 改造任务 | 验收点 |
|---|---|---|---|---|
| B-USER-01 | `backend/api/v1/admin_user_management.py` | `list_admin_users` | 同时兼容 `page/size` 与 `skip/limit`，统一响应分页字段 | 前端分页参数一致生效 |
| B-USER-02 | `backend/api/v1/admin_user_management.py` | `create_admin_user` | 放宽部门可选（已支持则保留），补充字段校验错误码 | 不填部门可创建成功 |
| B-USER-03 | `backend/api/v1/admin_user_management.py` | `get_admin_user` / `update_admin_user` | 字段映射统一（`department_id` 与 `department`） | 编辑后列表/详情一致 |
| B-USER-04 | `backend/api/v1/admin_user_management.py` | `batch_delete_admin_users` | 明确软删除语义与返回统计 | 返回删除数量准确 |
| B-USER-05 | `backend/crud/admin_user.py` | `get_multi` | 支持按 `department_id`/`role`/`status`/`search` 正确组合过滤 | 组合筛选结果正确 |
| B-USER-06 | `backend/schemas/admin_user.py` | `AdminUserCreate` / `AdminUserUpdate` / `AdminUserResponse` | 清理字段定义与校验文案，避免字段歧义 | 422 提示可读且稳定 |

## 3.3 角色/权限/部门契约收敛（P0/P1）

| ID | 文件 | 函数/对象 | 改造任务 | 验收点 |
|---|---|---|---|---|
| B-RBAC-01 | `backend/api/v1/roles.py` | `get_roles` / `get_role` / `create_role` / `update_role` / `delete_role` | 统一响应结构为 `code/data/message`（或统一包装器） | 与前端解析逻辑一致 |
| B-RBAC-02 | `backend/api/v1/roles.py` | `update_role_status` / `get_role_permissions` / `assign_role_permissions` | 明确请求体/查询参数契约，固定错误码 | 状态切换与授权可稳定调用 |
| B-RBAC-03 | `backend/api/v1/permissions.py` | `get_permissions` / `get_permission_tree` / `get_permissions_flat` | 从 mock 数据迁移到真实数据源（最少先只读） | 权限数据不再硬编码 |
| B-RBAC-04 | `backend/api/v1/departments.py` | `get_departments` / `get_department_members` / `assign_user_to_department` / `remove_user_from_department` | 统一分页/返回结构；成员变更写审计 | 成员调整可追踪 |
| B-RBAC-05 | `backend/main.py` | 路由注册区块 | 仅保留一套主路由声明；旧路由保留兼容提示并标记下线 | 路由冲突/重复注册消失 |

## 3.4 审计日志与安全（P1）

| ID | 文件 | 函数/对象 | 改造任务 | 验收点 |
|---|---|---|---|---|
| B-AUDIT-01 | `backend/crud/admin_user.py` | `CRUDAdminOperationLog.create` | 标准化审计必填字段（action/resource/ip/user_agent/status） | 关键操作日志完整 |
| B-AUDIT-02 | `backend/api/v1/admin_user_management.py` | 所有写接口 | 统一调用审计写入，补 `changes_before/after` | 审计可追溯 |
| B-AUDIT-03 | `backend/api/v1/admin/logs.py` | 查询接口 | 增加按动作/操作者/时间过滤的稳定契约 | 可用于运营审计检索 |

## 4. 前端任务（文件到函数级）

## 4.1 API 层收敛（P0）

| ID | 文件 | 函数 | 改造任务 | 验收点 |
|---|---|---|---|---|
| F-API-01 | `frontend/src/api/modules/roles.js` | `batchDeleteRoles` / `updateRoleStatus` / `getRolePermissions` / `assignRolePermissions` / `getPermissionTree` / `getAllPermissions` / `copyRole` / `getRoleStats` / `exportRoles` / `importRoles` | 把 `/api/admin/*` 全部改为 `/api/v1/admin/*` | 无 404/405 |
| F-API-02 | `frontend/src/api/modules/users.js` | `normalizeListParams` / `updateUserStatus` / `createUser` / `updateUser` | 与后端分页、状态接口契约对齐 | 列表与状态切换无回归 |
| F-API-03 | `frontend/src/api/modules/departments.js` | 成员相关函数 | 校验 method/path 与后端一致（特别是成员增删） | 成员管理可联调 |
| F-API-04 | `frontend/src/api/modules/permissions.js` | `getPermissions` / `getPermissionTree` | 对齐后端真实权限结构（tree/flat） | 角色授权树正常显示 |

## 4.2 用户管理页面链路（P1）

| ID | 文件 | 函数/逻辑 | 改造任务 | 验收点 |
|---|---|---|---|---|
| F-USER-01 | `frontend/src/views/admin/users/UserList.vue` | `loadUsers` / `handleSearch` / `handleToggleStatus` | 参数统一使用主契约；禁用/启用按钮按状态准确切换 | 列表筛选与状态操作正确 |
| F-USER-02 | `frontend/src/components/admin/UserDetailDialog.vue` | `handleCreate` / `handleUpdate` / 表单校验规则 | 部门改为非必填；`confirmPassword` 规则与后端一致；中文提示统一 | 创建/编辑体验稳定 |
| F-USER-03 | `frontend/src/views/admin/users/RolePermission.vue` | `loadRoles` / `loadPermissions` / `saveRolePermissions` | 使用统一 API 与响应解析 | 权限树保存成功 |
| F-USER-04 | `frontend/src/views/admin/users/DepartmentManagement.vue` | `loadDepartments` / `loadMembers` / `assign/remove member` | 对齐成员接口契约并处理错误提示 | 部门成员管理可用 |

## 4.3 权限入口统一（P1）

| ID | 文件 | 函数/逻辑 | 改造任务 | 验收点 |
|---|---|---|---|---|
| F-PERM-01 | `frontend/src/stores/user.js` | `login` / `initializeFromStorage` / `checkPermission` / `checkRole` | 统一 token/roles/permissions 字段来源；去除分散判定 | 刷新后权限状态一致 |
| F-PERM-02 | `frontend/src/directives/permission.js` | `getUserFromContext` / `checkAccess` / `handleElement` | 只从统一 store 取权限；减少多来源回退造成的不一致 | 按钮权限表现稳定 |
| F-PERM-03 | `frontend/src/router/index.js` 与 `frontend/src/router/modules/*.js` | 路由 `meta.roles/permissions` 与守卫 | 收敛路由权限定义风格，移除重复/冲突规则 | 路由鉴权行为一致 |

## 5. 测试任务（按文件）

## 5.1 后端测试

| ID | 文件 | 用例要点 |
|---|---|---|
| T-BE-01 | `backend/tests/unit/core/test_security.py` | token_version claim 生成与校验；版本不匹配返回 401 |
| T-BE-02 | `backend/tests/unit/api/admin/test_admin_user_management.py`（新增） | 创建用户（部门可空）、状态切换、重置密码、角色分配、审计写入 |
| T-BE-03 | `backend/tests/unit/api/admin/test_roles_permissions_contract.py`（新增） | roles/permissions/departments 契约与错误码 |
| T-BE-04 | `backend/tests/integration/test_rbac_token_invalidation.py`（新增） | 改权后旧 token 失效、重新登录生效 |

## 5.2 前端测试

| ID | 文件 | 用例要点 |
|---|---|---|
| T-FE-01 | `frontend/src/tests/unit/api/users.test.js` | `users.js` 参数归一化与状态接口 method/path |
| T-FE-02 | `frontend/src/tests/unit/api/admin.test.js` / 新增 `roles.test.js` | `roles.js` 路径统一为 `/api/v1/admin/*` |
| T-FE-03 | `frontend/src/tests/unit/stores/user.test.js` | 登录态、权限集合、刷新恢复 |
| T-FE-04 | `frontend/src/tests/e2e/user_management_e2e.test.js` | 用户列表->创建->编辑->状态切换->角色分配端到端 |

## 6. PR 拆分建议（执行顺序）

| PR | 范围 | 必过检查 |
|---|---|---|
| PR-1 | 契约收敛（API 路径、响应格式、前端 API 模块） | 后端单测 + 前端 API 单测 |
| PR-2 | 鉴权与会话（token_version + 关键操作失效） | 安全单测 + 集成测试 |
| PR-3 | 页面链路与权限统一（store/directive/router + 用户管理页面） | E2E 冒烟 + 回归 |

## 7. 发布验收最小清单

- 登录后访问用户管理三页（用户/角色权限/部门）无 4xx/5xx。
- 创建用户不填部门可成功。
- 状态切换接口不再出现 405。
- 角色权限保存成功，刷新后生效。
- 关键操作均有审计日志，且可按时间和操作者检索。
- 改权或重置密码后旧 token 失效，需重新登录。

---

状态：`可执行`  
版本：`v1`  
最后更新：`2026-03-01`
