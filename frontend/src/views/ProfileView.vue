<template>
  <div class="profile-view">
    <div class="profile-header">
      <div class="avatar-container">
        <img :src="avatarUrl" alt="头像" class="avatar">
        <button class="change-avatar-btn" @click="changeAvatar">
          <i class="fas fa-camera"></i>
        </button>
      </div>
      <div class="user-info">
        <h2 class="username">{{ userData.username }}</h2>
        <p class="user-level">{{ userData.level }}</p>
        <p class="user-id">ID: {{ userData.userId }}</p>
      </div>
    </div>
    
    <div class="profile-stats">
      <div class="stat-item">
        <div class="stat-label">注册日期</div>
        <div class="stat-value">{{ userData.registerDate }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">使用时长</div>
        <div class="stat-value">{{ userData.usageDuration || '128天' }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">总浏览数</div>
        <div class="stat-value">{{ userData.totalViews.toLocaleString() }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">预测准确率</div>
        <div class="stat-value">{{ userData.correctPredictions }}%</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">连续签到</div>
        <div class="stat-value">{{ userData.streakDays }}天</div>
      </div>
    </div>
    
    <div class="profile-settings">
      <h3>账户设置</h3>
      
      <div class="setting-item">
        <span>推送通知</span>
        <SwitchButton v-model="userData.settings.notifications" @change="toggleSetting('notifications')" />
      </div>
      
      <div class="setting-item">
        <span>深色模式</span>
        <SwitchButton v-model="userData.settings.darkMode" @change="toggleSetting('darkMode')" />
      </div>
    </div>
    
    <div class="profile-actions">
      <button class="action-btn clear-cache" @click="clearCache">
        <i class="fas fa-trash-alt"></i>
        <span>清除缓存</span>
      </button>
      <button class="action-btn logout" @click="logout">
        <i class="fas fa-sign-out-alt"></i>
        <span>退出登录</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SwitchButton from '@/components/common/SwitchButton.vue' // 假设有这个组件

const router = useRouter()

const userData = ref({
  username: '竞彩玩家',
  userId: 'JC2026001',
  level: 'VIP 3级会员',
  avatarSeed: 'default',
  registerDate: '2026-01-01',
  totalViews: 1248,
  correctPredictions: 68,
  streakDays: 7,
  settings: {
    notifications: true,
    darkMode: true
  }
})

const avatarUrl = ref('')

const updateAvatar = () => {
  avatarUrl.value = `https://api.dicebear.com/7.x/avataaars/svg?seed=${userData.value.avatarSeed}`
}

const changeAvatar = () => {
  userData.value.avatarSeed = Math.random().toString(36).substring(7)
  updateAvatar()
  localStorage.setItem('avatarSeed', userData.value.avatarSeed)
}

const toggleSetting = (settingName) => {
  localStorage.setItem(settingName, userData.value.settings[settingName])
}

const clearCache = () => {
  if (confirm('确定要清除所有缓存数据吗？')) {
    localStorage.clear()
    // 重置部分用户数据
    userData.value.username = '竞彩玩家'
    userData.value.userId = 'JC2026001'
    userData.value.level = 'VIP 3级会员'
    userData.value.avatarSeed = 'default'
    updateAvatar()
    alert('缓存已清除')
  }
}

const logout = () => {
  if (confirm('确定要退出登录吗？')) {
    localStorage.removeItem('auth_token')
    router.push('/login')
  }
}

// 初始化数据
onMounted(() => {
  // 从本地存储加载用户数据
  const storedAvatarSeed = localStorage.getItem('avatarSeed')
  if (storedAvatarSeed) {
    userData.value.avatarSeed = storedAvatarSeed
  }
  
  const storedNotifications = localStorage.getItem('notifications')
  if (storedNotifications !== null) {
    userData.value.settings.notifications = storedNotifications === 'true'
  }
  
  const storedDarkMode = localStorage.getItem('darkMode')
  if (storedDarkMode !== null) {
    userData.value.settings.darkMode = storedDarkMode === 'true'
  }
  
  updateAvatar()
})
</script>

<style scoped>
.profile-view {
  padding: 16px;
  background: var(--bg-body);
  min-height: 100%;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  background: var(--bg-card);
  border-radius: 12px;
  margin-bottom: 16px;
}

.avatar-container {
  position: relative;
  margin-bottom: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.user-info {
  text-align: center;
}

.username {
  color: var(--text-main);
  margin: 0 0 4px;
  font-size: 18px;
}

.user-level {
  color: var(--primary);
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
}

.user-id {
  color: var(--text-sub);
  margin: 0;
  font-size: 12px;
}

.profile-stats {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: var(--text-sub);
}

.stat-value {
  color: var(--text-main);
  font-weight: 600;
}

.profile-settings {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.profile-settings h3 {
  color: var(--text-main);
  margin: 0 0 16px;
  font-size: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 8px;
  border: none;
  background: var(--bg-card);
  color: var(--text-main);
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.action-btn.clear-cache {
  color: var(--text-main);
}

.action-btn.logout {
  color: var(--danger);
}
</style>