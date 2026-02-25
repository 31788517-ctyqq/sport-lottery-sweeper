<template>
  <div class="schedule-management" :class="themeClass">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div class="title-wrap">
            <div class="mode-chip">{{ modeLabel }}</div>
            <h3>{{ title }}</h3>
            <p class="subtitle">{{ subtitle }}</p>
          </div>
          <div class="header-actions">
            <el-date-picker
              v-if="isJczq || isBd"
              v-model="crawlDate"
              type="date"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              placeholder="赛程日期"
              style="width: 150px"
            />
            <el-button v-if="isJczq" type="primary" :loading="crawlLoading" @click="fetchFrom500w">
              从500W获取竞彩赛程
            </el-button>
            <el-button v-if="isBd" type="primary" :loading="crawlLoading" @click="fetchFromYingqiuBd">
              从盈球获取北单赛程
            </el-button>
            <el-button :icon="Refresh" @click="refreshData">刷新</el-button>
          </div>
        </div>
      </template>

      <el-form :model="queryParams" inline class="search-form">
        <el-form-item label="赛事">
          <el-select
            v-model="queryParams.leagueName"
            placeholder="选择赛事"
            clearable
            filterable
            :loading="leagueOptionsLoading"
            style="width: 220px"
          >
            <el-option
              v-for="league in leagueOptions"
              :key="league"
              :label="league"
              :value="league"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isBd" label="北单期号">
          <el-select
            v-model="queryParams.issueNo"
            placeholder="如26026"
            clearable
            filterable
            allow-create
            default-first-option
            :loading="issueOptionsLoading"
            style="width: 180px"
          >
            <el-option
              v-for="issue in issueOptions"
              :key="issue"
              :label="issue"
              :value="issue"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="赛程日期">
          <el-date-picker
            v-model="queryParams.matchDate"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Delete" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="view-hint">{{ viewHint }}</div>

      <el-table :data="scheduleList" v-loading="loading" stripe height="560" style="width: 100%">
        <el-table-column prop="number" label="编号" width="90" />
        <el-table-column prop="leagueName" label="赛事" width="130" show-overflow-tooltip />
        <el-table-column prop="matchTime" label="开赛时间" width="170" />
        <el-table-column v-if="isBd" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag class="status-tag" :type="getStatusTagType(row.statusText)" effect="light" round>
              {{ row.statusText }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isBd" label="比分/半场" width="120" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.score }}</span>
              <span class="sub">{{ row.halftimeScore }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="homeTeam" label="主队" min-width="150" show-overflow-tooltip />
        <el-table-column v-if="isJczq" prop="score" label="比分" width="90" align="center">
          <template #default="{ row }">
            <span class="score-text">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="awayTeam" label="客队" min-width="150" show-overflow-tooltip />
        <el-table-column label="让球" width="90" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.handicap0 }}</span>
              <span class="sub">{{ row.handicap }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="胜" width="98" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.oddsNspfWin }}</span>
              <span v-if="isJczq || isBd" class="sub">{{ row.oddsSpfWin }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="平" width="98" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.oddsNspfDraw }}</span>
              <span v-if="isJczq || isBd" class="sub">{{ row.oddsSpfDraw }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="负" width="98" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.oddsNspfLose }}</span>
              <span v-if="isJczq || isBd" class="sub">{{ row.oddsSpfLose }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column v-if="isJczq || isBd" label="其它" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" plain size="small" class="other-odds-btn" @click="openOtherOdds(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        style="margin-top: 16px; text-align: center"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog
      v-model="otherOddsVisible"
      title="其它"
      width="980px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="otherOddsActiveTab" class="other-odds-tabs">
        <el-tab-pane label="欧指数" name="eu" />
        <el-tab-pane label="让球" name="asia" />
        <el-tab-pane label="进球数" name="goals" />
      </el-tabs>

      <el-table
        v-if="otherOddsActiveTab === 'eu'"
        :data="otherOddsEuRows"
        v-loading="otherOddsLoading"
        stripe
        max-height="480"
      >
        <el-table-column prop="company" label="公司" min-width="220" show-overflow-tooltip />
        <el-table-column prop="updatedAt" label="更新时间" width="170" />
        <el-table-column prop="initWin" label="初赔胜" width="90" align="center" />
        <el-table-column prop="initDraw" label="初赔平" width="90" align="center" />
        <el-table-column prop="initLose" label="初赔负" width="90" align="center" />
        <el-table-column prop="instantWin" label="即时胜" width="90" align="center" />
        <el-table-column prop="instantDraw" label="即时平" width="90" align="center" />
        <el-table-column prop="instantLose" label="即时负" width="90" align="center" />
      </el-table>

      <el-table
        v-else-if="otherOddsActiveTab === 'asia'"
        :data="otherOddsAsiaRows"
        v-loading="otherOddsLoading"
        stripe
        max-height="480"
      >
        <el-table-column prop="company" label="公司" min-width="180" show-overflow-tooltip />
        <el-table-column prop="updatedAt" label="更新时间" width="170" />
        <el-table-column prop="initHome" label="初盘主" width="90" align="center" />
        <el-table-column prop="initHandicap" label="初盘让球" width="100" align="center" />
        <el-table-column prop="initAway" label="初盘客" width="90" align="center" />
        <el-table-column prop="instantHome" label="即盘主" width="90" align="center" />
        <el-table-column prop="instantHandicap" label="即盘让球" width="100" align="center" />
        <el-table-column prop="instantAway" label="即盘客" width="90" align="center" />
        <el-table-column prop="trend" label="走势" width="80" align="center" />
      </el-table>

      <el-table
        v-else
        :data="otherOddsGoalsRows"
        v-loading="otherOddsLoading"
        stripe
        max-height="480"
      >
        <el-table-column prop="company" label="公司" min-width="180" show-overflow-tooltip />
        <el-table-column prop="updatedAt" label="更新时间" width="170" />
        <el-table-column prop="initBig" label="初盘大" width="90" align="center" />
        <el-table-column prop="initLine" label="初盘进球数" width="110" align="center" />
        <el-table-column prop="initSmall" label="初盘小" width="90" align="center" />
        <el-table-column prop="instantBig" label="即盘大" width="90" align="center" />
        <el-table-column prop="instantLine" label="即盘进球数" width="110" align="center" />
        <el-table-column prop="instantSmall" label="即盘小" width="90" align="center" />
        <el-table-column prop="trend" label="走势" width="80" align="center" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Refresh, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

const props = defineProps({
  scheduleType: {
    type: String,
    default: 'jczq'
  }
})

const API_BASE = '/api/v1/admin/lottery-schedules'
const isJczq = computed(() => props.scheduleType === 'jczq')
const isBd = computed(() => props.scheduleType === 'bd')
const themeClass = computed(() => (isJczq.value ? 'theme-jczq' : 'theme-bd'))
const modeLabel = computed(() => (isJczq.value ? 'JZ 竞彩模式' : 'BD 北单模式'))
const viewHint = computed(() =>
  isJczq.value
    ? '竞彩视图：聚焦胜平负赔率与比分，适合快速看盘。'
    : '北单视图：聚焦状态、比分/半场与北单SP，适合赛果追踪。'
)

const title = computed(() => (isJczq.value ? '竞彩赛程管理' : '北单赛程管理'))
const subtitle = computed(() => (isJczq.value ? '支持按日期从500W抓取竞彩赛程并入库' : '支持按日期从盈球抓取北单赛程并入库'))

const scheduleList = ref([])
const loading = ref(false)
const crawlLoading = ref(false)
const leagueOptions = ref([])
const leagueOptionsLoading = ref(false)
const issueOptions = ref([])
const issueOptionsLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const crawlDate = ref(new Date().toISOString().slice(0, 10))
const otherOddsVisible = ref(false)
const otherOddsLoading = ref(false)
const otherOddsActiveTab = ref('eu')
const otherOddsEuRows = ref([])
const otherOddsAsiaRows = ref([])
const otherOddsGoalsRows = ref([])
let leagueOptionsRequestSeq = 0

const queryParams = reactive({
  leagueName: '',
  matchDate: '',
  issueNo: ''
})

const formatOdds = (v) => {
  if (v === null || v === undefined || v === '') return '-'
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : String(v)
}

const formatText = (v) => {
  const text = String(v ?? '').trim()
  return text || '-'
}

const formatMatchTime = (v) => {
  if (!v) return '-'
  const s = String(v).replace('T', ' ')
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})/)
  if (m) return `${m[2]}-${m[3]} ${m[4]}:${m[5]}`
  return s
}

