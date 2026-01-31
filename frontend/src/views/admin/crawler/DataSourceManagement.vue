<template>
  <div class="data-source-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>数据源管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增数据源
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number text-primary">{{ stats.total }}</div>
              <div class="stats-label">总数据源</div>
            </div>
            <el-icon class="stats-icon"><DataLine /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number text-success">{{ stats.online }}</div>
              <div class="stats-label">在线</div>
            </div>
            <el-icon class="stats-icon"><SuccessFilled /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number text-danger">{{ stats.offline }}</div>
              <div class="stats-label">离线</div>
            </div>
            <el-icon class="stats-icon"><CircleCloseFilled /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number text-warning">{{ stats.avgSuccessRate }}%</div>
              <div class="stats-label">平均成功率</div>
            </div>
            <el-icon class="stats-icon"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card">
      <template #header>
        <span class="card-header">筛选条件</span>
      </template>
      <el-form :model="filterForm" inline class="filter-form">
        <el-form-item label="源名称">
          <el-input 
            v-model="filterForm.name" 
            placeholder="请输入源名称（模糊搜索）" 
            clearable 
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="源ID">
          <el-input 
            v-model="filterForm.sourceId" 
            placeholder="请输入源ID（精确匹配）" 
            clearable 
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="内容分类">
          <el-select 
            v-model="filterForm.category" 
            placeholder="请选择内容分类" 
            clearable 
            style="width: 180px"
          >
            <el-option-group label="情报分类">
              <el-option label="比赛数据" value="match_data" />
              <el-option label="球员信息" value="player_info" />
              <el-option label="球队信息" value="team_info" />
              <el-option label="赔率数据" value="odds_data" />
              <el-option label="新闻资讯" value="news" />
            </el-option-group>
            <el-option-group label="足球SP">
              <el-option label="欧洲赔率" value="euro_odds" />
              <el-option label="亚洲盘口" value="asia_handicap" />
              <el-option label="大小球" value="over_under" />
              <el-option label="进球数" value="goals" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="filterForm.status" 
            placeholder="请选择状态" 
            clearable 
            style="width: 120px"
          >
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span class="card-header">数据源列表</span>
          <div class="table-actions">
            <el-button size="small" @click="batchHealthCheck">批量健康检查</el-button>
            <el-button size="small" type="danger" @click="batchDelete">批量删除</el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="tableData" 
        border 
        stripe 
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sourceId" label="源ID" width="120" />
        <el-table-column prop="name" label="数据源名称" min-width="150" />
        <el-table-column prop="category" label="内容分类" width="120">
          <template #default="scope">
            <el-tag :type="getCategoryTagType(scope.row.category)" size="small">
              {{ getCategoryLabel(scope.row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.successRate" 
              :color="getSuccessRateColor(scope.row.successRate)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="avgResponseTime" label="响应时间(ms)" width="120" />
        <el-table-column prop="lastUpdateTime" label="最后更新" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleTest(scope.row)">测试</el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
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
    </el-card>

    <!-- 新增/编辑数据源弹窗 -->
    <el-dialog 
      v-model="showAddDialog" 
      :title="isEdit ? '编辑数据源' : '新增数据源'" 
      width="800px"
      @close="resetForm"
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
        <el-form-item label="源ID" prop="sourceId">
          <el-input v-model="formData.sourceId" placeholder="自动生成，无需填写" disabled />
        </el-form-item>
          </el-col>
          <el-col :span="12">
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入数据源名称，如&quot;500彩票网竞彩足球&quot;" />
        </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="内容分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择内容分类" style="width: 100%">
            <el-option-group label="情报分类">
              <el-option label="比赛数据" value="match_data" />
              <el-option label="球员信息" value="player_info" />
              <el-option label="球队信息" value="team_info" />
              <el-option label="赔率数据" value="odds_data" />
              <el-option label="新闻资讯" value="news" />
            </el-option-group>
            <el-option-group label="足球SP">
              <el-option label="欧洲赔率" value="euro_odds" />
              <el-option label="亚洲盘口" value="asia_handicap" />
              <el-option label="大小球" value="over_under" />
              <el-option label="进球数" value="goals" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <el-form-item label="数据源地址" prop="url">
          <el-input v-model="formData.url" placeholder="请输入数据源地址，如&quot;https://trade.500.com/jczq/&quot;" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="请求方法" prop="method">
              <el-select v-model="formData.method" style="width: 100%">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number v-model="formData.timeout" :min="1" :max="300" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="请求头" prop="headers">
          <el-input 
            v-model="formData.headers" 
            type="textarea" 
            :rows="3" 
            placeholder='{"Content-Type": "application/json"}'
          />
        </el-form-item>

        <el-form-item label="请求参数" prop="params">
          <el-input 
            v-model="formData.params" 
            type="textarea" 
            :rows="3" 
            placeholder='{"key": "value"}'
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入数据源描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试结果显示弹窗 -->
    <el-dialog v-model="testResult.visible" title="测试结果" width="600px">
      <div v-if="testResult.loading" class="test-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        测试中...
      </div>
      <div v-else>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="测试状态">
            <el-tag :type="testResult.success ? 'success' : 'danger'">
              {{ testResult.success ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应时间">{{ testResult.responseTime }}ms</el-descriptions-item>
          <el-descriptions-item label="状态码">{{ testResult.statusCode }}</el-descriptions-item>
          <el-descriptions-item label="响应数据">
            <pre class="response-data">{{ JSON.stringify(testResult.data, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, DataLine, SuccessFilled, CircleCloseFilled, 
  TrendCharts, Loading 
} from '@element-plus/icons-vue'
import { 
  getSources, createSource, updateSource, deleteSource, 
  batchDeleteSources, healthCheck, batchHealthCheck as apiBatchHealthCheck 
} from '@/api/crawlerSource'

// 响应式数据
const tableData = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const formRef = ref()
const selectedRows = ref([])

// 统计数据
const stats = ref({
  total: 0,
  online: 0,
  offline: 0,
  avgSuccessRate: 0
})

// 筛选表单
const filterForm = reactive({
  name: '',
  sourceId: '',
  category: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive({
  id: null,
  sourceId: '',
  name: '',
  category: '',
  url: '',
  method: 'GET',
  timeout: 30,
  headers: '',
  params: '',
  description: ''
})

// 获取下一个可用的源ID
const getNextSourceId = async () => {
  try {
    // 获取所有数据源以找到最大的源ID
    const res = await getSources({ page: 1, size: 999 }) // 获取足够多的记录
    const sources = res.data?.items || res.items || []
    
    let maxId = 0
    sources.forEach(source => {
      if (source.sourceId && /^\d{3}$/.test(source.sourceId)) {
        const idNum = parseInt(source.sourceId, 10)
        if (idNum > maxId) {
          maxId = idNum
        }
      }
    })
    
    // 生成下一个ID，格式化为3位数
    const nextId = maxId + 1
    return nextId.toString().padStart(3, '0')
  } catch (error) {
    console.error('获取源ID失败:', error)
    // 如果获取失败，返回一个基于时间戳的临时ID
    return Math.floor(Math.random() * 900 + 100).toString()
  }
}

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择内容分类', trigger: 'change' }],
  url: [{ required: true, message: '请输入数据源地址', trigger: 'blur' }]
}

// 测试结果
const testResult = reactive({
  visible: false,
  loading: false,
  success: false,
  responseTime: 0,
  statusCode: 0,
  data: null
})

// 加载数据
const loadData = async () => {
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...filterForm
    }
    const res = await getSources(params)
    tableData.value = res.data?.items || res.items || []
    pagination.total = res.data?.total || res.total || 0
    calculateStats()
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

// 计算统计数据
const calculateStats = () => {
  const data = tableData.value
  stats.value.total = data.length
  stats.value.online = data.filter(item => item.status === 'online').length
  stats.value.offline = data.filter(item => item.status === 'offline').length
  
  if (data.length > 0) {
    const totalRate = data.reduce((sum, item) => sum + (item.successRate || 0), 0)
    stats.value.avgSuccessRate = Math.round(totalRate / data.length)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    name: '',
    sourceId: '',
    category: '',
    status: ''
  })
  handleSearch()
}

// 分页相关
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  showAddDialog.value = true
  resetForm()
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  showAddDialog.value = true
  Object.assign(formData, row)
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除数据源 "${row.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await deleteSource(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const batchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的数据源')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedRows.value.length} 个数据源吗？`, 
      '确认批量删除', 
      { type: 'warning' }
    )
    const ids = selectedRows.value.map(item => item.id)
    await batchDeleteSources(ids)
    ElMessage.success('批量删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 测试
const handleTest = async (row) => {
  testResult.loading = true
  testResult.visible = true
  testResult.success = false
  testResult.data = null

  try {
    const startTime = Date.now()
    const res = await healthCheck(row.id)
    const endTime = Date.now()
    
    testResult.success = res.data?.status === 'online'
    testResult.responseTime = endTime - startTime
    testResult.statusCode = res.data?.statusCode || 200
    testResult.data = res.data
  } catch (error) {
    testResult.success = false
    testResult.data = { error: error.message }
  } finally {
    testResult.loading = false
  }
}

// 批量健康检查
const batchHealthCheck = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要检查的数据源')
    return
  }

  try {
    const ids = selectedRows.value.map(item => item.id)
    await apiBatchHealthCheck(ids)
    ElMessage.success('批量健康检查已发起')
    setTimeout(() => loadData(), 2000)
  } catch (error) {
    ElMessage.error('批量检查失败')
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    let submitData = { ...formData }
    
    if (!isEdit.value) {
      // 新增时自动生成源ID
      const nextSourceId = await getNextSourceId()
      submitData.sourceId = nextSourceId
    }
    
    if (isEdit.value) {
      await updateSource(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createSource(submitData)
      ElMessage.success('创建成功')
    }
    
    showAddDialog.value = false
    loadData()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    id: null,
    sourceId: '',
    name: '',
    category: '',
    url: '',
    method: 'GET',
    timeout: 30,
    headers: '',
    params: '',
    description: ''
  })
  formRef.value?.clearValidate()
}

// 工具方法
const getCategoryLabel = (category) => {
  const labels = {
    match_data: '比赛数据', player_info: '球员信息', team_info: '球队信息',
    odds_data: '赔率数据', news: '新闻资讯', euro_odds: '欧洲赔率',
    asia_handicap: '亚洲盘口', over_under: '大小球', goals: '进球数'
  }
  return labels[category] || category
}

const getCategoryTagType = (category) => {
  const types = {
    match_data: '', player_info: 'info', team_info: 'info',
    odds_data: 'warning', news: '', euro_odds: 'warning',
    asia_handicap: 'warning', over_under: 'warning', goals: 'warning'
  }
  return types[category] || ''
}

const getStatusLabel = (status) => {
  const labels = {
    online: '在线', offline: '离线', maintenance: '维护中'
  }
  return labels[status] || status
}

const getStatusTagType = (status) => {
  const types = {
    online: 'success', offline: 'danger', maintenance: 'warning'
  }
  return types[status] || ''
}

const getSuccessRateColor = (rate) => {
  if (rate >= 90) return '#67C23A'
  if (rate >= 70) return '#E6A23C'
  return '#F56C6C'
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-source-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-card {
  position: relative;
  overflow: hidden;
}

.stats-content {
  position: relative;
  z-index: 2;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 8px;
}

.stats-label {
  color: #909399;
  font-size: 14px;
}

.stats-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  opacity: 0.3;
  z-index: 1;
}

.text-primary { color: #409EFF; }
.text-success { color: #67C23A; }
.text-danger { color: #F56C6C; }
.text-warning { color: #E6A23C; }

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.filter-form {
  margin: 0;
}

.table-card {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.test-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
}

.response-data {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow: auto;
  margin: 0;
}

:deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-progress-bar__outer) {
  background-color: #f0f0f0;
}
</style>