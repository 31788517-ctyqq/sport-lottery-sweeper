<template>
  <div class="lottery-schedule-container">
    <el-card class="schedule-card" :body-style="{ padding: '0' }">
      <div class="card-header">
        <h3>竞彩赛程管理</h3>
      </div>
      
      <!-- 搜索和控制区域 -->
      <div class="schedule-controls">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchForm.league_name"
              placeholder="请输入联赛名称"
              clearable
              class="search-input"
            />
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="searchForm.status"
              placeholder="请选择状态"
              clearable
              class="status-selector"
            >
              <el-option label="未开始" value="pending" />
              <el-option label="进行中" value="running" />
              <el-option label="已结束" value="finished" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-date-picker
              v-model="searchForm.date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="handleSearch" class="action-btn">
              查询
            </el-button>
            <el-button @click="resetSearch" class="action-btn">
              重置
            </el-button>
            <el-button type="success" @click="refreshData" class="action-btn">
              刷新
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 操作按钮区域 -->
      <div class="action-bar">
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          新增赛程
        </el-button>
      </div>
      
      <!-- 表格区域 -->
      <div class="table-wrapper">
        <el-table
          :data="tableData" 
          stripe 
          style="width: 100%" 
          v-loading="loading"
          height="calc(100vh - 320px)"
          :header-cell-style="{background: '#f5f7fa', color: '#606266'}"
          class="modern-table"
        >
          <el-table-column label="场次编号" width="100">
            <template #default="scope">
              {{ String(scope.row.id).padStart(3, '0') }}
            </template>
          </el-table-column>
          <el-table-column prop="league_name" label="联赛名称" min-width="140" show-overflow-tooltip />
          <el-table-column prop="home_team" label="主队" min-width="100" show-overflow-tooltip />
          <el-table-column prop="away_team" label="客队" min-width="100" show-overflow-tooltip />
          <el-table-column prop="match_time" label="比赛时间" width="170" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag
                :type="getStatusType(scope.row.status)"
                size="small"
              >
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="比分" width="100" />
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
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="pagination.page"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
        ></el-pagination>
      </div>
    </el-card>
    
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
          <el-input v-model="form.score" placeholder="请输入比分" />
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
// 临时注释掉 API 导入，使用模拟数据
// import { getLotterySchedules, createLotterySchedule, updateLotterySchedule, deleteLotterySchedule } from '@/api/lottery'

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

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

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

// 获取结果类型
const getResultType = (result) => {
  const resultMap = {
    '主胜': 'success',
    '客胜': 'danger',
    '平局': 'warning',
    '取消': 'info'
  }
  return resultMap[result] || 'info'
}

// 获取数据 - 使用模拟数据确保页面正常显示
const fetchData = async () => {
  loading.value = true
  
  // 模拟API请求延迟
  setTimeout(() => {
    tableData.value = [
      {
        id: 1,
        league_name: '英超联赛',
        home_team: '曼城',
        away_team: '阿森纳',
        match_time: '2026-01-25 20:00:00',
        status: 'pending',
        score: '',
        result: ''
      },
      {
        id: 2,
        league_name: '西甲联赛',
        home_team: '皇家马德里',
        away_team: '巴塞罗那',
        match_time: '2026-01-26 22:00:00',
        status: 'running',
        score: '2-1',
        result: '主胜'
      },
      {
        id: 3,
        league_name: '德甲联赛',
        home_team: '拜仁慕尼黑',
        away_team: '多特蒙德',
        match_time: '2026-01-24 21:30:00',
        status: 'finished',
        score: '3-0',
        result: '主胜'
      },
      {
        id: 4,
        league_name: '意甲联赛',
        home_team: 'AC米兰',
        away_team: '国际米兰',
        match_time: '2026-01-27 19:45:00',
        status: 'cancelled',
        score: '',
        result: '取消'
      },
      {
        id: 5,
        league_name: '法甲联赛',
        home_team: '巴黎圣日耳曼',
        away_team: '马赛',
        match_time: '2026-01-28 20:00:00',
        status: 'pending',
        score: '',
        result: ''
      }
    ]
    pagination.total = tableData.value.length
    loading.value = false
  }, 500)
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
  ElMessage.success('数据已刷新')
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
    
    // 模拟删除操作
    setTimeout(() => {
      const index = tableData.value.findIndex(item => item.id === row.id)
      if (index !== -1) {
        tableData.value.splice(index, 1)
        pagination.total = tableData.value.length
        ElMessage.success('删除成功')
      }
    }, 300)
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
    
    // 模拟API提交
    setTimeout(() => {
      if (form.id) {
        // 编辑模式：更新现有数据
        const index = tableData.value.findIndex(item => item.id === form.id)
        if (index !== -1) {
          tableData.value[index] = { ...form }
        }
        ElMessage.success('更新成功')
      } else {
        // 新增模式：添加新数据
        const newItem = {
          ...form,
          id: Date.now() // 简单的ID生成
        }
        tableData.value.unshift(newItem)
        pagination.total = tableData.value.length
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      submitLoading.value = false
    }, 500)
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
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
})
</script>

<style scoped>
.lottery-schedule-container {
  padding: 0;
  height: calc(100vh - 120px);
  width: 100%;
}

.schedule-card {
  height: 100%;
  border: none;
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  font-size: 16px;
  background-color: #fafafa;
}

.schedule-controls {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.search-input {
  width: 100%;
}

.status-selector {
  width: 100%;
}

.action-btn {
  margin-left: 8px;
}

.action-bar {
  padding: 16px 20px;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.table-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  height: calc(100% - 180px);
}

.modern-table {
  width: 100%;
}

.pagination-wrapper {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
  background-color: #fff;
  text-align: right;
}

.dialog-form .el-form-item {
  margin-bottom: 22px;
}

.text-muted {
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons .el-button {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .schedule-controls .el-col {
    margin-bottom: 12px;
  }
  
  .action-bar {
    padding: 12px 16px;
  }
  
  .table-wrapper {
    padding: 16px;
  }
}
</style>