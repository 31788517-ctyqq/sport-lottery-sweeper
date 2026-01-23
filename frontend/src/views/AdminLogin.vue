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
            name="username"
            v-model="credentials.username" 
            placeholder="请输入管理员用户名"
            required
            autocomplete="username"
          />
        </div>
        
        <div class="input-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            name="password"
            v-model="credentials.password" 
            placeholder="请输入管理员密码"
            required
            autocomplete="current-password"
          />
        </div>
        
        <div class="input-group checkbox-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              id="rememberMe"
              name="rememberMe"
              v-model="credentials.rememberMe"
              autocomplete="off"
            />
            <span>记住我</span>
          </label>
          
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              id="rememberPassword"
              name="rememberPassword"
              v-model="credentials.rememberPassword"
              :disabled="!credentials.rememberMe"
              autocomplete="off"
            />
            <span :class="{ 'disabled': !credentials.rememberMe }">记住密码</span>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

export default {
  name: 'AdminLogin',
  setup() {
    const router = useRouter()
    const adminStore = useAdminStore()

    const credentials = ref({
      username: '',
      password: '',
      rememberMe: false,
      rememberPassword: false
    })

    const loading = ref(false)
    const error = ref('')

    // 页面加载时恢复记住的凭据
    onMounted(() => {
      const savedCredentials = localStorage.getItem('admin_login_credentials')
      if (savedCredentials) {
        try {
          const parsed = JSON.parse(savedCredentials)
          credentials.value.username = parsed.username || ''
          if (parsed.rememberPassword) {
            credentials.value.password = parsed.password || ''
            credentials.value.rememberPassword = true
          }
          credentials.value.rememberMe = parsed.rememberMe || false
        } catch (e) {
          console.error('Failed to parse saved credentials:', e)
        }
      }
    })

    const handleLogin = async () => {
      loading.value = true
      error.value = ''

      if (!credentials.value.username || !credentials.value.password) {
        error.value = '请输入用户名和密码'
        loading.value = false
        return
      }

      try {
        const result = await adminStore.login({
          username: credentials.value.username,
          password: credentials.value.password,
          rememberMe: credentials.value.rememberMe
        })
        if (result.success) {
          // 如果用户选择了记住密码，保存凭据
          if (credentials.value.rememberMe && credentials.value.rememberPassword) {
            const credentialsToSave = {
              username: credentials.value.username,
              password: credentials.value.password,
              rememberMe: true,
              rememberPassword: true
            }
            localStorage.setItem('admin_login_credentials', JSON.stringify(credentialsToSave))
          } else {
            // 否则清除已保存的凭据
            localStorage.removeItem('admin_login_credentials')
          }
          router.push('/admin/dashboard')
        } else {
          error.value = '登录失败，请检查用户名和密码'
        }
      } catch (err) {
        error.value = err.message || '登录失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    return {
      credentials,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  padding: 20px;
  box-sizing: border-box;
}

.login-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  width: 100%;
  max-width: 420px;
  padding: 40px;
  color: #303133;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-section h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #409EFF;
  text-align: center;
}

.logo-section p {
  color: #909399;
  font-size: 14px;
  text-align: center;
  margin: 0;
}

.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 20px;
}

.input-group {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 6px;
}

.input-group input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  background: #fff;
  color: #303133;
  font-size: 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.input-group input:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
  gap: 16px;
  width: 100%;
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  flex: 1;
}

.checkbox-label:first-child {
  justify-content: flex-start;
}

.checkbox-label:last-child {
  justify-content: flex-end;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #409EFF;
}

.checkbox-label .disabled {
  color: #bbb;
}

.login-btn {
  background: #409EFF;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
  margin-top: 8px;
}

.login-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.login-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.error-message {
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.2);
  color: #f56c6c;
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
  border-top: 1px solid #ebeef5;
  width: 100%;
}

.footer-info p {
  color: #909399;
  font-size: 12px;
  margin: 0;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
}
</style>