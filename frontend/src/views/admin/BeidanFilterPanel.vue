<template>
  <div class="beidan-filter-panel">
    <FilterCardHeader 
      :total-results="realTimeMatchCount" 
      :loading="loading"
      @fetch-real-data="fetchRealData"
      @show-p-level-rules="showPLevelRules"
    >
      <template #extra-actions>
        <el-button type="primary" @click="multiStrategyVisible = true">
          <i class="el-icon-setting"></i>
          多策略管理
        </el-button>
      </template>
    </FilterCardHeader>
    
    <!-- 骨架屏 -->
    <div v-if="loading" class="skeleton-container">
      <!-- 筛选区域骨架屏 -->
      <div class="skeleton-filter-section">
        <div class="skeleton-row" v-for="i in 3" :key="i">
          <div class="skeleton-title"></div>
          <div class="skeleton-options">
            <div class="skeleton-option" v-for="j in 4" :key="j"></div>
          </div>
        </div>
      </div>
      
      <!-- 统计区域骨架屏 -->
      <div class="skeleton-stats-section">
        <div class="skeleton-stat-card" v-for="i in 4" :key="i"></div>
      </div>
      
      <!-- 结果区域骨架屏 -->
      <div class="skeleton-results-section">
        <div class="skeleton-table-header"></div>
        <div class="skeleton-table-row" v-for="i in 5" :key="i"></div>
      </div>
    </div>
    
    <!-- 正常内容 -->
    <template v-else>
      <div class="main-content">
        <section class="panel-section panel-filter">
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
        @save-strategy="onSaveStrategy"
        @manage-strategies="onManageStrategies"
        @load-example-strategy="handleLoadExampleStrategy"
        @apply-advanced-filter="() => applyAdvancedFilter(true)"
        @reset-filters="resetFilters"
      />
        </section>

        <section class="panel-section panel-strategy">
      <StrategySection
        :selected-strategy-name="selectedStrategyName"
        :strategy-options="strategyOptions"
        :strategy-detail-items="strategyDetailItems"
        @handle-select-strategy="handleSelectStrategy"
        @load-strategy-options="loadStrategyOptions"
      />
        </section>

        <section class="panel-section panel-stats" v-if="strategySelected">
          <StatsCard
            :statistics="statistics"
            :filter-form="filterForm"
          />
        </section>

        <section class="panel-section panel-results" v-if="strategySelected">
  <ResultsSection
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
    @open-analysis="handleOpenAnalysis"
  />
        </section>
      </div>
    </template>
    
    <!-- 多策略管理弹窗 -->
    <MultiStrategyManager 
      :visible="multiStrategyVisible"
      :preset-strategies="selectedMultiStrategies"
      :strategy-options-source="strategyOptionsAll"
      @close="multiStrategyVisible = false"
    />

    <!-- 分析弹窗 -->
    <AnalysisDialog
      :visible="analysisVisible"
      :analysis-data="currentAnalysisData"
      @update:visible="analysisVisible = $event"
    />

    <!-- P级规则说明 -->
    <RulesDialog v-model:visible="rulesDialogVisible" :rules="pLevelRules" />

    <!-- 策略管理弹窗 -->
    <el-dialog
      v-model="strategyManageVisible"
      title="管理筛选策略"
      width="600px"
      :before-close="closeStrategyManage"
    >
      <el-table
        ref="strategyManageTableRef"
        :data="getManageStrategyRows()"
        row-key="name"
        style="width: 100%"
        @selection-change="handleManageSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="name" label="策略名称" width="180" />
        <el-table-column label="条件摘要" width="260">
          <template #default="{ row }">
            <span>{{ getStrategySummary(row.name) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="openEditStrategy(row.name)">修改</el-button>
            <el-button size="small" type="danger" @click="deleteStrategy(row.name)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="applySelectedStrategiesToMultiConfig">同步到多策略配置</el-button>
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
        <el-form label-width="80px">
          <el-form-item label="策略名称：">
            <el-input 
              v-model="editStrategyName" 
              placeholder="请输入新策略名称"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
        <div style="text-align: right; margin-top: 20px;">
          <el-button @click="closeEditStrategy">取消</el-button>
          <el-button type="primary" @click="confirmEditStrategy" :disabled="!editStrategyName.trim()">保存修改</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { nextTick, ref, reactive, onMounted, watch } from 'vue'
import { 
  ElMessage, 
  ElMessageBox,
  ElDialog,
  ElTable,
  ElTableColumn,
  ElButton
} from 'element-plus'
import request from '@/utils/request'
// 绛栫暐璇︽儏缂撳瓨锛歬ey 涓虹瓥鐣ュ悕锛寁alue 涓?filters 鏉′欢

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
import AnalysisDialog from './components/AnalysisDialog.vue'
import RulesDialog from './components/RulesDialog.vue'

// 响应式数据
const loading = ref(false)
const realTimeMatchCount = ref(0)
const totalResults = ref(0)
const pagedResults = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const showStats = ref(true)
const strategyApplied = ref(false)
const strategySelected = ref(false) // 是否已选择策略（控制统计和结果卡片显示）
const hasResults = ref(false)
const multiStrategyVisible = ref(false)
const analysisVisible = ref(false)
const currentAnalysisData = ref(null)
const rulesDialogVisible = ref(false)
const pLevelRules = ref({
  p1_criteria: '双一赔且 P ≥ 140（正路稳胆）',
  p2_criteria: '双一赔且 110 ≤ P < 140（正路首选）',
  p3_criteria: '单一赔且 P ≥ 40（正路保障）',
  p4_criteria: '双一赔且 P < 110（正路分歧）',
  p5_criteria: '单一赔且 15 ≤ P < 40（正路存疑）',
  p6_criteria: '单一赔且 P < 15（正路脆弱）',
  p7_criteria: '无一赔或 P < 0（正路缺失）',
  derating_rules: [
    '实力等级差方向与赢盘等级差方向背离时，P级强制下移一档',
    '实力优势方评级为D级时，P级强制下移一档'
  ],
  sort_rules: [
    'P级降序排列',
    'P3场次排在P4之前',
    '同P级按ΔWP降序排列',
    'P7场次按Ssum升序排列'
  ]
})

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

// 选项数据
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
const dateTimeOptions = ref([])
const directionWarning = ref(false)

// 策略相关
const selectedStrategyName = ref('')
const strategyOptions = ref([]) // 策略筛选区域显示（最多 9 条 + 当前策略）
const strategyOptionsAll = ref([]) // 管理列表完整策略
const strategyDetailItems = ref([])
const MAX_FILTER_STRATEGIES = 9
const MULTI_STRATEGY_SELECTION_KEY = 'beidan_multi_strategy_selected'
const selectedMultiStrategies = ref([])
const strategyManageTableRef = ref(null)

// 缁熻数据
const statistics = ref({})

// 绀轰緥绛栫暐锛堜粎渚涢瑙堟潯浠讹紝涓嶈嚜鍔ㄥ簲鐢ㄧ瓫閫夛級
const exampleStrategies = {
  strong: {
    powerDiffs: [2, 3],
    winPanDiffs: [3, 4],
    stabilityTiers: ['S', 'A', 'B'],
    sortBy: 'p_level',
    sortOrder: 'desc'
  },
  upset: {
    powerDiffs: [-1, 0],
    winPanDiffs: [-3, -4],
    stabilityTiers: ['D', 'E'],
    sortBy: 'delta_wp',
    sortOrder: 'asc'
  },
  balance: {
    powerDiffs: [0],
    winPanDiffs: [0],
    stabilityTiers: ['B', 'C'],
    sortBy: 'power_diff',
    sortOrder: 'desc'
  }
}

// 绀轰緥绛栫暐鍚嶇О锛堜粎鐢ㄤ簬鍔犺浇鏉′欢棰勮锛屼笉鑷姩搴旂敤绛涢€夛級
const exampleStrategyNames = ['强势正路', '冷门潜质', '均衡博弈']

const rebuildFilterStrategyOptions = () => {
  const currentStrategyName = '当前策略'
  const currentExists = strategyOptions.value.includes(currentStrategyName)
  const topSaved = [...strategyOptionsAll.value]
    .filter((name) => name !== currentStrategyName)
    .slice(0, MAX_FILTER_STRATEGIES)

  strategyOptions.value = currentExists
    ? [currentStrategyName, ...topSaved]
    : topSaved
}

// 鐢熷懡鍛ㄦ湡
onMounted(async () => {
  console.log('页面加载，开始初始化...')
  loadSelectedMultiStrategies()
  await loadStrategyOptions()
  console.log('loadStrategyOptions瀹屾垚锛岃皟鐢╮efreshDateTimeOptions鍓?filterForm.dateTime:', filterForm.dateTime)
  await refreshDateTimeOptions()
  await fetchRealData(true)
  // 椤甸潰鍔犺浇鍚庤嚜鍔ㄥ簲鐢ㄧ瓫閫夛紝鏄剧ず鏈€新期号的比赛数据
  // 鏃犺filterForm.dateTime鏄惁鏈夊€硷紝閮藉皾璇曞簲鐢ㄧ瓫閫夛紙refreshDateTimeOptions浼氳缃渶鏂版湡鍙凤級
  console.log('椤甸潰鍔犺浇瀹屾垚锛屽皾璇曡嚜鍔ㄥ簲鐢ㄧ瓫閫夛紝鏈熷彿:', filterForm.dateTime)
  console.log('dateTimeOptions:', dateTimeOptions.value)
  console.log('璋冪敤鍓?strategySelected:', strategySelected.value)
  console.log('璋冪敤鍓?totalResults:', totalResults.value)
  try {
    await applyAdvancedFilter(false)
    console.log('鑷姩绛涢€夊畬鎴愶紝鎬荤粨鏋滄暟:', totalResults.value)
    console.log('璋冪敤鍚?strategySelected:', strategySelected.value)
    console.log('璋冪敤鍚?hasResults:', hasResults.value)
    console.log('璋冪敤鍚?pagedResults 数量:', pagedResults.value.length)
  } catch (error) {
    console.error('鑷姩绛涢€夊け璐?', error)
    console.error('閿欒璇︽儏:', error.message)
    console.error('閿欒鏍?', error.stack)
  }
})

// 将 powerDiffs 映射到 strength ֵ
function mapPowerDiffsToStrength(powerDiffs) {
  // 濡傛灉杈撳叆鏄暟鍊兼暟缁勶紝鐩存帴杩斿洖鍘婚噸鍚庣殑鏁扮粍
  if (powerDiffs.length > 0 && typeof powerDiffs[0] === 'number') {
    return [...new Set(powerDiffs)];
  }
  
  // 否则按分类标签映射
  const map = {
    large: [2, 3],
    medium: [1, 2],
    small: [-1, 0],
    tiny: [-2, -1]
  };
  const result = [];
  for (const key of powerDiffs) {
    if (map[key]) result.push(...map[key]);
  }
  return [...new Set(result)];
}

// 将 winPanDiffs 映射到 winPan ֵ
function mapWinPanDiffsToWinPan(winPanDiffs) {
  // 濡傛灉杈撳叆鏄暟鍊兼暟缁勶紝鐩存帴杩斿洖鍘婚噸鍚庣殑鏁扮粍
  if (winPanDiffs.length > 0 && typeof winPanDiffs[0] === 'number') {
    return [...new Set(winPanDiffs)];
  }
  
  // 否则按分类标签映射
  const map = {
    stable: [3, 4],
    unstable: [1, 2, -1, -2],
    risky: [-3, -4]
  };
  const result = [];
  for (const key of winPanDiffs) {
    if (map[key]) result.push(...map[key]);
  }
  return [...new Set(result)];
}

// 灏?strength 值映射到 powerDiffs
function mapStrengthToPowerDiffs(strengthArr) {
  if (!Array.isArray(strengthArr)) return []

  const labelMap = {
    large: [2, 3],
    medium: [1, 2],
    small: [-1, 0],
    tiny: [-2, -1]
  }

  const result = []
  for (const val of strengthArr) {
    if (typeof val === 'number') {
      if (!result.includes(val)) result.push(val)
      continue
    }

    const text = String(val).trim()
    if (/^[+-]?\d+$/.test(text)) {
      const num = Number(text)
      if (!result.includes(num)) result.push(num)
      continue
    }

    const mapped = labelMap[text] || []
    mapped.forEach((num) => {
      if (!result.includes(num)) result.push(num)
    })
  }
  return result
}

// 灏?winPan 值映射到 winPanDiffs
function mapWinPanToWinPanDiffs(winPanArr) {
  if (!Array.isArray(winPanArr)) return []

  const labelMap = {
    stable: [3, 4],
    unstable: [1, 2, -1, -2],
    neutral: [0],
    risky: [-3, -4]
  }

  const result = []
  for (const val of winPanArr) {
    if (typeof val === 'number') {
      if (!result.includes(val)) result.push(val)
      continue
    }

    const text = String(val).trim()
    if (/^[+-]?\d+$/.test(text)) {
      const num = Number(text)
      if (!result.includes(num)) result.push(num)
      continue
    }

    const mapped = labelMap[text] || []
    mapped.forEach((num) => {
      if (!result.includes(num)) result.push(num)
    })
  }
  return result
}

// 娉ㄦ剰锛氭牸寮忓寲鍑芥暟宸茬Щ鑷冲悇鑷娇鐢ㄤ綅缃紝閬垮厤鍏ㄥ眬鏈娇鐢ㄨ鍛?
// 方法
const refreshDateTimeOptions = async () => {
  console.log('寮€濮嬪埛鏂版棩鏈熸椂闂撮€夐」锛屽綋鍓嶉€夐」:', dateTimeOptions.value, '当前选中:', filterForm.dateTime)
  try {
    // 优先尝试从后端API鑾峰彇鏈€鏂扮殑姣旇禌鏃ユ湡鏃堕棿閫夐」
    const response = await request.get('/api/v1/beidan-filter/latest-date-times')
    console.log('API响应:', response)
    
    if (response && response.dateTimes && Array.isArray(response.dateTimes) && response.dateTimes.length > 0) {
      const latestFiveDateTimes = response.dateTimes.slice(0, 5)
      // 鏇存柊鏃ユ湡鏃堕棿閫夐」涓烘渶鏂扮殑姣旇禌鍦烘值（如：['26024', '26023', '26022']锛?      dateTimeOptions.value = latestFiveDateTimes
      console.log('鏃ユ湡鏃堕棿閫夐」宸蹭粠API更新:', latestFiveDateTimes)
      
      // 鑷姩閫夋嫨鏈€鏂版湡鍙凤紝闄ら潪宸茬粡閫夋嫨浜嗘湁鏁堢殑鏈熷彿
      if (!filterForm.dateTime || !latestFiveDateTimes.includes(filterForm.dateTime)) {
        filterForm.dateTime = latestFiveDateTimes[0] // 鏈€鏂版湡鍙?        console.log('宸茶嚜鍔ㄩ€夋嫨鏈€鏂版湡鍙?', latestFiveDateTimes[0])
      }
      console.log('鍒锋柊鍚庨€夐」:', dateTimeOptions.value, '选中:', filterForm.dateTime)
      return
    } else {
      console.warn('API鍝嶅簲鏍煎紡涓嶇鍚堥鏈熸垨杩斿洖绌烘暟缁?', response)
    }
  } catch (error) {
    console.warn('API鑾峰彇鏃ユ湡鏃堕棿閫夐」澶辫触:', error.message)
  }
  
  // 澶囬€夋柟妗堬細API澶辫触鏃朵笉鍐嶇‖缂栫爜鏈熷彿锛岄伩鍏嶉€夊埌搴撻噷涓嶅瓨鍦ㄧ殑鍊?  dateTimeOptions.value = []
  filterForm.dateTime = ''
  console.log('API澶辫触锛屽凡娓呯┖鏃ユ湡鏃堕棿閫夐」锛岀瓑寰呯敤鎴峰埛鏂版暟鎹悗閲嶈瘯')
}

const fetchRealData = async (silent = false) => {
  if (!silent) loading.value = true
  console.log('applyAdvancedFilter: loading set to true, filterForm.dateTime=', filterForm.dateTime)
  try {
    const dateRange = buildDateRangePayload()
    const params = {
      date_time: filterForm.dateTime || '',
      leagues: (filterForm.leagues || []).join(','),
      start_date: dateRange.startDate || '',
      end_date: dateRange.endDate || ''
    }
    // 璋冪敤鍚庣API获取实时比赛数量
    const response = await request.get('/api/v1/beidan-filter/real-time-count', { params })
    
    // request.js 已处理响应拦截，这里 response 就是业务数据
    // 检查 response 是否包含 matchCount
    if (response && response.matchCount !== undefined) {
      realTimeMatchCount.value = Number(response.matchCount || 0)
      // 这里只更新实时场次，不设置策略状态
      if (!silent) {
        ElMessage.success('实时匹配 ' + realTimeMatchCount.value + ' 场')
      }
    } else {
      throw new Error('API 响应格式不正确')
    }
  } catch (error) {
    console.error('实时数据获取失败:', error)
    // 用户友好的中文错误提示
    let errorMessage = '实时数据获取失败'
    if (error.message.includes('Network Error')) {
      errorMessage = '网络连接异常，请检查网络后重试'
    } else if (error.response?.status === 401) {
      errorMessage = '登录已过期，请重新登录'
    } else if (error.response?.status === 403) {
      errorMessage = '权限不足，请联系管理员'
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器繁忙，请稍后重试'
    } else if (error.message) {
      errorMessage = '获取数据失败：' + error.message
    }
    if (!silent) {
      ElMessage.error(errorMessage)
    }
  } finally {
    if (!silent) loading.value = false
  }
}

const showPLevelRules = () => {
  rulesDialogVisible.value = true
}

const applyPreset = async (type) => {
  const presetKey = type === 'conservative' ? 'balance' : type
  const strategy = exampleStrategies[presetKey]
  if (!strategy) {
    ElMessage.warning('未找到对应的示例策略')
    return
  }
  filterForm.powerDiffs = [...strategy.powerDiffs]
  filterForm.winPanDiffs = [...strategy.winPanDiffs]
  filterForm.stabilityTiers = [...strategy.stabilityTiers]
  filterForm.sortBy = strategy.sortBy || 'p_level'
  filterForm.sortOrder = strategy.sortOrder || 'desc'
  ElMessage.info('示例策略仅填充条件，请手动点击"生成当前策略"执行筛选')
}

const handlePreset = (type) => {
  applyPreset(type)
}

const onSaveStrategy = async () => {
  // 保存当前策略
  try {
    const { value: strategyName } = await ElMessageBox.prompt(
      '请输入策略名称，方便后续快速使用',
      '保存筛选策略',
      {
        confirmButtonText: '保存',
        cancelButtonText: '取消',
        inputPlaceholder: '例如：保守策略、激进策略、今日重点',
        inputPattern: /^.{1,20}$/,
        inputErrorMessage: '策略名称长度需为 1-20 个字符'
      }
    )
    
    if (strategyName) {
      // 妫€鏌ユ槸鍚﹀凡瀛樺湪鍚屽悕绛栫暐
      if (strategyOptionsAll.value.includes(strategyName)) {
        ElMessage.warning({
          message: '策略"' + strategyName + '"已经存在，请换一个名称',
          duration: 4000,
          showClose: true
        })
        return
      }
      
      // 构建策略数据（符合后端 StrategyItem 模型）
      // 生成 ISO 格式时间戳
      const now = new Date().toISOString()
      const strategyData = {
        name: strategyName,
        description: '基于当前筛选条件保存的策略',
        threeDimensional: {
          // 这里将前端筛选条件转换为后端三维条件
          powerDifference: {
            homeWeak: false,
            homeBalanced: false,
            homeStrong: false,
            guestWeak: false,
            guestBalanced: false,
            guestStrong: false
          },
          winPanDifference: 0,
          sizeBallDifference: 0
        },
        otherConditions: {
          leagues: filterForm.leagues || [],
          dateTime: filterForm.dateTime || '',
          dateRange: filterForm.dateRange || {},
          // 添加前端筛选字段，确保后端正确保存
          powerDiffs: filterForm.powerDiffs || [],
          winPanDiffs: filterForm.winPanDiffs || [],
          stabilityTiers: filterForm.stabilityTiers || []
        },
        sort: {
          field: filterForm.sortBy || 'p_level',
          order: filterForm.sortOrder || 'desc'
        },
        createdAt: now,
        updatedAt: now
      }
      
      try {
        // 璋冪敤鍚庣API保存策略
        const response = await request.post('/api/v1/beidan-filter/strategies', strategyData)
        
        // 检查响应是否成功
        if (response && (response.id || response.name)) {
          ElMessage.success('策略保存成功，正在刷新策略列表...')
          
          // 立即写入本地状态，确保 UI 立即更新
          if (!strategyOptionsAll.value.includes(strategyName)) {
            strategyOptionsAll.value.push(strategyName)
            rebuildFilterStrategyOptions()
          }
          strategiesMap.set(strategyName, {
            id: response.id,
            originalData: response
          })
          
          // 同时从后端刷新策略列表，确保一致
          try {
            await loadStrategyOptions()
          } catch (loadError) {
            console.error('刷新策略列表失败:', loadError)
            // 如果刷新失败，手动写入本地状态
            if (!strategyOptionsAll.value.includes(strategyName)) {
              strategyOptionsAll.value.push(strategyName)
              rebuildFilterStrategyOptions()
            }
            strategiesMap.set(strategyName, {
              id: response.id,
              originalData: response
            })
            ElMessage.warning('策略已保存，但刷新列表失败，请手动刷新页面查看最新列表')
          }
        } else {
          throw new Error('保存响应格式不正确')
        }
      } catch (error) {
        console.error('保存策略失败:', error)
        const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || '未知错误'
        ElMessage.error('保存失败: ' + errorMsg)
        
        // 濡傛灉鏄璇侀敊璇紝鎻愮ず鐢ㄦ埛閲嶆柊鐧诲綍
        if (error.response?.status === 401) {
          ElMessage.warning('登录已过期，请重新登录后再试')
        }
      }
    }
  } catch {
    // 用户取消
  }
};

const onManageStrategies = () => {
  console.log('绛栫暐绠＄悊鎸夐挳琚偣鍑伙紝鎵撳紑绠＄悊寮圭獥');
  openStrategyManage();
};



const handleLoadExampleStrategy = (type) => {
  const strategy = exampleStrategies[type]
  if (strategy) {
    // 只填充条件，不立刻应用筛选
    console.log('加载示例策略:', type, strategy)
    // 直接赋值，确保响应式
    filterForm.powerDiffs = strategy.powerDiffs
    filterForm.winPanDiffs = strategy.winPanDiffs
    filterForm.stabilityTiers = strategy.stabilityTiers
    filterForm.sortBy = strategy.sortBy || 'p_level'
    filterForm.sortOrder = strategy.sortOrder || 'desc'
    console.log('更新后的 filterForm:', filterForm)
    ElMessage.info('已加载' + (type === 'strong' ? '强势正路' : type === 'upset' ? '冷门潜质' : '均衡博弈') + '示例策略，请在筛选卡片中查看并手动点击"应用筛选"生成当前策略')
  }
}

const formatDateValue = (value) => {
  if (!value) return ''
  if (value instanceof Date) {
    return value.toISOString().slice(0, 10)
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return String(value).slice(0, 10)
  }
  return date.toISOString().slice(0, 10)
}

const buildDateRangePayload = () => {
  if (!Array.isArray(filterForm.dateRange) || filterForm.dateRange.length !== 2) {
    return {}
  }
  const [start, end] = filterForm.dateRange
  if (!start || !end) return {}
  return {
    startDate: formatDateValue(start),
    endDate: formatDateValue(end)
  }
}

const applyAdvancedFilter = async (generateCurrentStrategy = false) => {
  // 妫€鏌ヤ笁缁存潯浠舵槸鍚﹀叏閮ㄤ负绌猴紙瀹炲姏绛夌骇宸€佽耽鐩樼瓑绾у樊銆佺ǔ瀹氭€у垎灞傦級
  const isThreeDimensionalEmpty = 
    filterForm.powerDiffs.length === 0 && 
    filterForm.winPanDiffs.length === 0 && 
    filterForm.stabilityTiers.length === 0
  
  // 濡傛灉鏄敓鎴愬綋鍓嶇瓥鐣ヤ笖涓夌淮鏉′欢涓虹┖锛岀洿鎺ヨ繑鍥炰笉鎵ц任何操作
  if (generateCurrentStrategy && isThreeDimensionalEmpty) {
    ElMessage.info('三维筛选条件为空，未生成"当前策略"。请先设置筛选条件。')
    return
  }
  
  loading.value = true
  console.log('applyAdvancedFilter: loading set to true, filterForm.dateTime=', filterForm.dateTime)
  console.log('applyAdvancedFilter: filterForm.powerDiffs=', filterForm.powerDiffs)
  console.log('applyAdvancedFilter: filterForm.winPanDiffs=', filterForm.winPanDiffs)
  console.log('applyAdvancedFilter: filterForm.stabilityTiers=', filterForm.stabilityTiers)
  try {
    if (generateCurrentStrategy) {
      selectedStrategyName.value = '当前策略'
    }

    // 构建筛选参数
    const filterParams = {
      // 杞崲绛涢€夋潯浠朵负鍚庣闇€要的格式
      threeDimensional: {
        powerDifference: {
          homeWeak: false,
          homeBalanced: false,
          homeStrong: false,
          guestWeak: false,
          guestBalanced: false,
          guestStrong: false
        },
        winPanDifference: 0,
        sizeBallDifference: 0
      },
      otherConditions: {
        leagues: filterForm.leagues || [],
        dateTime: filterForm.dateTime || '',
        dateRange: buildDateRangePayload(),
        includeDerating: !!filterForm.includeDerating,
        // 涓夌淮绛涢€夋潯浠舵暟缁勶紝纭繚涓哄瓧绗︿覆绫诲瀷
        powerDiffs: (filterForm.powerDiffs || []).map(String),
        winPanDiffs: (filterForm.winPanDiffs || []).map(String),
        stabilityTiers: (filterForm.stabilityTiers || []).map(String)
      },
      sort: {
        field: filterForm.sortBy || 'p_level',
        order: filterForm.sortOrder || 'desc'
      },
      page: currentPage.value,
      pageSize: pageSize.value
    }
    
    console.log('applyAdvancedFilter: 鍙戦€佺殑绛涢€夊弬鏁?', JSON.stringify(filterParams, null, 2))
    
  // 调用后端 API 获取真实筛选结果
  const response = await request.post('/api/v1/beidan-filter/advanced-filter', filterParams)
  console.log('applyAdvancedFilter: API响应:', response)
    
    // 处理API响应数据
    if (response && response.matches) {
      const totalItems = Number(
        response?.pagination?.totalItems
        ?? response?.pagination?.total_items
        ?? response?.statistics?.filteredMatches
        ?? response?.statistics?.filtered_matches
        ?? response?.matches?.length
        ?? 0
      )
      totalResults.value = totalItems
      pagedResults.value = response.matches.map(match => {
        const sourceAttrs = resolveSourceAttrs(match)
        return ({
        // 鍩虹淇℃伅
        id: match.id,
        match_id: String(match.dateTime) + '_' + String(match.lineId),
        date_time: match.dateTime,                     // 期号
        line_id: match.lineId,                         // 线路ID
        match_time: pickField(match, ['matchTime', 'match_time', 'matchTimeStr', 'match_time_str'], '', sourceAttrs),
        league: match.league,
        home_team: match.homeTeam,
        away_team: match.guestTeam,
        
        // 三维筛选字段（后端原始值）
        power_diff: match.strength,                    // ΔP: 3/-2
        delta_wp: match.winLevel,                      // ΔWP: 4/-3
        p_level: match.pLevel,                         // P级: 1-7
        stability: match.stability,                    // 绋冲畾鎬х瓑绾э細S/A/B绛夛紙鍘熷瀛楃串）
        
        // 缁撴灉鍗＄墖瀛楁锛堜紭鍏堜娇鐢?00球原始字段）
        power_home: pickField(match, ['homePower', 'home_power'], null, sourceAttrs),
        power_away: pickField(match, ['guestPower', 'guest_power', 'away_power'], null, sourceAttrs),
        win_pan_home: pickField(match, ['homeWinPan', 'home_win_pan', 'home_wp'], null, sourceAttrs),
        win_pan_away: pickField(match, ['guestWinPan', 'guest_win_pan', 'away_win_pan', 'away_wp'], null, sourceAttrs),
        
        // 鐗瑰緛淇℃伅
        home_feature: pickField(match, ['homeFeature', 'home_feature'], null, sourceAttrs),
        away_feature: pickField(match, ['guestFeature', 'guest_feature', 'away_feature'], null, sourceAttrs),
        
        // 鍏朵粬淇℃伅
        handicap: match.handicap,
        odds: match.odds,
        strengthAnalysis: match.strengthAnalysis,
        predictScore: match.predictScore,
        recommendation: match.recommendation,
        
        // 鍘熷数据（用于分析弹窗）
        raw_strength: match.strength,
        raw_win_level: match.winLevel,
        raw_stability: match.stability,
        source_attrs: sourceAttrs
      })
      })
      
      // 鏇存柊缁熻淇℃伅
      statistics.value = response.statistics || {}
      
      // 设置策略应用状态
      strategyApplied.value = true
      strategySelected.value = !!selectedStrategyName.value
      hasResults.value = totalItems > 0
      showStats.value = strategySelected.value
      console.log('applyAdvancedFilter: 鐘舵€佸凡璁剧疆锛宻trategySelected=', strategySelected.value, 'hasResults=', hasResults.value, 'totalItems=', totalItems)
      
      if (strategySelected.value) {
        ElMessage.success('筛选完成，共找到 ' + totalItems + ' 场符合条件的比赛')
      }
    } else {
      throw new Error('API 响应格式不正确')
    }
    
    // ===== 生成"当前策略"涓存椂绛栫暐锛堜粎褰?generateCurrentStrategy 涓?true 时） =====
    if (generateCurrentStrategy) {
      const tempStrategyName = "当前策略"
      // 将 filterForm 条件映射到 strategiesMap 结构
      const currentFilters = {
        strength: mapPowerDiffsToStrength(filterForm.powerDiffs),
        winPan: mapWinPanDiffsToWinPan(filterForm.winPanDiffs),
        stability: filterForm.stabilityTiers || []
      }

      // 更新strategiesMap，添加或更新临时策略
      strategiesMap.set(tempStrategyName, currentFilters)

      // 如果筛选选项里没有"当前策略"，则添加
      if (!strategyOptions.value.includes(tempStrategyName)) {
        strategyOptions.value = [tempStrategyName, ...strategyOptions.value]
      }
      rebuildFilterStrategyOptions()
    }
    // ===== 生成结束 =====

  } catch (error) {
    console.error('绛涢€夊け璐?', error)
    ElMessage.error('筛选失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 安全的字符串转数值函数
const safeParseFloat = (value, defaultValue = null) => {
  const num = parseFloat(value)
  return isNaN(num) ? defaultValue : num
}

const resolveSourceAttrs = (item = {}) => {
  const source = item?.source_attrs ?? item?.sourceAttributes ?? item?.source_attributes ?? item?.rawData ?? item?.raw_data
  return source && typeof source === 'object' ? source : {}
}

const pickField = (item, keys = [], defaultValue = null, source = null) => {
  const attrs = source && typeof source === 'object' ? source : resolveSourceAttrs(item)
  for (const key of keys) {
    if (item?.[key] !== undefined && item?.[key] !== null) return item[key]
  }
  for (const key of keys) {
    if (attrs?.[key] !== undefined && attrs?.[key] !== null) return attrs[key]
  }
  return defaultValue
}

// 从特征字符串中提取百分比数值
const extractPercentValue = (featureStr) => {
  if (!featureStr) return 0
  const match = String(featureStr).match(/(\d+(?:\.\d+)?)%/)
  return match ? Math.min(100, parseFloat(match[1])) : 0
}

// 打开分析弹窗
const handleOpenAnalysis = (row) => {
  const sourceAttrs = resolveSourceAttrs(row)
  const fromRowOrSource = (keys, defaultValue = '-') => pickField(row, keys, defaultValue, sourceAttrs)

  const homePower = safeParseFloat(fromRowOrSource(['power_home', 'homePower', 'home_power']), null)
  const guestPower = safeParseFloat(fromRowOrSource(['power_away', 'guestPower', 'guest_power', 'away_power']), null)
  const homeWinPan = safeParseFloat(fromRowOrSource(['win_pan_home', 'homeWinPan', 'home_win_pan', 'home_wp']), null)
  const guestWinPan = safeParseFloat(fromRowOrSource(['win_pan_away', 'guestWinPan', 'guest_win_pan', 'away_win_pan', 'away_wp']), null)
  const homeFeature = fromRowOrSource(['home_feature', 'homeFeature'], '-')
  const guestFeature = fromRowOrSource(['away_feature', 'guestFeature', 'guest_feature'], '-')

  currentAnalysisData.value = {
    matchId: row.match_id,
    dateTime: row.date_time,
    lineId: fromRowOrSource(['line_id', 'lineId']),
    matchTime: fromRowOrSource(['match_time', 'matchTime', 'matchTimeStr']),
    matchTimeStr: fromRowOrSource(['match_time', 'matchTimeStr', 'matchTime']),
    league: fromRowOrSource(['league', 'gameShortName']),
    gameShortName: fromRowOrSource(['gameShortName', 'league']),

    homeTeam: fromRowOrSource(['home_team', 'homeTeam']),
    guestTeam: fromRowOrSource(['away_team', 'guestTeam', 'awayTeam']),

    homePower,
    guestPower,

    powerDiff: row.power_diff,
    deltaWp: row.delta_wp,
    pLevel: row.p_level,
    stability: row.stability,

    winPanHome: fromRowOrSource(['win_pan_home', 'homeWinPan', 'home_win_pan', 'home_wp']),
    winPanAway: fromRowOrSource(['win_pan_away', 'guestWinPan', 'guest_win_pan', 'away_win_pan', 'away_wp']),

    homeFeature,
    guestFeature,

    odds: row.odds || {},
    homeWinAward: row.odds?.homeWin ?? fromRowOrSource(['homeWinAward']),
    drawAward: row.odds?.draw ?? fromRowOrSource(['drawAward']),
    guestWinAward: row.odds?.guestWin ?? fromRowOrSource(['guestWinAward']),

    handicap: fromRowOrSource(['handicap', 'rq']),
    rq: fromRowOrSource(['rq', 'handicap']),

    strengthAnalysis: row.strengthAnalysis || {},
    predictScore: row.predictScore || '-',
    recommendation: row.recommendation || '-',

    rawStrength: row.power_diff,
    rawWinLevel: row.delta_wp,
    rawStability: row.stability,

    homeJiFenHome: fromRowOrSource(['homeJiFenHome']),
    homeJiFenHomeAll: fromRowOrSource(['homeJiFenHomeAll']),
    awayJiFenHome: fromRowOrSource(['awayJiFenHome']),
    awayJiFenHomeAll: fromRowOrSource(['awayJiFenHomeAll']),
    awayJiFenGuest: fromRowOrSource(['awayJiFenGuest']),

    homeFeaturePercent: extractPercentValue(homeFeature),
    guestFeaturePercent: extractPercentValue(guestFeature),

    homeEnterEfficiency: fromRowOrSource(['homeEnterEfficiency']),
    guestEnterEfficiency: fromRowOrSource(['guestEnterEfficiency']),
    homePreventEfficiency: fromRowOrSource(['homePreventEfficiency']),
    guestPreventEfficiency: fromRowOrSource(['guestPreventEfficiency']),

    homeSpf: fromRowOrSource(['homeSpf']),
    guestSpf: fromRowOrSource(['guestSpf']),

    homeDxqPercentStr: fromRowOrSource(['homeDxqPercentStr', 'home_feature', 'homeFeature'], homeFeature),
    guestDxqPercentStr: fromRowOrSource(['guestDxqPercentStr', 'away_feature', 'guestFeature', 'guest_feature'], guestFeature),

    homeDxqDesc: fromRowOrSource(['homeDxqDesc']),
    guestDxqDesc: fromRowOrSource(['guestDxqDesc']),
    homeDxqSame10Desc: fromRowOrSource(['homeDxqSame10Desc']),
    awayDxqSame10Desc: fromRowOrSource(['awayDxqSame10Desc']),

    homeWinPan,
    guestWinPan,
    homeWinQiu_0: fromRowOrSource(['homeWinQiu_0']),
    homeWinQiu_1: fromRowOrSource(['homeWinQiu_1']),
    homeWinQiu_2: fromRowOrSource(['homeWinQiu_2']),
    homeWinGap_1: fromRowOrSource(['homeWinGap_1']),
    homeWinGap_2: fromRowOrSource(['homeWinGap_2']),
    awayWinQiu_0: fromRowOrSource(['awayWinQiu_0']),
    awayWinQiu_1: fromRowOrSource(['awayWinQiu_1']),
    awayWinQiu_2: fromRowOrSource(['awayWinQiu_2']),
    awayWinGap_1: fromRowOrSource(['awayWinGap_1']),
    awayWinGap_2: fromRowOrSource(['awayWinGap_2']),

    homeLoseQiu_0: fromRowOrSource(['homeLoseQiu_0']),
    homeLoseQiu_1: fromRowOrSource(['homeLoseQiu_1']),
    homeLoseQiu_2: fromRowOrSource(['homeLoseQiu_2']),
    homeLoseGap_1: fromRowOrSource(['homeLoseGap_1']),
    homeLoseGap_2: fromRowOrSource(['homeLoseGap_2']),
    awayLoseQiu_0: fromRowOrSource(['awayLoseQiu_0']),
    awayLoseQiu_1: fromRowOrSource(['awayLoseQiu_1']),
    awayLoseQiu_2: fromRowOrSource(['awayLoseQiu_2']),
    awayLoseGap_1: fromRowOrSource(['awayLoseGap_1']),
    awayLoseGap_2: fromRowOrSource(['awayLoseGap_2']),

    jiaoFenDesc: fromRowOrSource(['jiaoFenDesc'], '暂无历史交锋数据'),
    jiaoFenMatch1: fromRowOrSource(['jiaoFenMatch1'], null),
    jiaoFenMatch2: fromRowOrSource(['jiaoFenMatch2'], null),
    jiaoFenMatch3: fromRowOrSource(['jiaoFenMatch3'], null),
    jiaoFenMatch4: fromRowOrSource(['jiaoFenMatch4'], null),
    jiaoFenMatch5: fromRowOrSource(['jiaoFenMatch5'], null),
    jiaoFenMatch6: fromRowOrSource(['jiaoFenMatch6'], null)
  }
  analysisVisible.value = true
}
const resetFilters = () => {
  const latestDateTime = dateTimeOptions.value[0] || ''
  Object.assign(filterForm, {
    powerDiffs: [],
    winPanDiffs: [],
    stabilityTiers: [],
    leagues: [],
    dateTime: latestDateTime,
    dateRange: [],
    sortBy: 'p_level',
    sortOrder: 'desc',
    includeDerating: true
  })
  strategyApplied.value = false
  strategySelected.value = false
  hasResults.value = false
  showStats.value = false
  currentPage.value = 1
  totalResults.value = 0
  pagedResults.value = []
  
  // 移除"当前策略"卡片
  const currentStrategyName = "当前策略"
  const index = strategyOptions.value.indexOf(currentStrategyName)
  if (index > -1) {
    strategyOptions.value.splice(index, 1)
  }
  strategiesMap.delete(currentStrategyName)
  rebuildFilterStrategyOptions()
  
  // 清空选中状态
  selectedStrategyName.value = ''
  CURRENT_STRATEGY.value = ''
  
  ElMessage.info('筛选条件已重置，"当前策略"已移除')
}

const handleSelectStrategy = async (name) => {
  // 处理清空选择
  if (!name) {
    selectedStrategyName.value = ''
    strategySelected.value = false
    hasResults.value = false
    strategyDetailItems.value = []
    // 涓嶆竻绌虹瓫閫夋潯浠讹紝浠呴殣钘忕粺璁″拰缁撴灉
    return
  }
  
  selectedStrategyName.value = name
  const strategy = strategiesMap.get(name)
  if (!strategy) {
    ElMessage.warning('未找到策略 "' + name + '" 的详情')
    return
  }
  // 鍏堣繘鍏モ€滃凡閫夌瓥鐣モ€濇€侊紝纭繚缁熻/缁撴灉鍗＄墖鍙
  strategySelected.value = true
  showStats.value = true

  // 检查策略数据结构
  if (strategy.strength !== undefined && strategy.winPan !== undefined && strategy.stability !== undefined) {
    // 妫€鏌ユ槸鍚︽槸鏁板€兼暟缁勶紙鏂版牸寮忥級
    const isNumericStrength = strategy.strength.length > 0 && typeof strategy.strength[0] === 'number';
    const isNumericWinPan = strategy.winPan.length > 0 && typeof strategy.winPan[0] === 'number';
    
    if (isNumericStrength && isNumericWinPan) {
      // 新格式：直接使用数值
      filterForm.powerDiffs = strategy.strength;
      filterForm.winPanDiffs = strategy.winPan;
    } else {
      // 旧格式：分类标签，映射后写入
      filterForm.powerDiffs = mapStrengthToPowerDiffs(strategy.strength || []);
      filterForm.winPanDiffs = mapWinPanToWinPanDiffs(strategy.winPan || []);
    }
    filterForm.stabilityTiers = strategy.stability || [];
    
    // 鏇存柊绛栫暐璇︽儏鏄剧ず
    updateStrategyDetails(strategy)
  } else if (strategy.originalData && strategy.originalData.threeDimensional) {
    // 新格式：API 加载的策略
    const otherCond = strategy.originalData.otherConditions || {}
    
    // 转换为前端筛选表单结构
    filterForm.powerDiffs = otherCond.powerDiffs || []
    filterForm.winPanDiffs = otherCond.winPanDiffs || []
    filterForm.stabilityTiers = otherCond.stabilityTiers || []
    
    // 鏇存柊绛栫暐璇︽儏鏄剧ず
    updateStrategyDetailsFromApi(strategy.originalData)
  } else {
    // 鏈煡鏍煎紡
    ElMessage.warning('策略 "' + name + '" 的格式无法识别')
    return
  }

  CURRENT_STRATEGY.value = name

  // 纯示例策略仅加载条件，不自动筛选
  const isPersistedStrategy = Boolean(strategy?.id || strategy?.originalData)
  if (exampleStrategyNames.includes(name) && !isPersistedStrategy) {
    strategySelected.value = false // 绀轰緥绛栫暐涓嶆縺娲荤粺璁″拰缁撴灉鍗＄墖
    hasResults.value = false
    ElMessage.info('已加载示例策略 "' + name + '" 条件，请在筛选卡片中查看并手动点击"应用筛选"生成当前策略')
    return
  }

  // 选择任意已保存策略或当前策略，立即应用筛选
  await applyAdvancedFilter()

  // 鏍囪宸查€夋嫨绛栫暐
  strategySelected.value = true

  // 鏍规嵁绛涢€夌粨鏋滃垽鏂槸鍚︽湁鏁版嵁
  hasResults.value = totalResults.value > 0

  ElMessage.success('已加载并应用策略：' + name)
}

const loadStrategyOptions = async () => {
    try {
      // 从后端API获取策略列表
      const response = await request.get('/api/v1/beidan-filter/strategies')
      console.log('策略API响应:', response)
      
      // 调试：打印完整的响应结构
      console.log('响应类型:', typeof response)
      console.log('响应keys:', Object.keys(response || {}))
      
      // 适配不同的响应格式
      let strategies = []
      if (response && Array.isArray(response.strategies)) {
        strategies = response.strategies
      } else if (Array.isArray(response)) {
        strategies = response
      } else if (response && response.data && Array.isArray(response.data.strategies)) {
        strategies = response.data.strategies
      } else if (response && response.result && Array.isArray(response.result.strategies)) {
        strategies = response.result.strategies
      } else {
        console.warn('鏈煡鐨勫搷搴旀牸寮?', response)
        strategyOptionsAll.value = []
        rebuildFilterStrategyOptions()
        syncSelectedMultiStrategiesWithAvailable()
        return
      }
      
      // 转换后端策略格式为前端格式
      const strategyNames = strategies
        .map(s => s?.name)
        .filter(name => typeof name === 'string' && name.trim().length > 0)
      strategyOptionsAll.value = strategyNames
      rebuildFilterStrategyOptions()
      syncSelectedMultiStrategiesWithAvailable()

      // 同时更新 strategiesMap，将后端策略转换为前端结构
      strategies.forEach(strategy => {
        if (!strategy?.name) return
        // 保存原始数据供后续使用
        strategiesMap.set(strategy.name, {
          id: strategy.id,
          originalData: strategy
        })
      })
  } catch (error) {
    console.error('加载策略选项失败:', error)
    // 检查是否是认证错误，但不自动跳转避免循环
    if (error.response && error.response.status === 401) {
      console.warn('璁よ瘉澶辫触锛屼絾璺宠繃鑷姩璺宠浆閬垮厤鍒锋柊寰幆')
      // 涓嶆墽琛岃烦杞紝閬垮厤鏃犻檺鍒锋柊
      // router.push('/login')
    } else {
      ElMessage.error('加载策略选项失败: ' + (error.message || '未知错误'))
    }
    strategyOptionsAll.value = []
    rebuildFilterStrategyOptions()
    syncSelectedMultiStrategiesWithAvailable()
  }
}

// === 策略管理弹窗逻辑 ===
const strategyManageVisible = ref(false)
const editStrategyVisible = ref(false)
const editingStrategy = ref(null)
const editStrategyName = ref('')

const openStrategyManage = () => {
  strategyManageVisible.value = true
  nextTick(() => {
    const table = strategyManageTableRef.value
    if (!table) return
    table.clearSelection()
    const selectedSet = new Set(selectedMultiStrategies.value)
    getManageStrategyRows().forEach((row) => {
      if (selectedSet.has(row.name)) {
        table.toggleRowSelection(row, true)
      }
    })
  })
}

const closeStrategyManage = () => {
  strategyManageVisible.value = false
}

const handleManageSelectionChange = (rows) => {
  selectedMultiStrategies.value = (rows || []).map((row) => row.name).filter(Boolean)
}

const applySelectedStrategiesToMultiConfig = () => {
  persistSelectedMultiStrategies()
  ElMessage.success('已同步到多策略筛选配置')
}

const getStrategySummary = (name) => {
  const s = strategiesMap.get(name)
  if (!s) return ''
  
  // 处理两种数据结构：
  // 1) 旧格式: 直接包含 strength/winPan/stability
  // 2) 新格式: 包含 originalData.threeDimensional
  if (s.strength !== undefined && s.winPan !== undefined && s.stability !== undefined) {
    return 'ΔP:' + s.strength.join(',') + ' ΔWP:' + s.winPan.join(',') + ' P-Tier:' + s.stability.join(',')
  } else if (s.originalData && s.originalData.threeDimensional) {
    const td = s.originalData.threeDimensional
    // 绠€化显示，因为threeDimensional结构复杂
    return '三维配置: ' + JSON.stringify(td).slice(0, 50) + '...'
  } else {
    return '策略详情未知'
  }
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

const deleteStrategy = async (name) => {
  console.log('=== 鍒犻櫎绛栫暐琚皟鐢?===', { name, strategiesMapSize: strategiesMap.size, strategyOptions: [...strategyOptions.value] })
  
  // 妫€鏌ユ槸鍚︽槸绀轰緥绛栫暐锛堢ず渚嬬瓥鐣ヤ笉鑳藉垹闄わ級
  if (exampleStrategyNames.includes(name)) {
    console.log('尝试删除示例策略，阻止操作')
    ElMessage.warning('示例策略不能删除')
    return
  }
  
    try {
      console.log('显示删除确认对话框')
      await ElMessageBox.confirm('确定删除策略"' + name + '"？', '警告', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      })
      console.log('鐢ㄦ埛纭删除')
      
      // 从strategiesMap获取策略数据
      const strategyData = strategiesMap.get(name)
      console.log('策略数据:', strategyData)
    
    if (!strategyData) {
      // 鏈湴绛栫暐锛屽彧浠庢湰鍦扮姸鎬佷腑鍒犻櫎
      strategiesMap.delete(name)
      const idxAll = strategyOptionsAll.value.indexOf(name)
      if (idxAll > -1) strategyOptionsAll.value.splice(idxAll, 1)
      const idx = strategyOptions.value.indexOf(name)
      if (idx > -1) strategyOptions.value.splice(idx, 1)
      rebuildFilterStrategyOptions()
      selectedMultiStrategies.value = selectedMultiStrategies.value.filter((item) => item !== name)
      persistSelectedMultiStrategies()
      ElMessage.success('删除成功')
      return
    }
    
    // 妫€鏌ョ瓥鐣ユ槸鍚︽湁id（从API鍔犺浇鐨勭瓥鐣ワ級
    if (strategyData.id) {
      // 璋冪敤鍚庣API删除策略 - 淇璺緞锛氫娇鐢ㄦ纭殑v1鍜岃繛瀛楃格式
      await request.delete('/api/v1/beidan-filter/strategies/' + strategyData.id)
    }
    
    // 从本地状态中删除策略
    strategiesMap.delete(name)
    const idxAll = strategyOptionsAll.value.indexOf(name)
    if (idxAll > -1) strategyOptionsAll.value.splice(idxAll, 1)
    const idx = strategyOptions.value.indexOf(name)
    if (idx > -1) strategyOptions.value.splice(idx, 1)
    rebuildFilterStrategyOptions()
    selectedMultiStrategies.value = selectedMultiStrategies.value.filter((item) => item !== name)
    persistSelectedMultiStrategies()
    
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') { // 鐢ㄦ埛鍙栨秷鍒犻櫎
      console.error('删除策略失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const confirmEditStrategy = async () => {
  console.log('=== 纭淇敼绛栫暐 ===', { editStrategyName: editStrategyName.value, editingStrategy: editingStrategy.value })
  
  if (!editStrategyName.value.trim()) {
    ElMessage.warning('策略名称不能为空');
    return;
  }
  
  const oldName = editingStrategy.value.name;

  // 妫€鏌ユ槸鍚︽槸绀轰緥绛栫暐锛堢ず渚嬬瓥鐣ヤ笉鑳戒慨鏀癸級
  if (exampleStrategyNames.includes(oldName)) {
    ElMessage.warning('示例策略不能修改，请先保存为自定义策略');
    return;
  }

  const strategyData = strategiesMap.get(oldName);
  
  if (!strategyData) {
    ElMessage.error('无法获取策略数据，请刷新页面后重试');
    return;
  }
  
  try {
    // 妫€鏌ョ瓥鐣ユ槸鍚︽湁originalData（从API鍔犺浇鐨勭瓥鐣ワ級
    if (strategyData.originalData) {
      // 从API鍔犺浇鐨勭瓥鐣ワ紝璋冪敤鍚庣API更新
      const originalData = strategyData.originalData
      const updatedStrategy = {
        id: originalData.id,
        name: editStrategyName.value.trim(),
        description: originalData.description || '',
        threeDimensional: originalData.threeDimensional || {},
        otherConditions: originalData.otherConditions || {},
        sort: originalData.sort || { field: 'p_level', order: 'desc' }
      }
      
      // 璋冪敤鍚庣API更新策略 - 淇璺緞锛氫娇鐢ㄦ纭殑v1鍜岃繛瀛楃格式
      const response = await request.post('/api/v1/beidan-filter/strategies', updatedStrategy)
      
      // 更新本地状态
      const idxAll = strategyOptionsAll.value.indexOf(oldName)
      if (idxAll > -1) {
        strategyOptionsAll.value[idxAll] = editStrategyName.value
      }
      const idx = strategyOptions.value.indexOf(oldName)
      if (idx > -1) {
        strategyOptions.value[idx] = editStrategyName.value
      }
      
      // 更新strategiesMap
      strategiesMap.delete(oldName)
      strategiesMap.set(editStrategyName.value, {
        id: response.id,
        originalData: response
      })
      rebuildFilterStrategyOptions()
    } else {
      // 本地策略（如"我的策略1"）只更新本地状态
      const idxAll = strategyOptionsAll.value.indexOf(oldName)
      if (idxAll > -1) {
        strategyOptionsAll.value[idxAll] = editStrategyName.value
      }
      const idx = strategyOptions.value.indexOf(oldName)
      if (idx > -1) {
        strategyOptions.value[idx] = editStrategyName.value
      }
      
      // 更新strategiesMap
      const data = strategiesMap.get(oldName)
      if (data) {
        strategiesMap.delete(oldName)
        strategiesMap.set(editStrategyName.value, data)
      }
      rebuildFilterStrategyOptions()
    }

    selectedMultiStrategies.value = selectedMultiStrategies.value
      .map((item) => (item === oldName ? editStrategyName.value.trim() : item))
      .filter(Boolean)
    selectedMultiStrategies.value = [...new Set(selectedMultiStrategies.value)]
    syncSelectedMultiStrategiesWithAvailable()
    
    // 更新editingStrategy鐨勫悕绉帮紙鐢ㄤ簬鏄剧ず锛?    editingStrategy.value.name = editStrategyName.value
    if (selectedStrategyName.value === oldName) {
      selectedStrategyName.value = editStrategyName.value
    }
    
    ElMessage.success('淇敼鎴愬姛');
    closeEditStrategy();
  } catch (error) {
    console.error('淇敼绛栫暐澶辫触:', error)
    ElMessage.error('修改失败: ' + (error.response?.data?.detail || error.message))
  }
}
// === 逻辑结束 ===

const toggleStats = () => {
  showStats.value = !showStats.value
}

const exportResults = async (format) => {
  if (pagedResults.value.length === 0) {
    ElMessage.warning({
      message: '没有数据可导出，请先进行筛选操作',
      duration: 4000,
      showClose: true
    })
    return
  }
  
  // 娣诲姞瀵煎嚭杩涘害鎻愮ず
  const loadingMsg = ElMessage({
    message: '正在准备 ' + format.toUpperCase() + ' 文件，请稍候...',
    type: 'info',
    duration: 0,
    showClose: true
  })
  
      try {
        switch (format) {
          case 'csv':
            exportAsCSV()
            break
          case 'json':
            exportAsJSON()
            break
          case 'excel':
            exportAsExcel()
            break
          default:
            throw new Error('不支持的导出格式: ' + format)
        }
    
    // 瀵煎嚭鎴愬姛鍙嶉
    loadingMsg.close()
    ElMessage.success({
      message: '成功导出 ' + pagedResults.value.length + ' 条数据到 ' + format.toUpperCase() + ' 文件\n文件已自动下载到你的设备',
      duration: 6000,
      showClose: true
    })
    
  } catch (error) {
    // 瀵煎嚭澶辫触鍙嶉
    loadingMsg.close()
    ElMessage.error({
      message: '导出失败：' + (error.message || '未知错误') + '\n请检查网络连接或联系技术支持',
      duration: 8000,
      showClose: true
    })
    console.error('Export failed:', error)
  }
}

const exportAsCSV = () => {
  try {
    const headers = ['ID', '比赛时间', '联赛', '主队', '客队', '实力差', '赢盘差', 'P级', '主队实力', '客队实力', '主队赢盘', '客队赢盘', '主队特征', '客队特征', '盘口', '赔率', '推荐']
    const rows = pagedResults.value.map(match => [
      match.id || '',
      match.match_time || '',
      match.league || '',
      match.home_team || '',
      match.away_team || '',
      match.power_diff || 0,
      match.delta_wp || 0,
      match.p_level || 0,
      match.power_home || 0,
      match.power_away || 0,
      match.win_pan_home || '',
      match.win_pan_away || '',
      match.home_feature || '',
      match.away_feature || '',
      match.handicap || '',
      match.odds ? (match.odds.homeWin + '/' + match.odds.draw + '/' + match.odds.guestWin) : '',
      match.recommendation || ''
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => '"' + String(cell).replace(/"/g, '""') + '"').join(','))
    ].join('\n')
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' })
    downloadFile(blob, 'beidan_filter_results_' + Date.now() + '.csv')
    ElMessage.success('CSV导出成功')
  } catch (error) {
    console.error('CSV导出失败:', error)
    ElMessage.error('CSV导出失败: ' + error.message)
  }
}

const exportAsJSON = () => {
  try {
    const jsonData = {
      exportTime: new Date().toISOString(),
      totalResults: totalResults.value,
      matches: pagedResults.value.map(match => ({
        id: match.id,
        matchTime: match.match_time,
        league: match.league,
        homeTeam: match.home_team,
        awayTeam: match.away_team,
        powerDiff: match.power_diff,
        deltaWp: match.delta_wp,
        pLevel: match.p_level,
        powerHome: match.power_home,
        powerAway: match.power_away,
        winPanHome: match.win_pan_home,
        winPanAway: match.win_pan_away,
        homeFeature: match.home_feature,
        awayFeature: match.away_feature,
        handicap: match.handicap,
        odds: match.odds,
        recommendation: match.recommendation
      }))
    }
    
    const jsonString = JSON.stringify(jsonData, null, 2)
    const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' })
    downloadFile(blob, 'beidan_filter_results_' + Date.now() + '.json')
    ElMessage.success('JSON导出成功')
  } catch (error) {
    console.error('JSON导出失败:', error)
    ElMessage.error('JSON导出失败: ' + error.message)
  }
}

const exportAsExcel = () => {
  try {
    // 创建工作表数据
    const worksheetData = [
      ['ID', '比赛时间', '联赛', '主队', '客队', '实力差', '赢盘差', 'P级', '主队实力', '客队实力', '主队赢盘', '客队赢盘', '主队特征', '客队特征', '盘口', '赔率', '推荐'],
      ...pagedResults.value.map(match => [
        match.id || '',
        match.match_time || '',
        match.league || '',
        match.home_team || '',
        match.away_team || '',
        match.power_diff || 0,
        match.delta_wp || 0,
        match.p_level || 0,
        match.power_home || 0,
        match.power_away || 0,
        match.win_pan_home || '',
        match.win_pan_away || '',
        match.home_feature || '',
        match.away_feature || '',
        match.handicap || '',
        match.odds ? (match.odds.homeWin + '/' + match.odds.draw + '/' + match.odds.guestWin) : '',
        match.recommendation || ''
      ])
    ]
    
    // 将数据转换为 CSV 格式（简化版 Excel 导出）
    const csvContent = worksheetData.map(row => 
      row.map(cell => '"' + String(cell).replace(/"/g, '""') + '"').join(',')
    ).join('\n')
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' })
    downloadFile(blob, 'beidan_filter_results_' + Date.now() + '.xlsx')
    ElMessage.success('Excel导出成功')
  } catch (error) {
    console.error('Excel导出失败:', error)
    ElMessage.error('Excel导出失败: ' + error.message)
  }
}

const downloadFile = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const handleSortChange = async ({ prop, order }) => {
  if (!prop || !order) return
  filterForm.sortBy = prop
  filterForm.sortOrder = order === 'ascending' ? 'asc' : 'desc'
  ElMessage.info('排序方式已更改为：' + prop + ' ' + filterForm.sortOrder)
  if (!selectedStrategyName.value) return
  currentPage.value = 1
  await applyAdvancedFilter(false)
}

const handleSizeChange = async (size) => {
  pageSize.value = size
  if (!selectedStrategyName.value) return
  currentPage.value = 1
  await applyAdvancedFilter(false)
}

const handleCurrentChange = async (page) => {
  currentPage.value = page
  if (!selectedStrategyName.value) return
  await applyAdvancedFilter(false)
}

// 监听器
watch(
  () => [
    ...(filterForm.leagues || []),
    filterForm.dateTime,
    ...(filterForm.dateRange || [])
  ],
  () => {
    fetchRealData(true)
  },
  { deep: true }
)

watch(() => filterForm.powerDiffs, (newVal) => {
  if (newVal.length > 0) {
    // 检测是否同时存在正负方向
    const hasPositive = newVal.some(val => Number(val) > 0);
    const hasNegative = newVal.some(val => Number(val) < 0);
    // 简单方向背离检测
    directionWarning.value = hasPositive && hasNegative;
  } else {
    directionWarning.value = false;
  }
  }, { deep: true })

// 鏇存柊绛栫暐璇︽儏鏄剧ず函数
const updateStrategyDetails = (strategy) => {
  strategyDetailItems.value = [
    { label: '实力筛选', value: strategy.strength ? strategy.strength.join(', ') : '未设置' },
    { label: '赢盘筛选', value: strategy.winPan ? strategy.winPan.join(', ') : '未设置' },
    { label: '稳定性筛选', value: strategy.stability ? strategy.stability.join(', ') : '未设置' }
  ]
}

const getManageStrategyRows = () => {
  return strategyOptionsAll.value
    .filter(name => !exampleStrategyNames.includes(name))
    .map(name => ({ name }))
}

const loadSelectedMultiStrategies = () => {
  try {
    const raw = localStorage.getItem(MULTI_STRATEGY_SELECTION_KEY)
    const parsed = JSON.parse(raw || '[]')
    const selected = Array.isArray(parsed) ? parsed.map(name => String(name || '').trim()).filter(Boolean) : []
    const validSet = new Set(strategyOptionsAll.value)
    selectedMultiStrategies.value = selected.filter(name => validSet.has(name))
  } catch {
    selectedMultiStrategies.value = []
  }
}

const persistSelectedMultiStrategies = () => {
  localStorage.setItem(MULTI_STRATEGY_SELECTION_KEY, JSON.stringify(selectedMultiStrategies.value))
}

const syncSelectedMultiStrategiesWithAvailable = () => {
  const validSet = new Set(strategyOptionsAll.value)
  selectedMultiStrategies.value = selectedMultiStrategies.value.filter(name => validSet.has(name))
  persistSelectedMultiStrategies()
}

// 从API鏁版嵁鏇存柊绛栫暐璇︽儏鏄剧ず
  const updateStrategyDetailsFromApi = (strategyData) => {
    const otherCond = strategyData.otherConditions || {}
    
    strategyDetailItems.value = [
      { label: '实力等级差', value: otherCond.powerDiffs && otherCond.powerDiffs.length > 0 ? otherCond.powerDiffs.join(', ') : '未设置' },
      { label: '赢盘等级差', value: otherCond.winPanDiffs && otherCond.winPanDiffs.length > 0 ? otherCond.winPanDiffs.join(', ') : '未设置' },
      { label: '一赔稳定性', value: otherCond.stabilityTiers && otherCond.stabilityTiers.length > 0 ? otherCond.stabilityTiers.join(', ') : '未设置' },
      { label: '排序方式', value: strategyData.sort ? (strategyData.sort.field + ' (' + strategyData.sort.order + ')') : '未设置' }
    ]
  }
</script>







<style scoped>
.beidan-filter-panel {
  --morandi-bg: #eceff1;
  --morandi-surface: #f7f6f3;
  --morandi-elevated: #fdfcfb;
  --morandi-border: #d6d2cb;
  --morandi-text: #5f6368;
  --morandi-text-muted: #8b8680;
  --morandi-accent: #8ea3b0;
  --morandi-accent-soft: #e6ebef;
  --morandi-success: #a8b9aa;
  --morandi-warn: #c9bba7;
  --morandi-danger: #c4a7a0;
  padding: 20px;
  max-width: 1520px;
  margin: 0 auto;
  color: var(--morandi-text);
  background:
    radial-gradient(1200px 520px at 18% -16%, rgba(142, 163, 176, 0.12), transparent 60%),
    radial-gradient(980px 420px at 95% 0%, rgba(201, 187, 167, 0.16), transparent 58%),
    var(--morandi-bg);
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.panel-section {
  width: 100%;
}

.beidan-filter-panel :deep(.el-card) {
  border-radius: 14px;
  border: 1px solid var(--morandi-border);
  background: var(--morandi-surface);
  box-shadow: 0 12px 28px rgba(95, 99, 104, 0.08);
}

.beidan-filter-panel :deep(.el-card__header) {
  border-bottom: 1px solid #e7e3dd;
  background: linear-gradient(180deg, #f9f8f6 0%, #f2f1ee 100%);
}

.beidan-filter-panel :deep(.filter-section .filter-group) {
  border-radius: 12px;
  border-color: var(--morandi-border);
  background: var(--morandi-elevated);
  box-shadow: 0 6px 16px rgba(95, 99, 104, 0.06);
}

.beidan-filter-panel :deep(.group-title),
.beidan-filter-panel :deep(.filter-item label),
.beidan-filter-panel :deep(.strategy-label),
.beidan-filter-panel :deep(.strategy-list-title) {
  color: var(--morandi-text);
}

.beidan-filter-panel :deep(.group-hint),
.beidan-filter-panel :deep(.rule-preview),
.beidan-filter-panel :deep(.detail-label) {
  color: var(--morandi-text-muted);
}

.beidan-filter-panel :deep(.el-input__wrapper),
.beidan-filter-panel :deep(.el-select__wrapper),
.beidan-filter-panel :deep(.el-textarea__inner) {
  border-radius: 10px;
  box-shadow: inset 0 0 0 1px #d9d6d0 !important;
  background: #f9f8f6;
}

.beidan-filter-panel :deep(.el-input__wrapper.is-focus),
.beidan-filter-panel :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px var(--morandi-accent) !important;
}

.beidan-filter-panel :deep(.el-button) {
  border-radius: 10px;
  min-height: 34px;
  padding: 0 14px;
  border-color: #d7d3cc;
  color: #636870;
  background: #f5f4f1;
}

.beidan-filter-panel :deep(.el-button--primary) {
  background: var(--morandi-accent);
  border-color: var(--morandi-accent);
  color: #fff;
}

.beidan-filter-panel :deep(.el-button--success) {
  background: var(--morandi-success);
  border-color: var(--morandi-success);
  color: #fff;
}

.beidan-filter-panel :deep(.el-button--warning) {
  background: var(--morandi-warn);
  border-color: var(--morandi-warn);
  color: #fff;
}

.beidan-filter-panel :deep(.el-button--danger) {
  background: var(--morandi-danger);
  border-color: var(--morandi-danger);
  color: #fff;
}

.beidan-filter-panel :deep(.el-button + .el-button) {
  margin-left: 10px;
}

.beidan-filter-panel :deep(.el-checkbox-button__inner) {
  border-radius: 10px !important;
  border-color: #d8d4cd !important;
  background: #f9f8f6;
  color: #5f6368;
}

.beidan-filter-panel :deep(.el-checkbox-button.is-checked .el-checkbox-button__inner) {
  background: var(--morandi-accent-soft);
  border-color: var(--morandi-accent);
  color: #4f5963;
  box-shadow: none;
}

.beidan-filter-panel :deep(.strategy-card),
.beidan-filter-panel :deep(.stats-card),
.beidan-filter-panel :deep(.result-card) {
  margin-top: 0;
  margin-bottom: 0;
}

.beidan-filter-panel :deep(.strategy-grid) {
  gap: 10px;
}

.beidan-filter-panel :deep(.strategy-item) {
  border-radius: 10px;
  border-color: #d8d4cd;
  background: #f9f8f6;
}

.beidan-filter-panel :deep(.strategy-item.active) {
  border-color: var(--morandi-accent);
  box-shadow: 0 8px 18px rgba(142, 163, 176, 0.22);
}

.beidan-filter-panel :deep(.stat-item) {
  border-radius: 0;
  border: none;
  background: transparent;
  box-shadow: none;
}

.beidan-filter-panel :deep(.stat-number) {
  color: #7f95a5;
}

.beidan-filter-panel :deep(.el-table) {
  font-size: 12px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(95, 99, 104, 0.08);
}

.beidan-filter-panel :deep(.result-card .el-card__body) {
  padding: 8px 0 12px;
}

.beidan-filter-panel :deep(.result-card .el-table) {
  border-radius: 0;
  box-shadow: none;
}

.beidan-filter-panel :deep(.el-table th.el-table__cell) {
  background: #eef1f3;
  color: #60656d;
  font-weight: 600;
  text-align: center;
  padding: 11px 8px;
}

.beidan-filter-panel :deep(.el-table td.el-table__cell) {
  padding: 9px 8px;
  text-align: center;
  color: #5f6368;
}

.beidan-filter-panel :deep(.el-table__row:hover > td.el-table__cell) {
  background: #f1f4f6 !important;
}

.beidan-filter-panel :deep(.el-tag) {
  border-radius: 999px;
  font-weight: 600;
}

.beidan-filter-panel :deep(.el-pagination) {
  margin-top: 18px;
  justify-content: flex-end;
}

.beidan-filter-panel :deep(.el-dialog) {
  border-radius: 14px;
  overflow: hidden;
}

.beidan-filter-panel :deep(.el-dialog__header) {
  margin: 0;
  padding: 16px 20px;
  background: #eef1f3;
  border-bottom: 1px solid #e3dfd8;
}

.beidan-filter-panel :deep(.el-dialog__title) {
  color: #59606a;
  font-weight: 700;
}

.beidan-filter-panel :deep(.dialog-footer) {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

/* skeleton */
.skeleton-container {
  border: 1px solid var(--morandi-border);
  border-radius: 14px;
  background: var(--morandi-surface);
  padding: 18px;
}

.skeleton-title,
.skeleton-option,
.skeleton-stat-card,
.skeleton-table-header,
.skeleton-table-row {
  background: linear-gradient(90deg, #ece9e4 25%, #f4f2ef 50%, #ece9e4 75%);
  background-size: 320% 100%;
  animation: shimmer 1.8s infinite linear;
  border-radius: 10px;
}

.skeleton-row {
  margin-bottom: 16px;
}

.skeleton-title {
  height: 16px;
  width: 240px;
  margin-bottom: 10px;
}

.skeleton-options {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.skeleton-option {
  height: 44px;
}

.skeleton-stats-section {
  margin: 10px 0 16px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.skeleton-stat-card {
  height: 72px;
}

.skeleton-table-header {
  height: 42px;
  margin-bottom: 10px;
}

.skeleton-table-row {
  height: 36px;
  margin-bottom: 8px;
}

@keyframes shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: 0 0; }
}

@media (max-width: 768px) {
  .beidan-filter-panel {
    padding: 12px;
  }

  .beidan-filter-panel :deep(.el-table__cell) {
    padding: 8px 4px;
    min-height: 42px;
  }

  .skeleton-options,
  .skeleton-stats-section {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .beidan-filter-panel :deep(.el-button) {
    min-height: 40px;
  }

  .beidan-filter-panel :deep(.el-pagination) {
    justify-content: center;
  }
}
</style>




