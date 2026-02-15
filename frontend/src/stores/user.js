import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, userAPI, adminAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

// 用户状态管理 Store
export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(null)
  const refreshToken = ref(null)
  const permissions = ref([])
  const roles = ref([])
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isSuperAdmin = computed(() => roles.value.includes('super_admin'))
  const isAdmin = computed(() => roles.value.includes('admin') || isSuperAdmin.value)
  const userInfo = computed(() => user.value)

  // Actions
  
  /**
   * 用户登录
   */
  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await authAPI.login(credentials)
      
      // 保存token和用户信息
      token.value = response.token
      refreshToken.value = response.refresh_token
      user.value = response.user
      permissions.value = response.permissions || []
      roles.value = response.roles || []
      
      // 保存到localStorage
      localStorage.setItem('token', response.token)
      localStorage.setItem('refreshToken', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      localStorage.setItem('permissions', JSON.stringify(response.permissions || []))
      localStorage.setItem('roles', JSON.stringify(response.roles || []))
      
      ElMessage.success('登录成功')
      return response
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      // 清除状态
      user.value = null
      token.value = null
      refreshToken.value = null
      permissions.value = []
      roles.value = []
      
      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      localStorage.removeItem('roles')
      
      // 开发环境下跳过强制跳转，避免循环
      if (import.meta.env.MODE !== 'development') {
        // 统一使用相对路径进行跳转，避免硬编码端口
        window.location.href = '/login'
      } else {
        console.warn('🔧 开发模式：跳过logout跳转')
      }
    }
  }

  /**
   * 更新用户信息
   */
  const updateProfile = async (profileData) => {
    loading.value = true
    try {
      const response = await updateProfileApi(profileData)
      user.value = { ...user.value, ...response }
      localStorage.setItem('user', JSON.stringify(user.value))
      ElMessage.success('个人信息更新成功')
      return response
    } catch (error) {
      ElMessage.error(error.message || '更新失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 修改密码
   */
  const changePassword = async (passwordData) => {
    loading.value = true
    try {
      const response = await changePasswordApi(passwordData)
      ElMessage.success('密码修改成功')
      return response
    } catch (error) {
      ElMessage.error(error.message || '密码修改失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新Token
   */
  const refreshTokenAction = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
    
    try {
      const response = await refreshTokenApi(refreshToken.value)
      token.value = response.token
      refreshToken.value = response.refresh_token
      
      localStorage.setItem('token', response.token)
      localStorage.setItem('refreshToken', response.refresh_token)
      
      return response
    } catch (error) {
      // Token刷新失败，执行登出
      logout()
      throw error
    }
  }

  /**
   * 检查权限
   */
  const checkPermission = (requiredPermissions, options = {}) => {
    const { requireAll = false } = options
    
    if (!isLoggedIn.value) {
      return false
    }
    
    if (isSuperAdmin.value) {
      return true
    }
    
    if (Array.isArray(requiredPermissions)) {
      if (requireAll) {
        return requiredPermissions.every(permission => 
          permissions.value.includes(permission)
        )
      } else {
        return requiredPermissions.some(permission => 
          permissions.value.includes(permission)
        )
      }
    }
    
    return permissions.value.includes(requiredPermissions)
  }

  /**
   * 检查角色
   */
  const checkRole = (requiredRoles, options = {}) => {
    const { requireAll = false } = options
    
    if (!isLoggedIn.value) {
      return false
    }
    
    if (isSuperAdmin.value) {
      return true
    }
    
    if (Array.isArray(requiredRoles)) {
      if (requireAll) {
        return requiredRoles.every(role => roles.value.includes(role))
      } else {
        return requiredRoles.some(role => roles.value.includes(role))
      }
    }
    
    return roles.value.includes(requiredRoles)
  }

  /**
   * 从localStorage初始化状态
   */
  const initializeFromStorage = () => {
    const savedToken = localStorage.getItem('token')
    const savedRefreshToken = localStorage.getItem('refreshToken')
    const savedUser = localStorage.getItem('user')
    const savedPermissions = localStorage.getItem('permissions')
    const savedRoles = localStorage.getItem('roles')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      refreshToken.value = savedRefreshToken
      user.value = JSON.parse(savedUser)
      permissions.value = savedPermissions ? JSON.parse(savedPermissions) : []
      roles.value = savedRoles ? JSON.parse(savedRoles) : []
    }
  }

  /**
   * 设置加载状态
   */
  const setLoading = (status) => {
    loading.value = status
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    permissions,
    roles,
    loading,
    
    // Getters
    isLoggedIn,
    isSuperAdmin,
    isAdmin,
    userInfo,
    
    // Actions
    login,
    logout,
    updateProfile,
    changePassword,
    refreshTokenAction,
    checkPermission,
    checkRole,
    initializeFromStorage,
    setLoading
  }
})