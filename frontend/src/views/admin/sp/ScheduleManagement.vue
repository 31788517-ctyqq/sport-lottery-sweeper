<template>
  <div class="schedule-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
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
          <el-input v-model="queryParams.leagueName" placeholder="输入赛事" clearable style="width: 180px" />
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

      <el-table :data="scheduleList" v-loading="loading" stripe height="560" style="width: 100%">
        <el-table-column prop="number" label="编号" width="90" />
        <el-table-column prop="leagueName" label="赛事" width="130" show-overflow-tooltip />
        <el-table-column prop="matchTime" label="开赛时间" width="170" />
        <el-table-column v-if="isBd" prop="statusText" label="状态" width="100" align="center" />
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
              <span class="sub">{{ row.oddsSpfWin }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="平" width="98" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.oddsNspfDraw }}</span>
              <span class="sub">{{ row.oddsSpfDraw }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="负" width="98" align="center">
          <template #default="{ row }">
            <div class="dual-line">
              <span>{{ row.oddsNspfLose }}</span>
              <span class="sub">{{ row.oddsSpfLose }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column v-if="isJczq || isBd" label="其它赔率" width="110" align="center" fixed="right">
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
      title="其它公司赔率汇总"
      width="860px"
      :close-on-click-modal="false"
    >
      <el-table :data="otherOddsRows" v-loading="otherOddsLoading" stripe max-height="480">
        <el-table-column prop="company" label="公司" min-width="220" show-overflow-tooltip />
        <el-table-column prop="updatedAt" label="更新时间" width="170" />
        <el-table-column prop="initWin" label="初赔胜" width="90" align="center" />
        <el-table-column prop="initDraw" label="初赔平" width="90" align="center" />
        <el-table-column prop="initLose" label="初赔负" width="90" align="center" />
        <el-table-column prop="instantWin" label="即时胜" width="90" align="center" />
        <el-table-column prop="instantDraw" label="即时平" width="90" align="center" />
        <el-table-column prop="instantLose" label="即时负" width="90" align="center" />
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

const API_BASE = '/api/v1/admin/lottery-schedules/lottery-schedules'
const isJczq = computed(() => props.scheduleType === 'jczq')
const isBd = computed(() => props.scheduleType === 'bd')

const title = computed(() => (isJczq.value ? '竞彩赛程管理' : '北单赛程管理'))
const subtitle = computed(() => (isJczq.value ? '支持按日期从500W抓取竞彩赛程并入库' : '支持按日期从盈球抓取北单赛程并入库'))

const scheduleList = ref([])
const loading = ref(false)
const crawlLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const crawlDate = ref(new Date().toISOString().slice(0, 10))
const otherOddsVisible = ref(false)
const otherOddsLoading = ref(false)
const otherOddsRows = ref([])

const queryParams = reactive({
  leagueName: '',
  matchDate: ''
})

const formatOdds = (v) => {
  if (v === null || v === undefined || v === '') return '-'
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : String(v)
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
  halftimeScore: normalizeScore(row.halftime_score ?? row.half_score ?? row.halfTimeScore)
})

const getScheduleList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      schedule_type: props.scheduleType
    }

    if (queryParams.leagueName) {
      params.league_name = queryParams.leagueName
    }
    if (queryParams.matchDate) {
      params.date_from = queryParams.matchDate
      params.date_to = queryParams.matchDate
    }

    const data = await request.get(`${API_BASE}/`, { params })
    const mapper = isBd.value ? mapBdRow : mapJczqRow
    scheduleList.value = (data.items || []).map(mapper)
    total.value = data.total || 0
  } catch (error) {
    console.error('加载赛程失败:', error)
    ElMessage.error('加载赛程失败')
  } finally {
    loading.value = false
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
    await getScheduleList()
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
    await getScheduleList()
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
  otherOddsRows.value = []
  try {
    const data = await request.get(`${API_BASE}/${row.id}/other-odds`, {
      params: { force_refresh: false },
      timeout: 60000
    })
    otherOddsRows.value = (data.items || []).map((x) => ({
      company: x.company || '-',
      updatedAt: x.updated_at || '-',
      initWin: formatOdds(x.init_win),
      initDraw: formatOdds(x.init_draw),
      initLose: formatOdds(x.init_lose),
      instantWin: formatOdds(x.instant_win),
      instantDraw: formatOdds(x.instant_draw),
      instantLose: formatOdds(x.instant_lose)
    }))
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
  getScheduleList()
}

const resetQuery = () => {
  queryParams.leagueName = ''
  queryParams.matchDate = ''
  currentPage.value = 1
  getScheduleList()
}

const refreshData = () => {
  getScheduleList()
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
    getScheduleList()
  }
)
</script>

<style scoped>
.schedule-management {
  padding: 20px;
}

.card-container {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
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
  color: #1f2937;
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

.score-text {
  color: #dc2626;
  font-weight: 700;
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

@media (max-width: 900px) {
  .schedule-management {
    padding: 12px;
  }
}
</style>
