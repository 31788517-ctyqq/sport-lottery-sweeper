<template>
  <div class="task-manager">
    <el-card class="manager-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><List /></el-icon>
            任务管理中心
          </span>
          <div class="card-actions">
            <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
              新建任务
            </el-button>
            <el-button :icon="Refresh" circle @click="refreshTasks" :loading="loading" />
          </div>
        </div>
      </template>

      <!-- 任务筛选 -->
      <div class="task-filters">
        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <el-select 
              v-model="filters.status" 
              placeholder="任务状态"
              clearable
              @change="applyFilters"
            >
              <el-option label="全部状态" value="" />
              <el-option label="运行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="已暂停" value="paused" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select 
              v-model="filters.priority" 
              placeholder="优先级"
              clearable
              @change="applyFilters"
            >
              <el-option label="全部优先级" value="" />
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select 
              v-model="filters.type" 
              placeholder="任务类型"
              clearable
              @change="applyFilters"
            >
              <el-option label="全部类型" value="" />
              <el-option label="数据采集" value="crawler" />
              <el-option label="数据分析" value="analysis" />
              <el-option label="报表生成" value="report" />
              <el-option label="系统监控" value="monitor" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="filters.search"
              placeholder="搜索任务名称"
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

      <!-- 任务统计 -->
      <div class="task-stats">
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number text-primary">{{ stats.running }}</div>
              <div class="stat-label">运行中</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number text-success">{{ stats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number text-warning">{{ stats.paused }}</div>
              <div class="stat-label">已暂停</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number text-danger">{{ stats.failed }}</div>
              <div class="stat-label">失败</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 任务列表 -->
      <div class="task-list">
        <el-table 
          :data="filteredTasks" 
          v-loading="loading"
          stripe
          class="task-table"
        >
          <el-table-column prop="name" label="任务名称" min-width="200">
            <template #default="scope">
              <div class="task-name">
                <el-tag :type="getTaskTypeTag(scope.row.type)" size="small" class="task-type">
                  {{ getTaskTypeText(scope.row.type) }}
                </el-tag>
                <span class="task-title">{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTag(scope.row.status)" size="small">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="scope">
              <el-tag :type="getPriorityTag(scope.row.priority)" size="small">
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="progress" label="进度" width="200">
            <template #default="scope">
              <div class="progress-container">
                <el-progress 
                  :percentage="scope.row.progress || 0" 
                  :stroke-width="6"
                  :color="getProgressColor(scope.row.progress)"
                />
                <span class="progress-text">{{ scope.row.progress || 0 }}%</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="scope">
              {{ formatTime(scope.row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="280" fixed="right">
            <template #default="scope">
              <el-button-group>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="viewTask(scope.row)"
                >
                  查看
                </el-button>
                
                <el-button 
                  v-if="scope.row.status === 'running'"
                  type="warning" 
                  size="small"
                  @click="pauseTask(scope.row)"
                >
                  暂停
                </el-button>
                
                <el-button 
                  v-if="scope.row.status === 'paused'"
                  type="success" 
                  size="small"
                  @click="resumeTask(scope.row)"
                >
                  继续
                </el-button>
                
                <el-button 
                  v-if="['running', 'paused'].includes(scope.row.status)"
                  type="danger" 
                  size="small"
                  @click="stopTask(scope.row)"
                >
                  停止
                </el-button>
                
                <el-dropdown @command="handleCommand" trigger="click">
                  <el-button size="small">
                    更多<el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="`log:${scope.row.id}`">
                        查看日志
                      </el-dropdown-item>
                      <el-dropdown-item :command="`edit:${scope.row.id}`">
                        编辑任务
                      </el-dropdown-item>
                      <el-dropdown-item :command="`copy:${scope.row.id}`">
                        复制任务
                      </el-dropdown-item>
                      <el-dropdown-item divided :command="`delete:${scope.row.id}`">
                        删除任务
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      title="新建任务" 
      width="600px"
      @close="resetForm"
    >
      <el-form 
        ref="taskFormRef"
        :model="taskForm" 
        :rules="formRules" 
        label-width="100px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="taskForm.type" placeholder="选择任务类型">
            <el-option label="数据采集" value="crawler" />
            <el-option label="数据分析" value="analysis" />
            <el-option label="报表生成" value="report" />
            <el-option label="系统监控" value="monitor" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="选择优先级">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="任务描述" prop="description">
          <el-input 
            v-model="taskForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        
        <el-form-item label="执行参数" prop="params">
          <el-input 
            v-model="taskForm.params" 
            type="textarea" 
            :rows="4"
            placeholder='JSON格式的执行参数，如：{"interval": 300, "batch_size": 100}'
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createTask" :loading="creating">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  List, Plus, Refresh, Search, ArrowDown 
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const taskFormRef = ref(null)

// 过滤器
const filters = reactive({
  status: '',
  priority: '',
  type: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 任务表单
const taskForm = reactive({
  name: '',
  type: '',
  priority: 'medium',
  description: '',
  params: ''
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

// 模拟任务数据
const tasks = ref([
  {
    id: 1,
    name: '足球赛事数据采集',
    type: 'crawler',
    status: 'running',
    priority: 'high',
    progress: 65,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    description: '定时采集各大平台足球赛事数据'
  },
  {
    id: 2,
    name: '赔率变化分析',
    type: 'analysis',
    status: 'completed',
    priority: 'medium',
    progress: 100,
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    description: '分析赔率变化趋势和异常波动'
  },
  {
    id: 3,
    name: '每日数据报表',
    type: 'report',
    status: 'paused',
    priority: 'low',
    progress: 30,
    created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    description: '生成每日运营数据汇总报表'
  },
  {
    id: 4,
    name: '系统健康监控',
    type: 'monitor',
    status: 'running',
    priority: 'high',
    progress: 85,
    created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    description: '监控系统各项指标和服务状态'
  },
  {
    id: 5,
    name: '异常数据清理',
    type: 'crawler',
    status: 'failed',
    priority: 'medium',
    progress: 20,
    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    description: '清理采集过程中的异常和重复数据'
  }
])

// 计算属性
const filteredTasks = computed(() => {
  let result = tasks.value
  
  // 状态过滤
  if (filters.status) {
    result = result.filter(task => task.status === filters.status)
  }
  
  // 优先级过滤
  if (filters.priority) {
    result = result.filter(task => task.priority === filters.priority)
  }
  
  // 类型过滤
  if (filters.type) {
    result = result.filter(task => task.type === filters.type)
  }
  
  // 搜索过滤
  if (filters.search) {
    const search = filters.search.toLowerCase()
    result = result.filter(task => 
      task.name.toLowerCase().includes(search) ||
      task.description.toLowerCase().includes(search)
    )
  }
  
  return result
})

// 统计信息
const stats = computed(() => {
  return {
    running: tasks.value.filter(t => t.status === 'running').length,
    completed: tasks.value.filter(t => t.status === 'completed').length,
    paused: tasks.value.filter(t => t.status === 'paused').length,
    failed: tasks.value.filter(t => t.status === 'failed').length
  }
})

// 方法
const refreshTasks = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    // 这里应该调用实际的API
    ElMessage.success('任务列表已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  pagination.page = 1
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

const getTaskTypeTag = (type) => {
  const map = {
    crawler: 'primary',
    analysis: 'success',
    report: 'warning',
    monitor: 'info'
  }
  return map[type] || 'info'
}

const getTaskTypeText = (type) => {
  const map = {
    crawler: '采集',
    analysis: '分析',
    report: '报表',
    monitor: '监控'
  }
  return map[type] || type
}

const getStatusTag = (status) => {
  const map = {
    running: 'primary',
    completed: 'success',
    paused: 'warning',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    running: '运行中',
    completed: '已完成',
    paused: '已暂停',
    failed: '失败'
  }
  return map[status] || status
}

const getPriorityTag = (priority) => {
  const map = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return map[priority] || 'info'
}

const getProgressColor = (progress) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#409eff'
  if (progress >= 20) return '#e6a23c'
  return '#f56c6c'
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const viewTask = (task) => {
  ElMessage.info(`查看任务: ${task.name}`)
}

const pauseTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要暂停任务 "${task.name}" 吗？`, '确认暂停')
    task.status = 'paused'
    ElMessage.success('任务已暂停')
  } catch {
    // 用户取消
  }
}

const resumeTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要继续任务 "${task.name}" 吗？`, '确认继续')
    task.status = 'running'
    ElMessage.success('任务已继续')
  } catch {
    // 用户取消
  }
}

const stopTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要停止任务 "${task.name}" 吗？`, '确认停止')
    task.status = 'completed'
    task.progress = 0
    ElMessage.success('任务已停止')
  } catch {
    // 用户取消
  }
}

const handleCommand = (command) => {
  const [action, id] = command.split(':')
  const task = tasks.value.find(t => t.id == id)
  
  switch (action) {
    case 'log':
      ElMessage.info(`查看任务日志: ${task?.name}`)
      break
    case 'edit':
      ElMessage.info(`编辑任务: ${task?.name}`)
      break
    case 'copy':
      ElMessage.info(`复制任务: ${task?.name}`)
      break
    case 'delete':
      handleDeleteTask(task)
      break
  }
}

const handleDeleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务 "${task.name}" 吗？此操作不可恢复。`, '确认删除', {
      type: 'warning'
    })
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index > -1) {
      tasks.value.splice(index, 1)
      ElMessage.success('任务已删除')
    }
  } catch {
    // 用户取消
  }
}

const createTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    creating.value = true
    
    // 模拟创建任务
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newTask = {
      id: Date.now(),
      ...taskForm,
      status: 'paused',
      progress: 0,
      created_at: new Date().toISOString()
    }
    
    tasks.value.unshift(newTask)
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    resetForm()
    
  } catch (error) {
    if (error !== false) {
      ElMessage.error('创建失败')
    }
  } finally {
    creating.value = false
  }
}

