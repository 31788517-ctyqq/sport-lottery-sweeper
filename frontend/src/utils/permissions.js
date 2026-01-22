/**
 * 权限检查工具类
 * 基于RBAC（基于角色的访问控制）模型
 */

/**
 * 权限类型枚举
 */
export const PermissionType = {
  READ: 'read',
  WRITE: 'write',
  DELETE: 'delete',
  ADMIN: 'admin',
  EXPORT: 'export',
  IMPORT: 'import'
};

/**
 * 资源类型枚举
 */
export const ResourceType = {
  MATCH: 'match',
  INTELLIGENCE: 'intelligence',
  USER: 'user',
  ADMIN: 'admin',
  SYSTEM: 'system',
  REPORT: 'report'
};

/**
 * 角色枚举
 */
export const UserRole = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  EDITOR: 'editor',
  VIEWER: 'viewer',
  USER: 'user',
  GUEST: 'guest'
};

/**
 * 权限定义
 */
export const PERMISSIONS = {
  // 比赛相关权限
  VIEW_MATCHES: `${ResourceType.MATCH}:${PermissionType.READ}`,
  EDIT_MATCH: `${ResourceType.MATCH}:${PermissionType.WRITE}`,
  DELETE_MATCH: `${ResourceType.MATCH}:${PermissionType.DELETE}`,
  
  // 情报相关权限
  VIEW_INTELLIGENCE: `${ResourceType.INTELLIGENCE}:${PermissionType.READ}`,
  EDIT_INTELLIGENCE: `${ResourceType.INTELLIGENCE}:${PermissionType.WRITE}`,
  DELETE_INTELLIGENCE: `${ResourceType.INTELLIGENCE}:${PermissionType.DELETE}`,
  
  // 用户相关权限
  VIEW_USERS: `${ResourceType.USER}:${PermissionType.READ}`,
  EDIT_USER: `${ResourceType.USER}:${PermissionType.WRITE}`,
  DELETE_USER: `${ResourceType.USER}:${PermissionType.DELETE}`,
  
  // 管理员权限
  ACCESS_ADMIN: `${ResourceType.ADMIN}:${PermissionType.ADMIN}`,
  
  // 系统权限
  MANAGE_SYSTEM: `${ResourceType.SYSTEM}:${PermissionType.ADMIN}`,
  
  // 报表权限
  EXPORT_REPORTS: `${ResourceType.REPORT}:${PermissionType.EXPORT}`,
  IMPORT_DATA: `${ResourceType.REPORT}:${PermissionType.IMPORT}`
};

/**
 * 角色权限映射
 */
export const ROLE_PERMISSIONS = {
  [UserRole.SUPER_ADMIN]: Object.values(PERMISSIONS),
  [UserRole.ADMIN]: [
    PERMISSIONS.VIEW_MATCHES,
    PERMISSIONS.EDIT_MATCH,
    PERMISSIONS.DELETE_MATCH,
    PERMISSIONS.VIEW_INTELLIGENCE,
    PERMISSIONS.EDIT_INTELLIGENCE,
    PERMISSIONS.DELETE_INTELLIGENCE,
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.EDIT_USER,
    PERMISSIONS.ACCESS_ADMIN,
    PERMISSIONS.EXPORT_REPORTS,
    PERMISSIONS.IMPORT_DATA
  ],
  [UserRole.EDITOR]: [
    PERMISSIONS.VIEW_MATCHES,
    PERMISSIONS.EDIT_MATCH,
    PERMISSIONS.VIEW_INTELLIGENCE,
    PERMISSIONS.EDIT_INTELLIGENCE,
    PERMISSIONS.EXPORT_REPORTS
  ],
  [UserRole.VIEWER]: [
    PERMISSIONS.VIEW_MATCHES,
    PERMISSIONS.VIEW_INTELLIGENCE,
    PERMISSIONS.EXPORT_REPORTS
  ],
  [UserRole.USER]: [
    PERMISSIONS.VIEW_MATCHES,
    PERMISSIONS.VIEW_INTELLIGENCE
  ],
  [UserRole.GUEST]: [
    // 最低权限或需要特殊处理的权限
  ]
};

/**
 * 检查用户是否拥有指定权限
 * @param {Array<string>} userPermissions - 用户拥有的权限列表
 * @param {string} requiredPermission - 需要的权限
 * @returns {boolean} 是否拥有权限
 */
export function hasPermission(userPermissions, requiredPermission) {
  if (!userPermissions || !Array.isArray(userPermissions)) {
    return false;
  }
  
  // 超级管理员拥有所有权限
  if (userPermissions.includes(PERMISSIONS.MANAGE_SYSTEM)) {
    return true;
  }
  
  return userPermissions.includes(requiredPermission);
}

/**
 * 检查用户是否拥有任一权限
 * @param {Array<string>} userPermissions - 用户拥有的权限列表
 * @param {Array<string>} requiredPermissions - 需要的权限列表
 * @returns {boolean} 是否拥有任一权限
 */
