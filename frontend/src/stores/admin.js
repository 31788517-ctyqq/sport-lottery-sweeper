import { defineStore } from 'pinia';
import { ref } from 'vue';
import request from '@/utils/request';
import { useUserStore } from '@/stores/user';

export const useAdminStore = defineStore('admin', () => {
  // 状态 - 不再使用持久化存储，仅内存存储
  const token = ref('');
  const user = ref(null);
  const isAuthenticated = ref(false);
  const rememberMe = ref(false);

  console.log('[Admin Store] 初始化状态:', {
    hasToken: !!token.value,
    isAuthenticated: isAuthenticated.value,
    user: user.value
  });

  // 动作
  const login = async (credentials) => {
    try {
      console.log('[Admin Login] 开始登录请求:', credentials.username);
      
      // 调用后端登录API - 使用配置好的request实例
      console.log('[Admin Login] 请求路径: /api/v1/auth/login');

      const response = await request.post('/api/v1/auth/login', {
        username: credentials.username,
        password: credentials.password
      });

      console.log('[Admin Login] 收到响应:', response);

      if (response && response.code === 200) {
        const { access_token, user_info } = response.data;
        
        // 保存token到本地存储
        token.value = access_token;
        localStorage.setItem('admin_token', access_token);
        
        // 保存用户信息到本地存储
        user.value = user_info;
        localStorage.setItem('admin_user', JSON.stringify(user_info));
        
        // 更新认证状态
        isAuthenticated.value = true;

        // 同时更新user store以兼容路由守卫
        try {
          const userStore = useUserStore();
          userStore.setToken(access_token);
          userStore.setUserInfo(user_info);
          userStore.isAuthenticated = true;
          console.log('[Admin Login] User store已更新');
        } catch (err) {
          console.warn('[Admin Login] 更新user store时出错:', err);
        }
        
        console.log('[Admin Login] 登录成功, 状态已更新:', {
          hasToken: !!token.value,
          isAuthenticated: isAuthenticated.value,
          user: user.value
        });
        
        // 自动登录功能已移除，不保存任何登录凭据

        return { success: true };
      } else {
        throw new Error(response.message || '登录失败');
      }
    } catch (error) {
      console.error('[Admin Login] 登录错误详情:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: error.config?.url
      });
      
      // 如果是HTTP错误，尝试获取错误信息
      if (error.response) {
        const errorMsg = error.response.data?.message || 
                        error.response.data?.detail || 
                        `服务器错误 (${error.response.status})`;
        throw new Error(errorMsg);
      } else if (error.request) {
        throw new Error('网络错误，请检查连接');
      } else {
        throw new Error(error.message || '登录过程中发生错误');
      }
    }
  };

  const logout = () => {
    console.log('[Admin Store] 执行登出');
    
    token.value = '';
    user.value = null;
    isAuthenticated.value = false;
    rememberMe.value = false;
    
    // 清除本地存储
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    // 登出时不清除 remember 信息，以便下次登录时可以自动填充

    // 同时清除user store
    try {
      const userStore = useUserStore();
      userStore.clear();
      console.log('[Admin Store] User store已清除');
    } catch (err) {
      console.warn('[Admin Store] 清除user store时出错:', err);
    }
    
    // 跳转到登录页面
    window.location.href = '/admin/login';
  };

  const initializeAuth = () => {
    const storedToken = localStorage.getItem('admin_token');
    if (storedToken) {
      token.value = storedToken;
      isAuthenticated.value = true;

      // 同时初始化user store
      try {
        const userStore = useUserStore();
        userStore.setToken(storedToken);
        
        // 尝试从localStorage获取用户信息
        const storedUser = localStorage.getItem('admin_user');
        if (storedUser) {
          try {
            const userInfo = JSON.parse(storedUser);
            userStore.setUserInfo(userInfo);
            userStore.isAuthenticated = true;
            console.log('[Admin Store] User store已从localStorage初始化');
          } catch (parseErr) {
            console.warn('[Admin Store] 解析用户信息时出错:', parseErr);
          }
        }
      } catch (err) {
        console.warn('[Admin Store] 初始化user store时出错:', err);
      }
    }
  };

  const refreshToken = async () => {
    try {
      // 调用后端刷新token的API
      const response = await request.post('/api/v1/auth/refresh');

      if (response && response.code === 200) {
        const { access_token } = response.data;

        token.value = access_token;
        localStorage.setItem('admin_token', access_token);

        return true;
      }
    } catch (error) {
      console.error('Refresh token failed:', error);
      logout();
      return false;
    }
  };

  // 获取记住的登录信息
  const getRememberedCredentials = () => {
    try {
      const stored = localStorage.getItem('admin_remember');
      if (stored) {
        const rememberData = JSON.parse(stored);
        rememberMe.value = true;
        return {
          username: rememberData.username,
          password: rememberData.password
        };
      }
    } catch (e) {
      console.warn('获取记住的登录信息失败:', e);
    }
    return null;
  };

  // 清除记住的登录信息
  const clearRememberedCredentials = () => {
    localStorage.removeItem('admin_remember');
    rememberMe.value = false;
  };

  return {
    token,
    user,
    isAuthenticated,
    rememberMe,
    login,
    logout,
    initializeAuth,
    refreshToken,
    getRememberedCredentials,
    clearRememberedCredentials
  };
});