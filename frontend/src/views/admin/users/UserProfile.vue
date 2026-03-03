<template>
  <div class="user-profile-container morandi-page um-page">
    <el-row :gutter="16">
      <el-col :xs="24" :lg="16">
        <el-card class="morandi-card">
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
            <div class="avatar-section" v-if="privacySettings.showProfile">
              <el-avatar :size="96" :src="userProfile.avatar" class="user-avatar">
                {{ (userProfile.realName || userProfile.username || 'U').charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="avatar-actions">
                <el-button size="small" @click="handleChangeAvatar">更换头像</el-button>
              </div>
            </div>
            <div v-else class="avatar-section">
              <el-empty description="个人资料已隐藏" :image-size="80" />
            </div>

            <div class="info-section">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="用户名">{{ userProfile.username || '-' }}</el-descriptions-item>
                <el-descriptions-item label="姓名">{{ userProfile.realName || '-' }}</el-descriptions-item>
                <el-descriptions-item label="邮箱">
                  {{ privacySettings.showEmail ? userProfile.email || '-' : '已隐藏' }}
                </el-descriptions-item>
                <el-descriptions-item label="手机号">
                  {{ privacySettings.showPhone ? userProfile.phone || '-' : '已隐藏' }}
                </el-descriptions-item>
                <el-descriptions-item label="部门">{{ userProfile.departmentName || '-' }}</el-descriptions-item>
                <el-descriptions-item label="职位">{{ userProfile.position || '-' }}</el-descriptions-item>
                <el-descriptions-item label="角色">
                  <el-tag v-for="role in userProfile.roleNames || []" :key="role" size="small" class="mr-8">
                    {{ role }}
                  </el-tag>
                  <span v-if="!userProfile.roleNames || userProfile.roleNames.length === 0">-</span>
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="getStatusTagType(userProfile.status)">
                    {{ getStatusText(userProfile.status) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="注册时间">{{ formatDate(userProfile.createdAt) }}</el-descriptions-item>
                <el-descriptions-item label="最后登录">
                  {{ formatDate(userProfile.lastLoginTime) || '从未登录' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>

        <el-card class="morandi-card">
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
              <el-form-item label="原密码" prop="oldPassword">
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
                <el-button type="primary" :loading="changingPassword" @click="handleChangePassword">
                  修改密码
                </el-button>
                <el-button @click="resetSecurityForm">重置</el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <div class="security-options">
              <div class="option-item">
                <div class="option-info">
                  <div class="option-title">双重认证 (2FA)</div>
                  <div class="option-desc">为账号增加额外安全保护</div>
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
                  <div class="option-desc">新设备登录时发送提醒</div>
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
                  <div class="option-desc">查看并管理当前登录会话</div>
                </div>
                <el-button @click="showSessionsDialog = true">查看会话</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="morandi-card">
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

        <el-card class="morandi-card">
          <template #header>
            <div class="card-header">
              <h4>最近登录</h4>
              <el-button size="small" :icon="Refresh" @click="handleRefreshLoginHistory">刷新</el-button>
            </div>
          </template>

          <div class="login-history">
            <div
              v-for="log in loginHistory"
              :key="log.id || `${log.loginTime}-${log.ip}`"
              class="login-item"
            >
              <div class="login-info">
                <div class="login-time">{{ formatDate(log.loginTime) }}</div>
                <div class="login-location">{{ log.location || '-' }} | {{ log.ip || '-' }}</div>
                <div class="login-device">{{ log.device || '-' }} | {{ log.browser || '-' }}</div>
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

        <el-card class="morandi-card">
          <template #header>
            <div class="card-header">
              <h4>数据统计</h4>
              <el-button size="small" :icon="Refresh" @click="handleRefreshStats">刷新</el-button>
            </div>
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

    <ProfileEditDialog
      v-model="showProfileDialog"
      :user-info="userProfile"
      @saved="handleProfileSaved"
    />

    <SessionManagementDialog
      v-model="showSessionsDialog"
      :user-id="userProfile.id"
      @session-ended="handleSessionEnded"
    />

    <el-dialog
      class="um-dialog"
      v-model="showPrivacyDialog"
      title="隐私设置"
      width="480px"
    >
      <el-form label-width="120px">
        <el-form-item label="公开个人资料">
          <el-switch v-model="privacySettings.showProfile" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
        <el-form-item label="显示邮箱">
          <el-switch v-model="privacySettings.showEmail" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
        <el-form-item label="显示手机号">
          <el-switch v-model="privacySettings.showPhone" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPrivacyDialog = false">取消</el-button>
          <el-button type="primary" @click="savePrivacySettings">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Document, Download, Lock, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import ProfileEditDialog from '@/components/admin/ProfileEditDialog.vue'
import SessionManagementDialog from '@/components/admin/SessionManagementDialog.vue'
import http from '@/utils/http'

const router = useRouter()

const userProfile = ref({})
const securitySettings = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
  twoFactorEnabled: false,
  loginNotification: true
})
const privacySettings = reactive({
  showEmail: true,
  showPhone: true,
  showProfile: true
})
const loginHistory = ref([])
const userStats = ref({})
const changingPassword = ref(false)
const showProfileDialog = ref(false)
const showSessionsDialog = ref(false)
const showPrivacyDialog = ref(false)
const securityFormRef = ref(null)

const securityRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能小于 8 位', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== securitySettings.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const normalizeUserProfile = (raw) => {
  const preferences =
    raw?.preferences && typeof raw.preferences === 'string'
      ? (() => {
          try {
            return JSON.parse(raw.preferences)
          } catch {
            return {}
          }
        })()
      : raw?.preferences || {}

  return {
    ...raw,
    preferences,
    realName: raw?.realName || raw?.real_name || '',
    avatar: raw?.avatar || preferences.avatar || '',
    bio: raw?.bio || preferences.bio || '',
    gender: raw?.gender ?? preferences.gender ?? 0,
    birthday: raw?.birthday || preferences.birthday || '',
    departmentName: raw?.departmentName || raw?.department_name || raw?.department || '',
    roleNames: raw?.roleNames || raw?.role_names || (raw?.role ? [raw.role] : []),
    createdAt: raw?.createdAt || raw?.created_at || raw?.created_at,
    lastLoginTime: raw?.lastLoginTime || raw?.last_login_at || raw?.last_login_at,
    twoFactorEnabled: raw?.two_factor_enabled ?? preferences.twoFactorEnabled ?? false,
    loginNotification: preferences.loginNotification ?? true,
    privacy: preferences.privacy || {}
  }
}

const loadUserProfile = async () => {
  try {
    const response = await http.get('/api/v1/admin/admin-users/current-user')
    const payload = response?.data ?? response
    if (payload) {
      userProfile.value = normalizeUserProfile(payload)
      securitySettings.twoFactorEnabled = userProfile.value.twoFactorEnabled
      securitySettings.loginNotification = userProfile.value.loginNotification
      privacySettings.showEmail = userProfile.value.privacy?.showEmail ?? true
      privacySettings.showPhone = userProfile.value.privacy?.showPhone ?? true
      privacySettings.showProfile = userProfile.value.privacy?.showProfile ?? true
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败，请确认已登录')
  }
}

const loadLoginHistory = async () => {
  try {
    const response = await http.get('/api/v1/admin/admin-users/login-history', { params: { limit: 10 } })
    const payload = response?.data ?? response
    loginHistory.value = Array.isArray(payload) ? payload : []
  } catch (error) {
    console.error('加载登录历史失败:', error)
    ElMessage.error('加载登录历史失败')
  }
}

const loadUserStats = async () => {
  try {
    const response = await http.get('/api/v1/admin/admin-users/stats/overview')
    const payload = response?.data ?? response
    if (payload) userStats.value = payload
  } catch (error) {
    console.error('加载用户统计失败:', error)
    ElMessage.error('加载用户统计失败')
  }
}

const handleEditProfile = () => {
  showProfileDialog.value = true
}

const handleChangeAvatar = () => {
  showProfileDialog.value = true
}

const handleChangePassword = async () => {
  try {
    await securityFormRef.value.validate()
    changingPassword.value = true

    await http.put('/api/v1/admin/admin-users/change-password', {
      old_password: securitySettings.oldPassword,
      new_password: securitySettings.newPassword
    })

    ElMessage.success('密码修改成功')
    resetSecurityForm()
  } catch (error) {
    if (error !== false) {
      console.error('修改密码失败:', error)
      ElMessage.error(error?.message || '修改密码失败')
    }
  } finally {
    changingPassword.value = false
  }
}

const resetSecurityForm = () => {
  securitySettings.oldPassword = ''
  securitySettings.newPassword = ''
  securitySettings.confirmPassword = ''
  securityFormRef.value?.clearValidate()
}

const buildPreferences = () => ({
  avatar: userProfile.value?.avatar || '',
  bio: userProfile.value?.bio || '',
  gender: userProfile.value?.gender ?? 0,
  birthday: userProfile.value?.birthday || '',
  twoFactorEnabled: securitySettings.twoFactorEnabled,
  loginNotification: securitySettings.loginNotification,
  privacy: {
    showEmail: privacySettings.showEmail,
    showPhone: privacySettings.showPhone,
    showProfile: privacySettings.showProfile
  }
})

const updateCurrentUser = async (payload) => {
  await http.put('/api/v1/admin/admin-users/current-user', payload)
  await loadUserProfile()
}

const handleTwoFactorChange = async (enabled) => {
  try {
    await updateCurrentUser({
      two_factor_enabled: enabled,
      preferences: buildPreferences()
    })
    ElMessage.success(enabled ? '已开启双重认证' : '已关闭双重认证')
  } catch (error) {
    console.error('设置双重认证失败:', error)
    ElMessage.error('设置失败')
    securitySettings.twoFactorEnabled = !enabled
  }
}

const handleLoginNotificationChange = async (enabled) => {
  try {
    await updateCurrentUser({
      preferences: buildPreferences()
    })
    ElMessage.success(enabled ? '已开启登录通知' : '已关闭登录通知')
  } catch (error) {
    console.error('设置登录通知失败:', error)
    ElMessage.error('设置失败')
    securitySettings.loginNotification = !enabled
  }
}

const handleViewMyLogs = () => {
  router.push('/admin/users/logs')
}

const handleExportMyData = async () => {
  try {
    if (!userProfile.value?.id) {
      await loadUserProfile()
    }

    const exportPayload = {
      profile: userProfile.value,
      stats: userStats.value,
      loginHistory: loginHistory.value
    }

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `my_profile_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('已导出个人数据')
  } catch (error) {
    console.error('导出个人数据失败:', error)
    ElMessage.error('导出失败')
  }
}

const handlePrivacySettings = () => {
  showPrivacyDialog.value = true
}

const savePrivacySettings = async () => {
  try {
    await updateCurrentUser({
      preferences: buildPreferences()
    })
    ElMessage.success('隐私设置已保存')
    showPrivacyDialog.value = false
  } catch (error) {
    console.error('保存隐私设置失败:', error)
    ElMessage.error('保存失败')
  }
}

const handleProfileSaved = () => {
  loadUserProfile()
}

const handleRefreshStats = () => {
  loadUserStats()
}

const handleRefreshLoginHistory = () => {
  loadLoginHistory()
}

const handleSessionEnded = () => {
  loadLoginHistory()
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const getStatusText = (status) => {
  const statusMap = {
    active: '正常',
    inactive: '禁用',
    locked: '锁定'
  }
  return statusMap[status] || status || '-'
}

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
.morandi-page {
  --m-bg: #f5f7fa;
  --m-card: #ffffff;
  --m-border: #ebeef5;
  --m-head: #ffffff;
  --m-text: #303133;
  --m-subtext: #909399;
}

.user-profile-container {
  padding: 20px;
  background: var(--m-bg);
  min-height: calc(100vh - 110px);
}

.morandi-card {
  border-radius: 4px;
  border: 1px solid var(--m-border);
  box-shadow: none;
  margin-bottom: 16px;
  background: var(--m-card);
}

.morandi-card :deep(.el-card__header) {
  background: var(--m-head);
  border-bottom: 1px solid var(--m-border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.card-header h3,
.card-header h4 {
  margin: 0;
  color: var(--m-text);
}

.profile-content {
  padding: 8px 0;
}

.avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.user-avatar {
  display: block;
  margin: 0 auto 12px;
  border: 3px solid #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.avatar-actions {
  margin-top: 10px;
}

.info-section {
  margin-top: 16px;
}

.security-content {
  padding: 8px 0;
}

.security-options {
  margin-top: 20px;
}

.option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--m-border);
}

.option-item:last-child {
  border-bottom: none;
}

.option-info {
  flex: 1;
}

.option-title {
  font-weight: 600;
  color: var(--m-text);
  margin-bottom: 4px;
}

.option-desc {
  font-size: 12px;
  color: var(--m-subtext);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
}

.login-history {
  max-height: 360px;
  overflow: auto;
}

.login-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed var(--m-border);
}

.login-item:last-child {
  border-bottom: none;
}

.login-time {
  font-weight: 600;
  color: var(--m-text);
}

.login-location,
.login-device {
  color: var(--m-subtext);
  font-size: 12px;
  margin-top: 2px;
}

.empty-history {
  padding: 12px 0;
}

.stats-content {
  display: flex;
  gap: 12px;
}

.stat-item {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--m-border);
  border-radius: 4px;
  background: #ffffff;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 12px;
  color: var(--m-subtext);
}

.mr-8 {
  margin-right: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.um-dialog.el-dialog) {
  border: 1px solid var(--m-border);
  border-radius: 4px;
  box-shadow: none;
  overflow: hidden;
}

:deep(.um-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 14px 16px;
  border-bottom: 1px solid var(--m-border);
}

:deep(.um-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: var(--m-text);
}

:deep(.um-dialog .el-dialog__body) {
  padding: 16px;
}

:deep(.um-dialog .el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid var(--m-border);
}

@media (max-width: 768px) {
  .user-profile-container {
    padding: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .option-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .stats-content {
    flex-direction: column;
  }
}
</style>