export function hasAnyPermission(userPermissions, requiredPermissions) {
  if (!requiredPermissions || !Array.isArray(requiredPermissions)) {
    return false;
  }
  
  return requiredPermissions.some(permission => 
    hasPermission(userPermissions, permission)
  );
}

/**
 * 检查用户是否拥有所有权限
 * @param {Array<string>} userPermissions - 用户拥有的权限列表
 * @param {Array<string>} requiredPermissions - 需要的权限列表
 * @returns {boolean} 是否拥有所有权限
 */
export function hasAllPermissions(userPermissions, requiredPermissions) {
  if (!requiredPermissions || !Array.isArray(requiredPermissions)) {
    return false;
  }
  
  return requiredPermissions.every(permission => 
    hasPermission(userPermissions, permission)
  );
}

/**
 * 根据角色获取权限列表
 * @param {string|Array<string>} roles - 用户角色
 * @returns {Array<string>} 权限列表
 */
export function getPermissionsByRole(roles) {
  if (!roles) return [];
  
  const roleArray = Array.isArray(roles) ? roles : [roles];
  const permissions = new Set();
  
  roleArray.forEach(role => {
    const rolePerms = ROLE_PERMISSIONS[role] || [];
    rolePerms.forEach(perm => permissions.add(perm));
  });
  
  return Array.from(permissions);
}

/**
 * 检查用户角色
 * @param {Array<string>} userRoles - 用户角色列表
 * @param {string|Array<string>} requiredRoles - 需要的角色
 * @returns {boolean} 是否拥有角色
 */
export function hasRole(userRoles, requiredRoles) {
  if (!userRoles || !Array.isArray(userRoles)) {
    return false;
  }
  
  const requiredArray = Array.isArray(requiredRoles) 
    ? requiredRoles 
    : [requiredRoles];
  
  return requiredArray.some(role => userRoles.includes(role));
}

/**
 * 获取用户的最高权限角色
 * @param {Array<string>} userRoles - 用户角色列表
 * @returns {string|null} 最高权限角色
 */
export function getHighestRole(userRoles) {
  if (!userRoles || !Array.isArray(userRoles)) {
    return null;
  }
  
  const roleHierarchy = [
    UserRole.GUEST,
    UserRole.USER,
    UserRole.VIEWER,
    UserRole.EDITOR,
    UserRole.ADMIN,
    UserRole.SUPER_ADMIN
  ];
  
  let highestRoleIndex = -1;
  let highestRole = null;
  
  userRoles.forEach(role => {
    const index = roleHierarchy.indexOf(role);
    if (index > highestRoleIndex) {
      highestRoleIndex = index;
      highestRole = role;
    }
  });
  
  return highestRole;
}

/**
 * 检查资源权限
 * @param {Object} user - 用户对象
 * @param {string} resourceType - 资源类型
 * @param {string} permissionType - 权限类型
 * @param {Object} resource - 资源对象（用于更细粒度的权限控制）
 * @returns {boolean} 是否有权限
 */
export function checkResourcePermission(
  user, 
  resourceType, 
  permissionType, 
  resource = null
) {
  if (!user || !user.permissions) {
    return false;
  }
  
  const requiredPermission = `${resourceType}:${permissionType}`;
  
  // 基础权限检查
  if (!hasPermission(user.permissions, requiredPermission)) {
    return false;
  }
  
  // 细粒度权限检查（例如：只能编辑自己创建的资源）
  if (resource && resource.createdBy && permissionType === PermissionType.WRITE) {
    if (user.id === resource.createdBy) {
      return true;
    }
    
    // 如果不是资源创建者，需要额外权限
    const adminPermission = `${resourceType}:${PermissionType.ADMIN}`;
    return hasPermission(user.permissions, adminPermission);
  }
  
  return true;
}

/**
 * 权限指令的辅助函数
 * @param {Object} user - 用户对象
 * @param {string} value - 指令值（权限字符串）
 * @param {Object} binding - 指令绑定对象
 * @returns {boolean} 是否显示元素
 */
export function permissionDirectiveHelper(user, value, binding) {
  if (!value) return true;
  
  const { arg, modifiers } = binding || {};
  
  // 处理不同的指令格式
  if (modifiers.any) {
    // v-permission.any="['perm1', 'perm2']"
    return hasAnyPermission(user?.permissions, value);
  } else if (modifiers.all) {
    // v-permission.all="['perm1', 'perm2']"
    return hasAllPermissions(user?.permissions, value);
  } else if (modifiers.role) {
    // v-permission.role="'admin'"
    return hasRole(user?.roles, value);
  } else if (arg === 'role') {
    // v-permission:role="'admin'"
    return hasRole(user?.roles, value);
  } else {
    // v-permission="'perm1'"
    return hasPermission(user?.permissions, value);
  }
}

export default {
  PermissionType,
  ResourceType,
  UserRole,
  PERMISSIONS,
  ROLE_PERMISSIONS,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getPermissionsByRole,
  hasRole,
  getHighestRole,
  checkResourcePermission,
  permissionDirectiveHelper
};