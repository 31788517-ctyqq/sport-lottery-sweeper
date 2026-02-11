<template>
  <div class="system-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>⚙️ 系统管理</h3>
            <p class="subtitle">系统配置、监控和维护</p>
          </div>
        </div>
      </template>

      <!-- 系统概览 -->
      <el-row :gutter="20" class="overview-stats">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <i class="el-icon-monitor" />
              </div>
              <div class="stat-info">
                <div class="stat-label">服务器状态</div>
                <div class="stat-value">正常</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <i class="el-icon-timer" />
              </div>
              <div class="stat-info">
                <div class="stat-label">运行时间</div>
                <div class="stat-value">{{ uptime }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <i class="el-icon-data-analysis" />
              </div>
              <div class="stat-info">
                <div class="stat-label">CPU使用率</div>
                <div class="stat-value">{{ cpuUsage }}%</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <i class="el-icon-files" />
              </div>
              <div class="stat-info">
                <div class="stat-label">内存使用率</div>
                <div class="stat-value">{{ memoryUsage }}%</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 系统配置选项卡 -->
      <el-tabs v-model="activeTab" class="system-tabs" type="border-card">
        <el-tab-pane label="系统配置" name="config">
          <el-form :model="configForm" label-width="150px" style="max-width: 800px; margin-top: 20px;">
            <el-form-item label="系统名称">
              <el-input v-model="configForm.systemName" placeholder="输入系统名称" />
            </el-form-item>
            
            <el-form-item label="最大并发数">
              <el-input-number v-model="configForm.maxConcurrency" :min="1" :max="100" />
            </el-form-item>
            
            <el-form-item label="数据保留天数">
              <el-input-number v-model="configForm.dataRetentionDays" :min="1" :max="365" />
            </el-form-item>
            
            <el-form-item label="API请求频率限制">
              <el-input-number v-model="configForm.apiRateLimit" :min="1" :max="10000" />
            </el-form-item>
            
            <el-form-item label="日志级别">
              <el-select v-model="configForm.logLevel" placeholder="选择日志级别">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
              <el-button @click="resetConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="系统监控" name="monitoring">
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card header="CPU使用率">
                <div ref="cpuChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card header="内存使用率">
                <div ref="memoryChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <el-card header="API请求统计">
                <div ref="apiChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card header="数据库连接">
                <div ref="dbChart" class="chart-container" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="系统日志" name="logs">
          <div style="margin-top: 20px;">
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="6">
                <el-select v-model="logLevelFilter" placeholder="日志级别" style="width: 100%;">
                  <el-option label="ALL" value="" />
                  <el-option label="DEBUG" value="debug" />
                  <el-option label="INFO" value="info" />
                  <el-option label="WARNING" value="warning" />
                  <el-option label="ERROR" value="error" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-date-picker
                  v-model="logDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :span="6">
                <el-button type="primary" @click="fetchLogs">查询日志</el-button>
              </el-col>
            </el-row>

            <el-table :data="logEntries" style="width: 100%" stripe height="400">
              <el-table-column prop="timestamp" label="时间" width="180" />
              <el-table-column prop="level" label="级别" width="100">
                <template #default="scope">
                  <el-tag :type="getLogLevelType(scope.row.level)">
                    {{ scope.row.level.toUpperCase() }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息" show-overflow-tooltip />
              <el-table-column prop="module" label="模块" width="150" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="维护工具" name="maintenance">
          <div style="margin-top: 20px;">
            <el-card header="系统维护工具">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>清理缓存</h4>
                    <p>清除系统缓存数据，释放内存空间</p>
                    <el-button type="warning" @click="clearCache">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>备份数据</h4>
                    <p>创建系统数据的完整备份</p>
                    <el-button type="primary" @click="backupData">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>清理日志</h4>
                    <p>删除过期的日志文件</p>
                    <el-button type="danger" @click="cleanupLogs">执行</el-button>
                  </div>
                </el-col>
              </el-row>
              
              <el-divider />
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>重启服务</h4>
                    <p>重启系统服务（谨慎操作）</p>
                    <el-button type="danger" @click="restartService">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>更新配置</h4>
                    <p>重新加载系统配置文件</p>
                    <el-button type="info" @click="reloadConfig">执行</el-button>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="maintenance-tool">
                    <h4>健康检查</h4>
                    <p>执行系统健康状态检查</p>
                    <el-button type="success" @click="performHealthCheck">执行</el-button>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="数据备份" name="backup">
          <div style="margin-top: 20px;">
            <el-card header="数据备份管理">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="maintenance-tool">
                    <h4>数据库备份</h4>
                    <p>创建数据库的完整备份文件</p>
                    <el-button type="primary" @click="backupDatabase">立即备份</el-button>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="maintenance-tool">
                    <h4>文件备份</h4>
                    <p>备份系统配置文件和数据文件</p>
                    <el-button type="success" @click="backupFiles">开始备份</el-button>
                  </div>
                </el-col>
              </el-row>
              
              <el-divider />
              
              <el-row :gutter="20">
                <el-col :span="24">
                  <h4>备份历史记录</h4>
                  <el-table :data="backupHistory" style="width: 100%; margin-top: 20px;" stripe>
                    <el-table-column prop="date" label="备份日期" width="180" />
                    <el-table-column prop="type" label="备份类型" width="120" />
                    <el-table-column prop="size" label="文件大小" width="120" />
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">
                          {{ scope.row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="200">
                      <template #default="scope">
                        <el-button size="small" @click="restoreBackup(scope.row)">恢复</el-button>
                        <el-button size="small" type="danger" @click="deleteBackup(scope.row)">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
              </el-row>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane label="API管理" name="api">
          <div style="margin-top: 20px;">
            <el-card header="API配置管理">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="maintenance-tool">
                    <h4>API接口状态</h4>
                    <p>查看和管理所有API接口的运行状态</p>
                    <el-button type="primary" @click="checkAPIStatus">检查状态</el-button>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="maintenance-tool">
                    <h4>API访问控制</h4>
                    <p>配置API访问权限和速率限制</p>
                    <el-button type="success" @click="manageAPIAccess">管理访问</el-button>
                  </div>
                </el-col>
              </el-row>
              
              <el-divider />
              
              <el-row :gutter="20">
                <el-col :span="24">
                  <h4>API端点列表</h4>
                  <el-table :data="apiEndpoints" style="width: 100%; margin-top: 20px;" stripe>
                    <el-table-column prop="path" label="路径" />
                    <el-table-column prop="method" label="方法" width="100" />
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.status === '正常' ? 'success' : 'danger'">
                          {{ scope.row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="requests" label="请求次数" width="120" />
                    <el-table-column label="操作" width="200">
                      <template #default="scope">
                        <el-button size="small" @click="testAPI(scope.row)">测试</el-button>
                        <el-button size="small" type="info" @click="viewAPIDocs(scope.row)">文档</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
              </el-row>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import * as systemAPI from '@/api/system.js'

// 响应式数据
const activeTab = ref('config')
const uptime = ref('7天12时34分')  // 修改默认值格式
const cpuUsage = ref(45)
const memoryUsage = ref(62)

// 格式化运行时间显示
const formatUptime = (uptimeStr) => {
  if (!uptimeStr) return '0天0时0分'
  
  // 处理 "7天 12小时 34分钟" -> "7天12时34分"
  let formatted = uptimeStr.trim()
  
  // 提取数字和单位
  const daysMatch = formatted.match(/(\d+)\s*天/)
  const hoursMatch = formatted.match(/(\d+)\s*小时/)
  const minutesMatch = formatted.match(/(\d+)\s*分钟/)
  
  const days = daysMatch ? daysMatch[1] : '0'
  const hours = hoursMatch ? hoursMatch[1] : '0'
  const minutes = minutesMatch ? minutesMatch[1] : '0'
  
  return `${days}天${hours}时${minutes}分`
}

// 路由处理
const route = useRoute()
console.log('route.meta:', route.meta)
console.log('route:', route)
// 根据路由meta.tab设置activeTab
watch(() => route.meta, (meta) => {
  const tab = meta?.tab
  if (tab) {
    activeTab.value = tab
  }
}, { immediate: true, deep: true })

// 配置表单
const configForm = ref({
  systemName: '体育彩票AI分析系统',
  maxConcurrency: 50,
  dataRetentionDays: 90,
  apiRateLimit: 1000,
  logLevel: 'info'
})

// 日志相关
const logLevelFilter = ref('')
const logDateRange = ref([])
const logEntries = ref([
  { id: 1, timestamp: '2023-05-01 10:30:15', level: 'info', message: '系统启动成功', module: 'core' },
  { id: 2, timestamp: '2023-05-01 10:31:22', level: 'warning', message: '数据库连接池接近上限', module: 'database' },
  { id: 3, timestamp: '2023-05-01 10:35:08', level: 'error', message: 'API请求超时', module: 'api' },
  { id: 4, timestamp: '2023-05-01 10:40:12', level: 'info', message: '数据同步完成', module: 'sync' },
  { id: 5, timestamp: '2023-05-01 10:45:33', level: 'debug', message: '调试信息输出', module: 'debug' },
])

// 图表引用
const cpuChart = ref(null)
const memoryChart = ref(null)
const apiChart = ref(null)
const dbChart = ref(null)

// 备份管理相关数据
const backupHistory = ref([
  { id: 1, date: '2023-05-01 14:30:00', type: '数据库备份', size: '2.5 GB', status: '成功' },
  { id: 2, date: '2023-04-28 10:15:00', type: '文件备份', size: '1.2 GB', status: '成功' },
  { id: 3, date: '2023-04-25 08:45:00', type: '数据库备份', size: '2.3 GB', status: '成功' },
  { id: 4, date: '2023-04-20 16:20:00', type: '文件备份', size: '1.1 GB', status: '失败' }
])

// API管理相关数据
const apiEndpoints = ref([
  { id: 1, path: '/api/v1/admin/system/status', method: 'GET', status: '正常', requests: 1200 },
  { id: 2, path: '/api/v1/admin/system/config', method: 'GET', status: '正常', requests: 850 },
  { id: 3, path: '/api/v1/admin/system/clear-cache', method: 'POST', status: '正常', requests: 45 },
  { id: 4, path: '/api/v1/admin/system/backup/database', method: 'POST', status: '正常', requests: 18 },
  { id: 5, path: '/api/v1/admin/system/api/endpoints', method: 'GET', status: '正常', requests: 320 }
])

// 方法
const saveConfig = async () => {
  try {
    // 这里暂时使用模拟保存，后续可以添加真正的配置保存API
    console.log('保存配置:', configForm.value)
    ElMessage.success('系统配置保存成功')
  } catch (error) {
    ElMessage.error(`保存失败: ${error.message}`)
  }
}

const resetConfig = () => {
  configForm.value = {
    systemName: '体育彩票AI分析系统',
    maxConcurrency: 50,
    dataRetentionDays: 90,
    apiRateLimit: 1000,
    logLevel: 'info'
  }
  ElMessage.info('配置已重置为默认值')
}

const fetchLogs = async () => {
  try {
    const params = {}
    if (logLevelFilter.value) {
      params.level = logLevelFilter.value
    }
    if (logDateRange.value && logDateRange.value.length === 2) {
      params.start_date = logDateRange.value[0].toISOString()
      params.end_date = logDateRange.value[1].toISOString()
    }
    const response = await systemAPI.getSystemLogs(params)
    if (response.success) {
      logEntries.value = response.data || []
      ElMessage.success(`获取到 ${logEntries.value.length} 条日志记录`)
    } else {
      ElMessage.warning(`获取日志失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`获取日志失败: ${error.message}`)
  }
}

const getLogLevelType = (level) => {
  switch (level.toLowerCase()) {
    case 'debug': return 'info'
    case 'info': return 'primary'
    case 'warning': return 'warning'
    case 'error': return 'danger'
    default: return 'info'
  }
}

// 加载系统状态信息
const loadSystemStatus = async () => {
  try {
    const [statusRes, statsRes] = await Promise.all([
      systemAPI.getSystemStatus(),
      systemAPI.getSystemStats()
    ])
    
    if (statusRes.success && statusRes.data) {
      const status = statusRes.data
      cpuUsage.value = Math.round(status.cpu_percent)
      memoryUsage.value = Math.round(status.memory.percent)
      // 处理运行时间显示
      if (status.uptime) {
        uptime.value = formatUptime(status.uptime)
      }
      // 可以添加更多状态显示
    }
    
    if (statsRes.success && statsRes.data) {
      // 可以更新系统统计信息
      console.log('系统统计:', statsRes.data)
    }
  } catch (error) {
    console.warn('加载系统状态失败:', error)
  }
}

// 维护工具方法
const clearCache = async () => {
  try {
    const response = await systemAPI.clearSystemCache()
    if (response.success) {
      ElMessage.success('缓存清理成功')
    } else {
      ElMessage.error(`清理失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`缓存清理失败: ${error.message}`)
  }
}

const backupData = () => {
  ElMessage.info('请使用专门的备份管理功能')
}

const cleanupLogs = async () => {
  try {
    const confirm = await ElMessageBox.confirm(
      '确定要清理所有系统日志吗？此操作不可恢复！',
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    if (confirm) {
      const response = await systemAPI.clearSystemLogs()
      if (response.success) {
        ElMessage.success('日志清理成功')
        fetchLogs()
      } else {
        ElMessage.error(`清理失败: ${response.message}`)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`日志清理失败: ${error.message}`)
    }
  }
}

const restartService = async () => {
  try {
    const confirm = await ElMessageBox.confirm(
      '确定要重启系统服务吗？这将暂时中断所有服务！',
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    if (confirm) {
      const response = await systemAPI.restartService()
      if (response.success) {
        ElMessage.success('服务重启指令已发送')
      } else {
        ElMessage.error(`重启失败: ${response.message}`)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`重启失败: ${error.message}`)
    }
  }
}

const reloadConfig = async () => {
  try {
    const response = await systemAPI.reloadConfig()
    if (response.success) {
      ElMessage.success('配置重载成功')
    } else {
      ElMessage.error(`重载失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`配置重载失败: ${error.message}`)
  }
}

const performHealthCheck = async () => {
  try {
    const response = await systemAPI.performHealthCheck()
    if (response.success) {
      ElMessage.success(`健康检查完成: ${response.message}`)
    } else {
      ElMessage.error(`健康检查失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`健康检查失败: ${error.message}`)
  }
}

// 备份管理方法
const backupDatabase = async () => {
  try {
    const confirm = await ElMessageBox.confirm(
      '确定要立即备份数据库吗？此操作可能需要几分钟时间。',
      '确认备份',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
    if (confirm) {
      const response = await systemAPI.createDatabaseBackup()
      if (response.success) {
        ElMessage.success('数据库备份任务已开始')
        // 刷新备份历史
        loadBackupHistory()
      } else {
        ElMessage.error(`备份失败: ${response.message}`)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`备份失败: ${error.message}`)
    }
  }
}

const backupFiles = async () => {
  try {
    const confirm = await ElMessageBox.confirm(
      '确定要备份系统文件吗？此操作可能需要几分钟时间。',
      '确认备份',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
    if (confirm) {
      const response = await systemAPI.createFileBackup()
      if (response.success) {
        ElMessage.success('文件备份任务已开始')
        // 刷新备份历史
        loadBackupHistory()
      } else {
        ElMessage.error(`备份失败: ${response.message}`)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`备份失败: ${error.message}`)
    }
  }
}

const loadBackupHistory = async () => {
  try {
    const response = await systemAPI.getBackupHistory()
    if (response.success) {
      backupHistory.value = response.data || []
    } else {
      ElMessage.warning(`获取备份历史失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`获取备份历史失败: ${error.message}`)
  }
}

const restoreBackup = async (backup) => {
  try {
    const confirm = await ElMessageBox.confirm(
      `确定要恢复备份 ${backup.date} (${backup.type}) 吗？当前数据将被覆盖！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    if (confirm) {
      const response = await systemAPI.restoreBackup(backup.id)
      if (response.success) {
        ElMessage.success('备份恢复任务已开始')
      } else {
        ElMessage.error(`恢复失败: ${response.message}`)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`恢复失败: ${error.message}`)
    }
  }
}

const deleteBackup = async (backup) => {
  try {
    const confirm = await ElMessageBox.confirm(
      `确定要删除备份 ${backup.date} (${backup.type}) 吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    if (confirm) {
      const response = await systemAPI.deleteBackup(backup.id)
      if (response.success) {
        ElMessage.success('备份已删除')
        // 刷新备份历史
        loadBackupHistory()
      } else {
        ElMessage.error(`删除失败: ${response.message}`)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

// API管理方法
const checkAPIStatus = async () => {
  try {
    const response = await systemAPI.getAPIEndpoints()
    if (response.success) {
      apiEndpoints.value = response.data || []
      ElMessage.success(`获取到 ${apiEndpoints.value.length} 个API端点信息`)
    } else {
      ElMessage.error(`获取API状态失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`获取API状态失败: ${error.message}`)
  }
}

const manageAPIAccess = async () => {
  try {
    const response = await systemAPI.getAPIAccessStats()
    if (response.success) {
      ElMessageBox.alert(
        `当前API访问统计：\n总请求数: ${response.data.total_requests}\n平均响应时间: ${response.data.avg_response_time}ms\n错误率: ${response.data.error_rate}%`,
        'API访问统计',
        { confirmButtonText: '确定' }
      )
    } else {
      ElMessage.error(`获取API统计失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`获取API统计失败: ${error.message}`)
  }
}

const testAPI = async (api) => {
  try {
    const response = await systemAPI.testAPIEndpoint(api.path, api.method)
    if (response.success) {
      ElMessage.success(`API测试成功: ${response.message}`)
    } else {
      ElMessage.error(`API测试失败: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`API测试失败: ${error.message}`)
  }
}

const viewAPIDocs = (api) => {
  ElMessage.info(`查看API文档: ${api.path}，将在后续版本中实现`)
}

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // 共用防抖函数
  const debounce = (func, delay) => {
    let timeoutId;
    return function (...args) {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  };

  // CPU使用率图表
  if (cpuChart.value) {
    const chart = echarts.init(cpuChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'] },
      yAxis: { type: 'value', name: '%' },
      series: [{ data: [20, 35, 40, 60, 55, 45, 30], type: 'line', smooth: true }]
    })
    const handleResize = debounce(() => chart?.resize(), 100)
    window.addEventListener('resize', handleResize)
    // 存储函数以便后续移除监听器（可选优化）
    chart.__resizeHandler = handleResize
  }

  // 内存使用率图表
  if (memoryChart.value) {
    const chart = echarts.init(memoryChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'] },
      yAxis: { type: 'value', name: '%' },
      series: [{ data: [45, 50, 65, 70, 68, 55, 50], type: 'line', smooth: true, itemStyle: { color: '#e74c3c' } }]
    })
    const handleResize = debounce(() => chart?.resize(), 100)
    window.addEventListener('resize', handleResize)
    chart.__resizeHandler = handleResize
  }

  // API请求统计图表
  if (apiChart.value) {
    const chart = echarts.init(apiChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['请求次数', '错误次数'] },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [
        { name: '请求次数', type: 'bar', data: [1200, 1320, 1010, 1340, 900, 2300, 2100] },
        { name: '错误次数', type: 'bar', data: [10, 15, 8, 12, 5, 20, 18] }
      ]
    })
    const handleResize = debounce(() => chart?.resize(), 100)
    window.addEventListener('resize', handleResize)
    chart.__resizeHandler = handleResize
  }

  // 数据库连接图表
  if (dbChart.value) {
    const chart = echarts.init(dbChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [
        {
          name: '连接状态',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 45, name: '活跃连接' },
            { value: 5, name: '等待连接' },
            { value: 2, name: '错误连接' },
            { value: 8, name: '空闲连接' }
          ],
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
          }
        }
      ]
    })
    const handleResize = debounce(() => chart?.resize(), 100)
    window.addEventListener('resize', handleResize)
    chart.__resizeHandler = handleResize
  }
}

onMounted(() => {
  console.log('SystemManagement component mounted')
  loadSystemStatus()
  loadBackupHistory()
  initCharts()
})
</script>

<style scoped>
.card-container {
  margin: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header > div:first-child h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.overview-stats {
  margin-bottom: 20px;
}

.stat-card {
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.bg-blue { background: #409eff; }
.bg-green { background: #67c23a; }
.bg-orange { background: #e6a23c; }
.bg-purple { background: #9013fe; }

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.system-tabs {
  margin-top: 20px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.maintenance-tool {
  padding: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  text-align: center;
}

.maintenance-tool h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.maintenance-tool p {
  color: #909399;
  font-size: 14px;
  margin: 0 0 15px 0;
}
</style>