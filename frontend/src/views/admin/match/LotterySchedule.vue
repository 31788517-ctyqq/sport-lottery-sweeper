<template>
  <div class="lottery-schedule">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>竞彩赛程管理</h2>
      <p>管理和监控所有竞彩赛程的执行状态</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="总赛程数"
              :value="matchStats.totalMatches"
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
              title="未开始"
              :value="matchStats.pendingMatches"
              :precision="0"
              style="color: #e6a23c"
            >
              <template #prefix>
                <el-icon><Clock /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="进行中"
              :value="matchStats.runningMatches"
              :precision="0"
              style="color: #409eff"
            >
              <template #prefix>
                <el-icon><VideoPlay /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="已结束"
              :value="matchStats.finishedMatches"
              :precision="0"
              style="color: #67c23a"
            >
              <template #prefix>
                <el-icon><CircleCheck /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" :icon="Plus" @click="handleAdd">
        新增赛程
      </el-button>
      <el-button type="danger" @click="batchDeleteMatches" :disabled="selectedMatches.length === 0">
        <el-icon><Delete /></el-icon>
        批量删除
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
              placeholder="请输入联赛名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="请选择状态"
              clearable
              style="width: 120px"
            >
              <el-option label="未开始" value="pending" />
              <el-option label="进行中" value="running" />
              <el-option label="已结束" value="finished" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="日期范围">
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
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 任务列表 -->
    <div class="table-section">
      <el-table
        :data="tableData"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="场次编号" width="110">
          <template #default="scope">
            <div class="match-number">{{ formatMatchNumber(scope.row.id, scope.row.match_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="联赛" width="80" show-overflow-tooltip>
          <template #default="scope">
            <div class="league-name-simple">{{ simplifyLeagueName(scope.row.league_name) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="home_team" label="主队" min-width="100" show-overflow-tooltip />
        <el-table-column prop="away_team" label="客队" min-width="100" show-overflow-tooltip />
        <el-table-column prop="match_time" label="比赛时间" width="190">
          <template #default="scope">
            <div class="match-time-compact">{{ scope.row.match_time }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag
              :type="getStatusType(scope.row.status)"
              size="small"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="比分" width="80" />
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="scope">
            <div class="action-buttons-compact">
              <el-button 
                type="primary" 
                size="small" 
                @click="handleView(scope.row)"
                class="compact-btn">
                查看
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="handleEdit(scope.row)"
                :disabled="['finished', 'cancelled'].includes(scope.row.status)"
                class="compact-btn">
                编辑
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="handleDelete(scope.row)"
                :disabled="scope.row.status === 'running'"
                class="compact-btn">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px" class="dialog-form">
        <el-form-item label="联赛名称" prop="league_name">
          <el-input v-model="form.league_name" placeholder="请输入联赛名称" />
        </el-form-item>
        <el-form-item label="主队" prop="home_team">
          <el-input v-model="form.home_team" placeholder="请输入主队名称" />
        </el-form-item>
        <el-form-item label="客队" prop="away_team">
          <el-input v-model="form.away_team" placeholder="请输入客队名称" />
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
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="running" />
            <el-option label="已结束" value="finished" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="比分" prop="score">
          <el-input v-model="form.score" placeholder="请输入比分，格式如：2-1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'  // 替代axios
import { Search, Edit, Delete, Plus, Refresh, Download, Upload, InfoFilled, Calendar, Clock, Flag } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const formRef = ref()

// 搜索表单
const searchForm = reactive({
  league_name: '',
  status: '',
  date_range: []
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 选中的赛程
const selectedMatches = ref([])

// 表单数据
const form = reactive({
  id: null,
  league_name: '',
  home_team: '',
  away_team: '',
  match_time: '',
  status: 'pending',
  score: ''
})

// 表单验证规则
const formRules = {
  league_name: [{ required: true, message: '请输入联赛名称', trigger: 'blur' }],
  home_team: [{ required: true, message: '请输入主队名称', trigger: 'blur' }],
  away_team: [{ required: true, message: '请输入客队名称', trigger: 'blur' }],
  match_time: [{ required: true, message: '请选择比赛时间', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 计算属性
const dialogTitle = computed(() => form.id ? '编辑赛程' : '新增赛程')

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    running: 'primary',
    finished: 'success',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '未开始',
    running: '进行中',
    finished: '已结束',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 获取星期几的中文表示
const getWeekdayText = (matchTime) => {
  if (!matchTime) return ''
  const date = new Date(matchTime)
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weekdays[date.getDay()]
}

// 格式化场次编号为 "周一 001" 格式
const formatMatchNumber = (id, matchTime) => {
  const weekday = getWeekdayText(matchTime)
  const sequence = String(id).padStart(3, '0')
  return `${weekday} ${sequence}`
}

// 简化联赛名称，如"西甲联赛"->"西甲"
const simplifyLeagueName = (leagueName) => {
  if (!leagueName) return ''
  // 移除常见的后缀：联赛、杯赛、锦标赛等
  return leagueName.replace(/(联赛|杯赛|锦标赛|超级联赛)$/, '')
}

// 统计数据计算
const matchStats = computed(() => {
  const stats = {
    totalMatches: tableData.value.length,
    pendingMatches: 0,
    runningMatches: 0,
    finishedMatches: 0
  }
  
  tableData.value.forEach(row => {
    switch(row.status) {
      case 'pending':
        stats.pendingMatches++
        break
      case 'running':
        stats.runningMatches++
        break
      case 'finished':
        stats.finishedMatches++
        break
    }
  })
  
  return stats
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (searchForm.league_name) {
      params.league_name = searchForm.league_name
    }
    
    if (searchForm.status) {
      params.status = searchForm.status
    }
    
    if (searchForm.date_range && searchForm.date_range.length === 2) {
      params.date_from = searchForm.date_range[0]
      params.date_to = searchForm.date_range[1]
    }
    
    const response = await request.get('/api/admin/v1/lottery-schedules/', { params });
    schedules.value = response.data.items || [];
    total.value = response.data.total || 0;

    if (response.data.success) {
      tableData.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取赛程数据失败')
    }
  } catch (error) {
    console.error('获取赛程数据失败:', error)
    ElMessage.error('获取赛程数据失败')
  } finally {
    loading.value = false
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await request.get('/api/admin/v1/lottery-schedules/stats');
    stats.value = response.data;

    if (response.data.success) {
      // 更新全局统计数据
      const stats = response.data.data
      // 直接修改响应式对象
      Object.assign(matchStats.value, stats)
    } else {
      console.error('获取统计数据失败:', response.data.message)
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    league_name: '',
    status: '',
    date_range: []
  })
  pagination.page = 1
  fetchData()
}

// 刷新数据
const refreshData = () => {
  fetchData()
  fetchStats()
  ElMessage.success('数据已刷新')
}

// 表格多选事件
const handleSelectionChange = (selection) => {
  selectedMatches.value = selection
}

// 批量删除赛程
const batchDeleteMatches = async () => {
  if (selectedMatches.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedMatches.value.length} 个赛程吗？`,
      '确认批量删除',
      { type: 'warning' }
    )
    
    const promises = selectedMatches.value.map(async (selected) => {
      await request.delete(`/api/admin/v1/lottery-schedules/${selected.id}`);
    })
    
    await Promise.all(promises)
    await fetchData()
    selectedMatches.value = []
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 新增
const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  ElMessage.info(`查看赛程：${row.league_name} ${row.home_team} vs ${row.away_team}`)
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除赛程 "${row.league_name} ${row.home_team} vs ${row.away_team}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await request.delete(`/api/admin/v1/lottery-schedules/${row.id}`);
    await fetchData()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    if (form.id) {
      // 编辑模式：更新现有数据
      const response = await request.put(`/api/admin/v1/lottery-schedules/${form.id}`, {
        league_name: form.league_name,
        home_team: form.home_team,
        away_team: form.away_team,
        match_time: form.match_time,
        status: form.status,
        score: form.score
      })
      
      if (response.data.success) {
        await fetchData()
        dialogVisible.value = false
        ElMessage.success('更新成功')
      } else {
        ElMessage.error(response.data.message || '更新失败')
      }
    } else {
      // 新增模式：添加新数据
      const response = await request.post('/api/admin/v1/lottery-schedules/', {
        league_name: form.league_name,
        home_team: form.home_team,
        away_team: form.away_team,
        match_time: form.match_time,
        status: form.status,
        score: form.score
      })
      
      if (response.data.success) {
        await fetchData()
        dialogVisible.value = false
        ElMessage.success('创建成功')
      } else {
        ElMessage.error(response.data.message || '创建失败')
      }
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    league_name: '',
    home_team: '',
    away_team: '',
    match_time: '',
    status: 'pending',
    score: ''
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 分页大小改变
const handleSizeChange = (val) => {
  pagination.size = val
  pagination.page = 1
  fetchData()
}

// 当前页改变
const handleCurrentChange = (val) => {
  pagination.page = val
  fetchData()
}

// 初始化
onMounted(() => {
  fetchData()
  fetchStats()
})
</script>

<style scoped>
.lottery-schedule {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.match-number {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  line-height: 1.2;
}

.match-time-compact {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.action-buttons-compact {
  display: flex;
  gap: 4px;
  white-space: nowrap;
}

.action-buttons-compact .compact-btn {
  padding: 4px 8px;
  min-height: 28px;
  font-size: 12px;
}

.action-buttons-compact .el-button + .el-button {
  margin-left: 0;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.operation-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
}

.table-section {
  background: white;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.dialog-form .el-form-item {
  margin-bottom: 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .lottery-schedule {
    padding: 10px;
  }
  
  .operation-bar {
    flex-direction: column;
  }
  
  .filter-section :deep(.el-form-item) {
    display: block;
    margin-right: 0;
  }
}
</style>