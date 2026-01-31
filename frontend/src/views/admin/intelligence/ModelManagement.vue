<template>
  <div class="intelligence-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>模型管理</h2>
      <p class="page-description">管理AI模型和机器学习算法配置</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="showCreateModelDialog = true">
        新建模型
      </el-button>
      <el-button type="success" :icon="VideoPlay" @click="trainModel">
        开始训练
      </el-button>
      <el-button type="warning" :icon="RefreshLeft" @click="refreshModels">
        刷新状态
      </el-button>
      <el-button type="info" :icon="Setting" @click="modelSettings">
        模型设置
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalModels }}</div>
              <div class="stats-label">总模型数</div>
            </div>
            <el-icon class="stats-icon"><Cpu /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.activeModels }}</div>
              <div class="stats-label">活跃模型</div>
            </div>
            <el-icon class="stats-icon"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.trainingJobs }}</div>
              <div class="stats-label">训练中任务</div>
            </div>
            <el-icon class="stats-icon"><Loading /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.avgAccuracy }}%</div>
              <div class="stats-label">平均准确率</div>
            </div>
            <el-icon class="stats-icon"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- Model Registry Tab -->
      <el-tab-pane label="模型仓库" name="models">
        <div class="tab-content">
          <!-- Model Categories -->
          <div class="category-filter">
            <el-button-group>
              <el-button 
                v-for="category in modelCategories" 
                :key="category.key"
                :type="selectedModelCategory === category.key ? 'primary' : ''"
                @click="selectedModelCategory = category.key"
              >
                {{ category.label }}
              </el-button>
            </el-button-group>
          </div>

          <!-- Models List -->
          <el-table 
            :data="filteredModels" 
            style="width: 100%"
            v-loading="loading"
          >
            <el-table-column prop="name" label="模型名称" min-width="150">
              <template #default="scope">
                <div class="model-name">
                  <el-link type="primary" @click="viewModelDetail(scope.row)">{{ scope.row.name }}</el-link>
                  <el-tag :type="getModelTypeColor(scope.row.type)" size="small">{{ scope.row.type }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusColor(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="accuracy" label="准确率" width="100">
              <template #default="scope">
                <el-progress :percentage="scope.row.accuracy" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column prop="trainingTime" label="训练时长" width="120" />
            <el-table-column prop="createdAt" label="创建时间" width="160" />
            <el-table-column prop="lastUsed" label="最后使用" width="160" />
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="editModel(scope.row)">编辑</el-button>
                <el-button size="small" type="success" @click="deployModel(scope.row)">部署</el-button>
                <el-button size="small" type="warning" @click="testModel(scope.row)">测试</el-button>
                <el-button size="small" type="danger" @click="deleteModel(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- Training Jobs Tab -->
      <el-tab-pane label="训练任务" name="training">
        <div class="tab-content">
          <!-- Training Statistics -->
          <el-row :gutter="16" class="training-stats">
            <el-col :span="6">
              <el-statistic title="排队中" :value="trainingStats.queued" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="运行中" :value="trainingStats.running" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已完成" :value="trainingStats.completed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败" :value="trainingStats.failed" />
            </el-col>
          </el-row>

          <!-- Training Jobs Table -->
          <el-table :data="trainingJobs" style="width: 100%; margin-top: 20px;">
            <el-table-column prop="name" label="任务名称" min-width="150" />
            <el-table-column prop="modelType" label="模型类型" width="120" />
            <el-table-column prop="dataset" label="数据集" width="120" />
            <el-table-column prop="progress" label="进度" width="200">
              <template #default="scope">
                <el-progress :percentage="scope.row.progress" :stroke-width="8" />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getTrainingStatusColor(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="startedAt" label="开始时间" width="160" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewTrainingLog(scope.row)">日志</el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  v-if="scope.row.status === 'running'"
                  @click="stopTraining(scope.row)"
                >
                  停止
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- Model Performance Tab -->
      <el-tab-pane label="性能监控" name="performance">
        <div class="tab-content">
          <!-- Performance Charts -->
          <el-row :gutter="20" class="performance-charts">
            <el-col :span="12">
              <el-card>
                <template #header>模型准确率趋势</template>
                <div ref="accuracyChart" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>预测响应时间</template>
                <div ref="latencyChart" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Performance Metrics -->
          <el-row :gutter="20" class="metrics-row">
            <el-col :span="8">
              <el-card class="metric-card">
                <template #header>实时指标</template>
                <div class="realtime-metrics">
                  <div class="metric-item">
                    <span class="label">QPS:</span>
                    <span class="value">{{ performanceMetrics.qps }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">延迟:</span>
                    <span class="value">{{ performanceMetrics.latency }}ms</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">内存:</span>
                    <span class="value">{{ performanceMetrics.memory }}MB</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="16">
              <el-card>
                <template #header>模型对比</template>
                <el-table :data="modelComparison" style="width: 100%">
                  <el-table-column prop="name" label="模型名称" width="150" />
                  <el-table-column prop="accuracy" label="准确率" width="100">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.accuracy" :stroke-width="6" />
                    </template>
                  </el-table-column>
                  <el-table-column prop="precision" label="精确率" width="100">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.precision" :stroke-width="6" />
                    </template>
                  </el-table-column>
                  <el-table-column prop="recall" label="召回率" width="100">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.recall" :stroke-width="6" />
                    </template>
                  </el-table-column>
                  <el-table-column prop="f1Score" label="F1分数" width="100">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.f1Score" :stroke-width="6" />
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Algorithm Library Tab -->
      <el-tab-pane label="算法库" name="algorithms">
        <div class="tab-content">
          <!-- Algorithm Categories -->
          <div class="algorithm-categories">
            <el-collapse v-model="activeAlgorithmCategory">
              <el-collapse-item 
                v-for="category in algorithmCategories" 
                :key="category.key"
                :title="category.label" 
                :name="category.key"
              >
                <div class="algorithm-grid">
                  <el-card 
                    v-for="algorithm in category.algorithms" 
                    :key="algorithm.id"
                    class="algorithm-card"
                    @click="useAlgorithm(algorithm)"
                  >
                    <template #header>
                      <div class="algorithm-header">
                        <span class="algorithm-name">{{ algorithm.name }}</span>
                        <el-tag size="small" :type="getDifficultyColor(algorithm.difficulty)">
                          {{ algorithm.difficulty }}
                        </el-tag>
                      </div>
                    </template>
                    <p class="algorithm-desc">{{ algorithm.description }}</p>
                    <div class="algorithm-meta">
                      <div class="meta-item">
                        <span class="label">类型:</span>
                        <el-tag size="small">{{ algorithm.type }}</el-tag>
                      </div>
                      <div class="meta-item">
                        <span class="label">使用次数:</span>
                        <span>{{ algorithm.usageCount }}</span>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Model Dialog -->
    <el-dialog 
      v-model="showCreateModelDialog" 
      :title="isEditing ? '编辑模型' : '新建模型'"
      width="800px"
    >
      <el-form :model="modelForm" :rules="modelFormRules" ref="modelFormRef" label-width="120px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型类型" prop="type">
          <el-select v-model="modelForm.type" placeholder="请选择模型类型">
            <el-option label="分类模型" value="classification" />
            <el-option label="回归模型" value="regression" />
            <el-option label="聚类模型" value="clustering" />
            <el-option label="深度学习" value="deep-learning" />
          </el-select>
        </el-form-item>
        <el-form-item label="算法" prop="algorithm">
          <el-select v-model="modelForm.algorithm" placeholder="请选择算法">
            <el-option v-for="alg in availableAlgorithms" :key="alg" :label="alg" :value="alg" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据集" prop="dataset">
          <el-select v-model="modelForm.dataset" placeholder="请选择训练数据集">
            <el-option label="历史比赛数据" value="historical-matches" />
            <el-option label="实时比赛数据" value="live-matches" />
            <el-option label="综合数据集" value="combined" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型配置" prop="config">
          <el-input 
            v-model="modelForm.config" 
            type="textarea" 
            :rows="6"
            placeholder="请输入JSON格式的模型配置参数"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="modelForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateModelDialog = false">取消</el-button>
          <el-button type="primary" @click="saveModel">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, VideoPlay, RefreshLeft, Setting, Cpu, CircleCheck, Loading, TrendCharts,
  Edit, Delete, View, Document 
} from '@element-plus/icons-vue'

// Reactive data
const activeTab = ref('models')
const activeAlgorithmCategory = ref(['classification'])
const loading = ref(false)
const showCreateModelDialog = ref(false)
const isEditing = ref(false)
const selectedModelCategory = ref('all')

// Stats data
const stats = reactive({
  totalModels: 15,
  activeModels: 8,
  trainingJobs: 3,
  avgAccuracy: 87.5
})

// Model categories
const modelCategories = ref([
  { key: 'all', label: '全部' },
  { key: 'classification', label: '分类模型' },
  { key: 'regression', label: '回归模型' },
  { key: 'clustering', label: '聚类模型' },
  { key: 'deep-learning', label: '深度学习' }
])

// Algorithm categories
const algorithmCategories = ref([
  {
    key: 'classification',
    label: '分类算法',
    algorithms: [
      { id: 1, name: '随机森林', type: 'ensemble', difficulty: '中等', description: '基于多棵决策树的集成学习算法', usageCount: 45 },
      { id: 2, name: '支持向量机', type: 'kernel', difficulty: '困难', description: '基于核函数的监督学习算法', usageCount: 23 },
      { id: 3, name: '神经网络', type: 'neural', difficulty: '困难', description: '多层感知器神经网络', usageCount: 67 }
    ]
  },
  {
    key: 'regression',
    label: '回归算法',
    algorithms: [
      { id: 4, name: '线性回归', type: 'linear', difficulty: '简单', description: '基础的线性预测模型', usageCount: 89 },
      { id: 5, name: '梯度提升', type: 'ensemble', difficulty: '中等', description: '迭代构建的决策树集成', usageCount: 34 }
    ]
  }
])

// Model form
const modelForm = reactive({
  name: '',
  type: '',
  algorithm: '',
  dataset: '',
  config: '',
  description: ''
})

const modelFormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  algorithm: [{ required: true, message: '请选择算法', trigger: 'change' }],
  dataset: [{ required: true, message: '请选择数据集', trigger: 'change' }]
}

// Available algorithms
const availableAlgorithms = ref(['随机森林', '支持向量机', '神经网络', '线性回归', '逻辑回归', '梯度提升'])

// Mock data
const models = ref([
  {
    id: 1,
    name: '比赛结果预测模型',
    type: 'classification',
    version: 'v2.1.0',
    status: 'active',
    accuracy: 89.5,
    trainingTime: '2h 34m',
    createdAt: '2024-01-15 10:30:00',
    lastUsed: '2024-01-23 09:15:00'
  },
  {
    id: 2,
    name: '赔率波动预测模型',
    type: 'regression',
    version: 'v1.8.3',
    status: 'active',
    accuracy: 85.2,
    trainingTime: '1h 56m',
    createdAt: '2024-01-10 14:20:00',
    lastUsed: '2024-01-23 08:45:00'
  },
  {
    id: 3,
    name: '用户行为聚类模型',
    type: 'clustering',
    version: 'v1.2.1',
    status: 'testing',
    accuracy: 78.9,
    trainingTime: '45m',
    createdAt: '2024-01-20 09:15:00',
    lastUsed: '2024-01-22 16:30:00'
  }
])

const trainingStats = reactive({
  queued: 2,
  running: 1,
  completed: 25,
  failed: 3
})

const trainingJobs = ref([
  {
    id: 1,
    name: '新赛季模型训练',
    modelType: 'classification',
    dataset: 'historical-matches',
    progress: 65,
    status: 'running',
    startedAt: '2024-01-23 08:00:00'
  },
  {
    id: 2,
    name: '赔率模型优化',
    modelType: 'regression',
    dataset: 'live-matches',
    progress: 100,
    status: 'completed',
    startedAt: '2024-01-22 20:00:00'
  }
])

const performanceMetrics = reactive({
  qps: 1250,
  latency: 45,
  memory: 2048
})

const modelComparison = ref([
  { name: '随机森林', accuracy: 89, precision: 87, recall: 91, f1Score: 89 },
  { name: '神经网络', accuracy: 85, precision: 83, recall: 88, f1Score: 85 },
  { name: 'SVM', accuracy: 82, precision: 80, recall: 85, f1Score: 82 }
])

// Computed
const filteredModels = computed(() => {
  if (selectedModelCategory.value === 'all') return models.value
  return models.value.filter(model => model.type === selectedModelCategory.value)
})

// Methods
const getModelTypeColor = (type) => {
  const colors = { classification: 'primary', regression: 'success', clustering: 'warning', 'deep-learning': 'danger' }
  return colors[type] || 'info'
}

const getStatusColor = (status) => {
  const colors = { active: 'success', inactive: 'danger', testing: 'warning', training: 'info' }
  return colors[status] || 'info'
}

const getTrainingStatusColor = (status) => {
  const colors = { running: 'primary', completed: 'success', failed: 'danger', queued: 'warning' }
  return colors[status] || 'info'
}

const getDifficultyColor = (difficulty) => {
  const colors = { '简单': 'success', '中等': 'warning', '困难': 'danger' }
  return colors[difficulty] || 'info'
}

const viewModelDetail = (model) => {
  ElMessage.info(`查看模型详情: ${model.name}`)
}

const editModel = (model) => {
  isEditing.value = true
  Object.assign(modelForm, model)
  showCreateModelDialog.value = true
}

const deployModel = (model) => {
  ElMessage.success(`部署模型: ${model.name}`)
}

const testModel = (model) => {
  ElMessage.info(`测试模型: ${model.name}`)
}

const deleteModel = (model) => {
  ElMessageBox.confirm(`确定要删除模型"${model.name}"吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  })
}

const trainModel = () => {
  ElMessage.info('打开模型训练向导')
}

const refreshModels = () => {
  ElMessage.success('刷新完成')
}

const modelSettings = () => {
  ElMessage.info('打开模型设置')
}

const viewTrainingLog = (job) => {
  ElMessage.info(`查看训练日志: ${job.name}`)
}

const stopTraining = (job) => {
  ElMessageBox.confirm(`确定要停止训练任务"${job.name}"吗？`, '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('训练任务已停止')
  })
}

const useAlgorithm = (algorithm) => {
  ElMessage.info(`使用算法: ${algorithm.name}`)
}

const saveModel = () => {
  ElMessage.success(isEditing.value ? '模型更新成功' : '模型创建成功')
  showCreateModelDialog.value = false
  resetModelForm()
}

const resetModelForm = () => {
  Object.assign(modelForm, {
    name: '',
    type: '',
    algorithm: '',
    dataset: '',
    config: '',
    description: ''
  })
  isEditing.value = false
}

onMounted(() => {
  console.log('Model Management mounted')
})
</script>

<style scoped>
.intelligence-management-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  position: relative;
  overflow: hidden;
}

.stats-content {
  position: relative;
  z-index: 2;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 48px;
  color: #409eff;
  opacity: 0.1;
  z-index: 1;
}

.management-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 20px;
}

.category-filter {
  margin-bottom: 20px;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.training-stats {
  margin-bottom: 20px;
}

.performance-charts {
  margin-bottom: 20px;
}

.metrics-row {
  margin-top: 20px;
}

.metric-card {
  height: 100%;
}

.realtime-metrics {
  padding: 16px 0;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-item .label {
  color: #909399;
  font-size: 14px;
}

.metric-item .value {
  font-weight: bold;
  color: #303133;
}

.algorithm-categories {
  margin-top: 16px;
}

.algorithm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.algorithm-card {
  cursor: pointer;
  transition: all 0.3s;
}

.algorithm-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.algorithm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.algorithm-name {
  font-weight: bold;
  color: #303133;
}

.algorithm-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.algorithm-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}
</style>