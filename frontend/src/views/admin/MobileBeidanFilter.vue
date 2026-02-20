<template>
  <div class="mobile-beidan-page" :class="{ 'supports-safe-area': supportsSafeArea }">
    <header class="top-header">
      <div>
        <h1>北单三维筛选器</h1>
        <p>移动端</p>
      </div>
      <button class="ghost-btn" :disabled="loading" @click="fetchRealData">获取实时数据</button>
    </header>

    <main class="content-wrap">
      <section v-if="activeTab === 'strategy'" class="card strategy-tab">
        <h2>策略</h2>
        <p class="sub">基于以下三维条件去配置</p>

        <div class="grid-block">
          <label>实力等级差 ΔP</label>
          <div class="chips">
            <button
              v-for="item in strengthOptions"
              :key="`power-${item}`"
              class="chip"
              :class="{ active: filterForm.powerDiffs.includes(item) }"
              @click="toggleFilterValue('powerDiffs', item)"
            >
              {{ item > 0 ? `+${item}` : item }}
            </button>
          </div>
        </div>

        <div class="grid-block">
          <label>赢盘等级差 ΔWP</label>
          <div class="chips">
            <button
              v-for="item in winPanOptions"
              :key="`win-${item}`"
              class="chip"
              :class="{ active: filterForm.winPanDiffs.includes(item) }"
              @click="toggleFilterValue('winPanDiffs', item)"
            >
              {{ item > 0 ? `+${item}` : item }}
            </button>
          </div>
        </div>

        <div class="grid-block">
          <label>稳定性层级</label>
          <div class="chips">
            <button
              v-for="item in stabilityOptions"
              :key="`tier-${item.value}`"
              class="chip"
              :class="{ active: filterForm.stabilityTiers.includes(item.value) }"
              @click="toggleFilterValue('stabilityTiers', item.value)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>

        <div class="action-row">
          <button class="secondary-btn" @click="saveStrategy">保存策略</button>
          <button class="secondary-btn" @click="resetThreeDimensional">清空三维条件</button>
          <button class="secondary-btn" @click="strategyManageVisible = true">管理策略</button>
        </div>
      </section>

      <section v-if="activeTab === 'filter'" class="card filter-tab">
        <h2>筛选</h2>
        <p class="sub">实时场次、筛选其它条件、策略、排序共同作用于结果场次</p>

        <div class="metric-panel">
          <span>实时匹配</span>
          <strong>{{ realTimeMatchCount }} 场</strong>
        </div>

        <div class="grid-block">
          <label>期号筛选</label>
          <select v-model="filterForm.dateTime" class="select-input">
            <option value="">全部期号</option>
            <option v-for="item in dateTimeOptions" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>

        <div class="grid-block dual-grid">
          <div>
            <label>时间筛选-开始</label>
            <input v-model="filterForm.dateRange[0]" class="select-input date-input" type="date" />
          </div>
          <div>
            <label>时间筛选-结束</label>
            <input v-model="filterForm.dateRange[1]" class="select-input date-input" type="date" />
          </div>
        </div>

        <div class="grid-block">
          <label>联赛筛选</label>
          <select v-model="selectedLeague" class="select-input" @change="onLeagueChange">
            <option value="">全部联赛</option>
            <option v-for="league in availableLeagues" :key="league" :value="league">{{ league }}</option>
          </select>
        </div>

        <div class="grid-block">
          <label>策略筛选</label>
          <div class="chips strategy-tags">
            <button
              class="chip"
              :class="{ active: !selectedStrategyName }"
              @click="clearStrategySelection"
            >
              不使用策略
            </button>
            <button
              v-for="item in strategyList"
              :key="`tag-${item.name}`"
              class="chip"
              :class="{ active: selectedStrategyName === item.name }"
              @click="selectStrategyTag(item.name)"
            >
              {{ item.name }}
            </button>
          </div>
        </div>

        <div class="grid-block dual-grid">
          <div>
            <label>排列方式</label>
            <select v-model="filterForm.sortBy" class="select-input">
              <option value="p_level">P级</option>
              <option value="delta_wp">ΔWP</option>
              <option value="strength">ΔP</option>
            </select>
          </div>
          <div>
            <label>排序方向</label>
            <select v-model="filterForm.sortOrder" class="select-input">
              <option value="desc">降序</option>
              <option value="asc">升序</option>
            </select>
          </div>
        </div>

        <div class="action-row">
          <button class="primary-btn" :disabled="loading" @click="applyFilter">筛选结果场次</button>
          <button class="secondary-btn" :disabled="loading" @click="fetchRealData">刷新场次</button>
          <button class="secondary-btn" :disabled="loading" @click="resetAllFilters">重置全部</button>
        </div>
      </section>

      <section v-if="activeTab === 'results'" class="card results-tab">
        <h2>结果</h2>
        <p class="sub">符合场次数量统计 + 场次列表</p>

        <div class="stats-grid">
          <div class="stat-box">
            <span>符合条件场次</span>
            <strong>{{ statTotalMatches }}</strong>
          </div>
          <div class="stat-box">
            <span>实力等级差 ΔP</span>
            <strong>{{ statDeltaPCount }}</strong>
          </div>
          <div class="stat-box">
            <span>赢盘等级差 ΔWP</span>
            <strong>{{ statDeltaWpCount }}</strong>
          </div>
          <div class="stat-box">
            <span>一赔稳定态 P-Tier</span>
            <strong>{{ statPTierCount }}</strong>
          </div>
        </div>

        <div class="result-summary">
          <span>条件摘要：</span>
          <span>{{ filterSummary }}</span>
        </div>

        <div v-if="loading" class="empty">加载中...</div>
        <div v-else-if="results.length === 0" class="empty">暂无结果，请先在“筛选”执行筛选</div>

        <div v-else class="result-list">
          <article v-for="item in pagedResults" :key="item.id" class="result-card clickable" @click="openAnalysis(item)">
            <div class="row top">
              <strong>{{ item.league || '-' }}</strong>
              <span>{{ item.matchTime || '-' }}</span>
            </div>
            <div class="teams">{{ item.homeTeam || '-' }} vs {{ item.guestTeam || '-' }}</div>
            <div class="row tags">
              <span>ΔP {{ item.strength ?? '-' }}</span>
              <span>ΔWP {{ item.winLevel ?? '-' }}</span>
              <span>P级 {{ item.pLevel ?? '-' }}</span>
            </div>
          </article>
        </div>

        <div v-if="results.length > pageSize" class="pager-row">
          <button class="secondary-btn" :disabled="currentPage <= 1" @click="currentPage--">上一页</button>
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button class="secondary-btn" :disabled="currentPage >= totalPages" @click="currentPage++">下一页</button>
        </div>
      </section>

      <template v-if="activeTab === 'output'">
        <section class="card output-tab">
          <h2>输出</h2>
          <p class="sub">导出筛选结果</p>

          <div class="action-row">
            <button class="primary-btn" :disabled="results.length === 0" @click="exportResults('csv')">导出 CSV</button>
            <button class="primary-btn" :disabled="results.length === 0" @click="exportResults('json')">导出 JSON</button>
            <button class="primary-btn" :disabled="results.length === 0" @click="exportResults('excel')">导出 Excel</button>
          </div>
        </section>

        <section class="card output-tab">
          <h2>定时与推送配置</h2>
          <p class="sub">预选策略 → 定时执行筛选 → 钉钉推送结果</p>

          <div v-if="strategyList.length === 0" class="empty">
            暂无已保存策略，请先在“策略”标签保存策略
          </div>

          <template v-else>
            <div class="grid-block">
              <label>预选策略（用于定时任务）</label>
              <div class="chips strategy-tags">
                <button
                  v-for="item in strategyList"
                  :key="`output-preselect-${item.name}`"
                  class="chip"
                  :class="{ active: selectedMultiStrategies.includes(item.name) }"
                  @click="toggleMultiStrategySelection(item.name)"
                >
                  {{ item.name }}
                </button>
              </div>
              <div class="result-summary">
                <span>已预选：</span>
                <span>{{ selectedMultiStrategies.length }} 个策略</span>
              </div>
            </div>

            <div class="grid-block">
              <label>任务名称</label>
              <input
                v-model.trim="multiStrategyForm.taskName"
                class="select-input"
                type="text"
                placeholder="例如：北单每日多策略筛选"
              />
            </div>

            <div class="grid-block dual-grid">
              <div>
                <label>执行频率</label>
                <select v-model="multiStrategyForm.cronType" class="select-input" @change="updateCronExpression">
                  <option value="daily">每天</option>
                  <option value="weekly">每周</option>
                  <option value="hourly">每小时</option>
                  <option value="custom">自定义</option>
                </select>
              </div>
              <div>
                <label>Cron 表达式</label>
                <input
                  v-model.trim="multiStrategyForm.cronExpression"
                  class="select-input"
                  type="text"
                  :readonly="multiStrategyForm.cronType !== 'custom'"
                  placeholder="例如：0 9 * * *"
                />
              </div>
            </div>

            <div class="grid-block">
              <label>消息格式</label>
              <div class="chips">
                <button
                  class="chip"
                  :class="{ active: multiStrategyForm.messageFormat === 'table' }"
                  @click="multiStrategyForm.messageFormat = 'table'"
                >
                  表格
                </button>
                <button
                  class="chip"
                  :class="{ active: multiStrategyForm.messageFormat === 'text' }"
                  @click="multiStrategyForm.messageFormat = 'text'"
                >
                  纯文本
                </button>
              </div>
            </div>

            <div class="grid-block">
              <label class="multi-check">
                <input v-model="multiStrategyForm.dingtalkEnabled" type="checkbox" />
                <span>启用钉钉推送</span>
              </label>
              <textarea
                v-if="multiStrategyForm.dingtalkEnabled"
                v-model.trim="multiStrategyForm.dingtalkWebhook"
                class="select-input webhook-input"
                rows="3"
                placeholder="请输入钉钉机器人 Webhook URL"
              ></textarea>
            </div>

            <div class="action-row output-action-row">
              <button class="secondary-btn" @click="selectAllMultiStrategies">全选策略</button>
              <button class="secondary-btn" @click="clearMultiStrategies">清空预选</button>
              <button class="secondary-btn" @click="strategyManageVisible = true">管理策略</button>
            </div>

            <div class="action-row output-action-row">
              <button
                class="primary-btn"
                :disabled="!canSaveMultiConfig || multiStrategySaving"
                @click="saveMultiStrategyConfig"
              >
                保存定时配置
              </button>
              <button class="secondary-btn" :disabled="multiStrategyLoadingTasks" @click="loadMultiStrategyTasks">
                刷新任务
              </button>
              <button
                class="secondary-btn output-action-wide"
                :disabled="selectedMultiStrategies.length === 0 || multiStrategyExecuting"
                @click="executeMultiStrategyNow"
              >
                立即执行并推送
              </button>
            </div>
            <p class="sub">当前账号任务数：{{ multiStrategyTaskCount }}</p>
          </template>
        </section>
      </template>
    </main>

    <el-dialog
      v-model="analysisVisible"
      title="比赛分析"
      width="96%"
      top="2vh"
      class="mobile-analysis-dialog"
      destroy-on-close
    >
      <div v-if="currentAnalysisData" class="analysis-mobile-wrap">
        <section class="analysis-mobile-card">
          <h3>比赛基本信息</h3>
          <div class="analysis-kv">
            <div><span>联赛</span><strong>{{ displayValue(currentAnalysisData.gameShortName) }}</strong></div>
            <div><span>比赛时间</span><strong>{{ displayValue(currentAnalysisData.matchTimeStr) }}</strong></div>
            <div><span>主队</span><strong>{{ displayValue(currentAnalysisData.homeTeam) }}</strong></div>
            <div><span>客队</span><strong>{{ displayValue(currentAnalysisData.guestTeam) }}</strong></div>
            <div><span>主队实力</span><strong>{{ displayValue(currentAnalysisData.homePower) }}</strong></div>
            <div><span>客队实力</span><strong>{{ displayValue(currentAnalysisData.guestPower) }}</strong></div>
          </div>
        </section>

        <section class="analysis-mobile-card">
          <h3>赔率与让球</h3>
          <div class="analysis-kv">
            <div><span>主胜</span><strong>{{ displayValue(currentAnalysisData.homeWinAward) }}</strong></div>
            <div><span>平局</span><strong>{{ displayValue(currentAnalysisData.drawAward) }}</strong></div>
            <div><span>客胜</span><strong>{{ displayValue(currentAnalysisData.guestWinAward) }}</strong></div>
            <div><span>让球</span><strong>{{ displayValue(currentAnalysisData.rq) }}</strong></div>
          </div>
        </section>

        <section class="analysis-mobile-card">
          <h3>核心对比指标</h3>
          <div class="analysis-kv">
            <div><span>实力等级差 ΔP</span><strong>{{ displayValue(currentAnalysisData.rawStrength) }}</strong></div>
            <div><span>赢盘等级差 ΔWP</span><strong>{{ displayValue(currentAnalysisData.rawWinLevel) }}</strong></div>
            <div><span>P级</span><strong>{{ displayValue(currentAnalysisData.pLevel) }}</strong></div>
            <div><span>稳定性</span><strong>{{ displayValue(currentAnalysisData.rawStability) }}</strong></div>
            <div><span>主队特征</span><strong>{{ displayValue(currentAnalysisData.homeFeature) }}</strong></div>
            <div><span>客队特征</span><strong>{{ displayValue(currentAnalysisData.guestFeature) }}</strong></div>
            <div><span>主队近期</span><strong>{{ displayValue(currentAnalysisData.homeSpf) }}</strong></div>
            <div><span>客队近期</span><strong>{{ displayValue(currentAnalysisData.guestSpf) }}</strong></div>
          </div>
        </section>

        <section class="analysis-mobile-card">
          <h3>历史交锋</h3>
          <p class="analysis-desc">{{ displayValue(currentAnalysisData.jiaoFenDesc) }}</p>
          <div class="history-list">
            <div v-for="item in getJiaoFenMatches(currentAnalysisData)" :key="item" class="history-item">{{ item }}</div>
            <div v-if="getJiaoFenMatches(currentAnalysisData).length === 0" class="history-item">暂无交锋记录</div>
          </div>
        </section>
      </div>
      <div v-else class="empty">暂无分析数据</div>
    </el-dialog>

    <el-dialog v-model="strategyManageVisible" title="管理策略" width="92%" top="8vh">
      <div class="manage-list">
        <div v-if="strategyList.length === 0" class="empty">暂无已保存策略</div>
        <div v-for="item in strategyList" :key="`manage-${item.name}`" class="manage-item">
          <div class="manage-name">{{ item.name }}</div>
          <label class="multi-check">
            <input
              type="checkbox"
              :checked="selectedMultiStrategies.includes(item.name)"
              @change="toggleMultiStrategySelection(item.name)"
            />
            <span>加入多策略输出</span>
          </label>
          <div class="manage-actions">
            <button class="secondary-btn" @click="applyStrategyByName(item.name, true)">应用</button>
            <button class="secondary-btn" @click="renameStrategy(item.name)">改名</button>
            <button class="danger-btn" @click="deleteStrategy(item.name)">删除</button>
          </div>
        </div>
      </div>
    </el-dialog>

    <nav class="bottom-nav" aria-label="页面标签">
      <button
        v-for="tab in navTabs"
        :key="tab.id"
        class="nav-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <span class="nav-dot"></span>
        <span>{{ tab.label }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const supportsSafeArea = typeof CSS !== 'undefined' && typeof CSS.supports === 'function'
  ? CSS.supports('padding-bottom: env(safe-area-inset-bottom)')
  : false

const activeTab = ref('strategy')
const loading = ref(false)
const realTimeMatchCount = ref(0)
const totalResults = ref(0)
const results = ref([])
const strategyList = ref([])
const strategyOptionsAll = ref([])
const selectedStrategyName = ref('')
const selectedMultiStrategies = ref([])
const strategyManageVisible = ref(false)
const dateTimeOptions = ref([])
const availableLeagues = ref([])
const selectedLeague = ref('')
const statistics = ref({})
const analysisVisible = ref(false)
const currentAnalysisData = ref(null)
const currentPage = ref(1)
const pageSize = 20
const multiStrategySaving = ref(false)
const multiStrategyLoadingTasks = ref(false)
const multiStrategyExecuting = ref(false)
const multiStrategyTaskCount = ref(0)

const MULTI_STRATEGY_SELECTION_KEY = 'beidan_multi_strategy_selected'

const filterForm = reactive({
  powerDiffs: [],
  winPanDiffs: [],
  stabilityTiers: [],
  leagues: [],
  dateTime: '',
  dateRange: ['', ''],
  sortBy: 'p_level',
  sortOrder: 'desc',
  includeDerating: true
})
const multiStrategyForm = reactive({
  taskName: '',
  cronType: 'daily',
  cronExpression: '0 9 * * *',
  messageFormat: 'table',
  dingtalkEnabled: false,
  dingtalkWebhook: ''
})

const navTabs = [
  { id: 'strategy', label: '策略' },
  { id: 'filter', label: '筛选' },
  { id: 'results', label: '结果' },
  { id: 'output', label: '输出' }
]

const strengthOptions = [-3, -2, -1, 0, 1, 2, 3]
const winPanOptions = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
const stabilityOptions = [
  { label: 'P1', value: 'S' },
  { label: 'P2', value: 'A' },
  { label: 'P3', value: 'B' },
  { label: 'P4', value: 'B-' },
  { label: 'P5', value: 'C' },
  { label: 'P6', value: 'D' },
  { label: 'P7', value: 'E' }
]

const statTotalMatches = computed(() =>
  statistics.value?.filteredMatches ??
  statistics.value?.filtered_matches ??
  statistics.value?.total_matches ??
  statistics.value?.totalMatches ??
  totalResults.value
)
const statDeltaPCount = computed(() =>
  filterForm.powerDiffs.length > 0
    ? (statistics.value?.delta_p_count ?? statistics.value?.deltaPCount ?? 0)
    : '未设置'
)
const statDeltaWpCount = computed(() =>
  filterForm.winPanDiffs.length > 0
    ? (statistics.value?.delta_wp_count ?? statistics.value?.deltaWpCount ?? 0)
    : '未设置'
)
const statPTierCount = computed(() =>
  filterForm.stabilityTiers.length > 0
    ? (statistics.value?.p_tier_count ?? statistics.value?.pTierCount ?? 0)
    : '未设置'
)
const totalPages = computed(() => Math.max(1, Math.ceil(results.value.length / pageSize)))
const pagedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return results.value.slice(start, start + pageSize)
})
const filterSummary = computed(() => {
  const parts = []
  if (selectedStrategyName.value) parts.push(`策略:${selectedStrategyName.value}`)
  if (filterForm.dateTime) parts.push(`期号:${filterForm.dateTime}`)
  if (filterForm.dateRange?.[0] && filterForm.dateRange?.[1]) parts.push(`时间:${filterForm.dateRange[0]}~${filterForm.dateRange[1]}`)
  if (filterForm.leagues.length > 0) parts.push(`联赛:${filterForm.leagues.join('/')}`)
  if (selectedStrategyName.value && filterForm.powerDiffs.length > 0) parts.push(`ΔP:${filterForm.powerDiffs.join(',')}`)
  if (selectedStrategyName.value && filterForm.winPanDiffs.length > 0) parts.push(`ΔWP:${filterForm.winPanDiffs.join(',')}`)
  if (selectedStrategyName.value && filterForm.stabilityTiers.length > 0) parts.push(`P:${filterForm.stabilityTiers.join(',')}`)
  return parts.length > 0 ? parts.join(' | ') : '未设置筛选条件'
})
const canSaveMultiConfig = computed(() =>
  selectedMultiStrategies.value.length > 0 &&
  String(multiStrategyForm.taskName || '').trim().length > 0 &&
  String(multiStrategyForm.cronExpression || '').trim().length > 0
)

