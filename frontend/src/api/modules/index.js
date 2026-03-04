/**
 * API模块统一出口
 * 按业务域组织所有的API接口
 */

// 用户管理模块
export * as UserAPI from './users.js'

// 角色管理模块
export * as RoleAPI from './roles.js'

// 部门管理模块
export * as DepartmentAPI from './departments.js'

// 权限管理模块
export * as PermissionAPI from './permissions.js'

// 操作日志模块
export * as OperationLogAPI from './operation-logs.js'

// 用户个人资料模块
export * as UserProfileAPI from './user-profile.js'

// 默认导出所有API
export default {
  UserAPI,
  RoleAPI,
  DepartmentAPI,
  PermissionAPI,
  OperationLogAPI,
  UserProfileAPI
}