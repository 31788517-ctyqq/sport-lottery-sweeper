<template>
  <div class="beidan-filter-panel">
    <!-- 多策略管理按钮 -->
    <div style="margin-bottom: 20px; text-align: right;">
      <el-button type="primary" @click="multiStrategyVisible = true">
        <i class="el-icon-setting"></i>
        多策略管理
      </el-button>
    </div>
    
    <FilterCardHeader 
      :total-results="totalResults" 
      :loading="loading"
      @fetch-real-data="fetchRealData"
      @show-p-level-rules="showPLevelRules"
    />
    
    <FilterSection
      :filter-form="filterForm"
      :strength-options="strengthOptions"
      :win-pan-options="winPanOptions"
      :stability-options="stabilityOptions"
      :available-leagues="availableLeagues"
      :date-time-options="dateTimeOptions"
      :loading="loading"
      :direction-warning="directionWarning"
      @apply-preset="handlePreset"
      @handle-save-strategy="handleSaveStrategy"
      @load-example-strategy="handleLoadExampleStrategy"
      @apply-advanced-filter="applyAdvancedFilter"
      @reset-filters="resetFilters"
    />
    
    <StrategySection
      :selected-strategy-name="selectedStrategyName"
      :strategy-options="strategyOptions"
      :strategy-detail-items="strategyDetailItems"
      @handle-select-strategy="handleSelectStrategy"
      @load-strategy-options="loadStrategyOptions"
    />
<StatsCard 
  v-if="strategySelected"
  :statistics="statistics"
  :filter-form="filterForm"
/>

<!-- 筛选结果 -->
<div v-if="strategySelected">
  <div v-if="!hasResults" style="text-align:center; color:#999; margin:40px 0;">
    没有符合场次
  </div>
  <ResultsSection
    v-else
    :paged-results="pagedResults"
    :loading="loading"
    :show-stats="showStats"
    :total-results="totalResults"
    :current-page="currentPage"
    :page-size="pageSize"
    @toggle-stats="toggleStats"
    @export-results="exportResults"
    @handle-sort-change="handleSortChange"
    @handle-size-change="handleSizeChange"
    @handle-current-change="handleCurrentChange"
  />
</div>
  </div>

<!-- 策略管理弹窗 -->
<el-dialog
  v-model="strategyManageVisible"
  title="管理筛选策略"
  width="600px"
  :before-close="closeStrategyManage"
>
  <el-table :data="strategyOptions.value.filter(name => !exampleStrategyNames.includes(name))" style="width: 100%">
    <el-table-column prop="name" label="策略名称" width="180" />
    <el-table-column label="条件摘要" width="260">
      <template #default="{ row }">
        <span>{{ getStrategySummary(row) }}</span>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="160">
      <template #default="{ row }">
        <el-button size="small" @click="openEditStrategy(row)">修改</el-button>
        <el-button size="small" type="danger" @click="deleteStrategy(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
  <template #footer>
    <span class="dialog-footer">
      <el-button @click="closeStrategyManage">关闭</el-button>
    </span>
  </template>
</el-dialog>

<!-- 修改策略弹窗 -->
<el-dialog
  v-model="editStrategyVisible"
  title="修改策略"
  width="500px"
  :before-close="closeEditStrategy"
>
  <div v-if="editingStrategy">
    <p>策略名称：{{ editingStrategy.name }}</p>
    <el-input v-model="editStrategyName" placeholder="输入新策略名称" style="margin-bottom:10px;" />
    <el-button type="primary" @click="confirmEditStrategy">保存修改</el-button>
    <el-button @click="closeEditStrategy">取消</el-button>
  </div>
</el-dialog>
    
    <!-- 多策略管理弹窗 -->
    <MultiStrategyManager 
      :visible="multiStrategyVisible" 
      @close="multiStrategyVisible = false"
    />
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { debounce } from 'lodash-es'
import { useRouter } from 'vue-router'
import { 
  ElMessage, 
  ElLoading, 
  ElMessageBox,
  ElDialog,
  ElTable,
  ElTableColumn,
  ElButton
} from 'element-plus'
// 策略详情缓存：key 为策略名，value 为 filters 条件
const strategiesMap = new Map([
  [
    '强势正路',
    {
      strength: [2, 3],
      winPan: [3, 4],
      stability: ['S', 'A']
    }
  ],
  [
    '冷门潜质',
    {
      strength: [-1, 0],
      winPan: [-3, -4],
      stability: ['D', 'E']
    }
  ],
  [
    '均衡博弈',
    {
      strength: [0],
      winPan: [0],
      stability: ['B', 'C']
    }
  ],
  [
    '当前策略',
    {
      strength: [],
      winPan: [],
      stability: []
    }
  ]
])

