<template>
  <div class="recommendation-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>推荐系统管理</h3>
            <p class="subtitle">基于用户画像和AI技术提供个性化投注建议和策略推荐</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="createNewAlgorithm" icon="Plus">新增算法</el-button>
            <el-button @click="loadData" :loading="loading" icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" class="filters-row">
        <el-col :span="6">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索算法名称或描述" 
            clearable
            @keyup.enter="applyFilters"
            @clear="applyFilters"
          />
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="typeFilter" 
            placeholder="算法类型" 
            clearable
            @change="applyFilters"
          >
            <el-option label="协同过滤" value="collaborative" />
            <el-option label="内容推荐" value="content" />
            <el-option label="深度学习" value="deep_learning" />
            <el-option label="混合推荐" value="hybrid" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="statusFilter" 
            placeholder="状态" 
            clearable
            @change="applyFilters"
          >
            <el-option label="启用" value="enabled" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <el-table
        :data="paginatedAlgorithms"
        v-loading="loading"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="name" label="算法名称" width="200">
          <template #default="scope">
            <div class="algorithm-name">
              <span>{{ scope.row.name }}</span>
              <el-tag 
                v-if="scope.row.type" 
                :type="getTypeTagType(scope.row.type)" 
                size="small"
                style="margin-left: 8px;"
              >
                {{ getAlgorithmTypeName(scope.row.type) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'enabled' ? 'success' : 'info'">
              {{ scope.row.status === 'enabled' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="accuracy" label="准确率" width="120">
          <template #default="scope">
            {{ (scope.row.accuracy * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="coverage" label="覆盖率" width="120">
          <template #default="scope">
            {{ (scope.row.coverage * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="performanceScore" label="性能评分" width="120">
          <template #default="scope">
            <el-rate v-model="scope.row.performanceScore" :max="5" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdated" label="更新时间" width="160">
          <template #default="scope">
            {{ scope.row.lastUpdated }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewDetails(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editAlgorithm(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'enabled' ? 'warning' : 'success'"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 'enabled' ? '停用' : '启用' }}
            </el-button>
            <el-popconfirm
              title="确定要删除此算法吗？"
              @confirm="deleteAlgorithm(scope.row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredAlgorithms.length"
        />
      </div>
    </el-card>

    <!-- 算法详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="算法详情" width="60%" destroy-on-close>
      <div v-if="selectedAlgorithm" class="algorithm-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="算法名称">{{ selectedAlgorithm.name }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getTypeTagType(selectedAlgorithm.type)">
              {{ getAlgorithmTypeName(selectedAlgorithm.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedAlgorithm.status === 'enabled' ? 'success' : 'info'">
              {{ selectedAlgorithm.status === 'enabled' ? '启用' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="准确率">{{ (selectedAlgorithm.accuracy * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="覆盖率">{{ (selectedAlgorithm.coverage * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="性能评分">
            <el-rate v-model="selectedAlgorithm.performanceScore" :max="5" disabled />
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedAlgorithm.description }}</el-descriptions-item>
          <el-descriptions-item label="参数配置" :span="2">{{ selectedAlgorithm.configParams }}</el-descriptions-item>
          <el-descriptions-item label="训练数据量">{{ selectedAlgorithm.trainingDataSize }}条</el-descriptions-item>
          <el-descriptions-item label="特征数量">{{ selectedAlgorithm.featureCount }}个</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ selectedAlgorithm.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="训练时间">{{ selectedAlgorithm.trainingTime }}分钟</el-descriptions-item>
        </el-descriptions>
        
        <div class="performance-chart">
          <h4>性能趋势</h4>
          <div ref="performanceChartRef" style="height: 300px; margin-top: 20px;"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 新增/编辑算法对话框 -->
    <el-dialog 
      v-model="formDialogVisible" 
      :title="editingAlgorithm ? '编辑算法' : '新增算法'" 
      width="50%" 
      destroy-on-close
    >
      <el-form 
        :model="algorithmForm" 
        :rules="algorithmRules" 
        ref="algorithmFormRef" 
        label-width="120px"
        style="padding-right: 20px;"
      >
        <el-form-item label="算法名称" prop="name">
          <el-input v-model="algorithmForm.name" placeholder="请输入算法名称" />
        </el-form-item>
        <el-form-item label="算法类型" prop="type">
          <el-select v-model="algorithmForm.type" placeholder="请选择算法类型" style="width: 100%;">
            <el-option label="协同过滤" value="collaborative" />
            <el-option label="内容推荐" value="content" />
            <el-option label="深度学习" value="deep_learning" />
            <el-option label="混合推荐" value="hybrid" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="algorithmForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入算法描述" 
          />
        </el-form-item>
        <el-form-item label="参数配置" prop="configParams">
          <el-input 
            v-model="algorithmForm.configParams" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入算法参数配置(JSON格式)" 
          />
        </el-form-item>
        <el-form-item label="准确率阈值" prop="accuracyThreshold">
          <el-slider 
            v-model="algorithmForm.accuracyThreshold" 
            :min="0" 
            :max="1" 
            :step="0.01"
            :format-tooltip="val => `${(val * 100).toFixed(2)}%`"
          />
          <div class="slider-value">{{ (algorithmForm.accuracyThreshold * 100).toFixed(2) }}%</div>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="algorithmForm.status"
            :active-value="'enabled'"
            :inactive-value="'disabled'"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 算法数据
const algorithms = ref([
  { 
    id: 1, 
    name: '协同过滤推荐', 
    description: '基于用户行为相似性的推荐算法', 
    status: 'enabled', 
    type: 'collaborative', 
    accuracy: 0.852,
    coverage: 0.785,
    performanceScore: 4.2,
    configParams: '{"k_neighbors": 50, "similarity": "cosine", "min_rating": 1}',
    trainingDataSize: 125000,
    featureCount: 25,
    trainingTime: 45,
    lastUpdated: '2026-01-30 03:15:22'
  },
  { 
    id: 2, 
    name: '内容基础推荐', 
    description: '基于比赛内容特征的推荐算法', 
    status: 'enabled', 
    type: 'content', 
    accuracy: 0.798,
    coverage: 0.852,
    performanceScore: 3.8,
    configParams: '{"vectorizer": "tfidf", "ngram_range": [1, 2], "max_features": 10000}',
    trainingDataSize: 98000,
    featureCount: 32,
    trainingTime: 32,
    lastUpdated: '2026-01-30 02:45:10'
  },
  { 
    id: 3, 
    name: '深度神经网络推荐', 
    description: '基于深度学习的推荐算法', 
    status: 'disabled', 
    type: 'deep_learning', 
    accuracy: 0.915,
    coverage: 0.821,
    performanceScore: 4.6,
    configParams: '{"layers": [128, 64, 32], "dropout": 0.3, "epochs": 100}',
    trainingDataSize: 156000,
    featureCount: 45,
    trainingTime: 120,
    lastUpdated: '2026-01-30 01:30:05'
  },
  { 
    id: 4, 
    name: '混合推荐算法', 
    description: '结合多种推荐技术的混合算法', 
    status: 'enabled', 
    type: 'hybrid', 
    accuracy: 0.923,
    coverage: 0.895,
    performanceScore: 4.8,
    configParams: '{"weights": [0.4, 0.3, 0.3], "models": ["cf", "content", "dl"]}',
    trainingDataSize: 210000,
    featureCount: 52,
    trainingTime: 95,
    lastUpdated: '2026-01-30 00:45:30'
  }
])

// 对话框相关
const detailDialogVisible = ref(false)
const formDialogVisible = ref(false)
const selectedAlgorithm = ref(null)
const editingAlgorithm = ref(null)

// 表单数据
const algorithmForm = ref({
  name: '',
  type: '',
  description: '',
  configParams: '',
  accuracyThreshold: 0.8,
  status: 'enabled'
})

// 表单验证规则
const algorithmRules = {
  name: [
    { required: true, message: '请输入算法名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2到50个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择算法类型', trigger: 'change' }
  ]
}

// 性能图表引用
const performanceChartRef = ref(null)

// 计算属性：筛选后的算法
const filteredAlgorithms = computed(() => {
  return algorithms.value.filter(algorithm => {
    // 搜索关键词筛选
    const matchesSearch = !searchQuery.value || 
      algorithm.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      algorithm.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    // 类型筛选
    const matchesType = !typeFilter.value || algorithm.type === typeFilter.value
    
    // 状态筛选
    const matchesStatus = !statusFilter.value || algorithm.status === statusFilter.value
    
    return matchesSearch && matchesType && matchesStatus
  })
})

// 计算属性：当前页数据
const paginatedAlgorithms = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAlgorithms.value.slice(start, end)
})

// 方法：加载数据
const loadData = async () => {
  loading.value = true
  // 模拟API调用
  setTimeout(() => {
    loading.value = false
    ElMessage.success('数据刷新成功')
  }, 800)
}

// 方法：应用筛选
const applyFilters = () => {
  currentPage.value = 1
  ElMessage.success('筛选条件已应用')
}

// 方法：重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  ElMessage.info('筛选条件已重置')
}

// 方法：分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 方法：获取类型标签类型
const getTypeTagType = (type) => {
  switch (type) {
    case 'collaborative': return 'info'
    case 'content': return 'primary'
    case 'deep_learning': return 'warning'
    case 'hybrid': return 'success'
    default: return 'info'
  }
}

// 方法：获取算法类型名称
const getAlgorithmTypeName = (type) => {
  switch (type) {
    case 'collaborative': return '协同过滤'
    case 'content': return '内容推荐'
    case 'deep_learning': return '深度学习'
    case 'hybrid': return '混合推荐'
    default: return type
  }
}

// 方法：查看算法详情
const viewDetails = async (algorithm) => {
  selectedAlgorithm.value = algorithm
  detailDialogVisible.value = true
  
  // 等待DOM更新后再初始化图表
  await nextTick()
  initPerformanceChart()
}

// 方法：初始化性能图表
const initPerformanceChart = () => {
  if (!performanceChartRef.value) return
  
  const chart = echarts.init(performanceChartRef.value)
  chart.setOption({
    title: {
      text: '准确率趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      data: [82.1, 85.2, 79.8, 91.5, 92.3, 88.7, 90.1],
      type: 'line',
      smooth: true,
      areaStyle: {},
      itemStyle: {
        color: '#5470c6'
      }
    }]
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 方法：编辑算法
const editAlgorithm = (algorithm) => {
  editingAlgorithm.value = algorithm
  Object.assign(algorithmForm.value, algorithm)
  formDialogVisible.value = true
}

// 方法：创建新算法
const createNewAlgorithm = () => {
  editingAlgorithm.value = null
  Object.assign(algorithmForm.value, {
    name: '',
    type: '',
    description: '',
    configParams: '',
    accuracyThreshold: 0.8,
    status: 'enabled'
  })
  formDialogVisible.value = true
}

// 方法：提交表单
const submitForm = () => {
  // 此处应添加表单验证
  if (editingAlgorithm.value) {
    // 更新现有算法
    Object.assign(editingAlgorithm.value, algorithmForm.value)
    ElMessage.success('算法更新成功')
  } else {
    // 添加新算法
    const newAlgorithm = {
      id: algorithms.value.length + 1,
      ...algorithmForm.value,
      performanceScore: 3.0, // 默认评分
      lastUpdated: new Date().toISOString().slice(0, 19).replace('T', ' ')
    }
    algorithms.value.push(newAlgorithm)
    ElMessage.success('算法添加成功')
  }
  formDialogVisible.value = false
}

// 方法：切换算法状态
const toggleStatus = async (algorithm) => {
  try {
    await ElMessageBox.confirm(
      `确定要${algorithm.status === 'enabled' ? '停用' : '启用'}此算法吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    algorithm.status = algorithm.status === 'enabled' ? 'disabled' : 'enabled'
    ElMessage.success(`算法已${algorithm.status === 'enabled' ? '启用' : '停用'}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 方法：删除算法
const deleteAlgorithm = (id) => {
  const index = algorithms.value.findIndex(a => a.id === id)
  if (index !== -1) {
    algorithms.value.splice(index, 1)
    ElMessage.success('算法删除成功')
  }
}

// 页面加载时初始化
onMounted(() => {
  loadData()
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

.filters-row {
  margin-bottom: 20px;
  padding: 15px 0;
}

.algorithm-name {
  display: flex;
  align-items: center;
}

.slider-value {
  text-align: center;
  margin-top: 5px;
  color: #606266;
  font-size: 12px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.algorithm-detail {
  max-height: 500px;
  overflow-y: auto;
}

.performance-chart {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.performance-chart h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
}
</style>