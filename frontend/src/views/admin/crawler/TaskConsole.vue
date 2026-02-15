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
              :title="displayTotalTitle"
              :value="displayTotalValue"
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
              :value="Number(statistics.runningTasks) || 0"
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
              :value="Number(statistics.successTasks) || 0"
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
              :value="Number(statistics.failedTasks) || 0"
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
      <!-- 空数据提示 -->
      <div v-if="displayTotalValue === 0 && !hasActiveFilters" class="empty-stats-tip">
        <el-alert type="info" show-icon :closable="false">
          暂无统计数据，请先创建或运行任务以生成统计信息。
        </el-alert>
      </div>
    </div>

    <!-- 操作栏 (已删除500彩票网相关按钮) -->
    <div class="operation-bar">
      <!-- AI_WORKING: coder1 @1770014206 - 删除500彩票网爬虫按钮和创建500数据源按钮 -->
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
      <el-button type="danger" @click="batchDeleteTasks" :disabled="selectedTasks.length === 0">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button @click="loadTasks">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      <!-- AI_DONE: coder1 @1770014206 -->
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
            <el-button type="primary" @click="searchTasks" :loading="searchLoading">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 任务列表 -->
    <div class="table-section">
      <div v-if="tasks.length === 0" class="empty-state">
        <el-empty description="暂无任务，请先创建数据源并配置任务">
          <el-button type="primary" @click="handleAdd">添加任务</el-button>
        </el-empty>
      </div>
      <el-table
        v-else
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
<el-tag :type="getTaskTypeColor(scope.row.task_type || '')">
  {{ getTaskTypeName(scope.row.task_type || '') }}
</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
<el-tag :type="getStatusColor(scope.row.status || '')">
  {{ getStatusName(scope.row.status || '') }}
