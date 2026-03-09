import { ref, computed, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

/**
 * 权限管理 Composable
 */
export function usePermissions() {
  const userStore = useUserStore()
  const loading = ref(false)
  
  // 权限缓存
  const permissionCache = reactive(new Map())
  
  /**
   * 检查用户是否具有指定权限
   * @param {string|Array} permissions - 权限标识或权限数组
   * @param {Object} options - 选项
   * @returns {boolean} 是否有权限
   */
  const hasPermission = (permissions, options = {}) => {
    const { requireAll = false, cache = true } = options
    
    // 超级管理员拥有所有权限
    if (userStore.isSuperAdmin) {
      return true
    }
    
    // 未登录用户没有任何权限
    if (!userStore.isLoggedIn) {
      return false
    }
    
    // 转换为数组处理
    const permissionList = Array.isArray(permissions) ? permissions : [permissions]
    
    // 检查权限
    const userPermissions = userStore.permissions || []
    
    if (requireAll) {
      // 需要拥有所有权限
      return permissionList.every(permission => 
        userPermissions.includes(permission) || 
        userPermissions.some(userPerm => userPerm.startsWith(`${permission}:`))
      )
    } else {
      // 只需要拥有其中一个权限
      return permissionList.some(permission => 
        userPermissions.includes(permission) || 
        userPermissions.some(userPerm => userPerm.startsWith(`${permission}:`))
      )
    }
  }
  
  /**
   * 检查用户是否具有指定角色
   * @param {string|Array} roles - 角色标识或角色数组
   * @param {Object} options - 选项
   * @returns {boolean} 是否有角色
   */
  const hasRole = (roles, options = {}) => {
    const { requireAll = false } = options
    
    // 超级管理员拥有所有角色
    if (userStore.isSuperAdmin) {
      return true
    }
    
    // 未登录用户没有任何角色
    if (!userStore.isLoggedIn) {
      return false
    }
    
    // 转换为数组处理
    const roleList = Array.isArray(roles) ? roles : [roles]
    
    // 检查角色
    const userRoles = userStore.roles || []
    
    if (requireAll) {
      return roleList.every(role => userRoles.includes(role))
    } else {
      return roleList.some(role => userRoles.includes(role))
    }
  }
  
  /**
   * 检查是否为管理员（管理员或超级管理员）
   * @returns {boolean} 是否为管理员
   */
  const isAdmin = computed(() => {
    return userStore.isSuperAdmin || userStore.isAdmin
  })
  
  /**
   * 检查是否可以访问管理功能
   * @returns {boolean} 是否可以访问
   */
  const canAccessAdmin = computed(() => {
    return hasRole(['admin', 'super_admin']) || hasPermission(['admin.access'])
  })
  
  /**
   * 权限指令函数 - 用于模板中的权限控制
   * @param {string|Array} permissions - 权限标识
   * @param {Object} options - 选项
   * @returns {{ value: boolean }} 权限状态
   */
  const permissionDirective = (permissions, options = {}) => {
    return {
      value: hasPermission(permissions, options),
      hasPermission: hasPermission(permissions, options)
    }
  }
  
  /**
   * 角色指令函数 - 用于模板中的角色控制
   * @param {string|Array} roles - 角色标识
   * @param {Object} options - 选项
   * @returns {{ value: boolean }} 角色状态
   */
  const roleDirective = (roles, options = {}) => {
    return {
      value: hasRole(roles, options),
      hasRole: hasRole(roles, options)
    }
  }
  
  /**
   * 获取用户权限树
   * @returns {Promise} 权限树
   */
  const getPermissionTree = async () => {
    const cacheKey = 'permission_tree'
    
    // 检查缓存
    if (permissionCache.has(cacheKey)) {
      return permissionCache.get(cacheKey)
    }
    
    loading.value = true
    try {
      // 这里应该调用API获取权限树
      // const tree = await getPermissionTreeApi()
      
      // 模拟权限树数据
      const tree = [
        {
          id: 'admin',
          label: '系统管理',
          children: [
            { id: 'admin.users', label: '用户管理' },
            { id: 'admin.roles', label: '角色管理' },
            { id: 'admin.permissions', label: '权限管理' },
            { id: 'admin.departments', label: '部门管理' },
            { id: 'admin.logs', label: '日志审计' }
          ]
        },
        {
          id: 'lottery',
          label: '彩票管理',
          children: [
            { id: 'lottery.matches', label: '比赛管理' },
            { id: 'lottery.predictions', label: '预测管理' },
            { id: 'lottery.analysis', label: '分析管理' }
          ]
        }
      ]
      
      permissionCache.set(cacheKey, tree)
      return tree
    } catch (error) {
      ElMessage.error('获取权限树失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 清除权限缓存
   * @param {string} key - 缓存键，不传则清除所有
   */
  const clearPermissionCache = (key) => {
    if (key) {
      permissionCache.delete(key)
    } else {
      permissionCache.clear()
    }
  }
  
  /**
   * 权限守卫 - 用于路由守卫
   * @param {string|Array} requiredPermissions - 需要的权限
   * @param {string} redirectRoute - 无权限时重定向的路由
   * @returns {boolean} 是否允许访问
   */
  const permissionGuard = (requiredPermissions, redirectRoute = '/403') => {
    if (!hasPermission(requiredPermissions)) {
      ElMessageBox.alert('您没有权限访问此功能', '权限不足', {
        type: 'warning',
        confirmButtonText: '确定'
      }).then(() => {
        router.push(redirectRoute)
      })
      return false
    }
    return true
  }
  
  return {
    // 状态
    loading,
    
    // 方法
    hasPermission,
    hasRole,
    isAdmin,
    canAccessAdmin,
    permissionDirective,
    roleDirective,
    getPermissionTree,
    clearPermissionCache,
    permissionGuard
  }
}

/**
 * 创建权限指令
 */
export const createPermissionDirective = (app) => {
  // v-permission 指令
  app.directive('permission', {
    mounted(el, binding) {
      const { value, modifiers } = binding
      const { hasPermission } = usePermissions()
      
      if (value && !hasPermission(value, { requireAll: modifiers.all })) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  })
  
  // v-role 指令
  app.directive('role', {
    mounted(el, binding) {
      const { value, modifiers } = binding
      const { hasRole } = usePermissions()
      
      if (value && !hasRole(value, { requireAll: modifiers.all })) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  })
  
  // v-admin 指令 - 仅管理员可见
  app.directive('admin', {
    mounted(el, binding) {
      const { hasPermission } = usePermissions()
      
      if (!hasPermission('admin.access')) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  })
}

/**
 * 常用权限常量
 */
export const PERMISSIONS = {
  // 系统管理
  ADMIN_ACCESS: 'admin.access',
  USER_VIEW: 'admin.users.view',
  USER_CREATE: 'admin.users.create',
  USER_EDIT: 'admin.users.edit',
  USER_DELETE: 'admin.users.delete',
  USER_MANAGE: 'admin.users.manage',
  
  ROLE_VIEW: 'admin.roles.view',
  ROLE_CREATE: 'admin.roles.create',
  ROLE_EDIT: 'admin.roles.edit',
  ROLE_DELETE: 'admin.roles.delete',
  ROLE_MANAGE: 'admin.roles.manage',
  
  PERMISSION_VIEW: 'admin.permissions.view',
  PERMISSION_MANAGE: 'admin.permissions.manage',
  
  DEPARTMENT_VIEW: 'admin.departments.view',
  DEPARTMENT_CREATE: 'admin.departments.create',
  DEPARTMENT_EDIT: 'admin.departments.edit',
  DEPARTMENT_DELETE: 'admin.departments.delete',
  DEPARTMENT_MANAGE: 'admin.departments.manage',
  
  LOG_VIEW: 'admin.logs.view',
  LOG_EXPORT: 'admin.logs.export',
  
  // 彩票管理
  LOTTERY_MATCHES_VIEW: 'lottery.matches.view',
  LOTTERY_MATCHES_MANAGE: 'lottery.matches.manage',
  LOTTERY_PREDICTIONS_VIEW: 'lottery.predictions.view',
  LOTTERY_ANALYSIS_VIEW: 'lottery.analysis.view'
}

/**
 * 常用角色常量
 */
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  MANAGER: 'manager',
  USER: 'user',
  GUEST: 'guest'
}