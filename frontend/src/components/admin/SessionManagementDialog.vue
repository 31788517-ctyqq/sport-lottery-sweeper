<template>
  <el-dialog
    title="会话管理"
    v-model="visible"
    width="800px"
    @close="handleClose"
  >
    <div class="session-management">
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="danger" @click="forceLogoutAll" :disabled="sessions.length === 0">
          强制退出所有设备
        </el-button>
        <el-button type="warning" @click="refreshSessions">
          刷新
        </el-button>
      </div>
      
      <!-- 会话列表 -->
      <el-table :data="sessions" style="width: 100%; margin-top: 16px">
        <el-table-column prop="deviceInfo" label="设备信息" width="200">
          <template #default="scope">
            <div class="device-info">
              <el-icon class="device-icon">
                <Monitor v-if="scope.row.deviceType === 'desktop'" />
                <Iphone v-else-if="scope.row.deviceType === 'mobile'" />
                <Cellphone v-else />
              </el-icon>
              <div>
                <div class="device-name">{{ scope.row.deviceName }}</div>
                <div class="device-type">{{ getDeviceTypeName(scope.row.deviceType) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="browserInfo" label="浏览器" width="150">
          <template #default="scope">
            <div>{{ scope.row.browser }}</div>
            <div class="version-info">{{ scope.row.browserVersion }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="loginIp" label="登录IP" width="140" />
        
        <el-table-column prop="loginLocation" label="登录地点" width="120" />
        
        <el-table-column prop="loginTime" label="登录时间" width="170">
          <template #default="scope">
            <div>{{ formatDate(scope.row.loginTime) }}</div>
            <div class="duration-info">已持续 {{ formatDuration(scope.row.duration) }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="lastActiveTime" label="最后活跃" width="170">
          <template #default="scope">
            {{ formatDate(scope.row.lastActiveTime) }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.isCurrent ? 'success' : 'info'">
              {{ scope.row.isCurrent ? '当前' : '其他' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button
              v-if="!scope.row.isCurrent"
              type="danger"
              size="small"
              @click="forceLogout(scope.row)"
            >
              踢出
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Monitor, Iphone, Cellphone } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: Boolean,
  userId: Number
})

// Emits
const emit = defineEmits(['update:modelValue', 'logout-session'])

// 响应式数据
const visible = ref(false)

// 模拟会话数据
const sessions = ref([
  {
    id: 1,
    deviceType: 'desktop',
    deviceName: 'Windows Chrome',
    browser: 'Chrome',
    browserVersion: '120.0.6099.109',
    loginIp: '192.168.1.100',
    loginLocation: '北京',
    loginTime: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2小时前
    lastActiveTime: new Date(Date.now() - 5 * 60 * 1000), // 5分钟前
    duration: 2 * 60 * 60 * 1000 + 5 * 60 * 1000, // 2小时5分钟
    isCurrent: true
  },
  {
    id: 2,
    deviceType: 'mobile',
    deviceName: 'iPhone Safari',
    browser: 'Safari',
    browserVersion: '17.1.2',
    loginIp: '10.0.0.50',
    loginLocation: '上海',
    loginTime: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1天前
    lastActiveTime: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2小时前
    duration: 26 * 60 * 60 * 1000, // 26小时
    isCurrent: false
  },
  {
    id: 3,
    deviceType: 'tablet',
    deviceName: 'iPad Chrome',
    browser: 'Chrome',
    browserVersion: '119.0.6045.82',
    loginIp: '172.16.0.25',
    loginLocation: '广州',
    loginTime: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3天前
    lastActiveTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1天前
    duration: 72 * 60 * 60 * 1000 + 5 * 60 * 60 * 1000, // 77小时
    isCurrent: false
  }
])

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadSessions()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const loadSessions = () => {
  // 这里应该从API加载用户的会话列表
  // loadUserSessions(props.userId).then(data => {
  //   sessions.value = data
  // })
}

const refreshSessions = () => {
  loadSessions()
  ElMessage.success('刷新成功')
}

const getDeviceTypeName = (type) => {
  const typeMap = {
    desktop: '桌面端',
    mobile: '移动端',
    tablet: '平板端'
  }
  return typeMap[type] || '未知'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const formatDuration = (duration) => {
  if (!duration) return '-'
  
  const hours = Math.floor(duration / (1000 * 60 * 60))
  const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}

const forceLogout = (session) => {
  ElMessageBox.confirm(
    `确定要强制退出设备「${session.deviceName}」的登录吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('logout-session', session.id)
    
    // 从列表中移除
    const index = sessions.value.findIndex(s => s.id === session.id)
    if (index > -1) {
      sessions.value.splice(index, 1)
    }
    
    ElMessage.success('已强制退出该设备')
  })
}

const forceLogoutAll = () => {
  const otherSessions = sessions.value.filter(s => !s.isCurrent)
  if (otherSessions.length === 0) {
    ElMessage.info('没有其他设备的登录会话')
    return
  }
  
  ElMessageBox.confirm(
    `确定要强制退出所有其他设备（共${otherSessions.length}台）的登录吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('logout-session', 'all')
    
    // 只保留当前会话
    sessions.value = sessions.value.filter(s => s.isCurrent)
    
    ElMessage.success(`已强制退出${otherSessions.length}台设备`)
  })
}

const handleClose = () => {
  visible.value = false
}

// 暴露方法
defineExpose({
  visible
})
</script>

<style scoped>
.session-management {
  max-height: 500px;
  overflow-y: auto;
}

.action-bar {
  display: flex;
  gap: 12px;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.device-icon {
  font-size: 24px;
  color: var(--el-text-color-regular);
}

.device-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.device-type {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.version-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.duration-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>