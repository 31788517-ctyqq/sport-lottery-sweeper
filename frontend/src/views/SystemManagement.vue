<template>
  <div class="system-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">⚙️ 系统管理</h1>
      <p class="page-description">管理系统配置、服务器状态、日志和安全设置</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索系统项..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.category" @change="handleFilterChange">
          <option value="">全部类别</option>
          <option value="config">配置</option>
          <option value="monitoring">监控</option>
          <option value="security">安全</option>
          <option value="logs">日志</option>
          <option value="backup">备份</option>
        </select>
        
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="active">启用</option>
          <option value="inactive">禁用</option>
          <option value="warning">警告</option>
          <option value="error">错误</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="addSystemItem">
          <span>➕</span> 添加配置
        </button>
        <button class="action-btn secondary" @click="refreshSystemData">
          <span>🔄</span> 刷新
        </button>
        <button class="action-btn tertiary" @click="exportSystemConfig">
          <span>📤</span> 导出配置
        </button>
      </div>
    </div>

    <!-- 系统统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon server">
          <i class="icon-server">🖥️</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">服务器状态</div>
          <div class="stat-value">{{ systemStatus.serverStatus }}</div>
          <div class="stat-change positive">{{ systemStatus.cpuUsage }}% CPU使用率</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon memory">
          <i class="icon-memory">💾</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">内存使用</div>
          <div class="stat-value">{{ systemStatus.memoryUsage }}%</div>
          <div class="stat-change negative">{{ systemStatus.memoryAvailable }}GB 可用</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon storage">
          <i class="icon-storage">🗄️</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">存储空间</div>
          <div class="stat-value">{{ systemStatus.storageUsage }}%</div>
          <div class="stat-change negative">{{ systemStatus.storageAvailable }}GB 可用</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon uptime">
          <i class="icon-uptime">⏱️</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">运行时间</div>
          <div class="stat-value">{{ systemStatus.uptime }}</div>
          <div class="stat-change neutral">在线</div>
        </div>
      </div>
    </div>

    <!-- 系统配置部分 -->
    <div class="system-config-section">
      <div class="section-header">
        <h2>🔧 系统配置</h2>
      </div>
      
      <div class="config-grid">
        <div class="config-item" v-for="config in systemConfigs" :key="config.id">
          <div class="config-header">
            <h3>{{ config.name }}</h3>
            <span class="config-status" :class="config.status">{{ config.statusLabel }}</span>
          </div>
          <div class="config-details">
            <p class="config-description">{{ config.description }}</p>
            <div class="config-value">
              <span class="config-key">键名:</span> {{ config.key }}
            </div>
            <div class="config-value">
              <span class="config-key">值:</span> {{ config.value }}
            </div>
            <div class="config-actions">
              <button class="action-btn edit" @click="editConfig(config)">编辑</button>
              <button class="action-btn delete" @click="deleteConfig(config)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 监控部分 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h2>📈 系统监控</h2>
      </div>
      
      <div class="monitoring-grid">
        <div class="metric-card">
          <div class="metric-header">
            <h3>CPU 使用率</h3>
            <span class="metric-value">{{ systemStatus.cpuUsage }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill cpu" :style="{ width: systemStatus.cpuUsage + '%' }"></div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <h3>内存使用率</h3>
            <span class="metric-value">{{ systemStatus.memoryUsage }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill memory" :style="{ width: systemStatus.memoryUsage + '%' }"></div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <h3>磁盘使用率</h3>
            <span class="metric-value">{{ systemStatus.storageUsage }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill storage" :style="{ width: systemStatus.storageUsage + '%' }"></div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <h3>网络流量</h3>
            <span class="metric-value">{{ systemStatus.networkTraffic }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill network" :style="{ width: 70 + '%' }"></div>
          </div>
        </div>
      </div>
      
      <!-- 实时监控图表 -->
      <div class="realtime-monitoring">
        <div class="chart-container">
          <h3>CPU 使用率趋势</h3>
          <div class="chart-placeholder">
            <canvas id="cpuChart" width="400" height="200"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <h3>内存使用趋势</h3>
          <div class="chart-placeholder">
            <canvas id="memoryChart" width="400" height="200"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <h3>磁盘 I/O</h3>
          <div class="chart-placeholder">
            <canvas id="diskIoChart" width="400" height="200"></canvas>
          </div>
        </div>
        <div class="chart-container">
          <h3>网络流量</h3>
          <div class="chart-placeholder">
            <canvas id="networkChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 日志部分 -->
    <div class="logs-section">
      <div class="section-header">
        <h2>📝 系统日志</h2>
        <div class="logs-actions">
          <button class="action-btn secondary" @click="clearLogs">清空日志</button>
          <button class="action-btn tertiary" @click="downloadLogs">下载日志</button>
        </div>
      </div>
      
      <div class="logs-table-container">
        <table class="logs-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>级别</th>
              <th>消息</th>
              <th>来源</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in recentLogs" :key="log.id">
              <td>{{ formatDateTime(log.timestamp) }}</td>
              <td>
                <span class="log-level" :class="log.level.toLowerCase()">
                  {{ log.level }}
                </span>
              </td>
              <td>{{ log.message }}</td>
              <td>{{ log.source }}</td>
              <td>
                <button class="action-btn view" @click="viewLogDetails(log)">详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加/编辑配置对话框 -->
    <div v-if="showConfigModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content medium-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingConfig ? '编辑配置' : '添加配置' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>配置名称 *</label>
            <input 
              v-model="currentConfig.name" 
              type="text" 
              placeholder="配置项名称"
            />
          </div>
          
          <div class="form-group">
            <label>键名 *</label>
            <input 
              v-model="currentConfig.key" 
              type="text" 
              placeholder="配置项键名"
            />
          </div>
          
          <div class="form-group">
            <label>值</label>
            <input 
              v-model="currentConfig.value" 
              type="text" 
              placeholder="配置项值"
            />
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="currentConfig.description" 
              placeholder="配置项描述"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>状态</label>
              <select v-model="currentConfig.status">
                <option value="active">启用</option>
                <option value="inactive">禁用</option>
                <option value="warning">警告</option>
                <option value="error">错误</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>类别</label>
              <select v-model="currentConfig.category">
                <option value="config">配置</option>
                <option value="monitoring">监控</option>
                <option value="security">安全</option>
                <option value="logs">日志</option>
                <option value="backup">备份</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveConfig"
            :disabled="!isValidConfig"
          >
            {{ editingConfig ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 日志详情对话框 -->
    <div v-if="showLogDetailModal" class="modal-overlay" @click="closeLogDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>日志详情</h3>
          <button class="close-btn" @click="closeLogDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">时间</div>
            <div class="detail-value">{{ formatDateTime(selectedLog.timestamp) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">级别</div>
            <div class="detail-value">
              <span class="log-level" :class="selectedLog.level.toLowerCase()">
                {{ selectedLog.level }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">来源</div>
            <div class="detail-value">{{ selectedLog.source }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">消息</div>
            <div class="detail-value">{{ selectedLog.message }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">详细信息</div>
            <div class="detail-value">
              <pre class="log-details">{{ selectedLog.details || '无详细信息' }}</pre>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeLogDetailModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 模拟系统配置数据
const systemConfigs = ref([
  {
    id: 1,
    name: '数据库连接池大小',
    key: 'database.pool.size',
    value: '20',
    description: '数据库连接池的最大连接数',
    status: 'active',
    statusLabel: '启用',
    category: 'config'
  },
  {
    id: 2,
    name: 'API请求超时',
    key: 'api.request.timeout',
    value: '30000',
    description: 'API请求的超时时间（毫秒）',
    status: 'active',
    statusLabel: '启用',
    category: 'config'
  },
  {
    id: 3,
    name: '日志保留天数',
    key: 'logging.retention.days',
    value: '30',
    description: '系统日志保留天数',
    status: 'active',
    statusLabel: '启用',
    category: 'logs'
  },
  {
    id: 4,
    name: '安全加密算法',
    key: 'security.encryption.algorithm',
    value: 'AES-256-GCM',
    description: '系统数据加密算法',
    status: 'warning',
    statusLabel: '警告',
    category: 'security'
  },
  {
    id: 5,
    name: '缓存过期时间',
    key: 'cache.expiration.time',
    value: '3600',
    description: '缓存数据过期时间（秒）',
    status: 'active',
    statusLabel: '启用',
    category: 'config'
  }
])

// 模拟系统状态数据
const systemStatus = ref({
  serverStatus: '运行中',
  cpuUsage: 65,
  memoryUsage: 72,
  memoryAvailable: 4.2,
  storageUsage: 45,
  storageAvailable: 234.5,
  uptime: '15天 8小时 32分钟',
  networkTraffic: '12.4 MB/s'
})

// 模拟最近日志
const recentLogs = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 300000),
    level: 'INFO',
    message: '系统启动成功',
    source: 'System',
    details: '系统已成功启动，所有服务正常运行'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 240000),
    level: 'WARN',
    message: '数据库连接池使用率超过80%',
    source: 'Database',
    details: '数据库连接池当前使用率85%，建议增加连接数'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 180000),
    level: 'ERROR',
    message: 'API请求超时',
    source: 'API',
    details: '请求 /api/v1/matches 超时，耗时超过设定阈值'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 120000),
    level: 'INFO',
    message: '用户登录成功',
    source: 'Auth',
    details: '用户 admin 登录成功，IP: 192.168.1.100'
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 60000),
    level: 'DEBUG',
    message: '数据同步完成',
    source: 'Sync',
    details: '与第三方数据源同步完成，新增数据 245 条'
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  category: '',
  status: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 配置模态框
const showConfigModal = ref(false)
const editingConfig = ref(null)
const currentConfig = ref({
  id: null,
  name: '',
  key: '',
  value: '',
  description: '',
  status: 'active',
  statusLabel: '启用',
  category: 'config'
})

// 日志详情模态框
const showLogDetailModal = ref(false)
const selectedLog = ref({})

// 定时器ID
let monitorInterval = null

// 计算属性
const filteredConfigs = computed(() => {
  let configs = [...systemConfigs.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    configs = configs.filter(config => 
      config.name.toLowerCase().includes(keyword) ||
      config.key.toLowerCase().includes(keyword) ||
      config.description.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.category) {
    configs = configs.filter(config => config.category === filters.value.category)
  }
  
  if (filters.value.status) {
    configs = configs.filter(config => config.status === filters.value.status)
  }
  
  return configs
})

const paginatedConfigs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredConfigs.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredConfigs.value.length / pageSize.value)
})

const isValidConfig = computed(() => {
  return currentConfig.value.name.trim() !== '' && 
         currentConfig.value.key.trim() !== '' &&
         currentConfig.value.value.trim() !== ''
})

// 更新系统状态的方法
const updateSystemStatus = () => {
  // 模拟系统指标的随机波动
  systemStatus.value.cpuUsage = Math.max(10, Math.min(95, systemStatus.value.cpuUsage + (Math.random() * 10 - 5)))
  systemStatus.value.memoryUsage = Math.max(20, Math.min(90, systemStatus.value.memoryUsage + (Math.random() * 8 - 4)))
  systemStatus.value.storageUsage = Math.max(10, Math.min(80, systemStatus.value.storageUsage + (Math.random() * 5 - 2.5)))
  systemStatus.value.networkTraffic = (Math.random() * 20 + 5).toFixed(1) + ' MB/s'
}

// 方法
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
  currentPage.value = 1
}

const handleFilterChange = () => {
  console.log('筛选条件改变:', filters.value)
  currentPage.value = 1
}

const refreshSystemData = () => {
  console.log('刷新系统数据')
  // 在实际应用中，这里会调用API获取最新数据
  updateSystemStatus()
  alert('系统数据已刷新')
}

const addSystemItem = () => {
  editingConfig.value = null
  currentConfig.value = {
    id: null,
    name: '',
    key: '',
    value: '',
    description: '',
    status: 'active',
    statusLabel: '启用',
    category: 'config'
  }
  showConfigModal.value = true
}

const editConfig = (config) => {
  editingConfig.value = config
  currentConfig.value = { ...config }
  showConfigModal.value = true
}

const closeModal = () => {
  showConfigModal.value = false
  editingConfig.value = null
}

const saveConfig = () => {
  if (!isValidConfig.value) return
  
  if (editingConfig.value) {
    // 更新现有配置
    const index = systemConfigs.value.findIndex(c => c.id === editingConfig.value.id)
    if (index !== -1) {
      systemConfigs.value[index] = { ...currentConfig.value, id: editingConfig.value.id }
    }
  } else {
    // 添加新配置
    const newId = Math.max(...systemConfigs.value.map(c => c.id)) + 1
    systemConfigs.value.push({
      ...currentConfig.value,
      id: newId
    })
  }
  
  closeModal()
}

const deleteConfig = (config) => {
  if (confirm(`确定要删除配置 "${config.name}" 吗？`)) {
    const index = systemConfigs.value.indexOf(config)
    if (index !== -1) {
      systemConfigs.value.splice(index, 1)
    }
  }
}

const viewLogDetails = (log) => {
  selectedLog.value = log
  showLogDetailModal.value = true
}

const closeLogDetailModal = () => {
  showLogDetailModal.value = false
  selectedLog.value = {}
}

const clearLogs = () => {
  if (confirm('确定要清空所有日志吗？此操作不可撤销！')) {
    recentLogs.value = []
  }
}

const downloadLogs = () => {
  console.log('下载日志...')
  // 在实际应用中，这里会导出日志到文件
  alert('正在下载系统日志文件...')
}

const exportSystemConfig = () => {
  console.log('导出系统配置...')
  // 在实际应用中，这里会导出配置到文件
  alert('正在导出系统配置文件...')
}

const formatDateTime = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 初始化数据
onMounted(() => {
  console.log('System Management 页面已加载')
  
  // 启动定时更新系统状态
  monitorInterval = setInterval(updateSystemStatus, 3000)
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (monitorInterval) {
    clearInterval(monitorInterval)
  }
})
</script>

<style scoped>
.system-management-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 工具栏样式 */
.toolbar {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 10px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-btn:hover {
  background: #2563eb;
}

.filters {
  display: flex;
  gap: 12px;
}

.filters select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn.primary {
  background: #10b981;
  color: white;
}

.action-btn.primary:hover {
  background: #059669;
}

.action-btn.secondary {
  background: #6366f1;
  color: white;
}

.action-btn.secondary:hover {
  background: #4f46e5;
}

.action-btn.tertiary {
  background: #f59e0b;
  color: white;
}

.action-btn.tertiary:hover {
  background: #d97706;
}

.action-btn.view {
  background: #e5e7eb;
  color: #374151;
  padding: 6px 10px;
}

.action-btn.view:hover {
  background: #d1d5db;
}

.action-btn.edit {
  background: #94a3b8;
  color: white;
  padding: 6px 10px;
}

.action-btn.edit:hover {
  background: #64748b;
}

.action-btn.delete {
  background: #ef4444;
  color: white;
  padding: 6px 10px;
}

.action-btn.delete:hover {
  background: #dc2626;
}

/* 统计卡片样式 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.server {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.memory {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.storage {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.uptime {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.negative {
  color: #dc2626;
}

.stat-change.neutral {
  color: #6b7280;
}

/* 系统配置部分 */
.system-config-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.section-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.config-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #f9fafb;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.config-status {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.config-status.active {
  background: #dcfce7;
  color: #166534;
}

.config-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.config-status.error {
  background: #fee2e2;
  color: #b91c1c;
}

.config-status.inactive {
  background: #e5e7eb;
  color: #374151;
}

.config-description {
  font-size: 14px;
  color: #6b7280;
  margin: 8px 0;
}

.config-value {
  margin: 8px 0;
  font-size: 14px;
}

.config-key {
  font-weight: 600;
  color: #374151;
}

.config-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

/* 实时监控图表 */
.realtime-monitoring {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.chart-container h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.chart-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
  border-radius: 8px;
}

/* 监控部分 */
.monitoring-section {
  margin-top: 32px;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
}

.progress-fill.cpu {
  background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.progress-fill.memory {
  background: linear-gradient(90deg, #10b981, #059669);
}

.progress-fill.storage {
  background: linear-gradient(90deg, #8b5cf6, #7c3aed);
}

.progress-fill.network {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

/* 日志部分 */
.logs-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.logs-actions {
  display: flex;
  gap: 8px;
}

.logs-table-container {
  overflow-x: auto;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th,
.logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.logs-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.logs-table tbody tr:hover {
  background-color: #f9fafb;
}

.log-level {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.log-level.info {
  background: #dbeafe;
  color: #1e40af;
}

.log-level.warn {
  background: #fef3c7;
  color: #92400e;
}

.log-level.error {
  background: #fee2e2;
  color: #b91c1c;
}

.log-level.debug {
  background: #ddd6fe;
  color: #5b21b6;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.2);
}

.medium-modal {
  width: 600px;
  max-width: 90vw;
  max-height: 70vh;
}

.large-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #9ca3af;
}

.close-btn:hover {
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group.half-width {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1f2937;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-row.full-width {
  flex-direction: column;
}

.detail-label {
  width: 120px;
  font-weight: 600;
  color: #374151;
}

.detail-value {
  flex: 1;
  color: #6b7280;
}

.log-details {
  background: #f3f4f6;
  padding: 12px;
  border-radius: 8px;
  font-family: monospace;
  white-space: pre-wrap;
  overflow-x: auto;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn.cancel:hover {
  background: #e5e7eb;
}

.btn.primary {
  background: #3b82f6;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn.primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .system-management-container {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .monitoring-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .modal-content {
    width: 95vw;
  }
  
  .medium-modal {
    width: 95vw;
  }
  
  .large-modal {
    width: 95vw;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: auto;
    margin-bottom: 4px;
  }
}
</style>