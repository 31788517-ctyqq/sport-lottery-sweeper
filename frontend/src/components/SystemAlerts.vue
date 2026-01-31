<template>
  <div class="system-alerts">
    <el-card class="alerts-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Bell /></el-icon>
            系统告警中心
          </span>
          <div class="card-actions">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
              <el-button :icon="Bell" circle />
            </el-badge>
            <el-button type="primary" :icon="Plus" @click="showCreateAlert = true">
              创建告警
            </el-button>
            <el-button :icon="Refresh" circle @click="refreshAlerts" :loading="loading" />
          </div>
        </div>
      </template>

      <!-- 告警统计 -->
      <div class="alert-stats">
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="stat-item critical">
              <div class="stat-number">{{ alertStats.critical }}</div>
              <div class="stat-label">严重</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item high">
              <div class="stat-number">{{ alertStats.high }}</div>
              <div class="stat-label">高危</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item medium">
              <div class="stat-number">{{ alertStats.medium }}</div>
              <div class="stat-label">中等</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item low">
              <div class="stat-number">{{ alertStats.low }}</div>
              <div class="stat-label">低危</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 告警筛选 -->
      <div class="alert-filters">
        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <el-select 
              v-model="filters.severity" 
              placeholder="告警级别"
              clearable
              @change="applyFilters"
            >
              <el-option label="全部级别" value="" />
              <el-option label="严重" value="critical" />
              <el-option label="高危" value="high" />
              <el-option label="中等" value="medium" />
              <el-option label="低危" value="low" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select 
              v-model="filters.status" 
              placeholder="处理状态"
              clearable
              @change="applyFilters"
            >
              <el-option label="全部状态" value="" />
              <el-option label="未处理" value="unresolved" />
              <el-option label="处理中" value="acknowledged" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已忽略" value="ignored" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select 
              v-model="filters.source" 
              placeholder="告警来源"
              clearable
              @change="applyFilters"
            >
              <el-option label="全部来源" value="" />
              <el-option label="系统监控" value="system" />
              <el-option label="应用服务" value="application" />
              <el-option label="数据库" value="database" />
              <el-option label="网络设备" value="network" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="filters.search"
              placeholder="搜索告警标题"
              clearable
              @input="debounceSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <!-- 告警列表 -->
      <div class="alerts-list">
        <div class="alert-tabs">
          <el-tabs v-model="activeTab" @tab-click="handleTabClick">
            <el-tab-pane label="全部告警" name="all">
              <AlertList 
                :alerts="filteredAlerts" 
                :loading="loading"
                @resolve="resolveAlert"
                @acknowledge="acknowledgeAlert"
                @ignore="ignoreAlert"
              />
            </el-tab-pane>
            <el-tab-pane label="未处理" name="unresolved">
              <AlertList 
                :alerts="unresolvedAlerts" 
                :loading="loading"
                @resolve="resolveAlert"
                @acknowledge="acknowledgeAlert"
                @ignore="ignoreAlert"
              />
            </el-tab-pane>
            <el-tab-pane label="最近24小时" name="recent">
              <AlertList 
                :alerts="recentAlerts" 
                :loading="loading"
                @resolve="resolveAlert"
                @acknowledge="acknowledgeAlert"
                @ignore="ignoreAlert"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-card>

    <!-- 创建告警对话框 -->
    <el-dialog 
      v-model="showCreateAlert" 
      title="创建告警规则" 
      width="700px"
    >
      <el-form 
        :model="alertForm" 
        :rules="alertRules" 
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="告警标题" prop="title">
              <el-input v-model="alertForm.title" placeholder="请输入告警标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="告警级别" prop="severity">
              <el-select v-model="alertForm.severity" placeholder="选择告警级别">
                <el-option label="严重" value="critical" />
                <el-option label="高危" value="high" />
                <el-option label="中等" value="medium" />
                <el-option label="低危" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="告警来源" prop="source">
          <el-select v-model="alertForm.source" placeholder="选择告警来源">
            <el-option label="系统监控" value="system" />
            <el-option label="应用服务" value="application" />
            <el-option label="数据库" value="database" />
            <el-option label="网络设备" value="network" />
            <el-option label="安全检测" value="security" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="告警条件" prop="condition">
          <el-input 
            v-model="alertForm.condition" 
            type="textarea" 
            :rows="3"
            placeholder='例如: CPU使用率 > 80% 持续5分钟'
          />
        </el-form-item>
        
        <el-form-item label="通知方式" prop="notifications">
          <el-checkbox-group v-model="alertForm.notifications">
            <el-checkbox label="email">邮件通知</el-checkbox>
            <el-checkbox label="sms">短信通知</el-checkbox>
            <el-checkbox label="webhook">Webhook</el-checkbox>
            <el-checkbox label="dingtalk">钉钉群</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="告警描述" prop="description">
          <el-input 
            v-model="alertForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="请输入告警规则的详细描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateAlert = false">取消</el-button>
          <el-button type="primary" @click="createAlertRule">
            创建规则
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, Plus, Refresh, Search } from '@element-plus/icons-vue'
import AlertList from './AlertList.vue'

