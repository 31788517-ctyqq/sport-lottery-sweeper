<template>
  <div class="headers-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>请求头管理</h3>
            <p class="subtitle">管理爬虫系统的 HTTP 请求头，提升数据抓取成功率</p>
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

      <div class="stats-row">
        <el-card class="stat-card">
          <div class="stat-title">总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-title">启用</div>
          <div class="stat-value">{{ stats.enabled }}</div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-title">禁用</div>
          <div class="stat-value">{{ stats.disabled }}</div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-title">成功率</div>
          <div class="stat-value">{{ stats.successRate }}%</div>
        </el-card>
      </div>

      <div class="batch-actions">
        <el-button size="small" type="primary" :disabled="selectedIds.length === 0" @click="batchEnable">批量启用</el-button>
        <el-button size="small" type="warning" :disabled="selectedIds.length === 0" @click="batchDisable">批量禁用</el-button>
        <el-button size="small" :disabled="selectedIds.length === 0" @click="batchTest">批量测试</el-button>
        <el-button size="small" type="danger" :disabled="selectedIds.length === 0" @click="batchRemove">批量删除</el-button>
        <el-button size="small" :disabled="selectedIds.length === 0" @click="openBindDialog()">批量绑定</el-button>
      </div>

      <el-table :data="headersList" style="width: 100%" v-loading="loading" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="48" />
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
            <el-button size="small" @click="openBindDialog(scope.row)">绑定</el-button>
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

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="700px">
      <el-form ref="headerFormRef" :model="currentHeader" :rules="headerRules" label-width="120px">
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
            <el-option label="特定站点" value="specific" />
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

    <el-dialog title="批量导入请求头" v-model="batchImportVisible" width="600px">
      <el-form :model="batchImportForm" label-width="100px">
        <el-form-item label="导入格式">
          <el-radio-group v-model="batchImportForm.format">
            <el-radio value="json">JSON格式</el-radio>
            <el-radio value="text">文本格式</el-radio>
            <el-radio value="csv">CSV格式</el-radio>
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

    <el-dialog title="绑定请求头" v-model="bindDialogVisible" width="520px">
      <el-form :model="bindForm" label-width="110px">
        <el-form-item label="数据源ID">
          <el-input v-model="bindForm.dataSourceId" placeholder="可选，绑定到数据源" />
        </el-form-item>
        <el-form-item label="任务ID">
          <el-input v-model="bindForm.taskId" placeholder="可选，绑定到任务" />
        </el-form-item>
        <el-form-item label="优先级覆盖">
          <el-select v-model="bindForm.priorityOverride" placeholder="可选">
            <el-option label="高" :value="3" />
            <el-option label="中" :value="2" />
            <el-option label="低" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="bindForm.enabled" />
        </el-form-item>
      </el-form>
      <div class="binding-preview">
        <div class="binding-title">当前绑定预览</div>
        <div class="binding-section">
          <div class="binding-section-title">数据源绑定</div>
          <div v-if="bindingInfo.dataSourceBindings.length === 0" class="binding-empty">暂无</div>
          <div v-else class="binding-list">
            <div v-for="item in bindingInfo.dataSourceBindings" :key="`ds-${item.headerId}`">
              {{ item.header?.name }} ({{ item.header?.domain }})
            </div>
          </div>
        </div>
        <div class="binding-section">
          <div class="binding-section-title">任务绑定</div>
          <div v-if="bindingInfo.taskBindings.length === 0" class="binding-empty">暂无</div>
          <div v-else class="binding-list">
            <div v-for="item in bindingInfo.taskBindings" :key="`task-${item.headerId}`">
              {{ item.header?.name }} ({{ item.header?.domain }})
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="bindDialogVisible = false">取消</el-button>
        <el-button @click="loadBindings">加载绑定</el-button>
        <el-button type="primary" @click="confirmBind">绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getHeadersList as getHeadersListApi,
  createHeader,
  updateHeader,
  deleteHeader as deleteHeaderApi,
  batchDeleteHeaders,
  batchTestHeaders,
  getHeaderStats,
  importHeaders,
  bindHeadersToDataSource,
  bindHeadersToTask,
  getHeaderBindings
} from '@/api/headers'

const loading = ref(false)
const dialogVisible = ref(false)
const batchImportVisible = ref(false)
const bindDialogVisible = ref(false)
const dialogTitle = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedIds = ref([])
const headerFormRef = ref()

const stats = reactive({
  total: 0,
  enabled: 0,
  disabled: 0,
  successRate: 100
})

const queryParams = reactive({
  domain: '',
  status: ''
})

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