const persistSelectedMultiStrategies = () => {
  localStorage.setItem(MULTI_STRATEGY_SELECTION_KEY, JSON.stringify(selectedMultiStrategies.value))
}

const restoreSelectedMultiStrategies = () => {
  const raw = localStorage.getItem(MULTI_STRATEGY_SELECTION_KEY)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      selectedMultiStrategies.value = parsed.map(item => String(item || '').trim()).filter(Boolean)
    }
  } catch {
    selectedMultiStrategies.value = []
  }
}

const buildDateRangePayload = () => {
  const [startDate, endDate] = filterForm.dateRange || []
  if (!startDate || !endDate) return {}
  return { startDate, endDate }
}

const buildFilterPayload = () => ({
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
    // 移动端仅允许调用“已保存策略”，未选策略时不带三维条件
    powerDiffs: (selectedStrategyName.value ? filterForm.powerDiffs : []).map(String),
    winPanDiffs: (selectedStrategyName.value ? filterForm.winPanDiffs : []).map(String),
    stabilityTiers: (selectedStrategyName.value ? filterForm.stabilityTiers : []).map(String)
  },
  sort: {
    field: filterForm.sortBy || 'p_level',
    order: filterForm.sortOrder || 'desc'
  },
  page: 1,
  pageSize: 100
})

