<template>
  <div class="login-container">
    <!-- Background Animation -->
    <div class="login-background">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
    </div>

    <!-- Login Form Card -->
    <div class="login-card">
      <div class="login-header">
        <div class="login-title-row">
          <div class="logo">
            <div class="logo-icon" aria-hidden="true">
              <svg viewBox="0 0 64 64" role="img" focusable="false" aria-hidden="true">
                <circle cx="32" cy="32" r="28" fill="currentColor" opacity="0.12" />
                <circle cx="32" cy="32" r="22" fill="none" stroke="currentColor" stroke-width="3" />
                <path d="M32 18l8 6-3 9H27l-3-9 8-6z" fill="currentColor" />
                <path d="M20 34l7 5-3 9-8-6 4-8zM44 34l4 8-8 6-3-9 7-5z" fill="currentColor" />
                <path d="M27 41h10l3 9H24l3-9z" fill="currentColor" />
              </svg>
            </div>
          </div>
          <h2>足彩扫盘系统</h2>
        </div>
        <p>Sports Betting Analysis System</p>
      </div>

      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            name="username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            name="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item class="login-options-item">
          <div class="login-options">
            <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
            <el-link type="primary" :underline="'never'" class="forgot-password" @click="handleForgotPassword">忘记密码？</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Loading Overlay -->
      <div v-if="loading" class="loading-overlay">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span class="loading-text">登录中...</span>
      </div>
      
      <!-- Removed demo accounts section -->
    </div>

    <!-- Footer -->
    <div class="login-footer">
      <p>&copy; 2024 Sports Sweeper. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, Loading } from '@element-plus/icons-vue'  // 移除了Key图标

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref()
const loading = ref(false)

// Login form data
const loginForm = reactive({
  username: '',
  password: ''
})

// Form validation rules
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// Handle forgot password
const handleForgotPassword = () => {
  ElMessage.info('忘记密码功能正在开发中')
}

// Handle login
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // Prepare credentials for API
    // Backend expects 'username' and 'password' fields
    const credentials = {
      username: loginForm.username,  // Changed from email to username to match backend API
      password: loginForm.password
    }
    
    const result = await authStore.login(credentials)
    
    if (result.success) {
      // Redirect based on role
      if (authStore.isAdmin) {
        router.push('/admin/dashboard')
      } else {
        router.push('/admin/dashboard')
      }
    } else {
      // 登录失败时，只显示错误信息，不重置表单
      ElMessage.error(result.error || '登录失败')
    }
    
  } catch (error) {
    console.error('Login validation failed:', error)
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  // 如果启用了记住我，且有记住的用户名和密码，则自动登录
  if (loginForm.rememberMe && loginForm.username && loginForm.password) {
    // 延迟执行自动登录，确保页面已准备就绪
    setTimeout(() => {
      handleLogin()
    }, 500)
  }
})
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--sports-gradient-start, #667eea) 0%, var(--sports-gradient-end, #764ba2) 100%);
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 70%;
  right: 10%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.login-card {
  position: relative;
  z-index: 2;
  width: 400px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  padding: 32px;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 6px;
}

.logo {
  margin-bottom: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: #409eff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.logo-icon svg {
  width: 32px;
  height: 32px;
  display: block;
}

.login-header h2 {
  margin: 0 0 6px 0;
  color: #111827;
  font-size: 20px;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.login-form {
  margin-bottom: 16px;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
  transition: all 0.2s;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 2px;
}

.login-options-item :deep(.el-form-item__content) {
  width: 100%;
}

.forgot-password {
  font-size: 13px;
}

.login-btn {
  width: 100%;
  height: 40px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
}

:deep(.el-link.forgot-password .el-link--inner) {
  text-decoration: none;
}

.login-footer {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  text-align: center;
}

.login-footer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .login-card {
    width: 90%;
    max-width: 360px;
    padding: 24px;
  }
  .login-header h2 {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 20px 16px;
    margin: 0 12px;
  }
  .login-header h2 {
    font-size: 17px;
  }
  .logo-icon {
    font-size: 36px;
  }
  .login-btn {
    height: 38px;
    font-size: 14px;
  }
}
</style>