// 当前应用的策略名称
const CURRENT_STRATEGY = ref('')
import FilterCardHeader from './components/FilterCardHeader.vue'
import FilterSection from './components/FilterSection.vue'
import StrategySection from './components/StrategySection.vue'
import StatsCard from './components/StatsCard.vue'
import ResultsSection from './components/ResultsSection.vue'
import MultiStrategyManager from '@/components/admin/MultiStrategyManager.vue'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const totalResults = ref(0)
const pagedResults = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const showStats = ref(true)
const strategyApplied = ref(false)
const strategySelected = ref(false) // 是否选择了策略（控制统计和结果卡片显示）
const hasResults = ref(false) // 是否有筛选结果
const multiStrategyVisible = ref(false) // 多策略管理弹窗可见性

// 筛选表单
const filterForm = reactive({
  powerDiffs: [],
  winPanDiffs: [],
  stabilityTiers: [],
  leagues: [],
  dateTime: '',
  dateRange: [],
  sortBy: 'p_level',
  sortOrder: 'desc',
  includeDerating: true
})

// 选项数据 - 完整详细版本（恢复原始设计）
const strengthOptions = [
  { value: -3, label: '-3', range: '< -25', desc: '客队实力碾压' },
  { value: -2, label: '-2', range: '-25 ~ -17', desc: '客队明显占优' },
  { value: -1, label: '-1', range: '-16 ~ -9', desc: '客队略有优势' },
  { value: 0, label: '0', range: '-8 ~ +8', desc: '双方实力接近' },
  { value: 1, label: '+1', range: '+9 ~ +16', desc: '主队略有优势' },
  { value: 2, label: '+2', range: '+17 ~ +25', desc: '主队明显占优' },
  { value: 3, label: '+3', range: '> +25', desc: '主队实力碾压' }
];

const winPanOptions = [
  { value: 4, label: '+4', range: 'S', desc: '主极致火热' },
  { value: 3, label: '+3', range: 'S', desc: '主极致火热' },
  { value: 2, label: '+2', range: 'A', desc: '主获利走强' },
  { value: 1, label: '+1', range: 'A', desc: '主获利走强' },
  { value: 0, label: '0', range: 'B', desc: '数据均衡' },
  { value: -1, label: '-1', range: 'C', desc: '客获利走强' },
  { value: -2, label: '-2', range: 'C', desc: '客获利走强' },
  { value: -3, label: '-3', range: 'D', desc: '客极致火热' },
  { value: -4, label: '-4', range: 'D', desc: '客极致火热' }
];

const stabilityOptions = [
  { value: 'S', label: 'S', range: 'P1', desc: '正路稳胆' },
  { value: 'A', label: 'A', range: 'P2', desc: '正路首选' },
  { value: 'B', label: 'B', range: 'P3', desc: '正路保障' },
  { value: 'B-', label: 'B-', range: 'P4', desc: '正路分歧' },
  { value: 'C', label: 'C', range: 'P5', desc: '正路存疑' },
  { value: 'D', label: 'D', range: 'P6', desc: '正路脆弱' },
  { value: 'E', label: 'E', range: 'P7', desc: '正路缺失' }
];

const availableLeagues = ref(['英超', '西甲', '德甲', '意甲', '法甲', '中超'])
const dateTimeOptions = ref(['今日', '近3日', '近7日', '本月'])
const directionWarning = ref(false)

// 策略相关
const selectedStrategyName = ref('')
const strategyOptions = ref([])
const strategyDetailItems = ref([])

// 统计数据
const statistics = ref({})

// 示例策略
const exampleStrategies = {
  strong: {
    powerDiffs: ['large'],
    winPanDiffs: ['stable'],
    stabilityTiers: ['high'],
    sortBy: 'p_level',
    sortOrder: 'desc'
  },
  upset: {
    powerDiffs: ['small'],
    winPanDiffs: ['risky'],
    stabilityTiers: ['low'],
    sortBy: 'delta_wp',
    sortOrder: 'asc'
  },
  balance: {
    powerDiffs: ['medium'],
    winPanDiffs: ['unstable'],
    stabilityTiers: ['medium'],
    sortBy: 'power_diff',
    sortOrder: 'desc'
  }
}

