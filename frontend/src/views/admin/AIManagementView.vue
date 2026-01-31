<template>
  <div class="ai-service-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>🤖 AI服务管理</h3>
            <p class="subtitle">管理本地和远程AI服务配置</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addLocalService">添加本地服务</el-button>
            <el-button @click="refreshServices">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 服务概览 -->
      <el-row :gutter="20" class="overview-stats">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <i class="el-icon-office-building" />
              </div>
              <div class="stat-info">
                <div class="stat-label">本地服务</div>
                <div class="stat-value">{{ localServices.length }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <i class="el-icon-position" />
              </div>
              <div class="stat-info">
                <div class="stat-label">远程服务</div>
                <div class="stat-value">{{ remoteServices.length }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <i class="el-icon-timer" />
              </div>
              <div class="stat-info">
                <div class="stat-label">健康服务</div>
                <div class="stat-value">{{ healthyServicesCount }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <i class="el-icon-setting" />
              </div>
              <div class="stat-info">
                <div class="stat-label">优先策略</div>
                <div class="stat-value">{{ priorityStrategy }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 本地AI服务管理 -->
      <el-tabs v-model="activeTab" class="service-tabs">
        <el-tab-pane label="本地AI服务" name="local">
          <el-table :data="localServices" style="width: 100%" stripe>
            <el-table-column prop="name" label="服务名称" width="200" />
            <el-table-column prop="type" label="服务类型" width="150">
              <template #default="scope">
                <el-tag>{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="baseUrl" label="基础URL" width="300" show-overflow-tooltip />
            <el-table-column prop="healthStatus" label="健康状态" width="120">
              <template #default="scope">
                <el-tag :type="getHealthTagType(scope.row.healthStatus)">
                  {{ scope.row.healthStatus }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="responseTime" label="响应时间(ms)" width="150">
              <template #default="scope">
                {{ scope.row.responseTime ? scope.row.responseTime.toFixed(2) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="models" label="支持模型" width="200">
              <template #default="scope">
                <el-tag 
                  v-for="model in scope.row.models" 
                  :key="model" 
                  size="small" 
                  style="margin-right: 5px;"
                >
                  {{ model }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="testService(scope.row)">测试</el-button>
                <el-button size="small" type="primary" @click="editService(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteService(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="远程AI服务" name="remote">
          <el-table :data="remoteServices" style="width: 100%" stripe>
            <el-table-column prop="name" label="服务名称" width="200" />
            <el-table-column prop="provider" label="提供商" width="150">
              <template #default="scope">
                <el-tag type="success">{{ scope.row.provider }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="model" label="模型" width="150" />
            <el-table-column prop="healthStatus" label="健康状态" width="120">
              <template #default="scope">
                <el-tag :type="getHealthTagType(scope.row.healthStatus)">
                  {{ scope.row.healthStatus }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cost" label="本月成本(¥)" width="150">
              <template #default="scope">
                {{ scope.row.cost ? scope.row.cost.toFixed(2) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="requestCount" label="请求数" width="120" />
            <el-table-column prop="lastUsed" label="最后使用" width="180">
              <template #default="scope">
                {{ scope.row.lastUsed ? formatDate(scope.row.lastUsed) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="testRemoteService(scope.row)">测试</el-button>
                <el-button size="small" type="primary" @click="editRemoteService(scope.row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="成本监控" name="costs">
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon bg-blue">
                    <i class="el-icon-wallet" />
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">本月总成本</div>
                    <div class="stat-value">¥{{ totalMonthlyCost.toFixed(2) }}</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon bg-green">
                    <i class="el-icon-data-analysis" />
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">总请求数</div>
                    <div class="stat-value">{{ totalRequests }}</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon bg-orange">
                    <i class="el-icon-timer" />
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">平均响应时间</div>
                    <div class="stat-value">{{ avgResponseTime.toFixed(2) }}s</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon bg-purple">
                    <i class="el-icon-success-filled" />
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">成功率</div>
                    <div class="stat-value">{{ successRate }}%</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <div ref="costChart" class="chart-container" style="height: 400px; margin-top: 20px;"></div>
        </el-tab-pane>

        <el-tab-pane label="智能体管理" name="agents">
          <el-table :data="agents" style="width: 100%" stripe>
            <el-table-column prop="id" label="ID" width="150" />
            <el-table-column prop="name" label="名称" width="200" />
            <el-table-column prop="type" label="类型" width="150">
              <template #default="scope">
                <el-tag :type="getAgentTypeTag(scope.row.type)">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getAgentStatusTag(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastExecuted" label="上次执行" width="180" />
            <el-table-column prop="executions" label="执行次数" width="100" />
            <el-table-column prop="errors" label="错误数" width="100" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewAgentLogs(scope.row)">查看日志</el-button>
                <el-button 
                  size="small" 
                  :type="scope.row.status === 'running' ? 'warning' : 'success'"
                  @click="toggleAgentStatus(scope.row)"
                >
                  {{ scope.row.status === 'running' ? '停止' : '启动' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="预测模型管理" name="models">
          <el-table :data="models" style="width: 100%" stripe>
            <el-table-column prop="name" label="模型名称" width="200" />
            <el-table-column prop="version" label="版本" width="120" />
            <el-table-column prop="accuracy" label="准确率" width="120">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.accuracy" 
                  :color="getAccuracyColor(scope.row.accuracy)"
                  :format="() => `${scope.row.accuracy}%`"
                />
              </template>
            </el-table-column>
            <el-table-column prop="lastTrained" label="最后训练" width="180" />
            <el-table-column prop="trainingDataSize" label="训练数据量" width="150" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getModelStatusTag(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="retrainModel(scope.row)">重新训练</el-button>
                <el-button size="small" type="primary" @click="deployModel(scope.row)">部署</el-button>
                <el-button size="small" type="info" @click="viewModelDetails(scope.row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="对话助手" name="conversation">
          <div class="conversation-container">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="conversation-sidebar">
                  <template #header>
                    <span>助手列表</span>
                  </template>
                  <div class="assistant-list">
                    <div 
                      v-for="assistant in assistants" 
                      :key="assistant.id"
                      class="assistant-item"
                      :class="{ active: currentAssistant.id === assistant.id }"
                      @click="selectAssistant(assistant)"
                    >
                      <div class="assistant-info">
                        <i class="el-icon-chat-dot-round" />
                        <span>{{ assistant.name }}</span>
                      </div>
                      <el-tag size="small" :type="getAssistantStatusTag(assistant.status)">
                        {{ assistant.status }}
                      </el-tag>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="16">
                <el-card class="conversation-panel">
                  <template #header>
                    <div class="conversation-header">
                      <span>{{ currentAssistant.name }}</span>
                      <el-button size="small" @click="clearConversation">清空对话</el-button>
                    </div>
                  </template>
                  
                  <div class="messages-container">
                    <div 
                      v-for="(msg, index) in currentAssistant.conversation" 
                      :key="index"
                      class="message"
                      :class="msg.sender"
                    >
                      <div class="message-content">
                        <i 
                          :class="msg.sender === 'user' ? 'el-icon-user' : 'el-icon-chat-dot-round'" 
                          class="message-icon"
                        />
                        <div class="message-text">{{ msg.text }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="input-area">
                    <el-input
                      v-model="inputMessage"
                      type="textarea"
                      :rows="3"
                      placeholder="输入您的问题..."
                      @keydown.enter="sendToAssistant"
                    />
                    <el-button 
                      type="primary" 
                      @click="sendToAssistant" 
                      :disabled="!inputMessage.trim()"
                      style="margin-top: 10px;"
                    >
                      发送
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="配置" name="config">
          <el-form :model="configForm" label-width="150px" style="max-width: 600px; margin-top: 20px;">
            <el-form-item label="服务优先级">
              <el-select v-model="configForm.priority" placeholder="选择优先级策略">
                <el-option label="优先本地服务" value="local_first" />
                <el-option label="优先远程服务" value="remote_first" />
                <el-option label="平衡使用" value="balanced" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="故障转移">
              <el-switch v-model="configForm.fallbackEnabled" />
            </el-form-item>
            
            <el-form-item label="健康检查间隔(秒)">
              <el-input-number v-model="configForm.healthCheckInterval" :min="10" :max="300" />
            </el-form-item>
            
            <el-form-item label="最大并发数">
              <el-input-number v-model="configForm.maxConcurrency" :min="1" :max="100" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
              <el-button @click="resetConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加/编辑本地服务对话框 -->
    <el-dialog 
      v-model="serviceDialogVisible" 
      :title="editingService ? '编辑本地服务' : '添加本地服务'" 
      width="500px"
    >
      <el-form :model="serviceForm" :rules="serviceRules" ref="serviceFormRef" label-width="100px">
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="serviceForm.name" placeholder="输入服务名称" />
        </el-form-item>
        
        <el-form-item label="服务类型" prop="type">
          <el-select v-model="serviceForm.type" placeholder="选择服务类型">
            <el-option label="ClawDBot" value="clawdbot" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="vLLM" value="vllm" />
            <el-option label="LM Studio" value="lmstudio" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="基础URL" prop="baseUrl">
          <el-input v-model="serviceForm.baseUrl" placeholder="输入基础URL，如 http://localhost:8080" />
        </el-form-item>
        
        <el-form-item label="API密钥">
          <el-input 
            v-model="serviceForm.apiKey" 
            type="password" 
            placeholder="如果需要请输入API密钥" 
            show-password
          />
        </el-form-item>
        
        <el-form-item label="支持模型">
          <el-input 
            v-model="serviceForm.models" 
            type="textarea" 
            :rows="3"
            placeholder="输入支持的模型名称，用逗号分隔，如: llama2,mistral,phi2" 
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="serviceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveService">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

// 响应式数据
const activeTab = ref('local')
const serviceDialogVisible = ref(false)
const editingService = ref(null)

// 服务数据
const localServices = ref([
  {
    id: 1,
    name: 'ClawDBot-Primary',
    type: 'clawdbot',
    baseUrl: 'http://localhost:8080',
    healthStatus: 'healthy',
    responseTime: 245.3,
    models: ['llama2', 'mistral', 'gemma']
  },
  {
    id: 2,
    name: 'Ollama-Secondary',
    type: 'ollama',
    baseUrl: 'http://localhost:11434',
    healthStatus: 'degraded',
    responseTime: 567.2,
    models: ['llama2', 'phi2', 'mistral']
  }
])

const remoteServices = ref([
  {
    id: 1,
    name: 'OpenAI-GPT4',
    provider: 'openai',
    model: 'gpt-4',
    healthStatus: 'healthy',
    cost: 24.50,
    requestCount: 1200,
    lastUsed: new Date().toISOString()
  },
  {
    id: 2,
    name: 'Anthropic-Claude',
    provider: 'anthropic',
    model: 'claude-3-opus',
    healthStatus: 'healthy',
    cost: 12.30,
    requestCount: 980,
    lastUsed: new Date(Date.now() - 3600000).toISOString() // 1小时前
  },
  {
    id: 3,
    name: 'Gemini-Pro',
    provider: 'google',
    model: 'gemini-pro',
    healthStatus: 'unhealthy',
    cost: 8.70,
    requestCount: 750,
    lastUsed: new Date(Date.now() - 7200000).toISOString() // 2小时前
  }
])

const agents = ref([
  {
    id: 'odds_monitor',
    name: '赔率监控智能体',
    type: 'monitor',
    status: 'running',
    lastExecuted: '2026-01-30 03:30:15',
    executions: 125,
    errors: 2
  },
  {
    id: 'recommendation',
    name: '推荐智能体',
    type: 'recommendation',
    status: 'running',
    lastExecuted: '2026-01-30 03:35:22',
    executions: 89,
    errors: 1
  },
  {
    id: 'collaborative_pred',
    name: '协作预测智能体',
    type: 'prediction',
    status: 'stopped',
    lastExecuted: '2026-01-30 02:45:10',
    executions: 42,
    errors: 5
  },
  {
    id: 'data_analyzer',
    name: '数据分析智能体',
    type: 'analysis',
    status: 'running',
    lastExecuted: '2026-01-30 04:15:30',
    executions: 210,
    errors: 0
  }
])

const models = ref([
  {
    id: 1,
    name: '比赛结果预测模型',
    version: 'v1.2.3',
    accuracy: 85.2,
    lastTrained: '2026-01-25 10:30:00',
    trainingDataSize: 12500,
    status: 'deployed'
  },
  {
    id: 2,
    name: '赔率分析模型',
    version: 'v1.1.0',
    accuracy: 78.5,
    lastTrained: '2026-01-20 14:22:15',
    trainingDataSize: 9800,
    status: 'training'
  },
  {
    id: 3,
    name: '情感分析模型',
    version: 'v2.0.1',
    accuracy: 92.1,
    lastTrained: '2026-01-18 09:15:45',
    trainingDataSize: 15600,
    status: 'deployed'
  }
])

const assistants = ref([
  {
    id: 1,
    name: '体育分析师助手',
    status: 'online',
    conversation: [
      { sender: 'ai', text: '您好！我是体育分析师助手，我可以帮助您分析比赛数据、预测结果等。有什么我可以帮您的吗？' }
    ]
  },
  {
    id: 2,
    name: '赔率计算器',
    status: 'online',
    conversation: [
      { sender: 'ai', text: '您好！我是赔率计算器，可以帮助您计算各种投注策略的预期收益。' }
    ]
  },
  {
    id: 3,
    name: '数据洞察助手',
    status: 'offline',
    conversation: []
  }
])

const currentAssistant = ref(assistants.value[0])
const inputMessage = ref('')

// 统计数据
const healthyServicesCount = ref(0)
const priorityStrategy = ref('local_first')
const totalMonthlyCost = ref(0)
const totalRequests = ref(0)
const avgResponseTime = ref(0)
const successRate = ref(0)

// 图表引用
const costChart = ref(null)

// 配置表单
const configForm = reactive({
  priority: 'local_first',
  fallbackEnabled: true,
  healthCheckInterval: 30,
  maxConcurrency: 10
})

// 服务表单
const serviceForm = reactive({
  name: '',
  type: '',
  baseUrl: '',
  apiKey: '',
  models: ''
})

const serviceRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择服务类型', trigger: 'change' }
  ],
  baseUrl: [
    { required: true, message: '请输入基础URL', trigger: 'blur' }
  ]
}

// 计算健康服务数量
const calculateHealthyServices = () => {
  const localHealthy = localServices.value.filter(s => s.healthStatus === 'healthy').length
  const remoteHealthy = remoteServices.value.filter(s => s.healthStatus === 'healthy').length
  healthyServicesCount.value = localHealthy + remoteHealthy
}

// 计算统计数据
const calculateStats = () => {
  totalMonthlyCost.value = remoteServices.value.reduce((sum, service) => sum + (service.cost || 0), 0)
  totalRequests.value = remoteServices.value.reduce((sum, service) => sum + (service.requestCount || 0), 0)
  const responseTimes = localServices.value.map(s => s.responseTime).filter(rt => rt)
  avgResponseTime.value = responseTimes.length ? responseTimes.reduce((sum, rt) => sum + rt, 0) / responseTimes.length / 1000 : 0
  successRate.value = 98.5 // 模拟成功率
}

// 方法
const addLocalService = () => {
  editingService.value = null
  Object.assign(serviceForm, {
    name: '',
    type: '',
    baseUrl: '',
    apiKey: '',
    models: ''
  })
  serviceDialogVisible.value = true
}

const editService = (service) => {
  editingService.value = service
  Object.assign(serviceForm, {
    name: service.name,
    type: service.type,
    baseUrl: service.baseUrl,
    apiKey: service.apiKey || '',
    models: service.models.join(',')
  })
  serviceDialogVisible.value = true
}

const deleteService = async (service) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除本地服务 "${service.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟删除操作
    const index = localServices.value.findIndex(s => s.id === service.id)
    if (index !== -1) {
      localServices.value.splice(index, 1)
      ElMessage.success('服务删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除服务失败')
    }
  }
}

const testService = async (service) => {
  try {
    // 模拟测试服务
    ElMessage.success(`服务 "${service.name}" 测试成功`)
  } catch (error) {
    ElMessage.error(`服务 "${service.name}" 测试失败: ${error.message}`)
  }
}

const testRemoteService = async (service) => {
  try {
    ElMessage.success(`远程服务 "${service.name}" 测试成功`)
  } catch (error) {
    ElMessage.error(`远程服务 "${service.name}" 测试失败: ${error.message}`)
  }
}

const editRemoteService = (service) => {
  ElMessage.info(`编辑远程服务: ${service.name}`)
}

const saveService = async () => {
  // 表单验证
  // 这里应该添加实际的表单验证逻辑
  
  if (editingService.value) {
    // 编辑现有服务
    const service = localServices.value.find(s => s.id === editingService.value.id)
    if (service) {
      Object.assign(service, {
        name: serviceForm.name,
        type: serviceForm.type,
        baseUrl: serviceForm.baseUrl,
        models: serviceForm.models.split(',').map(m => m.trim()).filter(m => m)
      })
      ElMessage.success('服务更新成功')
    }
  } else {
    // 添加新服务
    const newService = {
      id: localServices.value.length + 1,
      name: serviceForm.name,
      type: serviceForm.type,
      baseUrl: serviceForm.baseUrl,
      healthStatus: 'checking',
      responseTime: null,
      models: serviceForm.models.split(',').map(m => m.trim()).filter(m => m)
    }
    localServices.value.push(newService)
    ElMessage.success('服务添加成功')
  }
  
  serviceDialogVisible.value = false
  calculateHealthyServices()
}

const saveConfig = async () => {
  try {
    // 模拟保存配置
    priorityStrategy.value = configForm.priority
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('配置保存失败')
  }
}

const resetConfig = () => {
  // 重置为默认配置
  configForm.priority = 'local_first'
  configForm.fallbackEnabled = true
  configForm.healthCheckInterval = 30
  configForm.maxConcurrency = 10
}

const getHealthTagType = (status) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'unhealthy': return 'danger'
    case 'checking': return 'info'
    default: return 'info'
  }
}

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
  return status === 'running' ? 'success' : 'info'
}

const getModelStatusTag = (status) => {
  const types = {
    deployed: 'success',
    training: 'warning',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getAccuracyColor = (accuracy) => {
  if (accuracy >= 90) return '#67C23A' // 绿色
  if (accuracy >= 80) return '#E6A23C' // 黄色
  return '#F56C6C' // 红色
}

const getAssistantStatusTag = (status) => {
  return status === 'online' ? 'success' : 'danger'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const refreshServices = () => {
  calculateHealthyServices()
  calculateStats()
  ElMessage.success('服务列表已刷新')
}

// 智能体管理方法
const viewAgentLogs = (agent) => {
  ElMessage.info(`查看${agent.name}日志`)
}

const toggleAgentStatus = async (agent) => {
  try {
    const newStatus = agent.status === 'running' ? 'stopped' : 'running'
    await ElMessageBox.confirm(
      `确定要${agent.status === 'running' ? '停止' : '启动'}智能体 "${agent.name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: agent.status === 'running' ? 'warning' : 'success'
      }
    )
    
    agent.status = newStatus
    ElMessage.success(`智能体已${newStatus === 'running' ? '启动' : '停止'}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 预测模型管理方法
const retrainModel = (model) => {
  ElMessage.info(`开始重新训练模型: ${model.name}`)
}

const deployModel = (model) => {
  ElMessage.success(`模型 ${model.name} 部署成功`)
}

const viewModelDetails = (model) => {
  ElMessage.info(`查看模型 ${model.name} 详情`)
}

// 助手相关方法
const selectAssistant = (assistant) => {
  currentAssistant.value = assistant
}

const clearConversation = () => {
  currentAssistant.value.conversation = [
    { sender: 'ai', text: `您好！我是${currentAssistant.value.name}，有什么可以帮助您的吗？` }
  ]
}

const sendToAssistant = () => {
  if (!inputMessage.value.trim()) return
  
  // 添加用户消息
  currentAssistant.value.conversation.push({
    sender: 'user',
    text: inputMessage.value
  })
  
  // 模拟AI回复
  setTimeout(() => {
    currentAssistant.value.conversation.push({
      sender: 'ai',
      text: `这是关于"${inputMessage.value}"的模拟回复。在实际实现中，这里会调用AI服务。`
    })
    
    // 滚动到底部
    nextTick(() => {
      const container = document.querySelector('.messages-container')
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    })
  }, 1000)
  
  inputMessage.value = ''
}

// 初始化图表
const initCostChart = async () => {
  await nextTick()
  
  if (costChart.value) {
    const chart = echarts.init(costChart.value)
    chart.setOption({
      title: { text: 'AI服务月度成本趋势' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['OpenAI', 'Anthropic', 'Google', '本地服务预估'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'] },
      yAxis: { type: 'value', name: '成本 (¥)', axisLabel: { formatter: '¥{value}' } },
      series: [
        { name: 'OpenAI', type: 'line', data: [1200, 1320, 1010, 1340, 900, 2300, 2100], smooth: true },
        { name: 'Anthropic', type: 'line', data: [800, 920, 810, 740, 600, 1200, 1000], smooth: true },
        { name: 'Google', type: 'line', data: [600, 720, 610, 840, 700, 900, 800], smooth: true },
        { name: '本地服务预估', type: 'line', data: [0, 0, 50, 100, 150, 200, 250], smooth: true, lineStyle: { type: 'dashed' } }
      ]
    })
    
    window.addEventListener('resize', () => chart.resize())
  }
}

onMounted(() => {
  calculateHealthyServices()
  calculateStats()
  initCostChart()
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

.overview-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.service-tabs {
  margin-top: 20px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.conversation-container {
  margin-top: 20px;
}

.conversation-sidebar {
  height: 500px;
}

.assistant-list {
  max-height: 400px;
  overflow-y: auto;
}

.assistant-item {
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assistant-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.assistant-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.conversation-panel {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  margin-bottom: 15px;
  max-height: 300px;
}

.message {
  margin-bottom: 15px;
}

.message.user {
  text-align: right;
}

.message-content {
  display: inline-block;
  max-width: 80%;
}

.message-icon {
  font-size: 18px;
  vertical-align: middle;
  margin-right: 8px;
}

.message-text {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 4px;
  background-color: #e6f3ff;
  color: #303133;
}

.message.user .message-text {
  background-color: #409eff;
  color: white;
}

.input-area {
  margin-top: auto;
}
</style>