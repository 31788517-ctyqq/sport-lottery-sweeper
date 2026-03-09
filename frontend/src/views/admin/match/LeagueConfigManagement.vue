<template>
  <div class="league-config-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>联赛配置管理</h2>
      <p>管理系统支持的联赛信息、数据源配置和展示规则</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="总联赛数"
              :value="tableData.length"
              :precision="0"
            >
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="启用联赛"
              :value="tableData.filter(item => item.status === 'active').length"
              :precision="0"
              style="color: #67c23a"
            >
              <template #prefix>
                <el-icon><CircleCheck /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="禁用联赛"
              :value="tableData.filter(item => item.status === 'inactive').length"
              :precision="0"
              style="color: #f56c6c"
            >
              <template #prefix>
                <el-icon><CircleClose /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="数据源类型"
              :value="dataSourceTypesCount"
              :precision="0"
              style="color: #409eff"
            >
              <template #prefix>
                <el-icon><Connection /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增联赛
      </el-button>
      <el-button type="success" @click="exportConfig">
        <el-icon><Download /></el-icon>
        导出配置
      </el-button>
      <el-button type="warning" @click="batchUpdateStatus">
        <el-icon><Refresh /></el-icon>
        批量更新状态
      </el-button>
      <el-button type="info" @click="showImportDialog('auto')">
        <el-icon><Connection /></el-icon>
        自动导入
      </el-button>
      <el-button type="success" @click="showImportDialog('manual')">
        <el-icon><UploadFilled /></el-icon>
        手动导入
      </el-button>
      <el-button type="warning" @click="showImportDialog('file')">
        <el-icon><Document /></el-icon>
        文件导入
      </el-button>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <el-card>
        <el-form :model="searchForm" inline>
          <el-form-item label="联赛名称">
            <el-input
              v-model="searchForm.league_name"
              placeholder="联赛名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="状态"
              clearable
              style="width: 120px"
            >
              <el-option label="启用" value="active" />
              <el-option label="禁用" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item label="数据源类型">
            <el-select
              v-model="searchForm.data_source_type"
              placeholder="数据源类型"
              clearable
              style="width: 150px"
            >
              <el-option label="官方接口" value="official" />
              <el-option label="爬虫抓取" value="crawler" />
              <el-option label="第三方API" value="third_party" />
            </el-select>
          </el-form-item>
          <el-form-item label="创建时间">
            <el-date-picker
              v-model="searchForm.date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
        </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 联赛配置数据表格 -->
    <div class="table-section">
      <el-table
        :data="tableData" 
        v-loading="loading"
        stripe
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="联赛名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="code" label="联赛代码" width="120" />
        <el-table-column prop="country" label="国家/地区" width="100" />
        <el-table-column prop="season" label="赛季" width="100" />
        <el-table-column label="数据源配置" width="150">
          <template #default="scope">
            <el-tag size="small" type="success" v-if="scope.row.data_source_type === 'official'">官方接口</el-tag>
            <el-tag size="small" type="warning" v-else-if="scope.row.data_source_type === 'crawler'">爬虫抓取</el-tag>
            <el-tag size="small" type="info" v-else>第三方API</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" sortable />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                @click="handleEdit(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="success"
                size="small"
                @click="handleView(scope.row)"
              >
                查看
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDelete(scope.row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
        
    <!-- 分页区域 -->
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
        class="dialog-form"
      >
        <el-form-item label="联赛名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入联赛名称" />
        </el-form-item>
        <el-form-item label="联赛代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入联赛代码" />
        </el-form-item>
        <el-form-item label="国家/地区" prop="country">
          <el-input v-model="form.country" placeholder="请输入国家/地区" />
        </el-form-item>
        <el-form-item label="赛季" prop="season">
          <el-input v-model="form.season" placeholder="请输入赛季" />
        </el-form-item>
        <el-form-item label="数据源类型" prop="data_source_type">
          <el-select v-model="form.data_source_type" placeholder="请选择数据源类型" style="width: 100%">
            <el-option label="官方接口" value="official" />
            <el-option label="爬虫抓取" value="crawler" />
            <el-option label="第三方API" value="third_party" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据源URL" prop="data_source_url">
          <el-input v-model="form.data_source_url" placeholder="请输入数据源URL" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入联赛描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Download, Refresh, Connection, UploadFilled, Document,
  Document as DocumentIcon, CircleCheck, CircleClose, Search, RefreshRight
} from '@element-plus/icons-vue'

// AI_WORKING: coder1 @2026-01-27T00:15:00 - 重建文件解决结构损坏和编译错误
// AI_DONE: coder1 @2026-01-27T00:15:00

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const formRef = ref()
const multipleSelection = ref([])

// 搜索表单
const searchForm = reactive({
  league_name: '',
  status: '',
  data_source_type: '',
  date_range: []
})

// 表单数据
const form = reactive({
  id: null,
  name: '',
  code: '',
  country: '',
  season: '',
  data_source_type: 'official',
  data_source_url: '',
  priority: 1,
  status: 'active',
  description: ''
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入联赛名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入联赛代码', trigger: 'blur' }],
  country: [{ required: true, message: '请输入国家/地区', trigger: 'blur' }],
  data_source_type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }]
}

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 计算属性
const dialogTitle = computed(() => form.id ? '编辑联赛配置' : '新增联赛配置')