// 示例策略名称（仅用于加载条件预览，不自动应用筛选）
const exampleStrategyNames = ['强势正路', '冷门潜质', '均衡博弈']

// 生命周期
onMounted(async () => {
  loadStrategyOptions()
  await refreshDateTimeOptions() // 初始加载最新3期
})

// 将 powerDiffs 映射到 strength 值
function mapPowerDiffsToStrength(powerDiffs) {
  const map = {
    large: [2, 3],
    medium: [1, 2],
    small: [-1, 0],
    tiny: [-2, -1]
  }
  const result = []
  for (const key of powerDiffs) {
    if (map[key]) result.push(...map[key])
  }
  return [...new Set(result)]
}

// 将 winPanDiffs 映射到 winPan 值
function mapWinPanDiffsToWinPan(winPanDiffs) {
  const map = {
    stable: [3, 4],
    unstable: [1, 2, -1, -2],
    risky: [-3, -4]
  }
  const result = []
  for (const key of winPanDiffs) {
    if (map[key]) result.push(...map[key])
  }
  return [...new Set(result)]
}

// 将 strength 值映射到 powerDiffs
function mapStrengthToPowerDiffs(strengthArr) {
  const map = {
    2: 'large',
    1: 'medium',
    0: 'small',
    '-1': 'small',
    '-2': 'tiny'
  }
  const result = []
  for (const val of strengthArr) {
    const key = String(val)
    if (map[key] && !result.includes(map[key])) {
      result.push(map[key])
    }
  }
  return result
}

// 将 winPan 值映射到 winPanDiffs
function mapWinPanToWinPanDiffs(winPanArr) {
  const map = {
    3: 'stable',
    4: 'stable',
    2: 'unstable',
    1: 'unstable',
    '-1': 'unstable',
    '-2': 'unstable',
    '-3': 'risky',
    '-4': 'risky'
  }
  const result = []
  for (const val of winPanArr) {
    const key = String(val)
    if (map[key] && !result.includes(map[key])) {
      result.push(map[key])
    }
  }
  return result
}

// 方法
const fetchRealData = async () => {
  loading.value = true
  try {
    // 模拟API调用：获取最新比赛数量
    const mockApiResponse = {
      count: 38, // 从数据库最新date_time获取的比赛场次数
      latestDate: '26024' // 最新date_time字段值
    }
    totalResults.value = mockApiResponse.count
    pagedResults.value = [] // 实时数据可能不分页，先清空
    // 注意：这里不设置 strategyApplied 或 strategySelected，避免显示策略统计卡片
    await refreshDateTimeOptions()
    ElMessage.success(`实时匹配 ${mockApiResponse.count} 场`)
  } catch (error) {
    ElMessage.error('实时数据获取失败')
  } finally {
    loading.value = false
  }
}

const showPLevelRules = () => {
  ElMessage.info('显示P级规则')
}

const handlePreset = (type) => {
  console.log('应用预设:', type)
}

const handleSaveStrategy = async (command) => {
  if (command === 'save') {
    // 保存当前策略
    try {
      const { value: strategyName } = await ElMessageBox.prompt(
        '请输入策略名称',
        '保存当前策略',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^.{1,20}$/,
          inputErrorMessage: '策略名称长度应在1-20个字符之间'
        }
      )
      
      if (strategyName) {
        // 这里应该调用API保存策略
        strategyOptions.value.push(strategyName)
        ElMessage.success('策略保存成功')
      }
    } catch {
      // 用户取消
    }
  } else if (command === 'manage') {
    openStrategyManage()
  }
}

const handleLoadExampleStrategy = (type) => {
  const strategy = exampleStrategies[type]
  if (strategy) {
    // 只填充条件，不立即应用筛选
    Object.assign(filterForm, strategy)
    ElMessage.info(`已加载${type === 'strong' ? '强势正路' : type === 'upset' ? '冷门潜质' : '均衡博弈'}示例策略，请在筛选卡片中查看条件，并手动点击“应用筛选”生成当前策略`)
  }
}