const toggleFilterValue = (field, value) => {
  const list = filterForm[field]
  const idx = list.indexOf(value)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(value)
  // 手动修改三维条件后，视为未调用已保存策略
  selectedStrategyName.value = ''
}

const resetThreeDimensional = () => {
  filterForm.powerDiffs = []
  filterForm.winPanDiffs = []
  filterForm.stabilityTiers = []
  selectedStrategyName.value = ''
}

const resetAllFilters = () => {
  resetThreeDimensional()
  filterForm.leagues = []
  filterForm.dateTime = ''
  filterForm.dateRange = ['', '']
  filterForm.sortBy = 'p_level'
  filterForm.sortOrder = 'desc'
  selectedLeague.value = ''
  clearStrategySelection()
  currentPage.value = 1
}

const onLeagueChange = () => {
  filterForm.leagues = selectedLeague.value ? [selectedLeague.value] : []
}

const normalizeMatch = (match) => ({
  id: match.id ?? `${match.dateTime || match.date_time || ''}_${match.lineId || match.line_id || ''}`,
  dateTime: match.dateTime ?? match.date_time ?? '',
  matchTime:
    match.match_time ??
    match.matchTime ??
    match.matchTimeStr ??
    match.match_time_str ??
    match?.sourceAttributes?.match_time ??
    match?.sourceAttributes?.matchTime ??
    match?.sourceAttributes?.matchTimeStr ??
    match?.source_attrs?.match_time ??
    match?.source_attrs?.matchTime ??
    match?.source_attrs?.matchTimeStr ??
    '',
  league: match.league,
  homeTeam: match.homeTeam,
  guestTeam: match.guestTeam,
  strength: match.strength,
  winLevel: match.winLevel,
  pLevel: match.pLevel,
  stability: match.stability,
  raw: match
})