const formatStatus = (status, statusDes) => {
  const s = String(status || '').toLowerCase()
  if (s === 'pending') return '未开赛'
  if (s === 'running') return '比赛中'
  if (s === 'finished') return '已完成'
  if (s === 'cancelled') return '已完成'
  const raw = String(statusDes || '')
  if (raw.includes('未开')) return '未开赛'
  if (raw.includes('完场') || raw.includes('已结束') || raw.includes('已完成')) return '已完成'
  if (raw.includes('中场') || raw.includes('进行')) return '比赛中'
  return '-'
}

const normalizeScore = (value) => {
  const text = String(value || '').trim()
  if (!text || text === '-' || text.toLowerCase() === 'null' || text.toLowerCase() === 'none') return '-'
  const m = text.match(/(\d+)\s*[-:：]\s*(\d+)/)
  if (m) return `${m[1]}-${m[2]}`
  return text
}

const hasBdHandicapLine = (value) => {
  const text = String(value ?? '').trim()
  return Boolean(text && text !== '-')
}

const shouldResolveBdIssue = (value) => {
  const text = String(value ?? '').trim()
  if (!text) return true
  return /^\d{5}$/.test(text)
}

const buildScheduleQuery = ({ includePagination = true } = {}) => {
  const params = {
    schedule_type: props.scheduleType
  }
  if (includePagination) {
    params.page = currentPage.value
    params.size = pageSize.value
  }
  if (queryParams.leagueName) {
    params.league_name = queryParams.leagueName
  }
  if (queryParams.matchDate) {
    params.date_from = queryParams.matchDate
    params.date_to = queryParams.matchDate
  }
  if (isBd.value) {
    const issueNo = String(queryParams.issueNo || '').trim()
    if (/^\d{5}$/.test(issueNo)) {
      params.issue_no = issueNo
    }
  }
  return params
}

