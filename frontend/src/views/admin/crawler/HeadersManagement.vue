<template>
  <div class="headers-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>请求头管理</h3>
            <p class="subtitle">管理爬虫系统的HTTP请求头，提高数据抓取成功率</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addHeader">添加请求头</el-button>
            <el-button @click="refreshList">刷新</el-button>
            <el-button @click="batchImport">批量导入</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="目标域名">
          <el-input v-model="queryParams.domain" placeholder="请输入目标域名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="启用" value="enabled" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="headersList" style="width: 100%" v-loading="loading">
        <el-table-column prop="domain" label="目标域名" width="200" />
        <el-table-column prop="name" label="请求头名称" width="150" />
        <el-table-column prop="value" label="请求头值" width="250" show-tooltip-when-overflow />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="getTypeTagType(scope.row.type)">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityTagType(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastUsed" label="最后使用" width="150" />
        <el-table-column prop="usageCount" label="使用次数" width="100" />
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.successRate" 
              :color="getSuccessRateColor(scope.row.successRate)"
              :show-text="false"
              :stroke-width="20"
            />
            <span>{{ scope.row.successRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="editHeader(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteHeader(scope.row)">删除</el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'enabled' ? 'info' : 'success'" 
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 'enabled' ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" @click="duplicateHeader(scope.row)">复制</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        style="margin-top: 20px; justify-content: center;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 请求头编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="700px">
      <el-form :model="currentHeader" :rules="headerRules" ref="headerFormRef" label-width="120px">
        <el-form-item label="目标域名" prop="domain">
          <el-input v-model="currentHeader.domain" placeholder="请输入目标域名，如：example.com" />
        </el-form-item>
        <el-form-item label="请求头名称" prop="name">
          <el-input v-model="currentHeader.name" placeholder="请输入请求头名称，如：User-Agent" />
        </el-form-item>
        <el-form-item label="请求头值" prop="value">
          <el-input 
            v-model="currentHeader.value" 
            type="textarea" 
            :rows="4"
            placeholder="请输入请求头值" 
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="currentHeader.type" placeholder="请选择请求头类型">
            <el-option label="通用" value="common" />
            <el-option label="特定网站" value="specific" />
            <el-option label="移动端" value="mobile" />
            <el-option label="桌面端" value="desktop" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="currentHeader.priority" placeholder="请选择优先级">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="currentHeader.status"
            :active-value="'enabled'"
            :inactive-value="'disabled'"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="currentHeader.remarks" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveHeader">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog title="批量导入请求头" v-model="batchImportVisible" width="600px">
      <el-form :model="batchImportForm" label-width="100px">
        <el-form-item label="导入格式">
          <el-radio-group v-model="batchImportForm.format">
            <el-radio label="json">JSON格式</el-radio>
            <el-radio label="text">文本格式</el-radio>
            <el-radio label="csv">CSV格式</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="数据内容">
          <el-input 
            v-model="batchImportForm.content" 
            type="textarea" 
            :rows="8"
            placeholder="请粘贴要导入的请求头数据..." 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchImportVisible = false">取消</el-button>
        <el-button type="primary" @click="doBatchImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const dialogVisible = ref(false)
const batchImportVisible = ref(false)
const dialogTitle = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 查询参数
const queryParams = reactive({
  domain: '',
  status: ''
})

// 当前编辑的请求头
const currentHeader = reactive({
  id: null,
  domain: '',
  name: '',
  value: '',
  type: 'common',
  priority: 'medium',
  status: 'enabled',
  lastUsed: '',
  usageCount: 0,
  successRate: 0,
  remarks: ''
})

// 批量导入表单
const batchImportForm = reactive({
  format: 'json',
  content: ''
})

// 表格数据
const headersList = ref([])

// 请求头表单验证规则
const headerRules = {
  domain: [
    { required: true, message: '请输入目标域名', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入请求头名称', trigger: 'blur' }
  ],
  value: [
    { required: true, message: '请输入请求头值', trigger: 'blur' }
  ]
}

// 获取请求头列表
const getHeadersList = () => {
  loading.value = true
  
  // 模拟获取数据
  setTimeout(() => {
    // 根据查询条件过滤数据
    let data = mockHeadersData
    
    if (queryParams.domain) {
      data = data.filter(item => item.domain.toLowerCase().includes(queryParams.domain.toLowerCase()))
    }
    
    if (queryParams.status) {
      data = data.filter(item => item.status === queryParams.status)
    }
    
    // 计算总数
    total.value = data.length
    
    // 计算当前页数据
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    headersList.value = data.slice(start, end)
    
    loading.value = false
  }, 500)
}

// 搜索
const onQuery = () => {
  currentPage.value = 1
  getHeadersList()
}

// 重置查询
const resetQuery = () => {
  queryParams.domain = ''
  queryParams.status = ''
  currentPage.value = 1
  getHeadersList()
}

// 添加请求头
const addHeader = () => {
  Object.assign(currentHeader, {
    id: null,
    domain: '',
    name: '',
    value: '',
    type: 'common',
    priority: 'medium',
    status: 'enabled',
    lastUsed: '',
    usageCount: 0,
    successRate: 0,
    remarks: ''
  })
  
  dialogTitle.value = '添加请求头'
  dialogVisible.value = true
}

// 编辑请求头
const editHeader = (row) => {
  Object.assign(currentHeader, { ...row })
  dialogTitle.value = '编辑请求头'
  dialogVisible.value = true
}

// 复制请求头
const duplicateHeader = (row) => {
  const newRow = { ...row, id: null, lastUsed: '', usageCount: 0, successRate: 0 }
  Object.assign(currentHeader, newRow)
  dialogTitle.value = '复制请求头'
  dialogVisible.value = true
}

// 保存请求头
const saveHeader = () => {
  // 这里应该是实际的保存逻辑
  console.log('保存请求头:', currentHeader)
  dialogVisible.value = false
  ElMessage.success('保存成功')
  getHeadersList()
}

// 删除请求头
const deleteHeader = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除请求头 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 实际删除逻辑
    console.log('删除请求头:', row)
    ElMessage.success('删除成功')
    getHeadersList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 切换状态
const toggleStatus = (row) => {
  row.status = row.status === 'enabled' ? 'disabled' : 'enabled'
  const statusText = row.status === 'enabled' ? '启用' : '禁用'
  ElMessage.success(`请求头 ${statusText}成功`)
}

// 批量导入
const batchImport = () => {
  batchImportForm.content = ''
  batchImportVisible.value = true
}

// 执行批量导入
const doBatchImport = () => {
  // 模拟导入过程
  console.log('执行批量导入:', batchImportForm)
  batchImportVisible.value = false
  ElMessage.success('批量导入成功')
  getHeadersList()
}

// 刷新列表
const refreshList = () => {
  getHeadersList()
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  getHeadersList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  getHeadersList()
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'enabled': return '启用'
    case 'disabled': return '禁用'
    default: return status
  }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'enabled': return 'success'
    case 'disabled': return 'info'
    default: return 'info'
  }
}

// 获取类型标签类型
const getTypeTagType = (type) => {
  switch (type) {
    case 'common': return 'primary'
    case 'specific': return 'warning'
    case 'mobile': return 'success'
    case 'desktop': return 'danger'
    default: return 'info'
  }
}

// 获取优先级标签类型
const getPriorityTagType = (priority) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

// 获取成功率颜色
const getSuccessRateColor = (rate) => {
  if (rate >= 90) return '#67c23a' // green
  if (rate >= 70) return '#e6a23c' // yellow
  return '#f56c6c' // red
}

// 模拟数据
const mockHeadersData = [
  { id: 1, domain: 'sports.data.com', name: 'User-Agent', value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36', type: 'desktop', priority: 'high', status: 'enabled', lastUsed: '2026-01-30 10:30:00', usageCount: 245, successRate: 92, remarks: 'Chrome浏览器模拟' },
  { id: 2, domain: 'odds.api.com', name: 'Accept', value: 'application/json, text/plain, */*', type: 'common', priority: 'medium', status: 'enabled', lastUsed: '2026-01-30 09:45:20', usageCount: 180, successRate: 88, remarks: '接受JSON格式响应' },
  { id: 3, domain: 'api.soccer.com', name: 'Authorization', value: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', type: 'specific', priority: 'high', status: 'enabled', lastUsed: '2026-01-30 08:20:15', usageCount: 150, successRate: 95, remarks: 'API访问令牌' },
  { id: 4, domain: 'mobile.data.com', name: 'User-Agent', value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15', type: 'mobile', priority: 'medium', status: 'disabled', lastUsed: '2026-01-29 16:30:45', usageCount: 95, successRate: 78, remarks: 'iOS移动设备模拟' },
  { id: 5, domain: 'live.score.net', name: 'Content-Type', value: 'application/json;charset=utf-8', type: 'common', priority: 'low', status: 'enabled', lastUsed: '2026-01-30 11:15:30', usageCount: 320, successRate: 90, remarks: 'POST请求内容类型' },
  { id: 6, domain: 'proxy.service.org', name: 'Proxy-Authorization', value: 'Basic dXNlcjpwYXNzd29yZA==', type: 'specific', priority: 'high', status: 'enabled', lastUsed: '2026-01-30 07:45:10', usageCount: 210, successRate: 85, remarks: '代理服务器认证' },
  { id: 7, domain: 'cache.data.com', name: 'Cache-Control', value: 'no-cache', type: 'common', priority: 'medium', status: 'enabled', lastUsed: '2026-01-29 14:20:05', usageCount: 175, successRate: 82, remarks: '跳过缓存获取最新数据' },
  { id: 8, domain: 'secure.api.com', name: 'X-Requested-With', value: 'XMLHttpRequest', type: 'common', priority: 'low', status: 'disabled', lastUsed: '2026-01-28 12:10:30', usageCount: 60, successRate: 75, remarks: '标识AJAX请求' }
]

onMounted(() => {
  getHeadersList()
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

.search-form {
  margin-bottom: 20px;
}
</style>