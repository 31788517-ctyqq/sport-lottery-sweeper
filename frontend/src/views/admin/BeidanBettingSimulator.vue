<template>
  <div class="beidan-betting-simulator">
    <el-card class="page-card">
      <div class="page-header">
        <div class="title">北单投注模拟</div>
        <div class="actions">
          <el-button size="small" @click="refreshAll" :loading="loadingMatches || loadingSchemes">刷新</el-button>
        </div>
      </div>

      <el-form :inline="true" class="control-form">
        <el-form-item label="期号">
          <el-select v-model="selectedExpect" placeholder="选择期号" @change="handleExpectChange" style="width: 180px">
            <el-option
              v-for="option in expectOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="方案名称">
          <el-input v-model="schemeName" placeholder="自动生成" style="width: 200px" />
        </el-form-item>
        <el-form-item label="投注注数">
          <el-input :model-value="betCount" disabled style="width: 120px" />
        </el-form-item>
        <el-form-item label="投注金额(每注2元)">
          <el-input :model-value="betAmount" disabled style="width: 140px" />
        </el-form-item>
        <el-form-item label="串关类型">
          <el-select
            v-model="passTypes"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="选择串关"
            style="width: 220px"
          >
            <el-option
              v-for="option in passTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :disabled="!canCreate" @click="createScheme">保存方案</el-button>
          <el-button @click="resetSelections">清空选择</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">比赛列表</div>
      </template>
      <el-table :data="matches" v-loading="loadingMatches" height="420">
        <el-table-column prop="matchSeq" label="场次" width="80" />
        <el-table-column label="对阵" min-width="240">
          <template #default="{ row }">
            <div class="teams">{{ row.homeTeam }} vs {{ row.awayTeam }}</div>
            <div class="time">{{ row.matchTime }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" :formatter="formatText" />
        <el-table-column prop="scoreDisplay" label="比分/半场" width="120" :formatter="formatText" />
        <el-table-column prop="handicap" label="让球" width="80" :formatter="formatText" />
        <el-table-column label="赔率(胜/平/负)" min-width="260">
          <template #default="{ row }">
            <div class="odds-editor">
              <el-input-number v-model="row.odds.homeWin" :min="0" :step="0.01" size="small" controls-position="right" />
              <el-input-number v-model="row.odds.draw" :min="0" :step="0.01" size="small" controls-position="right" />
              <el-input-number v-model="row.odds.guestWin" :min="0" :step="0.01" size="small" controls-position="right" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="选择" min-width="240">
          <template #default="{ row }">
            <el-checkbox-group v-model="selections[row.matchSeq]" size="small" :disabled="isSelectionLocked(row)">
              <el-checkbox-button value="win">胜</el-checkbox-button>
              <el-checkbox-button value="draw">平</el-checkbox-button>
              <el-checkbox-button value="lose">负</el-checkbox-button>
            </el-checkbox-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">投注统计</div>
      </template>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-title">模拟投注统计</div>
          <div class="stat-row">
            <span>方案数</span>
            <span>{{ simulatedStats.count }}</span>
          </div>
          <div class="stat-row">
            <span>投注金额</span>
            <span>{{ formatNumber(simulatedStats.stake) }}</span>
          </div>
          <div class="stat-row">
            <span>中奖金额</span>
            <span>{{ formatNumber(simulatedStats.winAmount) }}</span>
          </div>
          <div class="stat-row">
            <span>盈亏</span>
            <span :class="profitClass(simulatedStats.profit)">{{ formatNumber(simulatedStats.profit) }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-title">实际投注盈亏统计</div>
          <div class="stat-row">
            <span>已打票方案</span>
            <span>{{ actualStats.count }}</span>
          </div>
          <div class="stat-row">
            <span>投注金额</span>
            <span>{{ formatNumber(actualStats.stake) }}</span>
          </div>
          <div class="stat-row">
            <span>中奖金额</span>
            <span>{{ formatNumber(actualStats.winAmount) }}</span>
          </div>
          <div class="stat-row">
            <span>盈亏</span>
            <span :class="profitClass(actualStats.profit)">{{ formatNumber(actualStats.profit) }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">投注方案</div>
      </template>
      <el-table :data="schemes" v-loading="loadingSchemes" row-key="id">
        <el-table-column prop="name" label="方案名称" min-width="180" />
        <el-table-column prop="expect" label="期号" width="100" />
        <el-table-column prop="passType" label="串关" width="120" />
        <el-table-column prop="stake" label="金额" width="100" />
        <el-table-column prop="totalOdds" label="全串赔率" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="winAmount" label="中奖" width="120" />
        <el-table-column prop="profit" label="盈亏" width="120">
          <template #default="{ row }">
            <span :class="profitClass(row.profit)">{{ formatNumber(row.profit) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="380">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" :disabled="row.ticketed" @click="ticketScheme(row)">打票</el-button>
            <el-button size="small" type="success" @click="simulateScheme(row)">模拟</el-button>
            <el-button size="small" type="danger" @click="deleteScheme(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="方案详情" width="880px">
      <el-table :data="detailItems">
        <el-table-column prop="matchSeq" label="场次" width="80" />
        <el-table-column label="对阵" min-width="220">
          <template #default="{ row }">
            <div class="teams">{{ row.homeTeam }} vs {{ row.awayTeam }}</div>
            <div class="time">{{ row.matchTime }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="selectedResult" label="选择" width="100">
          <template #default="{ row }">
            {{ resultText(row.selectedResult) }}
          </template>
        </el-table-column>
        <el-table-column prop="odds" label="赔率" width="100" />
        <el-table-column prop="result" label="开奖" width="100">
          <template #default="{ row }">
            <span :class="resultClass(row)">{{ resultText(row.result) || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="editVisible" title="编辑方案" width="980px">
      <el-form :inline="true" class="control-form">
        <el-form-item label="方案名称">
          <el-input v-model="editName" placeholder="方案名称" style="width: 200px" />
        </el-form-item>
        <el-form-item label="投注注数">
          <el-input :model-value="editBetCount" disabled style="width: 120px" />
        </el-form-item>
        <el-form-item label="投注金额(每注2元)">
          <el-input :model-value="editBetAmount" disabled style="width: 140px" />
        </el-form-item>
        <el-form-item label="串关类型">
          <el-select
            v-model="editPassTypes"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="选择串关"
            style="width: 220px"
          >
            <el-option
              v-for="option in editPassTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="editRows" height="360">
        <el-table-column prop="matchSeq" label="场次" width="80" />
        <el-table-column label="对阵" min-width="240">
          <template #default="{ row }">
            <div class="teams">{{ row.homeTeam }} vs {{ row.awayTeam }}</div>
            <div class="time">{{ row.matchTime }}</div>
          </template>
        </el-table-column>
        <el-table-column label="赔率(胜/平/负)" min-width="260">
          <template #default="{ row }">
            <div class="odds-editor">
              <el-input-number v-model="row.odds.homeWin" :min="0" :step="0.01" size="small" controls-position="right" />
              <el-input-number v-model="row.odds.draw" :min="0" :step="0.01" size="small" controls-position="right" />
              <el-input-number v-model="row.odds.guestWin" :min="0" :step="0.01" size="small" controls-position="right" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="选择" min-width="240">
          <template #default="{ row }">
            <el-checkbox-group v-model="editSelections[row.matchSeq]" size="small" :disabled="isSelectionLocked(row)">
              <el-checkbox-button value="win">胜</el-checkbox-button>
              <el-checkbox-button value="draw">平</el-checkbox-button>
              <el-checkbox-button value="lose">负</el-checkbox-button>
            </el-checkbox-group>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <div class="dialog-actions">
          <el-button @click="editVisible = false">取消</el-button>
          <el-button type="primary" :disabled="editBetCount <= 0" @click="saveEdit">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const expectOptions = ref([])
const selectedExpect = ref('')
const matches = ref([])
const loadingMatches = ref(false)
const loadingSchemes = ref(false)

const schemeName = ref('')
const selections = ref({})
const passTypes = ref([])

const schemes = ref([])
const detailVisible = ref(false)
const detailItems = ref([])

const editVisible = ref(false)
const editSchemeId = ref(null)
const editName = ref('')
const editSelections = ref({})
const editRows = ref([])
const editPassTypes = ref([])
const nowTs = ref(Date.now())
let nowTimerId = null

const normalizeDisplayText = (value) => {
  if (value === null || value === undefined || value === '') return '-'
  if (Array.isArray(value)) {
    const joined = value.map((item) => normalizeDisplayText(item)).filter((item) => item && item !== '-').join('/')
    return joined || '-'
  }
  if (typeof value === 'object') {
    const preferredKeys = ['text', 'label', 'name', 'value', 'statusDes', 'status_des', 'status']
    for (const key of preferredKeys) {
      if (value[key] !== undefined && value[key] !== null) {
        return normalizeDisplayText(value[key])
      }
    }
    for (const nested of Object.values(value)) {
      const nestedText = normalizeDisplayText(nested)
      if (nestedText !== '-') {
        return nestedText
      }
    }
    return '-'
  }
  const text = String(value).trim()
  return text || '-'
}

const normalizeStatus = (value) => {
  const text = normalizeDisplayText(value)
  if (text === '-') return '-'
  const raw = text.toLowerCase()
  if (['pending', 'scheduled', 'not_started', 'not started'].includes(raw) || text.includes('未开')) return '未开赛'
  if (['running', 'live', 'inplay', 'in_play'].includes(raw) || text.includes('比赛中') || text.includes('中场') || text.includes('进行')) return '比赛中'
  if (['finished', 'ended', 'completed', 'ft'].includes(raw) || text.includes('完场') || text.includes('已结束') || text.includes('已完成')) return '已完成'
  if (['cancelled', 'canceled', 'abandoned'].includes(raw) || text.includes('取消')) return '已取消'
  return text
}

const normalizeScore = (value) => {
  const text = normalizeDisplayText(value)
  if (text === '-') return '-'
  const normalized = text.replace(/：/g, '-').replace(/:/g, '-')
  const matched = normalized.match(/(\d+)\s*-\s*(\d+)/)
  if (matched) return `${matched[1]}-${matched[2]}`
  return normalized
}

const normalizeHandicap = (value) => {
  const text = normalizeDisplayText(value)
  if (text === '-') return '0'
  const matched = text.match(/[-+]?\d+(?:\.\d+)?/)
  if (!matched) return text
  const parsed = Number(matched[0])
  if (Number.isNaN(parsed)) return text
  if (Number.isInteger(parsed)) return String(parsed)
  return String(parsed).replace(/\.?0+$/, '')
}

const parseMatchTime = (value) => {
  const raw = String(value || '').trim()
  if (!raw) return null
  const normalized = raw.replace('T', ' ').replace(/\.\d+$/, '')
  const full = normalized.match(/^(\d{4})-(\d{2})-(\d{2})(?:\s+(\d{2}):(\d{2})(?::(\d{2}))?)?$/)
  if (full) {
    const [, y, m, d, hh = '00', mm = '00', ss = '00'] = full
    return new Date(Number(y), Number(m) - 1, Number(d), Number(hh), Number(mm), Number(ss))
  }
  const monthDay = normalized.match(/^(\d{2})-(\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?$/)
  if (monthDay) {
    const [, m, d, hh, mm, ss = '00'] = monthDay
    const year = new Date(nowTs.value).getFullYear()
    return new Date(year, Number(m) - 1, Number(d), Number(hh), Number(mm), Number(ss))
  }
  const ts = Date.parse(normalized)
  if (Number.isNaN(ts)) return null
  return new Date(ts)
}

const isSelectionLocked = (row) => {
  const statusText = normalizeStatus(row?.status)
  if (statusText !== '-' && ['比赛中', '已完成', '已取消'].some((keyword) => statusText.includes(keyword))) {
    return true
  }
  const kickoff = parseMatchTime(row?.matchTime)
  if (!kickoff) return false
  return nowTs.value >= kickoff.getTime()
}

const buildScoreDisplay = (row) => {
  const full = normalizeScore(row?.score)
  const half = normalizeScore(row?.halfScore)
  if (full === '-' && half === '-') return '-'
  if (half === '-') return full
  if (full === '-') return `- / ${half}`
  return `${full} / ${half}`
}

const normalizeMatchRow = (row) => {
  row.status = normalizeStatus(row.status)
  row.handicap = normalizeHandicap(row.handicap)
  row.score = normalizeScore(row.score)
  row.halfScore = normalizeScore(row.halfScore)
  const sourceScoreDisplay = normalizeDisplayText(row.scoreDisplay)
  row.scoreDisplay = sourceScoreDisplay !== '-' ? sourceScoreDisplay : buildScoreDisplay(row)
}

const clearLockedSelections = () => {
  let changed = false
  const next = { ...selections.value }
  matches.value.forEach((row) => {
    const key = row.matchSeq
    if (isSelectionLocked(row) && Array.isArray(next[key]) && next[key].length > 0) {
      next[key] = []
      changed = true
    }
  })
  if (changed) {
    selections.value = next
  }
}

const clearLockedEditSelections = () => {
  let changed = false
  const next = { ...editSelections.value }
  editRows.value.forEach((row) => {
    const key = row.matchSeq
    if (isSelectionLocked(row) && Array.isArray(next[key]) && next[key].length > 0) {
      next[key] = []
      changed = true
    }
  })
  if (changed) {
    editSelections.value = next
  }
}

const selectedMatches = computed(() => {
  return matches.value
    .filter((row) => !isSelectionLocked(row) && (selections.value[row.matchSeq] || []).length > 0)
    .map((row) => ({
      ...row,
      selectedResults: selections.value[row.matchSeq] || []
    }))
})

const passTypeOptions = computed(() => {
  const count = selectedMatches.value.length
  if (count < 2) return []
  return Array.from({ length: count - 1 }, (_, idx) => {
    const value = idx + 2
    return { value, label: `${value}串1` }
  })
})

const betCount = computed(() => calculateBetCount(selectedMatches.value, passTypes.value, selections.value))
const betAmount = computed(() => betCount.value * 2)

const canCreate = computed(() => {
  return selectedExpect.value && selectedMatches.value.length >= 2 && betCount.value > 0
})

const simulatedSchemes = computed(() => schemes.value.filter((item) => !item.ticketed))
const actualSchemes = computed(() => schemes.value.filter((item) => item.ticketed))

const sumBy = (list, key) => list.reduce((total, item) => total + Number(item?.[key] || 0), 0)

const simulatedStats = computed(() => ({
  count: simulatedSchemes.value.length,
  stake: sumBy(simulatedSchemes.value, 'stake'),
  winAmount: sumBy(simulatedSchemes.value, 'winAmount'),
  profit: sumBy(simulatedSchemes.value, 'profit')
}))

const actualStats = computed(() => ({
  count: actualSchemes.value.length,
  stake: sumBy(actualSchemes.value, 'stake'),
  winAmount: sumBy(actualSchemes.value, 'winAmount'),
  profit: sumBy(actualSchemes.value, 'profit')
}))

watch(
  () => selectedMatches.value.length,
  (count) => {
    if (count < 2) {
      passTypes.value = []
      return
    }
    const allowed = passTypeOptions.value.map((option) => option.value)
    passTypes.value = passTypes.value.filter((value) => allowed.includes(value))
    if (!passTypes.value.length) {
      passTypes.value = [count]
    }
  }
)

const editSelectedMatches = computed(() => {
  return editRows.value
    .filter((row) => !isSelectionLocked(row) && (editSelections.value[row.matchSeq] || []).length > 0)
    .map((row) => ({
      ...row,
      selectedResults: editSelections.value[row.matchSeq] || []
    }))
})

const editPassTypeOptions = computed(() => {
  const count = editSelectedMatches.value.length
  if (count < 2) return []
  return Array.from({ length: count - 1 }, (_, idx) => {
    const value = idx + 2
    return { value, label: `${value}串1` }
  })
})

const editBetCount = computed(() => calculateBetCount(editSelectedMatches.value, editPassTypes.value, editSelections.value))
const editBetAmount = computed(() => editBetCount.value * 2)

watch(
  () => editSelectedMatches.value.length,
  (count) => {
    if (count < 2) {
      editPassTypes.value = []
      return
    }
    const allowed = editPassTypeOptions.value.map((option) => option.value)
    editPassTypes.value = editPassTypes.value.filter((value) => allowed.includes(value))
    if (!editPassTypes.value.length) {
      editPassTypes.value = [count]
    }
  }
)

const formatOdds = (odds = {}) => {
  return `${formatNumber(odds.homeWin)} / ${formatNumber(odds.draw)} / ${formatNumber(odds.guestWin)}`
}

const formatNumber = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
  return Number(value).toFixed(2)
}

const formatText = (...args) => {
  const target = args.length >= 3 ? args[2] : args[0]
  return normalizeDisplayText(target)
}

const resultText = (value) => {
  if (value === 'win') return '胜'
  if (value === 'draw') return '平'
  if (value === 'lose') return '负'
  return ''
}

const statusText = (status) => {
  if (status === 'won') return '中奖'
  if (status === 'lost') return '未中'
  return '待开奖'
}

const statusType = (status) => {
  if (status === 'won') return 'success'
  if (status === 'lost') return 'danger'
  return 'info'
}

const profitClass = (profit) => {
  if (profit > 0) return 'profit positive'
  if (profit < 0) return 'profit negative'
  return 'profit'
}

const resultClass = (row) => {
  if (!row?.result) return ''
  return row.result === row.selectedResult ? 'result-hit' : 'result-miss'
}

const calculateBetCount = (rows, passTypeValues, selectionMap) => {
  if (!rows.length) return 0
  const matchCounts = rows.map((row) => (selectionMap[row.matchSeq] || []).length).filter((count) => count > 0)
  if (!matchCounts.length) return 0
  const totalMatches = matchCounts.length
  const passTypes = passTypeValues.length ? passTypeValues : [totalMatches]
  let total = 0
  const indices = Array.from({ length: totalMatches }, (_, idx) => idx)

  const combine = (start, depth, size, current) => {
    if (depth === size) {
      const product = current.reduce((acc, idx) => acc * matchCounts[idx], 1)
      total += product
      return
    }
    for (let i = start; i < indices.length; i += 1) {
      combine(i + 1, depth + 1, size, [...current, indices[i]])
    }
  }

  passTypes.forEach((size) => {
    if (size <= totalMatches && size > 1) {
      combine(0, 0, size, [])
    }
  })

  return total
}

const parsePassTypeText = (text, matchCount) => {
  if (!text || text === 'all' || text === 'full') {
    return matchCount ? [matchCount] : []
  }
  const matches = text.match(/(\d+)x1/g) || text.match(/(\d+)串1/g) || []
  const values = matches.map((value) => Number(value.replace(/\D/g, ''))).filter((val) => val > 1)
  return values.length ? values : matchCount ? [matchCount] : []
}

const getSelectedOdds = (row, result) => {
  if (!row || !row.odds) return 0
  if (result === 'win') return row.odds.homeWin ?? 0
  if (result === 'draw') return row.odds.draw ?? 0
  if (result === 'lose') return row.odds.guestWin ?? 0
  return 0
}

const fetchExpectOptions = async () => {
  try {
    const data = await request.get('/api/v1/beidan-betting/expect-options')
    expectOptions.value = data?.options || []
    if (!selectedExpect.value) {
      selectedExpect.value = data?.latestPeriod || expectOptions.value[0]?.value || ''
    }
  } catch (error) {
    console.error(error)
  }
}

const fetchMatches = async () => {
  if (!selectedExpect.value) return
  loadingMatches.value = true
  try {
    const data = await request.get('/api/v1/beidan-betting/matches', {
      params: { expect: selectedExpect.value }
    })
    const rows = Array.isArray(data) ? data : []
    rows.forEach((row) => {
      row.odds = row.odds || { homeWin: 0, draw: 0, guestWin: 0 }
      normalizeMatchRow(row)
    })
    matches.value = rows
    clearLockedSelections()
  } finally {
    loadingMatches.value = false
  }
}

const fetchSchemes = async () => {
  if (!selectedExpect.value) return
  loadingSchemes.value = true
  try {
    const data = await request.get('/api/v1/beidan-betting/schemes', {
      params: { expect: selectedExpect.value, page: 1, page_size: 50 }
    })
    schemes.value = (data?.items || []).map((item) => ({
      ...item,
      ticketed: !!item.ticketed
    }))
  } finally {
    loadingSchemes.value = false
  }
}

const handleExpectChange = async () => {
  resetSelections()
  await fetchMatches()
  await fetchSchemes()
}

const resetSelections = () => {
  selections.value = {}
}

const createScheme = async () => {
  if (!canCreate.value) return
  const items = []
  selectedMatches.value.forEach((row) => {
    const selected = selections.value[row.matchSeq] || []
    selected.forEach((result) => {
      items.push({
        matchSeq: row.matchSeq,
        homeTeam: row.homeTeam,
        awayTeam: row.awayTeam,
        matchTime: row.matchTime,
        selectedResult: result,
        odds: getSelectedOdds(row, result)
      })
    })
  })

  try {
    await request.post('/api/v1/beidan-betting/schemes', {
      expect: selectedExpect.value,
      name: schemeName.value || undefined,
      stake: betAmount.value,
      passType: passTypes.value,
      splitMode: 'even',
      selections: items
    })
    ElMessage.success('方案保存成功')
    schemeName.value = ''
    await fetchSchemes()
  } catch (error) {
    console.error(error)
  }
}

const openDetail = (scheme) => {
  detailItems.value = scheme.items || []
  detailVisible.value = true
}

const openEdit = (scheme) => {
  if (!scheme) return
  editSchemeId.value = scheme.id
  editName.value = scheme.name || ''

  const matchMap = new Map(matches.value.map((row) => [String(row.matchSeq), row]))
  const grouped = {}
  ;(scheme.items || []).forEach((item) => {
    const key = String(item.matchSeq)
    if (!grouped[key]) {
      grouped[key] = {
        matchSeq: key,
        homeTeam: item.homeTeam,
        awayTeam: item.awayTeam,
        matchTime: item.matchTime,
        odds: { homeWin: 0, draw: 0, guestWin: 0 },
        items: []
      }
    }
    grouped[key].items.push(item)
  })

  editSelections.value = {}
  const rows = Object.values(grouped).map((row) => {
    const baseMatch = matchMap.get(String(row.matchSeq))
    if (baseMatch?.odds) {
      row.odds = { ...baseMatch.odds }
      row.status = baseMatch.status
      row.score = baseMatch.score
      row.halfScore = baseMatch.halfScore
      row.scoreDisplay = baseMatch.scoreDisplay
      row.matchTime = baseMatch.matchTime || row.matchTime
    } else {
      row.items.forEach((item) => {
        if (item.selectedResult === 'win') row.odds.homeWin = item.odds
        if (item.selectedResult === 'draw') row.odds.draw = item.odds
        if (item.selectedResult === 'lose') row.odds.guestWin = item.odds
      })
    }
    normalizeMatchRow(row)
    editSelections.value[row.matchSeq] = row.items.map((item) => item.selectedResult)
    return row
  })

  editRows.value = rows
  clearLockedEditSelections()
  editPassTypes.value = parsePassTypeText(scheme.passType, rows.length)
  editVisible.value = true
}

const saveEdit = async () => {
  if (!editSchemeId.value) return
  const items = []
  editRows.value.forEach((row) => {
    if (isSelectionLocked(row)) return
    const selected = editSelections.value[row.matchSeq] || []
    selected.forEach((result) => {
      items.push({
        matchSeq: row.matchSeq,
        homeTeam: row.homeTeam,
        awayTeam: row.awayTeam,
        matchTime: row.matchTime,
        selectedResult: result,
        odds: getSelectedOdds(row, result)
      })
    })
  })

  try {
    await request.put(`/api/v1/beidan-betting/schemes/${editSchemeId.value}`, {
      name: editName.value,
      stake: editBetAmount.value,
      passType: editPassTypes.value,
      splitMode: 'even',
      selections: items
    })
    ElMessage.success('方案已更新')
    editVisible.value = false
    await fetchSchemes()
  } catch (error) {
    console.error(error)
  }
}

const ticketScheme = async (scheme) => {
  try {
    await ElMessageBox.confirm('确认该方案已打票？', '提示', { type: 'warning' })
    await request.post(`/api/v1/beidan-betting/schemes/${scheme.id}/ticket`)
    ElMessage.success('已打票')
    await fetchSchemes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const simulateScheme = async (scheme) => {
  try {
    await request.post(`/api/v1/beidan-betting/schemes/${scheme.id}/simulate`)
    ElMessage.success('模拟完成')
    await fetchSchemes()
  } catch (error) {
    console.error(error)
  }
}

const deleteScheme = async (scheme) => {
  try {
    await ElMessageBox.confirm('确认删除该方案？', '提示', { type: 'warning' })
    await request.delete(`/api/v1/beidan-betting/schemes/${scheme.id}`)
    ElMessage.success('已删除')
    await fetchSchemes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const refreshAll = async () => {
  await fetchExpectOptions()
  await fetchMatches()
  await fetchSchemes()
}

onMounted(async () => {
  nowTimerId = window.setInterval(() => {
    nowTs.value = Date.now()
    clearLockedSelections()
    clearLockedEditSelections()
  }, 30000)
  await fetchExpectOptions()
  await fetchMatches()
  await fetchSchemes()
})

onBeforeUnmount(() => {
  if (nowTimerId) {
    window.clearInterval(nowTimerId)
    nowTimerId = null
  }
})
</script>

<style scoped>
.beidan-betting-simulator {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.page-card :deep(.el-card__body) {
  padding-bottom: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.page-header .title {
  font-size: 18px;
  font-weight: 600;
}

.control-form {
  margin-bottom: 12px;
}

.table-card {
  min-height: 200px;
}

.card-header {
  font-weight: 600;
}

.teams {
  font-weight: 500;
}

.time {
  font-size: 12px;
  color: #999;
}

.odds-editor {
  display: flex;
  gap: 8px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 12px 16px;
  background: #fff;
}

.stat-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  color: #606266;
}

.profit.positive {
  color: #00a870;
}

.profit.negative {
  color: #f56c6c;
}

.result-hit {
  color: #f56c6c;
  font-weight: 600;
}

.result-miss {
  color: #00a870;
  font-weight: 600;
}

@media (max-width: 900px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
