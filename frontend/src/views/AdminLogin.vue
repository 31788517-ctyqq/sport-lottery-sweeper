<template>
  <div class="admin-login-container">
    <div class="login-card">
      <div class="logo-section">
        <h1>🏆 竞彩管理后台</h1>
        <p>数据审核与管理系统</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="credentials.username" 
            placeholder="请输入管理员用户名"
            required
          />
        </div>
        
        <div class="input-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="credentials.password" 
            placeholder="请输入管理员密码"
            required
          />
        </div>
        
        <div class="input-group checkbox-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="credentials.rememberMe"
            />
            <span>记住我</span>
          </label>
        </div>
        
        <button 
          type="submit" 
          class="login-btn"
          :disabled="loading"
        >
          <span v-if="!loading">登录</span>
          <span v-else class="loading-text">登录中...</span>
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
      
      <div class="footer-info">
        <p>© 2026 竞彩扫盘工具. 保留所有权利.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAdminStore } from '@/stores/admin';

export default {
  name: 'AdminLogin',
  setup() {
    const router = useRouter();
    const adminStore = useAdminStore();
    
    const credentials = ref({
      username: '',
      password: '',
      rememberMe: false
    });
    
    const loading = ref(false);
    const error = ref('');
    
    const handleLogin = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        // 调用登录API
        await adminStore.login(credentials.value);
        
        // 登录成功后跳转到管理首页
        router.push('/admin/dashboard');
      } catch (err) {
        error.value = err.message || '登录失败，请检查用户名和密码';
      } finally {
        loading.value = false;
      }
    };
    
    return {
      credentials,
      loading,
      error,
      handleLogin
    };
  }
};
</script>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
  padding: 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 420px;
  padding: 40px;
  color: #f0f6fc;
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo-section h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #58a6ff;
}

.logo-section p {
  color: #8b949e;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 14px;
  color: #c9d1d9;
  font-weight: 500;
}

.input-group input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid rgba(240, 246, 252, 0.1);
  background: rgba(0, 0, 0, 0.2);
  color: #f0f6fc;
  font-size: 16px;
  transition: all 0.2s;
}

.input-group input:focus {
  outline: none;
  border-color: #58a6ff;
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.2);
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.checkbox-group .checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #8b949e;
}

.checkbox-group input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #58a6ff;
}

.login-btn {
  background: #58a6ff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.login-btn:hover:not(:disabled) {
  background: #4c9aff;
}

.login-btn:disabled {
  background: #32383f;
  cursor: not-allowed;
}

.loading-text {
  display: inline-block;
  width: 40px;
  text-align: center;
}

.error-message {
  background: rgba(248, 81, 73, 0.2);
  border: 1px solid rgba(248, 81, 73, 0.3);
  color: #ff7b72;
  padding: 12px 16px;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  margin-top: 10px;
}

.footer-info {
  text-align: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(240, 246, 252, 0.1);
}

.footer-info p {
  color: #8b949e;
  font-size: 12px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
}
</style>