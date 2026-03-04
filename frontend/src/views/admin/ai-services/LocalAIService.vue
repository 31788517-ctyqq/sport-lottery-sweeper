<template>
  <div class="local-ai-service">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>🤖 本地AI服务</h3>
            <p class="subtitle">管理本地AI服务（ClawDBot、Ollama、vLLM、LM Studio等）</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addLocalService">添加本地服务</el-button>
            <el-button @click="refreshServices">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索服务名称" @keyup.enter="searchServices" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="typeFilter" placeholder="服务类型" style="width: 100%;" @change="filterServices">
            <el-option label="全部类型" value="" />
            <el-option label="ClawDBot" value="clawdbot" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="vLLM" value="vllm" />
            <el-option label="LM Studio" value="lmstudio" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="健康状态" style="width: 100%;" @change="filterServices">
            <el-option label="全部状态" value="" />
            <el-option label="健康" value="healthy" />
            <el-option label="降级" value="degraded" />
            <el-option label="不健康" value="unhealthy" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchServices">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 本地服务表格 -->
      <el-table :data="filteredServices" style="width: 100%" stripe v-loading="loading">
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
  },
  {
    id: 3,
    name: 'vLLM-Production',
    type: 'vllm',
    baseUrl: 'http://localhost:8000',
    healthStatus: 'healthy',
    responseTime: 123.5,
    models: ['mixtral-8x7b', 'llama2-70b']
  }
])

// 筛选和分页数据
const filteredServices = ref([...services.value])
const currentPage = ref(1)
const pageSize = ref(10)
const totalServices = ref(services.value.length)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')

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

// 方法
const getHealthTagType = (status) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'unhealthy': return 'danger'
    case 'checking': return 'info'
    default: return 'info'
  }
}

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
    
    const index = services.value.findIndex(s => s.id === service.id)
    if (index !== -1) {
      services.value.splice(index, 1)
      applyFilters()
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

const saveService = async () => {
  // 表单验证
  // 这里应该添加实际的表单验证逻辑
  
  if (editingService.value) {
    // 编辑现有服务
    const service = services.value.find(s => s.id === editingService.value.id)
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
      id: services.value.length + 1,
      name: serviceForm.name,
      type: serviceForm.type,
      baseUrl: serviceForm.baseUrl,
      healthStatus: 'checking',
      responseTime: null,
      models: serviceForm.models.split(',').map(m => m.trim()).filter(m => m)
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
  typeFilter.value = ''
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
      service.type.toLowerCase().includes(query)
    )
  }
  
  // 应用类型筛选
  if (typeFilter.value) {
    result = result.filter(service => service.type === typeFilter.value)
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