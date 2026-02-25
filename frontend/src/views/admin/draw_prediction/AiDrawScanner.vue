<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>北单平局预测扫盘（北单 / 盈球）</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleFetch" :loading="fetching">手动抓取并计算</el-button>
            <el-button @click="openRules">计算规则</el-button>
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
            <el-option label="盈球（北单）" value="yingqiu_bd" />
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
          <el-table-column prop="league" label="联赛" width="120" />
          <el-table-column prop="home_team" label="主队" />
          <el-table-column prop="away_team" label="客队" />
          <el-table-column prop="score" label="比分" width="90" :formatter="formatScore" />
          <el-table-column prop="odds_win" label="主胜" width="90" :formatter="formatNumber" />
          <el-table-column prop="odds_draw" label="平" width="90" :formatter="formatNumber" />
          <el-table-column prop="odds_lose" label="客胜" width="90" :formatter="formatNumber" />
          <el-table-column prop="total_goals_line" label="大小球" width="90" :formatter="formatNumber" />
        <el-table-column prop="prob_draw" label="平局概率" width="120">
          <template #default="scope">
            {{ formatPercent(scope.row.prob_draw) }}
          </template>
        </el-table-column>
        <el-table-column prop="p_value" label="P值" width="90">
          <template #default="scope">
            {{ formatValue(scope.row.p_value ?? scope.row.prob_draw, 3) }}
          </template>
        </el-table-column>

          <el-table-column prop="recommendation" label="推荐" width="90" />
          <el-table-column prop="rank" label="排名" width="70" />
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" @click="openDetail(scope.row)">模型数据</el-button>
            <el-button size="small" type="primary" @click="openOptimize(scope.row)">优化</el-button>
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
      <el-descriptions-item label="联赛">{{ detailData.league || '-' }}</el-descriptions-item>
      <el-descriptions-item label="比赛时间">{{ formatDateTime(null, null, detailData.match_time) }}</el-descriptions-item>
      <el-descriptions-item label="平局概率">{{ formatPercent(detailData.prob_draw) }}</el-descriptions-item>
      <el-descriptions-item label="A 实力接近">
        <el-input v-model="detailEdit.a" placeholder="-" />
      </el-descriptions-item>
      <el-descriptions-item label="B 平赔结构">
        <el-input v-model="detailEdit.b" placeholder="-" />
      </el-descriptions-item>
      <el-descriptions-item label="C 小球环境">
        <el-input v-model="detailEdit.c" placeholder="-" />
      </el-descriptions-item>
      <el-descriptions-item label="D 战意">
        <el-input v-model="detailEdit.d" placeholder="-" />
      </el-descriptions-item>
      <el-descriptions-item label="推荐">{{ detailData.recommendation || '-' }}</el-descriptions-item>
      <el-descriptions-item label="排名">{{ formatValue(detailData.rank, 0) }}</el-descriptions-item>
    </el-descriptions>

        <div class="index-logic">
          <div class="index-logic-title">A/B/C/D 指数计算逻辑</div>
          <ul class="index-logic-list">
            <li><strong>A 实力接近</strong>：A=exp(-3×|ln(主胜/客胜)|)，值在 0–1 之间。</li>
            <li><strong>B 平赔结构</strong>：B=exp(-((平赔-3.05)/0.45)^2)，值在 0–1 之间。</li>
            <li><strong>C 小球环境</strong>：C=exp(-0.9×(大小球-2.2))，值在 0–1 之间。</li>
            <li><strong>D 战意指数</strong>：默认取值 0。场景取值：双方满意平 +0.6、首回合淘汰赛 +0.4、普通联赛 0、必须分胜负 -0.6。</li>
          </ul>
        </div>

        <div class="index-logic">
          <div class="index-logic-title">取值来源与计算过程</div>
          <ul class="index-logic-list">
            <li v-for="(item, idx) in detailCalcRows" :key="idx">{{ item }}</li>
          </ul>
        </div>

        <h4 style="margin: 16px 0 8px">模型输入四类数据</h4>
        <el-table :data="modelDataRows" border size="small" class="model-input-table">
          <el-table-column prop="name" label="数据" width="140" />
          <el-table-column prop="usage" label="用途" />
          <el-table-column prop="required" label="是否必须" width="90" />
          <el-table-column prop="value" label="取值" width="260" />
        </el-table>

        <h4 style="margin: 16px 0 8px">输入与中间量</h4>
        <pre class="json-box">{{ detailPayload }}</pre>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveDetailOverrides">保存A/B/C/D</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rulesVisible" title="计算规则" width="720px">
      <div class="rules-formula">
        <div class="rules-formula-title">计算公式</div>
        <div class="rules-formula-content">
          P(Draw)=0.248+0.32A+0.28C+0.24B+0.16D
        </div>
        <div class="rules-formula-sub">最终会按平局概率从高到低排序，并根据阈值给出推荐。</div>
      </div>
      <el-form :model="rulesForm" label-width="140px" class="rules-form">
        <el-form-item label="基础项">
          <el-input-number v-model="rulesForm.base" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">基础概率偏置，整体上移或下调。</div>
        </el-form-item>
        <el-form-item label="权重 A">
          <el-input-number v-model="rulesForm.weights.a" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 A 指数（实力接近，0–1）。A=exp(-3×|ln(主胜/客胜)|)。</div>
        </el-form-item>
        <el-form-item label="权重 C">
          <el-input-number v-model="rulesForm.weights.c" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 C 指数（小球环境，0–1）。C=exp(-0.9×(大小球-2.2))，并裁剪到0~1。</div>
        </el-form-item>
        <el-form-item label="权重 B">
          <el-input-number v-model="rulesForm.weights.b" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 B 指数（平赔结构/市场定价，0–1）。B=exp(-((平赔-3.05)/0.45)^2)。</div>
        </el-form-item>
        <el-form-item label="权重 D">
          <el-input-number v-model="rulesForm.weights.d" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 D 指数（战意，-1～1），可选加权。场景取值如下：</div>
          <table class="rule-table">
            <thead>
              <tr>
                <th>场景</th>
                <th>D值</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>双方满意平</td>
                <td>+0.6</td>
              </tr>
              <tr>
                <td>首回合淘汰赛</td>
                <td>+0.4</td>
              </tr>
              <tr>
                <td>普通联赛</td>
                <td>0</td>
              </tr>
              <tr>
                <td>必须分胜负</td>
                <td>-0.6</td>
              </tr>
            </tbody>
          </table>
        </el-form-item>
        <el-form-item label="高平阈值">
          <el-input-number v-model="rulesForm.thresholds.high" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">概率 ≥ 此值标记为“高平”。</div>
        </el-form-item>
        <el-form-item label="偏高阈值">
          <el-input-number v-model="rulesForm.thresholds.midHigh" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">概率 ≥ 此值标记为“偏高”。</div>
        </el-form-item>
        <el-form-item label="正常阈值">
          <el-input-number v-model="rulesForm.thresholds.normal" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">概率 ≥ 此值标记为“正常”。</div>
        </el-form-item>
        <el-form-item label="偏低阈值">
          <el-input-number v-model="rulesForm.thresholds.low" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">低于“正常阈值”且 ≥ 此值标记为“偏低”，低于该值为“不推荐”。</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetRules">恢复默认</el-button>
        <el-button @click="rulesVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRules">保存并应用</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="optimizeVisible" title="单场优化" width="720px">
      <div class="rules-formula">
        <div class="rules-formula-title">计算公式</div>
        <div class="rules-formula-content">
          P(Draw)=0.248+0.32A+0.28C+0.24B+0.16D
        </div>
        <div class="rules-formula-sub">仅对当前场次生效，优先于全局“计算规则”。</div>
        <div class="rules-formula-sub">{{ optimizeCalcText }}</div>
      </div>
      <el-form :model="optimizeForm" label-width="140px" class="rules-form">
        <el-form-item label="基础项">
          <el-input-number v-model="optimizeForm.base" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">基础概率偏置，整体上移或下调。</div>
        </el-form-item>
        <el-form-item label="权重 A">
          <el-input-number v-model="optimizeForm.weights.a" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 A 指数（实力接近，0–1）。A=exp(-3×|ln(主胜/客胜)|)。</div>
        </el-form-item>
        <el-form-item label="权重 C">
          <el-input-number v-model="optimizeForm.weights.c" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 C 指数（小球环境，0–1）。C=exp(-0.9×(大小球-2.2))，并裁剪到0~1。</div>
        </el-form-item>
        <el-form-item label="权重 B">
          <el-input-number v-model="optimizeForm.weights.b" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 B 指数（平赔结构/市场定价，0–1）。B=exp(-((平赔-3.05)/0.45)^2)。</div>
        </el-form-item>
        <el-form-item label="权重 D">
          <el-input-number v-model="optimizeForm.weights.d" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">对应 D 指数（战意，-1～1），可选加权。场景取值如下：</div>
          <table class="rule-table">
            <thead>
              <tr>
                <th>场景</th>
                <th>D值</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>双方满意平</td>
                <td>+0.6</td>
              </tr>
              <tr>
                <td>首回合淘汰赛</td>
                <td>+0.4</td>
              </tr>
              <tr>
                <td>普通联赛</td>
                <td>0</td>
              </tr>
              <tr>
                <td>必须分胜负</td>
                <td>-0.6</td>
              </tr>
            </tbody>
          </table>
        </el-form-item>
        <el-form-item label="高平阈值">
          <el-input-number v-model="optimizeForm.thresholds.high" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">概率 ≥ 此值标记为“高平”。</div>
        </el-form-item>
        <el-form-item label="偏高阈值">
          <el-input-number v-model="optimizeForm.thresholds.midHigh" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">概率 ≥ 此值标记为“偏高”。</div>
        </el-form-item>
        <el-form-item label="正常阈值">
          <el-input-number v-model="optimizeForm.thresholds.normal" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">概率 ≥ 此值标记为“正常”。</div>
        </el-form-item>
        <el-form-item label="偏低阈值">
          <el-input-number v-model="optimizeForm.thresholds.low" :precision="3" :step="0.01" :min="0" :max="1" />
          <div class="rule-help">低于“正常阈值”且 ≥ 此值标记为“偏低”，低于该值为“不推荐”。</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetOptimizeRules">恢复默认</el-button>
        <el-button @click="optimizeVisible = false">取消</el-button>
        <el-button type="primary" @click="saveOptimizeRules">保存并应用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  startAiDrawFetchTask,
  getDrawPredictionTask,
  getAiDrawList,
  getAiDrawDetail,
  getAiDrawRules,
  saveAiDrawRules,
  getAiDrawMatchRules,
  saveAiDrawMatchRules,
  getAiDrawMatchOverrides,
  saveAiDrawMatchOverrides,
  importYingqiuBdSchedule,
  getBdIssueOptions,
  getBdLeagueOptions
} from '@/api/drawPrediction'

