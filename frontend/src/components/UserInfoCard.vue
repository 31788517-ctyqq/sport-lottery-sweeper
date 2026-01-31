<template>
  <div class="user-info-card">
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><User /></el-icon>
            用户信息
          </span>
          <el-button 
            type="primary" 
            :icon="Refresh" 
            circle 
            size="small"
            @click="refreshUserInfo"
            :loading="loading"
          />
        </div>
      </template>
      
      <!-- 未登录状态 -->
      <div v-if="!userInfo.id" class="not-logged-in">
        <el-empty description="未登录">
          <el-button type="primary" @click="handleLogin">
            <el-icon><Key /></el-icon>
            立即登录
          </el-button>
        </el-empty>
      </div>

      <!-- 用户信息展示 -->
      <div v-else class="user-content">
        <!-- 用户头像和基本信息 -->
        <div class="user-profile">
          <div class="avatar-section">
            <el-avatar 
              :size="80" 
              :src="userInfo.avatar_url || ''"
              class="user-avatar"
            >
              {{ userInfo.full_name?.charAt(0) || userInfo.email?.charAt(0) || 'U' }}
            </el-avatar>
            <div class="user-basic">
              <h3 class="user-name">{{ userInfo.full_name || '未设置姓名' }}</h3>
              <p class="user-email">{{ userInfo.email }}</p>
              <el-tag :type="getRoleType(userInfo.role)" size="small">
                {{ getRoleText(userInfo.role) }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 详细信息 -->
        <div class="user-details">
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="用户ID">
              <el-tag size="small" type="info">{{ userInfo.id }}</el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="邮箱">
              {{ userInfo.email }}
            </el-descriptions-item>
            
            <el-descriptions-item label="姓名">
              {{ userInfo.full_name || '未设置' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="角色">
              <el-tag :type="getRoleType(userInfo.role)" size="small">
                {{ getRoleText(userInfo.role) }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="账户状态">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'" size="small">
                {{ userInfo.is_active ? '激活' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="创建时间">
              {{ formatTime(userInfo.created_at) }}
            </el-descriptions-item>
            
            <el-descriptions-item label="最后更新">
              {{ formatTime(userInfo.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 操作按钮 -->
        <div class="user-actions">
          <el-space wrap>
            <el-button type="primary" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑信息
            </el-button>
            <el-button @click="handleChangePassword">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-button>
            <el-button type="warning" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </el-space>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="errorMessage" class="error-message">
        <el-alert 
          :title="errorMessage" 
          type="error" 
          show-icon 
          :closable="false"
          @close="errorMessage = ''"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  User, Refresh, Key, Edit, Lock, SwitchButton 
} from '@element-plus/icons-vue'
import { getUserProfile } from '@/api/example.js'

// Props
const props = defineProps({
  autoLoad: {
    type: Boolean,
    default: true
  },
  userId: {
    type: [String, Number],
    default: null
  }
})

// Emits
const emit = defineEmits(['login', 'logout', 'edit', 'change-password', 'load-error'])

// 响应式数据
const loading = ref(false)
const userInfo = ref({})
const errorMessage = ref('')

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '未知'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 获取角色类型样式
const getRoleType = (role) => {
  const roleMap = {
    admin: 'danger',
    analyst: 'warning',
    operator: 'success',
    viewer: 'info'
  }
  return roleMap[role] || 'info'
}

// 获取角色文本
const getRoleText = (role) => {
  const roleMap = {
    admin: '管理员',
    analyst: '分析师',
    operator: '操作员',
    viewer: '查看者'
  }
  return roleMap[role] || role || '未知'
}

// 加载用户信息
const loadUserInfo = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await getUserProfile()
    userInfo.value = response.data || response
    
    if (!userInfo.value.id) {
      throw new Error('用户信息为空')
    }
    
    ElMessage.success('用户信息加载成功')
    
  } catch (error) {
    console.error('加载用户信息失败:', error)
    errorMessage.value = error.message || '加载用户信息失败'
    userInfo.value = {}
    emit('load-error', error)
  } finally {
    loading.value = false
  }
}

// 刷新用户信息
const refreshUserInfo = () => {
  loadUserInfo()
}

// 处理登录
const handleLogin = () => {
  emit('login')
}

// 处理退出登录
const handleLogout = () => {
  emit('logout')
}

// 处理编辑
const handleEdit = () => {
  emit('edit', userInfo.value)
}

// 处理修改密码
const handleChangePassword = () => {
  emit('change-password', userInfo.value)
}

// 生命周期
onMounted(() => {
  if (props.autoLoad) {
    loadUserInfo()
  }
})

// 暴露方法给父组件
defineExpose({
  loadUserInfo,
  refreshUserInfo,
  userInfo
})
</script>

<style scoped>
.user-info-card {
  width: 100%;
}

.info-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.not-logged-in {
  text-align: center;
  padding: 40px 20px;
}

.user-content {
  space-y: 20px;
}

.user-profile {
  margin-bottom: 24px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-basic {
  flex: 1;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.user-email {
  margin: 0 0 12px 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.user-details {
  margin-bottom: 24px;
}

.user-actions {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.error-message {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .user-actions {
    flex-direction: column;
  }
  
  .user-actions .el-button {
    width: 100%;
  }
}</style>