const applyAdvancedFilter = async () => {
  loading.value = true
  try {
    // 走筛选API而不是全量数据API
    await new Promise(resolve => setTimeout(resolve, 1500))
    totalResults.value = 45
    pagedResults.value = Array.from({ length: Math.min(pageSize.value, 45) }, (_, i) => ({
      id: i + 1,
      homeTeam: `筛选主队${i + 1}`,
      awayTeam: `筛选客队${i + 1}`,
      score: '1:0',
      pLevel: Math.floor(Math.random() * 5) + 1
    }))

    // ===== 生成"当前策略"临时策略（不自动筛选） =====
    const tempStrategyName = "当前策略"
    // 将 filterForm 的筛选条件映射到 strategiesMap 的结构
    const currentFilters = {
      strength: mapPowerDiffsToStrength(filterForm.powerDiffs),
      winPan: mapWinPanDiffsToWinPan(filterForm.winPanDiffs),
      stability: filterForm.stabilityTiers || []
    }

    // 更新strategiesMap，添加或更新临时策略
    strategiesMap.set(tempStrategyName, currentFilters)

    // 如果策略选项中没有"当前策略"，则添加它
    if (!strategyOptions.value.includes(tempStrategyName)) {
      strategyOptions.value = [tempStrategyName, ...strategyOptions.value]
    }

    // 设置当前策略但不触发筛选
    selectedStrategyName.value = tempStrategyName
    CURRENT_STRATEGY.value = tempStrategyName

    strategyApplied.value = true
    showStats.value = true
    ElMessage.success(`已生成当前策略，请在策略筛选中选择它以应用结果`)
    // ===== 生成结束 =====

  } catch (error) {
    ElMessage.error('筛选失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  Object.assign(filterForm, {
    powerDiffs: [],
    winPanDiffs: [],
    stabilityTiers: [],
    leagues: [],
    dateTime: '',
    dateRange: [],
    sortBy: 'p_level',
    sortOrder: 'desc',
    includeDerating: true
  })
  strategyApplied.value = false
  ElMessage.info('筛选条件已重置')
}

const handleSelectStrategy = async (name) => {
  selectedStrategyName.value = name
  const strategy = strategiesMap.get(name)
  if (!strategy) {
    ElMessage.warning(`未找到策略“${name}”的详情`)
    return
  }

  // 将策略的条件映射到 filterForm
  filterForm.powerDiffs = mapStrengthToPowerDiffs(strategy.strength || [])
  filterForm.winPanDiffs = mapWinPanToWinPanDiffs(strategy.winPan || [])
  filterForm.stabilityTiers = strategy.stability || []

  CURRENT_STRATEGY.value = name

  // 如果是示例策略，只加载条件，不自动应用筛选
  if (exampleStrategyNames.includes(name)) {
    strategySelected.value = false // 示例策略不激活统计和结果卡片
    hasResults.value = false
    ElMessage.info(`已加载示例策略“${name}”条件，请在筛选卡片中查看，并手动点击“应用筛选”生成当前策略`)
    return
  }

  // 选择任意已保存策略或当前策略立即应用筛选
  await applyAdvancedFilter()

  // 标记已选择策略
  strategySelected.value = true

  // 根据筛选结果判断是否有数据
  hasResults.value = totalResults.value > 0

  ElMessage.success(`已加载并应用策略：${name}`)
}

const loadStrategyOptions = () => {
  // 模拟加载策略选项
  strategyOptions.value = ['我的策略1', '强势正路', '冷门挖掘']
}

const loadDateTimeOptionsFromDB = async () => {
  try {
    // 模拟API调用：获取所有不同的date_time值
    const mockDbDates = ['26024', '26023', '26022', '26021'] // 从数据库查出来的
    dateTimeOptions.value = mockDbDates
  } catch (error) {
    console.warn('加载date_time选项失败，使用默认值', error)
    dateTimeOptions.value = ['今日', '近3日', '近7日', '本月']
  }
}

const refreshDateTimeOptions = async () => {
  try {
    // 模拟API调用：获取最新date_time及前几期
    // 假设后端返回 { dates: [latest, prev1, prev2, ...] }
    const mockResponse = {
      dates: ['26024', '26023', '26022'] // 最新 + 前两期
    }
    dateTimeOptions.value = mockResponse.dates
  } catch (error) {
    console.warn('刷新date_time选项失败，保留当前值', error)
  }
}

// === 策略管理弹窗逻辑 ===
const strategyManageVisible = ref(false)
const editStrategyVisible = ref(false)
const editingStrategy = ref(null)
const editStrategyName = ref('')

const openStrategyManage = () => {
  strategyManageVisible.value = true
}

