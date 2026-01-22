<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">模型训练与评估</span>
      </template>
      <div class="card-content">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="输入任务名称搜索"
            clearable
            style="width: 300px; margin-right: 10px;"
            @clear="fetchJobs"
            @keyup.enter="fetchJobs"
          />
          <el-button type="primary" @click="openCreateDialog">创建训练任务</el-button>
        </div>

        <!-- 任务列表 -->
        <el-table :data="jobList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="job_name" label="任务名称" />
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="started_at" label="开始时间" :formatter="formatDate" />
          <el-table-column prop="finished_at" label="结束时间" :formatter="formatDate" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="viewLogs(scope.row)">日志</el-button>
              <el-button size="small" type="danger" @click="deleteJob(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 创建任务对话框 -->
        <el-dialog
          v-model="createDialogVisible"
          title="创建训练任务"
          width="600px"
        >
          <el-form :model="createForm" label-width="120px">
            <el-form-item label="任务名称">
              <el-input v-model="createForm.job_name" />
            </el-form-item>
            <el-form-item label="特征集">
              <el-select
                v-model="createForm.feature_set_ids"
                multiple
                placeholder="选择特征"
                style="width: 100%;"
              >
                <el-option
                  v-for="f in featureOptions"
                  :key="f.id"
                  :label="f.name"
                  :value="f.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="算法">
              <el-select v-model="createForm.algorithm" placeholder="选择算法" style="width: 100%;">
                <el-option label="XGBoost" value="xgboost" />
                <el-option label="LightGBM" value="lightgbm" />
                <el-option label="LogisticRegression" value="lr" />
              </el-select>
            </el-form-item>
            <el-form-item label="超参数">
              <el-input
                v-model="createForm.hyperparameters"
                type="textarea"
                :rows="4"
                placeholder='如：{"max_depth": 6, "learning_rate": 0.1}'
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="createDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitCreateJob">确定</el-button>
          </template>
        </el-dialog>

        <!-- 日志弹窗 -->
        <el-dialog
          v-model="logDialogVisible"
          title="训练日志"
          width="700px"
          top="5vh"
        >
          <el-scrollbar height="400px">
            <pre class="log-content">{{ logContent }}</pre>
          </el-scrollbar>
        </el-dialog>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchKeyword = ref('')
const jobList = ref([])
const featureOptions = ref([]) // 需要从后端获取特征列表供选择
const createDialogVisible = ref(false)
const logDialogVisible = ref(false)
const logContent = ref('')

const createForm = reactive({
  job_name: '',
  feature_set_ids: [],
  algorithm: '',
  hyperparameters: ''
})

const fetchJobs = async () => {
  try {
    const res = await axios.get('/api/v1/admin/draw-prediction/training-jobs', {
      params: { keyword: searchKeyword.value }
    })
    jobList.value = res.data
  } catch (err) {
    ElMessage.error('获取训练任务列表失败')
  }
}

const fetchFeaturesForSelect = async () => {
  // 假设有接口 /api/v1/admin/draw-prediction/features 返回 id、name
  try {
    const res = await axios.get('/api/v1/admin/draw-prediction/features')
    featureOptions.value = res.data
  } catch (err) {
    ElMessage.error('获取特征列表失败')
  }
}

const openCreateDialog = () => {
  createForm.job_name = ''
  createForm.feature_set_ids = []
  createForm.algorithm = ''
  createForm.hyperparameters = ''
  createDialogVisible.value = true
}

const submitCreateJob = async () => {
  try {
    await axios.post('/api/v1/admin/draw-prediction/training-jobs', createForm)
    ElMessage.success('训练任务已创建')
    createDialogVisible.value = false
    fetchJobs()
  } catch (err) {
    ElMessage.error('创建训练任务失败')
  }
}

const viewLogs = async (job) => {
  // 假设有接口 /api/v1/admin/draw-prediction/training-jobs/{id}/logs
  try {
    const res = await axios.get(`/api/v1/admin/draw-prediction/training-jobs/${job.id}/logs`)
    logContent.value = res.data.logs || ''
    logDialogVisible.value = true
  } catch (err) {
    ElMessage.error('获取日志失败')
  }
}

const deleteJob = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该训练任务吗？', '提示', { type: 'warning' })
    await axios.delete(`/api/v1/admin/draw-prediction/training-jobs/${id}`)
    ElMessage.success('删除成功')
    fetchJobs()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

const statusTagType = (status) => {
  return (
    { pending: 'info', running: 'warning', success: 'success', failed: 'danger' }[status] || 'info'
  )
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  const d = new Date(cellValue)
  return d.toLocaleString()
}

onMounted(() => {
  fetchJobs()
  fetchFeaturesForSelect()
  // 可选：定时轮询状态
  setInterval(fetchJobs, 10000)
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
}
.log-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 10px;
  margin: 0;
  font-family: monospace;
  font-size: 14px;
  white-space: pre-wrap;
}
</style>
