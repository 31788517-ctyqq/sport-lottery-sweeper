import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建axios实例用于管理员API
const adminApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
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
      // 重定向到登录页（如果在浏览器环境中）
      if (typeof window !== 'undefined') {
        window.location.href = '/admin/login';
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
    const response = await adminApi.post('/auth/login', credentials);
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
    const response = await adminApi.post('/auth/logout');
    return response;
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
    const response = await adminApi.post('/auth/refresh');
    return response;
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
    const response = await adminApi.get('/auth/me');
    return response.data;
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
    const response = await adminApi.put('/auth/me', data);
    return response.data;
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
    const response = await adminApi.post('/auth/change-password', data);
    return response;
  } catch (error) {
    console.error('更改管理员密码失败:', error);
    throw error;
  }
};