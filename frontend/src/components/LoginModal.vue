<template>
  <div class="modal" v-if="showModal" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>登录 / 注册</h3>
        <button class="modal-close" @click="closeModal">&times;</button>
      </div>
      <div class="modal-body">
        <div class="login-tabs">
          <button 
            class="login-tab" 
            :class="{ active: activeTab === 'login' }"
            @click="switchTab('login')"
          >
            登录
          </button>
          <button 
            class="login-tab" 
            :class="{ active: activeTab === 'register' }"
            @click="switchTab('register')"
          >
            注册
          </button>
        </div>
        
        <div class="login-form" :class="{ active: activeTab === 'login' }">
          <div class="form-group">
            <label for="loginUsername">用户名</label>
            <input 
              type="text" 
              id="loginUsername" 
              v-model="loginForm.username"
              placeholder="请输入用户名"
            >
          </div>
          <div class="form-group">
            <label for="loginPassword">密码</label>
            <input 
              type="password" 
              id="loginPassword" 
              v-model="loginForm.password"
              placeholder="请输入密码"
            >
          </div>
          <button class="btn-primary" @click="handleLogin">登录</button>
          <p class="form-note">演示账号: demo / demo123</p>
        </div>
        
        <div class="login-form" :class="{ active: activeTab === 'register' }">
          <div class="form-group">
            <label for="registerUsername">用户名</label>
            <input 
              type="text" 
              id="registerUsername" 
              v-model="registerForm.username"
              placeholder="请输入用户名"
            >
          </div>
          <div class="form-group">
            <label for="registerPassword">密码</label>
            <input 
              type="password" 
              id="registerPassword" 
              v-model="registerForm.password"
              placeholder="请输入密码"
            >
          </div>
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input 
              type="password" 
              id="confirmPassword" 
              v-model="registerForm.confirmPassword"
              placeholder="请再次输入密码"
            >
          </div>
          <div class="form-group">
            <label for="email">邮箱</label>
            <input 
              type="email" 
              id="email" 
              v-model="registerForm.email"
              placeholder="请输入邮箱"
            >
          </div>
          <button class="btn-primary" @click="handleRegister">注册</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useAppStore } from '@/stores';

export default {
  name: 'LoginModal',
  setup() {
    const store = useAppStore();
    
    const showModal = computed(() => store.showLoginModal);
    const activeTab = ref('login');
    
    const loginForm = ref({
      username: '',
      password: ''
    });
    
    const registerForm = ref({
      username: '',
      password: '',
      confirmPassword: '',
      email: ''
    });
    
    const switchTab = (tab) => {
      activeTab.value = tab;
    };
    
    const closeModal = () => {
      store.setShowLoginModal(false);
      // 重置表单
      loginForm.value = { username: '', password: '' };
      registerForm.value = { username: '', password: '', confirmPassword: '', email: '' };
    };
    
    const handleLogin = () => {
      const { username, password } = loginForm.value;
      
      if (!username || !password) {
        alert('请输入用户名和密码');
        return;
      }
      
      // 模拟登录
      if (username === 'demo' && password === 'demo123') {
        store.updateUserData({ 
          ...store.userData,
          isLoggedIn: true,
          username: username,
          avatarSeed: username,
          userId: `USER${Math.floor(Math.random() * 10000)}`,
          level: 'VIP 1级会员'
        });
        
        closeModal();
        alert('登录成功！');
      } else {
        // 演示模式，随便输入都能"登录"
        store.updateUserData({ 
          ...store.userData,
          isLoggedIn: true,
          username: username,
          avatarSeed: username,
          userId: `USER${Math.floor(Math.random() * 10000)}`,
          level: '普通会员'
        });
        
        closeModal();
        alert('登录成功！(演示模式)');
      }
    };
    
    const handleRegister = () => {
      const { username, password, confirmPassword, email } = registerForm.value;
      
      if (!username || !password || !confirmPassword || !email) {
        alert('请填写所有必填项');
        return;
      }
      
      if (password !== confirmPassword) {
        alert('两次输入的密码不一致');
        return;
      }
      
      if (password.length < 6) {
        alert('密码长度至少6位');
        return;
      }
      
      // 模拟注册
      store.updateUserData({ 
        ...store.userData,
        isLoggedIn: true,
        username: username,
        avatarSeed: username,
        userId: `USER${Math.floor(Math.random() * 10000)}`,
        level: '新会员',
        registerDate: new Date().toISOString().split('T')[0]
      });
      
      closeModal();
      alert('注册成功！欢迎使用');
    };
    
    return {
      showModal,
      activeTab,
      loginForm,
      registerForm,
      switchTab,
      closeModal,
      handleLogin,
      handleRegister
    };
  }
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background: var(--bg-card);
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 18px;
  color: var(--text-main);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-sub);
  font-size: 24px;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:active {
  color: var(--text-main);
}

.modal-body {
  padding: 20px;
}

.login-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 4px;
}

.login-tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: var(--text-sub);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.login-tab.active {
  background: var(--primary);
  color: white;
}

.login-form {
  display: none;
}

.login-form.active {
  display: block;
  animation: fadeIn 0.3s ease-out;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: var(--text-main);
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
  font-size: 15px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary);
}

.btn-primary {
  width: 100%;
  padding: 16px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:active {
  background: var(--primary-hover);
  transform: scale(0.98);
}

.form-note {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-sub);
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.slide-in {
  animation: slideIn 0.3s ease-out;
}
</style>