const getStatusTagType = (statusText) => {
  const text = String(statusText || '')
  if (text.includes('已完成')) return 'success'
  if (text.includes('比赛中')) return 'warning'
  if (text.includes('未开赛')) return 'info'
  return 'info'
}

const mapJczqRow = (row) => ({
  id: row.id,
  number: row.number || '-',
  leagueName: row.league_name || '-',
  matchTime: formatMatchTime(row.match_time),
  homeTeam: row.home_team || '-',
  score: normalizeScore(row.score ?? row.full_score ?? row.score_full),
  awayTeam: row.away_team || '-',
  handicap0: row.handicap_0 || '0',
  handicap: row.handicap || '-',
  oddsNspfWin: formatOdds(row.odds_nspf_win ?? row.odds_win),
  oddsNspfDraw: formatOdds(row.odds_nspf_draw ?? row.odds_draw),
  oddsNspfLose: formatOdds(row.odds_nspf_lose ?? row.odds_lose),
  oddsSpfWin: formatOdds(row.odds_spf_win),
  oddsSpfDraw: formatOdds(row.odds_spf_draw),
  oddsSpfLose: formatOdds(row.odds_spf_lose)
})

const mapBdRow = (row) => ({
  ...mapJczqRow(row),
  // 优先使用后端归一化文案，兜底再前端归一
  statusText:
    row.status_text && row.status_text !== '-'
      ? row.status_text
      : formatStatus(row.status, row.status_des),
  score: normalizeScore(row.score ?? row.full_score ?? row.score_full),
  halftimeScore: normalizeScore(row.halftime_score ?? row.half_score ?? row.halfTimeScore),
  // 北单显示双行SP：与让球0/让球值两行对齐，真实SP放到匹配让球值那一行，另一行显示"-"
  oddsNspfWin: hasBdHandicapLine(row.handicap) ? '-' : formatOdds(row.odds_nspf_win),
  oddsNspfDraw: hasBdHandicapLine(row.handicap) ? '-' : formatOdds(row.odds_nspf_draw),
  oddsNspfLose: hasBdHandicapLine(row.handicap) ? '-' : formatOdds(row.odds_nspf_lose),
  oddsSpfWin: hasBdHandicapLine(row.handicap) ? formatOdds(row.odds_nspf_win) : '-',
  oddsSpfDraw: hasBdHandicapLine(row.handicap) ? formatOdds(row.odds_nspf_draw) : '-',
  oddsSpfLose: hasBdHandicapLine(row.handicap) ? formatOdds(row.odds_nspf_lose) : '-'
})