const resolveSourceAttrs = (item) => {
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

const safeParseFloat = (value, defaultValue = 0) => {
  const num = Number.parseFloat(value)
  return Number.isNaN(num) ? defaultValue : num
}

const openAnalysis = (row) => {
  const base = row?.raw && typeof row.raw === 'object' ? row.raw : row
  const sourceAttrs = resolveSourceAttrs(base)
  const fromRowOrSource = (keys, defaultValue = '-') => pickField(base, keys, defaultValue, sourceAttrs)

  currentAnalysisData.value = {
    lineId: fromRowOrSource(['line_id', 'lineId']),
    matchTimeStr: fromRowOrSource(['match_time', 'matchTimeStr', 'matchTime']),
    gameShortName: fromRowOrSource(['gameShortName', 'league']),
    homeTeam: fromRowOrSource(['home_team', 'homeTeam']),
    guestTeam: fromRowOrSource(['away_team', 'guestTeam', 'awayTeam']),
    homePower: safeParseFloat(fromRowOrSource(['power_home', 'homePower', 'home_power']), '-'),
    guestPower: safeParseFloat(fromRowOrSource(['power_away', 'guestPower', 'guest_power', 'away_power']), '-'),
    homeWinAward: base?.odds?.homeWin ?? fromRowOrSource(['homeWinAward']),
    drawAward: base?.odds?.draw ?? fromRowOrSource(['drawAward']),
    guestWinAward: base?.odds?.guestWin ?? fromRowOrSource(['guestWinAward']),
    rq: fromRowOrSource(['rq', 'handicap']),
    rawStrength: fromRowOrSource(['strength', 'power_diff']),
    rawWinLevel: fromRowOrSource(['winLevel', 'delta_wp']),
    rawStability: fromRowOrSource(['stability']),
    pLevel: fromRowOrSource(['pLevel', 'p_level']),
    homeFeature: fromRowOrSource(['home_feature', 'homeFeature']),
    guestFeature: fromRowOrSource(['away_feature', 'guestFeature', 'guest_feature']),
    homeSpf: fromRowOrSource(['homeSpf']),
    guestSpf: fromRowOrSource(['guestSpf']),
    jiaoFenDesc: fromRowOrSource(['jiaoFenDesc'], '暂无历史交锋数据'),
    jiaoFenMatch1: fromRowOrSource(['jiaoFenMatch1'], null),
    jiaoFenMatch2: fromRowOrSource(['jiaoFenMatch2'], null),
    jiaoFenMatch3: fromRowOrSource(['jiaoFenMatch3'], null),
    jiaoFenMatch4: fromRowOrSource(['jiaoFenMatch4'], null),
    jiaoFenMatch5: fromRowOrSource(['jiaoFenMatch5'], null),
    jiaoFenMatch6: fromRowOrSource(['jiaoFenMatch6'], null)
  }
  if (!currentAnalysisData.value?.homeTeam && !currentAnalysisData.value?.guestTeam) {
    ElMessage.warning('当前场次缺少分析数据')
  }
  analysisVisible.value = true
}

const getJiaoFenMatches = (data) => {
  if (!data) return []
  const matches = []
  for (let i = 1; i <= 6; i += 1) {
    const key = `jiaoFenMatch${i}`
    if (data[key]) matches.push(data[key])
  }
  return matches
}

const displayValue = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  return value
}

