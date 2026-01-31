<template>
  <div class="agent-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>🤖 智能体管理</h3>
            <p class="subtitle">管理各类AI智能体（赔率监控、推荐、预测、数据分析等）</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addAgent">添加智能体</el-button>
            <el-button @click="refreshAgents">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索智能体名称" @keyup.enter="searchAgents" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="typeFilter" placeholder="智能体类型" style="width: 100%;" @change="filterAgents">
            <el-option label="全部类型" value="" />
            <el-option label="监控" value="monitor" />
            <el-option label="推荐" value="recommendation" />
            <el-option label="预测" value="prediction" />
            <el-option label="分析" value="analysis" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态" style="width: 100%;" @change="filterAgents">
            <el-option label="全部状态" value="" />
            <el-option label="运行中" value="running" />
            <el-option label="已停止" value="stopped" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchAgents">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 智能体表格 -->
      <el-table :data="filteredAgents" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="150" />
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="type" label="类型" width="150">
          <template #default="scope">
            <el-tag :type="getAgentTypeTag(scope.row.type)">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getAgentStatusTag(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastExecuted" label="上次执行" width="180" />
        <el-table-column prop="executions" label="执行次数" width="120" />
        <el-table-column prop="errors" label="错误数" width="120" />
        <el-table-column prop="lastUpdated" label="更新时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewAgentLogs(scope.row)">查看日志</el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'running' ? 'warning' : 'success'"
              @click="toggleAgentStatus(scope.row)"
            >
              {{ scope.row.status === 'running' ? '停止' : '启动' }}
            </el-button>
            <el-button size="small" type="primary" @click="editAgent(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalAgents"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <!-- 添加/编辑智能体对话框 -->
      <el-dialog 
        v-model="agentDialogVisible" 
        :title="editingAgent ? '编辑智能体' : '添加智能体'" 
        width="500px"
      >
        <el-form :model="agentForm" :rules="agentRules" ref="agentFormRef" label-width="100px">
          <el-form-item label="智能体ID" prop="id">
            <el-input 
              v-model="agentForm.id" 
              :disabled="!!editingAgent"
              placeholder="输入智能体唯一标识符"
            />
          </el-form-item>
          
          <el-form-item label="名称" prop="name">
            <el-input v-model="agentForm.name" placeholder="输入智能体名称" />
          </el-form-item>
          
          <el-form-item label="类型" prop="type">
            <el-select v-model="agentForm.type" placeholder="选择智能体类型" style="width: 100%;">
              <el-option label="监控" value="monitor" />
              <el-option label="推荐" value="recommendation" />
              <el-option label="预测" value="prediction" />
              <el-option label="分析" value="analysis" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input 
              v-model="agentForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="输入智能体描述（可选）"
            />
          </el-form-item>
          
          <el-form-item label="启用">
            <el-switch v-model="agentForm.enabled" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="agentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAgent">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const agentDialogVisible = ref(false)
const editingAgent = ref(null)

// 智能体数据
const agents = ref([
  {
    id: 'odds_monitor',
    name: '赔率监控智能体',
    type: 'monitor',
    status: 'running',
    lastExecuted: '2026-01-30 03:30:15',
    executions: 125,
    errors: 2,
    lastUpdated: '2026-01-29 15:22:10'
  },
  {
    id: 'recommendation',
    name: '推荐智能体',
    type: 'recommendation',
    status: 'running',
    lastExecuted: '2026-01-30 03:35:22',
    executions: 89,
    errors: 1,
    lastUpdated: '2026-01-29 16:45:30'
  },
  {
    id: 'collaborative_pred',
    name: '协作预测智能体',
    type: 'prediction',
    status: 'stopped',
    lastExecuted: '2026-01-30 02:45:10',
    executions: 42,
    errors: 5,
    lastUpdated: '2026-01-28 14:30:15'
  },
  {
    id: 'data_analyzer',
    name: '数据分析智能体',
    type: 'analysis',
    status: 'running',
    lastExecuted: '2026-01-30 04:15:30',
    executions: 210,
    errors: 0,
    lastUpdated: '2026-01-30 04:10:25'
  },
  {
    id: 'sentiment_analyzer',
    name: '情感分析智能体',
    type: 'analysis',
    status: 'error',
    lastExecuted: '2026-01-30 01:20:45',
    executions: 56,
    errors: 12,
    lastUpdated: '2026-01-29 11:30:05'
  },
  {
    id: 'market_trend',
    name: '市场趋势智能体',
    type: 'analysis',
    status: 'running',
    lastExecuted: '2026-01-30 03:50:12',
    executions: 98,
    errors: 3,
    lastUpdated: '2026-01-29 18:15:40'
  }
])

// 筛选和分页数据
const filteredAgents = ref([...agents.value])
const currentPage = ref(1)
const pageSize = ref(10)
const totalAgents = ref(agents.value.length)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')

// 智能体表单
const agentForm = reactive({
  id: '',
  name: '',
  type: '',
  description: '',
  enabled: true
})

const agentRules = {
  id: [
    { required: true, message: '请输入智能体ID', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_-]*$/, message: 'ID只能包含字母、数字、下划线和短横线，且必须以字母开头', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入智能体名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择智能体类型', trigger: 'change' }
  ]
}

// 方法
const getAgentTypeTag = (type) => {
  const types = {
    monitor: 'primary',
    recommendation: 'success',
    prediction: 'warning',
    analysis: 'info'
  }
  return types[type] || 'info'
}

const getAgentStatusTag = (status) => {
  const types = {
    running: 'success',
    stopped: 'info',
    error: 'danger'
  }
  return types[status] || 'warning'
}

const addAgent = () => {
  editingAgent.value = null
  Object.assign(agentForm, {
    id: '',
    name: '',
    type: '',
    description: '',
    enabled: true
  })
  agentDialogVisible.value = true
}

const editAgent = (agent) => {
  editingAgent.value = agent
  Object.assign(agentForm, {
    id: agent.id,
    name: agent.name,
    type: agent.type,
    description: agent.description,
    enabled: agent.enabled !== undefined ? agent.enabled : true
  })
  agentDialogVisible.value = true
}

const viewAgentLogs = (agent) => {
  ElMessage.info(`查看${agent.name}日志`)
  // 实际应用中可以打开日志查看器
}

const toggleAgentStatus = async (agent) => {
  try {
    const newStatus = agent.status === 'running' ? 'stopped' : 'running'
    const actionText = agent.status === 'running' ? '停止' : '启动'
    
    await ElMessageBox.confirm(
      `确定要${actionText}智能体 "${agent.name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: agent.status === 'running' ? 'warning' : 'success'
      }
    )
    
    agent.status = newStatus
    agent.lastUpdated = new Date().toISOString().slice(0, 19).replace('T', ' ')
    ElMessage.success(`智能体已${newStatus === 'running' ? '启动' : '停止'}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const saveAgent = async () => {
  if (editingAgent.value) {
    // 编辑现有智能体
    const agent = agents.value.find(a => a.id === editingAgent.value.id)
    if (agent) {
      Object.assign(agent, {
        name: agentForm.name,
        type: agentForm.type,
        description: agentForm.description,
        enabled: agentForm.enabled
      })
      ElMessage.success('智能体更新成功')
    }
  } else {
    // 添加新智能体
    const newAgent = {
      id: agentForm.id,
      name: agentForm.name,
      type: agentForm.type,
      status: 'stopped', // 新建的智能体默认为停止状态
      lastExecuted: '-',
      executions: 0,
      errors: 0,
      lastUpdated: new Date().toISOString().slice(0, 19).replace('T', ' '),
      description: agentForm.description,
      enabled: agentForm.enabled
    }
    agents.value.push(newAgent)
    ElMessage.success('智能体添加成功')
  }
  
  agentDialogVisible.value = false
  applyFilters()
}

const searchAgents = () => {
  applyFilters()
}

const filterAgents = () => {
  applyFilters()
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
  applyFilters()
}

const applyFilters = () => {
  let result = [...agents.value]
  
  // 应用搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(agent => 
      agent.name.toLowerCase().includes(query) || 
      agent.id.toLowerCase().includes(query) ||
      (agent.description && agent.description.toLowerCase().includes(query))
    )
  }
  
  // 应用类型筛选
  if (typeFilter.value) {
    result = result.filter(agent => agent.type === typeFilter.value)
  }
  
  // 应用状态筛选
  if (statusFilter.value) {
    result = result.filter(agent => agent.status === statusFilter.value)
  }
  
  filteredAgents.value = result
  totalAgents.value = result.length
}

const handleSizeChange = (size) => {
  pageSize.value = size
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const refreshAgents = () => {
  applyFilters()
  ElMessage.success('智能体列表已刷新')
}

// 初始化数据
onMounted(() => {
  applyFilters()
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

.header-actions {
  display: flex;
  gap: 10px;
}
</style>