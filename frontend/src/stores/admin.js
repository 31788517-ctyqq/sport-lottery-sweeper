import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

export const useAdminStore = defineStore('admin', () => {
  // 状态
  const token = ref(localStorage.getItem('admin_token') || '');
  const user = ref(null);
  const isAuthenticated = ref(!!token.value);

  // 动作
  const login = async (credentials) => {
    try {
      // 调用后端登录API
      const response = await axios.post('/api/v1/auth/login', {
        username: credentials.username,
        password: credentials.password
      });

      if (response.data && response.data.code === 200) {
        const { access_token, user_info } = response.data.data;
        
        // 保存token到本地存储
        token.value = access_token;
        localStorage.setItem('admin_token', access_token);
        
        // 保存用户信息
        user.value = user_info;
        isAuthenticated.value = true;
        
        // 设置axios默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        return { success: true };
      } else {
        throw new Error(response.data.message || '登录失败');
      }
    } catch (error) {
      console.error('Admin login error:', error);
      
      // 如果是HTTP错误，尝试获取错误信息
      if (error.response) {
        throw new Error(error.response.data?.message || '服务器错误');
      } else if (error.request) {
        throw new Error('网络错误，请检查连接');
      } else {
        throw new Error(error.message || '登录过程中发生错误');
      }
    }
  };

  const logout = () => {
    token.value = '';
    user.value = null;
    isAuthenticated.value = false;
    
    // 清除本地存储
    localStorage.removeItem('admin_token');
    
    // 清除axios默认请求头
    delete axios.defaults.headers.common['Authorization'];
  };

  const initializeAuth = () => {
    const storedToken = localStorage.getItem('admin_token');
    if (storedToken) {
      token.value = storedToken;
      isAuthenticated.value = true;
      
      // 设置axios默认请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
  };

  const refreshToken = async () => {
    try {
      // 调用后端刷新token的API
      const response = await axios.post('/api/v1/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      });

      if (response.data && response.data.code === 200) {
        const { access_token } = response.data.data;
        
        token.value = access_token;
        localStorage.setItem('admin_token', access_token);
        
        // 更新axios请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        return true;
      }
    } catch (error) {
      console.error('Refresh token failed:', error);
      logout();
      return false;
    }
  };

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    initializeAuth,
    refreshToken
  };
});