const applyFilter = async () => {
  loading.value = true
  try {
    const response = await request.post('/api/v1/beidan-filter/advanced-filter', buildFilterPayload())
    const matches = Array.isArray(response?.matches) ? response.matches : []
    results.value = matches.map(normalizeMatch)
    statistics.value = response?.statistics || {}
    totalResults.value = Number(
      response?.pagination?.totalItems ??
      response?.pagination?.total_items ??
      response?.statistics?.filteredMatches ??
      response?.statistics?.filtered_matches ??
      results.value.length
    )
    availableLeagues.value = [...new Set(results.value.map(item => item.league).filter(Boolean))]
    currentPage.value = 1
    activeTab.value = 'results'
    ElMessage.success(`筛选完成，共 ${totalResults.value} 场`)
  } catch (error) {
    console.error('applyFilter error:', error)
    const message = error?.response?.data?.detail || error?.message || '筛选失败，请稍后重试'
    ElMessage.error(String(message))
  } finally {
    loading.value = false
  }
}

const fetchRealData = async () => {
  loading.value = true
  try {
    const dateRange = buildDateRangePayload()
    const params = {
      date_time: filterForm.dateTime || '',
      leagues: (filterForm.leagues || []).join(','),
      start_date: dateRange.startDate || '',
      end_date: dateRange.endDate || ''
    }
    const response = await request.get('/api/v1/beidan-filter/real-time-count', { params })
    realTimeMatchCount.value = Number(response?.matchCount || 0)
    ElMessage.success(`实时匹配 ${realTimeMatchCount.value} 场`)
  } catch (error) {
    console.error('fetchRealData error:', error)
    const message = error?.response?.data?.detail || error?.message || '实时数据获取失败'
    ElMessage.error(String(message))
  } finally {
    loading.value = false
  }
}

const refreshDateTimeOptions = async () => {
  try {
    const response = await request.get('/api/v1/beidan-filter/latest-date-times')
    const next = response?.dateTimes || response?.date_times || []
    dateTimeOptions.value = Array.isArray(next) ? next.slice(0, 8) : []
    if (!filterForm.dateTime && dateTimeOptions.value.length > 0) {
      filterForm.dateTime = dateTimeOptions.value[0]
    }
  } catch {
    dateTimeOptions.value = []
  }
}

const normalizeStrategy = (item) => {
  const three = item?.threeDimensional || {}
  const other = item?.otherConditions || {}
  const parseNumArray = (arr) => (Array.isArray(arr) ? arr.map(v => Number(v)).filter(v => !Number.isNaN(v)) : [])
  const parseStrArray = (arr) => (Array.isArray(arr) ? arr.map(v => String(v)) : [])

  return {
    id: item?.id,
    name: item?.name,
    description: item?.description || '',
    powerDiffs: parseNumArray(other.powerDiffs || three.powerDiffs),
    winPanDiffs: parseNumArray(other.winPanDiffs || three.winPanDiffs),
    stabilityTiers: parseStrArray(other.stabilityTiers || three.stabilityTiers),
    leagues: Array.isArray(other.leagues) ? other.leagues : [],
    dateTime: other.dateTime || '',
    sortBy: item?.sort?.field || 'p_level',
    sortOrder: item?.sort?.order || 'desc',
    raw: item
  }
}

const fetchStrategies = async () => {
  try {
    const response = await request.get('/api/v1/beidan-filter/strategies')
    const list = Array.isArray(response?.strategies)
      ? response.strategies
      : (Array.isArray(response) ? response : [])
    strategyList.value = list.map(normalizeStrategy).filter(item => item.name)
    strategyOptionsAll.value = strategyList.value.map(item => item.name)

    if (selectedStrategyName.value && !strategyOptionsAll.value.includes(selectedStrategyName.value)) {
      selectedStrategyName.value = ''
    }

    selectedMultiStrategies.value = selectedMultiStrategies.value.filter(name => strategyOptionsAll.value.includes(name))
    persistSelectedMultiStrategies()
  } catch (error) {
    console.error('fetchStrategies error:', error)
    strategyList.value = []
    strategyOptionsAll.value = []
    ElMessage.error('策略列表加载失败')
  }
}

const applyStrategyByName = async (name, autoApply = false) => {
  const strategy = strategyList.value.find(item => item.name === name)
  if (!strategy) return
  selectedStrategyName.value = name
  filterForm.powerDiffs = [...strategy.powerDiffs]
  filterForm.winPanDiffs = [...strategy.winPanDiffs]
  filterForm.stabilityTiers = [...strategy.stabilityTiers]
  filterForm.leagues = [...strategy.leagues]
  filterForm.dateTime = strategy.dateTime || filterForm.dateTime
  filterForm.sortBy = strategy.sortBy
  filterForm.sortOrder = strategy.sortOrder
  selectedLeague.value = filterForm.leagues[0] || ''
  if (autoApply) await applyFilter()
}

const selectStrategyTag = async (name) => {
  await applyStrategyByName(name, false)
}

const clearStrategySelection = () => {
  selectedStrategyName.value = ''
}

