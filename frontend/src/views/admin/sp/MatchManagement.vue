<template>
  <div class="match-management">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="比赛ID">
          <el-input 
            v-model="searchForm.match_id" 
            placeholder="请输入比赛ID" 
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="主队">
          <el-input 
            v-model="searchForm.home_team" 
            placeholder="请输入主队名称" 
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="客队">
          <el-input 
            v-model="searchForm.away_team" 
            placeholder="请输入客队名称" 
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="联赛">
          <el-input 
            v-model="searchForm.league" 
            placeholder="请输入联赛名称" 
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-form-item>
        <el-form-item label="比赛日期">
          <el-date-picker
            v-model="searchForm.dateRange"
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
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增比赛
        </el-button>
        <el-button type="success" @click="handleImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="warning" @click="handleBatchUpdateStatus">
          <el-icon><Refresh /></el-icon>
          批量更新状态
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
      <el-table-column prop="match_id" label="比赛ID" width="120" />
      <el-table-column label="对阵" min-width="250">
        <template #default="scope">
          <div class="match-teams">
            <div class="team home-team">{{ scope.row.home_team }}</div>
            <div class="vs">VS</div>
            <div class="team away-team">{{ scope.row.away_team }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="league" label="联赛" width="120" />
      <el-table-column prop="match_time" label="比赛时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.match_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="比分" width="100">
        <template #default="scope">
          <span v-if="scope.row.status === 'finished' && scope.row.home_score !== null">
            {{ scope.row.home_score }}:{{ scope.row.away_score }}
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="final_result" label="赛果" width="100" />
      <el-table-column label="SP记录数" width="100">
        <template #default="scope">
          <el-tag type="info">{{ scope.row.sp_record_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="handleViewSP(scope.row)">
            SP记录
          </el-button>
          <el-button size="small" type="primary" @click="handleEdit(scope.row)">
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="info" 
            @click="handleViewHistory(scope.row)"
          >
            历史
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
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="比赛ID" prop="match_id">
          <el-input v-model="form.match_id" placeholder="请输入比赛唯一标识" />
        </el-form-item>
        
        <el-row>
          <el-col :span="11">
            <el-form-item label="主队" prop="home_team">
              <el-input v-model="form.home_team" placeholder="请输入主队名称" />
            </el-form-item>
          </el-col>
          <el-col :span="2">&nbsp;</el-col>
          <el-col :span="11">
            <el-form-item label="客队" prop="away_team">
              <el-input v-model="form.away_team" placeholder="请输入客队名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="联赛" prop="league">
          <el-input v-model="form.league" placeholder="请输入联赛/杯赛名称" />
        </el-form-item>
        
        <el-form-item label="比赛时间" prop="match_time">
          <el-date-picker
            v-model="form.match_time"
            type="datetime"
            placeholder="请选择比赛时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择比赛状态" style="width: 100%">
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-form-item>
        
        <el-row v-if="form.status === 'finished'">
          <el-col :span="11">
            <el-form-item label="主队得分" prop="home_score">
              <el-input-number 
                v-model="form.home_score" 
                :min="0" 
                :max="20" 
                style="width: 100%"
                placeholder="主队得分"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2">&nbsp;</el-col>
          <el-col :span="11">
            <el-form-item label="客队得分" prop="away_score">
              <el-input-number 
                v-model="form.away_score" 
                :min="0" 
                :max="20" 
                style="width: 100%"
                placeholder="客队得分"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="最终赛果" prop="final_result">
          <el-input v-model="form.final_result" placeholder="请输入最终赛果" />
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

    <!-- 批量导入对话框 -->
    <el-dialog title="批量导入比赛数据" v-model="importDialogVisible" width="500px">
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        accept=".csv,.xlsx,.json"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">
            支持 CSV、Excel、JSON 格式文件<br>
            字段映射：match_id, home_team, away_team, match_time, league, status
          </div>
        </template>
      </el-upload>
      
      <div v-if="importFile" class="file-info">
        <el-tag>{{ importFile.name }}</el-tag>
        <el-button size="small" @click="importFile = null">移除</el-button>
      </div>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Refresh, UploadFilled } from '@element-plus/icons-vue'
import { getMatchList, createMatch, updateMatch, deleteMatch, batchImportMatches, getMatchSPRecords } from '@/api/sp'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const importLoading = ref(false)
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const formRef = ref()
const tableData = ref([])
const selectedRows = ref([])
const importFile = ref(null)

// 搜索表单
const searchForm = reactive({
  match_id: '',
  home_team: '',
  away_team: '',
  league: '',
  status: '',
  dateRange: []
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
  match_id: '',
  home_team: '',
  away_team: '',
  away_team: '',
  league: '',
  match_time: '',
  status: 'pending',
  home_score: null,
  away_score: null,
  final_result: ''
})

// 表单验证规则
const rules = {
  match_id: [{ required: true, message: '请输入比赛ID', trigger: 'blur' }],
  home_team: [{ required: true, message: '请输入主队名称', trigger: 'blur' }],
  away_team: [{ required: true, message: '请输入客队名称', trigger: 'blur' }],
  match_time: [{ required: true, message: '请选择比赛时间', trigger: 'change' }]
}

// 计算属性
const dialogTitle = computed(() => form.id ? '编辑比赛' : '新增比赛')

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      size: pagination.size
    }
    // 处理日期范围
    if (params.dateRange && params.dateRange.length === 2) {
      params.date_from = params.dateRange[0]
      params.date_to = params.dateRange[1]
      delete params.dateRange
    }
    
    const response = await getMatchList(params)
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    match_id: '',
    home_team: '',
    away_team: '',
    league: '',
    status: '',
    dateRange: []
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
    await ElMessageBox.confirm('确认删除该比赛吗？删除后相关的SP记录也将被删除。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteMatch(row.id)
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
      await updateMatch(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createMatch(form)
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

const handleImport = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    
    await batchImportMatches(formData)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleBatchUpdateStatus = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要更新的比赛')
    return
  }
  
  try {
    await ElMessageBox.prompt('请输入目标状态', '批量更新状态', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^pending|ongoing|finished$/,
      inputErrorMessage: '状态必须是 pending、ongoing 或 finished'
    }).then(async ({ value }) => {
      const ids = selectedRows.value.map(row => row.id)
      // 这里应该调用批量更新状态的API
      ElMessage.info(`已将 ${ids.length} 场比赛状态更新为 ${value}`)
      loadData()
    })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量更新失败')
    }
  }
}

const handleViewSP = (row) => {
  // 跳转到SP记录页面并筛选该比赛的记录
  // 这里可以通过路由参数或者状态管理来实现
  ElMessage.info(`查看比赛 ${row.match_id} 的SP记录`)
}

const handleViewHistory = (row) => {
  ElMessage.info(`查看比赛 ${row.match_id} 的操作历史`)
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
    match_id: '',
    home_team: '',
    away_team: '',
    league: '',
    match_time: '',
    status: 'pending',
    home_score: null,
    away_score: null,
    final_result: ''
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

const getStatusType = (status) => {
  const statusMap = {
    'pending': 'info',
    'ongoing': 'warning',
    'finished': 'success'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '未开始',
    'ongoing': '进行中',
    'finished': '已结束'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.match-management {
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

.match-teams {
  display: flex;
  align-items: center;
  gap: 10px;
}

.team {
  flex: 1;
  text-align: center;
  font-weight: 500;
}

.home-team {
  color: #409EFF;
}

.away-team {
  color: #E6A23C;
}

.vs {
  color: #909399;
  font-size: 12px;
}

.file-info {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
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

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>