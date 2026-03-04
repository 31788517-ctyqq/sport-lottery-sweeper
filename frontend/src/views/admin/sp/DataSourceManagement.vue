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
          <el-radio-group v-model="form.type" @change="handleTypeChange">
            <el-radio value="api">API接口</el-radio>
            <el-radio value="file">本地文件</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          v-if="form.type === 'api'" 
          label="地址/路径" 
          prop="url"
        >
          <el-input 
            v-model="form.url" 
            placeholder="请输入API接口地址"
          />
        </el-form-item>
        
        <el-form-item 
          v-else 
          label="上传文件" 
          prop="url"
        >
          <div class="file-upload-section">
            <el-upload
              class="upload-demo"
              drag
              :action="uploadUrl"
              :on-success="handleFileUploadSuccess"
              :on-error="handleFileUploadError"
              :before-upload="beforeFileUpload"
              :file-list="fileList"
              :show-file-list="true"
              accept=".csv,.xlsx,.xls,.json,.txt"
            >
              <div v-if="!uploadedFile" class="upload-placeholder">
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或<em>点击上传</em>
                </div>
                <div class="el-upload__tip">
                  只能上传 csv/xlsx/xls/json/txt 文件
                </div>
              </div>
              <div v-else class="uploaded-file-info">
                <div class="file-name">{{ uploadedFile.name }}</div>
                <div class="file-size">{{ formatFileSize(uploadedFile.size) }}</div>
              </div>
            </el-upload>
            
            <div v-if="uploadedFile" class="file-path-display">
              <el-input 
                v-model="form.url" 
                placeholder="上传后的文件路径"
                readonly
              >
                <template #prepend>{{ storagePrefix }}</template>
              </el-input>
              <el-button 
                type="danger" 
                size="small" 
                @click="removeUploadedFile"
                style="margin-left: 10px;"
              >
                重新选择
              </el-button>
            </div>
          </div>
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
import { Plus, Connection, Upload, SuccessFilled, CircleCloseFilled, UploadFilled } from '@element-plus/icons-vue'
import { getDataSourceList, createDataSource, updateDataSource, deleteDataSource, testDataSourceConnection } from '@/api/sp'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const testResultVisible = ref(false)
const formRef = ref()
const tableData = ref([])
const selectedRows = ref([])
const fileList = ref([])
const uploadedFile = ref(null)

// 上传相关配置
const uploadUrl = ref(`${import.meta.env.VITE_API_BASE_URL}/admin/sp/upload-file`) // 假设后端有这个上传接口
const storagePrefix = ref('/uploads/') // 假设文件存储在该路径下

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
  url: [
    { 
      required: true, 
      message: '请输入地址/路径', 
      trigger: 'blur',
      validator: validateUrl 
    }
  ]
}

// 测试连接结果
const testResult = ref({})

// 计算属性
const dialogTitle = computed(() => form.id ? '编辑数据源' : '新增数据源')

// 验证URL
function validateUrl(rule, value, callback) {
  if (form.type === 'api' && !value) {
    callback(new Error('请输入API接口地址'))
  } else if (form.type === 'file' && !value && !uploadedFile.value) {
    callback(new Error('请上传文件'))
  } else {
    callback()
  }
}

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
  // 如果是文件类型，提取文件名显示
  if (form.type === 'file' && form.url) {
    uploadedFile.value = {
      name: form.url.split('/').pop(),
      size: 0 // 实际应用中可能需要从后端获取文件大小
    }
  }
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
    // 特殊处理文件类型：如果选择了文件类型但还没有URL，但是有上传的文件，则使用上传的文件
    if (form.type === 'file' && !form.url && uploadedFile.value) {
      form.url = storagePrefix.value + uploadedFile.value.name
    }
    
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
    console.error('提交错误:', error)
    if (error?.message?.includes('ElUpload')) {
      // 这是Element Plus上传组件的错误
      ElMessage.error('请先上传文件')
    } else if (error?.toString().includes('表单验证失败')) {
      ElMessage.error('请填写必填字段')
    } else {
      ElMessage.error(form.id ? '更新失败' : '创建失败')
    }
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
  uploadedFile.value = null
  fileList.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  // 尝试解析ISO格式日期字符串
  let dateObj
  if (typeof date === 'string') {
    dateObj = new Date(date)
  } else {
    dateObj = date
  }
  
  // 检查日期是否有效
  if (isNaN(dateObj.getTime())) {
    return '-'
  }
  
  // 格式化为本地日期时间字符串
  return dateObj.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 添加缺失的handleViewLogs方法
const handleViewLogs = (row) => {
  // 跳转到日志页面，传入数据源ID
  ElMessage.info('跳转到日志查看页面，当前仅作演示')
  console.log('查看数据源', row.id, '的日志')
}

// 添加缺失的handleImport方法
const handleImport = () => {
  ElMessage.info('批量导入功能，当前仅作演示')
  console.log('开始批量导入数据源')
}

// 处理类型变化
const handleTypeChange = (type) => {
  if (type === 'api') {
    // 切换到API时不处理
  } else {
    // 切换到文件类型时清空URL，准备上传文件
    form.url = ''
    uploadedFile.value = null
  }
}

// 文件上传相关方法
const beforeFileUpload = (file) => {
  const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json', 'text/plain']
  const isAllowedType = allowedTypes.includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 20 // 限制20MB

  if (!isAllowedType) {
    ElMessage.error('只能上传csv/xlsx/xls/json/txt格式的文件!')
  }
  if (!isLt2M) {
    ElMessage.error('文件大小不能超过20MB!')
  }

  return isAllowedType && isLt2M
}

const handleFileUploadSuccess = (response, file) => {
  ElMessage.success('文件上传成功')
  uploadedFile.value = file
  // 假设后端返回文件路径，或者直接使用文件名
  form.url = storagePrefix.value + file.name
}

const handleFileUploadError = (error) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败')
}

const removeUploadedFile = () => {
  uploadedFile.value = null
  form.url = ''
  fileList.value = []
  ElMessage.info('已清除已上传的文件')
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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

.file-upload-section {
  width: 100%;
}

.upload-demo {
  width: 100%;
}

.upload-placeholder {
  text-align: center;
  padding: 20px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.uploaded-file-info {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 10px;
}

.file-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.file-size {
  color: #909399;
  font-size: 12px;
}

.file-path-display {
  display: flex;
  align-items: center;
  margin-top: 15px;
}
</style>