const toggleMultiStrategySelection = (name) => {
  const idx = selectedMultiStrategies.value.indexOf(name)
  if (idx >= 0) selectedMultiStrategies.value.splice(idx, 1)
  else selectedMultiStrategies.value.push(name)
  selectedMultiStrategies.value = [...new Set(selectedMultiStrategies.value)]
  persistSelectedMultiStrategies()
}

const selectAllMultiStrategies = () => {
  selectedMultiStrategies.value = [...new Set(strategyList.value.map(item => item.name).filter(Boolean))]
  persistSelectedMultiStrategies()
}

const clearMultiStrategies = () => {
  selectedMultiStrategies.value = []
  persistSelectedMultiStrategies()
}

const updateCronExpression = () => {
  const map = {
    daily: '0 9 * * *',
    weekly: '0 9 * * 1',
    hourly: '0 * * * *'
  }
  if (multiStrategyForm.cronType !== 'custom') {
    multiStrategyForm.cronExpression = map[multiStrategyForm.cronType] || '0 9 * * *'
  }
}

const getCurrentUserId = () => {
  const username = localStorage.getItem('username')
  if (username) return username
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')
  if (!token) return 'admin'
  try {
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return decoded.username || decoded.sub || 'admin'
  } catch {
    return 'admin'
  }
}

const unwrapApiResponse = (response) => {
  if (Array.isArray(response)) return { success: true, data: response }
  if (!response || typeof response !== 'object') return { success: false, data: null, message: '响应格式不正确' }
  if (Object.prototype.hasOwnProperty.call(response, 'success')) return response
  if (Object.prototype.hasOwnProperty.call(response, 'data')) return { success: true, data: response.data, message: response.message }
  return { success: true, data: response }
}

const saveMultiStrategyConfig = async () => {
  if (!canSaveMultiConfig.value) {
    ElMessage.warning('请先选择策略并填写任务配置')
    return
  }
  multiStrategySaving.value = true
  try {
    const raw = await request.post('/api/multi-strategy/config', {
      task_name: String(multiStrategyForm.taskName || '').trim(),
      strategy_ids: selectedMultiStrategies.value,
      cron_expression: String(multiStrategyForm.cronExpression || '').trim(),
      message_format: multiStrategyForm.messageFormat,
      user_id: getCurrentUserId(),
      dingtalk_webhook: multiStrategyForm.dingtalkEnabled
        ? String(multiStrategyForm.dingtalkWebhook || '').trim()
        : null,
      enabled: true
    })
    const response = unwrapApiResponse(raw)
    if (response.success) {
      ElMessage.success('定时与推送配置保存成功')
      await loadMultiStrategyTasks()
      return
    }
    ElMessage.error(`保存失败: ${response.message || '未知错误'}`)
  } catch (error) {
    ElMessage.error(`保存失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`)
  } finally {
    multiStrategySaving.value = false
  }
}

const loadMultiStrategyTasks = async () => {
  multiStrategyLoadingTasks.value = true
  try {
    const raw = await request.get(`/api/multi-strategy/config?user_id=${getCurrentUserId()}`)
    const response = unwrapApiResponse(raw)
    const taskList = Array.isArray(response?.data) ? response.data : []
    multiStrategyTaskCount.value = taskList.length
  } catch {
    multiStrategyTaskCount.value = 0
  } finally {
    multiStrategyLoadingTasks.value = false
  }
}

const executeMultiStrategyNow = async () => {
  if (selectedMultiStrategies.value.length === 0) {
    ElMessage.warning('请先预选至少一个策略')
    return
  }
  multiStrategyExecuting.value = true
  try {
    const raw = await request.post('/api/multi-strategy/execute', {
      strategy_ids: selectedMultiStrategies.value,
      message_format: multiStrategyForm.messageFormat
    })
    const response = unwrapApiResponse(raw)
    if (response.success) {
      ElMessage.success('多策略筛选已执行，结果已发起推送')
      return
    }
    ElMessage.error(`执行失败: ${response.message || '未知错误'}`)
  } catch (error) {
    ElMessage.error(`执行失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`)
  } finally {
    multiStrategyExecuting.value = false
  }
}

const saveStrategy = async () => {
  const { value } = await ElMessageBox.prompt('请输入策略名称', '保存策略', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputPlaceholder: '例如：今日稳健策略'
  }).catch(() => ({ value: '' }))

  const name = String(value || '').trim()
  if (!name) return

  const duplicated = strategyList.value.some(item => item.name === name)
  if (duplicated) {
    ElMessage.warning('策略名称已存在，请更换后重试')
    return
  }

  try {
    const now = new Date().toISOString()
    await request.post('/api/v1/beidan-filter/strategies', {
      name,
      description: '移动端保存策略',
      threeDimensional: {
        powerDiffs: filterForm.powerDiffs.map(String),
        winPanDiffs: filterForm.winPanDiffs.map(String),
        stabilityTiers: filterForm.stabilityTiers.map(String)
      },
      otherConditions: {
        leagues: filterForm.leagues,
        dateTime: filterForm.dateTime,
        dateRange: buildDateRangePayload(),
        includeDerating: !!filterForm.includeDerating,
        powerDiffs: filterForm.powerDiffs.map(String),
        winPanDiffs: filterForm.winPanDiffs.map(String),
        stabilityTiers: filterForm.stabilityTiers.map(String)
      },
      sort: {
        field: filterForm.sortBy,
        order: filterForm.sortOrder
      },
      createdAt: now,
      updatedAt: now
    })
    ElMessage.success('策略保存成功')
    await fetchStrategies()
  } catch (error) {
    console.error('saveStrategy error:', error)
    const message = error?.response?.data?.detail || error?.message || '保存策略失败'
    ElMessage.error(String(message))
  }
}

