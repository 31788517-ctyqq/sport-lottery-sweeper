·<template>
  <div class="remote-ai-service">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>🌐 远程AI服务</h3>
            <p class="subtitle">管理远程AI服务提供商（OpenAI、Anthropic、Google等）</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addRemoteService">添加远程服务</el-button>
            <el-button @click="refreshServices">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索供应商名称" @keyup.enter="searchServices" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="providerFilter" placeholder="供应商类型" style="width: 100%;" @change="filterServices">
            <el-option label="全部供应商" value="" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
            <el-option label="Azure OpenAI" value="azure" />
            <el-option label="阿里云" value="alibaba" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="vLLM" value="vllm" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="健康状态" style="width: 100%;" @change="filterServices">
            <el-option label="全部状态" value="" />
            <el-option label="健康" value="healthy" />
            <el-option label="不健康" value="unhealthy" />
            <el-option label="检查中" value="checking" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchServices">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 批量操作 -->
      <div v-if="selectedServices.length > 0" class="batch-actions" style="margin-bottom: 15px;">
        <el-button size="small" @click="batchEnableSelected">批量启用</el-button>
        <el-button size="small" type="warning" @click="batchDisableSelected">批量禁用</el-button>
        <el-button size="small" type="info" @click="clearSelection">清空选择</el-button>
        <span style="margin-left: 10px; color: #909399; font-size: 14px;">
          已选择 {{ selectedServices.length }} 个供应商
        </span>
      </div>

      <!-- 远程服务表格 -->
      <el-table 
        :data="filteredServices" 
        style="width: 100%" 
        stripe 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="供应商名称" width="180" />
        <el-table-column prop="provider_type" label="供应商类型" width="130">
          <template #default="scope">
            <el-tag :type="getProviderTagType(scope.row.provider_type)">
              {{ getProviderDisplayName(scope.row.provider_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.enabled ? 'success' : 'info'">
              {{ scope.row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="health_status" label="健康状态" width="110">
          <template #default="scope">
            <el-tag :type="getHealthTagType(scope.row.health_status)">
              {{ getHealthStatusDisplayName(scope.row.health_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="scope">
            <el-tag :type="getPriorityTagType(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="default_model" label="默认模型" width="140" />
        <el-table-column prop="successful_requests" label="成功请求" width="110">
          <template #default="scope">
            {{ scope.row.successful_requests || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="failed_requests" label="失败请求" width="110">
          <template #default="scope">
            {{ scope.row.failed_requests || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="success_rate" label="成功率" width="100">
          <template #default="scope">
            {{ scope.row.success_rate !== undefined ? scope.row.success_rate.toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_requests" label="总请求数" width="110" />
        <el-table-column prop="monthly_cost" label="本月成本" width="120">
          <template #default="scope">
            {{ scope.row.monthly_cost !== undefined && scope.row.monthly_cost !== null ? '¥' + scope.row.monthly_cost.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_cost" label="累计成本" width="120">
          <template #default="scope">
            {{ scope.row.total_cost !== undefined && scope.row.total_cost !== null ? '¥' + scope.row.total_cost.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="last_checked_at" label="最后检查" width="160">
          <template #default="scope">
            {{ scope.row.last_checked_at ? formatDate(scope.row.last_checked_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="testRemoteService(scope.row)">测试</el-button>
            <el-button size="small" type="warning" @click="toggleProviderStatus(scope.row)">
              {{ scope.row.enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="primary" @click="editRemoteService(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteService(scope.row)">删除</el-button>
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
        :total="totalServices"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <!-- 添加/编辑远程服务对话框 -->
      <el-dialog 
        v-model="serviceDialogVisible" 
        :title="editingService ? '编辑远程服务' : '添加远程服务'" 
        width="600px"
      >
        <el-form :model="serviceForm" :rules="serviceRules" ref="serviceFormRef" label-width="140px">
          <el-form-item label="供应商名称" prop="name">
            <el-input v-model="serviceForm.name" placeholder="输入供应商名称（唯一标识）" />
          </el-form-item>
          
          <el-form-item label="供应商类型" prop="provider_type">
            <el-select v-model="serviceForm.provider_type" placeholder="选择供应商类型" style="width: 100%;">
              <el-option label="OpenAI" value="openai" />
              <el-option label="Anthropic" value="anthropic" />
              <el-option label="Google" value="google" />
              <el-option label="Azure OpenAI" value="azure" />
              <el-option label="阿里云" value="alibaba" />
              <el-option label="Ollama" value="ollama" />
              <el-option label="vLLM" value="vllm" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="描述" prop="description">
            <el-input 
              v-model="serviceForm.description" 
              type="textarea" 
              :rows="2"
              placeholder="输入供应商描述（可选）" 
            />
          </el-form-item>
          
          <el-form-item label="API密钥" prop="api_key">
            <el-input 
              v-model="serviceForm.api_key" 
              type="password" 
              placeholder="输入API密钥" 
              show-password
            />
            <div class="form-tip">编辑时留空表示不更新密钥</div>
          </el-form-item>
          
          <el-form-item label="基础URL" prop="base_url">
            <el-input v-model="serviceForm.base_url" placeholder="输入基础URL（可选，如 https://api.openai.com/v1）" />
          </el-form-item>
          
          <el-form-item label="默认模型" prop="default_model">
            <el-input v-model="serviceForm.default_model" placeholder="输入默认模型名称，如 gpt-4-turbo" />
          </el-form-item>
          
          <el-form-item label="启用状态" prop="enabled">
            <el-switch v-model="serviceForm.enabled" active-text="启用" inactive-text="禁用" />
          </el-form-item>
          
          <el-form-item label="优先级" prop="priority">
            <el-slider 
              v-model="serviceForm.priority" 
              :min="1" 
              :max="10" 
              :step="1"
              show-stops
              :marks="{1: '高', 5: '中', 10: '低'}"
            />
            <div class="form-tip">数值越小优先级越高（1-10）</div>
          </el-form-item>
          
          <el-form-item label="每分钟请求限制" prop="max_requests_per_minute">
            <el-input-number 
              v-model="serviceForm.max_requests_per_minute" 
              :min="1" 
              :max="1000"
              :step="10"
              placeholder="60"
            />
            <span class="form-tip"> 次/分钟</span>
          </el-form-item>
          
          <el-form-item label="超时时间" prop="timeout_seconds">
            <el-input-number 
              v-model="serviceForm.timeout_seconds" 
              :min="1" 
              :max="300"
              :step="5"
              placeholder="30"
            />
            <span class="form-tip"> 秒</span>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="serviceDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveService">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as llmProviderApi from '@/api/llm-providers'

// 响应式数据
const loading = ref(false)
const serviceDialogVisible = ref(false)
const editingService = ref(null)

// 服务数据
const services = ref([])

// 筛选和分页数据
const filteredServices = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalServices = ref(0)
const searchQuery = ref('')
const providerFilter = ref('')
const statusFilter = ref('')

// 批量选择
const selectedServices = ref([])

// 服务表单
const serviceForm = reactive({
  name: '',
  provider_type: 'openai',
  description: '',
  api_key: '',
  base_url: '',
  default_model: '',
  available_models: [],
  enabled: true,
  priority: 10,
  max_requests_per_minute: 60,
  timeout_seconds: 30,
  rate_limit_strategy: 'fixed_window',
  retry_policy: {},
  circuit_breaker_config: {},
  cost_per_token: {},
  version: '1.0',
  tags: []
})

const serviceRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 2, max: 200, message: '名称长度在2到200个字符之间', trigger: 'blur' }
  ],
  provider_type: [
    { required: true, message: '请选择提供商类型', trigger: 'change' }
  ],
  api_key: [
    { required: true, message: '请输入API密钥', trigger: 'blur' },
    { min: 8, message: 'API密钥长度至少8个字符', trigger: 'blur' }
  ],
  default_model: [
    { required: true, message: '请输入默认模型名称', trigger: 'blur' }
  ]
}

// 方法
const getProviderDisplayName = (providerType) => {
  const typeLower = providerType ? providerType.toLowerCase() : ''
  const names = {
    openai: 'OpenAI',
    anthropic: 'Anthropic',
    google: 'Google',
    azure: 'Azure OpenAI',
    alibaba: '阿里云',
    ollama: 'Ollama',
    vllm: 'vLLM',
    zhipuai: 'ZhipuAi',
    custom: '自定义'
  }
  return names[typeLower] || providerType || '未知'
}

const getProviderTagType = (providerType) => {
  const typeUpper = providerType ? providerType.toUpperCase() : ''
  const types = {
    OPENAI: 'primary',
    ANTHROPIC: 'success',
    GOOGLE: 'warning',
    AZURE: 'info',
    ALIBABA: 'danger',
    OLLAMA: 'success',
    VLLM: 'warning',
    CUSTOM: 'default'
  }
  return types[typeUpper] || 'info'
}

const getHealthStatusDisplayName = (status) => {
  const statusLower = status ? status.toLowerCase() : ''
  switch (statusLower) {
    case 'healthy': return '健康'
    case 'unhealthy': return '不健康'
    case 'checking': return '检查中'
    case 'disabled': return '禁用'
    default: return '未知'
  }
}

const getPriorityTagType = (priority) => {
  if (priority <= 3) return 'danger'      // 高优先级（1-3）
  if (priority <= 6) return 'warning'     // 中优先级（4-6）
  return 'success'                        // 低优先级（7-10）
}

const getHealthTagType = (status) => {
  const statusUpper = status ? status.toUpperCase() : ''
  switch (statusUpper) {
    case 'HEALTHY': return 'success'
    case 'UNHEALTHY': return 'danger'
    case 'CHECKING': return 'info'
    case 'DISABLED': return 'warning'
    default: return 'info'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}



const loadServices = async () => {
  try {
    loading.value = true
    
    // 构建查询参数，过滤空值
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (providerFilter.value) params.provider_type = providerFilter.value
    if (statusFilter.value) params.health_status = statusFilter.value
    
    // 首先获取总数量
    const countResponse = await llmProviderApi.getLLMProvidersCount(params)
    
    // 处理数量响应
    let totalCount = 0
    if (typeof countResponse === 'number') {
      totalCount = countResponse
    } else if (countResponse && typeof countResponse.count === 'number') {
      totalCount = countResponse.count
    } else if (countResponse && typeof countResponse.total === 'number') {
      totalCount = countResponse.total
    } else if (countResponse && Array.isArray(countResponse)) {
      totalCount = countResponse.length
    }
    
    totalServices.value = totalCount
    
    // 获取分页数据
    const listParams = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      order_by: 'priority',
      order_desc: false
    }
    if (searchQuery.value) listParams.search = searchQuery.value
    if (providerFilter.value) listParams.provider_type = providerFilter.value
    if (statusFilter.value) listParams.health_status = statusFilter.value
    
    const response = await llmProviderApi.getLLMProviders(listParams)
    
    // 处理数据响应
    let data = []
    if (Array.isArray(response)) {
      data = response
    } else if (response && Array.isArray(response.data)) {
      data = response.data
    } else if (response && response.providers && Array.isArray(response.providers)) {
      data = response.providers
    }
    
    services.value = data
    filteredServices.value = data
    
    // 如果总数量为0但数据不为空，则更新总数量
    if (totalServices.value === 0 && data.length > 0) {
      totalServices.value = data.length
    }
  } catch (error) {
    console.error('加载LLM供应商失败:', error)
    ElMessage.error('加载LLM供应商失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const addRemoteService = () => {
  editingService.value = null
  Object.assign(serviceForm, {
    name: '',
    provider_type: 'openai',
    description: '',
    api_key: '',
    base_url: '',
    default_model: '',
    available_models: [],
    enabled: true,
    priority: 10,
    max_requests_per_minute: 60,
    timeout_seconds: 30,
    rate_limit_strategy: 'fixed_window',
    retry_policy: {},
    circuit_breaker_config: {},
    cost_per_token: {},
    version: '1.0',
    tags: []
  })
  serviceDialogVisible.value = true
}

const editRemoteService = (service) => {
  editingService.value = service
  Object.assign(serviceForm, {
    name: service.name,
    provider_type: service.provider_type,
    description: service.description || '',
    api_key: '', // 安全考虑，不显示实际API密钥
    base_url: service.base_url || '',
    default_model: service.default_model || '',
    available_models: service.available_models || [],
    enabled: service.enabled,
    priority: service.priority,
    max_requests_per_minute: service.max_requests_per_minute,
    timeout_seconds: service.timeout_seconds,
    rate_limit_strategy: service.rate_limit_strategy,
    retry_policy: service.retry_policy || {},
    circuit_breaker_config: service.circuit_breaker_config || {},
    cost_per_token: service.cost_per_token || {},
    version: service.version || '1.0',
    tags: service.tags || []
  })
  serviceDialogVisible.value = true
}

const testRemoteService = async (service) => {
  try {
    loading.value = true
    const response = await llmProviderApi.testLLMProviderConnection(service.id, {
      test_prompt: 'Hello, please respond with "OK" to confirm connectivity.',
      timeout_ms: 5000
    })
    
    if (response.success) {
      ElMessage.success(`远程服务 "${service.name}" 测试成功，响应时间: ${response.response_time_ms}ms`)
    } else {
      ElMessage.warning(`远程服务 "${service.name}" 测试失败: ${response.message}`)
    }
  } catch (error) {
    console.error('测试LLM供应商连接失败:', error)
    ElMessage.error('测试连接失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const saveService = async () => {
  try {
    loading.value = true
    
    if (editingService.value) {
      // 编辑现有服务
      const updateData = { ...serviceForm }
      // 如果API密钥为空，表示用户不想更新密钥，移除该字段
      if (!updateData.api_key) {
        delete updateData.api_key
      }
      
      await llmProviderApi.updateLLMProvider(editingService.value.id, updateData)
      ElMessage.success('服务更新成功')
    } else {
      // 创建新服务
      await llmProviderApi.createLLMProvider(serviceForm)
      ElMessage.success('服务添加成功')
    }
    
    serviceDialogVisible.value = false
    // 重置到第一页并清除筛选条件，确保新供应商可见
    currentPage.value = 1
    searchQuery.value = ''
    providerFilter.value = ''
    statusFilter.value = ''
    await loadServices()
  } catch (error) {
    console.error('保存LLM供应商失败:', error)
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const searchServices = async () => {
  await loadServices()
}

const filterServices = async () => {
  await loadServices()
}

const resetFilters = () => {
  searchQuery.value = ''
  providerFilter.value = ''
  statusFilter.value = ''
  loadServices()
}

const handleSizeChange = async (size) => {
  pageSize.value = size
  await loadServices()
}

const handleCurrentChange = async (page) => {
  currentPage.value = page
  await loadServices()
}

const refreshServices = async () => {
  await loadServices()
  ElMessage.success('服务列表已刷新')
}

const toggleProviderStatus = async (service) => {
  try {
    const action = service.enabled ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}远程服务 "${service.name}" 吗？`,
      `确认${action}`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    if (service.enabled) {
      await llmProviderApi.disableLLMProvider(service.id)
    } else {
      await llmProviderApi.enableLLMProvider(service.id)
    }
    ElMessage.success(`服务${action}成功`)
    await loadServices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${service.enabled ? '禁用' : '启用'}LLM供应商失败:`, error)
      ElMessage.error(`${service.enabled ? '禁用' : '启用'}失败: ` + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedServices.value = selection
}

const clearSelection = () => {
  selectedServices.value = []
}

const batchEnableSelected = async () => {
  if (selectedServices.value.length === 0) {
    ElMessage.warning('请先选择要操作的供应商')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要启用 ${selectedServices.value.length} 个供应商吗？`,
      '确认批量启用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    const providerIds = selectedServices.value.map(s => s.id)
    const response = await llmProviderApi.batchUpdateLLMProvidersStatus({
      provider_ids: providerIds,
      action: 'enable'
    })
    
    ElMessage.success(`成功启用 ${response.success || response.success_count || 0} 个供应商`)
    clearSelection()
    await loadServices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量启用LLM供应商失败:', error)
      ElMessage.error('批量启用失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const batchDisableSelected = async () => {
  if (selectedServices.value.length === 0) {
    ElMessage.warning('请先选择要操作的供应商')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要禁用 ${selectedServices.value.length} 个供应商吗？`,
      '确认批量禁用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    const providerIds = selectedServices.value.map(s => s.id)
    const response = await llmProviderApi.batchUpdateLLMProvidersStatus({
      provider_ids: providerIds,
      action: 'disable'
    })
    
    ElMessage.success(`成功禁用 ${response.success || response.success_count || 0} 个供应商`)
    clearSelection()
    await loadServices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量禁用LLM供应商失败:', error)
      ElMessage.error('批量禁用失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const deleteService = async (service) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除远程服务 "${service.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await llmProviderApi.deleteLLMProvider(service.id)
    ElMessage.success('服务删除成功')
    await loadServices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除LLM供应商失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 初始化数据
onMounted(() => {
  loadServices()
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

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.batch-actions {
  padding: 12px 16px;
  background-color: #f0f9ff;
  border: 1px solid #d1e9ff;
  border-radius: 4px;
  display: flex;
  align-items: center;
}
</style>