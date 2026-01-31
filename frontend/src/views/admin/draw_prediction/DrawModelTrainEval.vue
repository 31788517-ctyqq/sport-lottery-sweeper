<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>模型训练与评估</span>
          <el-button type="primary" @click="handleStartTraining">开始训练</el-button>
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
          <el-table-column label="操作" width="250">
            <template #default="scope">
              <el-button size="small" @click="viewLogs(scope.row.id)">查看日志</el-button>
              <el-button 
                v-if="['pending', 'training'].includes(scope.row.status)" 
                size="small" 
                type="primary" 
                @click="updateJobStatus(scope.row.id, 'success')"
              >
                标记完成
              </el-button>
              <el-button 
                v-if="['pending', 'training'].includes(scope.row.status)" 
                size="small" 
                type="danger" 
                @click="updateJobStatus(scope.row.id, 'failed')"
              >
                标记失败
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
        <el-form-item label="训练参数">
          <el-input 
            v-model="trainForm.params" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入JSON格式的训练参数" 
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
import { getTrainingJobs, createTrainingJob, getTrainingJobLogs, updateTrainingJobStatus } from '@/api/drawPrediction'
import { ElMessage, ElMessageBox } from 'element-plus'

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
  params: '{}'
})

const trainRules = {
  job_name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ]
}

const fetchTrainingJobs = async () => {
  try {
    const params = {
      keyword: keyword.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    const res = await getTrainingJobs(params)
    jobList.value = res.data?.items || res.data || res || []
    total.value = res.data?.total || jobList.value.length
  } catch (err) {
    console.error('获取训练任务失败:', err)
    ElMessage.error('获取训练任务失败')
  }
}

const handleStartTraining = () => {
  trainForm.value = {
    job_name: `平局预测训练_${new Date().toISOString().slice(0, 10)}`,
    params: JSON.stringify({
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
    
    // 解析参数
    let paramsObj = {}
    try {
      paramsObj = JSON.parse(trainForm.value.params)
    } catch (e) {
      ElMessage.error('训练参数JSON格式错误')
      return
    }
    
    const data = {
      job_name: trainForm.value.job_name,
      params: paramsObj
    }
    
    await createTrainingJob(data)
    ElMessage.success('训练任务已创建')
    trainDialogVisible.value = false
    fetchTrainingJobs()
  } catch (err) {
    console.error('创建训练任务失败:', err)
    ElMessage.error('创建训练任务失败')
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
  switch (status) {
    case 'pending': return 'info'
    case 'training': return 'warning'
    case 'trained': return 'primary'
    case 'evaluated': return 'success'
    case 'deployed': return 'danger'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending': return '待处理'
    case 'training': return '训练中'
    case 'trained': return '已训练'
    case 'evaluated': return '已评估'
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

onMounted(() => {
  fetchTrainingJobs()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