const batchImportForm = reactive({
  format: 'json',
  content: ''
})

const bindForm = reactive({
  dataSourceId: '',
  taskId: '',
  priorityOverride: null,
  enabled: true,
  headerIds: []
})

const bindingInfo = reactive({
  dataSourceBindings: [],
  taskBindings: []
})

const headersList = ref([])

const headerRules = {
  domain: [{ required: true, message: '请输入目标域名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入请求头名称', trigger: 'blur' }],
  value: [{ required: true, message: '请输入请求头值', trigger: 'blur' }]
}

const getHeadersList = async () => {
  loading.value = true
  try {
    const res = await getHeadersListApi({
      page: currentPage.value,
      size: pageSize.value,
      ...queryParams
    })
    const data = res.data?.items || res.items || []
    headersList.value = data
    total.value = res.data?.total || res.total || 0
  } catch (error) {
    ElMessage.error('加载请求头列表失败')
    console.error('Error loading headers list:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await getHeaderStats()
    const data = res.data || {}
    stats.total = data.total || 0
    stats.enabled = data.enabled || 0
    stats.disabled = data.disabled || 0
    const totalCount = data.total || 0
    stats.successRate = totalCount > 0 ? Math.round((data.enabled / totalCount) * 100) : 100
  } catch (error) {
    console.error('Error loading header stats:', error)
  }
}

const onQuery = () => {
  currentPage.value = 1
  getHeadersList()
  loadStats()
}

const resetQuery = () => {
  queryParams.domain = ''
  queryParams.status = ''
  currentPage.value = 1
  getHeadersList()
  loadStats()
}

const onSelectionChange = (rows) => {
  selectedIds.value = rows.map((row) => row.id)
}

const batchEnable = async () => {
  try {
    await Promise.all(selectedIds.value.map((id) => updateHeader(id, { status: 'enabled' })))
    ElMessage.success('批量启用成功')
    getHeadersList()
    loadStats()
  } catch (error) {
    ElMessage.error('批量启用失败')
  }
}

const batchDisable = async () => {
  try {
    await Promise.all(selectedIds.value.map((id) => updateHeader(id, { status: 'disabled' })))
    ElMessage.success('批量禁用成功')
    getHeadersList()
    loadStats()
  } catch (error) {
    ElMessage.error('批量禁用失败')
  }
}

const batchTest = async () => {
  try {
    await batchTestHeaders({ ids: selectedIds.value })
    ElMessage.success('批量测试已提交')
    loadStats()
  } catch (error) {
    ElMessage.error('批量测试失败')
  }
}

const batchRemove = async () => {
  try {
    await ElMessageBox.confirm('确定删除选中的请求头吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await batchDeleteHeaders({ ids: selectedIds.value })
    ElMessage.success('批量删除成功')
    getHeadersList()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const openBindDialog = (row) => {
  bindForm.headerIds = row ? [row.id] : [...selectedIds.value]
  bindForm.dataSourceId = ''
  bindForm.taskId = ''
  bindForm.priorityOverride = null
  bindForm.enabled = true
  bindDialogVisible.value = true
}

const loadBindings = async () => {
  try {
    bindingInfo.dataSourceBindings = []
    bindingInfo.taskBindings = []
    if (bindForm.dataSourceId) {
      const res = await getHeaderBindings({ data_source_id: Number(bindForm.dataSourceId) })
      bindingInfo.dataSourceBindings = res.data?.dataSourceBindings || []
    }
    if (bindForm.taskId) {
      const res = await getHeaderBindings({ task_id: Number(bindForm.taskId) })
      bindingInfo.taskBindings = res.data?.taskBindings || []
    }
  } catch (error) {
    console.error('Error loading bindings:', error)
  }
}

const confirmBind = async () => {
  try {
    if (!bindForm.dataSourceId && !bindForm.taskId) {
      ElMessage.warning('请填写数据源ID或任务ID')
      return
    }

    if (bindForm.dataSourceId) {
      await bindHeadersToDataSource({
        dataSourceId: Number(bindForm.dataSourceId),
        headerIds: bindForm.headerIds,
        enabled: bindForm.enabled,
        priorityOverride: bindForm.priorityOverride
      })
    }

    if (bindForm.taskId) {
      await bindHeadersToTask({
        taskId: Number(bindForm.taskId),
        headerIds: bindForm.headerIds,
        enabled: bindForm.enabled,
        priorityOverride: bindForm.priorityOverride
      })
    }

    ElMessage.success('绑定成功')
    bindDialogVisible.value = false
  } catch (error) {
    ElMessage.error('绑定失败')
  }
}

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
  headerFormRef.value?.clearValidate()
  dialogTitle.value = '添加请求头'
  dialogVisible.value = true
}

const editHeader = (row) => {
  Object.assign(currentHeader, { ...row })
  headerFormRef.value?.clearValidate()
  dialogTitle.value = '编辑请求头'
  dialogVisible.value = true
}

const duplicateHeader = (row) => {
  const newRow = { ...row, id: null, lastUsed: '', usageCount: 0, successRate: 0 }
  Object.assign(currentHeader, newRow)
  headerFormRef.value?.clearValidate()
  dialogTitle.value = '复制请求头'
  dialogVisible.value = true
}

const saveHeader = async () => {
  try {
    if (!headerFormRef.value) return
    await headerFormRef.value.validate()

    const payload = {
      ...currentHeader,
      domain: currentHeader.domain.trim(),
      name: currentHeader.name.trim(),
      value: currentHeader.value.trim(),
      remarks: (currentHeader.remarks || '').trim()
    }

    if (currentHeader.id) {
      await updateHeader(currentHeader.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createHeader(payload)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    getHeadersList()
    loadStats()
  } catch (error) {
    ElMessage.error(currentHeader.id ? '更新失败' : '创建失败')
    console.error('Error saving header:', error)
  }
}

const deleteHeader = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除请求头 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteHeaderApi(row.id)
    ElMessage.success('删除成功')
    getHeadersList()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('Error deleting header:', error)
    }
  }
}

const toggleStatus = async (row) => {
  try {
    const newStatus = row.status === 'enabled' ? 'disabled' : 'enabled'
    await updateHeader(row.id, { status: newStatus })
    row.status = newStatus
    ElMessage.success(`请求头${newStatus === 'enabled' ? '启用' : '禁用'}成功`)
    loadStats()
  } catch (error) {
    ElMessage.error('切换状态失败')
    console.error('Error toggling header status:', error)
  }
}

const batchImport = () => {
  batchImportForm.content = ''
  batchImportVisible.value = true
}

const doBatchImport = async () => {
  try {
    let importData
    try {
      if (batchImportForm.format === 'json') {
        importData = JSON.parse(batchImportForm.content)
      } else if (batchImportForm.format === 'text') {
        const lines = batchImportForm.content.split('\n').filter((line) => line.trim())
        importData = lines.map((line) => {
          const [domain, name, value, type = 'common', priority = 'medium'] = line.split('|')
          return { domain, name, value, type, priority, status: 'enabled' }
        })
      } else if (batchImportForm.format === 'csv') {
        const lines = batchImportForm.content.split('\n').filter((line) => line.trim())
        const headers = lines[0].split(',').map((h) => h.trim())
        importData = lines.slice(1).map((line) => {
          const values = line.split(',').map((v) => v.trim())
          const obj = {}
          headers.forEach((header, index) => {
            obj[header] = values[index] || ''
          })
          return obj
        })
      }
    } catch {
      ElMessage.error('数据格式错误，请检查输入内容')
      return
    }

    await importHeaders(importData)
    batchImportVisible.value = false
    ElMessage.success('批量导入成功')
    getHeadersList()
    loadStats()
  } catch (error) {
    ElMessage.error('批量导入失败')
    console.error('Error batch importing headers:', error)
  }
}

const refreshList = () => {
  getHeadersList()
  loadStats()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  getHeadersList()
  loadStats()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  getHeadersList()
  loadStats()
}

const getStatusText = (status) => {
  switch (status) {
    case 'enabled': return '启用'
    case 'disabled': return '禁用'
    default: return status
  }
}

const getStatusTagType = (status) => {
  switch (status) {
    case 'enabled': return 'success'
    case 'disabled': return 'info'
    default: return 'info'
  }
}

const getTypeTagType = (type) => {
  switch (type) {
    case 'common': return 'primary'
    case 'specific': return 'warning'
    case 'mobile': return 'success'
    case 'desktop': return 'danger'
    default: return 'info'
  }
}

const getPriorityTagType = (priority) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const getSuccessRateColor = (rate) => {
  if (rate >= 90) return '#67c23a'
  if (rate >= 70) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  getHeadersList()
  loadStats()
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

.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.stat-card {
  flex: 1;
}

.stat-title {
  color: #909399;
  font-size: 12px;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

.batch-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.binding-preview {
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
  margin-top: 10px;
}

.binding-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.binding-section {
  margin-bottom: 8px;
}

.binding-section-title {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
}

.binding-empty {
  color: #c0c4cc;
  font-size: 12px;
}

.binding-list {
  font-size: 12px;
}
</style>