const compareByMatchNumber = (a, b) => {
  const na = String(a?.number || '').trim()
  const nb = String(b?.number || '').trim()

  if (!na || na === '-') return !nb || nb === '-' ? 0 : 1
  if (!nb || nb === '-') return -1

  const cmp = na.localeCompare(nb, 'zh-Hans-CN', { numeric: true, sensitivity: 'base' })
  if (cmp !== 0) return cmp
  return String(a?.matchTime || '').localeCompare(String(b?.matchTime || ''))
}

const getScheduleList = async () => {
  loading.value = true
  try {
    const params = buildScheduleQuery({ includePagination: true })
    const data = await request.get(`${API_BASE}/`, { params })
    const mapper = isBd.value ? mapBdRow : mapJczqRow
    const mapped = (data.items || []).map(mapper)
    if (isJczq.value) {
      mapped.sort(compareByMatchNumber)
    }
    scheduleList.value = mapped
    total.value = data.total || 0
  } catch (error) {
    console.error('加载赛程失败:', error)
    ElMessage.error('加载赛程失败')
  } finally {
    loading.value = false
  }
}

const getLeagueOptions = async () => {
  if (isBd.value && !shouldResolveBdIssue(queryParams.issueNo)) return
  const requestSeq = ++leagueOptionsRequestSeq
  leagueOptionsLoading.value = true
  try {
    const params = buildScheduleQuery({ includePagination: false })
    delete params.league_name
    const data = await request.get(`${API_BASE}/league-options`, {
      params,
      suppressErrorMessage: true
    })
    if (requestSeq !== leagueOptionsRequestSeq) return
    leagueOptions.value = Array.isArray(data?.items) ? data.items : []
    if (queryParams.leagueName && !leagueOptions.value.includes(queryParams.leagueName)) {
      queryParams.leagueName = ''
    }
  } catch (error) {
    console.error('加载赛事选项失败:', error)
    if (requestSeq === leagueOptionsRequestSeq) {
      leagueOptions.value = []
    }
  } finally {
    if (requestSeq === leagueOptionsRequestSeq) {
      leagueOptionsLoading.value = false
    }
  }
}

const getIssueOptions = async () => {
  if (!isBd.value) {
    issueOptions.value = []
    return
  }
  issueOptionsLoading.value = true
  try {
    const data = await request.get(`${API_BASE}/issue-options`, {
      params: { count: 3 },
      suppressErrorMessage: true
    })
    issueOptions.value = Array.isArray(data?.items) ? data.items : []
  } catch (error) {
    console.error('加载北单期号选项失败:', error)
    issueOptions.value = []
  } finally {
    issueOptionsLoading.value = false
  }
}