const deleteStrategy = async (targetName = '') => {
  const name = targetName || selectedStrategyName.value
  const strategy = strategyList.value.find(item => item.name === name)
  if (!strategy) return

  try {
    await ElMessageBox.confirm(`确定删除策略“${strategy.name}”？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (strategy.id) {
      await request.delete(`/api/v1/beidan-filter/strategies/${strategy.id}`)
    }

    ElMessage.success('策略删除成功')
    if (selectedStrategyName.value === strategy.name) selectedStrategyName.value = ''
    await fetchStrategies()
  } catch (error) {
    if (error !== 'cancel') console.error('deleteStrategy error:', error)
  }
}

const renameStrategy = async (targetName = '') => {
  const nameRef = targetName || selectedStrategyName.value
  const strategy = strategyList.value.find(item => item.name === nameRef)
  if (!strategy) return

  const { value } = await ElMessageBox.prompt('请输入新策略名称', '重命名策略', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputValue: strategy.name
  }).catch(() => ({ value: '' }))

  const nextName = String(value || '').trim()
  if (!nextName || nextName === strategy.name) return

  try {
    await request.post('/api/v1/beidan-filter/strategies', {
      ...(strategy.raw || {}),
      id: strategy.id,
      name: nextName,
      otherConditions: {
        ...(strategy.raw?.otherConditions || {}),
        leagues: strategy.leagues,
        dateTime: strategy.dateTime,
        powerDiffs: strategy.powerDiffs.map(String),
        winPanDiffs: strategy.winPanDiffs.map(String),
        stabilityTiers: strategy.stabilityTiers.map(String)
      },
      sort: {
        field: strategy.sortBy,
        order: strategy.sortOrder
      }
    })
    ElMessage.success('策略重命名成功')
    selectedStrategyName.value = nextName
    await fetchStrategies()
  } catch (error) {
    console.error('renameStrategy error:', error)
  }
}

const exportResults = (format) => {
  if (results.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  const headers = ['id', 'matchTime', 'league', 'homeTeam', 'guestTeam', 'strength', 'winLevel', 'pLevel', 'stability']
  let content = ''
  let fileType = 'text/plain;charset=utf-8'
  let ext = format

  if (format === 'json') {
    content = JSON.stringify(results.value, null, 2)
    fileType = 'application/json;charset=utf-8'
  } else {
    const csv = [
      headers.join(','),
      ...results.value.map(item => headers.map(key => JSON.stringify(item[key] ?? '')).join(','))
    ].join('\n')
    content = csv
    fileType = 'text/csv;charset=utf-8'
    if (format === 'excel') ext = 'xlsx'
  }

  const blob = new Blob(['\ufeff' + content], { type: fileType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `beidan_mobile_${Date.now()}.${ext}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
  ElMessage.success(`${format.toUpperCase()} 导出成功`)
}

onMounted(async () => {
  restoreSelectedMultiStrategies()
  await Promise.all([refreshDateTimeOptions(), fetchStrategies()])
  await fetchRealData()
  await loadMultiStrategyTasks()
  if (!multiStrategyForm.taskName) {
    multiStrategyForm.taskName = '北单多策略筛选任务'
  }
})
</script>

<style scoped>
.mobile-beidan-page {
  --bg: #f3f5fb;
  --card: #ffffff;
  --text: #111827;
  --muted: #6b7280;
  --line: #e5e7eb;
  --primary: #3b6eea;
  --primary-soft: #e9f0ff;
  --danger: #dc2626;
  position: relative;
  height: 100vh;
  min-height: 100vh;
  background: radial-gradient(120% 120% at 50% -10%, #dfe9ff 0%, var(--bg) 50%, #f7f9ff 100%);
  color: var(--text);
  font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", "Helvetica Neue", sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mobile-beidan-page::before,
.mobile-beidan-page::after {
  content: "";
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
  filter: blur(48px);
  opacity: 0.45;
}

.mobile-beidan-page::before {
  width: 240px;
  height: 240px;
  top: -110px;
  right: -90px;
  background: #c7dcff;
}

.mobile-beidan-page::after {
  width: 200px;
  height: 200px;
  left: -90px;
  bottom: 70px;
  background: #d9e9ff;
}

.top-header {
  position: sticky;
  top: 0;
  z-index: 12;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 14px 12px;
  border-bottom: 1px solid rgba(219, 228, 243, 0.85);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.88));
  backdrop-filter: blur(14px);
}

.top-header h1 {
  margin: 0;
  font-size: 19px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.top-header p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 12px;
}

.content-wrap {
  position: relative;
  z-index: 1;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  padding: 12px 12px calc(114px + env(safe-area-inset-bottom, 0px));
  display: grid;
  gap: 12px;
}

.card {
  background: var(--card);
  border: 1px solid #e4e9f2;
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 10px 28px rgba(36, 52, 86, 0.08);
}

.card h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.1px;
}

.sub {
  margin: 5px 0 10px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
}

.grid-block {
  margin-bottom: 12px;
}

.grid-block label {
  display: block;
  margin-bottom: 7px;
  font-size: 12px;
  font-weight: 700;
  color: #374151;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  min-height: 34px;
  min-width: 34px;
  border: 1px solid #d8deea;
  border-radius: 999px;
  padding: 0 11px;
  background: #f8faff;
  color: #374151;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  transition: all 0.18s ease;
}

.chip.active {
  border-color: var(--primary);
  background: linear-gradient(180deg, #eaf1ff, #dbe8ff);
  color: #2453c7;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(59, 110, 234, 0.16);
}

.chip:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.metric-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 13px;
  border-radius: 14px;
  background: linear-gradient(135deg, #edf3ff, #f2f8ff);
  border: 1px solid #d8e5ff;
  margin-bottom: 12px;
}

.metric-panel strong {
  font-size: 24px;
  color: #2a5dd4;
}

.select-input {
  width: 100%;
  min-height: 40px;
  font-size: 13px;
  border: 1px solid #d6deea;
  border-radius: 11px;
  padding: 0 12px;
  background: #fff;
  box-sizing: border-box;
  color: #0f172a;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.select-input:focus {
  outline: none;
  border-color: #9dbcf7;
  box-shadow: 0 0 0 3px rgba(77, 129, 236, 0.16);
}

.webhook-input {
  min-height: 82px;
  padding: 10px;
  resize: vertical;
  line-height: 1.4;
}

.date-input {
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.date-input::-webkit-datetime-edit {
  font-family: inherit;
  letter-spacing: 0.2px;
}

.dual-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.action-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.action-row > .primary-btn:first-child:last-child,
.action-row > .secondary-btn:first-child:last-child,
.action-row > .danger-btn:first-child:last-child {
  grid-column: 1 / -1;
}

.output-action-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 2px;
}

.output-action-row .primary-btn,
.output-action-row .secondary-btn,
.output-action-row .danger-btn {
  width: 100%;
}

.output-action-wide {
  grid-column: 1 / -1;
}

button {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.primary-btn,
.secondary-btn,
.danger-btn,
.ghost-btn {
  min-height: 40px;
  border-radius: 12px;
  padding: 0 12px;
  border: 1px solid #d2d9e6;
  transition: all 0.18s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #4b7af2, #3b6eea);
  border-color: #3b6eea;
  color: #fff;
  box-shadow: 0 8px 16px rgba(59, 110, 234, 0.25);
}

.secondary-btn,
.ghost-btn {
  background: #f4f6fb;
  border-color: #d4dae6;
  color: #1f2937;
}

.danger-btn {
  background: #ffe8e8;
  border-color: #ffd0d0;
  color: var(--danger);
}

.primary-btn:active,
.secondary-btn:active,
.danger-btn:active,
.ghost-btn:active {
  transform: translateY(1px) scale(0.995);
}

.primary-btn:disabled,
.secondary-btn:disabled,
.danger-btn:disabled,
.ghost-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
  margin-bottom: 11px;
}

.stat-box {
  border: 1px solid #e1e7f1;
  border-radius: 14px;
  padding: 11px;
  background: linear-gradient(180deg, #f9fbff, #f3f7ff);
}

.stat-box span {
  font-size: 12px;
  color: var(--muted);
}

.stat-box strong {
  display: block;
  margin-top: 3px;
  font-size: 20px;
}

.empty {
  color: var(--muted);
  padding: 14px 0;
}

.result-list {
  display: grid;
  gap: 10px;
}

.result-summary {
  margin-bottom: 10px;
  border: 1px solid #e4e9f2;
  background: #f8fafd;
  border-radius: 12px;
  padding: 9px 11px;
  font-size: 12px;
  color: #425066;
  line-height: 1.45;
}

.result-card {
  border: 1px solid #e1e7f1;
  border-radius: 14px;
  padding: 11px;
  background: #fff;
  box-shadow: 0 4px 14px rgba(37, 54, 85, 0.06);
}

.result-card.clickable {
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}

.result-card.clickable:active {
  transform: scale(0.99);
}

.result-card.clickable:hover {
  border-color: #93c5fd;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.12);
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.row.top span {
  color: var(--muted);
  font-size: 12px;
}

.teams {
  margin: 6px 0;
  font-weight: 700;
}

.row.tags span {
  font-size: 11px;
  background: #eff4ff;
  color: #34549e;
  border-radius: 999px;
  padding: 4px 9px;
}

.manage-list {
  display: grid;
  gap: 8px;
}

.manage-item {
  border: 1px solid #e3e8f2;
  border-radius: 12px;
  padding: 11px;
  background: #fbfcff;
}

.manage-name {
  font-weight: 700;
  margin-bottom: 8px;
}

.manage-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.multi-check {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #334155;
  margin-bottom: 8px;
}

.pager-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 10px;
}

.pager-row span {
  font-size: 12px;
  color: var(--muted);
}

.mobile-analysis-dialog :deep(.el-dialog) {
  margin: 0 auto;
  max-height: 96vh;
  border-radius: 16px;
}

.mobile-analysis-dialog :deep(.el-dialog__header) {
  padding: 14px 44px 10px 16px;
}

.mobile-analysis-dialog :deep(.el-dialog__title) {
  font-size: 16px;
  font-weight: 800;
  color: #111827;
}

.mobile-analysis-dialog :deep(.el-dialog__headerbtn) {
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  border: 1px solid #d8dfeb;
  background: #f5f7fc;
  color: #4b5563;
  transition: all 0.18s ease;
}

.mobile-analysis-dialog :deep(.el-dialog__headerbtn:hover) {
  background: #eaf0ff;
  border-color: #b7caf8;
  color: #315ecf;
}

.mobile-analysis-dialog :deep(.el-dialog__close) {
  font-size: 14px;
  font-weight: 700;
}

.mobile-analysis-dialog :deep(.el-dialog__body) {
  padding-top: 8px;
  max-height: calc(96vh - 120px);
  overflow-y: auto;
}

:deep(.el-dialog__headerbtn) {
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  border: 1px solid #d8dfeb;
  background: #f5f7fc;
  color: #4b5563;
  transition: all 0.18s ease;
}

:deep(.el-dialog__headerbtn:hover) {
  background: #eaf0ff;
  border-color: #b7caf8;
  color: #315ecf;
}

.analysis-mobile-wrap {
  display: grid;
  gap: 10px;
}

.analysis-mobile-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
  background: #f8fbff;
}

.analysis-mobile-card h3 {
  margin: 0 0 8px;
  font-size: 14px;
}

.analysis-kv {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.analysis-kv div {
  background: #fff;
  border: 1px solid #dbe2ef;
  border-radius: 10px;
  padding: 8px;
}

.analysis-kv span {
  display: block;
  font-size: 11px;
  color: var(--muted);
}

.analysis-kv strong {
  display: block;
  margin-top: 3px;
  font-size: 13px;
  color: #0f172a;
  line-height: 1.35;
}

.analysis-desc {
  margin: 0 0 8px;
  color: #334155;
  font-size: 13px;
  line-height: 1.5;
}

.history-list {
  display: grid;
  gap: 6px;
}

.history-item {
  font-size: 12px;
  color: #334155;
  border: 1px solid #e2e8f2;
  border-radius: 11px;
  background: #fff;
  padding: 8px;
}

.bottom-nav {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  z-index: 40;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 8px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #dfe6f3;
  backdrop-filter: blur(16px);
  box-shadow: 0 14px 32px rgba(27, 43, 72, 0.18);
}

.nav-btn {
  min-height: 52px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: transparent;
  color: #708097;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  touch-action: manipulation;
}

.nav-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e1;
}

.nav-btn.active {
  color: #2f5fda;
  background: linear-gradient(180deg, #edf3ff, #dbe8ff);
  border-color: #a7c1f8;
  box-shadow: 0 6px 14px rgba(63, 113, 230, 0.2);
}

.nav-btn.active .nav-dot {
  background: #2563eb;
}

@media (max-width: 430px) {
  .top-header {
    padding: 13px 12px 11px;
  }

  .top-header h1 {
    font-size: 18px;
  }

  .card {
    border-radius: 16px;
    padding: 12px;
  }

  .dual-grid {
    grid-template-columns: 1fr;
  }

  .analysis-kv {
    grid-template-columns: 1fr;
  }

  .action-row {
    grid-template-columns: 1fr;
  }

  .output-action-row {
    grid-template-columns: 1fr;
  }

  .output-action-wide {
    grid-column: auto;
  }
}
</style>