const resetForm = () => {
  Object.assign(taskForm, {
    name: '',
    type: '',
    priority: 'medium',
    description: '',
    params: ''
  })
  taskFormRef.value?.resetFields()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
}

const handleCurrentChange = (page) => {
  pagination.page = page
}

// 生命周期
onMounted(() => {
  refreshTasks()
})

// 暴露方法
defineExpose({
  refreshTasks,
  tasks
})
</script>

<style scoped>
.task-manager {
  width: 100%;
}

.manager-card {
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

.task-filters {
  margin-bottom: 20px;
}

.filter-row {
  margin-bottom: 16px;
}

.task-stats {
  margin-bottom: 24px;
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-top: 4px;
}

.task-list {
  space-y: 16px;
}

.task-table {
  margin-bottom: 16px;
}

.task-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-type {
  flex-shrink: 0;
}

.task-title {
  font-weight: 500;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: var(--el-text-color-regular);
  min-width: 35px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.text-primary { color: var(--el-color-primary); }
.text-success { color: var(--el-color-success); }
.text-warning { color: var(--el-color-warning); }
.text-danger { color: var(--el-color-danger); }

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
  
  .task-table {
    font-size: 12px;
  }
  
  .progress-container {
    flex-direction: column;
    gap: 4px;
  }
}</style>