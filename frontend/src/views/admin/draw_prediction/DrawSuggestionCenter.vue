<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>下注建议中心</span>
          <div class="header-actions">
            <el-date-picker
              v-model="query.date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 160px"
            />
            <el-button :loading="submitting" @click="fetchSnapshots">采集快照</el-button>
            <el-button type="primary" :loading="submitting" @click="generateSuggestions">生成建议</el-button>
            <el-button type="warning" :loading="submitting" @click="settlePaperBets">执行结算</el-button>
          </div>
        </div>
      </template>

      <div class="metrics-row" v-loading="metricsLoading">
        <div class="metric-card">
          <div class="metric-label">Kill-Switch</div>
          <el-tag :type="stateTagType">{{ metrics.state || 'RUN' }}</el-tag>
        </div>
        <div class="metric-card">
          <div class="metric-label">ROI(7d)</div>
          <div class="metric-value">{{ formatPercent(metrics.roi_7d) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">回撤</div>
          <div class="metric-value">{{ formatPercent(metrics.max_drawdown) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">胜率</div>
          <div class="metric-value">{{ formatPercent(metrics.win_rate) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">CLV(50)</div>
          <div class="metric-value">{{ formatPercent(metrics.clv_50) }}</div>
        </div>
      </div>

      <div class="task-row">
        <div class="task-item">
          <div class="task-title">快照采集任务</div>
          <el-progress :percentage="safeProgress(snapshotTask.progress)" :status="taskStatus(snapshotTask.status)" />
          <div class="task-text">{{ snapshotTask.message || snapshotTask.status }}</div>
        </div>
        <div class="task-item">
          <div class="task-title">建议生成任务</div>
          <el-progress :percentage="safeProgress(generateTask.progress)" :status="taskStatus(generateTask.status)" />
          <div class="task-text">{{ generateTask.message || generateTask.status }}</div>
        </div>
        <div class="task-item">
          <div class="task-title">结算任务</div>
          <el-progress :percentage="safeProgress(settleTask.progress)" :status="taskStatus(settleTask.status)" />
          <div class="task-text">{{ settleTask.message || settleTask.status }}</div>
        </div>
      </div>

      <div class="toolbar">
        <el-select v-model="query.decision" clearable placeholder="决策筛选" style="width: 120px">
          <el-option label="BET" value="BET" />
          <el-option label="SKIP" value="SKIP" />
        </el-select>
        <el-button :loading="loading" @click="refreshSuggestions">刷新建议</el-button>
        <el-button :loading="snapshotsLoading" @click="refreshSnapshots">刷新快照</el-button>
        <el-button type="success" @click="handleBatchCreatePaperBets">创建模拟下注</el-button>
        <el-button type="primary" :loading="reportLoading" @click="handleGenerateReport">生成日报</el-button>
      </div>

      <el-table
        :data="suggestions"
        border
        style="width: 100%; margin-top: 16px"
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="match_id" label="比赛ID" min-width="180" />
        <el-table-column prop="decision" label="决策" width="90">
          <template #default="scope">
            <el-tag :type="scope.row.decision === 'BET' ? 'success' : 'info'">{{ scope.row.decision }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="stake_pct" label="仓位" width="90">
          <template #default="scope">{{ formatPercent(scope.row.stake_pct) }}</template>
        </el-table-column>
        <el-table-column prop="edge" label="Edge" width="90">
          <template #default="scope">{{ formatPercent(scope.row.edge) }}</template>
        </el-table-column>
        <el-table-column label="决策路径" min-width="300">
          <template #default="scope">
            <div class="decision-path">
              <div class="decision-main">{{ decisionPathShort(scope.row) }}</div>
              <el-button link type="primary" @click="copyDecisionPath(scope.row)">一键复制</el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="killswitch_state" label="风控状态" width="110" />
        <el-table-column prop="reason_codes" label="原因" min-width="180">
          <template #default="scope">{{ (scope.row.reason_codes || []).join(', ') || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="scope">
            <el-button
              size="small"
              :loading="!!explaining[String(scope.row.id)]"
              @click="handleExplain(scope.row)"
            >AI解读</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        :page-size="query.pageSize"
        :total="suggestionsTotal"
        layout="total, prev, pager, next"
        style="margin-top: 12px; text-align: right"
        @current-change="refreshSuggestions"
      />

      <div class="snapshot-panel">
        <div class="panel-title">最新赔率快照（{{ snapshotsTotal }}）</div>
        <el-table :data="snapshots" border size="small" v-loading="snapshotsLoading">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="match_id" label="比赛ID" min-width="180" />
          <el-table-column prop="fixture_id" label="外部ID" width="120" />
          <el-table-column prop="odds_draw" label="平赔" width="90" />
          <el-table-column prop="captured_at" label="采集时间" width="180">
            <template #default="scope">{{ formatDate(scope.row.captured_at) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <el-dialog v-model="explainVisible" title="AI解读" width="640px">
      <div class="explain-content">{{ activeExplanation || '暂无内容' }}</div>
      <template #footer>
        <el-button @click="explainVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reportVisible" title="AI日报" width="760px">
      <pre class="report-content">{{ latestReport || '暂无内容' }}</pre>
      <template #footer>
        <el-button @click="reportVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useDrawSuggestion } from '@/composables/useDrawSuggestion'

const {
  loading,
  snapshotsLoading,
  metricsLoading,
  submitting,
  suggestions,
  suggestionsTotal,
  snapshots,
  snapshotsTotal,
  metrics,
  query,
  snapshotTask,
  generateTask,
  settleTask,
  stateTagType,
  explanationMap,
  explaining,
  latestReport,
  reportLoading,
  refreshSuggestions,
  refreshSnapshots,
  refreshMetrics,
  fetchSnapshots,
  generateSuggestions,
  settlePaperBets,
  batchCreatePaperBets,
  explainSuggestion,
  generateReport
} = useDrawSuggestion()

const selectedRows = ref([])
const explainVisible = ref(false)
const activeExplanation = ref('')
const reportVisible = ref(false)

const betSelectedIds = computed(() => {
  return selectedRows.value
    .filter((x) => x.decision === 'BET')
    .map((x) => Number(x.id))
    .filter((x) => Number.isInteger(x) && x > 0)
})

const taskStatus = (status) => {
  const s = String(status || '').toLowerCase()
  if (s === 'success') return 'success'
  if (s === 'failed' || s === 'cancelled') return 'exception'
  return ''
}

const safeProgress = (v) => {
  const n = Number(v)
  if (!Number.isFinite(n)) return 0
  if (n < 0) return 0
  if (n > 100) return 100
  return Math.round(n)
}

const formatPercent = (v) => {
  if (typeof v !== 'number') return '-'
  return `${(v * 100).toFixed(2)}%`
}

const formatDate = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v)
  return d.toLocaleString()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = Array.isArray(rows) ? rows : []
}

const handleBatchCreatePaperBets = async () => {
  if (!betSelectedIds.value.length) {
    ElMessage.warning('请先勾选 decision=BET 的建议')
    return
  }
  try {
    const result = await batchCreatePaperBets(betSelectedIds.value)
    ElMessage.success(`已创建 ${result?.created_count || 0} 条模拟下注`)
    await refreshMetrics()
  } catch (err) {
    console.error('创建模拟下注失败:', err)
    ElMessage.error('创建模拟下注失败')
  }
}

const handleExplain = async (row) => {
  try {
    const text = await explainSuggestion(row.id)
    activeExplanation.value = explanationMap[String(row.id)] || text || '暂无内容'
    explainVisible.value = true
  } catch (err) {
    console.error('获取AI解读失败:', err)
    ElMessage.error('获取AI解读失败')
  }
}

const toNumber = (v) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

const buildDecisionPath = (row) => {
  const features = row?.features || {}
  const baseProb = toNumber(features.base_prob ?? features.base_draw_prob)
  const oddsDraw = toNumber(features.odds_draw_place ?? features.odds_draw)
  const impliedProbRaw = toNumber(features.implied_prob)
  const impliedProb = oddsDraw && oddsDraw > 0 ? 1 / oddsDraw : impliedProbRaw
  const edge = toNumber(row?.edge)
  const edgeMin = toNumber(features.edge_min ?? features.edge_threshold)
  const decision = String(row?.decision || '-').toUpperCase()
  const killSwitchState = String(row?.killswitch_state || metrics.value?.state || 'RUN').toUpperCase()

  const parts = [
    `Base=${baseProb == null ? '-' : formatPercent(baseProb)}`,
    `Implied=${impliedProb == null ? '-' : formatPercent(impliedProb)}`,
    `Edge=${edge == null ? '-' : formatPercent(edge)}`,
    `Min=${edgeMin == null ? '-' : formatPercent(edgeMin)}`,
    `KS=${killSwitchState}`,
    `Decision=${decision}`
  ]

  return {
    short: `${parts[0]} | ${parts[1]} | ${parts[2]} > ${parts[3]} | ${parts[4]} => ${parts[5]}`,
    full: parts.join(' | ')
  }
}

const decisionPathShort = (row) => buildDecisionPath(row).short

const copyDecisionPath = async (row) => {
  const text = buildDecisionPath(row).full
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const input = document.createElement('textarea')
      input.value = text
      input.style.position = 'fixed'
      input.style.opacity = '0'
      document.body.appendChild(input)
      input.focus()
      input.select()
      const copied = document.execCommand('copy')
      document.body.removeChild(input)
      if (!copied) {
        throw new Error('execCommand copy returned false')
      }
    }
    ElMessage.success('决策路径已复制')
  } catch (_) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const handleGenerateReport = async () => {
  try {
    await generateReport('daily')
    reportVisible.value = true
  } catch (err) {
    console.error('生成日报失败:', err)
    ElMessage.error('生成日报失败')
  }
}

onMounted(async () => {
  const now = new Date()
  const yyyy = now.getFullYear()
  const mm = `${now.getMonth() + 1}`.padStart(2, '0')
  const dd = `${now.getDate()}`.padStart(2, '0')
  query.date = `${yyyy}-${mm}-${dd}`

  await Promise.all([refreshSuggestions(), refreshSnapshots(), refreshMetrics()])
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.metrics-row { display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 10px; margin-bottom: 14px; }
.metric-card { border: 1px solid #ebeef5; border-radius: 6px; padding: 10px; background: #fff; }
.metric-label { color: #909399; font-size: 12px; margin-bottom: 6px; }
.metric-value { font-weight: 700; color: #303133; }
.task-row { display: grid; grid-template-columns: repeat(3, minmax(200px, 1fr)); gap: 10px; margin-bottom: 14px; }
.task-item { border: 1px dashed #dcdfe6; border-radius: 6px; padding: 10px; }
.task-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.task-text { margin-top: 6px; font-size: 12px; color: #606266; }
.toolbar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.decision-path { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.decision-main { color: #303133; font-size: 12px; line-height: 1.5; }
.snapshot-panel { margin-top: 18px; }
.panel-title { font-weight: 600; margin-bottom: 8px; }
.explain-content { white-space: pre-wrap; line-height: 1.7; color: #303133; }
.report-content { white-space: pre-wrap; background: #f7f8fa; border-radius: 6px; padding: 12px; max-height: 420px; overflow-y: auto; }
</style>
