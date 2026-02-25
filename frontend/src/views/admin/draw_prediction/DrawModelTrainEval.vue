<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>模型训练与评估</span>
          <div class="header-actions">
            <el-button @click="goModelDeployment">去模型部署</el-button>
            <el-button type="primary" @click="handleStartTraining">开始训练</el-button>
          </div>
        </div>
      </template>
      <div class="card-content">
        <div class="toolbar">
          <el-input
            v-model="keyword"
            placeholder="请输入关键词搜索"
            style="width: 200px; margin-right: 10px;"
          />
          <el-button type="primary" @click="fetchTrainingJobs">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>

        <el-table :data="jobList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="job_name" label="任务名称" width="150" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="性能指标" width="200">
            <template #default="scope">
              <div v-if="scope.row.metrics">
                <p>准确率: {{ scope.row.metrics.accuracy ? (scope.row.metrics.accuracy * 100).toFixed(2) + '%' : '-' }}</p>
                <p>精确率: {{ scope.row.metrics.precision ? (scope.row.metrics.precision * 100).toFixed(2) + '%' : '-' }}</p>
                <p>召回率: {{ scope.row.metrics.recall ? (scope.row.metrics.recall * 100).toFixed(2) + '%' : '-' }}</p>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="started_at" label="开始时间" width="180" :formatter="formatDate" />
          <el-table-column prop="finished_at" label="完成时间" width="180" :formatter="formatDate" />
          <el-table-column label="操作" width="320">
            <template #default="scope">
              <el-button size="small" @click="viewLogs(scope.row.id)">查看日志</el-button>
              <el-button 
                v-if="['pending', 'training', 'running'].includes(String(scope.row.status || '').toLowerCase())" 
                size="small" 
                type="primary" 
                @click="updateJobStatus(scope.row.id, 'success')"
              >
                标记完成
              </el-button>
              <el-button 
                v-if="['pending', 'training', 'running'].includes(String(scope.row.status || '').toLowerCase())" 
                size="small" 
                type="danger" 
                @click="updateJobStatus(scope.row.id, 'failed')"
              >
                标记失败
              </el-button>
              <el-button
                v-if="['success', 'trained', 'evaluated'].includes(String(scope.row.status || '').toLowerCase())"
                size="small"
                type="success"
                @click="pushToDeployment(scope.row)"
              >
                推送部署
              </el-button>
              <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; text-align: right;"
        />
      </div>
    </el-card>

    <!-- 开始训练对话框 -->
    <el-dialog
      v-model="trainDialogVisible"
      title="开始训练"
      width="600px"
    >
      <el-form :model="trainForm" :rules="trainRules" ref="trainFormRef" label-width="120px">
        <el-form-item label="任务名称" prop="job_name">
          <el-input v-model="trainForm.job_name" placeholder="请输入训练任务名称" />
        </el-form-item>
        <el-form-item label="算法" prop="algorithm">
          <el-select v-model="trainForm.algorithm" placeholder="请选择算法" style="width: 100%;">
            <el-option label="逻辑回归 (logistic_regression)" value="logistic_regression" />
            <el-option label="随机森林 (random_forest)" value="random_forest" />
            <el-option label="XGBoost (xgboost)" value="xgboost" />
          </el-select>
        </el-form-item>
        <el-form-item label="特征ID列表">
          <el-input
            v-model="trainForm.feature_set_ids_text"
            placeholder="多个ID用逗号分隔，如: 1,2,3"
          />
        </el-form-item>
        <el-form-item label="超参数(JSON)">
          <el-input 
            v-model="trainForm.hyperparameters" 
            type="textarea" 
            :rows="5" 
            placeholder="请输入JSON格式超参数" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="trainDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="startTraining">开始训练</el-button>
      </template>
    </el-dialog>

    <!-- 训练日志对话框 -->
    <el-dialog
      v-model="logDialogVisible"
      title="训练日志"
      width="800px"
    >
      <div class="log-content">
        <pre v-for="(log, index) in logContent" :key="index">{{ log }}</pre>
      </div>
      <template #footer>
        <el-button @click="logDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="800px"
    >
      <div v-if="selectedJob">
        <h3>基本信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedJob.id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ selectedJob.job_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedJob.status)">
              {{ getStatusText(selectedJob.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(null, null, selectedJob.started_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ formatDate(null, null, selectedJob.finished_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px;">性能指标</h3>
        <el-table :data="[selectedJob.metrics]" border>
          <el-table-column prop="accuracy" label="准确率" :formatter="formatPercentage" />
          <el-table-column prop="precision" label="精确率" :formatter="formatPercentage" />
          <el-table-column prop="recall" label="召回率" :formatter="formatPercentage" />
          <el-table-column prop="f1_score" label="F1得分" :formatter="formatPercentage" />
          <el-table-column prop="auc" label="AUC" :formatter="formatPercentage" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getTrainingJobs,
  createTrainingJob,
  getTrainingJobLogs,
  updateTrainingJobStatus,
  bootstrapDrawPredictionMockData,
  getRetrainDraft
} from '@/api/drawPrediction'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const jobList = ref([])
const trainDialogVisible = ref(false)
const logDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const logContent = ref([])
const selectedJob = ref(null)
const trainFormRef = ref()

const trainForm = ref({
  job_name: '',
  algorithm: 'xgboost',
  feature_set_ids_text: '',
  hyperparameters: JSON.stringify({
    epochs: 100,
    batch_size: 32,
    learning_rate: 0.001,
    validation_split: 0.2
  }, null, 2)
})

const trainRules = {
  job_name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  algorithm: [
    { required: true, message: '请选择算法', trigger: 'change' }
  ]
}

const parseFeatureSetIds = (rawText) => {
  if (!rawText || !rawText.trim()) return []
  return rawText
    .split(',')
    .map((item) => Number(item.trim()))
    .filter((val) => Number.isInteger(val) && val > 0)
}


const extractTrainingErrorMessage = (err) => {
  const detail = err?.response?.data?.detail
  if (!detail) return ""
  if (typeof detail === "string") return detail

  const code = detail.code
  if (code === "missing_feature_ids") {
    const ids = Array.isArray(detail.missing_feature_ids) ? detail.missing_feature_ids.join(", ") : ""
    return ids ? `Feature IDs not found: ${ids}` : "Found non-existent feature IDs"
  }
  if (code === "inactive_feature_ids") {
    const ids = Array.isArray(detail.inactive_feature_ids) ? detail.inactive_feature_ids.join(", ") : ""
    return ids ? `Disabled feature IDs: ${ids}` : "Contains disabled features"
  }
  if (code === "no_active_features") {
    return detail.message || "No active features available. Please enable features first."
  }
  return detail.message || ""
}

const ensureMockDataReady = async () => {
  try {
    await bootstrapDrawPredictionMockData()
  } catch (err) {
    console.error('初始化模拟数据失败:', err)
  }
}

const applyRetrainDraftIfNeeded = async () => {
  const draftId = route.query?.draft_id
  if (!draftId) return
  try {
    const draft = await getRetrainDraft(String(draftId))
    const suggestion = draft?.suggestion || {}
    trainForm.value = {
      job_name: suggestion.job_name || `再训练_${new Date().toISOString().slice(0, 10)}`,
      algorithm: suggestion.algorithm || 'xgboost',
      feature_set_ids_text: Array.isArray(suggestion.feature_set_ids) ? suggestion.feature_set_ids.join(',') : '',
      hyperparameters: JSON.stringify(suggestion.hyperparameters || {
        epochs: 100,
        batch_size: 32,
        learning_rate: 0.001
      }, null, 2)
    }
    trainDialogVisible.value = true
    ElMessage.success('已加载再训练建议草稿，请确认后提交训练')
  } catch (err) {
    console.error('加载再训练草稿失败:', err)
    ElMessage.error('加载再训练草稿失败')
  }
}

const fetchTrainingJobs = async () => {
  try {
    const params = {
      keyword: keyword.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    const res = await getTrainingJobs(params)
    jobList.value = Array.isArray(res) ? res : (res?.data || [])
    total.value = Array.isArray(jobList.value) ? jobList.value.length : 0
  } catch (err) {
    console.error('获取训练任务失败:', err)
    ElMessage.error('获取训练任务失败')
  }
}

const handleStartTraining = () => {
  trainForm.value = {
    job_name: `平局预测训练_${new Date().toISOString().slice(0, 10)}`,
    algorithm: 'xgboost',
    feature_set_ids_text: '',
    hyperparameters: JSON.stringify({
      epochs: 100,
      batch_size: 32,
      learning_rate: 0.001,
      validation_split: 0.2
    }, null, 2)
  }
  trainDialogVisible.value = true
}

const startTraining = async () => {
  try {
    await trainFormRef.value.validate()

    let hyperparameters = {}
    try {
      hyperparameters = JSON.parse(trainForm.value.hyperparameters || '{}')
    } catch (e) {
      ElMessage.error('Hyperparameters JSON is invalid')
      return
    }

    const data = {
      job_name: trainForm.value.job_name,
      algorithm: trainForm.value.algorithm,
      feature_set_ids: parseFeatureSetIds(trainForm.value.feature_set_ids_text),
      hyperparameters
    }

    const resp = await createTrainingJob(data)
    if (resp?.queue_warning) {
      ElMessage.warning(resp.queue_warning)
    } else {
      ElMessage.success('Training job created')
    }
    trainDialogVisible.value = false
    fetchTrainingJobs()
  } catch (err) {
    console.error('Create training job failed:', err)
    const friendly = extractTrainingErrorMessage(err)
    ElMessage.error(friendly || 'Create training job failed')
  }
}

const viewLogs = async (jobId) => {
  try {
    const res = await getTrainingJobLogs(jobId)
    logContent.value = res.logs || ['暂无日志']
    logDialogVisible.value = true
  } catch (err) {
    console.error('获取日志失败:', err)
    ElMessage.error('获取日志失败')
  }
}

const updateJobStatus = async (jobId, status) => {
  try {
    await ElMessageBox.confirm(`确定要将任务状态更新为 ${getStatusText(status)} 吗?`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateTrainingJobStatus(jobId, { status })
    ElMessage.success('状态更新成功')
    fetchTrainingJobs()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('更新状态失败:', err)
      ElMessage.error('更新状态失败')
    }
  }
}

const viewDetails = (job) => {
  selectedJob.value = job
  detailDialogVisible.value = true
}

const pushToDeployment = (job) => {
  router.push({
    path: '/admin/draw-prediction/model-deployment',
    query: { training_job_id: String(job.id) }
  })
}

const goModelDeployment = () => {
  router.push('/admin/draw-prediction/model-deployment')
}

const resetFilter = () => {
  keyword.value = ''
  currentPage.value = 1
  fetchTrainingJobs()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchTrainingJobs()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchTrainingJobs()
}

const getStatusType = (status) => {
  const value = String(status || '').toLowerCase()
  switch (value) {
    case 'pending': return 'info'
    case 'running': return 'warning'
    case 'training': return 'warning'
    case 'success': return 'success'
    case 'trained': return 'primary'
    case 'evaluated': return 'success'
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'deployed': return 'danger'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  const value = String(status || '').toLowerCase()
  switch (value) {
    case 'pending': return '待处理'
    case 'running': return '训练中'
    case 'training': return '训练中'
    case 'success': return '训练完成'
    case 'trained': return '已训练'
    case 'evaluated': return '已评估'
    case 'active': return '已上线'
    case 'inactive': return '未上线'
    case 'deployed': return '已部署'
    case 'failed': return '失败'
    default: return status
  }
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return '-'
  const d = new Date(cellValue)
  return d.toLocaleString()
}

const formatPercentage = (row, column, cellValue) => {
  if (typeof cellValue === 'number') {
    return (cellValue * 100).toFixed(2) + '%'
  }
  return '-'
}

onMounted(async () => {
  await ensureMockDataReady()
  fetchTrainingJobs()
  applyRetrainDraftIfNeeded()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-content {
  max-height: 400px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
}

h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: bold;
}
</style>