const closeStrategyManage = () => {
  strategyManageVisible.value = false
}

const getStrategySummary = (name) => {
  const s = strategiesMap.get(name)
  if (!s) return ''
  return `ΔP:${s.strength.join(',')} ΔWP:${s.winPan.join(',')} P-Tier:${s.stability.join(',')}`
}

const openEditStrategy = (name) => {
  editingStrategy.value = { name }
  editStrategyName.value = name
  editStrategyVisible.value = true
}

const closeEditStrategy = () => {
  editStrategyVisible.value = false
  editingStrategy.value = null
}

const deleteStrategy = (name) => {
  ElMessageBox.confirm(`确定删除策略“${name}”？`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    strategiesMap.delete(name)
    const idx = strategyOptions.value.indexOf(name)
    if (idx > -1) strategyOptions.value.splice(idx, 1)
    strategyOptions.value = strategyOptions.value.filter(n => !exampleStrategyNames.includes(n))
    ElMessage.success('删除成功')
  })
}

const confirmEditStrategy = () => {
  if (!editStrategyName.value.trim()) {
    ElMessage.warning('策略名称不能为空')
    return
  }
  const oldName = editingStrategy.value.name
  const idx = strategyOptions.value.indexOf(oldName)
  if (idx > -1) {
    strategyOptions.value[idx] = editStrategyName.value
  }
  const data = strategiesMap.get(oldName)
  if (data) {
    strategiesMap.delete(oldName)
    strategiesMap.set(editStrategyName.value, data)
  }
  editingStrategy.value.name = editStrategyName.value
  ElMessage.success('修改成功')
  closeEditStrategy()
}
// === 逻辑结束 ===

const toggleStats = () => {
  showStats.value = !showStats.value
}

const exportResults = (format) => {
  ElMessage.info(`正在导出${format}格式...`)
}

const handleSortChange = ({ prop, order }) => {
  filterForm.sortBy = prop
  filterForm.sortOrder = order === 'ascending' ? 'asc' : 'desc'
  ElMessage.info(`排序方式已更改为：${prop} ${filterForm.sortOrder}`)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 监听器
watch(() => filterForm.powerDiffs, (newVal) => {
  if (newVal.length > 0) {
    const positive = newVal.includes('large') || newVal.includes('medium')
    const negative = newVal.includes('small')
    // 简单的方向背离检测
    directionWarning.value = positive && negative
  } else {
    directionWarning.value = false
  }
  }, { deep: true })
    </script>







<style scoped>
.beidan-filter-panel {
  padding: 20px;
}

/* 优化结果表格样式 */
.el-table {
  font-size: 12px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.el-table :deep(.el-table__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.el-table :deep(.el-table__header th) {
  background: transparent;
  font-weight: 600;
  text-align: center;
  padding: 12px 8px;
}

.el-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.el-table :deep(.el-table__row:hover) {
  background-color: #f8f9ff !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-table :deep(.el-table__cell) {
  padding: 8px;
  text-align: center;
}

/* 状态标签样式优化 */
.el-tag {
  border-radius: 12px;
  font-weight: 500;
}

/* 按钮组样式 */
.el-button + .el-button {
  margin-left: 8px;
}

/* 卡片样式优化 */
.el-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e4e7ed;
}

.el-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-bottom: 1px solid #e4e7ed;
}

/* 分页样式 */
.el-pagination {
  margin-top: 20px;
  text-align: center;
}

/* 统计卡片样式 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.9em;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .beidan-filter-panel {
    padding: 10px;
  }
  
  .el-table :deep(.el-table__cell) {
    padding: 4px;
    font-size: 11px;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
  }
}

/* 加载动画 */
.el-loading-mask {
  backdrop-filter: blur(2px);
}

/* 对话框样式优化 */
.el-dialog {
  border-radius: 12px;
}

.el-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  margin: 0;
  padding: 20px;
}

/* 表单样式优化 */
.el-form-item__label {
  font-weight: 600;
  color: #333;
}

.el-checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

/* 表格斑马纹优化 */
.el-table :deep(.el-table__row:nth-child(even)) {
  background-color: #fafbfc;
}

/* 选中行样式 */
.el-table :deep(.el-table__row.current-row) {
  background-color: #e6f7ff !important;
}

/* 排序图标样式 */
.el-table :deep(.el-table__column-sorter) {
  color: #667eea;
}
</style>