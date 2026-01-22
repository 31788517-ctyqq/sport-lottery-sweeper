<template>
  <div class="user-profile">
    <!-- 用户资料卡片 -->
    <BaseCard class="profile-card" :loading="loading">
      <div class="profile-header">
        <h2 class="profile-title">个人资料</h2>
        <BaseButton 
          v-if="isOwnProfile"
          variant="outline"
          size="sm"
          @click="editMode = !editMode"
        >
          {{ editMode ? '取消编辑' : '编辑资料' }}
        </BaseButton>
      </div>

      <!-- 头像和基本信息区域 -->
      <div class="profile-basic">
        <div class="avatar-section">
          <UserAvatar 
            :src="userData.avatar"
            :username="userData.username"
            :size="120"
            :editable="isOwnProfile"
            @avatar-change="handleAvatarChange"
          />
          <div v-if="isOwnProfile" class="avatar-upload-tip">
            点击头像上传新图片
          </div>
        </div>

        <div class="info-section">
          <!-- 查看模式 -->
          <div v-if="!editMode" class="info-view">
            <div class="info-row">
              <span class="info-label">用户名：</span>
              <span class="info-value">{{ userData.username }}</span>
              <UserLevel :level="userData.level" class="ml-2" />
            </div>
            
            <div class="info-row">
              <span class="info-label">邮箱：</span>
              <span class="info-value">{{ userData.email }}</span>
              <span v-if="userData.emailVerified" class="verified-badge">
                <i class="fas fa-check-circle"></i> 已验证
              </span>
            </div>
            
            <div class="info-row">
              <span class="info-label">注册时间：</span>
              <span class="info-value">{{ formatDate(userData.createdAt) }}</span>
            </div>
            
            <div class="info-row">
              <span class="info-label">会员到期：</span>
              <span 
                class="info-value"
                :class="{ 'text-warning': isSubscriptionExpiring }"
              >
                {{ formatDate(userData.subscriptionExpiresAt) }}
                <span v-if="isSubscriptionExpiring" class="expire-warning">
                  （即将到期）
                </span>
              </span>
            </div>
          </div>

          <!-- 编辑模式 -->
          <div v-else class="info-edit">
            <form @submit.prevent="saveProfile">
              <div class="form-group">
                <label for="displayName">显示名称</label>
                <BaseInput
                  id="displayName"
                  v-model="editData.displayName"
                  placeholder="输入显示名称"
                  maxlength="20"
                />
              </div>
              
              <div class="form-group">
                <label for="bio">个人简介</label>
                <textarea
                  id="bio"
                  v-model="editData.bio"
                  class="form-control"
                  rows="3"
                  placeholder="简单介绍一下自己..."
                  maxlength="200"
                ></textarea>
                <div class="char-count">
                  {{ editData.bio?.length || 0 }}/200
                </div>
              </div>

              <div class="form-group">
                <label>通知设置</label>
                <div class="checkbox-group">
                  <label class="checkbox-item">
                    <input
                      type="checkbox"
                      v-model="editData.notifications.email"
                    />
                    邮箱通知
                  </label>
                  <label class="checkbox-item">
                    <input
                      type="checkbox"
                      v-model="editData.notifications.push"
                    />
                    推送通知
                  </label>
                </div>
              </div>

              <div class="form-actions">
                <BaseButton
                  type="submit"
                  :loading="saving"
                  :disabled="!hasChanges"
                >
                  保存更改
                </BaseButton>
                <BaseButton
                  type="button"
                  variant="outline"
                  @click="cancelEdit"
                >
                  取消
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ userData.stats?.favorites || 0 }}</div>
            <div class="stat-label">收藏比赛</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userData.stats?.notifications || 0 }}</div>
            <div class="stat-label">关注提醒</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userData.stats?.daysActive || 0 }}</div>
            <div class="stat-label">活跃天数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userData.stats?.accuracy || '--' }}%</div>
            <div class="stat-label">预测准确率</div>
          </div>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useUserStore } from '@/store/modules/user'
import { storeToRefs } from 'pinia'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import UserAvatar from './UserAvatar.vue'
import UserLevel from './UserLevel.vue'
import { formatDate } from '@/utils/date'
import type { UserProfileData, UserProfileUpdate } from '@/types/user'

// Props
interface Props {
  userId?: string
}

const props = withDefaults(defineProps<Props>(), {
  userId: undefined
})

