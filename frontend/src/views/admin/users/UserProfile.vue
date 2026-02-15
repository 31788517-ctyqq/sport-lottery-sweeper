<template>
  <div class="user-profile-container">
    <el-row :gutter="20">
      <!-- 个人信息 -->
      <el-col :xs="24" :lg="16">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h3>个人信息</h3>
              <el-button type="primary" @click="handleEditProfile">
                <el-icon><Edit /></el-icon>
                编辑信息
              </el-button>
            </div>
          </template>
          
          <div class="profile-content">
            <!-- 头像区域 -->
            <div class="avatar-section">
              <el-avatar :size="100" :src="userProfile.avatar" class="user-avatar">
                {{ (userProfile.realName || userProfile.username || 'U').charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="avatar-actions">
                <el-button size="small" @click="handleChangeAvatar">更换头像</el-button>
              </div>
            </div>
            
            <!-- 基本信息 -->
            <div class="info-section">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="用户名">
                  {{ userProfile.username }}
                </el-descriptions-item>
                <el-descriptions-item label="姓名">
                  {{ userProfile.realName || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="邮箱">
                  {{ userProfile.email }}
                </el-descriptions-item>
                <el-descriptions-item label="手机号">
                  {{ userProfile.phone || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="部门">
                  {{ userProfile.departmentName || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="职位">
                  {{ userProfile.position || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="角色">
                  <el-tag 
                    v-for="role in userProfile.roleNames" 
                    :key="role"
                    size="small"
                    style="margin-right: 8px;"
                  >
                    {{ role }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="getStatusTagType(userProfile.status)">
                    {{ getStatusText(userProfile.status) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="注册时间">
                  {{ formatDate(userProfile.createdAt) }}
                </el-descriptions-item>
                <el-descriptions-item label="最后登录">
                  {{ formatDate(userProfile.lastLoginTime) || '从未登录' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
        
        <!-- 安全设置 -->
        <el-card class="security-card">
          <template #header>
            <div class="card-header">
              <h3>安全设置</h3>
            </div>
          </template>
          
          <div class="security-content">
            <el-form 
              ref="securityFormRef"
              :model="securitySettings" 
              :rules="securityRules"
              label-width="120px"
            >
              <el-form-item label="原密码">
                <el-input 
                  v-model="securitySettings.oldPassword" 
                  name="old_password"
                  type="password" 
                  placeholder="请输入原密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="新密码" prop="newPassword">
                <el-input 
                  v-model="securitySettings.newPassword" 
                  name="new_password"
                  type="password" 
                  placeholder="请输入新密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input 
                  v-model="securitySettings.confirmPassword" 
                  name="confirm_password"
                  type="password" 
                  placeholder="请再次输入新密码"
                  show-password
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
                  修改密码
                </el-button>
                <el-button @click="resetSecurityForm">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
            
            <!-- 其他安全选项 -->
            <el-divider />
            
            <div class="security-options">
              <div class="option-item">
                <div class="option-info">
                  <div class="option-title">双重认证 (2FA)</div>
                  <div class="option-desc">为账户添加额外的安全保护层</div>
                </div>
                <el-switch 
                  v-model="securitySettings.twoFactorEnabled"
                  active-text="开启"
                  inactive-text="关闭"
                  @change="handleTwoFactorChange"
                />
              </div>
              
              <div class="option-item">
                <div class="option-info">
                  <div class="option-title">登录通知</div>
                  <div class="option-desc">新设备登录时发送邮件通知</div>
                </div>
                <el-switch 
                  v-model="securitySettings.loginNotification"
                  active-text="开启"
                  inactive-text="关闭"
                  @change="handleLoginNotificationChange"
                />
              </div>
              
              <div class="option-item">
                <div class="option-info">
                  <div class="option-title">会话管理</div>
                  <div class="option-desc">查看和管理当前活跃的登录会话</div>
                </div>
                <el-button @click="showSessionsDialog = true">
                  查看会话
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 侧边栏 -->
      <el-col :xs="24" :lg="8">
        <!-- 快捷操作 -->
        <el-card class="quick-actions-card">
          <template #header>
            <h4>快捷操作</h4>
          </template>
          
          <div class="quick-actions">
            <el-button class="action-btn" @click="handleViewMyLogs">
              <el-icon><Document /></el-icon>
              我的操作日志
            </el-button>
            <el-button class="action-btn" @click="handleExportMyData">
              <el-icon><Download /></el-icon>
              导出我的数据
            </el-button>
            <el-button class="action-btn" @click="handlePrivacySettings">
              <el-icon><Lock /></el-icon>
              隐私设置
            </el-button>
          </div>
        </el-card>
        
        <!-- 登录历史 -->
        <el-card class="login-history-card">
          <template #header>
            <h4>最近登录</h4>
          </template>
          
          <div class="login-history">
            <div 
              v-for="log in loginHistory" 
              :key="log.id"
              class="login-item"
            >
              <div class="login-info">
                <div class="login-time">{{ formatDate(log.loginTime) }}</div>
                <div class="login-location">{{ log.location }} · {{ log.ip }}</div>
                <div class="login-device">{{ log.device }} · {{ log.browser }}</div>
              </div>
              <div class="login-status">
                <el-tag :type="log.success ? 'success' : 'danger'" size="small">
                  {{ log.success ? '成功' : '失败' }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="loginHistory.length === 0" class="empty-history">
              <el-empty description="暂无登录记录" :image-size="60" />
            </div>
          </div>
        </el-card>
        
        <!-- 数据统计 -->
        <el-card class="stats-card">
          <template #header>
            <h4>数据统计</h4>
          </template>
          
          <div class="stats-content">
            <div class="stat-item">
              <div class="stat-value">{{ userStats.totalLogins || 0 }}</div>
              <div class="stat-label">总登录次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.thisMonthLogins || 0 }}</div>
              <div class="stat-label">本月登录</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.totalOperations || 0 }}</div>
              <div class="stat-label">操作总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 编辑个人信息对话框 -->
    <ProfileEditDialog
      v-model="showProfileDialog"
      :user-data="userProfile"
      @saved="handleProfileSaved"
    />
    
    <!-- 会话管理对话框 -->
    <SessionManagementDialog
      v-model="showSessionsDialog"
      @session-ended="handleSessionEnded"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
// AI_WORKING: coder2 @2026-01-28T09:48:00Z - 移除未使用的ElMessageBox导入
import { ElMessage } from 'element-plus'
// AI_DONE: coder2 @2026-01-28T09:48:00Z
import { Edit, Document, Download, Lock } from '@element-plus/icons-vue'
import ProfileEditDialog from '@/components/admin/ProfileEditDialog.vue'
import SessionManagementDialog from '@/components/admin/SessionManagementDialog.vue'
import http from '@/utils/http'
// AI_WORKING: coder2 @2026-01-28T09:48:00Z - 移除未使用的API函数导入
// AI_DONE: coder2 @2026-01-28T09:48:00Z

const userProfile = ref({})
const securitySettings = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
  twoFactorEnabled: false,
  loginNotification: true
})
const loginHistory = ref([])
const userStats = ref({})
const changingPassword = ref(false)
const showProfileDialog = ref(false)
const showSessionsDialog = ref(false)

// 表单引用
const securityFormRef = ref(null)

// 安全设置验证规则
const securityRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      // AI_WORKING: coder2 @2026-01-28T09:48:00Z - 重命名未使用的参数
      validator: (_rule, value, callback) => {
        if (value !== securitySettings.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      // AI_DONE: coder2 @2026-01-28T09:48:00Z
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserProfile = async () => {
  try {
    // 使用adminAPI来获取当前用户信息
    const response = await http.get('/api/v1/admin/users/current-user')
    if (response && response.data) {
      userProfile.value = response.data
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败，请确认您已登录')
  }
}

// 加载登录历史
const loadLoginHistory = async () => {
  try {
    const response = await http.get('/api/v1/admin/users/login-history', { params: { limit: 10 } })
    if (response && response.data) {
      loginHistory.value = Array.isArray(response.data) ? response.data : []
    }
  } catch (error) {
    console.error('加载登录历史失败:', error)
    ElMessage.error('加载登录历史失败')
  }
}

// 加载用户统计
const loadUserStats = async () => {
  try {
    const response = await http.get('/api/v1/admin/users/stats/overview')
    if (response && response.data) {
      userStats.value = response.data
    }
  } catch (error) {
    console.error('加载用户统计失败:', error)
    ElMessage.error('加载用户统计失败')
  }
}

// 编辑个人信息
const handleEditProfile = () => {
  showProfileDialog.value = true
}

// 更换头像
const handleChangeAvatar = () => {
  ElMessage.info('更换头像功能开发中...')
}

// 修改密码
const handleChangePassword = async () => {
  try {
    await securityFormRef.value.validate()
    changingPassword.value = true
    
    // 使用正确的密码修改API
    const response = await http.put('/api/v1/admin/change-password', {
      old_password: securitySettings.oldPassword,
      new_password: securitySettings.newPassword
    })
    
    if (response && response.code === 200) {
      ElMessage.success('密码修改成功')
      resetSecurityForm()
    } else {
      ElMessage.error(response?.message || '修改密码失败')
    }
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('修改密码失败:', error)
      ElMessage.error(error.message || '修改密码失败')
    }
  } finally {
    changingPassword.value = false
  }
}

// 重置安全设置表单
const resetSecurityForm = () => {
  securitySettings.oldPassword = ''
  securitySettings.newPassword = ''
  securitySettings.confirmPassword = ''
  securityFormRef.value?.clearValidate()
}

// 双重认证开关
const handleTwoFactorChange = async (enabled) => {
  try {
    // TODO: 调用API设置双重认证
    ElMessage.success(enabled ? '已开启双重认证' : '已关闭双重认证')
  } catch (error) {
    console.error('设置双重认证失败:', error)
    ElMessage.error('设置失败')
    securitySettings.twoFactorEnabled = !enabled
  }
}

// 登录通知开关
const handleLoginNotificationChange = async (enabled) => {
  try {
    // TODO: 调用API设置登录通知
    ElMessage.success(enabled ? '已开启登录通知' : '已关闭登录通知')
  } catch (error) {
    console.error('设置登录通知失败:', error)
    ElMessage.error('设置失败')
    securitySettings.loginNotification = !enabled
  }
}

// 查看我的操作日志
const handleViewMyLogs = () => {
  ElMessage.info('跳转到我的操作日志页面')
}

// 导出我的数据
const handleExportMyData = () => {
  ElMessage.info('数据导出功能开发中...')
}

// 隐私设置
const handlePrivacySettings = () => {
  ElMessage.info('隐私设置功能开发中...')
}

// 个人信息保存回调
const handleProfileSaved = () => {
  loadUserProfile()
}

// 会话结束回调
const handleSessionEnded = () => {
  loadLoginHistory()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    active: '正常',
    inactive: '禁用',
    locked: '锁定'
  }
  return statusMap[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const tagTypeMap = {
    active: 'success',
    inactive: 'danger',
    locked: 'warning'
  }
  return tagTypeMap[status] || 'info'
}

onMounted(() => {
  loadUserProfile()
  loadLoginHistory()
  loadUserStats()
})
</script>

<style scoped>
.user-profile-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.profile-card,
.security-card,
.quick-actions-card,
.login-history-card,
.stats-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3,
.card-header h4 {
  margin: 0;
  color: #303133;
}

.profile-content {
  padding: 20px 0;
}

.avatar-section {
  text-align: center;
  margin-bottom: 32px;
}

.user-avatar {
  display: block;
  margin: 0 auto 16px;
  border: 4px solid #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.avatar-actions {
  margin-top: 16px;
}

.info-section {
  margin-top: 24px;
}

.security-content {
  padding: 20px 0;
}

.security-options {
  margin-top: 24px;
}

.option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.option-item:last-child {
  border-bottom: none;
}

.option-info {
  flex: 1;
}

.option-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.option-desc {
  font-size: 12px;
  color: #909399;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

.login-history {
  max-height: 300px;
  overflow-y: auto;
}

.login-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.login-item:last-child {
  border-bottom: none;
}

.login-info {
  flex: 1;
}

.login-time {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.login-location,
.login-device {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.empty-history {
  padding: 20px;
  text-align: center;
}

.stats-content {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.stat-item {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .user-profile-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .option-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .stats-content {
    flex-direction: column;
    gap: 16px;
  }
}
</style>