// 响应式数据
const loading = ref(false)
const showCreateAlert = ref(false)

// 过滤器
const filters = reactive({
  severity: '',
  status: '',
  source: '',
  search: ''
})

// 活动标签页
const activeTab = ref('all')

// 告警表单
const alertForm = reactive({
  title: '',
  severity: '',
  source: '',
  condition: '',
  notifications: [],
  description: ''
})

// 表单验证规则
const alertRules = {
  title: [{ required: true, message: '请输入告警标题', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择告警级别', trigger: 'change' }],
  source: [{ required: true, message: '请选择告警来源', trigger: 'change' }],
  condition: [{ required: true, message: '请输入告警条件', trigger: 'blur' }]
}

// 模拟告警数据
const alerts = ref([
  {
    id: 1,
    title: 'CPU使用率过高',
    severity: 'critical',
    status: 'unresolved',
    source: 'system',
    condition: 'CPU使用率 > 90%',
    description: '服务器CPU使用率持续超过90%，可能影响系统性能',
    created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    acknowledged_by: null
  },
  {
    id: 2,
    title: '数据库连接池耗尽',
    severity: 'high',
    status: 'acknowledged',
    source: 'database',
    condition: '连接池使用率 = 100%',
    description: '数据库连接池已满，新请求无法获取数据库连接',
    created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    acknowledged_by: 'admin'
  },
  {
    id: 3,
    title: '内存使用率警告',
    severity: 'medium',
    status: 'resolved',
    source: 'system',
    condition: '内存使用率 > 80%',
    description: '服务器内存使用率达到80%，建议进行优化',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    acknowledged_by: 'operator'
  },
  {
    id: 4,
    title: 'API响应时间过长',
    severity: 'high',
    status: 'unresolved',
    source: 'application',
    condition: 'API响应时间 > 5s',
    description: '主要API接口响应时间超过5秒，用户体验受影响',
    created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
    acknowledged_by: null
  },
  {
    id: 5,
    title: '磁盘空间不足',
    severity: 'low',
    status: 'ignored',
    source: 'system',
    condition: '磁盘使用率 > 85%',
    description: '日志分区磁盘使用率较高，需要清理历史日志',
    created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    acknowledged_by: 'admin'
  }
])

// 计算属性
const filteredAlerts = computed(() => {
  let result = alerts.value
  
  // 严重程度过滤
  if (filters.severity) {
    result = result.filter(alert => alert.severity === filters.severity)
  }
  
  // 状态过滤
  if (filters.status) {
    result = result.filter(alert => alert.status === filters.status)
  }
  
  // 来源过滤
  if (filters.source) {
    result = result.filter(alert => alert.source === filters.source)
  }
  
  // 搜索过滤
  if (filters.search) {
    const search = filters.search.toLowerCase()
    result = result.filter(alert => 
      alert.title.toLowerCase().includes(search) ||
      alert.description.toLowerCase().includes(search)
    )
  }
  
  return result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const unresolvedAlerts = computed(() => {
  return filteredAlerts.value.filter(alert => alert.status === 'unresolved')
})

const recentAlerts = computed(() => {
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000)
  return filteredAlerts.value.filter(alert => 
    new Date(alert.created_at) > yesterday
  )
})

const alertStats = computed(() => {
  return {
    critical: alerts.value.filter(a => a.severity === 'critical').length,
    high: alerts.value.filter(a => a.severity === 'high').length,
    medium: alerts.value.filter(a => a.severity === 'medium').length,
    low: alerts.value.filter(a => a.severity === 'low').length
  }
})

const unreadCount = computed(() => {
  return alerts.value.filter(a => a.status === 'unresolved').length
})

// 方法
const refreshAlerts = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('告警列表已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  // 过滤器已在计算属性中实时生效
}

const debounceSearch = (() => {
  let timer = null
  return (value) => {
    clearTimeout(timer)
    timer = setTimeout(() => {
      applyFilters()
    }, 300)
  }
})()

const handleTabClick = (tab) => {
  activeTab.value = tab.name
}

const resolveAlert = async (alert) => {
  try {
    await ElMessageBox.confirm(`确定要标记告警 "${alert.title}" 为已解决吗？`, '确认解决')
    alert.status = 'resolved'
    alert.updated_at = new Date().toISOString()
    ElMessage.success('告警已标记为已解决')
  } catch {
    // 用户取消
  }
}

const acknowledgeAlert = async (alert) => {
  try {
    await ElMessageBox.confirm(`确定要确认告警 "${alert.title}" 吗？`, '确认确认')
    alert.status = 'acknowledged'
    alert.acknowledged_by = 'current_user'
    alert.updated_at = new Date().toISOString()
    ElMessage.success('告警已确认')
  } catch {
    // 用户取消
  }
}

const ignoreAlert = async (alert) => {
  try {
    await ElMessageBox.confirm(`确定要忽略告警 "${alert.title}" 吗？`, '确认忽略')
    alert.status = 'ignored'
    alert.updated_at = new Date().toISOString()
    ElMessage.success('告警已忽略')
  } catch {
    // 用户取消
  }
}

const createAlertRule = async () => {
  try {
    // 简单验证
    if (!alertForm.title || !alertForm.severity || !alertForm.source || !alertForm.condition) {
      ElMessage.error('请填写必填字段')
      return
    }
    
    // 模拟创建告警规则
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newAlert = {
      id: Date.now(),
      ...alertForm,
      status: 'unresolved',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      acknowledged_by: null
    }
    
    alerts.value.unshift(newAlert)
    ElMessage.success('告警规则创建成功')
    showCreateAlert.value = false
    
    // 重置表单
    Object.assign(alertForm, {
      title: '',
      severity: '',
      source: '',
      condition: '',
      notifications: [],
      description: ''
    })
    
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 生命周期
onMounted(() => {
  refreshAlerts()
})

// 暴露方法
defineExpose({
  refreshAlerts,
  alerts
})
</script>

<style scoped>
.system-alerts {
  width: 100%;
}

.alerts-card {
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

.card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-badge {
  margin-right: 8px;
}

.alert-stats {
  margin-bottom: 24px;
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  border-radius: 6px;
  color: white;
}

.stat-item.critical {
  background: linear-gradient(135deg, #f56c6c, #e74c3c);
}

.stat-item.high {
  background: linear-gradient(135deg, #e6a23c, #f39c12);
}

.stat-item.medium {
  background: linear-gradient(135deg, #409eff, #3498db);
}

.stat-item.low {
  background: linear-gradient(135deg, #67c23a, #27ae60);
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.9;
}

.alert-filters {
  margin-bottom: 20px;
}

.filter-row {
  margin-bottom: 16px;
}

.alerts-list {
  min-height: 400px;
}

.alert-tabs {
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: center;
  }
  
  .filter-row .el-col {
    margin-bottom: 12px;
  }
  
  .stat-item {
    padding: 12px 8px;
  }
  
  .stat-number {
    font-size: 20px;
  }
}</style>