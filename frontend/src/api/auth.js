import axios from 'axios'
import { ElMessage } from 'element-plus'
import { mockLogin, mockLogout, mockGetUserInfo } from './mock/auth.js'

// 环境变量控制是否使用mock
const USE_MOCK = true // 设置为true来使用mock，避免后端500错误

// 使用环境变量或配置文件中的API地址
const API_BASE_URL = ''

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 认证相关API
const authAPI = USE_MOCK ? {
  // 使用Mock API
  // 用户登录
  login: (credentials) => {
    console.log('Using MOCK login API')
    return mockLogin(credentials)
  },
  
  // 用户登出
  logout: () => {
    return mockLogout()
  },
  
  // 获取用户信息
  getUserInfo: () => {
    return mockGetUserInfo()
  },
  
  // 刷新令牌 (Mock)
  refreshToken: (refreshToken) => {
    return Promise.resolve({ code: 200, message: "刷新成功", data: { access_token: "new-mock-token" } })
  }
} : {
  // 使用真实API
  login: (credentials) => {
    return apiClient.post('/api/v1/auth/login', credentials)
  },
  
  logout: () => {
    return apiClient.post('/api/v1/auth/logout')
  },
  
  getUserInfo: (userId) => {
    return apiClient.get(`/api/v1/users/${userId}`)
  },
  
  refreshToken: (refreshToken) => {
    return apiClient.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
  }
}

// 用户管理API (保持原有代码)
const userAPI = {
  getUserInfo: (userId) => {
    return apiClient.get(`/api/v1/users/${userId}`)
  },
  updateUserInfo: (userId, userData) => {
    return apiClient.put(`/api/v1/users/${userId}`, userData)
  },
  getUsers: (params) => {
    return apiClient.get('/api/v1/users/', { params })
  }
}

// 管理员用户API (保持原有代码)
const adminAPI = {
  createAdmin: (adminData) => {
    return apiClient.post('/api/v1/users/admin', adminData)
  },
  getAdmins: (params) => {
    return apiClient.get('/api/v1/users/admin', { params })
  },
  getAdminInfo: (adminId) => {
    return apiClient.get(`/api/v1/users/admin/${adminId}`)
  }
}

export { authAPI, userAPI, adminAPI }
export default apiClient
