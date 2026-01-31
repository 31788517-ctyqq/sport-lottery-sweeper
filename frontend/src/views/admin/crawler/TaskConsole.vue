<template>
  <div class="task-console">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>任务控制台</h2>
      <p>管理和监控所有爬虫任务的执行状态</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="总任务数"
              :value="statistics.totalTasks"
              :precision="0"
            >
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="运行中"
              :value="statistics.runningTasks"
              :precision="0"
              style="color: #67c23a"
            >
              <template #prefix>
                <el-icon><VideoPlay /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="成功完成"
              :value="statistics.successTasks"
              :precision="0"
              style="color: #409eff"
            >
              <template #prefix>
                <el-icon><CircleCheck /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="失败任务"
              :value="statistics.failedTasks"
              :precision="0"
              style="color: #f56c6c"
            >
              <template #prefix>
                <el-icon><CircleClose /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
      <el-button type="danger" @click="batchDeleteTasks" :disabled="selectedTasks.length === 0">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button type="success" @click="executeFiveHundredCrawl(3)">
        <el-icon><VideoPlay /></el-icon>
        执行500彩票网爬虫(3天)
      </el-button>
      <el-button type="warning" @click="createFiveHundredDataSource">
        <el-icon><Plus /></el-icon>
        创建500数据源
      </el-button>
      <el-button @click="loadTasks">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <el-card>
        <el-form :model="filters" inline>
          <el-form-item label="任务名称">
            <el-input
              v-model="filters.name"
              placeholder="请输入任务名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="任务类型">
            <el-select
              v-model="filters.task_type"
              placeholder="请选择任务类型"
              clearable
              style="width: 150px"
            >
              <el-option label="数据采集" value="DATA_COLLECTION" />
              <el-option label="数据分析" value="DATA_ANALYSIS" />
              <el-option label="数据清洗" value="DATA_CLEANING" />
              <el-option label="报告生成" value="REPORT_GENERATION" />
            </el-select>
          </el-form-item>
          <el-form-item label="任务状态">
            <el-select
              v-model="filters.status"
              placeholder="请选择状态"
              clearable
              style="width: 120px"
            >
              <el-option label="待执行" value="PENDING" />
              <el-option label="运行中" value="RUNNING" />
              <el-option label="已完成" value="SUCCESS" />
              <el-option label="失败" value="FAILED" />
              <el-option label="已取消" value="CANCELLED" />
            </el-select>
          </el-form-item>
          <el-form-item label="源ID">
            <el-input
              v-model="filters.source_id"
              placeholder="请输入源ID"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchTasks">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 任务列表 -->
    <div class="table-section">
      <el-table
        :data="tasks"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="150" />
        <el-table-column prop="task_type" label="任务类型" width="100">
          <template #default="scope">
            <el-tag :type="getTaskTypeColor(scope.row.task_type)">
              {{ getTaskTypeName(scope.row.task_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusColor(scope.row.status)">
              {{ getStatusName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_id" label="源ID" width="100" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="scope">
            <el-tag :type="getPriorityColor(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="120">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress || 0" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewLogs(scope.row)"
              :disabled="scope.row.status !== 'RUNNING'">
              日志
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="editTask(scope.row)"
              :disabled="['RUNNING', 'CANCELLED'].includes(scope.row.status)">
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteTask(scope.row)"
              :disabled="scope.row.status === 'RUNNING'">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 任务创建/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑任务' : '新建任务'"
      v-model="showCreateDialog"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="taskForm" :rules="formRules" ref="taskFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="taskForm.task_type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="数据采集" value="DATA_COLLECTION" />
            <el-option label="数据分析" value="DATA_ANALYSIS" />
            <el-option label="数据清洗" value="DATA_CLEANING" />
            <el-option label="报告生成" value="REPORT_GENERATION" />
          </el-select>
        </el-form-item>
        <el-form-item label="源ID" prop="source_id">
          <el-input v-model="taskForm.source_id" placeholder="请输入数据源ID" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="低 (1)" value="1" />
            <el-option label="中 (2)" value="2" />
            <el-option label="高 (3)" value="3" />
            <el-option label="紧急 (4)" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置参数" prop="config">
          <el-input
            v-model="taskForm.config"
            type="textarea"
            :rows="4"
            placeholder='请输入JSON格式的配置参数，如：{"timeout": 30, "retry_count": 3}'
          />
        </el-form-item>
        <el-form-item label="计划执行时间" prop="scheduled_at">
          <el-date-picker
            v-model="taskForm.scheduled_at"
            type="datetime"
            placeholder="选择计划执行时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="submitTaskForm" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 实时日志抽屉 -->
    <el-drawer
      v-model="showLogDrawer"
      title="任务执行日志"
      direction="rtl"
      size="50%"
    >
      <div class="log-viewer">
        <div class="log-header">
          <el-button @click="clearLogs">清空日志</el-button>
          <el-button @click="pauseLogs" v-if="!logsPaused">暂停</el-button>
          <el-button @click="resumeLogs" v-else>继续</el-button>
        </div>
        <div class="log-content">
          <pre v-for="log in taskLogs" :key="log.id" class="log-line">
{{ log.timestamp }} [{{ log.level }}] {{ log.message }}</pre>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, VideoPlay, CircleCheck, CircleClose, 
  Plus, Refresh, Delete, Edit 
} from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showLogDrawer = ref(false)
const isEdit = ref(false)
const logsPaused = ref(false)
const taskFormRef = ref()

// 统计数据
const statistics = reactive({
  totalTasks: 0,
  runningTasks: 0,
  successTasks: 0,
  failedTasks: 0
})

// 筛选条件
const filters = reactive({
  name: '',
  task_type: '',
  status: '',
  source_id: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 任务列表
const tasks = ref([])

// 选中的任务
const selectedTasks = ref([])

// 任务表单
const taskForm = reactive({
  id: null,
  name: '',
  task_type: '',
  source_id: '',
  priority: 2,
  config: '',
  scheduled_at: null
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  source_id: [{ required: true, message: '请输入源ID', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

// 任务日志
const taskLogs = ref([])
let logWebSocket = null

// API基础URL
const API_BASE = '/api/v1/crawler'

// 生命周期
onMounted(() => {
  loadTasks()
  loadStatistics()
})

onUnmounted(() => {
  if (logWebSocket) {
    logWebSocket.close()
  }
})

// 方法定义
const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...filters
    }
    const response = await axios.get(`${API_BASE}/tasks`, { params })
    tasks.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载任务列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await axios.get(`${API_BASE}/tasks/statistics`)
    Object.assign(statistics, response.data)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const refreshTasks = () => {
  loadTasks()
  loadStatistics()
}

const searchTasks = () => {
  pagination.page = 1
  loadTasks()
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  searchTasks()
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadTasks()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadTasks()
}

const submitTaskForm = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    submitting.value = true
    
    const payload = { ...taskForm }
    if (payload.config && typeof payload.config === 'string') {
      try {
        payload.config = JSON.parse(payload.config)
      } catch (e) {
        ElMessage.error('配置参数必须是有效的JSON格式')
        return
      }
    }
    
    if (isEdit.value) {
      await axios.put(`${API_BASE}/tasks/${payload.id}`, payload)
      ElMessage.success('任务更新成功')
    } else {
      await axios.post(`${API_BASE}/tasks`, payload)
      ElMessage.success('任务创建成功')
    }
    
    showCreateDialog.value = false
    loadTasks()
    loadStatistics()
  } catch (error) {
    ElMessage.error(isEdit.value ? '任务更新失败' : '任务创建失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const editTask = (task) => {
  isEdit.value = true
  Object.assign(taskForm, {
    id: task.id,
    name: task.name,
    task_type: task.task_type,
    source_id: task.source_id,
    priority: task.priority,
    config: task.config ? JSON.stringify(task.config, null, 2) : '',
    scheduled_at: task.scheduled_at ? new Date(task.scheduled_at) : null
  })
  showCreateDialog.value = true
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务"${task.name}"吗？`, '确认删除', {
      type: 'warning'
    })
    
    await axios.delete(`${API_BASE}/tasks/${task.id}`)
    ElMessage.success('任务删除成功')
    loadTasks()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('任务删除失败')
    }
  }
}

const batchDeleteTasks = async () => {
  if (selectedTasks.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？`,
      '确认批量删除',
      { type: 'warning' }
    )
    
    const ids = selectedTasks.value.map(task => task.id)
    await axios.delete(`${API_BASE}/tasks/batch`, { data: { ids } })
    ElMessage.success('批量删除成功')
    loadTasks()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const viewLogs = (task) => {
  showLogDrawer.value = true
  connectLogWebSocket(task.id)
}

const connectLogWebSocket = (taskId) => {
  if (logWebSocket) {
    logWebSocket.close()
  }
  
  taskLogs.value = []
  logsPaused.value = false
  
  // 这里应该连接到实际的WebSocket端点
  // logWebSocket = new WebSocket(`ws://localhost:8001/ws/logs/${taskId}`)
  
  // 模拟日志数据
  const mockLogs = [
    { id: 1, timestamp: new Date().toISOString(), level: 'INFO', message: '任务开始执行' },
    { id: 2, timestamp: new Date().toISOString(), level: 'INFO', message: '正在连接数据源...' },
    { id: 3, timestamp: new Date().toISOString(), level: 'INFO', message: '数据源连接成功' },
    { id: 4, timestamp: new Date().toISOString(), level: 'INFO', message: '开始数据采集' }
  ]
  
  let index = 0
  const interval = setInterval(() => {
    if (!logsPaused.value && index < mockLogs.length) {
      taskLogs.value.push(mockLogs[index])
      index++
    }
  }, 1000)
  
  // 存储interval以便在组件卸载时清理
  logWebSocket = { close: () => clearInterval(interval) }
}

const clearLogs = () => {
  taskLogs.value = []
}

const pauseLogs = () => {
  logsPaused.value = true
}

const resumeLogs = () => {
  logsPaused.value = false
}

// 新增：执行500彩票网爬虫任务
const executeFiveHundredCrawl = async (days = 3) => {
  try {
    const response = await axios.post(`${API_BASE}/tasks/0/execute-five-hundred-crawl`, {}, {
      params: { days }
    });
    
    ElMessage.success(`成功执行500彩票网爬虫任务: ${response.data.message}`);
    console.log('爬虫任务执行结果:', response.data);
  } catch (error) {
    console.error('执行500彩票网爬虫任务失败:', error);
    ElMessage.error(`执行爬虫任务失败: ${error.response?.data?.detail || error.message}`);
  }
}

// 新增：创建500彩票网数据源
const createFiveHundredDataSource = async () => {
  try {
    const response = await axios.post(`${API_BASE}/sources/five-hundred-create`);
    
    ElMessage.success(response.data.message);
    console.log('500彩票网数据源创建结果:', response.data);
  } catch (error) {
    console.error('创建500彩票网数据源失败:', error);
    ElMessage.error(`创建数据源失败: ${error.response?.data?.detail || error.message}`);
  }
}

const resetForm = () => {
  if (taskFormRef.value) {
    taskFormRef.value.resetFields()
  }
  Object.assign(taskForm, {
    id: null,
    name: '',
    task_type: '',
    source_id: '',
    priority: 2,
    config: '',
    scheduled_at: null
  })
  isEdit.value = false
}

// 辅助方法
const getTaskTypeColor = (type) => {
  const colors = {
    'DATA_COLLECTION': 'primary',
    'DATA_ANALYSIS': 'success',
    'DATA_CLEANING': 'warning',
    'REPORT_GENERATION': 'info'
  }
  return colors[type] || 'default'
}

const getTaskTypeName = (type) => {
  const names = {
    'DATA_COLLECTION': '数据采集',
    'DATA_ANALYSIS': '数据分析',
    'DATA_CLEANING': '数据清洗',
    'REPORT_GENERATION': '报告生成'
  }
  return names[type] || type
}

const getStatusColor = (status) => {
  const colors = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'SUCCESS': 'success',
    'FAILED': 'danger',
    'CANCELLED': 'default'
  }
  return colors[status] || 'default'
}

const getStatusName = (status) => {
  const names = {
    'PENDING': '待执行',
    'RUNNING': '运行中',
    'SUCCESS': '已完成',
    'FAILED': '失败',
    'CANCELLED': '已取消'
  }
  return names[status] || status
}

const getPriorityColor = (priority) => {
  const num = parseInt(priority)
  if (num >= 4) return 'danger'
  if (num >= 3) return 'warning'
  if (num >= 2) return 'info'
  return 'success'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.task-console {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.operation-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
}

.table-section {
  background: white;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.log-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.log-header {
  padding: 10px;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 10px;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: #1e1e1e;
  color: #fff;
}

.log-line {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-console {
    padding: 10px;
  }
  
  .operation-bar {
    flex-direction: column;
  }
  
  .filter-section :deep(.el-form-item) {
    display: block;
    margin-right: 0;
  }
}
</style>