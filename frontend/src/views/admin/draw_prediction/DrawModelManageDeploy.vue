<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>模型版本管理</span>
          <div class="header-actions">
            <el-button @click="goTrainingPage">训练与评估</el-button>
            <el-button @click="goPredictionMonitor()">去预测监控</el-button>
            <el-button type="primary" @click="refreshAllData">刷新</el-button>
          </div>
        </div>
      </template>

      <div class="card-content">
        <el-alert
          title="闭环流程：在训练与评估页创建训练任务 -> 训练成功自动生成模型版本 -> 本页部署上线"
          type="info"
          :closable="false"
          show-icon
          class="sample-alert"
        />

        <div class="training-summary">
          <el-tag type="info">待处理 {{ trainingSummary.pending }}</el-tag>
          <el-tag type="warning">训练中 {{ trainingSummary.running }}</el-tag>
          <el-tag type="success">已完成 {{ trainingSummary.success }}</el-tag>
          <el-tag type="danger">失败 {{ trainingSummary.failed }}</el-tag>
        </div>

        <div class="toolbar">
          <el-input
            v-model="keyword"
            placeholder="请输入关键词搜索"
            style="width: 200px;"
          />
          <el-input
            v-model="trainingJobIdFilter"
            placeholder="按训练任务ID筛选"
            style="width: 180px;"
          />
          <el-button type="primary" @click="fetchModelVersions">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>

        <el-table :data="modelList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="version_tag" label="版本号" width="140" />
          <el-table-column prop="training_job_id" label="训练任务ID" width="120" />
          <el-table-column label="性能指标" width="220">
            <template #default="scope">
              <div v-if="scope.row.performance_metrics">
                <p>准确率: {{ toPercent(scope.row.performance_metrics.accuracy) }}</p>
                <p>精确率: {{ toPercent(scope.row.performance_metrics.precision) }}</p>
                <p>召回率: {{ toPercent(scope.row.performance_metrics.recall) }}</p>
              </div>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deployed_at" label="部署时间" width="180" :formatter="formatDate" />
          <el-table-column label="操作" width="300">
            <template #default="scope">
              <el-button
                v-if="!isModelDeployed(scope.row.status)"
                size="small"
                type="success"
                @click="handleDeploy(scope.row.id)"
              >
                部署
              </el-button>
              <el-button
                v-if="isModelDeployed(scope.row.status)"
                size="small"
                type="warning"
                @click="handleRollback(scope.row.id)"
              >
                回滚
              </el-button>
              <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
              <el-button size="small" type="primary" @click="goPredictionMonitor(scope.row.id)">监控</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="暂无模型版本，请先前往训练与评估页创建训练任务">
              <el-button type="success" @click="goTrainingPage">去训练评估</el-button>
            </el-empty>
          </template>
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

    <el-dialog
      v-model="detailDialogVisible"
      title="模型详情"
      width="800px"
    >
      <div v-if="selectedModel">
        <h3>基本信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedModel.id }}</el-descriptions-item>
          <el-descriptions-item label="版本号">{{ selectedModel.version_tag }}</el-descriptions-item>
          <el-descriptions-item label="训练任务ID">{{ selectedModel.training_job_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedModel.status)">
              {{ getStatusText(selectedModel.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="部署时间">
            {{ formatDate(null, null, selectedModel.deployed_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px;">性能指标</h3>
        <el-table :data="[selectedModel.performance_metrics || {}]" border>
          <el-table-column prop="accuracy" label="准确率" :formatter="formatPercentage" />
          <el-table-column prop="precision" label="精确率" :formatter="formatPercentage" />
          <el-table-column prop="recall" label="召回率" :formatter="formatPercentage" />
          <el-table-column prop="f1_score" label="F1得分" :formatter="formatPercentage" />
          <el-table-column prop="auc" label="AUC" :formatter="formatPercentage" />
        </el-table>

        <h3 style="margin-top: 20px;">来源追溯</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="来源训练任务">
            {{ modelTrace?.training_job?.job_name || '-' }} (ID: {{ modelTrace?.training_job?.id || selectedModel.training_job_id }})
          </el-descriptions-item>
          <el-descriptions-item label="特征集ID">
            {{ (modelTrace?.feature_set?.ids || []).join(', ') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="特征名称">
            {{ (modelTrace?.feature_set?.items || []).map((i) => i.name).join('、') || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getModelVersions,
  deployModelVersion,
  rollbackModelVersion,
  getTrainingJobsSummary,
  getModelTrace,
  bootstrapDrawPredictionMockData
} from '@/api/drawPrediction'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const trainingJobIdFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const modelList = ref([])
const detailDialogVisible = ref(false)
const selectedModel = ref(null)
const modelTrace = ref(null)

const trainingSummary = ref({
  pending: 0,
  running: 0,
  success: 0,
  failed: 0
})

const fetchModelVersions = async () => {
  try {
    const params = {
      keyword: keyword.value,
      page: currentPage.value,
      size: pageSize.value
    }
    const res = await getModelVersions(params)
    const rawList = res?.data || res || []
    modelList.value = Array.isArray(rawList) ? rawList : []

    if (trainingJobIdFilter.value) {
      const targetJobId = Number(trainingJobIdFilter.value)
      if (Number.isInteger(targetJobId) && targetJobId > 0) {
        modelList.value = modelList.value.filter((m) => Number(m.training_job_id) === targetJobId)
      }
    }

    total.value = res?.total || modelList.value.length
  } catch (err) {
    console.error('获取模型版本失败:', err)
    ElMessage.error('获取模型版本失败')
  }
}

const refreshTrainingSummary = async () => {
  try {
    const summary = await getTrainingJobsSummary()
    trainingSummary.value = {
      pending: Number(summary?.pending || 0),
      running: Number(summary?.running || 0),
      success: Number(summary?.success || 0),
      failed: Number(summary?.failed || 0)
    }
  } catch (err) {
    console.error('获取训练任务概览失败:', err)
  }
}

const refreshAllData = async () => {
  await fetchModelVersions()
  await refreshTrainingSummary()
}

const goTrainingPage = () => {
  router.push('/admin/draw-prediction/training-evaluation')
}

const goPredictionMonitor = (modelVersionId) => {
  if (modelVersionId) {
    router.push({
      path: '/admin/draw-prediction/prediction-monitoring',
      query: { model_version_id: String(modelVersionId) }
    })
    return
  }
  router.push('/admin/draw-prediction/prediction-monitoring')
}

const isModelDeployed = (status) => ['deployed', 'active'].includes(String(status || '').toLowerCase())

const handleDeploy = async (id) => {
  try {
    await ElMessageBox.confirm('确定要部署此模型版本吗？这将替换当前线上模型。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deployModelVersion(id)
    ElMessage.success('部署成功')
    await fetchModelVersions()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('部署模型失败:', err)
      ElMessage.error('部署模型失败')
    }
  }
}

const handleRollback = async (id) => {
  try {
    await ElMessageBox.confirm('确定要回滚此模型版本吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await rollbackModelVersion(id)
    ElMessage.success('回滚成功')
    await fetchModelVersions()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('回滚模型失败:', err)
      ElMessage.error('回滚模型失败')
    }
  }
}

const viewDetails = async (model) => {
  selectedModel.value = model
  detailDialogVisible.value = true
  modelTrace.value = null
  try {
    const trace = await getModelTrace(model.id)
    modelTrace.value = trace
  } catch (err) {
    console.error('获取模型追溯信息失败:', err)
  }
}

const resetFilter = () => {
  keyword.value = ''
  trainingJobIdFilter.value = ''
  currentPage.value = 1
  fetchModelVersions()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchModelVersions()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchModelVersions()
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
    case 'deployed': return 'danger'
    case 'active': return 'success'
    case 'inactive': return 'info'
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
    case 'deployed': return '已部署'
    case 'active': return '已上线'
    case 'inactive': return '未上线'
    case 'failed': return '失败'
    default: return status
  }
}

const formatDate = (_row, _column, cellValue) => {
  if (!cellValue) return '-'
  return new Date(cellValue).toLocaleString()
}

const toPercent = (v) => (typeof v === 'number' ? `${(v * 100).toFixed(2)}%` : '-')

const formatPercentage = (_row, _column, cellValue) => toPercent(cellValue)

onMounted(async () => {
  try {
    await bootstrapDrawPredictionMockData()
  } catch (err) {
    console.error('初始化模拟数据失败:', err)
  }

  if (route.query?.training_job_id) {
    trainingJobIdFilter.value = String(route.query.training_job_id)
  }

  await refreshAllData()
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

.sample-alert {
  margin-bottom: 12px;
}

.training-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: bold;
}
</style>
