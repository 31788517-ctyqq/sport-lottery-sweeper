<template>
  <div class="hedging-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>对冲策略管理</h3>
            <p class="subtitle">智能监控和管理对冲策略，最大化收益并控制风险</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="createNewStrategy" icon="Plus">新增策略</el-button>
            <el-button @click="loadData" :loading="loading" icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" class="filters-row">
        <el-col :span="6">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索策略名称或描述" 
            clearable
            @keyup.enter="applyFilters"
            @clear="applyFilters"
          />
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="statusFilter" 
            placeholder="状态筛选" 
            clearable
            @change="applyFilters"
          >
            <el-option label="启用" value="enabled" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="typeFilter" 
            placeholder="类型筛选" 
            clearable
            @change="applyFilters"
          >
            <el-option label="静态对冲" value="static" />
            <el-option label="动态对冲" value="dynamic" />
            <el-option label="套利对冲" value="arbitrage" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select 
            v-model="riskLevelFilter" 
            placeholder="风险等级" 
            clearable
            @change="applyFilters"
          >
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <el-table
        :data="paginatedStrategies"
        v-loading="loading"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="策略名称" width="200">
          <template #default="scope">
            <div class="strategy-name">
              <span>{{ scope.row.name }}</span>
              <el-tag 
                v-if="scope.row.type" 
                :type="getTypeTagType(scope.row.type)" 
                size="small"
                style="margin-left: 8px;"
              >
                {{ getStrategyTypeName(scope.row.type) }}
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
        <el-table-column prop="riskLevel" label="风险等级" width="120">
          <template #default="scope">
            <el-tag :type="getRiskTagType(scope.row.riskLevel)">
              {{ getRiskLevelName(scope.row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="profitability" label="历史收益率" width="120">
          <template #default="scope">
            <span :class="scope.row.profitability > 0 ? 'positive-profit' : 'negative-profit'">
              {{ scope.row.profitability > 0 ? '+' : '' }}{{ (scope.row.profitability * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="executionCount" label="执行次数" width="100" />
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="scope">
            {{ (scope.row.successRate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="lastExecuted" label="最后执行" width="160">
          <template #default="scope">
            {{ scope.row.lastExecuted || '从未执行' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewDetails(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editStrategy(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'enabled' ? 'warning' : 'success'"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 'enabled' ? '停用' : '启用' }}
            </el-button>
            <el-popconfirm
              title="确定要删除此策略吗？"
              @confirm="deleteStrategy(scope.row.id)"
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
          :total="filteredStrategies.length"
        />
      </div>
    </el-card>

    <!-- 策略详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="策略详情" width="60%" destroy-on-close>
      <div v-if="selectedStrategy" class="strategy-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="策略名称">{{ selectedStrategy.name }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getTypeTagType(selectedStrategy.type)">
              {{ getStrategyTypeName(selectedStrategy.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedStrategy.status === 'enabled' ? 'success' : 'info'">
              {{ selectedStrategy.status === 'enabled' ? '启用' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskTagType(selectedStrategy.riskLevel)">
              {{ getRiskLevelName(selectedStrategy.riskLevel) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedStrategy.description }}</el-descriptions-item>
          <el-descriptions-item label="阈值设置">{{ selectedStrategy.thresholdSettings }}</el-descriptions-item>
          <el-descriptions-item label="执行条件">{{ selectedStrategy.executionConditions }}</el-descriptions-item>
          <el-descriptions-item label="历史收益率">
            <span :class="selectedStrategy.profitability > 0 ? 'positive-profit' : 'negative-profit'">
              {{ selectedStrategy.profitability > 0 ? '+' : '' }}{{ (selectedStrategy.profitability * 100).toFixed(2) }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="成功率">{{ (selectedStrategy.successRate * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="执行次数">{{ selectedStrategy.executionCount }}</el-descriptions-item>
          <el-descriptions-item label="最后执行">{{ selectedStrategy.lastExecuted || '从未执行' }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="performance-chart">
          <h4>近期表现</h4>
          <div ref="performanceChartRef" style="height: 300px; margin-top: 20px;"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 新增/编辑策略对话框 -->
    <el-dialog 
      v-model="formDialogVisible" 
      :title="editingStrategy ? '编辑策略' : '新增策略'" 
      width="50%" 
      destroy-on-close
    >
      <el-form 
        :model="strategyForm" 
        :rules="strategyRules" 
        ref="strategyFormRef" 
        label-width="120px"
        style="padding-right: 20px;"
      >
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型" prop="type">
          <el-select v-model="strategyForm.type" placeholder="请选择策略类型" style="width: 100%;">
            <el-option label="静态对冲" value="static" />
            <el-option label="动态对冲" value="dynamic" />
            <el-option label="套利对冲" value="arbitrage" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级" prop="riskLevel">
          <el-radio-group v-model="strategyForm.riskLevel">
            <el-radio label="low">低风险</el-radio>
            <el-radio label="medium">中风险</el-radio>
            <el-radio label="high">高风险</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="strategyForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入策略描述" 
          />
        </el-form-item>
        <el-form-item label="阈值设置" prop="thresholdSettings">
          <el-input 
            v-model="strategyForm.thresholdSettings" 
            placeholder="例如：最小利润率2%，最大投入5000元" 
          />
        </el-form-item>
        <el-form-item label="执行条件" prop="executionConditions">
          <el-input 
            v-model="strategyForm.executionConditions" 
            type="textarea" 
            :rows="3" 
            placeholder="例如：仅在工作日执行，避开重大赛事" 
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="strategyForm.status"
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
const statusFilter = ref('')
const typeFilter = ref('')
const riskLevelFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 策略数据
const strategies = ref([
  { 
    id: 1, 
    name: '基础对冲策略', 
    description: '基于赔率差异的对冲策略', 
    status: 'enabled', 
    type: 'static', 
    riskLevel: 'medium',
    profitability: 0.032,
    executionCount: 125,
    successRate: 0.85,
    lastExecuted: '2026-01-30 03:15:22',
    thresholdSettings: '最小利润率2%',
    executionConditions: '24小时运行'
  },
  { 
    id: 2, 
    name: '动态风险对冲', 
    description: '根据市场波动动态调整的对冲策略', 
    status: 'enabled', 
    type: 'dynamic', 
    riskLevel: 'high',
    profitability: -0.015,
    executionCount: 89,
    successRate: 0.62,
    lastExecuted: '2026-01-30 02:45:10',
    thresholdSettings: '最大投入5000元',
    executionConditions: '避开重大赛事'
  },
  { 
    id: 3, 
    name: '多市场套利', 
    description: '跨平台套利策略', 
    status: 'disabled', 
    type: 'arbitrage', 
    riskLevel: 'low',
    profitability: 0.058,
    executionCount: 42,
    successRate: 0.91,
    lastExecuted: '2026-01-30 01:30:05',
    thresholdSettings: '最小差价3%',
    executionConditions: '仅工作日执行'
  },
  { 
    id: 4, 
    name: '高频交易策略', 
    description: '快速捕捉市场机会的策略', 
    status: 'enabled', 
    type: 'dynamic', 
    riskLevel: 'high',
    profitability: 0.021,
    executionCount: 210,
    successRate: 0.78,
    lastExecuted: '2026-01-30 00:45:30',
    thresholdSettings: '最大单笔1000元',
    executionConditions: '每5分钟检查一次'
  },
  { 
    id: 5, 
    name: '保守对冲策略', 
    description: '低风险对冲策略，专注于资金安全', 
    status: 'enabled', 
    type: 'static', 
    riskLevel: 'low',
    profitability: 0.015,
    executionCount: 78,
    successRate: 0.95,
    lastExecuted: '2026-01-29 23:20:15',
    thresholdSettings: '最大投入1000元',
    executionConditions: '仅在赔率稳定时执行'
  }
])

// 对话框相关
const detailDialogVisible = ref(false)
const formDialogVisible = ref(false)
const selectedStrategy = ref(null)
const editingStrategy = ref(null)

// 表单数据
const strategyForm = ref({
  name: '',
  type: '',
  riskLevel: 'medium',
  description: '',
  thresholdSettings: '',
  executionConditions: '',
  status: 'enabled'
})

// 表单验证规则
const strategyRules = {
  name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2到50个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择策略类型', trigger: 'change' }
  ],
  riskLevel: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ]
}

// 性能图表引用
const performanceChartRef = ref(null)

// 计算属性：筛选后的策略
const filteredStrategies = computed(() => {
  return strategies.value.filter(strategy => {
    // 搜索关键词筛选
    const matchesSearch = !searchQuery.value || 
      strategy.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      strategy.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    // 状态筛选
    const matchesStatus = !statusFilter.value || strategy.status === statusFilter.value
    
    // 类型筛选
    const matchesType = !typeFilter.value || strategy.type === typeFilter.value
    
    // 风险等级筛选
    const matchesRiskLevel = !riskLevelFilter.value || strategy.riskLevel === riskLevelFilter.value
    
    return matchesSearch && matchesStatus && matchesType && matchesRiskLevel
  })
})

// 计算属性：当前页数据
const paginatedStrategies = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStrategies.value.slice(start, end)
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
  statusFilter.value = ''
  typeFilter.value = ''
  riskLevelFilter.value = ''
  currentPage.value = 1
  ElMessage.info('筛选条件已重置')
}

// 方法：处理多选
const handleSelectionChange = (selection) => {
  console.log('Selected strategies:', selection)
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
    case 'static': return 'info'
    case 'dynamic': return 'primary'
    case 'arbitrage': return 'warning'
    default: return 'info'
  }
}

// 方法：获取类型名称
const getStrategyTypeName = (type) => {
  switch (type) {
    case 'static': return '静态对冲'
    case 'dynamic': return '动态对冲'
    case 'arbitrage': return '套利对冲'
    default: return type
  }
}

// 方法：获取风险等级标签类型
const getRiskTagType = (level) => {
  switch (level) {
    case 'low': return 'success'
    case 'medium': return 'warning'
    case 'high': return 'danger'
    default: return 'info'
  }
}

// 方法：获取风险等级名称
const getRiskLevelName = (level) => {
  switch (level) {
    case 'low': return '低风险'
    case 'medium': return '中风险'
    case 'high': return '高风险'
    default: return level
  }
}

// 方法：查看策略详情
const viewDetails = async (strategy) => {
  selectedStrategy.value = strategy
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
      text: '收益率趋势',
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
      data: [2.1, 3.2, -1.5, 5.8, 2.1, 3.2, -1.5],
      type: 'line',
      smooth: true,
      areaStyle: {},
      itemStyle: {
        color: '#409EFF'
      }
    }]
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 方法：编辑策略
const editStrategy = (strategy) => {
  editingStrategy.value = strategy
  Object.assign(strategyForm.value, strategy)
  formDialogVisible.value = true
}

// 方法：创建新策略
const createNewStrategy = () => {
  editingStrategy.value = null
  Object.assign(strategyForm.value, {
    name: '',
    type: '',
    riskLevel: 'medium',
    description: '',
    thresholdSettings: '',
    executionConditions: '',
    status: 'enabled'
  })
  formDialogVisible.value = true
}

// 方法：提交表单
const submitForm = () => {
  // 此处应添加表单验证
  if (editingStrategy.value) {
    // 更新现有策略
    Object.assign(editingStrategy.value, strategyForm.value)
    ElMessage.success('策略更新成功')
  } else {
    // 添加新策略
    const newStrategy = {
      id: strategies.value.length + 1,
      ...strategyForm.value
    }
    strategies.value.push(newStrategy)
    ElMessage.success('策略添加成功')
  }
  formDialogVisible.value = false
}

// 方法：切换策略状态
const toggleStatus = async (strategy) => {
  try {
    await ElMessageBox.confirm(
      `确定要${strategy.status === 'enabled' ? '停用' : '启用'}此策略吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    strategy.status = strategy.status === 'enabled' ? 'disabled' : 'enabled'
    ElMessage.success(`策略已${strategy.status === 'enabled' ? '启用' : '停用'}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 方法：删除策略
const deleteStrategy = (id) => {
  const index = strategies.value.findIndex(s => s.id === id)
  if (index !== -1) {
    strategies.value.splice(index, 1)
    ElMessage.success('策略删除成功')
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

.strategy-name {
  display: flex;
  align-items: center;
}

.positive-profit {
  color: #67c23a;
  font-weight: bold;
}

.negative-profit {
  color: #f56c6c;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.strategy-detail {
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