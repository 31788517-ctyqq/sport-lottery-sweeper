<template>
  <div class="schedule-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>{{ title }}</h3>
            <p class="subtitle">{{ subtitle }}</p>
          </div>
          <div class="header-actions">
            <el-button @click="refreshData">刷新</el-button>
            <el-button type="primary" @click="importSchedule">导入赛程</el-button>
            <el-button @click="exportSchedule">导出</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :model="queryParams" inline class="search-form">
        <el-form-item label="联赛名称">
          <el-input v-model="queryParams.leagueName" placeholder="请输入联赛名称" clearable />
        </el-form-item>
        <el-form-item label="比赛日期">
          <el-date-picker
            v-model="queryParams.matchDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="scheduleList" v-loading="loading" style="width: 100%">
        <el-table-column prop="matchId" label="比赛ID" width="120" />
        <el-table-column prop="homeTeam" label="主队" width="120">
          <template #default="scope">
            <span class="team-name">{{ scope.row.homeTeam }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="awayTeam" label="客队" width="120">
          <template #default="scope">
            <span class="team-name">{{ scope.row.awayTeam }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="leagueName" label="联赛" width="120" />
        <el-table-column prop="matchDate" label="比赛日期" width="150" />
        <el-table-column prop="matchTime" label="比赛时间" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="round" label="轮次" width="80" />
        <el-table-column prop="group" label="分组" width="80" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editSchedule(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="viewDetails(scope.row)">详情</el-button>
            <el-button size="small" type="danger" @click="deleteSchedule(scope.row)">删除</el-button>
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
        :total="total"
        style="margin-top: 20px; justify-content: center;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px">
      <el-form :model="currentSchedule" :rules="scheduleRules" ref="scheduleFormRef" label-width="100px">
        <el-form-item label="主队" prop="homeTeam">
          <el-input v-model="currentSchedule.homeTeam" placeholder="请输入主队名称" />
        </el-form-item>
        <el-form-item label="客队" prop="awayTeam">
          <el-input v-model="currentSchedule.awayTeam" placeholder="请输入客队名称" />
        </el-form-item>
        <el-form-item label="联赛" prop="leagueName">
          <el-input v-model="currentSchedule.leagueName" placeholder="请输入联赛名称" />
        </el-form-item>
        <el-form-item label="比赛日期" prop="matchDate">
          <el-date-picker
            v-model="currentSchedule.matchDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="比赛时间" prop="matchTime">
          <el-time-picker
            v-model="currentSchedule.matchTime"
            placeholder="选择时间"
            format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="currentSchedule.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="未开始" value="未开始" />
            <el-option label="进行中" value="进行中" />
            <el-option label="已结束" value="已结束" />
            <el-option label="延期" value="延期" />
            <el-option label="取消" value="取消" />
          </el-select>
        </el-form-item>
        <el-form-item label="轮次">
          <el-input v-model="currentSchedule.round" placeholder="请输入轮次" />
        </el-form-item>
        <el-form-item label="分组">
          <el-input v-model="currentSchedule.group" placeholder="请输入分组" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// props接收类型参数
const props = defineProps({
  scheduleType: {
    type: String,
    default: 'jczq' // jczq: 竞彩足球, bd: 北单
  }
})

// 计算标题和副标题
const title = computed(() => {
  return props.scheduleType === 'jczq' ? '竞彩赛程管理' : '北单赛程管理'
})

const subtitle = computed(() => {
  return props.scheduleType === 'jczq' 
    ? '管理竞彩足球相关赛事安排' 
    : '管理北单足球相关赛事安排'
})

// 表格数据
const scheduleList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 查询参数
const queryParams = reactive({
  leagueName: '',
  matchDate: '',
})

// 当前编辑的赛程
const currentSchedule = reactive({
  matchId: '',
  homeTeam: '',
  awayTeam: '',
  leagueName: '',
  matchDate: '',
  matchTime: '',
  status: '未开始',
  round: '',
  group: ''
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const scheduleFormRef = ref()

// 表单验证规则
const scheduleRules = {
  homeTeam: [
    { required: true, message: '请输入主队名称', trigger: 'blur' }
  ],
  awayTeam: [
    { required: true, message: '请输入客队名称', trigger: 'blur' }
  ],
  leagueName: [
    { required: true, message: '请输入联赛名称', trigger: 'blur' }
  ],
  matchDate: [
    { required: true, message: '请选择比赛日期', trigger: 'change' }
  ],
  matchTime: [
    { required: true, message: '请选择比赛时间', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 获取赛程列表
const getScheduleList = () => {
  loading.value = true
  
  // 模拟数据获取
  setTimeout(() => {
    // 生成模拟数据
    scheduleList.value = Array.from({ length: 50 }, (_, idx) => ({
      matchId: `M${String(idx + 1).padStart(4, '0')}`,
      homeTeam: `主队${idx + 1}`,
      awayTeam: `客队${idx + 1}`,
      leagueName: `联赛${idx % 5 + 1}`,
      matchDate: `2026-${String(Math.floor(idx / 10) + 1).padStart(2, '0')}-${String((idx % 28) + 1).padStart(2, '0')}`,
      matchTime: `${String(Math.floor(idx / 2) % 24).padStart(2, '0')}:${String((idx * 3) % 60).padStart(2, '0')}`,
      status: ['未开始', '进行中', '已结束', '延期'][idx % 4],
      round: `第${(idx % 10) + 1}轮`,
      group: ['A组', 'B组', 'C组', 'D组'][idx % 4]
    }))
    
    total.value = 50
    loading.value = false
  }, 500)
}

// 查询
const handleQuery = () => {
  getScheduleList()
}

// 重置查询
const resetQuery = () => {
  Object.keys(queryParams).forEach(key => {
    queryParams[key] = ''
  })
  getScheduleList()
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  getScheduleList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  getScheduleList()
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case '未开始': return 'info'
    case '进行中': return 'warning'
    case '已结束': return 'success'
    case '延期': return 'danger'
    case '取消': return 'danger'
    default: return 'info'
  }
}

// 刷新数据
const refreshData = () => {
  getScheduleList()
  ElMessage.success('数据已刷新')
}

// 导入赛程
const importSchedule = () => {
  ElMessage.info('导入赛程功能')
}

// 导出赛程
const exportSchedule = () => {
  ElMessage.info('导出赛程功能')
}

// 编辑赛程
const editSchedule = (row) => {
  Object.assign(currentSchedule, { ...row })
  dialogTitle.value = '编辑赛程'
  dialogVisible.value = true
}

// 查看详情
const viewDetails = (row) => {
  ElMessage.info(`查看比赛 ${row.matchId} 的详情`)
}

// 删除赛程
const deleteSchedule = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除比赛 "${row.homeTeam} VS ${row.awayTeam}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 实际删除逻辑
    scheduleList.value = scheduleList.value.filter(item => item.matchId !== row.matchId)
    total.value = scheduleList.value.length
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 保存赛程
const confirmSave = () => {
  scheduleFormRef.value.validate((valid) => {
    if (valid) {
      // 这里应该是实际的保存逻辑
      if (currentSchedule.matchId) {
        // 更新现有记录
        const index = scheduleList.value.findIndex(item => item.matchId === currentSchedule.matchId)
        if (index !== -1) {
          scheduleList.value[index] = { ...currentSchedule }
        }
        ElMessage.success('更新成功')
      } else {
        // 添加新记录
        currentSchedule.matchId = `M${String(scheduleList.value.length + 1).padStart(4, '0')}`
        scheduleList.value.unshift({ ...currentSchedule })
        total.value++
        ElMessage.success('添加成功')
      }
      
      dialogVisible.value = false
      getScheduleList()
    }
  })
}

onMounted(() => {
  getScheduleList()
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

.team-name {
  font-weight: bold;
  color: #409eff;
}
</style>