const fetchFrom500w = async () => {
  if (!crawlDate.value) {
    ElMessage.warning('请先选择赛程日期')
    return
  }
  crawlLoading.value = true
  try {
    const result = await request.post(`${API_BASE}/import/500w`, null, {
      params: { schedule_date: crawlDate.value }
    })
    ElMessage.success(result?.message || `已抓取 ${crawlDate.value} 赛程`)
    currentPage.value = 1
    queryParams.matchDate = crawlDate.value
    await Promise.all([getLeagueOptions(), getScheduleList()])
  } catch (error) {
    console.error('500W抓取失败:', error)
    ElMessage.error('500W抓取失败')
  } finally {
    crawlLoading.value = false
  }
}

const fetchFromYingqiuBd = async () => {
  if (!crawlDate.value) {
    ElMessage.warning('请先选择赛程日期')
    return
  }
  crawlLoading.value = true
  try {
    const result = await request.post(`${API_BASE}/import/yingqiu-bd`, null, {
      params: { schedule_date: crawlDate.value },
      timeout: 120000
    })
    ElMessage.success(result?.message || `已抓取 ${crawlDate.value} 北单赛程`)
    currentPage.value = 1
    queryParams.matchDate = crawlDate.value
    await Promise.all([getLeagueOptions(), getScheduleList()])
  } catch (error) {
    console.error('盈球北单抓取失败:', error)
    if (error?.code === 'ECONNABORTED' || String(error?.message || '').includes('timeout')) {
      ElMessage.error('盈球抓取耗时较长，请稍后刷新列表查看结果')
      return
    }
    const msg = error?.response?.data?.error?.message || error?.response?.data?.detail || '盈球北单抓取失败'
    ElMessage.error(msg)
  } finally {
    crawlLoading.value = false
  }
}

const openOtherOdds = async (row) => {
  otherOddsVisible.value = true
  otherOddsLoading.value = true
  otherOddsActiveTab.value = 'eu'
  otherOddsEuRows.value = []
  otherOddsAsiaRows.value = []
  otherOddsGoalsRows.value = []
  try {
    const data = await request.get(`${API_BASE}/${row.id}/other-odds`, {
      // 北单详情优先实时抓取，避免历史缓存导致标签页数据缺失或错位
      params: { force_refresh: isBd.value },
      timeout: 60000
    })
    const tabs = data.tabs || {}
    const euRows = tabs.eu || data.items || []
    const asiaRows = tabs.asia || []
    const goalsRows = tabs.goals || []

    otherOddsEuRows.value = euRows.map((x) => ({
      company: x.company || '-',
      updatedAt: x.updated_at || '-',
      initWin: formatOdds(x.init_win),
      initDraw: formatOdds(x.init_draw),
      initLose: formatOdds(x.init_lose),
      instantWin: formatOdds(x.instant_win),
      instantDraw: formatOdds(x.instant_draw),
      instantLose: formatOdds(x.instant_lose)
    }))

    otherOddsAsiaRows.value = asiaRows.map((x) => ({
      company: x.company || '-',
      updatedAt: x.updated_at || '-',
      initHome: formatOdds(x.init_home),
      initHandicap: formatText(x.init_handicap),
      initAway: formatOdds(x.init_away),
      instantHome: formatOdds(x.instant_home),
      instantHandicap: formatText(x.instant_handicap),
      instantAway: formatOdds(x.instant_away),
      trend: formatText(x.trend)
    }))

    otherOddsGoalsRows.value = goalsRows.map((x) => ({
      company: x.company || '-',
      updatedAt: x.updated_at || '-',
      initBig: formatOdds(x.init_big),
      initLine: formatText(x.init_line),
      initSmall: formatOdds(x.init_small),
      instantBig: formatOdds(x.instant_big),
      instantLine: formatText(x.instant_line),
      instantSmall: formatOdds(x.instant_small),
      trend: formatText(x.trend)
    }))

    if (!otherOddsEuRows.value.length && otherOddsAsiaRows.value.length) {
      otherOddsActiveTab.value = 'asia'
    } else if (
      !otherOddsEuRows.value.length &&
      !otherOddsAsiaRows.value.length &&
      otherOddsGoalsRows.value.length
    ) {
      otherOddsActiveTab.value = 'goals'
    }
  } catch (error) {
    console.error('加载其它赔率失败:', error)
    if (error?.code === 'ECONNABORTED' || String(error?.message || '').includes('timeout')) {
      ElMessage.error('加载其它赔率超时，请稍后重试')
      return
    }
    ElMessage.error(error?.response?.data?.detail || '加载其它赔率失败')
  } finally {
    otherOddsLoading.value = false
  }
}

