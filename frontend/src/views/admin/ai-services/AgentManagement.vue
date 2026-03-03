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

      <!-- 智能体监控面板 -->
      <div class="agent-dashboard">
        <el-row :gutter="20" class="agent-monitor">
          <el-col :span="6">
            <el-card class="monitor-card">
              <div class="monitor-header">
                <i class="el-icon-video-camera"></i>
                <span>活跃智能体</span>
              </div>
              <div class="monitor-value">{{ activeAgentsCount }}</div>
              <div class="monitor-trend">
                <el-tag :type="trendType">{{ trendText }}</el-tag>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="monitor-card">
              <div class="monitor-header">
                <i class="el-icon-time"></i>
                <span>平均响应时间</span>
              </div>
              <div class="monitor-value">{{ avgResponseTime }}ms</div>
              <el-progress :percentage="performanceScore" :stroke-width="8"/>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="monitor-card">
              <div class="monitor-header">
                <i class="el-icon-warning"></i>
                <span>待处理任务</span>
              </div>
              <div class="monitor-value">{{ pendingTasksCount }}</div>
              <el-button size="small" type="primary" @click="viewTaskQueue">查看队列</el-button>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="monitor-card">
              <div class="monitor-header">
                <i class="el-icon-chat-line-round"></i>
                <span>智能体协作</span>
              </div>
              <div class="monitor-value">{{ collaborationScore }}%</div>
              <el-button size="small" @click="optimizeCollaboration">优化协作</el-button>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 批量操作工具栏 -->
      <div v-if="selectedAgents.length > 0" class="batch-operations">
        <el-alert
          :title="`已选择 ${selectedAgents.length} 个智能体`"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px;"
        />
        <div class="batch-buttons">
          <el-button 
            type="success" 
            size="small" 
            @click="startSelected"
            :disabled="!hasStoppedAgents"
          >
            <i class="el-icon-video-play"></i>
            批量启动
          </el-button>
          <el-button 
            type="warning" 
            size="small" 
            @click="stopSelected"
            :disabled="!hasRunningAgents"
          >
            <i class="el-icon-video-pause"></i>
            批量停止
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            @click="restartSelected"
            :disabled="!hasRunningAgents"
          >
            <i class="el-icon-refresh"></i>
            批量重启
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="deleteSelected"
            :disabled="selectedAgents.length === 0"
          >
            <i class="el-icon-delete"></i>
            批量删除
          </el-button>
          <el-button 
            size="small" 
            @click="clearSelection"
          >
            <i class="el-icon-close"></i>
            取消选择
          </el-button>
        </div>
      </div>

      <!-- 智能体表格 -->
      <el-table 
        :data="filteredAgents" 
        style="width: 100%" 
        stripe 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
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
            <el-button size="small" @click="viewAgentDetail(scope.row)">详情</el-button>
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

      <!-- 智能体工作流可视化 -->
      <el-card class="workflow-card" style="margin-top: 20px;">
        <template #header>
          <div class="workflow-header">
            <span>🤖 智能体工作流可视化</span>
            <div class="workflow-actions">
              <el-button size="small" @click="refreshWorkflow">刷新</el-button>
              <el-button size="small" type="primary" @click="showWorkflowDialog">全屏查看</el-button>
            </div>
          </div>
        </template>
        
        <AgentWorkflowVisualization
          :workflow-data="workflowData"
          title="智能体协作工作流"
          :width="800"
          :height="400"
          :interactive="true"
          :show-grid="true"
        />
      </el-card>

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

      <!-- AI_WORKING: coder1 @2026-02-01T14:15:00 - 添加智能体详情视图对话框 -->
      <!-- 智能体详情对话框 -->
      <el-dialog 
        v-model="agentDetailDialogVisible" 
        title="智能体详情"
        width="800px"
      >
        <div v-if="currentAgentDetail" class="agent-detail-container">
          <!-- 基本信息 -->
          <el-card class="detail-section" shadow="never">
            <template #header>
              <div class="detail-header">
                <span>基本信息</span>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="analyzeAgentPerformance(currentAgentDetail.id)"
                >
                  性能分析
                </el-button>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="智能体ID">{{ currentAgentDetail.id }}</el-descriptions-item>
              <el-descriptions-item label="名称">{{ currentAgentDetail.name }}</el-descriptions-item>
              <el-descriptions-item label="类型">
                <el-tag :type="getAgentTypeTag(currentAgentDetail.type)">
                  {{ currentAgentDetail.type }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getAgentStatusTag(currentAgentDetail.status)">
                  {{ currentAgentDetail.status }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="上次执行">{{ currentAgentDetail.lastExecuted }}</el-descriptions-item>
              <el-descriptions-item label="执行次数">{{ currentAgentDetail.executions }}</el-descriptions-item>
              <el-descriptions-item label="错误数">{{ currentAgentDetail.errors }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ currentAgentDetail.lastUpdated }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 性能指标 -->
          <el-card class="detail-section" shadow="never" style="margin-top: 20px;">
            <template #header>
              <span>性能指标</span>
            </template>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="metric-item">
                  <div class="metric-label">成功率</div>
                  <div class="metric-value">{{ calculateSuccessRate(currentAgentDetail) }}%</div>
                  <el-progress :percentage="calculateSuccessRate(currentAgentDetail)" :stroke-width="6" />
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-item">
                  <div class="metric-label">平均执行时间</div>
                  <div class="metric-value">245ms</div>
                  <el-progress :percentage="85" :stroke-width="6" status="success" />
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-item">
                  <div class="metric-label">资源使用率</div>
                  <div class="metric-value">42%</div>
                  <el-progress :percentage="42" :stroke-width="6" status="warning" />
                </div>
              </el-col>
            </el-row>
          </el-card>

          <!-- 操作记录 -->
          <el-card class="detail-section" shadow="never" style="margin-top: 20px;">
            <template #header>
              <div class="detail-header">
                <span>最近操作记录</span>
                <el-button size="small" @click="viewAgentLogs(currentAgentDetail)">查看完整日志</el-button>
              </div>
            </template>
            <el-table :data="agentLogs" style="width: 100%" size="small">
              <el-table-column prop="time" label="时间" width="180" />
              <el-table-column prop="action" label="操作" width="120" />
              <el-table-column prop="result" label="结果" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.result === '成功' ? 'success' : 'danger'" size="small">
                    {{ scope.row.result }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="details" label="详情" />
            </el-table>
          </el-card>
        </div>
        
        <template #footer>
          <el-button @click="agentDetailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="editAgent(currentAgentDetail)">编辑</el-button>
          <el-button 
            :type="currentAgentDetail?.status === 'running' ? 'warning' : 'success'"
            @click="toggleAgentStatus(currentAgentDetail)"
          >
            {{ currentAgentDetail?.status === 'running' ? '停止' : '启动' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- 工作流全屏查看对话框 -->
      <el-dialog
        v-model="workflowDialogVisible"
        title="智能体工作流可视化 - 全屏模式"
        fullscreen
        :close-on-click-modal="false"
      >
        <AgentWorkflowVisualization
          :workflow-data="workflowData"
          title="智能体协作工作流"
          :width="1200"
          :height="700"
          :interactive="true"
          :show-grid="true"
        />
        
        <template #footer>
          <el-button @click="workflowDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="refreshWorkflow">刷新</el-button>
        </template>
      </el-dialog>
      <!-- AI_DONE: coder1 @2026-02-01T14:15:00 -->
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AgentWorkflowVisualization from '@/components/visualization/AgentWorkflowVisualization.vue'

// 响应式数据
const loading = ref(false)
const agentDialogVisible = ref(false)
const editingAgent = ref(null)

// 智能体监控面板数据
const activeAgentsCount = ref(0)
const avgResponseTime = ref(245)
const performanceScore = ref(85)
const pendingTasksCount = ref(12)
const collaborationScore = ref(78)
const trendType = ref('success')
const trendText = ref('+2 个')

// 智能体详情对话框数据
const agentDetailDialogVisible = ref(false)
const currentAgentDetail = ref(null)
const agentLogs = ref([
  {
    time: '2026-01-30 03:30:15',
    action: '赔率监控',
    result: '成功',
    details: '监控了15场比赛的赔率变化'
  },
  {
    time: '2026-01-30 03:25:10',
    action: '数据同步',
    result: '成功',
    details: '同步了3个数据源的比赛信息'
  },
  {
    time: '2026-01-30 03:20:05',
    action: '异常检测',
    result: '失败',
    details: '检测到网络连接超时，已重试'
  },
  {
    time: '2026-01-30 03:15:00',
    action: '定时任务',
    result: '成功',
    details: '执行了每日数据备份'
  }
])

// 工作流可视化数据
const workflowData = ref({
  nodes: [
    { id: '1', name: '数据采集', type: 'crawler', status: 'completed' },
    { id: '2', name: '数据处理', type: 'process', status: 'running' },
    { id: '3', name: '特征提取', type: 'analysis', status: 'pending' },
    { id: '4', name: '模型预测', type: 'prediction', status: 'pending' },
    { id: '5', name: '结果输出', type: 'output', status: 'pending' }
  ],
  edges: [
    { source: '1', target: '2', type: 'data', status: 'success' },
    { source: '2', target: '3', type: 'data', status: 'active' },
    { source: '3', target: '4', type: 'data', status: null },
    { source: '4', target: '5', type: 'result', status: null }
  ],
  metadata: {
    name: '智能体协作工作流',
    description: '展示智能体之间的协作关系和数据流向'
  }
})

const workflowDialogVisible = ref(false)

// 批量操作数据
const selectedAgents = ref([])
const hasStoppedAgents = computed(() => selectedAgents.value.some(agent => agent.status !== 'running'))
const hasRunningAgents = computed(() => selectedAgents.value.some(agent => agent.status === 'running'))

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

// 智能体详情相关方法
const viewAgentDetail = (agent) => {
  currentAgentDetail.value = agent
  agentDetailDialogVisible.value = true
}

const analyzeAgentPerformance = async (agentId) => {
  try {
    ElMessage.info(`正在分析智能体 ${agentId} 的性能...`)
    // 实际应用中可以调用API获取性能数据
    // const response = await api.get(`/api/v1/agents/${agentId}/performance`)
    // showPerformanceDialog(response.data)
    setTimeout(() => {
      ElMessage.success('性能分析完成！')
    }, 1500)
  } catch (error) {
    ElMessage.error('性能分析失败')
  }
}

const calculateSuccessRate = (agent) => {
  if (!agent || !agent.executions) return 0
  const successRate = ((agent.executions - agent.errors) / agent.executions) * 100
  return Math.round(successRate * 100) / 100 // 保留两位小数
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

const handleSelectionChange = (selection) => {
  selectedAgents.value = selection
}

const startSelected = async () => {
  const stoppedAgents = selectedAgents.value.filter(agent => agent.status !== 'running')
  if (stoppedAgents.length === 0) return
  stoppedAgents.forEach(agent => {
    agent.status = 'running'
    agent.lastUpdated = new Date().toISOString().slice(0, 19).replace('T', ' ')
  })
  applyFilters()
  ElMessage.success(`已启动 ${stoppedAgents.length} 个智能体`)
}

const stopSelected = async () => {
  const runningAgents = selectedAgents.value.filter(agent => agent.status === 'running')
  if (runningAgents.length === 0) return
  runningAgents.forEach(agent => {
    agent.status = 'stopped'
    agent.lastUpdated = new Date().toISOString().slice(0, 19).replace('T', ' ')
  })
  applyFilters()
  ElMessage.success(`已停止 ${runningAgents.length} 个智能体`)
}

const restartSelected = async () => {
  const runningAgents = selectedAgents.value.filter(agent => agent.status === 'running')
  if (runningAgents.length === 0) return
  runningAgents.forEach(agent => {
    agent.lastUpdated = new Date().toISOString().slice(0, 19).replace('T', ' ')
  })
  applyFilters()
  ElMessage.success(`已重启 ${runningAgents.length} 个智能体`)
}

const deleteSelected = async () => {
  if (selectedAgents.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定删除已选择的 ${selectedAgents.value.length} 个智能体吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const selectedIds = new Set(selectedAgents.value.map(agent => agent.id))
    agents.value = agents.value.filter(agent => !selectedIds.has(agent.id))
    selectedAgents.value = []
    applyFilters()
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const clearSelection = () => {
  selectedAgents.value = []
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
  
  // 更新监控面板数据
  activeAgentsCount.value = agents.value.filter(agent => agent.status === 'running').length
}

const handleSizeChange = (size) => {
  pageSize.value = size
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 监控面板方法
const viewTaskQueue = () => {
  ElMessage.info('查看任务队列功能待实现')
}

const optimizeCollaboration = () => {
  ElMessage.success('智能体协作优化功能待实现')
}

const refreshAgents = () => {
  applyFilters()
  ElMessage.success('智能体列表已刷新')
}

// 工作流相关方法
const refreshWorkflow = () => {
  ElMessage.info('刷新工作流数据...')
  // 实际应用中这里可以调用API获取最新的工作流数据
  setTimeout(() => {
    ElMessage.success('工作流数据已刷新')
  }, 1000)
}

const showWorkflowDialog = () => {
  workflowDialogVisible.value = true
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

/* 智能体监控面板样式 */
.agent-dashboard {
  margin-bottom: 24px;
}

.agent-monitor {
  margin-bottom: 20px;
}

.monitor-card {
  height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.monitor-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: #606266;
}

.monitor-header i {
  font-size: 18px;
  margin-right: 8px;
}

.monitor-header span {
  font-size: 14px;
  font-weight: 500;
}

.monitor-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 8px 0;
}

.monitor-trend {
  margin-top: 8px;
}

/* 智能体详情对话框样式 */
.agent-detail-container {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-item {
  text-align: center;
  padding: 15px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}
</style>
