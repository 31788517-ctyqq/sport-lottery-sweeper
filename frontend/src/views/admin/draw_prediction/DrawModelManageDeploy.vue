<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>模型版本管理</span>
          <el-button type="primary" @click="fetchModelVersions">刷新</el-button>
        </div>
      </template>
      <div class="card-content">
        <div class="toolbar">
          <el-input
            v-model="keyword"
            placeholder="请输入关键词搜索"
            style="width: 200px; margin-right: 10px;"
          />
          <el-button type="primary" @click="fetchModelVersions">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>

        <el-table :data="modelList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="version_tag" label="版本号" width="120" />
          <el-table-column prop="training_job_id" label="训练任务ID" width="120" />
          <el-table-column label="性能指标" width="200">
            <template #default="scope">
              <div v-if="scope.row.performance_metrics">
                <p>准确率: {{ scope.row.performance_metrics.accuracy ? (scope.row.performance_metrics.accuracy * 100).toFixed(2) + '%' : '-' }}</p>
                <p>精确率: {{ scope.row.performance_metrics.precision ? (scope.row.performance_metrics.precision * 100).toFixed(2) + '%' : '-' }}</p>
                <p>召回率: {{ scope.row.performance_metrics.recall ? (scope.row.performance_metrics.recall * 100).toFixed(2) + '%' : '-' }}</p>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deployed_at" label="部署时间" width="180" :formatter="formatDate" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button 
                v-if="scope.row.status !== 'deployed'" 
                size="small" 
                type="success" 
                @click="handleDeploy(scope.row.id)"
              >
                部署
              </el-button>
              <el-button 
                v-if="scope.row.status === 'deployed'" 
                size="small" 
                type="warning" 
                @click="handleRollback(scope.row.id)"
              >
                回滚
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

    <!-- 模型详情对话框 -->
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
        <el-table :data="[selectedModel.performance_metrics]" border>
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
import { getModelVersions, deployModelVersion, rollbackModelVersion } from '@/api/drawPrediction'
import { ElMessage, ElMessageBox } from 'element-plus'

const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const modelList = ref([])
const detailDialogVisible = ref(false)
const selectedModel = ref(null)

const fetchModelVersions = async () => {
  try {
    const params = {
      keyword: keyword.value,
      page: currentPage.value,
      size: pageSize.value
    }
    const res = await getModelVersions(params)
    // 假设API返回的数据结构为 { data: [...], total: 100 }
    modelList.value = res.data || res
    total.value = res.total || res.length
  } catch (err) {
    console.error('获取模型版本失败:', err)
    ElMessage.error('获取模型版本失败')
  }
}

const handleDeploy = async (id) => {
  try {
    await ElMessageBox.confirm('确定要部署此模型版本吗? 这将替换当前线上模型!', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deployModelVersion(id)
    ElMessage.success('部署成功')
    fetchModelVersions()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('部署模型失败:', err)
      ElMessage.error('部署模型失败')
    }
  }
}

const handleRollback = async (id) => {
  try {
    await ElMessageBox.confirm('确定要回滚此模型版本吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await rollbackModelVersion(id)
    ElMessage.success('回滚成功')
    fetchModelVersions()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('回滚模型失败:', err)
      ElMessage.error('回滚模型失败')
    }
  }
}

const viewDetails = (model) => {
  selectedModel.value = model
  detailDialogVisible.value = true
}

const resetFilter = () => {
  keyword.value = ''
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
  fetchModelVersions()
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

h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: bold;
}
</style>
