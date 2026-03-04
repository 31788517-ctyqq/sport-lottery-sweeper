<template>
  <div class="crawler-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">🕷️ 爬虫管理</h1>
      <p class="page-description">管理爬虫任务、配置和监控状态</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索爬虫任务..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="running">运行中</option>
          <option value="paused">已暂停</option>
          <option value="stopped">已停止</option>
          <option value="error">错误</option>
        </select>
        
        <select v-model="filters.dataSource" @change="handleFilterChange">
          <option value="">全部数据源</option>
          <option value="five_hundred">500彩票网</option>
          <option value="bet365">Bet365</option>
          <option value="odds">赔率数据源</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="addNewTask">
          <span>➕</span> 新建任务
        </button>
        <button class="action-btn secondary" @click="refreshTasks">
          <span>🔄</span> 刷新
        </button>
      </div>
    </div>

    <!-- 爬虫任务列表 -->
    <div class="tasks-section">
      <div class="section-header">
        <h2>📋 爬虫任务</h2>
        <div class="task-stats">
          <span class="stat-item">总数: {{ crawlerTasks.length }}</span>
          <span class="stat-item running">运行中: {{ runningTasksCount }}</span>
          <span class="stat-item paused">暂停: {{ pausedTasksCount }}</span>
          <span class="stat-item stopped">停止: {{ stoppedTasksCount }}</span>
          <span class="stat-item error">错误: {{ errorTasksCount }}</span>
        </div>
      </div>
      
      <div class="task-list">
        <div v-for="task in filteredTasks" :key="task.id" class="task-item">
          <div class="task-info">
            <div class="task-name">{{ task.name }}</div>
            <div class="task-details">
              <span class="task-source">{{ task.dataSource }}</span>
              <span class="task-frequency">频率: {{ task.frequency }}分钟</span>
              <span class="task-last-run">上次运行: {{ formatTime(task.lastRun) }}</span>
            </div>
          </div>
          
          <div class="task-status">
            <span class="status-badge" :class="task.status">{{ task.statusText }}</span>
            <span class="last-update">更新: {{ formatTime(task.lastUpdate) }}</span>
          </div>
          
          <div class="task-actions">
            <button 
              class="action-btn start" 
              @click="startTask(task)" 
              v-if="task.status !== 'running'"
              :disabled="task.status === 'starting'"
            >
              {{ task.status === 'starting' ? '启动中...' : '▶️ 启动' }}
            </button>
            <button 
              class="action-btn pause" 
              @click="pauseTask(task)" 
              v-else
              :disabled="task.status === 'stopping'"
            >
              {{ task.status === 'stopping' ? '停止中...' : '⏸️ 暂停' }}
            </button>
            
            <button class="action-btn edit" @click="editTask(task)">✏️ 编辑</button>
            <button class="action-btn log" @click="viewLog(task)">📋 日志</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态卡片 -->
    <div class="system-status-grid">
      <div class="status-card">
        <div class="status-header">
          <h3>🔧 爬虫服务状态</h3>
          <span class="status-indicator" :class="overallStatusClass"></span>
        </div>
        <div class="status-content">
          <div class="status-item">
            <span class="label">服务状态:</span>
            <span class="value" :class="overallStatusClass">{{ overallStatusText }}</span>
          </div>
          <div class="status-item">
            <span class="label">活跃任务数:</span>
            <span class="value highlight">{{ runningTasksCount }}</span>
          </div>
          <div class="status-item">
            <span class="label">总请求数:</span>
            <span class="value highlight">{{ stats.totalRequests }}</span>
          </div>
          <div class="status-item">
            <span class="label">成功率:</span>
            <span class="value highlight">{{ stats.successRate }}%</span>
          </div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-header">
          <h3>📊 今日统计</h3>
        </div>
        <div class="status-content">
          <div class="status-item">
            <span class="label">今日抓取:</span>
            <span class="value highlight">{{ stats.todayCrawled }} 条</span>
          </div>
          <div class="status-item">
            <span class="label">平均响应时间:</span>
            <span class="value highlight">{{ stats.avgResponseTime }}ms</span>
          </div>
          <div class="status-item">
            <span class="label">IP池状态:</span>
            <span class="value" :class="ipPoolStatusClass">{{ ipPoolStatusText }}</span>
          </div>
          <div class="status-item">
            <span class="label">错误数:</span>
            <span class="value highlight">{{ stats.errorCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑任务对话框 -->
    <div v-if="showTaskModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingTask ? '编辑爬虫任务' : '新建爬虫任务' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>任务名称 *</label>
            <input 
              v-model="currentTask.name" 
              type="text" 
              placeholder="输入任务名称"
              :disabled="!!editingTask"
            />
          </div>
          
          <div class="form-group">
            <label>数据源 *</label>
            <select v-model="currentTask.dataSource">
              <option value="five_hundred">500彩票网</option>
              <option value="bet365">Bet365</option>
              <option value="odds">赔率数据源</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>抓取频率(分钟) *</label>
            <input 
              v-model.number="currentTask.frequency" 
              type="number" 
              min="1" 
              max="1440"
              placeholder="输入抓取频率(1-1440分钟)"
            />
          </div>
          
          <div class="form-group">
            <label>启用代理</label>
            <div class="toggle-switch">
              <input 
                type="checkbox" 
                id="useProxy" 
                v-model="currentTask.useProxy"
              />
              <label for="useProxy">开启代理IP轮换</label>
            </div>
          </div>
          
          <div class="form-group">
            <label>任务描述</label>
            <textarea 
              v-model="currentTask.description" 
              placeholder="输入任务描述(可选)"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveTask"
            :disabled="!isValidTask"
          >
            {{ editingTask ? '更新' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 查看日志对话框 -->
    <div v-if="showLogModal" class="modal-overlay" @click="closeLogModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>📋 {{ selectedTask ? selectedTask.name + ' 日志' : '任务日志' }}</h3>
          <button class="close-btn" @click="closeLogModal">✕</button>
        </div>
        <div class="modal-body log-body">
          <div class="log-controls">
            <select v-model="logLevel" @change="filterLogs">
              <option value="">全部级别</option>
              <option value="info">信息</option>
              <option value="warning">警告</option>
              <option value="error">错误</option>
            </select>
            <button class="btn secondary" @click="loadLogs">刷新日志</button>
          </div>
          
          <div class="log-entries">
            <div 
              v-for="log in filteredLogs" 
              :key="log.id" 
              class="log-entry"
              :class="log.level"
            >
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
              <div class="log-level">{{ log.level.toUpperCase() }}</div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeLogModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 模拟爬虫任务数据
const crawlerTasks = ref([
  {
    id: 1,
    name: '500彩票网-比赛数据',
    dataSource: '500彩票网',
    frequency: 5,
    lastRun: new Date(Date.now() - 300000), // 5分钟前
    lastUpdate: new Date(Date.now() - 60000), // 1分钟前
    status: 'running',
    statusText: '运行中',
    description: '抓取500彩票网的比赛数据'
  },
  {
    id: 2,
    name: '赔率数据采集',
    dataSource: '赔率数据源',
    frequency: 10,
    lastRun: new Date(Date.now() - 1200000), // 20分钟前
    lastUpdate: new Date(Date.now() - 120000), // 2分钟前
    status: 'paused',
    statusText: '已暂停',
    description: '采集各大博彩公司的赔率数据'
  },
  {
    id: 3,
    name: '历史数据同步',
    dataSource: 'Bet365',
    frequency: 60,
    lastRun: new Date(Date.now() - 3600000), // 1小时前
    lastUpdate: new Date(Date.now() - 1800000), // 30分钟前
    status: 'stopped',
    statusText: '已停止',
    description: '同步历史比赛和赔率数据'
  },
  {
    id: 4,
    name: '实时情报抓取',
    dataSource: '500彩票网',
    frequency: 2,
    lastRun: new Date(Date.now() - 120000), // 2分钟前
    lastUpdate: new Date(Date.now() - 30000), // 30秒前
    status: 'running',
    statusText: '运行中',
    description: '实时抓取比赛情报和分析数据'
  },
  {
    id: 5,
    name: '备用数据源',
    dataSource: 'Bet365',
    frequency: 30,
    lastRun: new Date(Date.now() - 1800000), // 30分钟前
    lastUpdate: new Date(Date.now() - 300000), // 5分钟前
    status: 'error',
    statusText: '错误',
    description: '备用数据源，当主数据源不可用时使用'
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  status: '',
  dataSource: ''
})

// 统计数据
const stats = ref({
  totalRequests: 12450,
  successRate: 98.5,
  todayCrawled: 1240,
  avgResponseTime: 320,
  errorCount: 18
})

// 任务模态框
const showTaskModal = ref(false)
const editingTask = ref(null)
const currentTask = ref({
  name: '',
  dataSource: 'five_hundred',
  frequency: 5,
  useProxy: true,
  description: ''
})

// 日志模态框
const showLogModal = ref(false)
const selectedTask = ref(null)
const logEntries = ref([])
const logLevel = ref('')
const filteredLogs = ref([])

// 计算属性
const filteredTasks = computed(() => {
  let tasks = [...crawlerTasks.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    tasks = tasks.filter(task => 
      task.name.toLowerCase().includes(keyword) ||
      task.description.toLowerCase().includes(keyword) ||
      task.dataSource.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.status) {
    tasks = tasks.filter(task => task.status === filters.value.status)
  }
  
  if (filters.value.dataSource) {
    tasks = tasks.filter(task => task.dataSource.includes(filters.value.dataSource))
  }
  
  return tasks
})

const runningTasksCount = computed(() => 
  crawlerTasks.value.filter(task => task.status === 'running').length
)

const pausedTasksCount = computed(() => 
  crawlerTasks.value.filter(task => task.status === 'paused').length
)

const stoppedTasksCount = computed(() => 
  crawlerTasks.value.filter(task => task.status === 'stopped').length
)

const errorTasksCount = computed(() => 
  crawlerTasks.value.filter(task => task.status === 'error').length
)

const overallStatusClass = computed(() => {
  if (runningTasksCount.value > 0) return 'online'
  if (errorTasksCount.value > 0) return 'error'
  return 'offline'
})

const overallStatusText = computed(() => {
  if (runningTasksCount.value > 0) return '正常运行'
  if (errorTasksCount.value > 0) return '部分错误'
  return '无任务运行'
})

const ipPoolStatusClass = computed(() => {
  // 假设IP池状态取决于活跃IP数量
  const activeIps = 24 // 模拟数据
  if (activeIps > 20) return 'highlight'
  if (activeIps > 10) return 'normal'
  return 'warning'
})

const ipPoolStatusText = computed(() => {
  const activeIps = 24 // 模拟数据
  return `${activeIps} 个活跃IP`
})

const isValidTask = computed(() => {
  return currentTask.value.name.trim() !== '' && 
         currentTask.value.frequency > 0 && 
         currentTask.value.frequency <= 1440
})

// 方法
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
  // 实现搜索逻辑
}

const handleFilterChange = () => {
  console.log('筛选条件改变:', filters.value)
}

const refreshTasks = () => {
  console.log('刷新任务列表')
  // 在实际应用中，这里会调用API获取最新数据
}

const addNewTask = () => {
  editingTask.value = null
  currentTask.value = {
    name: '',
    dataSource: 'five_hundred',
    frequency: 5,
    useProxy: true,
    description: ''
  }
  showTaskModal.value = true
}

const editTask = (task) => {
  editingTask.value = task
  currentTask.value = { ...task }
  showTaskModal.value = true
}

const closeModal = () => {
  showTaskModal.value = false
  editingTask.value = null
}

const saveTask = () => {
  if (!isValidTask.value) return
  
  if (editingTask.value) {
    // 更新现有任务
    const index = crawlerTasks.value.findIndex(t => t.id === editingTask.value.id)
    if (index !== -1) {
      crawlerTasks.value[index] = { ...currentTask.value, id: editingTask.value.id }
    }
  } else {
    // 添加新任务
    const newId = Math.max(...crawlerTasks.value.map(t => t.id)) + 1
    crawlerTasks.value.push({
      ...currentTask.value,
      id: newId,
      lastRun: new Date(),
      lastUpdate: new Date(),
      status: 'stopped',
      statusText: '已停止'
    })
  }
  
  closeModal()
}

const startTask = async (task) => {
  console.log(`启动任务: ${task.name}`)
  // 更新任务状态为启动中
  task.status = 'starting'
  task.statusText = '启动中'
  
  // 模拟启动过程
  setTimeout(() => {
    task.status = 'running'
    task.statusText = '运行中'
    task.lastUpdate = new Date()
  }, 1000)
}

const pauseTask = async (task) => {
  console.log(`暂停任务: ${task.name}`)
  // 更新任务状态为停止中
  task.status = 'stopping'
  task.statusText = '停止中'
  
  // 模拟停止过程
  setTimeout(() => {
    task.status = 'stopped'
    task.statusText = '已停止'
    task.lastUpdate = new Date()
  }, 1000)
}

const viewLog = (task) => {
  selectedTask.value = task
  loadLogs()
  showLogModal.value = true
}

const closeLogModal = () => {
  showLogModal.value = false
  selectedTask.value = null
  logEntries.value = []
  filteredLogs.value = []
}

const loadLogs = () => {
  // 模拟加载日志数据
  logEntries.value = [
    { id: 1, timestamp: new Date(Date.now() - 300000), level: 'info', message: '任务启动成功' },
    { id: 2, timestamp: new Date(Date.now() - 240000), level: 'info', message: '开始抓取数据' },
    { id: 3, timestamp: new Date(Date.now() - 180000), level: 'info', message: '获取到25条比赛数据' },
    { id: 4, timestamp: new Date(Date.now() - 120000), level: 'warning', message: '检测到反爬机制，启用代理IP' },
    { id: 5, timestamp: new Date(Date.now() - 60000), level: 'info', message: '数据处理完成，已保存到数据库' },
    { id: 6, timestamp: new Date(), level: 'info', message: '下次运行时间: ' + new Date(Date.now() + currentTask.value.frequency * 60000).toLocaleString() }
  ]
  
  filterLogs()
}

const filterLogs = () => {
  if (logLevel.value) {
    filteredLogs.value = logEntries.value.filter(log => log.level === logLevel.value)
  } else {
    filteredLogs.value = [...logEntries.value]
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleString()
}

// 初始化数据
onMounted(() => {
  console.log('Crawler Management 页面已加载')
})
</script>

<style scoped>
.crawler-management-container {
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

.action-btn.start {
  background: #10b981;
  color: white;
}

.action-btn.start:hover {
  background: #059669;
}

.action-btn.pause {
  background: #f59e0b;
  color: white;
}

.action-btn.pause:hover {
  background: #d97706;
}

.action-btn.edit {
  background: #94a3b8;
  color: white;
}

.action-btn.edit:hover {
  background: #64748b;
}

.action-btn.log {
  background: #94a3b8;
  color: white;
}

.action-btn.log:hover {
  background: #64748b;
}

/* 任务列表样式 */
.tasks-section {
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

.task-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.stat-item.running { color: #10b981; }
.stat-item.paused { color: #f59e0b; }
.stat-item.stopped { color: #6b7280; }
.stat-item.error { color: #ef4444; }

.task-list {
  padding: 0;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.task-item:hover {
  background: #f9fafb;
}

.task-item:last-child {
  border-bottom: none;
}

.task-info {
  flex: 1;
}

.task-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
  font-size: 16px;
}

.task-details {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}

.task-source {
  background: #eff6ff;
  color: #2563eb;
  padding: 2px 6px;
  border-radius: 4px;
}

.task-frequency, .task-last-run {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.task-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 120px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 4px;
}

.status-badge.running {
  background: #dcfce7;
  color: #166534;
}

.status-badge.paused {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.stopped {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.error {
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge.starting, .status-badge.stopping {
  background: #dbeafe;
  color: #1e40af;
}

.last-update {
  font-size: 12px;
  color: #9ca3af;
}

.task-actions {
  display: flex;
  gap: 8px;
}

/* 系统状态网格 */
.system-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #10b981;
}

.status-indicator.error {
  background: #ef4444;
}

.status-indicator.offline {
  background: #9ca3af;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.status-item .label {
  color: #6b7280;
  font-size: 14px;
}

.status-item .value {
  font-weight: 500;
  font-size: 14px;
}

.status-item .value.online {
  color: #10b981;
}

.status-item .value.error {
  color: #ef4444;
}

.status-item .value.highlight {
  color: #3b82f6;
  font-weight: 600;
}

.status-item .value.warning {
  color: #f59e0b;
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

.large-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
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
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
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

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-switch input[type="checkbox"] {
  width: auto;
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

.btn.secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn.secondary:hover {
  background: #e5e7eb;
}

/* 日志样式 */
.log-body {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.log-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.log-entries {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: #f9fafb;
}

.log-entry {
  padding: 8px 12px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  font-family: monospace;
  font-size: 13px;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-entry.info {
  border-left: 3px solid #3b82f6;
}

.log-entry.warning {
  border-left: 3px solid #f59e0b;
}

.log-entry.error {
  border-left: 3px solid #ef4444;
}

.log-time {
  color: #6b7280;
  min-width: 120px;
}

.log-level {
  min-width: 60px;
  font-weight: bold;
}

.log-message {
  flex: 1;
}

@media (max-width: 768px) {
  .crawler-management-container {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .task-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .task-status {
    align-items: flex-start;
    margin-top: 8px;
  }
  
  .task-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .system-status-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95vw;
  }
  
  .large-modal {
    width: 95vw;
  }
}
</style>