// 数据源类型统计
const dataSourceTypesCount = computed(() => {
  const types = new Set(tableData.value.map(item => item.data_source_type))
  return types.size
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟数据
    tableData.value = [
      {
        id: 1,
        name: '英超联赛',
        code: 'EPL',
        country: '英格兰',
        season: '2023-24',
        data_source_type: 'official',
        data_source_url: 'https://api.premierleague.com',
        priority: 1,
        status: 'active',
        created_at: '2023-08-01 10:00:00',
        description: '英格兰足球超级联赛'
      },
      {
        id: 2,
        name: '西甲联赛',
        code: 'LALIGA',
        country: '西班牙',
        season: '2023-24',
        data_source_type: 'crawler',
        data_source_url: 'https://www.laliga.com',
        priority: 2,
        status: 'active',
        created_at: '2023-08-01 11:00:00',
        description: '西班牙足球甲级联赛'
      },
      {
        id: 3,
        name: '德甲联赛',
        code: 'BUNDESLIGA',
        country: '德国',
        season: '2023-24',
        data_source_type: 'third_party',
        data_source_url: 'https://api.football-data.org',
        priority: 3,
        status: 'inactive',
        created_at: '2023-08-01 12:00:00',
        description: '德国足球甲级联赛'
      }
    ]
    
    pagination.total = tableData.value.length
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    league_name: '',
    status: '',
    data_source_type: '',
    date_range: []
  })
  handleSearch()
}

const refreshData = () => {
  fetchData()
  ElMessage.success('数据已刷新')
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleView = (row) => {
  console.log('查看联赛配置:', row)
  ElMessage.info('查看功能开发中...')
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除联赛 "${row.name}" 的配置吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = tableData.value.findIndex(item => item.id === row.id)
    if (index > -1) {
      tableData.value.splice(index, 1)
      pagination.total--
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSelectionChange = (val) => {
  multipleSelection.value = val
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (form.id) {
      // 编辑
      const index = tableData.value.findIndex(item => item.id === form.id)
      if (index > -1) {
        Object.assign(tableData.value[index], form)
        ElMessage.success('更新成功')
      }
    } else {
      // 新增
      form.id = Date.now()
      form.created_at = new Date().toLocaleString('zh-CN')
      tableData.value.unshift({ ...form })
      pagination.total++
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    resetForm()
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    id: null,
    name: '',
    code: '',
    country: '',
    season: '',
    data_source_type: 'official',
    data_source_url: '',
    priority: 1,
    status: 'active',
    description: ''
  })
}

const exportConfig = () => {
  ElMessage.info('导出功能开发中...')
}

const batchUpdateStatus = () => {
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请选择要操作的联赛')
    return
  }
  ElMessage.info('批量更新状态功能开发中...')
}

const showImportDialog = (type) => {
  console.log('显示导入对话框:', type)
  ElMessage.info(`${type}导入功能开发中...`)
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchData()
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.league-config-management {
  padding: 20px;
  background-color: var(--bg-body, #f5f7fa);
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: var(--text-primary, #303133);
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--text-secondary, #909399);
  font-size: 14px;
}

/* 统计卡片区域 */
.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 操作栏 */
.operation-bar {
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  flex-wrap: nowrap;
  align-items: center;
}

.operation-bar .el-button {
  margin-right: 0;
  margin-bottom: 0;
}

/* 筛选栏 */
.filter-section {
  margin-bottom: 24px;
}

.filter-section :deep(.el-card) {
  border-radius: 8px;
}

/* 表格区域 */
.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

/* 分页区域 */
.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: nowrap;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .league-config-management {
    padding: 10px;
  }
  
  .operation-bar {
    flex-direction: column;
  }
  
  .operation-bar .el-button {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .filter-section :deep(.el-form-item) {
    display: block;
    margin-right: 0;
  }
}
</style>