const queryDate = ref(new Date().toISOString().slice(0, 10))
const queryIssueNo = ref('')
const queryLeague = ref('')
const dataSource = ref('yingqiu_bd')
const issueOptions = ref([])
const issueOptionsLoading = ref(false)
const leagueOptions = ref([])
const leagueOptionsLoading = ref(false)
const resolvedIssueDates = ref([])
const loading = ref(false)
const fetching = ref(false)
const fetchTaskId = ref('')
const fetchTaskStatus = ref('')
const fetchTaskProgress = ref(0)
const fetchTaskMessage = ref('')
let fetchTaskPollTimer = null
let fetchTaskStartedAt = 0
const FETCH_TASK_POLL_INTERVAL_MS = 1200
const FETCH_TASK_TIMEOUT_MS = 10 * 60 * 1000
const tableData = ref([])
const allItems = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const tableKey = ref(0)

const detailVisible = ref(false)
const detailData = ref(null)
const detailEdit = ref({ a: '-', b: '-', c: '-', d: '-' })

const defaultRules = {
  base: 0.248,
  weights: {
    a: 0.32,
    b: 0.24,
    c: 0.28,
    d: 0.16
  },
  thresholds: {
    high: 0.36,
    midHigh: 0.31,
    normal: 0.26,
    low: 0.22
  }
}
const rulesVisible = ref(false)
const rulesForm = ref(JSON.parse(JSON.stringify(defaultRules)))
const optimizeVisible = ref(false)
const optimizeForm = ref(JSON.parse(JSON.stringify(defaultRules)))
const optimizingMatch = ref(null)

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

