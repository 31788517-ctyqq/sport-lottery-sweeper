<template>
  <el-main>
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">比赛总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">即将开始</div>
          <div class="stat-value">{{ stats.pending }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">进行中</div>
          <div class="stat-value">{{ stats.running }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已结束</div>
          <div class="stat-value">{{ stats.finished }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索联赛/主队/客队" clearable style="width: 240px" />
        <el-button type="primary" @click="handleAdd">新增比赛</el-button>
        <el-button @click="loadData">刷新</el-button>
      </div>
    </el-card>

    <!-- 比赛表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredTableData" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="league" label="联赛" />
        <el-table-column prop="home_team" label="主队" />
        <el-table-column prop="away_team" label="客队" />
        <el-table-column prop="match_time" label="比赛时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'finished' ? 'info' : 'success'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="联赛" prop="league">
          <el-input v-model="form.league" placeholder="请输入联赛名称" />
        </el-form-item>
        <el-form-item label="主队" prop="home_team">
          <el-input v-model="form.home_team" placeholder="请输入主队名称" />
        </el-form-item>
        <el-form-item label="客队" prop="away_team">
          <el-input v-model="form.away_team" placeholder="请输入客队名称" />
        </el-form-item>
        <el-form-item label="比赛时间" prop="match_time">
          <el-date-picker v-model="form.match_time" type="datetime" placeholder="选择日期时间" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="running" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </el-main>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMatchList, createMatch, deleteMatch } from '@/api/match'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增比赛')
const formRef = ref(null)
const search = ref('')

const stats = reactive({
  total: 320,
  pending: 80,
  running: 12,
  finished: 228
})

const form = reactive({
  id: null, league: '', home_team: '', away_team: '', match_time: '', status: 'pending'
})

const rules = {
  league: [{ required: true, message: '请输入联赛名称', trigger: 'blur' }],
  home_team: [{ required: true, message: '请输入主队名称', trigger: 'blur' }],
  away_team: [{ required: true, message: '请输入客队名称', trigger: 'blur' }],
  match_time: [{ required: true, message: '请选择比赛时间', trigger: 'change' }]
}

const filteredTableData = computed(() =>
  tableData.value.filter(row =>
    row.league.includes(search.value) ||
    row.home_team.includes(search.value) ||
    row.away_team.includes(search.value)
  )
)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMatchList()
    tableData.value = res.data || []
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增比赛'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑比赛'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该比赛？', '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteMatch(id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  })
}

const submitForm = async () => {
  await formRef.value.validate()
  try {
    if (form.id) {
      ElMessage.info('编辑功能待实现')
    } else {
      await createMatch(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  Object.assign(form, { id: null, league: '', home_team: '', away_team: '', match_time: '', status: 'pending' })
  formRef.value?.resetFields()
}

onMounted(loadData)
</script>

<style scoped>
.stat-row { margin-bottom: 24px; }
.stat-card { border-radius: 12px; text-align: center; }
.stat-title { color: #64748b; font-size: 14px; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #1e293b; }
.toolbar-card { border-radius: 12px; margin-bottom: 24px; }
.toolbar { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.table-card { border-radius: 12px; }
.modern-table { border-radius: 12px; overflow: hidden; }
</style>