const handleQuery = () => {
  currentPage.value = 1
  Promise.all([getLeagueOptions(), getScheduleList()])
}

const resetQuery = () => {
  queryParams.leagueName = ''
  queryParams.matchDate = ''
  queryParams.issueNo = ''
  currentPage.value = 1
  getLeagueOptions()
  getScheduleList()
}

const refreshData = () => {
  Promise.all([getLeagueOptions(), getScheduleList()])
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  getScheduleList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  getScheduleList()
}

onMounted(() => {
  queryParams.matchDate = crawlDate.value
  getIssueOptions()
  getLeagueOptions()
  getScheduleList()
})

watch(
  () => props.scheduleType,
  () => {
    // 同组件复用时，按类型切换后重置查询和列表，避免串页
    scheduleList.value = []
    total.value = 0
    currentPage.value = 1
    queryParams.leagueName = ''
    queryParams.matchDate = crawlDate.value
    queryParams.issueNo = ''
    getIssueOptions()
    getLeagueOptions()
    getScheduleList()
  }
)

watch(
  () => [queryParams.matchDate, queryParams.issueNo, props.scheduleType],
  () => {
    getLeagueOptions()
  }
)
</script>

<style scoped>
.schedule-management {
  --theme-primary: #2563eb;
  --theme-soft: #eef4ff;
  --theme-border: #dbe8ff;
  --theme-head-bg: linear-gradient(90deg, #eaf2ff 0%, #ffffff 100%);
  --theme-text: #1d4ed8;
  --theme-hint-bg: #edf4ff;
  --theme-hint-text: #1e3a8a;
  padding: 20px;
}

.schedule-management.theme-bd {
  --theme-primary: #d97706;
  --theme-soft: #fff7ea;
  --theme-border: #f7ddb4;
  --theme-head-bg: linear-gradient(90deg, #fff0d8 0%, #ffffff 100%);
  --theme-text: #b45309;
  --theme-hint-bg: #fff4e3;
  --theme-hint-text: #9a3412;
}

.card-container {
  border: 1px solid var(--theme-border);
  background: linear-gradient(180deg, var(--theme-soft) 0, #ffffff 220px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.title-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mode-chip {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 2px 10px;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  background: #ffffff;
  color: var(--theme-text);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.subtitle {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-form {
  margin-bottom: 12px;
}

.view-hint {
  margin: 0 0 10px;
  padding: 8px 12px;
  border: 1px solid var(--theme-border);
  border-radius: 10px;
  background: var(--theme-hint-bg);
  color: var(--theme-hint-text);
  font-size: 12px;
  line-height: 1.4;
}

.score-text {
  color: #dc2626;
  font-weight: 700;
}

.status-tag {
  min-width: 68px;
  justify-content: center;
  font-weight: 600;
}

.dual-line {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.dual-line .sub {
  color: #16a34a;
}

.other-odds-btn {
  min-width: 58px;
}

.other-odds-tabs {
  margin-bottom: 10px;
}

:deep(.el-card__header) {
  background: var(--theme-head-bg);
  border-bottom: 1px solid var(--theme-border);
}

:deep(.el-table th.el-table__cell) {
  background: var(--theme-soft);
  color: #374151;
}

:deep(.el-button--primary) {
  background-color: var(--theme-primary);
  border-color: var(--theme-primary);
}

:deep(.el-button--primary.is-plain) {
  color: var(--theme-primary);
  border-color: var(--theme-border);
  background-color: #fff;
}

@media (max-width: 900px) {
  .schedule-management {
    padding: 12px;
  }
}
</style>
