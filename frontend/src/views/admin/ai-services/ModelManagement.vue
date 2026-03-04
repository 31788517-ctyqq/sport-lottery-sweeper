<template>
  <div class="model-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>🧠 预测模型管理</h3>
            <p class="subtitle">管理预测模型（显示模型准确率、重新训练、部署和详情查看）</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addModel">添加模型</el-button>
            <el-button @click="refreshModels">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索模型名称" @keyup.enter="searchModels" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="typeFilter" placeholder="模型类型" style="width: 100%;" @change="filterModels">
            <el-option label="全部类型" value="" />
            <el-option label="比赛结果预测" value="match_result" />
            <el-option label="赔率分析" value="odds_analysis" />
            <el-option label="情感分析" value="sentiment_analysis" />
            <el-option label="趋势预测" value="trend_prediction" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态" style="width: 100%;" @change="filterModels">
            <el-option label="全部状态" value="" />
            <el-option label="已部署" value="deployed" />
            <el-option label="训练中" value="training" />
            <el-option label="已暂停" value="paused" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchModels">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 模型表格 -->
      <el-table :data="filteredModels" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="name" label="模型名称" width="200" />
        <el-table-column prop="version" label="版本" width="120" />
        <el-table-column prop="type" label="类型" width="150">
          <template #default="scope">
            <el-tag :type="getModelTypeTag(scope.row.type)">
              {{ scope.row.typeLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="accuracy" label="准确率" width="150">
          <template #default="scope">
            <el-progress
              :percentage="scope.row.accuracy" 
              :color="getAccuracyColor(scope.row.accuracy)"
              :format='() => `${scope.row.accuracy}%`'
            />
          </template>
        </el-table-column>
        <el-table-column prop="lastTrained" label="最后训练" width="180" />
        <el-table-column prop="trainingDataSize" label="训练数据量" width="150" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getModelStatusTag(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="retrainModel(scope.row)">重新训练</el-button>
            <el-button 
              size="small" 
              type="primary" 
              @click="deployModel(scope.row)"
              :disabled="scope.row.status === 'training'"
            >
              部署
            </el-button>
            <el-button size="small" type="info" @click="viewModelDetails(scope.row)">详情</el-button>
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
        :total="totalModels"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <!-- 模型详情对话框 -->
      <el-dialog v-model="detailDialogVisible" title="模型详情" width="700px">
        <div v-if="selectedModel" class="model-detail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="模型名称">{{ selectedModel.name }}</el-descriptions-item>
            <el-descriptions-item label="版本">{{ selectedModel.version }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ selectedModel.typeLabel }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getModelStatusTag(selectedModel.status)">
                {{ selectedModel.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="准确率">
              <el-progress
                :percentage="selectedModel.accuracy" 
                :color="getAccuracyColor(selectedModel.accuracy)"
                :format='() => `${selectedModel.accuracy}%`'
              />
            </el-descriptions-item>
            <el-descriptions-item label="训练数据量">{{ selectedModel.trainingDataSize }}</el-descriptions-item>
            <el-descriptions-item label="最后训练">{{ selectedModel.lastTrained }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ selectedModel.createdAt }}</el-descriptions-item>
            <el-descriptions-item label="算法类型">{{ selectedModel.algorithmType }}</el-descriptions-item>
            <el-descriptions-item label="特征工程">{{ selectedModel.featureEngineering }}</el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <h4>模型性能指标</h4>
          <el-table :data="selectedModel.metrics" style="width: 100%" size="small">
            <el-table-column prop="metric" label="指标" width="150" />
            <el-table-column prop="value" label="值" width="150" />
            <el-table-column prop="description" label="说明" />
          </el-table>
          
          <el-divider />
          
          <h4>模型描述</h4>
          <p>{{ selectedModel.description }}</p>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedModel = ref(null)

// 模型数据
const models = ref([
  {
    id: 1,
    name: '比赛结果预测模型',
    version: 'v1.2.3',
    type: 'match_result',
    typeLabel: '比赛结果预测',
    accuracy: 85.2,
    lastTrained: '2026-01-25 10:30:00',
    trainingDataSize: '12,500条',
    status: 'deployed',
    algorithmType: 'XGBoost + 深度学习融合',
    featureEngineering: '历史战绩、赔率变化、球员状态',
    createdAt: '2025-12-10 14:22:15',
    description: '基于历史比赛数据和实时赔率变化，预测比赛胜负平结果的高级机器学习模型',
    metrics: [
      { metric: '精确率', value: '84.7%', description: '预测正确的比例' },
      { metric: '召回率', value: '85.5%', description: '实际正例中被预测正确的比例' },
      { metric: 'F1分数', value: '85.1%', description: '精确率和召回率的调和平均' },
      { metric: 'AUC', value: '0.89', description: 'ROC曲线下面积' }
    ]
  },
  {
    id: 2,
    name: '赔率分析模型',
    version: 'v1.1.0',
    type: 'odds_analysis',
    typeLabel: '赔率分析',
    accuracy: 78.5,
    lastTrained: '2026-01-20 14:22:15',
    trainingDataSize: '9,800条',
    status: 'training',
    algorithmType: '深度神经网络',
    featureEngineering: '赔率波动、资金流向、市场情绪',
    createdAt: '2025-11-15 09:15:30',
    description: '分析赔率变化规律，识别异常赔率的深度学习模型',
    metrics: [
      { metric: '精确率', value: '77.2%', description: '预测正确的比例' },
      { metric: '召回率', value: '79.1%', description: '实际正例中被预测正确的比例' },
      { metric: 'F1分数', value: '78.1%', description: '精确率和召回率的调和平均' },
      { metric: 'AUC', value: '0.83', description: 'ROC曲线下面积' }
    ]
  },
  {
    id: 3,
    name: '情感分析模型',
    version: 'v2.0.1',
    type: 'sentiment_analysis',
    typeLabel: '情感分析',
    accuracy: 92.1,
    lastTrained: '2026-01-18 09:15:45',
    trainingDataSize: '15,600条',
    status: 'deployed',
    algorithmType: 'BERT + LSTM',
    featureEngineering: '文本情感、关键词提取、上下文分析',
    createdAt: '2025-10-05 16:45:20',
    description: '分析社交媒体和新闻文章对球队的情感倾向的NLP模型',
    metrics: [
      { metric: '精确率', value: '91.8%', description: '预测正确的比例' },
      { metric: '召回率', value: '92.3%', description: '实际正例中被预测正确的比例' },
      { metric: 'F1分数', value: '92.0%', description: '精确率和召回率的调和平均' },
      { metric: 'AUC', value: '0.94', description: 'ROC曲线下面积' }
    ]
  },
  {
    id: 4,
    name: '趋势预测模型',
    version: 'v0.8.5',
    type: 'trend_prediction',
    typeLabel: '趋势预测',
    accuracy: 72.3,
    lastTrained: '2026-01-28 11:30:20',
    trainingDataSize: '8,200条',
    status: 'paused',
    algorithmType: '时间序列分析 + ARIMA',
    featureEngineering: '历史趋势、周期性分析、外部因素',
    createdAt: '2025-12-20 13:10:45',
    description: '预测长期趋势和模式的时序分析模型',
    metrics: [
      { metric: '精确率', value: '71.5%', description: '预测正确的比例' },
      { metric: '召回率', value: '73.2%', description: '实际正例中被预测正确的比例' },
      { metric: 'F1分数', value: '72.3%', description: '精确率和召回率的调和平均' },
      { metric: 'MAE', value: '0.12', description: '平均绝对误差' }
    ]
  }
])

// 筛选和分页数据
const filteredModels = ref([...models.value])
const currentPage = ref(1)
const pageSize = ref(10)
const totalModels = ref(models.value.length)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')

// 方法
const getModelTypeTag = (type) => {
  const types = {
    match_result: 'primary',
    odds_analysis: 'success',
    sentiment_analysis: 'warning',
    trend_prediction: 'info'
  }
  return types[type] || 'info'
}

const getModelStatusTag = (status) => {
  const types = {
    deployed: 'success',
    training: 'warning',
    paused: 'info',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getAccuracyColor = (accuracy) => {
  if (accuracy >= 90) return '#67C23A' // 绿色
  if (accuracy >= 80) return '#E6A23C' // 黄色
  return '#F56C6C' // 红色
}

const addModel = () => {
  ElMessage.info('添加模型功能将在后续版本中实现')
}

const retrainModel = async (model) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新训练模型 "${model.name}" 吗？这可能需要一段时间。`,
      '确认重新训练',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 更新模型状态
    model.status = 'training'
    model.lastTrained = new Date().toISOString().slice(0, 19).replace('T', ' ')
    ElMessage.success(`模型 ${model.name} 开始重新训练`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新训练请求失败')
    }
  }
}

const deployModel = async (model) => {
  if (model.status === 'training') {
    ElMessage.warning('训练中的模型无法部署，请等待训练完成')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要部署模型 "${model.name}" 吗？`,
      '确认部署',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    
    model.status = 'deployed'
    ElMessage.success(`模型 ${model.name} 部署成功`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('部署失败')
    }
  }
}

const viewModelDetails = (model) => {
  selectedModel.value = model
  detailDialogVisible.value = true
}

const searchModels = () => {
  applyFilters()
}

const filterModels = () => {
  applyFilters()
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
  applyFilters()
}

const applyFilters = () => {
  let result = [...models.value]
  
  // 应用搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(model => 
      model.name.toLowerCase().includes(query) || 
      model.version.toLowerCase().includes(query) ||
      model.typeLabel.toLowerCase().includes(query)
    )
  }
  
  // 应用类型筛选
  if (typeFilter.value) {
    result = result.filter(model => model.type === typeFilter.value)
  }
  
  // 应用状态筛选
  if (statusFilter.value) {
    result = result.filter(model => model.status === statusFilter.value)
  }
  
  filteredModels.value = result
  totalModels.value = result.length
}

const handleSizeChange = (size) => {
  pageSize.value = size
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const refreshModels = () => {
  applyFilters()
  ElMessage.success('模型列表已刷新')
}

// 初始化数据
onMounted(() => {
  applyFilters()
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

.model-detail {
  padding: 20px 0;
}

:deep(.el-descriptions__header) {
  margin-bottom: 20px;
}
</style>