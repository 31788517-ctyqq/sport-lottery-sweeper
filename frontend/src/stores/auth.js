import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, userAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => {
    // 检查用户角色 - API返回的是roles数组而不是单个role字段
    if (user.value && user.value.roles) {
      return user.value.roles.includes('admin') || user.value.roles.includes('super_admin')
    }
    return false
  })
  const userInfo = computed(() => user.value)

  // 登录动作
  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await authAPI.login(credentials)
      
      // 处理嵌套响应结构 {code, message, data}
      let loginData;
      if (response && response.code === 200 && response.data) {
        // 嵌套结构：{code: 200, message: "...", data: {...}}
        loginData = response.data;
      } else if (response && response.access_token) {
        // 扁平结构：{access_token: "...", ...}
        loginData = response;
      } else {
        // 如果响应格式不符合预期，抛出错误
        throw new Error('登录响应格式错误');
      }
      
      if (loginData && loginData.access_token) {
        const { access_token, refresh_token, user_info } = loginData
        
        // 保存token和用户信息 - 统一使用access_token作为标准键名
        token.value = access_token
        refreshToken.value = refresh_token || ''  // refresh_token可能不存在
        user.value = user_info
        
        localStorage.setItem('access_token', access_token)
        // 同时保存token键名以确保向后兼容
        localStorage.setItem('token', access_token)
        if (refresh_token) {
          localStorage.setItem('refresh_token', refresh_token)
        }
        
        ElMessage.success('登录成功')
        return { success: true, data: loginData }
      } else {
        // 如果响应格式不符合预期，抛出错误
        throw new Error('登录响应格式错误');
      }
    } catch (error) {
      console.error('Login error:', error)
      // 检查错误类型，如果是网络错误或其他非业务错误
      let errorMessage = '登录失败'
      if (error.response) {
        // 服务器响应了错误状态码
        errorMessage = error.response.data?.message || `登录失败: ${error.response.status}`
      } else if (error.request) {
        // 请求发出但没有收到响应
        errorMessage = '网络错误，请检查后端服务是否正常'
      } else {
        // 其他错误
        errorMessage = error.message || '登录失败'
      }
      ElMessage.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // 注册动作
  const register = async (userData) => {
    isLoading.value = true
    try {
      // authAPI中没有register函数，暂时使用mock实现或提示功能暂不可用
      // 实际实现需要在auth.js中添加相应的API调用
      console.warn('Register API not implemented yet')
      throw new Error('注册功能暂不可用')
    } catch (error) {
      console.error('Register error:', error)
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // 登出动作
  const logout = async () => {
    try {
      // 这里可以添加调用后端登出API的逻辑
      token.value = null
      refreshToken.value = null
      user.value = null
      
      localStorage.removeItem('access_token')
      // 同时移除旧的token键名（如果存在）
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      
      ElMessage.success('已退出登录')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!token.value) return
    
    try {
      const response = await userAPI.getUserInfo('me') // 假设后端支持 'me' 来获取当前用户
      if (response && response.code === 200) {
        user.value = response.data
      }
    } catch (error) {
      console.error('Fetch user info error:', error)
      // 如果获取用户信息失败，可能是token过期
      if (error.response?.status === 401) {
        logout()
      }
    }
  }

  // 刷新token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      logout()
      return false
    }
    
    try {
      const response = await authAPI.refreshToken(refreshToken.value)
      
      if (response && response.code === 200) {
        const { access_token, refresh_token: new_refresh_token } = response.data
        token.value = access_token
        refreshToken.value = new_refresh_token
        
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('token', access_token)
        localStorage.setItem('refresh_token', new_refresh_token)
        
        return true
      } else {
        logout()
        return false
      }
    } catch (error) {
      console.error('Refresh token error:', error)
      logout()
      return false
    }
  }

  // 初始化认证状态
  const initializeAuth = async () => {
    if (token.value) {
      await fetchUserInfo()
    }
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    userInfo,
    
    // 动作
    login,
    register,
    logout,
    fetchUserInfo,
    refreshAccessToken,
    initializeAuth
  }
})