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
        <div class="logo">
          <el-icon class="logo-icon"><Trophy /></el-icon>
        </div>
        <h2>体育彩票扫盘系统</h2>
        <p>Intelligent Sports Lottery Analysis Platform</p>
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

        <el-form-item prop="captcha">
          <div class="captcha-container">
            <el-input 
              v-model="loginForm.captcha" 
              name="captcha"
              placeholder="验证码"
              size="large"
              prefix-icon="Key"
              clearable
              style="flex: 1; margin-right: 12px;"
            />
            <div class="captcha-image" @click="refreshCaptcha" role="button" aria-label="刷新验证码" tabindex="0" @keyup.enter="refreshCaptcha">
              <canvas ref="captchaCanvas" width="120" height="40" aria-label="验证码图像" role="img"></canvas>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
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
import { Trophy, User, Lock, Key, Loading } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref()
const captchaCanvas = ref()
const loading = ref(false)

// Login form data
const loginForm = reactive({
  username: '',
  password: '',
  captcha: ''
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
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码长度为4位', trigger: 'blur' }
  ]
}

// Generate captcha
const generateCaptcha = () => {
  const canvas = captchaCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'
  let captcha = ''
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw background
  ctx.fillStyle = '#f8f9fa'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  // Draw random lines
  for (let i = 0; i < 5; i++) {
    ctx.strokeStyle = `rgb(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)})`
    ctx.beginPath()
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height)
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height)
    ctx.stroke()
  }
  
  // Generate captcha text
  for (let i = 0; i < 4; i++) {
    const char = chars.charAt(Math.floor(Math.random() * chars.length))
    captcha += char
    
    ctx.font = `${16 + Math.random() * 8}px Arial`
    ctx.fillStyle = `rgb(${Math.floor(Math.random() * 100)}, ${Math.floor(Math.random() * 100)}, ${Math.floor(Math.random() * 100)})`
    ctx.textBaseline = 'middle'
    ctx.save()
    ctx.translate(30 * i + 15, 20)
    ctx.rotate((Math.random() - 0.5) * 0.4)
    ctx.fillText(char, -8, 0)
    ctx.restore()
  }
  
  // Store captcha for validation (in real app, store in session)
  canvas.dataset.captcha = captcha.toLowerCase()
}

// Refresh captcha
const refreshCaptcha = () => {
  generateCaptcha()
}

// Fill demo account
const fillDemoAccount = (username, password) => {
  loginForm.username = username
  loginForm.password = password
  loginForm.captcha = '' // 清空验证码，让用户重新输入
  generateCaptcha()
}

// Handle forgot password
const handleForgotPassword = () => {
  ElMessage.info('忘记密码功能正在开发中')
}

// Handle login
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 如果是自动登录且验证码为空，先填充当前验证码
    if (loginForm.autoLoginAttempt) {
      // 获取当前验证码
      const canvas = captchaCanvas.value;
      if (canvas && canvas.dataset.captcha) {
        // 自动填充当前验证码
        loginForm.captcha = canvas.dataset.captcha.substring(0, 4); // 取前4位作为验证码
      }
      // 重置标志
      loginForm.autoLoginAttempt = false;
    }
    
    await loginFormRef.value.validate()
    
    // Validate captcha
    const canvas = captchaCanvas.value
    if (!canvas || !canvas.dataset.captcha) {
      ElMessage.error('验证码已过期，请刷新')
      return
    }
    
    if (loginForm.captcha.toLowerCase() !== canvas.dataset.captcha) {
      ElMessage.error('验证码错误')
      generateCaptcha()
      loginForm.captcha = ''
      return
    }
    
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
      // 重新生成验证码，但不清除用户输入
      generateCaptcha()
      loginForm.captcha = '' // 只清除验证码，保留用户名和密码
    }
    
  } catch (error) {
    console.error('Login validation failed:', error)
    // 发生错误时也不清空表单
    generateCaptcha()
    loginForm.captcha = '' // 只清除验证码
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  generateCaptcha()
  
  // 如果启用了记住我，且有记住的用户名和密码，则自动登录
  if (loginForm.rememberMe && loginForm.username && loginForm.password) {
    // 设置标志表示这是自动登录尝试
    loginForm.autoLoginAttempt = true;
    // 延迟执行自动登录，确保验证码已生成
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

.logo {
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 40px;
  color: #409eff;
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

.captcha-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.captcha-image {
  cursor: pointer;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.captcha-image canvas {
  display: block;
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
  .captcha-container {
    flex-direction: column;
    gap: 10px;
  }
}
</style>