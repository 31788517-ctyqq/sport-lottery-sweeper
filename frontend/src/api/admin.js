import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建axios实例用于管理员API
const adminApi = axios.create({
  // 强制使用空字符串，通过 Vite proxy 转发到后端，避免重复/api路径
  baseURL: '',
  timeout: 10000,
});

// 请求拦截器
adminApi.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
adminApi.interceptors.response.use(
  (response) => {
    // 检查响应结构是否符合预期
    if (response.data.code === 200) {
      return response.data;
    } else {
      ElMessage.error(response.data.message || '请求失败');
      return Promise.reject(new Error(response.data.message || '请求失败'));
    }
  },
  (error) => {
    console.error('Admin API请求错误:', error);
    
    // 检查是否是认证错误
    if (error.response?.status === 401) {
      // 清除本地token
      localStorage.removeItem('admin_token');
      // 开发环境下跳过强制跳转，避免循环
      if (import.meta.env.MODE !== 'development') {
        // 重定向到登录页（如果在浏览器环境中）
        if (typeof window !== 'undefined') {
          window.location.href = '/admin/login';
        }
      } else {
        console.warn('🔧 开发模式：跳过admin.js 401跳转')
      }
    }
    
    ElMessage.error(error.message || '网络请求失败');
    return Promise.reject(error);
  }
);

/**
 * 管理员登录
 */
export const adminLogin = async (credentials) => {
  try {
    const response = await adminApi.post('/login', credentials);
    return response;
  } catch (error) {
    console.error('管理员登录失败:', error);
    throw error;
  }
};

/**
 * 管理员登出
 */
export const adminLogout = async () => {
  try {
    // 注意：后端可能未实现logout接口，这里仅作占位
    console.warn('Logout endpoint not implemented in backend');
    return Promise.resolve({ code: 200, message: 'success' });
  } catch (error) {
    console.error('管理员登出失败:', error);
    throw error;
  }
};

/**
 * 刷新管理员token
 */
export const refreshAdminToken = async () => {
  try {
    // 注意：后端可能未实现refresh接口，这里仅作占位
    console.warn('Refresh token endpoint not implemented in backend');
    return Promise.resolve({ code: 200, message: 'success' });
  } catch (error) {
    console.error('刷新管理员token失败:', error);
    throw error;
  }
};

/**
 * 获取管理员信息
 */
export const getAdminInfo = async () => {
  try {
    // 注意：后端可能未实现获取用户信息接口，返回模拟数据
    console.warn('Get admin info endpoint not implemented in backend');
    return Promise.resolve({ id: 1, username: 'admin', role: 'super_admin' });
  } catch (error) {
    console.error('获取管理员信息失败:', error);
    throw error;
  }
};

/**
 * 更新管理员信息
 */
export const updateAdminInfo = async (data) => {
  try {
    // 注意：后端可能未实现更新用户信息接口，这里仅作占位
    console.warn('Update admin info endpoint not implemented in backend');
    return Promise.resolve({ code: 200, message: 'success' });
  } catch (error) {
    console.error('更新管理员信息失败:', error);
    throw error;
  }
};

/**
 * 更改管理员密码
 */
export const changeAdminPassword = async (data) => {
  try {
    // 注意：后端可能未实现更改密码接口，这里仅作占位
    console.warn('Change password endpoint not implemented in backend');
    return Promise.resolve({ code: 200, message: 'success' });
  } catch (error) {
    console.error('更改管理员密码失败:', error);
    throw error;
  }
};