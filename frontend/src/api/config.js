/**
 * 后端API配置
 * 后端服务地址: 使用环境变量 VITE_API_BASE_URL (默认: http://localhost:3000/api)
 * 前端开发服务器: http://localhost:3000
 */

// 开发环境配置
const DEVELOPMENT_CONFIG = {
  // 强制使用空字符串，通过 Vite proxy 转发到后端，避免重复/api路径
  BASE_URL: '',
  
  // API版本前缀 - 不需要，由Vite proxy处理
  API_PREFIX: ''
  
  // 超时时间（毫秒）
  TIMEOUT: 10000,
  
  // 跨域配置
  CORS: {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    }
  }
}

// 生产环境配置（待部署时修改）
const PRODUCTION_CONFIG = {
  BASE_URL: 'http://your-production-domain.com',
  API_PREFIX: '/api',
  TIMEOUT: 10000,
  CORS: {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    }
  }
}

// 根据环境选择配置
const isDevelopment = process.env.NODE_ENV === 'development'
const API_CONFIG = isDevelopment ? DEVELOPMENT_CONFIG : PRODUCTION_CONFIG

// 导出API端点配置
const API_ENDPOINTS = {
  // 健康检查
  HEALTH: {
    LIVE: `${API_CONFIG.BASE_URL}/health/live`,
    READY: `${API_CONFIG.BASE_URL}/health/ready`,
    API: `${API_CONFIG.BASE_URL}/api/health`
  },
  
  // 认证相关
  AUTH: {
    LOGIN_V1: `${API_CONFIG.BASE_URL}/api/auth/login`,
    REGISTER_V1: `${API_CONFIG.BASE_URL}/api/register`,
    ME_V1: `${API_CONFIG.BASE_URL}/api/me`,
    LOGIN_COMPAT: `${API_CONFIG.BASE_URL}/api/auth/login`,
    PROFILE_COMPAT: `${API_CONFIG.BASE_URL}/api/auth/profile`
  },
  
  // 仪表板
  DASHBOARD: {
    SUMMARY: `${API_CONFIG.BASE_URL}/api/dashboard/summary`
  },
  
  // 情报系统
  INTELLIGENCE: {
    SCREENING_LIST: `${API_CONFIG.BASE_URL}/api/intelligence/screening/list`
  }
}

// 导出配置
export default {
  ...API_CONFIG,
  ENDPOINTS: API_ENDPOINTS
}