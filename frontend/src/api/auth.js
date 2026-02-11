import { request } from '@/utils/http'
import { ElMessage } from 'element-plus'
import { mockLogin, mockLogout, mockGetUserInfo } from './mock/auth.js'

// 环境变量控制是否使用mock
const USE_MOCK = false // 设置为false来使用真实API

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
  login: async (credentials) => {
    try {
      console.log('Sending login request to /api/v1/login with credentials:', credentials);
      // 使用带拦截器的request实例
      const response = await request.post('/api/v1/login', credentials);
      console.log('Login response received:', response);
      
      // 将扁平结构转换为前端期望的嵌套结构
      const nestedResponse = {
        code: 200,
        message: "登录成功",
        data: {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
          token_type: response.token_type,
          expires_in: response.expires_in,
          user_info: response.user_info
        }
      };
      
      return nestedResponse;
    } catch (error) {
      console.error('Login request failed:', error);
      // 重新抛出错误，让调用者处理
      throw error;
    }
  },
  
  logout: () => {
    return request.post('/api/v1/logout')
  },
  
  getUserInfo: (userId) => {
    return request.get(`/api/v1/users/${userId}`)
  },
  
  refreshToken: (refreshToken) => {
    return request.post('/api/v1/refresh', { refresh_token: refreshToken })
  }
}

// 用户管理API (保持原有代码)
const userAPI = {
  getUserInfo: (userId) => {
    return request.get(`/api/v1/users/${userId}`)
  },
  updateUserInfo: (userId, userData) => {
    return request.put(`/api/v1/users/${userId}`, userData)
  },
  getUsers: (params) => {
    return request.get('/api/v1/users/', { params })
  }
}

// 管理员用户API (保持原有代码)
const adminAPI = {
  createAdmin: (adminData) => {
    return request.post('/api/v1/users/admin', adminData)
  },
  getAdmins: (params) => {
    return request.get('/api/v1/users/admin', { params })
  },
  getAdminInfo: (adminId) => {
    return request.get(`/api/v1/users/admin/${adminId}`)
  }
}

export { authAPI, userAPI, adminAPI }
export default request