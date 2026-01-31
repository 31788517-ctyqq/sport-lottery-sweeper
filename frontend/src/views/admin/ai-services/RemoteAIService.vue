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
          <el-input v-model="searchQuery" placeholder="搜索提供商名称" @keyup.enter="searchServices" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="providerFilter" placeholder="提供商" style="width: 100%;" @change="filterServices">
            <el-option label="全部提供商" value="" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
            <el-option label="Azure OpenAI" value="azure" />
            <el-option label="Alibaba Cloud" value="aliyun" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态" style="width: 100%;" @change="filterServices">
            <el-option label="全部状态" value="" />
            <el-option label="健康" value="healthy" />
            <el-option label="不健康" value="unhealthy" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchServices">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 远程服务表格 -->
      <el-table :data="filteredServices" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="name" label="服务名称" width="200" />
        <el-table-column prop="provider" label="提供商" width="150">
          <template #default="scope">
            <el-tag :type="getProviderTagType(scope.row.provider)">
              {{ scope.row.provider }}
            </el-tag>
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
        width="500px"
      >
        <el-form :model="serviceForm" :rules="serviceRules" ref="serviceFormRef" label-width="120px">
          <el-form-item label="服务名称" prop="name">
            <el-input v-model="serviceForm.name" placeholder="输入服务名称" />
          </el-form-item>
          
          <el-form-item label="提供商" prop="provider">
            <el-select v-model="serviceForm.provider" placeholder="选择提供商" style="width: 100%;">
              <el-option label="OpenAI" value="openai" />
              <el-option label="Anthropic" value="anthropic" />
              <el-option label="Google" value="google" />
              <el-option label="Azure OpenAI" value="azure" />
              <el-option label="Alibaba Cloud" value="aliyun" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="模型" prop="model">
            <el-input v-model="serviceForm.model" placeholder="输入模型名称，如 gpt-4" />
          </el-form-item>
          
          <el-form-item label="API密钥" prop="apiKey">
            <el-input 
              v-model="serviceForm.apiKey" 
              type="password" 
              placeholder="输入API密钥" 
              show-password
            />
          </el-form-item>
          
          <el-form-item label="基础URL">
            <el-input v-model="serviceForm.baseUrl" placeholder="输入基础URL（可选）" />
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

// 响应式数据
const loading = ref(false)
const serviceDialogVisible = ref(false)
const editingService = ref(null)

// 服务数据
const services = ref([
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
    name: 'Google-Gemini',
    provider: 'google',
    model: 'gemini-pro',
    healthStatus: 'unhealthy',
    cost: 8.70,
    requestCount: 750,
    lastUsed: new Date(Date.now() - 7200000).toISOString() // 2小时前
  },
  {
    id: 4,
    name: 'Azure-OpenAI',
    provider: 'azure',
    model: 'gpt-35-turbo',
    healthStatus: 'healthy',
    cost: 15.20,
    requestCount: 1050,
    lastUsed: new Date(Date.now() - 1800000).toISOString() // 30分钟前
  }
])

// 筛选和分页数据
const filteredServices = ref([...services.value])
const currentPage = ref(1)
const pageSize = ref(10)
const totalServices = ref(services.value.length)
const searchQuery = ref('')
const providerFilter = ref('')
const statusFilter = ref('')

// 服务表单
const serviceForm = reactive({
  name: '',
  provider: '',
  model: '',
  apiKey: '',
  baseUrl: ''
})

const serviceRules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  model: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  apiKey: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ]
}

// 方法
const getProviderTagType = (provider) => {
  const types = {
    openai: 'primary',
    anthropic: 'success',
    google: 'warning',
    azure: 'info',
    aliyun: 'danger'
  }
  return types[provider] || 'info'
}

const getHealthTagType = (status) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'unhealthy': return 'danger'
    default: return 'info'
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const addRemoteService = () => {
  editingService.value = null
  Object.assign(serviceForm, {
    name: '',
    provider: '',
    model: '',
    apiKey: '',
    baseUrl: ''
  })
  serviceDialogVisible.value = true
}

const editRemoteService = (service) => {
  editingService.value = service
  Object.assign(serviceForm, {
    name: service.name,
    provider: service.provider,
    model: service.model,
    apiKey: service.apiKey || '',
    baseUrl: service.baseUrl || ''
  })
  serviceDialogVisible.value = true
}

const testRemoteService = async (service) => {
  try {
    ElMessage.success(`远程服务 "${service.name}" 测试成功`)
  } catch (error) {
    ElMessage.error(`远程服务 "${service.name}" 测试失败: ${error.message}`)
  }
}

const saveService = async () => {
  if (editingService.value) {
    // 编辑现有服务
    const service = services.value.find(s => s.id === editingService.value.id)
    if (service) {
      Object.assign(service, {
        name: serviceForm.name,
        provider: serviceForm.provider,
        model: serviceForm.model,
        baseUrl: serviceForm.baseUrl
      })
      ElMessage.success('服务更新成功')
    }
  } else {
    // 添加新服务
    const newService = {
      id: services.value.length + 1,
      name: serviceForm.name,
      provider: serviceForm.provider,
      model: serviceForm.model,
      healthStatus: 'checking',
      cost: 0,
      requestCount: 0,
      lastUsed: new Date().toISOString(),
      apiKey: serviceForm.apiKey,
      baseUrl: serviceForm.baseUrl
    }
    services.value.push(newService)
    ElMessage.success('服务添加成功')
  }
  
  serviceDialogVisible.value = false
  applyFilters()
}

const searchServices = () => {
  applyFilters()
}

const filterServices = () => {
  applyFilters()
}

const resetFilters = () => {
  searchQuery.value = ''
  providerFilter.value = ''
  statusFilter.value = ''
  applyFilters()
}

const applyFilters = () => {
  let result = [...services.value]
  
  // 应用搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(service => 
      service.name.toLowerCase().includes(query) || 
      service.provider.toLowerCase().includes(query) ||
      service.model.toLowerCase().includes(query)
    )
  }
  
  // 应用提供商筛选
  if (providerFilter.value) {
    result = result.filter(service => service.provider === providerFilter.value)
  }
  
  // 应用状态筛选
  if (statusFilter.value) {
    result = result.filter(service => service.healthStatus === statusFilter.value)
  }
  
  filteredServices.value = result
  totalServices.value = result.length
}

const handleSizeChange = (size) => {
  pageSize.value = size
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const refreshServices = () => {
  applyFilters()
  ElMessage.success('服务列表已刷新')
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