</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_id" label="源ID" width="100" />
        <el-table-column prop="progress" label="进度" width="120">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress != null ? Number(scope.row.progress) : 0" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at || null) }}
            </template>
          </el-table-column>
          <el-table-column prop="started_at" label="开始时间" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.started_at || null) }}
            </template>
          </el-table-column>
        <el-table-column label="操作" width="380" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleToggleTask(scope.row)"
              :loading="scope.row.loadingTrigger">
              {{ scope.row.status === 'RUNNING' ? '停止' : '启动' }}
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="viewTaskDetails(scope.row)">
              详情
            </el-button>
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

      <!-- 空数据提示 -->
      <div v-if="tasks.length === 0 && !loading" class="empty-table-tip">
        <el-empty description="暂无任务数据" />
      </div>

      <!-- 分页 -->
      <div v-if="tasks.length > 0" class="pagination-wrapper">
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
        <el-tabs v-model="editActiveTab">
          <el-tab-pane label="基础信息" name="basic">
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
          <el-input v-model="taskForm.source_id" placeholder="请输入数据源ID（数字）" />
        </el-form-item>
        <el-form-item label="Cron表达式" prop="cron_expression">
          <el-input v-model="taskForm.cron_expression" placeholder="请输入Cron表达式，例如：0 * * * *" />
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
          </el-tab-pane>
          <el-tab-pane label="请求头绑定" name="headers">
            <div class="bind-header-actions">
              <el-select
                v-model="bindTaskForm.headerIds"
                multiple
                filterable
                remote
                :remote-method="loadHeaderOptions"
                placeholder="选择请求头（可搜索）"
                style="width: 320px;"
              >
                <el-option
                  v-for="item in headerOptions"
                  :key="item.id"
                  :label="`${item.name} (${item.domain})`"
                  :value="item.id"
                />
              </el-select>
              <el-select v-model="bindTaskForm.priorityOverride" placeholder="优先级覆盖" style="width: 140px;">
                <el-option label="高" :value="3" />
                <el-option label="中" :value="2" />
                <el-option label="低" :value="1" />
              </el-select>
              <el-button size="small" type="primary" @click="bindTaskHeaders">绑定</el-button>
              <el-button size="small" @click="loadTaskHeaderBindings">刷新绑定</el-button>
            </div>
            <el-table :data="taskHeaderBindings" size="small" style="width: 100%">
              <el-table-column prop="header.id" label="Header ID" width="90" />
              <el-table-column prop="header.name" label="名称" width="120" />
              <el-table-column prop="header.domain" label="域名" min-width="140" />
              <el-table-column prop="priorityOverride" label="优先级覆盖" width="110" />
              <el-table-column prop="enabled" label="启用" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.enabled ? 'success' : 'info'">
                    {{ scope.row.enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button size="small" @click="toggleTaskBinding(scope.row)">
                    {{ scope.row.enabled ? '禁用' : '启用' }}
                  </el-button>
                  <el-button size="small" type="danger" @click="removeTaskBinding(scope.row)">解绑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
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
          <el-button @click="fetchLatestLogs">刷新日志</el-button>
        </div>
        <div class="log-content">
          <div v-if="taskLogs.length === 0" class="empty-logs-tip">
            <el-empty description="暂无日志" />
          </div>
          <div v-else>
            <div v-for="log in taskLogs" :key="log.id" class="log-line">
              <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
              <span :class="`log-level log-level-${(log.level || 'info').toLowerCase()}`">[{{ log.level || 'INFO' }}]</span>
              <span class="log-message">{{ log.message || '' }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 添加任务执行监控抽屉 -->
    <el-drawer
      v-model="showMonitorDrawer"
      title="任务执行监控"
      direction="rtl"
      size="40%"
    >
      <div class="monitor-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务ID">{{ currentTask?.id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ currentTask?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(currentTask?.status)">
              {{ getStatusName(currentTask?.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">
            <el-progress :percentage="currentProgress" :status="currentTask?.status === 'RUNNING' ? null : 'success'" />
          </el-descriptions-item>
          <el-descriptions-item label="数据源ID">{{ currentTask?.source_id }}</el-descriptions-item>
          <el-descriptions-item label="上次运行时间">{{ formatDate(currentTask?.last_run_time || null) }}</el-descriptions-item>
          <el-descriptions-item label="下次运行时间">{{ formatDate(currentTask?.next_run_time || null) }}</el-descriptions-item>
          <el-descriptions-item label="运行次数">{{ currentTask?.run_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="成功次数">{{ currentTask?.success_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="错误次数">{{ currentTask?.error_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentTask?.created_at || null) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, VideoPlay, CircleCheck, CircleClose, 
  Plus, Refresh, Delete, Edit 
} from '@element-plus/icons-vue'
import { 
  listTasks, 
  createTask, 
  updateTask, 
  deleteTask as deleteTaskApi,
  triggerTask,
  stopTask,
  getLogs,
  batchDeleteTasks as batchDeleteTasksApi,
  getTaskStatistics
} from '@/api/crawlerTask'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const searchLoading = ref(false)
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
  cron_expression: '* * * * *', // 添加cron_expression字段
  config: '',
  scheduled_at: null
})

// 自定义校验：正整数
const validatePositiveInteger = (rule, value, callback) => {
  if (!value) {
    return callback(new Error('请输入源ID'))
  }
  const num = Number(value)
  if (!Number.isInteger(num) || num <= 0) {
    return callback(new Error('源ID必须为正整数'))
  }
  callback()
}

// 自定义校验：cron 表达式（5段非空）
const validateCronExpression = (rule, value, callback) => {
  if (!value) {
    return callback(new Error('请输入Cron表达式'))
  }
  const parts = value.trim().split(/\s+/)
  if (parts.length < 5) {
    return callback(new Error('Cron表达式至少需要5个字段'))
  }
  // 简单检查每段非空
  if (parts.some(p => p === '')) {
    return callback(new Error('Cron表达式字段不能为空'))
  }
  callback()
}

// 自定义校验：JSON 格式
const validateJsonConfig = (rule, value, callback) => {
  if (!value) {
    return callback() // 允许为空
  }
  try {
    JSON.parse(value.trim() || '{}')
    callback()
  } catch (e) {
    return callback(new Error('配置参数必须是有效的JSON格式'))
  }
}

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 1, max: 50, message: '任务名称长度应在1到50个字符之间', trigger: 'blur' }
  ],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  source_id: [
    { required: true, message: '请输入源ID', trigger: 'blur' },
    { validator: validatePositiveInteger, trigger: 'blur' }
  ],
  cron_expression: [
    { required: true, message: '请输入Cron表达式', trigger: 'blur' },
    { validator: validateCronExpression, trigger: 'blur' }
  ],
  config: [
    { validator: validateJsonConfig, trigger: 'blur' }
  ]
}

// 计算属性：判断是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return Object.values(filters).some(value => value !== '' && value !== null && value !== undefined);
});

// 计算属性：显示的总数标题
const displayTotalTitle = computed(() => {
  return hasActiveFilters.value ? '当前筛选结果' : '总任务数';
});

// 计算属性：显示的总数值
const displayTotalValue = computed(() => {
  return hasActiveFilters.value ? pagination.total : (Number(statistics.totalTasks) || 0);
});

// 任务日志
const taskLogs = ref([])
let logWebSocket = null

// 添加响应式变量
const showMonitorDrawer = ref(false)
const currentTask = ref(null)
const currentProgress = ref(0)

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
    const response = await listTasks(params)
    tasks.value = (response.data?.items || response.items || []).map(task => ({
      ...task,
      loadingTrigger: false  // 初始化启动按钮的加载状态
    }))
    pagination.total = response.data?.total || response.total || 0
    
    // 检查是否没有应用任何筛选条件，如果没有则更新总任务数
    const hasFilters = Object.values(filters).some(value => value !== '' && value !== null && value !== undefined);
    if (!hasFilters) {
      statistics.totalTasks = pagination.total;
    }
    
    // 每次加载任务列表后都更新统计数据，确保一致性
    await loadStatistics();
  } catch (error) {
    ElMessage.error('加载任务列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await getTaskStatistics()
    // 修正：从statusStats对象中获取各个状态的统计值
    const statusStats = response.data.statusStats || {}
    statistics.runningTasks = (statusStats.RUNNING || statusStats.running || 0)
    statistics.successTasks = (statusStats.SUCCESS || statusStats.success || 0)
    statistics.failedTasks = (statusStats.FAILED || statusStats.failed || 0)
    // totalTasks已经在loadTasks中处理，这里不需要重复设置
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const refreshTasks = () => {
  loadTasks()
  loadStatistics()
}

const searchTasks = async () => {
  searchLoading.value = true
  try {
    pagination.page = 1
    await loadTasks()
  } finally {
    searchLoading.value = false
  }
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  searchTasks()
  loadStatistics()  // 重置筛选条件后也更新统计数据
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

    // 检查数据源是否可用
    if (!sourceOptions || sourceOptions.length === 0) {
      ElMessage.warning('请先添加数据源后再创建任务')
      return
    }
    if (!taskForm.source_id) {
      ElMessage.warning('请选择数据源')
      return
    }

    submitting.value = true
    
    const payload = { ...taskForm }
    
    // 解析config：如果是字符串，尝试转换为对象；否则使用空对象
    let configObj = {}
    if (payload.config) {
      if (typeof payload.config === 'string') {
        try {
          configObj = JSON.parse(payload.config.trim() || '{}')
        } catch (e) {
          console.warn('配置参数JSON解析失败，使用空对象:', e)
          configObj = {}
        }
      } else if (typeof payload.config === 'object') {
        configObj = payload.config
      }
    }
    
    if (!isEdit.value) { // 创建任务
      const taskPayload = {
        name: payload.name.trim(),
        source_id: payload.source_id, // 作为字符串传递，后端会验证是否为数字
        task_type: payload.task_type,
        cron_expression: payload.cron_expression,
        config: configObj
      }
      
      await createTask(taskPayload)
      ElMessage.success('任务创建成功')
    } else { // 更新任务
      const updatePayload = {
        name: payload.name.trim(),
        source_id: payload.source_id,
        task_type: payload.task_type,
        cron_expression: payload.cron_expression,
        is_active: payload.is_active !== undefined ? !!payload.is_active : true,
        config: configObj
      }
      
      await updateTask(payload.id, updatePayload)
      ElMessage.success('任务更新成功')
    }
    
    showCreateDialog.value = false
    loadTasks()
    loadStatistics()
  } catch (error) {
    if (error.message && error.message.includes('validate')) {
      console.error('表单验证失败:', error)
      ElMessage.error('请检查表单中的必填项')
    } else {
      ElMessage.error(isEdit.value ? '任务更新失败' : '任务创建失败')
      console.error(error)
    }
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
    cron_expression: task.cron_expression || '* * * * *',
    config: task.config ? JSON.stringify(task.config, null, 2) : '{}',
    scheduled_at: task.scheduled_at ? new Date(task.scheduled_at) : null,
    is_active: task.is_active !== undefined ? task.is_active : true
  })
  showCreateDialog.value = true
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务"${task.name}"吗？`, '确认删除', {
      type: 'warning'
    })
    
    await deleteTaskApi(task.id)
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
    await batchDeleteTasksApi(ids)
    ElMessage.success('批量删除成功')
    loadTasks()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const viewLogs = async (task) => {
  try {
    showLogDrawer.value = true;
    const response = await getLogs(task.id);
    // 直接使用后端返回的日志数据，而不是构建消息
    taskLogs.value = response.data.items.map(log => ({
      id: log.id,
      timestamp: log.created_at || log.started_at,
      level: log.status ? log.status.toUpperCase() : 'INFO',
      message: log.message || `${log.status || 'LOG'} - 处理了${log.records_processed || 0}条记录，成功${log.records_success || 0}条，失败${log.records_failed || 0}条`
    }));
  } catch (error) {
    console.error('获取日志失败:', error);
    ElMessage.error('获取日志失败');
  }
}

// 添加刷新日志功能
const fetchLatestLogs = async () => {
  if (!currentTask.value) return;
  
  try {
    const response = await getLogs(currentTask.value.id);
    taskLogs.value = response.data.items.map(log => ({
      id: log.id,
      timestamp: log.created_at || log.started_at,
      level: log.status ? log.status.toUpperCase() : 'INFO',
      message: log.message || `${log.status || 'LOG'} - 处理了${log.records_processed || 0}条记录，成功${log.records_success || 0}条，失败${log.records_failed || 0}条`
    }));
  } catch (error) {
    console.error('刷新日志失败:', error);
    ElMessage.error('刷新日志失败');
  }
}

const connectLogWebSocket = (taskId) => {
  if (logWebSocket) {
    logWebSocket.close()
  }
  
  taskLogs.value = []
  logsPaused.value = false
  
  // TODO: 这里应该连接到实际的WebSocket端点
  // logWebSocket = new WebSocket(`ws://localhost:8001/ws/logs/${taskId}`)
  // 临时保持模拟数据，直到WebSocket实现完成
  
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

const handleToggleTask = async (task) => {
  try {
    // 设置加载状态
    task.loadingTrigger = true;

    if (task.status === 'RUNNING') {
      // 如果任务正在运行，则停止任务
      await stopTask(task.id);
      ElMessage.success('任务停止成功');
      
      // 更新任务状态
      task.status = 'STOPPED';
    } else {
      // 如果任务不在运行，则启动任务
      await triggerTask(task.id);
      ElMessage.success('任务启动成功');
      
      // 更新任务状态，设置开始时间为当前时间
      task.status = 'RUNNING';
      task.started_at = new Date().toISOString();
    }
    
    // 重新加载任务列表以获取最新状态
    loadTasks();
    loadStatistics();
  } catch (error) {
    console.error(task.status === 'RUNNING' ? '停止任务失败:' : '启动任务失败:', error);
    ElMessage.error(task.status === 'RUNNING' ? '停止任务失败' : '启动任务失败');
  } finally {
    // 清除加载状态
    task.loadingTrigger = false;
  }
};

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
  return colors[type] || 'info'  // 将'default'改为'info'
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
    'CANCELLED': 'info'
  }
  return colors[status] || 'info'  // 确保默认返回值也是'info'
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

// 添加格式化时间戳函数
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-';
  return new Date(timestamp).toLocaleTimeString('zh-CN');
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 添加查看任务详情功能
const viewTaskDetails = (task) => {
  currentTask.value = task;
  // 计算进度百分比，基于处理成功的记录数
  if (task.success_count && task.run_count) {
    currentProgress.value = Math.min(100, Math.round((task.success_count / task.run_count) * 100));
  } else {
    currentProgress.value = 0;
  }
  showMonitorDrawer.value = true;
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
  padding: 2px 0;
  border-bottom: 1px solid #eee;
}

.log-timestamp {
  color: #999;
  margin-right: 8px;
}

.log-level {
  font-weight: bold;
  margin-right: 8px;
  padding: 0 4px;
  border-radius: 2px;
}

.log-level-info {
  color: #409eff;
}

.log-level-warning {
  color: #e6a23c;
}

.log-level-error {
  color: #f56c6c;
}

.log-level-success {
  color: #67c23a;
}

.log-message {
  color: #333;
}

.monitor-content {
  padding: 20px 0;
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
.empty-stats-tip {
  margin-top: 16px;
}
.empty-table-tip {
  margin: 40px 0;
  text-align: center;
}
.empty-logs-tip {
  margin: 40px 0;
  text-align: center;
}
</style>