// Emits
const emit = defineEmits<{
  'profile-updated': [data: UserProfileData]
  'avatar-changed': [file: File]
}>()

// Store
const userStore = useUserStore()
const { currentUser } = storeToRefs(userStore)

// State
const loading = ref(false)
const saving = ref(false)
const editMode = ref(false)
const userData = ref<UserProfileData>({
  id: '',
  username: '',
  email: '',
  avatar: '',
  level: 1,
  subscriptionExpiresAt: new Date(),
  createdAt: new Date(),
  emailVerified: false,
  stats: {
    favorites: 0,
    notifications: 0,
    daysActive: 0,
    accuracy: 0
  }
})

const editData = ref<UserProfileUpdate>({
  displayName: '',
  bio: '',
  notifications: {
    email: true,
    push: true
  }
})

// Computed
const isOwnProfile = computed(() => {
  if (!props.userId) return true
  return props.userId === currentUser.value?.id
})

const isSubscriptionExpiring = computed(() => {
  const expiresAt = userData.value.subscriptionExpiresAt
  if (!expiresAt) return false
  
  const now = new Date()
  const daysDiff = Math.ceil((expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return daysDiff <= 7 && daysDiff > 0
})

const hasChanges = computed(() => {
  return editData.value.displayName !== userData.value.displayName ||
    editData.value.bio !== userData.value.bio ||
    JSON.stringify(editData.value.notifications) !== JSON.stringify(userData.value.notificationSettings)
})

// Methods
const fetchUserProfile = async () => {
  try {
    loading.value = true
    // 这里调用API获取用户资料
    // const response = await userApi.getProfile(props.userId)
    // userData.value = response.data
    
    // 模拟数据
    userData.value = {
      id: props.userId || '1',
      username: '足球分析达人',
      email: 'user@example.com',
      avatar: '/avatars/default.jpg',
      displayName: '足球达人',
      bio: '热爱足球分析，专注于欧洲五大联赛研究',
      level: 3,
      subscriptionExpiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      createdAt: new Date('2024-01-01'),
      emailVerified: true,
      notificationSettings: {
        email: true,
        push: true
      },
      stats: {
        favorites: 42,
        notifications: 15,
        daysActive: 120,
        accuracy: 68.5
      }
    }
    
    // 初始化编辑数据
    editData.value = {
      displayName: userData.value.displayName || '',
      bio: userData.value.bio || '',
      notifications: { ...userData.value.notificationSettings }
    }
  } catch (error) {
    console.error('获取用户资料失败:', error)
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  try {
    saving.value = true
    
    // 这里调用API更新用户资料
    // await userApi.updateProfile(editData.value)
    
    // 更新本地数据
    Object.assign(userData.value, editData.value)
    
    // 退出编辑模式
    editMode.value = false
    
    emit('profile-updated', userData.value)
  } catch (error) {
    console.error('保存资料失败:', error)
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  editData.value = {
    displayName: userData.value.displayName || '',
    bio: userData.value.bio || '',
    notifications: { ...userData.value.notificationSettings }
  }
  editMode.value = false
}

const handleAvatarChange = (file: File) => {
  emit('avatar-changed', file)
  // 这里可以调用API上传头像
}

// Lifecycle
onMounted(() => {
  fetchUserProfile()
})

// Watch
watch(() => props.userId, () => {
  fetchUserProfile()
})
</script>

<style scoped>
.user-profile {
  max-width: 800px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.profile-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.profile-basic {
  display: flex;
  gap: 32px;
  margin-bottom: 32px;
}

@media (max-width: 768px) {
  .profile-basic {
    flex-direction: column;
    gap: 24px;
  }
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.avatar-upload-tip {
  margin-top: 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-align: center;
}

.info-section {
  flex: 1;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
}

.info-label {
  min-width: 80px;
  color: var(--text-secondary);
  font-weight: 500;
}

.info-value {
  flex: 1;
  color: var(--text-primary);
}

.verified-badge {
  margin-left: 8px;
  padding: 2px 8px;
  background-color: var(--success-light);
  color: var(--success);
  border-radius: 12px;
  font-size: 0.75rem;
}

.verified-badge i {
  margin-right: 4px;
}

.text-warning {
  color: var(--warning);
}

.expire-warning {
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: border-color 0.2s;
  resize: vertical;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
}

.char-count {
  text-align: right;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.checkbox-item input {
  margin-right: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.stats-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-item {
  text-align: center;
  padding: 16px;
  background-color: var(--bg-secondary);
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
</style>