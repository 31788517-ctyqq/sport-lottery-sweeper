<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>1-1比分预测扫盘</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleFetch" :loading="fetching">手动抓取并计算</el-button>
          </div>
        </div>
      </template>

      <div class="card-content">
        <div class="toolbar">
          <el-date-picker
            v-model="queryDate"
            type="date"
            placeholder="选择日期"
            style="width: 180px"
            value-format="YYYY-MM-DD"
          />
          <el-select v-model="dataSource" placeholder="数据源" style="width: 160px" disabled>
            <el-option label="盈球北单（详情赔率）" value="yingqiu_bd" />
          </el-select>
          <el-select
            v-model="queryIssueNo"
            placeholder="如26026"
            clearable
            filterable
            allow-create
            default-first-option
            :loading="issueOptionsLoading"
            style="width: 150px"
          >
            <el-option
              v-for="issue in issueOptions"
              :key="issue"
              :label="issue"
              :value="issue"
            />
          </el-select>
          <el-select
            v-model="queryLeague"
            placeholder="选择赛事"
            clearable
            filterable
            :loading="leagueOptionsLoading"
            style="width: 180px"
          >
            <el-option
              v-for="league in leagueOptions"
              :key="league"
              :label="league"
              :value="league"
            />
          </el-select>
          <el-button type="primary" @click="handleQuery" :loading="loading">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>

        <div v-if="fetching" class="fetch-progress">
          <el-progress
            :percentage="Math.round(fetchTaskProgress)"
            :stroke-width="12"
            :status="fetchTaskStatus === 'failed' ? 'exception' : (fetchTaskStatus === 'success' ? 'success' : '')"
          />
          <div class="fetch-progress-text">{{ fetchTaskMessage || '处理中...' }}</div>
        </div>

        <el-table :key="tableKey" :data="tableData" border style="width: 100%; margin-top: 20px" :loading="loading">
          <el-table-column prop="number" label="编号" width="90" />
          <el-table-column prop="match_time" label="比赛时间" width="160" :formatter="formatDateTime" />
          <el-table-column prop="league" label="赛事" width="120" />
          <el-table-column prop="home_team" label="主队" />
          <el-table-column prop="away_team" label="客队" />
          <el-table-column prop="mu_total" label="μT" width="90" :formatter="formatNumber" />
          <el-table-column prop="mu_diff" label="μD" width="90" :formatter="formatNumber" />
          <el-table-column prop="prob_11" label="1-1概率" width="110">
            <template #default="scope">
              {{ formatPercent(scope.row.prob_11) }}
            </template>
          </el-table-column>
          <el-table-column prop="odds_11" label="1-1赔率" width="100">
            <template #default="scope">
              {{ formatValue(scope.row.odds_11) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220">
            <template #default="scope">
              <div class="row-actions">
                <el-button size="small" @click="openDetail(scope.row)">模型数据</el-button>
                <el-button
                  size="small"
                  :type="isRowBetOpportunity(scope.row) ? 'success' : 'primary'"
                  :plain="!isRowBetOpportunity(scope.row)"
                  @click="openSuggestion(scope.row)"
                >
                  建议
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; text-align: right"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="模型数据" width="860px">
      <div v-if="detailData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="比赛">{{ detailData.home_team }} vs {{ detailData.away_team }}</el-descriptions-item>
          <el-descriptions-item label="赛事">{{ detailData.league || '-' }}</el-descriptions-item>
          <el-descriptions-item label="比赛时间">{{ formatDateTime(null, null, detailData.match_time) }}</el-descriptions-item>
          <el-descriptions-item label="1-1概率">{{ formatPercent(detailData.prob_11) }}</el-descriptions-item>
          <el-descriptions-item label="μT">{{ formatValue(detailData.mu_total) }}</el-descriptions-item>
          <el-descriptions-item label="μD">{{ formatValue(detailData.mu_diff) }}</el-descriptions-item>
          <el-descriptions-item label="μH">{{ formatValue(detailData.mu_home) }}</el-descriptions-item>
          <el-descriptions-item label="μA">{{ formatValue(detailData.mu_away) }}</el-descriptions-item>
          <el-descriptions-item label="排名">{{ formatValue(detailData.rank, 0) }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin: 16px 0 8px">模型输入四类数据</h4>
        <el-table :data="modelDataRows" border size="small" class="model-input-table">
          <el-table-column prop="name" label="数据" width="140" />
          <el-table-column prop="usage" label="用途" />
          <el-table-column prop="required" label="必需" width="100" />
          <el-table-column prop="source" label="来源" width="220" />
          <el-table-column prop="value" label="取值" width="260" />
        </el-table>

        <h4 style="margin: 16px 0 8px">输入与中间量</h4>
        <pre class="json-box">{{ detailPayload }}</pre>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="suggestionVisible" title="1-1投注建议" width="980px">
      <el-skeleton :loading="suggestionLoading" animated :rows="8">
        <div v-if="suggestionView">
          <el-alert
            type="info"
            show-icon
            :closable="false"
            style="margin-bottom: 12px"
            title="提示：本建议用于筛选有价值机会，不保证单场命中。"
          />

          <el-card class="suggestion-section" shadow="never">
            <template #header>
              <div class="suggestion-section-title">结论卡</div>
            </template>
            <div class="conclusion-grid">
              <div class="conclusion-item">
                <div class="item-label">建议等级</div>
                <el-tag size="large" :type="levelTagType(suggestionView.level)">{{ suggestionView.level }}</el-tag>
              </div>
              <div class="conclusion-item">
                <div class="item-label">操作建议</div>
                <div class="item-value">{{ suggestionView.action }}</div>
              </div>
              <div class="conclusion-item">
                <div class="item-label">建议仓位</div>
                <div class="item-value">{{ suggestionView.stake }}</div>
              </div>
              <div class="conclusion-item">
                <div class="item-label">综合评分</div>
                <div class="item-value">{{ suggestionView.totalScore }}</div>
              </div>
            </div>
            <div class="reasons-box">
              <div class="item-label">核心理由</div>
              <ul>
                <li v-for="reason in suggestionView.reasons" :key="reason">{{ reason }}</li>
              </ul>
            </div>
          </el-card>

          <div class="suggestion-grid">
            <el-card class="suggestion-section" shadow="never">
              <template #header>
                <div class="suggestion-section-title">模型面</div>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="P(1-1)">{{ formatPercent(suggestionView.model.prob11) }}</el-descriptions-item>
                <el-descriptions-item label="排名">{{ formatValue(suggestionView.model.rank, 0) }}</el-descriptions-item>
                <el-descriptions-item label="μT">{{ formatValue(suggestionView.model.muTotal) }}</el-descriptions-item>
                <el-descriptions-item label="μD">{{ formatValue(suggestionView.model.muDiff) }}</el-descriptions-item>
                <el-descriptions-item label="μH">{{ formatValue(suggestionView.model.muHome) }}</el-descriptions-item>
                <el-descriptions-item label="μA">{{ formatValue(suggestionView.model.muAway) }}</el-descriptions-item>
                <el-descriptions-item label="来源完整度">{{ suggestionView.model.completeness }}%</el-descriptions-item>
                <el-descriptions-item label="模型得分">{{ suggestionView.scoreBreakdown.model }}/40</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-card class="suggestion-section" shadow="never">
              <template #header>
                <div class="suggestion-section-title">价值面</div>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="1-1赔率">{{ formatValue(suggestionView.value.odds11) }}</el-descriptions-item>
                <el-descriptions-item label="安全垫">{{ formatPercentRaw(suggestionView.value.margin) }}</el-descriptions-item>
                <el-descriptions-item label="隐含概率 P_imp">{{ formatPercentRaw(suggestionView.value.pImp) }}</el-descriptions-item>
                <el-descriptions-item label="模型概率 P_model">{{ formatPercentRaw(suggestionView.value.pModel) }}</el-descriptions-item>
                <el-descriptions-item label="价值差 Edge">{{ formatPercentRaw(suggestionView.value.edge) }}</el-descriptions-item>
                <el-descriptions-item label="价值结论">{{ suggestionView.value.conclusion }}</el-descriptions-item>
                <el-descriptions-item label="赔率来源" :span="2">{{ suggestionView.value.source }}</el-descriptions-item>
                <el-descriptions-item label="价值得分" :span="2">{{ suggestionView.scoreBreakdown.value }}/30</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </div>

          <div class="suggestion-grid">
            <el-card class="suggestion-section" shadow="never">
              <template #header>
                <div class="suggestion-section-title">结构面</div>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="大小球区间">{{ suggestionView.structure.goalsBand }}</el-descriptions-item>
                <el-descriptions-item label="亚洲让球区间">{{ suggestionView.structure.handicapBand }}</el-descriptions-item>
                <el-descriptions-item label="平赔区间">{{ suggestionView.structure.drawBand }}</el-descriptions-item>
                <el-descriptions-item label="结构标签">{{ suggestionView.structure.tag }}</el-descriptions-item>
                <el-descriptions-item label="结构得分" :span="2">{{ suggestionView.scoreBreakdown.structure }}/20</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-card class="suggestion-section" shadow="never">
              <template #header>
                <div class="suggestion-section-title">风险面</div>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="数据缺失风险">
                  <el-tag :type="riskTagType(suggestionView.risk.dataMissing.level)">{{ suggestionView.risk.dataMissing.level }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="盘口异常风险">
                  <el-tag :type="riskTagType(suggestionView.risk.marketAnomaly.level)">{{ suggestionView.risk.marketAnomaly.level }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="状态/比分提示" :span="2">{{ suggestionView.risk.statusHint }}</el-descriptions-item>
                <el-descriptions-item label="总体风险">
                  <el-tag :type="riskTagType(suggestionView.risk.overallLevel)">{{ suggestionView.risk.overallLevel }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="风险得分">{{ suggestionView.scoreBreakdown.risk }}/10</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </div>

          <el-card class="suggestion-section" shadow="never">
            <template #header>
              <div class="suggestion-section-title">资金与执行面</div>
            </template>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="单场上限">{{ suggestionView.bankroll.singleCap }}</el-descriptions-item>
              <el-descriptions-item label="当日上限">{{ suggestionView.bankroll.dailyCap }}</el-descriptions-item>
              <el-descriptions-item label="连亏保护">{{ suggestionView.bankroll.stopLossRule }}</el-descriptions-item>
              <el-descriptions-item label="执行纪律" :span="3">
                命中阈值才下单，不因临场情绪加码。
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>
      </el-skeleton>
      <template #footer>
        <el-button @click="suggestionVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  startPoisson11FetchTask,
  getDrawPredictionTask,
  getPoisson11List,
  getPoisson11Detail,
  getBdIssueOptions,
  getBdLeagueOptions
} from '@/api/drawPrediction'

const VALUE_MARGIN = 0.08

const queryDate = ref(new Date().toISOString().slice(0, 10))
const dataSource = ref('yingqiu_bd')
const queryIssueNo = ref('')
const queryLeague = ref('')
const loading = ref(false)
const fetching = ref(false)
const tableData = ref([])
const allItems = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const tableKey = ref(0)
const issueOptions = ref([])
const issueOptionsLoading = ref(false)
const leagueOptions = ref([])
const leagueOptionsLoading = ref(false)
const resolvedIssueDates = ref([])

const detailVisible = ref(false)
const detailData = ref(null)
const suggestionVisible = ref(false)
const suggestionLoading = ref(false)
const suggestionData = ref(null)
const detailCache = new Map()
const suggestionOpportunityMap = ref({})
const suggestionPrimePending = new Set()
const fetchTaskId = ref('')
const fetchTaskStatus = ref('')
const fetchTaskProgress = ref(0)
const fetchTaskMessage = ref('')
let fetchTaskPollTimer = null
let fetchTaskStartedAt = 0
const FETCH_TASK_POLL_INTERVAL_MS = 1200
const FETCH_TASK_TIMEOUT_MS = 10 * 60 * 1000

const detailPayload = computed(() => {
  if (!detailData.value?.input_payload) return ''
  return JSON.stringify(detailData.value.input_payload, null, 2)
})

const formatValue = (value, digits = 2) => {
  if (value === null || value === undefined || value === '') return '-'
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) return '-'
    return digits === 0 ? String(Math.round(value)) : value.toFixed(digits)
  }
  return String(value)
}

const formatNumber = (row, column, cellValue) => formatValue(cellValue)

const formatPercent = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = Number(value)
  if (!Number.isFinite(num)) return '-'
  return `${(num * 100).toFixed(2)}%`
}

const formatPercentRaw = (value) => {
  const num = Number(value)
  if (!Number.isFinite(num)) return '-'
  return `${(num * 100).toFixed(2)}%`
}

const hasData = (value) => !(value === null || value === undefined || value === '')

const toNumber = (value) => {
  if (!hasData(value)) return null
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

const levelTagType = (level) => {
  const map = {
    强建议: 'danger',
    可跟进: 'warning',
    仅观察: 'info',
    放弃: ''
  }
  return map[level] || 'info'
}

const riskTagType = (level) => {
  const map = { 低: 'success', 中: 'warning', 高: 'danger' }
  return map[level] || 'info'
}

const formatSourceLabel = (source) => {
  const key = String(source || '').trim()
  if (!key || key === 'default') return '-'
  const map = {
    '500_bjdc_index.asianhand': '500北单首页-亚盘',
    '500_bjdc_project_fq_bf.xml.c13': '500北单比分-1:1(XML c13)',
    'bd_other_odds_tabs.goals.instant_line': '北单详情-进球数(即时盘)',
    'bd_other_odds_tabs.goals.init_line': '北单详情-进球数(初始盘)',
    'bd_other_odds_tabs.asia.instant_handicap': '北单详情-让球(即时盘)',
    'bd_other_odds_tabs.asia.init_handicap': '北单详情-让球(初始盘)',
    source_attributes: '赛程字段',
    inferred_from_draw_odds: '由平赔推断'
  }
  return map[key] || key
}

const inferOddsSource = (attrs, odds) => {
  if (!hasData(odds?.draw) && !hasData(odds?.win) && !hasData(odds?.lose)) {
    return '-'
  }
  const tabs = attrs?.other_odds_tabs
  if (tabs && Array.isArray(tabs.eu) && tabs.eu.length > 0) {
    return '北单详情-欧指'
  }
  if (hasData(attrs?.odds_draw) || hasData(attrs?.odds_nspf_draw) || hasData(attrs?.odds_spf_draw)) {
    return '赛程字段'
  }
  return '-'
}

const inferXgSource = (attrs, xgHome, xgAway) => {
  if (!hasData(xgHome) && !hasData(xgAway)) return '-'
  const sources = attrs?.external_sources
  if (sources && typeof sources === 'object') {
    if (sources.understat) return 'Understat'
    if (sources.fbref) return 'FBref'
    if (sources.oddsportal) return 'OddsPortal'
  }
  return '赛程字段'
}

const modelDataRows = computed(() => {
  const payload = detailData.value?.input_payload || {}
  const odds = payload.odds || {}
  const attrs = payload.source_attributes || {}
  const xgHome = attrs.xg_home
  const xgAway = attrs.xg_away
  const xgValue = xgHome !== undefined || xgAway !== undefined
    ? `主 ${formatValue(xgHome)} / 客 ${formatValue(xgAway)}`
    : '-'
  const oddsValue = odds.win !== undefined || odds.draw !== undefined || odds.lose !== undefined
    ? `胜 ${formatValue(odds.win)} / 平 ${formatValue(odds.draw)} / 负 ${formatValue(odds.lose)}`
    : '-'

  return [
    {
      name: '大小球盘口',
      usage: '推总进球 μT',
      required: '必须',
      source: formatSourceLabel(payload.total_goals_line_source),
      value: formatValue(payload.total_goals_line)
    },
    {
      name: '亚洲让球',
      usage: '推强弱 μD',
      required: '必须',
      source: formatSourceLabel(payload.handicap_source),
      value: formatValue(payload.handicap)
    },
    {
      name: '欧赔(可选)',
      usage: '校验市场',
      required: '推荐',
      source: inferOddsSource(attrs, odds),
      value: oddsValue
    },
    {
      name: '1-1比分赔率',
      usage: '价值评估',
      required: '推荐',
      source: formatSourceLabel(payload.odds_score_11_source),
      value: formatValue(payload.odds_score_11)
    },
    {
      name: 'xG / 进球数据',
      usage: '模型升级',
      required: '进阶',
      source: inferXgSource(attrs, xgHome, xgAway),
      value: xgValue
    }
  ]
})

const parseLineValue = (value) => {
  if (!hasData(value)) return null
  const text = String(value).replace(/\s+/g, '')
  if (!text || text === '-') return null

  const slash = text.match(/([+-]?\d+(?:\.\d+)?)\/([+-]?\d+(?:\.\d+)?)/)
  if (slash) {
    const left = toNumber(slash[1])
    const right = toNumber(slash[2])
    if (left !== null && right !== null) return (left + right) / 2
  }

  const direct = toNumber(text)
  if (direct !== null) return direct

  const firstNumber = text.match(/[+-]?\d+(?:\.\d+)?/)
  if (firstNumber) return toNumber(firstNumber[0])
  return null
}

const normalizeOtherOddsTabs = (rawTabs) => {
  let value = rawTabs
  if (typeof value === 'string' && value) {
    try {
      value = JSON.parse(value)
    } catch (err) {
      value = null
    }
  }
  if (!value || typeof value !== 'object') {
    return { eu: [], asia: [], goals: [] }
  }
  return {
    eu: Array.isArray(value.eu) ? value.eu : [],
    asia: Array.isArray(value.asia) ? value.asia : [],
    goals: Array.isArray(value.goals) ? value.goals : []
  }
}

const isCrownCompany = (row) => {
  const providerId = String(row?.provider_id || row?.providerId || '').trim()
  const company = String(row?.company || '').trim()
  return providerId === '629' || company.includes('皇冠') || company.startsWith('皇')
}

const pickPreferredRow = (rows) => rows.find((row) => isCrownCompany(row)) || rows[0] || null

const extractOdds11 = (payload, attrs) => {
  const directSource = formatSourceLabel(payload?.odds_score_11_source || attrs?.odds_score_11_source || '')
  const directCandidates = [
    payload?.odds_score_11,
    payload?.odds11,
    attrs?.odds_score_11,
    attrs?.score_odds_11,
    attrs?.odds_11,
    attrs?.odds11
  ]
  for (const candidate of directCandidates) {
    const num = toNumber(candidate)
    if (num !== null && num > 1) return { value: num, source: directSource === '-' ? '赛程字段' : directSource }
  }

  const mapCandidates = [attrs?.score_odds, attrs?.odds_score, attrs?.odds_score_map, attrs?.bf_odds]
  for (const candidate of mapCandidates) {
    if (!candidate || typeof candidate !== 'object') continue
    const num = toNumber(candidate['1:1'] ?? candidate['1-1'] ?? candidate['11'])
    if (num !== null && num > 1) return { value: num, source: '比分赔率映射字段' }
  }

  return { value: null, source: '-' }
}

const classifyGoalsBand = (line) => {
  if (line === null) return '-'
  if (line <= 2.5) return '2.0-2.5'
  if (line <= 2.75) return '2.75'
  return '>=3.0'
}

const classifyHandicapBand = (line) => {
  if (line === null) return '-'
  const absVal = Math.abs(line)
  if (absVal < 0.01) return '0'
  if (absVal <= 0.3) return '±0.25'
  if (absVal <= 0.55) return '±0.5'
  return '其他'
}

const classifyDrawBand = (drawOdds) => {
  if (drawOdds === null) return '-'
  return drawOdds >= 2.8 && drawOdds <= 3.1 ? '2.8-3.1' : '其他'
}

const classifyStructureTag = (goalsBand, handicapBand, drawBand) => {
  const hitCount = Number(goalsBand === '2.0-2.5') + Number(handicapBand === '0' || handicapBand === '±0.25') + Number(drawBand === '2.8-3.1')
  if (hitCount >= 3) return '甜点区'
  if (hitCount === 2) return '次甜点'
  return '非甜点'
}

const scoreToLevel = (score) => {
  if (score >= 80) return '强建议'
  if (score >= 65) return '可跟进'
  if (score >= 50) return '仅观察'
  return '放弃'
}

const downgradeLevel = (level) => {
  if (level === '强建议') return '可跟进'
  if (level === '可跟进') return '仅观察'
  if (level === '仅观察') return '放弃'
  return '放弃'
}

const getActionByLevel = (level) => {
  const map = {
    强建议: '建议投注1-1',
    可跟进: '小注试投',
    仅观察: '继续观察',
    放弃: '不投注'
  }
  return map[level] || '继续观察'
}

const getStakeByLevel = (level) => {
  const map = {
    强建议: '1.0u',
    可跟进: '0.5u',
    仅观察: '-',
    放弃: '-'
  }
  return map[level] || '-'
}

const maxRiskLevel = (left, right) => {
  const order = { 低: 1, 中: 2, 高: 3 }
  return (order[left] || 0) >= (order[right] || 0) ? left : right
}

const inferDataMissingRisk = ({ qualityFlags, totalGoalsLine, handicap, odds11 }) => {
  const flags = Array.isArray(qualityFlags) ? qualityFlags : []
  const defaultCount = flags.filter((flag) => String(flag).includes('default')).length
  const missingCore = Number(totalGoalsLine === null) + Number(handicap === null) + Number(odds11 === null)
  if (defaultCount >= 2 || missingCore >= 2) return { level: '高', detail: '关键字段缺失较多' }
  if (defaultCount > 0 || missingCore > 0) return { level: '中', detail: '存在字段缺失或默认值' }
  return { level: '低', detail: '关键字段完整' }
}

const inferMarketAnomalyRisk = (attrs) => {
  const tabs = normalizeOtherOddsTabs(attrs?.other_odds_tabs)
  let maxDiff = 0

  const evaluateRows = (rows, initKeys, instantKeys) => {
    if (!rows.length) return
    const row = pickPreferredRow(rows)
    if (!row) return

    let initLine = null
    let instantLine = null
    initKeys.some((key) => {
      initLine = parseLineValue(row[key])
      return initLine !== null
    })
    instantKeys.some((key) => {
      instantLine = parseLineValue(row[key])
      return instantLine !== null
    })
    if (initLine !== null && instantLine !== null) {
      maxDiff = Math.max(maxDiff, Math.abs(instantLine - initLine))
    }
  }

  evaluateRows(tabs.asia, ['init_handicap', 'init_line', 'line'], ['instant_handicap', 'instant_line', 'line'])
  evaluateRows(tabs.goals, ['init_line', 'init_handicap', 'line'], ['instant_line', 'instant_handicap', 'line'])

  if (maxDiff >= 0.5) return { level: '高', detail: '盘口波动较大' }
  if (maxDiff >= 0.25) return { level: '中', detail: '盘口有明显波动' }
  if (maxDiff > 0) return { level: '低', detail: '盘口波动可控' }
  return { level: '低', detail: '暂无异常波动' }
}

const buildSuggestionView = (detail) => {
  if (!detail) return null

  const payload = detail.input_payload || {}
  const attrs = payload.source_attributes || {}
  const odds = payload.odds || {}
  const qualityFlags = Array.isArray(payload.quality_flags) ? payload.quality_flags : []

  const prob11 = toNumber(detail.prob_11)
  const rank = toNumber(detail.rank)
  const muTotal = toNumber(detail.mu_total ?? payload?.mu?.total)
  const muDiff = toNumber(detail.mu_diff ?? payload?.mu?.diff)
  const muHome = toNumber(detail.mu_home ?? payload?.mu?.home)
  const muAway = toNumber(detail.mu_away ?? payload?.mu?.away)
  const totalGoalsLine = toNumber(payload.total_goals_line)
  const handicap = toNumber(payload.handicap)
  const drawOdds = toNumber(odds.draw)

  const odds11Result = extractOdds11(payload, attrs)
  const odds11 = odds11Result.value
  const pImp = odds11 !== null && odds11 > 1 ? (1 / odds11) : null
  const pModel = prob11
  const edge = pImp !== null && pModel !== null ? (pModel - pImp) : null

  const completenessSignals = [
    hasData(payload.total_goals_line_source) && String(payload.total_goals_line_source) !== 'default',
    hasData(payload.handicap_source) && String(payload.handicap_source) !== 'default',
    drawOdds !== null
  ]
  const completeness = Math.round((completenessSignals.filter(Boolean).length / 3) * 100)

  const goalsBand = classifyGoalsBand(totalGoalsLine)
  const handicapBand = classifyHandicapBand(handicap)
  const drawBand = classifyDrawBand(drawOdds)
  const structureTag = classifyStructureTag(goalsBand, handicapBand, drawBand)

  const dataMissingRisk = inferDataMissingRisk({ qualityFlags, totalGoalsLine, handicap, odds11 })
  const marketAnomalyRisk = inferMarketAnomalyRisk(attrs)

  const statusText = String(attrs.status_des || attrs.status || '').trim() || '-'
  const fullScore = String(attrs.full_score || attrs.score || '').trim()
  const halfScore = String(attrs.halftime_score || attrs.half_score || '').trim()
  const scoreText = fullScore || '-'
  const statusHint = `${statusText}${scoreText !== '-' ? ` / ${scoreText}` : ''}${halfScore ? `（半场 ${halfScore}）` : ''}`

  const isFinished = /(完场|已完|结束|FT|赛果)/i.test(statusText)
  const isInplay = /(进行|中场|上半场|下半场|live|滚球)/i.test(statusText)
  const statusRiskLevel = (isFinished || isInplay) ? '高' : '低'
  const overallRiskLevel = maxRiskLevel(maxRiskLevel(dataMissingRisk.level, marketAnomalyRisk.level), statusRiskLevel)

  let modelScore = 0
  if (prob11 !== null) {
    if (prob11 >= 0.12) modelScore += 20
    else if (prob11 >= 0.10) modelScore += 17
    else if (prob11 >= 0.08) modelScore += 14
    else if (prob11 >= 0.06) modelScore += 10
    else modelScore += 5
  }
  if (rank !== null) {
    if (rank <= 5) modelScore += 10
    else if (rank <= 10) modelScore += 8
    else if (rank <= 20) modelScore += 6
    else if (rank <= 40) modelScore += 4
    else modelScore += 2
  }
  if (muTotal !== null) modelScore += (muTotal >= 1.8 && muTotal <= 2.8) ? 5 : 2
  if (muDiff !== null) modelScore += (Math.abs(muDiff) <= 0.35) ? 5 : 2
  modelScore = clamp(Math.round(modelScore), 0, 40)

  let valueScore = 0
  if (edge !== null) {
    if (edge >= 0.03) valueScore = 30
    else if (edge >= 0.015) valueScore = 24
    else if (edge >= 0.005) valueScore = 18
    else if (edge > 0) valueScore = 12
  }

  let structureScore = 0
  if (goalsBand === '2.0-2.5') structureScore += 8
  else if (goalsBand === '2.75') structureScore += 5
  else if (goalsBand !== '-') structureScore += 2

  if (handicapBand === '0' || handicapBand === '±0.25') structureScore += 7
  else if (handicapBand === '±0.5') structureScore += 4
  else if (handicapBand !== '-') structureScore += 1

  if (drawBand === '2.8-3.1') structureScore += 5
  else if (drawBand !== '-') structureScore += 2
  structureScore = clamp(Math.round(structureScore), 0, 20)

  let riskScore = 10
  if (dataMissingRisk.level === '高') riskScore -= 4
  else if (dataMissingRisk.level === '中') riskScore -= 2
  if (marketAnomalyRisk.level === '高') riskScore -= 3
  else if (marketAnomalyRisk.level === '中') riskScore -= 2
  if (statusRiskLevel === '高') riskScore = 0
  riskScore = clamp(Math.round(riskScore), 0, 10)

  const totalScore = Math.round(modelScore + valueScore + structureScore + riskScore)
  let level = scoreToLevel(totalScore)
  const vetoTriggered = isFinished || isInplay || (edge !== null && edge <= 0)

  if (vetoTriggered) {
    level = '放弃'
  } else if (odds11 === null) {
    level = downgradeLevel(level)
  }

  let valueConclusion = '数据不足，建议观望'
  if (edge !== null && pModel !== null && pImp !== null) {
    valueConclusion = pModel > pImp * (1 + VALUE_MARGIN) ? '有价值' : '无明显价值'
  }

  const reasons = []
  if (prob11 !== null) {
    reasons.push(prob11 >= 0.08 ? '模型概率处于可跟进区间' : '模型概率偏弱，需谨慎')
  }
  if (edge !== null) {
    reasons.push(edge > 0 ? '模型概率高于赔率隐含概率' : '赔率价值不足')
  } else {
    reasons.push('1-1赔率缺失，价值项降级处理')
  }
  reasons.push(`结构标签：${structureTag}`)
  if (overallRiskLevel !== '低') reasons.push(`风险提示：${overallRiskLevel}风险`)
  if (statusRiskLevel === '高') reasons.push('状态异常：当前不满足投注前置条件')

  return {
    level,
    action: getActionByLevel(level),
    stake: getStakeByLevel(level),
    totalScore,
    reasons: reasons.slice(0, 3),
    scoreBreakdown: {
      model: modelScore,
      value: valueScore,
      structure: structureScore,
      risk: riskScore
    },
    model: {
      prob11,
      rank,
      muTotal,
      muDiff,
      muHome,
      muAway,
      completeness
    },
    value: {
      odds11,
      pImp,
      pModel,
      edge,
      margin: VALUE_MARGIN,
      conclusion: valueConclusion,
      source: odds11Result.source
    },
    structure: {
      goalsBand,
      handicapBand,
      drawBand,
      tag: structureTag
    },
    risk: {
      dataMissing: dataMissingRisk,
      marketAnomaly: marketAnomalyRisk,
      statusHint: statusHint || '-',
      overallLevel: overallRiskLevel
    },
    bankroll: {
      singleCap: '0.5%-2%',
      dailyCap: '3%-5%',
      stopLossRule: '连亏3场暂停'
    }
  }
}

const suggestionView = computed(() => buildSuggestionView(suggestionData.value))

const isOpportunityLevel = (level) => level === '强建议' || level === '可跟进'

const setRowBetOpportunity = (matchId, value) => {
  const key = String(matchId || '').trim()
  if (!key) return
  suggestionOpportunityMap.value = {
    ...suggestionOpportunityMap.value,
    [key]: Boolean(value)
  }
}

const isRowBetOpportunity = (row) => {
  const key = String(row?.match_id || '').trim()
  if (!key) return false
  return suggestionOpportunityMap.value[key] === true
}

const normalizeIssueNo = (value) => String(value || '').trim()

const isValidIssueNo = (value) => /^\d{5}$/.test(normalizeIssueNo(value))

const refreshCurrentPageData = () => {
  total.value = allItems.value.length
  const start = (currentPage.value - 1) * pageSize.value
  tableData.value = allItems.value.slice(start, start + pageSize.value)
  tableKey.value = Date.now()
  primeSuggestionButtonsForVisibleRows()
}

const clearFetchTaskPollTimer = () => {
  if (fetchTaskPollTimer) {
    clearTimeout(fetchTaskPollTimer)
    fetchTaskPollTimer = null
  }
}

const scheduleFetchTaskPoll = (taskId) => {
  clearFetchTaskPollTimer()
  fetchTaskPollTimer = setTimeout(() => {
    pollFetchTask(taskId)
  }, FETCH_TASK_POLL_INTERVAL_MS)
}

const finishFetchTaskWithError = (message) => {
  clearFetchTaskPollTimer()
  fetching.value = false
  fetchTaskStatus.value = 'failed'
  fetchTaskMessage.value = message || '抓取任务失败'
  ElMessage.error(fetchTaskMessage.value)
}

const pollFetchTask = async (taskId) => {
  try {
    const task = await getDrawPredictionTask(taskId)
    fetchTaskId.value = task?.task_id || taskId
    fetchTaskStatus.value = String(task?.status || '')
    fetchTaskProgress.value = Math.max(0, Math.min(100, Number(task?.progress || 0)))
    fetchTaskMessage.value = String(task?.message || '处理中')

    if (fetchTaskStatus.value === 'success') {
      clearFetchTaskPollTimer()
      fetching.value = false
      fetchTaskProgress.value = 100
      detailCache.clear()
      ElMessage.success(fetchTaskMessage.value || '抓取完成')
      currentPage.value = 1
      await fetchList()
      return
    }

    if (fetchTaskStatus.value === 'failed') {
      const errText = String(task?.error || '')
      finishFetchTaskWithError(errText ? `抓取失败：${errText}` : '抓取失败')
      return
    }

    if (Date.now() - fetchTaskStartedAt > FETCH_TASK_TIMEOUT_MS) {
      finishFetchTaskWithError('抓取任务轮询超时，请稍后手动查询列表')
      return
    }

    scheduleFetchTaskPoll(taskId)
  } catch (err) {
    console.error('轮询抓取任务失败:', err)
    if (Date.now() - fetchTaskStartedAt > FETCH_TASK_TIMEOUT_MS) {
      finishFetchTaskWithError('抓取任务轮询超时，请稍后手动查询列表')
      return
    }
    scheduleFetchTaskPoll(taskId)
  }
}

const loadIssueOptions = async () => {
  issueOptionsLoading.value = true
  try {
    const res = await getBdIssueOptions({ count: 3 })
    issueOptions.value = Array.isArray(res?.items) ? res.items : []
  } catch (err) {
    console.error('加载北单期号失败:', err)
    issueOptions.value = []
  } finally {
    issueOptionsLoading.value = false
  }
}

const loadLeagueOptions = async ({ silent = false } = {}) => {
  const issueNo = normalizeIssueNo(queryIssueNo.value)
  if (issueNo && !isValidIssueNo(issueNo)) {
    resolvedIssueDates.value = []
    leagueOptions.value = []
    if (queryLeague.value) queryLeague.value = ''
    return
  }

  const params = {}
  if (queryDate.value) {
    params.date_from = queryDate.value
    params.date_to = queryDate.value
  }
  if (issueNo) {
    params.issue_no = issueNo
  }

  leagueOptionsLoading.value = true
  try {
    const res = await getBdLeagueOptions(params)
    leagueOptions.value = Array.isArray(res?.items) ? res.items : []
    resolvedIssueDates.value = Array.isArray(res?.resolved_issue_dates) ? res.resolved_issue_dates : []
    if (queryLeague.value && !leagueOptions.value.includes(queryLeague.value)) {
      queryLeague.value = ''
    }
  } catch (err) {
    console.error('加载赛事选项失败:', err)
    leagueOptions.value = []
    resolvedIssueDates.value = []
    if (!silent) ElMessage.error('加载赛事选项失败')
  } finally {
    leagueOptionsLoading.value = false
  }
}

const fetchList = async () => {
  const issueNo = normalizeIssueNo(queryIssueNo.value)
  if (issueNo && !isValidIssueNo(issueNo)) {
    ElMessage.warning('北单期号需为5位数字，如26026')
    return
  }
  if (!queryDate.value && !issueNo) {
    ElMessage.warning('请先选择日期或输入北单期号')
    return
  }

  loading.value = true
  try {
    suggestionOpportunityMap.value = {}
    suggestionPrimePending.clear()
    await loadLeagueOptions({ silent: true })
    tableData.value = []

    const targetDates = issueNo
      ? [...resolvedIssueDates.value]
      : (queryDate.value ? [queryDate.value] : [])

    if (!targetDates.length) {
      allItems.value = []
      refreshCurrentPageData()
      return
    }

    const responses = await Promise.all(
      targetDates.map((dateStr, idx) => getPoisson11List({
        date_str: dateStr,
        data_source: dataSource.value,
        _ts: Date.now() + idx
      }))
    )

    const mergedItems = responses.flatMap((res) => (Array.isArray(res?.items) ? res.items : []))
    const uniqueMap = new Map()
    mergedItems.forEach((item) => {
      const key = String(item?.match_id || '')
      if (!key || uniqueMap.has(key)) return
      uniqueMap.set(key, item)
    })

    const leagueName = String(queryLeague.value || '').trim()
    allItems.value = Array.from(uniqueMap.values())
      .filter((item) => (leagueName ? String(item?.league || '').trim() === leagueName : true))
      .sort((a, b) => {
        const rankA = Number(a?.rank)
        const rankB = Number(b?.rank)
        if (Number.isFinite(rankA) && Number.isFinite(rankB) && rankA !== rankB) {
          return rankA - rankB
        }
        return Number(b?.prob_11 || 0) - Number(a?.prob_11 || 0)
      })
      .map((item, idx) => ({ ...item, rank: idx + 1 }))

    refreshCurrentPageData()
  } catch (err) {
    console.error('获取扫盘列表失败:', err)
    ElMessage.error('获取扫盘列表失败')
  } finally {
    loading.value = false
  }
}

const handleFetch = async () => {
  if (!queryDate.value) {
    ElMessage.warning('请先选择日期')
    return
  }
  clearFetchTaskPollTimer()
  fetchTaskId.value = ''
  fetchTaskStatus.value = 'pending'
  fetchTaskProgress.value = 0
  fetchTaskMessage.value = '任务提交中...'
  fetchTaskStartedAt = Date.now()
  fetching.value = true
  try {
    const taskResp = await startPoisson11FetchTask({
      date_str: queryDate.value,
      data_source: dataSource.value,
      _ts: Date.now()
    })
    const taskId = String(taskResp?.task_id || '').trim()
    if (!taskId) {
      throw new Error('未返回任务ID')
    }
    fetchTaskId.value = taskId
    fetchTaskMessage.value = '任务已提交，等待处理...'
    await pollFetchTask(taskId)
  } catch (err) {
    console.error('抓取失败:', err)
    finishFetchTaskWithError('抓取任务提交失败')
  } finally {
    if (fetchTaskStatus.value === 'success' || fetchTaskStatus.value === 'failed') {
      fetching.value = false
    }
  }
}

const handleQuery = () => {
  currentPage.value = 1
  fetchList()
}

const resetFilter = () => {
  queryDate.value = new Date().toISOString().slice(0, 10)
  dataSource.value = 'yingqiu_bd'
  queryIssueNo.value = ''
  queryLeague.value = ''
  currentPage.value = 1
  loadLeagueOptions({ silent: true })
  fetchList()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  refreshCurrentPageData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  refreshCurrentPageData()
}

const getDetailForMatch = async (matchId) => {
  const key = `${dataSource.value}:${matchId}`
  if (detailCache.has(key)) return detailCache.get(key)
  const data = await getPoisson11Detail(matchId, { data_source: dataSource.value })
  detailCache.set(key, data)
  return data
}

const primeSuggestionButtonsForVisibleRows = async () => {
  const rows = Array.isArray(tableData.value) ? tableData.value : []
  if (!rows.length) return

  await Promise.all(
    rows.map(async (row) => {
      const matchId = String(row?.match_id || '').trim()
      if (!matchId) return
      if (Object.prototype.hasOwnProperty.call(suggestionOpportunityMap.value, matchId)) return
      if (suggestionPrimePending.has(matchId)) return

      suggestionPrimePending.add(matchId)
      try {
        const detail = await getDetailForMatch(matchId)
        const view = buildSuggestionView(detail)
        setRowBetOpportunity(matchId, isOpportunityLevel(view?.level))
      } catch (err) {
        // 静默失败，避免影响列表交互
      } finally {
        suggestionPrimePending.delete(matchId)
      }
    })
  )
}

const openDetail = async (row) => {
  try {
    detailData.value = await getDetailForMatch(row.match_id)
    detailVisible.value = true
  } catch (err) {
    console.error('获取模型详情失败:', err)
    ElMessage.error('获取模型详情失败')
  }
}

const openSuggestion = async (row) => {
  suggestionVisible.value = true
  suggestionLoading.value = true
  suggestionData.value = null
  try {
    suggestionData.value = await getDetailForMatch(row.match_id)
    const view = buildSuggestionView(suggestionData.value)
    setRowBetOpportunity(row.match_id, isOpportunityLevel(view?.level))
  } catch (err) {
    console.error('获取建议数据失败:', err)
    ElMessage.error('获取建议数据失败')
    suggestionVisible.value = false
  } finally {
    suggestionLoading.value = false
  }
}

const formatDateTime = (row, column, cellValue) => {
  if (!cellValue) return '-'
  const d = new Date(cellValue)
  if (Number.isNaN(d.getTime())) return String(cellValue)
  return d.toLocaleString()
}

onMounted(async () => {
  await loadIssueOptions()
  await loadLeagueOptions({ silent: true })
  fetchList()
})

onBeforeUnmount(() => {
  clearFetchTaskPollTimer()
})

watch(
  () => [queryDate.value, queryIssueNo.value],
  () => {
    loadLeagueOptions({ silent: true })
  }
)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.fetch-progress {
  margin-top: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border: 1px solid #e5eaf3;
  border-radius: 8px;
}

.fetch-progress-text {
  margin-top: 8px;
  color: #606266;
  font-size: 13px;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.json-box {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  max-height: 300px;
  overflow: auto;
}

.model-input-table {
  margin-bottom: 8px;
}

.suggestion-section {
  margin-bottom: 12px;
}

.suggestion-section-title {
  font-weight: 600;
}

.conclusion-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.conclusion-item {
  background: #f7f9fc;
  border-radius: 6px;
  padding: 10px 12px;
}

.item-label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 6px;
}

.item-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.reasons-box {
  margin-top: 12px;
  background: #f7f9fc;
  border-radius: 6px;
  padding: 10px 12px;
}

.reasons-box ul {
  margin: 8px 0 0;
  padding-left: 18px;
}

.reasons-box li {
  line-height: 1.6;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

@media (max-width: 992px) {
  .conclusion-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .suggestion-grid {
    grid-template-columns: 1fr;
  }
}
</style>
