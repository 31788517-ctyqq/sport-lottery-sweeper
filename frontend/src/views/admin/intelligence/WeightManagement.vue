<template>
  <div class="intelligence-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>权重管理</h2>
      <p class="page-description">管理特征权重和评分算法配置</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="showCreateWeightDialog = true">
        新建权重方案
      </el-button>
      <el-button type="success" :icon="VideoPlay" @click="applyWeights">
        应用权重
      </el-button>
      <el-button type="warning" :icon="RefreshLeft" @click="autoOptimize">
        自动优化
      </el-button>
      <el-button type="info" :icon="ScaleToOriginal" @click="weightAnalysis">
        权重分析
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.weightSchemes }}</div>
              <div class="stats-label">权重方案</div>
            </div>
            <el-icon class="stats-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.activeScheme }}</div>
              <div class="stats-label">当前方案</div>
            </div>
            <el-icon class="stats-icon"><Star /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.optimizations }}</div>
              <div class="stats-label">优化次数</div>
            </div>
            <el-icon class="stats-icon"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.impactScore }}</div>
              <div class="stats-label">影响评分</div>
            </div>
            <el-icon class="stats-icon"><Aim /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- Weight Schemes Tab -->
      <el-tab-pane label="权重方案" name="schemes">
        <div class="tab-content">
          <!-- Scheme Categories -->
          <div class="scheme-categories">
            <el-radio-group v-model="selectedSchemeCategory" size="large">
              <el-radio-button 
                v-for="category in schemeCategories" 
                :key="category.key"
                :value="category.key"
              >
                {{ category.label }}
              </el-radio-button>
            </el-radio-group>
          </div>

          <!-- Weight Schemes List -->
          <div class="schemes-list">
            <el-card 
              v-for="scheme in filteredSchemes" 
              :key="scheme.id"
              class="scheme-card"
              :class="{ active: scheme.isActive }"
            >
              <template #header>
                <div class="scheme-header">
                  <div class="scheme-info">
                    <div class="scheme-name">
                      <h4>{{ scheme.name }}</h4>
                      <el-tag v-if="scheme.isActive" type="success" size="small">当前使用</el-tag>
                    </div>
                    <el-tag :type="getSchemeTypeColor(scheme.type)" size="small">{{ scheme.type }}</el-tag>
                  </div>
                  <div class="scheme-actions">
                    <el-button size="small" @click="viewSchemeDetail(scheme)">详情</el-button>
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="applyScheme(scheme)"
                      :disabled="scheme.isActive"
                    >
                      应用
                    </el-button>
                    <el-button size="small" @click="editScheme(scheme)">编辑</el-button>
                  </div>
                </div>
              </template>

              <div class="scheme-content">
                <p class="scheme-desc">{{ scheme.description }}</p>
                
                <!-- Weight Distribution Chart -->
                <div class="weight-distribution">
                  <h5>权重分布</h5>
                  <div class="weight-bars">
                    <div 
                      v-for="weight in scheme.weights" 
                      :key="weight.feature"
                      class="weight-bar"
                    >
                      <div class="feature-label">{{ weight.feature }}</div>
                      <el-progress 
                        :percentage="weight.value" 
                        :stroke-width="8"
                        :color="getWeightColor(weight.value)"
                      />
                      <div class="weight-value">{{ weight.value }}%</div>
                    </div>
                  </div>
                </div>

                <div class="scheme-meta">
                  <div class="meta-item">
                    <span class="label">创建时间:</span>
                    <span>{{ scheme.createdAt }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">更新时间:</span>
                    <span>{{ scheme.updatedAt }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">使用次数:</span>
                    <span>{{ scheme.usageCount }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">效果评分:</span>
                    <el-rate 
                      v-model="scheme.effectiveness" 
                      disabled 
                      show-score 
                      text-color="#ff9900"
                      score-template="{value}"
                    />
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- Feature Weights Tab -->
      <el-tab-pane label="特征权重" name="features">
        <div class="tab-content">
          <!-- Feature Categories -->
          <el-row :gutter="16" class="feature-categories">
            <el-col :span="6">
              <el-card class="feature-category-card" @click="selectFeatureCategory('basic')" :class="{ active: selectedFeatureCategory === 'basic' }">
                <div class="category-icon">📊</div>
                <div class="category-name">基础特征</div>
                <div class="category-count">{{ featureStats.basic }} 项</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="feature-category-card" @click="selectFeatureCategory('advanced')" :class="{ active: selectedFeatureCategory === 'advanced' }">
                <div class="category-icon">🎯</div>
                <div class="category-name">高级特征</div>
                <div class="category-count">{{ featureStats.advanced }} 项</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="feature-category-card" @click="selectFeatureCategory('derived')" :class="{ active: selectedFeatureCategory === 'derived' }">
                <div class="category-icon">🔄</div>
                <div class="category-name">衍生特征</div>
                <div class="category-count">{{ featureStats.derived }} 项</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="feature-category-card" @click="selectFeatureCategory('external')" :class="{ active: selectedFeatureCategory === 'external' }">
                <div class="category-icon">🌐</div>
                <div class="category-name">外部特征</div>
                <div class="category-count">{{ featureStats.external }} 项</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Features Weight Editor -->
          <el-card class="weight-editor-card">
            <template #header>
              <div class="editor-header">
                <span>特征权重编辑器 - {{ getFeatureCategoryLabel(selectedFeatureCategory) }}</span>
                <div class="editor-actions">
                  <el-button size="small" @click="resetWeights">重置</el-button>
                  <el-button size="small" type="primary" @click="saveWeights">保存</el-button>
                </div>
              </div>
            </template>

            <div class="weight-editor">
              <div class="feature-list">
                <div 
                  v-for="feature in filteredFeatures" 
                  :key="feature.id"
                  class="feature-item"
                >
                  <div class="feature-info">
                    <div class="feature-name">{{ feature.name }}</div>
                    <div class="feature-desc">{{ feature.description }}</div>
                  </div>
                  <div class="feature-controls">
                    <el-slider
                      v-model="feature.weight"
                      :min="0"
                      :max="100"
                      :step="1"
                      show-input
                      style="width: 200px; margin-right: 16px;"
                      @input="updateWeightPreview(feature)"
                    />
                    <el-tooltip :content="getWeightImpact(feature.weight)" placement="top">
                      <el-icon><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
              </div>

              <!-- Weight Preview -->
              <div class="weight-preview">
                <h5>权重预览</h5>
                <div ref="weightPreviewChart" style="height: 200px;"></div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Optimization History Tab -->
      <el-tab-pane label="优化历史" name="optimization">
        <div class="tab-content">
          <!-- Optimization Stats -->
          <el-row :gutter="20" class="optimization-stats">
            <el-col :span="8">
              <el-card class="opt-stat-card">
                <div class="opt-stat-value">{{ optimizationStats.autoOptimizations }}</div>
                <div class="opt-stat-label">自动优化次数</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="opt-stat-card">
                <div class="opt-stat-value">{{ optimizationStats.manualOptimizations }}</div>
                <div class="opt-stat-label">手动优化次数</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="opt-stat-card">
                <div class="opt-stat-value">{{ optimizationStats.improvementRate }}%</div>
                <div class="opt-stat-label">平均改善率</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Optimization Timeline -->
          <el-card class="timeline-card">
            <template #header>优化时间线</template>
            <el-timeline>
              <el-timeline-item
                v-for="record in optimizationHistory"
                :key="record.id"
                :timestamp="record.timestamp"
                :type="getOptimizationTypeColor(record.type)"
              >
                <div class="timeline-content">
                  <h4>{{ record.title }}</h4>
                  <p>{{ record.description }}</p>
                  <div class="optimization-details">
                    <el-tag size="small" :type="getStatusColor(record.result)">{{ record.result }}</el-tag>
                    <span class="improvement">改善: +{{ record.improvement }}%</span>
                    <el-button size="small" @click="viewOptimizationDetail(record)">详情</el-button>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- A/B Testing Tab -->
      <el-tab-pane label="A/B测试" name="abtest">
        <div class="tab-content">
          <!-- AB Test Overview -->
          <el-row :gutter="20" class="ab-test-overview">
            <el-col :span="12">
              <el-card>
                <template #header>A/B测试概况</template>
                <div class="ab-test-stats">
                  <div class="ab-stat-item">
                    <span class="label">活跃测试:</span>
                    <span class="value highlight">{{ abTestStats.activeTests }}</span>
                  </div>
                  <div class="ab-stat-item">
                    <span class="label">参与用户:</span>
                    <span class="value">{{ abTestStats.participants }}</span>
                  </div>
                  <div class="ab-stat-item">
                    <span class="label">转化率提升:</span>
                    <span class="value success">{{ abTestStats.conversionImprovement }}%</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>创建新测试</template>
                <el-form :model="abTestForm" label-width="80px">
                  <el-form-item label="测试名称">
                    <el-input v-model="abTestForm.name" placeholder="输入测试名称" />
                  </el-form-item>
                  <el-form-item label="对照组">
                    <el-select v-model="abTestForm.controlGroup" placeholder="选择对照方案">
                      <el-option v-for="scheme in weightSchemes" :key="scheme.id" :label="scheme.name" :value="scheme.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="实验组">
                    <el-select v-model="abTestForm.experimentGroup" placeholder="选择实验方案">
                      <el-option v-for="scheme in weightSchemes" :key="scheme.id" :label="scheme.name" :value="scheme.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="createABTest">创建测试</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-col>
          </el-row>

          <!-- Active Tests Table -->
          <el-card class="active-tests-card">
            <template #header>活跃测试列表</template>
            <el-table :data="activeABTests" style="width: 100%">
              <el-table-column prop="name" label="测试名称" min-width="150" />
              <el-table-column prop="controlScheme" label="对照组" width="120" />
              <el-table-column prop="experimentScheme" label="实验组" width="120" />
              <el-table-column prop="participants" label="参与用户" width="100" />
              <el-table-column prop="duration" label="持续时间" width="120" />
              <el-table-column prop="progress" label="进度" width="150">
                <template #default="scope">
                  <el-progress :percentage="scope.row.progress" :stroke-width="6" />
                </template>
              </el-table-column>
              <el-table-column prop="result" label="当前结果" width="100">
                <template #default="scope">
                  <el-tag :type="getABTestResultColor(scope.row.result)">{{ scope.row.result }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="viewABTest(scope.row)">查看</el-button>
                  <el-button size="small" type="danger" @click="stopABTest(scope.row)">停止</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Weight Scheme Dialog -->
    <el-dialog 
      v-model="showCreateWeightDialog" 
      :title="isEditing ? '编辑权重方案' : '新建权重方案'"
      width="900px"
    >
      <el-form :model="weightSchemeForm" :rules="weightSchemeFormRules" ref="weightSchemeFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="方案名称" prop="name">
              <el-input v-model="weightSchemeForm.name" placeholder="请输入方案名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="方案类型" prop="type">
              <el-select v-model="weightSchemeForm.type" placeholder="请选择方案类型">
                <el-option label="通用方案" value="general" />
                <el-option label="专项方案" value="specialized" />
                <el-option label="实验方案" value="experimental" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="方案描述" prop="description">
          <el-input 
            v-model="weightSchemeForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入方案描述"
          />
        </el-form-item>
        
        <el-form-item label="特征权重" prop="weights">
          <div class="weight-input-grid">
            <div 
              v-for="(weight, index) in weightSchemeForm.weights" 
              :key="index"
              class="weight-input-item"
            >
              <el-input 
                v-model="weight.feature" 
                placeholder="特征名称" 
                style="width: 200px; margin-right: 8px;"
              />
              <el-input-number 
                v-model="weight.value" 
                :min="0" 
                :max="100" 
                :step="1"
                placeholder="权重值"
                style="width: 120px; margin-right: 8px;"
              />
              <el-button 
                type="danger" 
                size="small" 
                icon="Delete" 
                circle
                @click="removeWeight(index)"
              />
            </div>
            <el-button type="primary" @click="addWeight" style="margin-top: 8px;">
              添加特征权重
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateWeightDialog = false">取消</el-button>
          <el-button type="primary" @click="saveWeightScheme">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, VideoPlay, RefreshLeft, ScaleToOriginal, Document, Star, TrendCharts, Aim,
  InfoFilled, Delete, Edit, View 
} from '@element-plus/icons-vue'

// Reactive data
const activeTab = ref('schemes')
const selectedSchemeCategory = ref('all')
const selectedFeatureCategory = ref('basic')
const loading = ref(false)
const showCreateWeightDialog = ref(false)
const isEditing = ref(false)

// Stats data
const stats = reactive({
  weightSchemes: 12,
  activeScheme: 1,
  optimizations: 45,
  impactScore: 87
})

// Scheme categories
const schemeCategories = ref([
  { key: 'all', label: '全部方案' },
  { key: 'general', label: '通用方案' },
  { key: 'specialized', label: '专项方案' },
  { key: 'experimental', label: '实验方案' }
])

// Feature categories
const featureStats = reactive({
  basic: 8,
  advanced: 12,
  derived: 6,
  external: 4
})

// Weight scheme form
const weightSchemeForm = reactive({
  name: '',
  type: '',
  description: '',
  weights: []
})

const weightSchemeFormRules = {
  name: [{ required: true, message: '请输入方案名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择方案类型', trigger: 'change' }]
}

// AB Test form
const abTestForm = reactive({
  name: '',
  controlGroup: '',
  experimentGroup: ''
})

// Mock data for weight schemes
const weightSchemes = ref([
  {
    id: 1,
    name: '默认均衡方案',
    type: 'general',
    description: '适用于大多数场景的基础权重配置',
    isActive: true,
    createdAt: '2024-01-01 10:00:00',
    updatedAt: '2024-01-20 15:30:00',
    usageCount: 1250,
    effectiveness: 4,
    weights: [
      { feature: '历史胜率', value: 25 },
      { feature: '主客场优势', value: 20 },
      { feature: '近期状态', value: 20 },
      { feature: '赔率变化', value: 15 },
      { feature: '球队实力', value: 12 },
      { feature: '其他因素', value: 8 }
    ]
  },
  {
    id: 2,
    name: '进攻型方案',
    type: 'specialized',
    description: '重点关注进攻数据的权重配置',
    isActive: false,
    createdAt: '2024-01-10 14:20:00',
    updatedAt: '2024-01-22 09:15:00',
    usageCount: 340,
    effectiveness: 3,
    weights: [
      { feature: '进球能力', value: 30 },
      { feature: '射门效率', value: 25 },
      { feature: '进攻配合', value: 20 },
      { feature: '历史胜率', value: 15 },
      { feature: '主场优势', value: 10 }
    ]
  }
])

// Mock data for features
const features = ref({
  basic: [
    { id: 1, name: '历史胜率', description: '球队历史比赛胜率统计', weight: 25 },
    { id: 2, name: '主客场优势', description: '主客场表现差异', weight: 20 },
    { id: 3, name: '近期状态', description: '最近几场比赛表现', weight: 20 },
    { id: 4, name: '球队实力', description: '综合球队实力评级', weight: 12 }
  ],
  advanced: [
    { id: 5, name: '进攻效率', description: '进攻数据统计', weight: 18 },
    { id: 6, name: '防守稳定性', description: '防守数据统计', weight: 15 },
    { id: 7, name: '关键球员', description: '核心球员状态', weight: 22 }
  ],
  derived: [
    { id: 8, name: '动量指标', description: '趋势分析指标', weight: 16 },
    { id: 9, name: '协同效应', description: '团队配合度', weight: 14 }
  ],
  external: [
    { id: 10, name: '天气影响', description: '天气条件影响', weight: 8 },
    { id: 11, name: '舆论热度', description: '媒体关注度', weight: 6 }
  ]
})

// Optimization history
const optimizationHistory = ref([
  {
    id: 1,
    title: '自动权重优化',
    description: '基于最新数据自动调整特征权重分配',
    timestamp: '2024-01-23 08:00:00',
    type: 'auto',
    result: 'success',
    improvement: 5.2
  },
  {
    id: 2,
    title: '手动权重调整',
    description: '根据专家意见调整进攻特征权重',
    timestamp: '2024-01-22 16:30:00',
    type: 'manual',
    result: 'success',
    improvement: 3.8
  }
])

// AB Test stats
const abTestStats = reactive({
  activeTests: 2,
  participants: 1250,
  conversionImprovement: 12.5
})

const activeABTests = ref([
  {
    id: 1,
    name: '进攻型vs均衡型测试',
    controlScheme: '默认均衡方案',
    experimentScheme: '进攻型方案',
    participants: 800,
    duration: '7天',
    progress: 65,
    result: 'pending'
  }
])

// Computed
const filteredSchemes = computed(() => {
  if (selectedSchemeCategory.value === 'all') return weightSchemes.value
  return weightSchemes.value.filter(scheme => scheme.type === selectedSchemeCategory.value)
})

const filteredFeatures = computed(() => {
  return features.value[selectedFeatureCategory.value] || []
})

const optimizationStats = reactive({
  autoOptimizations: 28,
  manualOptimizations: 17,
  improvementRate: 8.3
})

// Methods
const getSchemeTypeColor = (type) => {
  const colors = { general: 'primary', specialized: 'success', experimental: 'warning' }
  return colors[type] || 'info'
}

const getWeightColor = (value) => {
  if (value >= 25) return '#67c23a'
  if (value >= 15) return '#409eff'
  if (value >= 10) return '#e6a23c'
  return '#f56c6c'
}

const getFeatureCategoryLabel = (category) => {
  const labels = { basic: '基础特征', advanced: '高级特征', derived: '衍生特征', external: '外部特征' }
  return labels[category] || category
}

const getWeightImpact = (weight) => {
  if (weight >= 25) return '高影响力特征'
  if (weight >= 15) return '中等影响力特征'
  if (weight >= 10) return '一般影响力特征'
  return '低影响力特征'
}

const getOptimizationTypeColor = (type) => {
  return type === 'auto' ? 'primary' : 'success'
}

const getStatusColor = (status) => {
  const colors = { success: 'success', failure: 'danger', pending: 'warning' }
  return colors[status] || 'info'
}

const getABTestResultColor = (result) => {
  const colors = { success: 'success', failure: 'danger', pending: 'warning' }
  return colors[result] || 'info'
}

const selectFeatureCategory = (category) => {
  selectedFeatureCategory.value = category
}

const viewSchemeDetail = (scheme) => {
  ElMessage.info(`查看方案详情: ${scheme.name}`)
}

const applyScheme = (scheme) => {
  ElMessageBox.confirm(`确定要应用方案"${scheme.name}"吗？`, '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // Update active scheme
    weightSchemes.value.forEach(s => s.isActive = false)
    scheme.isActive = true
    ElMessage.success('方案应用成功')
  })
}

const editScheme = (scheme) => {
  isEditing.value = true
  Object.assign(weightSchemeForm, scheme)
  showCreateWeightDialog.value = true
}

const applyWeights = () => {
  ElMessage.info('应用当前权重配置')
}

const autoOptimize = () => {
  ElMessage.info('启动自动权重优化')
}

const weightAnalysis = () => {
  ElMessage.info('打开权重分析报告')
}

const addWeight = () => {
  weightSchemeForm.weights.push({ feature: '', value: 10 })
}

const removeWeight = (index) => {
  weightSchemeForm.weights.splice(index, 1)
}

const saveWeightScheme = () => {
  ElMessage.success(isEditing.value ? '权重方案更新成功' : '权重方案创建成功')
  showCreateWeightDialog.value = false
  resetWeightSchemeForm()
}

const resetWeightSchemeForm = () => {
  Object.assign(weightSchemeForm, {
    name: '',
    type: '',
    description: '',
    weights: []
  })
  isEditing.value = false
}

const resetWeights = () => {
  ElMessage.info('重置权重设置')
}

const saveWeights = () => {
  ElMessage.success('权重保存成功')
}

const updateWeightPreview = (feature) => {
  // Update chart preview
  console.log('Update weight preview:', feature)
}

const createABTest = () => {
  if (!abTestForm.name || !abTestForm.controlGroup || !abTestForm.experimentGroup) {
    ElMessage.warning('请填写完整的测试信息')
    return
  }
  ElMessage.success('A/B测试创建成功')
}

const viewABTest = (test) => {
  ElMessage.info(`查看A/B测试: ${test.name}`)
}

const stopABTest = (test) => {
  ElMessageBox.confirm(`确定要停止测试"${test.name}"吗？`, '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('测试已停止')
  })
}

const viewOptimizationDetail = (record) => {
  ElMessage.info(`查看优化详情: ${record.title}`)
}

onMounted(() => {
  console.log('Weight Management mounted')
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

.scheme-categories {
  margin-bottom: 20px;
}

.schemes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scheme-card {
  transition: all 0.3s;
}

.scheme-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.scheme-card.active {
  border: 2px solid #409eff;
}

.scheme-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.scheme-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scheme-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.scheme-name h4 {
  margin: 0;
  color: #303133;
}

.scheme-actions {
  display: flex;
  gap: 8px;
}

.scheme-content {
  margin-top: 16px;
}

.scheme-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.weight-distribution h5 {
  margin: 0 0 12px 0;
  color: #303133;
}

.weight-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weight-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-label {
  width: 100px;
  font-size: 12px;
  color: #606266;
}

.weight-value {
  width: 40px;
  text-align: right;
  font-size: 12px;
  font-weight: bold;
  color: #303133;
}

.scheme-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.meta-item .label {
  color: #909399;
}

.feature-categories {
  margin-bottom: 20px;
}

.feature-category-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-category-card.active {
  border: 2px solid #409eff;
}

.category-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.category-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.category-count {
  color: #909399;
  font-size: 12px;
}

.weight-editor-card {
  margin-top: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.weight-editor {
  display: flex;
  gap: 20px;
}

.feature-list {
  flex: 1;
}

.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-info {
  flex: 1;
}

.feature-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.feature-desc {
  color: #606266;
  font-size: 12px;
}

.feature-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weight-preview {
  width: 300px;
}

.weight-preview h5 {
  margin: 0 0 12px 0;
  color: #303133;
}

.weight-input-grid {
  max-height: 200px;
  overflow-y: auto;
}

.weight-input-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.optimization-stats {
  margin-bottom: 20px;
}

.opt-stat-card {
  text-align: center;
}

.opt-stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.opt-stat-label {
  color: #606266;
  font-size: 14px;
}

.timeline-card {
  margin-top: 16px;
}

.timeline-content h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.timeline-content p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.optimization-details {
  display: flex;
  align-items: center;
  gap: 12px;
}

.improvement {
  color: #67c23a;
  font-weight: bold;
}

.ab-test-overview {
  margin-bottom: 20px;
}

.ab-test-stats {
  padding: 16px 0;
}

.ab-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.ab-stat-item .label {
  color: #909399;
}

.ab-stat-item .value {
  font-weight: bold;
  color: #303133;
}

.ab-stat-item .value.highlight {
  color: #409eff;
  font-size: 18px;
}

.ab-stat-item .value.success {
  color: #67c23a;
}

.active-tests-card {
  margin-top: 20px;
}
</style>
