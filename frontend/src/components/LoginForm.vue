<template>
  <div class="login-form-container">
    <div class="login-card">
      <h2 class="login-title">体育彩票扫盘系统</h2>
      
      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="loginForm.email"
            type="email"
            placeholder="请输入邮箱"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="loading"
          />
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <!-- 登录按钮 -->
        <button 
          type="submit" 
          class="login-button"
          :disabled="loading"
        >
          <span v-if="loading">登录中...</span>
          <span v-else>登录</span>
        </button>
      </form>

      <!-- 服务状态检查 -->
      <div class="service-status">
        <button @click="checkServiceHealth" class="status-button">
          检查服务状态
        </button>
        <div v-if="serviceStatus" class="status-info">
          <span :class="['status-indicator', serviceStatus.status === 'healthy' ? 'healthy' : 'unhealthy']">
            ●
          </span>
          {{ serviceStatus.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { loginUser, checkServiceHealth } from '@/api/example.js'

// 响应式数据
const loading = ref(false)
const errorMessage = ref('')
const serviceStatus = ref(null)

// 登录表单数据
const loginForm = reactive({
  email: '',
  password: ''
})

// 登录处理函数
const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const result = await loginUser(loginForm.email, loginForm.password)
    
    if (result.code === 200) {
      console.log('登录成功:', result.data)
      // 这里可以存储token或跳转到首页
      localStorage.setItem('user_token', result.data.access_token)
      localStorage.setItem('user_info', JSON.stringify(result.data.user_info))
      
      // 触发登录成功事件
      emit('login-success', result.data)
    } else {
      errorMessage.value = result.message || '登录失败'
    }
  } catch (error) {
    console.error('登录错误:', error)
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

// 检查服务状态
const checkServiceHealth = async () => {
  try {
    const status = await checkServiceHealth()
    serviceStatus.value = status
    console.log('服务状态:', status)
  } catch (error) {
    serviceStatus.value = {
      status: 'unhealthy',
      service: 'sport-lottery-sweeper',
      message: `服务异常: ${error.message}`
    }
  }
}

// 定义事件
const emit = defineEmits(['login-success'])

// 组件挂载时检查服务状态
setTimeout(checkServiceHealth, 500)
</script>

<style scoped>
.login-form-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.login-form {
  width: 100%;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  border-left: 4px solid #c33;
}

.login-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.service-status {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.status-button {
  background: none;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
  font-size: 14px;
}

.status-button:hover {
  background-color: #f8f9fa;
}

.status-info {
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  font-size: 12px;
}

.status-indicator.healthy {
  color: #28a745;
}

.status-indicator.unhealthy {
  color: #dc3545;
}
</style>