<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>专抓1-1扫盘</span>
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
          <el-select v-model="dataSource" placeholder="数据源" style="width: 180px" disabled>
            <el-option label="盈球北单（详情赔率）" value="yingqiu_bd" />
          </el-select>
          <el-button type="primary" @click="fetchList" :loading="loading">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
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
          <el-table-column label="操作" width="140">
            <template #default="scope">
              <el-button size="small" @click="openDetail(scope.row)">模型数据</el-button>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPoisson11, getPoisson11List, getPoisson11Detail } from '@/api/drawPrediction'

const queryDate = ref(new Date().toISOString().slice(0, 10))
const dataSource = ref('yingqiu_bd')
const loading = ref(false)
const fetching = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const tableKey = ref(0)

const detailVisible = ref(false)
const detailData = ref(null)

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

const hasData = (value) => !(value === null || value === undefined || value === '')

const formatSourceLabel = (source) => {
  const key = String(source || '').trim()
  if (!key || key === 'default') return '-'
  const map = {
    '500_bjdc_index.asianhand': '500北单首页-亚盘',
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
      name: 'xG / 进球数据',
      usage: '模型升级',
      required: '进阶',
      source: inferXgSource(attrs, xgHome, xgAway),
      value: xgValue
    }
  ]
})

const fetchList = async () => {
  loading.value = true
  try {
    tableData.value = []
    const res = await getPoisson11List({
      date_str: queryDate.value,
      data_source: dataSource.value,
      _ts: Date.now()
    })
    const items = res.items || []
    total.value = res.total || items.length
    const start = (currentPage.value - 1) * pageSize.value
    tableData.value = items.slice(start, start + pageSize.value)
    tableKey.value = Date.now()
  } catch (err) {
    console.error('获取扫盘列表失败:', err)
    ElMessage.error('获取扫盘列表失败')
  } finally {
    loading.value = false
  }
}

const handleFetch = async () => {
  fetching.value = true
  try {
    await fetchPoisson11({
      date_str: queryDate.value,
      data_source: dataSource.value,
      _ts: Date.now()
    })
    ElMessage.success('抓取完成')
    currentPage.value = 1
    await fetchList()
  } catch (err) {
    console.error('抓取失败:', err)
    ElMessage.error('抓取失败')
  } finally {
    fetching.value = false
  }
}

const resetFilter = () => {
  queryDate.value = new Date().toISOString().slice(0, 10)
  dataSource.value = 'yingqiu_bd'
  currentPage.value = 1
  fetchList()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchList()
}

const openDetail = async (row) => {
  try {
    const res = await getPoisson11Detail(row.match_id, { data_source: dataSource.value })
    detailData.value = res
    detailVisible.value = true
  } catch (err) {
    console.error('获取模型详情失败:', err)
    ElMessage.error('获取模型详情失败')
  }
}

const formatDateTime = (row, column, cellValue) => {
  if (!cellValue) return '-'
  const d = new Date(cellValue)
  if (Number.isNaN(d.getTime())) return String(cellValue)
  return d.toLocaleString()
}

onMounted(() => {
  fetchList()
})
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
</style>