const formatScore = (row, column, cellValue) => formatValue(cellValue, 0)

const formatPercent = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = Number(value)
  if (!Number.isFinite(num)) return '-'
  return `${(num * 100).toFixed(2)}%`
}

const toNum = (value) => {
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

const totalGoalsSourceLabel = (source) => {
  if (source === 'yingqiu_goals_crown') return '北单详情-进球数-皇冠'
  if (source === '500w_crown') return '500w 皇冠'
  if (source === 'inferred_from_draw_odds') return '平赔推断'
  if (source === 'source_attributes') return '源数据'
  return '-'
}

const aSourceLabel = (source) => {
  if (source === '100qiu_power') return '100qiu 实力指数'
  if (source === 'missing') return '缺失'
  return '-'
}

const modelDataRows = computed(() => {
  const payload = detailData.value?.input_payload || {}
  const indices = payload.indices || {}
  return [
    { name: 'A 实力接近', usage: 'A=exp(-3×|ln(主胜/客胜)|)，0–1', required: '必须', value: formatValue(indices.a, 3) },
    { name: 'B 平赔结构', usage: 'B=exp(-((平赔-3.05)/0.45)^2)，0–1', required: '必须', value: formatValue(indices.b) },
    { name: 'C 小球环境', usage: 'C=exp(-0.9×(大小球-2.2))，0–1', required: '必须', value: formatValue(indices.c) },
    { name: 'D 战意指数', usage: '默认0；场景：+0.6/+0.4/0/-0.6', required: '可选', value: formatValue(indices.d) }
  ]
})

const detailCalcRows = computed(() => {
  const payload = detailData.value?.input_payload || {}
  const odds = payload.odds || {}
  const indices = payload.indices || {}
  const totalGoals = payload.total_goals_line
  const inferred = payload.inferred_total_goals_line
  const source = payload.total_goals_line_source || (inferred !== null && inferred !== undefined ? 'inferred_from_draw_odds' : (totalGoals !== null && totalGoals !== undefined ? 'source_attributes' : null))
  const oddsDraw = toNum(odds.draw)
  const totalGoalsNum = toNum(totalGoals)
  const bCalc = oddsDraw === null ? null : Math.exp(-Math.pow((oddsDraw - 3.05) / 0.45, 2))
  const cRaw = totalGoalsNum === null ? null : Math.exp(-0.9 * (totalGoalsNum - 2.2))
  const cClamped = cRaw === null ? null : Math.max(0, Math.min(1, cRaw))
  const aSource = payload.a_index_source
  const aInputs = payload.a_inputs || {}
  const homePower = toNum(aInputs.home_power)
  const awayPower = toNum(aInputs.away_power)
  const aCalc = homePower === null || awayPower === null ? null : Math.exp(-3 * Math.abs(Math.log(homePower / awayPower)))
  return [
    `A 取值来源：${aSourceLabel(aSource)}`,
    `A 输入：主队实力=${formatValue(homePower, 3)}，客队实力=${formatValue(awayPower, 3)}`,
    `A 计算：A=exp(-3×|ln(主队实力/客队实力)|)，结果=${formatValue(aCalc, 3)}`,
    `大小球取值来源：${totalGoalsSourceLabel(source)}`,
    `大小球取值：${formatValue(totalGoalsNum, 2)}`,
    `B 计算：B=exp(-((平赔-3.05)/0.45)^2)，平赔=${formatValue(oddsDraw, 2)}，结果=${formatValue(bCalc, 3)}`,
    `C 计算：C=exp(-0.9×(大小球-2.2))，大小球=${formatValue(totalGoalsNum, 2)}，原始=${formatValue(cRaw, 3)}，裁剪后=${formatValue(cClamped, 3)}`,
    `A 当前值：${formatValue(indices.a, 3)}；D 当前值：${formatValue(indices.d)}`
  ]
})

const optimizeCalcText = computed(() => {
  if (!optimizingMatch.value) return '本场比赛真实值计算过程：-'
  const weights = optimizeForm.value?.weights || {}
  const base = Number(optimizeForm.value?.base ?? 0)
  const aRaw = optimizingMatch.value?.a_index
  const bRaw = optimizingMatch.value?.b_index
  const cRaw = optimizingMatch.value?.c_index
  const dRaw = optimizingMatch.value?.d_index
  const toNum = (val) => {
    const num = Number(val)
    return Number.isFinite(num) ? num : null
  }
  const a = toNum(aRaw)
  const b = toNum(bRaw)
  const c = toNum(cRaw)
  const d = toNum(dRaw)
  const wa = Number(weights.a ?? 0)
  const wb = Number(weights.b ?? 0)
  const wc = Number(weights.c ?? 0)
  const wd = Number(weights.d ?? 0)
  const safe = (val) => (val === null ? 0 : val)
  const result = base + wa * safe(a) + wc * safe(c) + wb * safe(b) + wd * safe(d)
  const fmt = (val, digits = 3) => (val === null ? '-' : Number(val).toFixed(digits))
  return `本场比赛真实值计算过程：P=${base.toFixed(3)}+${wa.toFixed(3)}×A(${fmt(a)})+${wc.toFixed(3)}×C(${fmt(c)})+${wb.toFixed(3)}×B(${fmt(b)})+${wd.toFixed(3)}×D(${fmt(d)})=${result.toFixed(4)}`
})

const normalizeRules = (rules) => {
  const parsed = rules || {}
  return {
    base: Number(parsed.base ?? defaultRules.base),
    weights: {
      a: Number(parsed.weights?.a ?? defaultRules.weights.a),
      b: Number(parsed.weights?.b ?? defaultRules.weights.b),
      c: Number(parsed.weights?.c ?? defaultRules.weights.c),
      d: Number(parsed.weights?.d ?? defaultRules.weights.d)
    },
    thresholds: {
      high: Number(parsed.thresholds?.high ?? defaultRules.thresholds.high),
      midHigh: Number(parsed.thresholds?.midHigh ?? defaultRules.thresholds.midHigh),
      normal: Number(parsed.thresholds?.normal ?? defaultRules.thresholds.normal),
      low: Number(parsed.thresholds?.low ?? defaultRules.thresholds.low)
    }
  }
}

const loadRules = async () => {
  try {
    const res = await getAiDrawRules()
    rulesForm.value = normalizeRules(res.rules)
  } catch (e) {
    console.warn('读取计算规则失败:', e)
    rulesForm.value = normalizeRules(defaultRules)
  }
}

const saveRules = async () => {
  rulesForm.value = normalizeRules(rulesForm.value)
  try {
    await saveAiDrawRules(rulesForm.value)
    rulesVisible.value = false
    ElMessage.success('规则已保存并应用')
    await fetchList()
  } catch (e) {
    console.error('保存计算规则失败:', e)
    ElMessage.error('保存规则失败')
  }
}

const resetRules = () => {
  rulesForm.value = JSON.parse(JSON.stringify(defaultRules))
}

const openRules = () => {
  rulesVisible.value = true
}

const resetOptimizeRules = () => {
  optimizeForm.value = JSON.parse(JSON.stringify(rulesForm.value))
}

const openOptimize = async (row) => {
  optimizingMatch.value = row
  optimizeVisible.value = true
  try {
    const res = await getAiDrawMatchRules(row.match_id)
    optimizeForm.value = normalizeRules(res.rules || rulesForm.value)
  } catch (e) {
    console.warn('读取单场规则失败:', e)
    optimizeForm.value = normalizeRules(rulesForm.value)
  }
}

const saveOptimizeRules = async () => {
  if (!optimizingMatch.value?.match_id) return
  optimizeForm.value = normalizeRules(optimizeForm.value)
  try {
    await saveAiDrawMatchRules(optimizingMatch.value.match_id, optimizeForm.value)
    optimizeVisible.value = false
    ElMessage.success('单场优化已保存并应用')
    await fetchList()
  } catch (e) {
    console.error('保存单场规则失败:', e)
    ElMessage.error('保存单场规则失败')
  }
}

const normalizeIssueNo = (value) => String(value || '').trim()

const isValidIssueNo = (value) => /^\d{5}$/.test(normalizeIssueNo(value))

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
    if (queryLeague.value) {
      queryLeague.value = ''
    }
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
    if (!silent) {
      ElMessage.error('加载赛事选项失败')
    }
  } finally {
    leagueOptionsLoading.value = false
  }
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
    await loadLeagueOptions({ silent: true })
    tableData.value = []

    const targetDates = issueNo
      ? [...resolvedIssueDates.value]
      : (queryDate.value ? [queryDate.value] : [])
    if (!targetDates.length) {
      allItems.value = []
      total.value = 0
      tableData.value = []
      tableKey.value = Date.now()
      return
    }

    const responses = await Promise.all(
      targetDates.map((dateStr, idx) => getAiDrawList({
        date_str: dateStr,
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
    const items = Array.from(uniqueMap.values())
      .filter((item) => (leagueName ? String(item?.league || '').trim() === leagueName : true))
      .sort((a, b) => Number(b?.prob_draw || 0) - Number(a?.prob_draw || 0))
      .map((item, idx) => ({ ...item, rank: idx + 1 }))

    allItems.value = items
    total.value = allItems.value.length
    const start = (currentPage.value - 1) * pageSize.value
    tableData.value = allItems.value.slice(start, start + pageSize.value)
    tableKey.value = Date.now()
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
    await importYingqiuBdSchedule({ schedule_date: queryDate.value })
    const taskResp = await startAiDrawFetchTask({
      date_str: queryDate.value,
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
  queryIssueNo.value = ''
  queryLeague.value = ''
  resolvedIssueDates.value = []
  currentPage.value = 1
  loadLeagueOptions({ silent: true })
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

const toDisplayValue = (value, digits = null) => {
  if (value === null || value === undefined || value === '') return '-'
  if (digits !== null) {
    const num = Number(value)
    if (!Number.isFinite(num)) return '-'
    return num.toFixed(digits)
  }
  return String(value)
}

const parseOverrideValue = (value) => {
  if (value === null || value === undefined) return null
  const text = String(value).trim()
  if (!text || text === '-') return null
  const num = Number(text)
  if (!Number.isFinite(num)) return null
  return num
}

const openDetail = async (row) => {
  try {
    const res = await getAiDrawDetail(row.match_id)
    detailData.value = res
    detailEdit.value = {
      a: toDisplayValue(res.a_index, 3),
      b: toDisplayValue(res.b_index),
      c: toDisplayValue(res.c_index),
      d: toDisplayValue(res.d_index)
    }
    try {
      const overrides = await getAiDrawMatchOverrides(row.match_id)
      if (overrides?.overrides) {
        detailEdit.value = {
          a: toDisplayValue(overrides.overrides.a ?? detailEdit.value.a, 3),
          b: toDisplayValue(overrides.overrides.b ?? detailEdit.value.b),
          c: toDisplayValue(overrides.overrides.c ?? detailEdit.value.c),
          d: toDisplayValue(overrides.overrides.d ?? detailEdit.value.d)
        }
      }
    } catch (e) {
      console.warn('读取单场修正值失败:', e)
    }
    detailVisible.value = true
  } catch (err) {
    console.error('获取详情失败:', err)
    ElMessage.error('获取详情失败')
  }
}

const saveDetailOverrides = async () => {
  if (!detailData.value?.match_id) return
  try {
    await saveAiDrawMatchOverrides(detailData.value.match_id, {
      a: parseOverrideValue(detailEdit.value.a),
      b: parseOverrideValue(detailEdit.value.b),
      c: parseOverrideValue(detailEdit.value.c),
      d: parseOverrideValue(detailEdit.value.d)
    })
    const res = await getAiDrawDetail(detailData.value.match_id)
    detailData.value = res
    ElMessage.success('A/B/C/D 已保存')
    fetchList()
  } catch (err) {
    console.error('保存A/B/C/D失败:', err)
    ElMessage.error('保存A/B/C/D失败')
  }
}

const formatDateTime = (row, column, cellValue) => {
  const value = cellValue || (row && row.match_time) || row
  if (!value) return '-'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return String(value)
  const yyyy = dt.getFullYear()
  const mm = String(dt.getMonth() + 1).padStart(2, '0')
  const dd = String(dt.getDate()).padStart(2, '0')
  const hh = String(dt.getHours()).padStart(2, '0')
  const mi = String(dt.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}

onMounted(async () => {
  await loadRules()
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
.page-container {
  padding: 20px;
}

.box-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
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

.index-logic {
  margin: 12px 0 4px;
  padding: 10px 12px;
  background: #f9fafc;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
}

.index-logic-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: #303133;
}

.index-logic-list {
  margin: 0;
  padding-left: 18px;
}

.index-logic-list li {
  line-height: 1.5;
}

.rules-formula {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 14px;
}

.rules-formula-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.rules-formula-content {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  color: #303133;
  margin-bottom: 6px;
}

.rules-formula-sub {
  color: #909399;
  font-size: 12px;
}

.rule-help {
  margin-top: 6px;
  color: #909399;
  font-size: 12px;
}

.rule-table {
  margin-top: 8px;
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  color: #606266;
}

.rule-table th,
.rule-table td {
  border: 1px solid #ebeef5;
  padding: 6px 8px;
  text-align: left;
}

.rule-table thead {
  background: #f5f7fa;
}
</style>
