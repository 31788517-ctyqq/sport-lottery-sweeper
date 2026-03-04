<template>
  <div class="profile-panel">
    <div class="profile-header">
      <div class="profile-avatar">
        <img :src="avatarUrl" alt="用户头像" id="userAvatar">
        <button class="avatar-edit" @click="changeAvatar">
          <i class="fas fa-camera"></i>
        </button>
      </div>
      <div class="profile-info">
        <h3>{{ userData.username }}</h3>
        <p class="user-level">{{ userData.level }}</p>
        <div class="user-stats">
          <span class="stat-badge">
            <i class="fas fa-eye"></i>
            <span>关注: <strong>{{ userData.followCount }}</strong></span>
          </span>
          <span class="stat-badge">
            <i class="fas fa-star"></i>
            <span>收藏: <strong>{{ userData.favoriteCount }}</strong></span>
          </span>
        </div>
      </div>
    </div>
    
    <div class="profile-section">
      <div class="section-header">
        <h4 class="section-title">
          <i class="fas fa-user-circle"></i>
          账户信息
        </h4>
        <el-button type="primary" size="small" @click="openEditDialog">编辑资料</el-button>
      </div>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">会员ID</span>
          <span class="info-value">{{ userData.userId }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">昵称</span>
          <span class="info-value">{{ userData.nickname || userData.username }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">注册时间</span>
          <span class="info-value">{{ userData.registerDate }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">使用时长</span>
          <span class="info-value">{{ userData.usageDuration }}天</span>
        </div>
        <div class="info-item">
          <span class="info-label">邮箱</span>
          <span class="info-value">{{ userData.email || '未设置' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">手机号</span>
          <span class="info-value">{{ userData.phone || '未设置' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">性别</span>
          <span class="info-value">{{ getGenderText(userData.gender) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">生日</span>
          <span class="info-value">{{ userData.birthday || '未设置' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">个人简介</span>
          <span class="info-value">{{ userData.bio || userData.description || '未填写' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">账户状态</span>
          <span 
            class="info-value" 
            :class="userData.isLoggedIn ? 'status-active' : ''"
          >
            {{ userData.isLoggedIn ? '正常' : '未登录' }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="profile-section">
      <h4 class="section-title">
        <i class="fas fa-chart-line"></i>
        数据统计
      </h4>
      <div class="stats-grid-mini">
        <div class="stat-card-mini">
          <div class="stat-icon" style="background: rgba(88, 166, 255, 0.2); color: var(--primary);">
            <i class="fas fa-eye"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ userData.totalViews.toLocaleString() }}</div>
            <div class="stat-label">总浏览量</div>
          </div>
        </div>
        <div class="stat-card-mini">
          <div class="stat-icon" style="background: rgba(126, 231, 135, 0.2); color: var(--success);">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ userData.correctPredictions }}%</div>
            <div class="stat-label">预测准确率</div>
          </div>
        </div>
        <div class="stat-card-mini">
          <div class="stat-icon" style="background: rgba(240, 136, 62, 0.2); color: var(--warning);">
            <i class="fas fa-fire"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ userData.streakDays }}</div>
            <div class="stat-label">连续登录</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="profile-section">
      <h4 class="section-title">
        <i class="fas fa-cog"></i>
        设置
      </h4>
      <div class="settings-list">
        <div class="setting-item" @click="toggleSetting('notifications')">
          <div class="setting-content">
            <i class="fas fa-bell setting-icon"></i>
            <span>消息通知</span>
          </div>
          <div class="setting-toggle">
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="userData.settings.notifications"
                @change="updateSetting"
              >
              <span class="slider"></span>
            </label>
          </div>
        </div>
        <div class="setting-item" @click="toggleSetting('darkMode')">
          <div class="setting-content">
            <i class="fas fa-moon setting-icon"></i>
            <span>深色模式</span>
          </div>
          <div class="setting-toggle">
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="userData.settings.darkMode"
                @change="updateSetting"
              >
              <span class="slider"></span>
            </label>
          </div>
        </div>
        <div class="setting-item" @click="openLoginModal">
          <div class="setting-content">
            <i class="fas fa-sign-in-alt setting-icon"></i>
            <span>登录/注册</span>
          </div>
          <i class="fas fa-chevron-right"></i>
        </div>
        <div class="setting-item" @click="clearCache">
          <div class="setting-content">
            <i class="fas fa-trash setting-icon"></i>
            <span style="color: var(--danger);">清除缓存</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑个人信息对话框 -->
    <UserProfileEditDialog
      v-model="editDialogVisible"
      :userData="userData"
      @updated="onProfileUpdated"
    />
  </div>
</template>

<script>
import { computed, ref } from 'vue';
import { useAppStore } from '../stores';
import UserProfileEditDialog from './UserProfileEditDialog.vue';

export default {
  name: 'ProfilePanel',
  components: {
    UserProfileEditDialog
  },
  setup() {
    const store = useAppStore();
    const editDialogVisible = ref(false);
    
    const userData = computed(() => store.userData);
    
    const avatarUrl = computed(() => {
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${store.userData.avatarSeed}`;
    });
    
    const changeAvatar = () => {
      const newSeed = prompt('请输入头像种子 (任意字符串):', store.userData.avatarSeed);
      if (newSeed) {
        store.updateUserData({ ...store.userData, avatarSeed: newSeed });
      }
    };
    
    const toggleSetting = (setting) => {
      store.toggleSetting(setting);
    };
    
    const updateSetting = () => {
      // 设置已经在computed属性中更新了，这里可以添加额外处理
    };
    
    const openLoginModal = () => {
      store.setShowLoginModal(true);
    };
    
    const clearCache = () => {
      if (confirm('确定要清除所有缓存数据吗？')) {
        localStorage.clear();
        // 重置部分用户数据
        store.updateUserData({
          ...store.userData,
          isLoggedIn: false,
          username: '竞彩玩家',
          userId: 'JC2026001',
          level: 'VIP 3级会员',
          avatarSeed: 'default'
        });
      }
    };
    
    const openEditDialog = () => {
      editDialogVisible.value = true;
    };
    
    const onProfileUpdated = (updatedData) => {
      // 更新本地存储的用户数据
      store.updateUserData({
        ...store.userData,
        ...updatedData,
        nickname: updatedData.nickname || updatedData.username
      });
    };
    
    const getGenderText = (gender) => {
      switch(gender) {
        case 1: return '男';
        case 2: return '女';
        case 0: return '保密';
        default: return '未设置';
      }
    };
    
    return {
      userData,
      avatarUrl,
      changeAvatar,
      toggleSetting,
      updateSetting,
      openLoginModal,
      clearCache,
      openEditDialog,
      editDialogVisible,
      onProfileUpdated,
      getGenderText
    };
  }
};
</script>

<style scoped>
.profile-panel {
  padding: 16px;
  animation: fadeIn 0.4s ease-out;
}

.profile-header {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.profile-avatar {
  position: relative;
  margin-right: 20px;
}

.profile-avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid var(--primary);
  background: var(--bg-body);
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar-edit:active {
  transform: scale(0.9);
}

.profile-info {
  flex: 1;
}

.profile-info h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: var(--text-main);
}

.user-level {
  font-size: 14px;
  color: var(--warning);
  background: rgba(240, 136, 62, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
  margin-bottom: 12px;
}

.user-stats {
  display: flex;
  gap: 16px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-sub);
}

.stat-badge i {
  color: var(--primary);
}

.stat-badge strong {
  color: var(--text-main);
  margin-left: 4px;
}

.profile-section {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  color: var(--text-main);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-title i {
  color: var(--primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  color: var(--text-main);
  font-weight: 500;
}

.status-active {
  color: var(--success) !important;
}

.stats-grid-mini {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-card-mini {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 2px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-sub);
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:active {
  background: rgba(255, 255, 255, 0.05);
}

.setting-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-icon {
  width: 24px;
  color: var(--text-sub);
  text-align: center;
}

.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border-color);
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary);
}

input:checked + .slider:before {
  transform: translateX(24px);
}
</style>