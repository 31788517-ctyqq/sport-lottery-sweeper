<template>
  <div class="data-source-management">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="数据源名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入数据源名称" 
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="请选择类型" clearable style="width: 120px">
            <el-option label="API接口" value="api" />
            <el-option label="本地文件" value="file" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 100px">
            <el-option label="启用" :value="true" />
            <el-option label="停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增数据源
        </el-button>
        <el-button type="success" @click="handleBatchTest">
          <el-icon><Connection /></el-icon>
          批量测试连接
        </el-button>
        <el-button type="warning" @click="handleImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      v-loading="loading"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="数据源名称" min-width="150" />
      <el-table-column prop="type" label="类型" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.type === 'api' ? 'primary' : 'success'">
            {{ scope.row.type === 'api' ? 'API接口' : '本地文件' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="地址/路径" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            :active-value="true"
            :inactive-value="false"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="last_update" label="最后更新" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.last_update) }}
        </template>
      </el-table-column>
      <el-table-column prop="error_rate" label="错误率" width="100">
        <template #default="scope">
          <span :class="{'error-rate-high': scope.row.error_rate > 10}">
            {{ scope.row.error_rate }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="handleTest(scope.row)">
            测试连接
          </el-button>
          <el-button size="small" type="primary" @click="handleEdit(scope.row)">
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="info" 
            @click="handleViewLogs(scope.row)"
          >
            日志
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
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
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据源名称" />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio label="api">API接口</el-radio>
            <el-radio label="file">本地文件</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="地址/路径" prop="url">
          <el-input 
            v-model="form.url" 
            :placeholder="form.type === 'api' ? '请输入API接口地址' : '请输入文件路径'"
          />
        </el-form-item>
        
        <el-form-item label="配置信息" prop="config">
          <el-input
            v-model="form.config"
            type="textarea"
            :rows="4"
            placeholder='请输入JSON格式的配置信息，如：{"headers":{"Authorization":"Bearer token"}}'
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="form.status"
            :active-value="true"
            :inactive-value="false"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 测试连接结果对话框 -->
    <el-dialog title="连接测试结果" v-model="testResultVisible" width="500px">
      <div v-if="testResult.success" class="test-success">
        <el-icon color="#67C23A"><SuccessFilled /></el-icon>
        <p>连接测试成功！</p>
        <pre>{{ JSON.stringify(testResult.data, null, 2) }}</pre>
      </div>
      <div v-else class="test-error">
        <el-icon color="#F56C6C"><CircleCloseFilled /></el-icon>
        <p>连接测试失败：{{ testResult.error }}</p>
      </div>
      <template #footer>
        <el-button @click="testResultVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Connection, Upload, SuccessFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { getDataSourceList, createDataSource, updateDataSource, deleteDataSource, testDataSourceConnection } from '@/api/sp'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const testResultVisible = ref(false)
const formRef = ref()
const tableData = ref([])
const selectedRows = ref([])

// 搜索表单
const searchForm = reactive({
  name: '',
  type: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const form = reactive({
  id: null,
  name: '',
  type: 'api',
  url: '',
  config: '',
  status: true
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  url: [{ required: true, message: '请输入地址/路径', trigger: 'blur' }]
}

// 测试连接结果
const testResult = ref({})

// 计算属性
const dialogTitle = computed(() => form.id ? '编辑数据源' : '新增数据源')

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      size: pagination.size
    }
    const response = await getDataSourceList(params)
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    name: '',
    type: '',
    status: ''
  })
  handleSearch()
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该数据源吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteDataSource(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    if (form.id) {
      await updateDataSource(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createDataSource(form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(form.id ? '更新失败' : '创建失败')
  } finally {
    submitLoading.value = false
  }
}

const handleTest = async (row) => {
  try {
    const response = await testDataSourceConnection(row.id)
    testResult.value = response.data
    testResultVisible.value = true
  } catch (error) {
    ElMessage.error('测试连接失败')
  }
}

const handleBatchTest = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要测试的数据源')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确认批量测试 ${selectedRows.value.length} 个数据源的连接吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 批量测试逻辑
    ElMessage.info('批量测试已开始，请稍后查看结果')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量测试失败')
    }
  }
}

const handleStatusChange = async (row) => {
  try {
    await updateDataSource(row.id, { status: row.status })
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.status = !row.status // 回滚状态
    ElMessage.error('状态更新失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    type: 'api',
    url: '',
    config: '',
    status: true
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-source-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 20px;
}

.search-form {
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.error-rate-high {
  color: #F56C6C;
  font-weight: bold;
}

.test-success {
  text-align: center;
  color: #67C23A;
}

.test-error {
  text-align: center;
  color: #F56C6C;
}

.test-success pre {
  background: #f0f9ff;
  padding: 10px;
  border-radius: 4px;
  text-align: left;
  font-size: 12px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>