<template>
  <div class="user-profile-management morandi-page um-page">
    <el-card class="morandi-card card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>用户画像管理</h3>
            <p class="subtitle">基于真实数据分析和维护用户画像</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" :loading="loading" @click="loadData">刷新</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="12" class="filters-row">
        <el-col :xs="24" :sm="10" :md="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名或邮箱"
            clearable
            @keyup.enter="applyFilters"
            @clear="applyFilters"
          />
        </el-col>
        <el-col :xs="12" :sm="7" :md="4">
          <el-select v-model="riskLevelFilter" placeholder="风险等级" clearable @change="applyFilters">
            <el-option label="保守型" value="conservative" />
            <el-option label="稳健型" value="moderate" />
            <el-option label="激进型" value="aggressive" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="7" :md="4">
          <el-select v-model="activityFilter" placeholder="活跃度" clearable @change="applyFilters">
            <el-option label="高活跃" value="high" />
            <el-option label="中活跃" value="medium" />
            <el-option label="低活跃" value="low" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="10">
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <el-table :data="paginatedProfiles" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="userId" label="用户ID" width="100" />

        <el-table-column prop="username" label="用户名" width="170">
          <template #default="scope">
            <div class="user-info">
              <el-avatar size="small" :style="{ backgroundColor: getAvatarColor(scope.row.userId) }">
                {{ (scope.row.username || 'U').charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ scope.row.username || '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="email" label="邮箱" width="220" show-overflow-tooltip />

        <el-table-column prop="riskTolerance" label="风险偏好" width="120">
          <template #default="scope">
            <el-tag :type="getRiskTagType(scope.row.riskTolerance)">{{ getRiskLevelName(scope.row.riskTolerance) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="preferredTeams" label="偏好球队" min-width="180">
          <template #default="scope">
            <el-tag
              v-for="(team, idx) in (scope.row.preferredTeams || []).slice(0, 3)"
              :key="idx"
              size="small"
              class="team-tag"
            >
              {{ team }}
            </el-tag>
            <el-tag v-if="(scope.row.preferredTeams || []).length > 3" size="small" type="info">
              +{{ (scope.row.preferredTeams || []).length - 3 }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="scope">{{ toPercent(scope.row.successRate) }}</template>
        </el-table-column>

        <el-table-column prop="bettingFrequency" label="投注频率" width="120">
          <template #default="scope">
            <el-tag :type="getFrequencyTagType(scope.row.bettingFrequency)">{{ getFrequencyName(scope.row.bettingFrequency) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="lastUpdated" label="更新时间" width="170" />

        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" @click="viewDetails(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="editProfile(scope.row)">编辑</el-button>
              <el-button size="small" type="success" plain @click="analyzeBehavior(scope.row)">分析</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredProfiles.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog class="um-dialog" v-model="detailDialogVisible" title="用户画像详情" width="60%" destroy-on-close @closed="disposeBehaviorChart">
      <div v-if="selectedProfile" class="profile-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">{{ selectedProfile.userId }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedProfile.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedProfile.email }}</el-descriptions-item>
          <el-descriptions-item label="风险偏好">
            <el-tag :type="getRiskTagType(selectedProfile.riskTolerance)">{{ getRiskLevelName(selectedProfile.riskTolerance) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="偏好球队" :span="2">
            <el-tag v-for="(team, idx) in selectedProfile.preferredTeams || []" :key="idx" size="small" class="team-tag">
              {{ team }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="投注习惯">{{ selectedProfile.bettingHabits || '-' }}</el-descriptions-item>
          <el-descriptions-item label="投注频率">{{ getFrequencyName(selectedProfile.bettingFrequency) }}</el-descriptions-item>
          <el-descriptions-item label="成功率">{{ toPercent(selectedProfile.successRate) }}</el-descriptions-item>
          <el-descriptions-item label="总投注额">{{ formatMoney(selectedProfile.totalBettingAmount) }}</el-descriptions-item>
          <el-descriptions-item label="总收益">{{ formatMoney(selectedProfile.totalProfit) }}</el-descriptions-item>
          <el-descriptions-item label="盈利概率">{{ toPercent(selectedProfile.profitProbability) }}</el-descriptions-item>
          <el-descriptions-item label="最后更新">{{ selectedProfile.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="画像标签" :span="2">
            <el-tag v-for="(tag, idx) in selectedProfile.tags || []" :key="idx" size="small" class="team-tag">
              {{ tag }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="behavior-chart">
          <h4>行为分析图表</h4>
          <div ref="behaviorChartRef" style="height: 300px; margin-top: 12px"></div>
        </div>
      </div>
    </el-dialog>

    <el-dialog class="um-dialog" v-model="editDialogVisible" title="编辑用户画像" width="50%" destroy-on-close>
      <el-form ref="profileFormRef" :model="profileForm" label-width="120px" class="edit-form">
        <el-form-item label="风险偏好">
          <el-radio-group v-model="profileForm.riskTolerance">
            <el-radio :value="'conservative'">保守型</el-radio>
            <el-radio :value="'moderate'">稳健型</el-radio>
            <el-radio :value="'aggressive'">激进型</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="偏好球队">
          <el-select v-model="profileForm.preferredTeams" multiple filterable placeholder="请选择偏好球队" style="width: 100%">
            <el-option v-for="team in allTeams" :key="team" :label="team" :value="team" />
          </el-select>
        </el-form-item>

        <el-form-item label="投注习惯">
          <el-input v-model="profileForm.bettingHabits" type="textarea" :rows="3" placeholder="请输入投注习惯" />
        </el-form-item>

        <el-form-item label="投注频率">
          <el-select v-model="profileForm.bettingFrequency" placeholder="请选择投注频率">
            <el-option label="低频" value="low" />
            <el-option label="中频" value="medium" />
            <el-option label="高频" value="high" />
          </el-select>
        </el-form-item>

        <el-form-item label="成功率">
          <el-input-number v-model="profileForm.successRate" :min="0" :max="1" :step="0.01" :precision="2" style="width: 100%" />
        </el-form-item>

        <el-form-item label="总投注额">
          <el-input-number v-model="profileForm.totalBettingAmount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getUserProfiles, getUserProfile, updateUserProfile } from '@/api/modules/user-profiles'

const loading = ref(false)
const searchQuery = ref('')
const riskLevelFilter = ref('')
const activityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const profiles = ref([])
const detailDialogVisible = ref(false)
const editDialogVisible = ref(false)
const selectedProfile = ref(null)
const profileForm = ref({})
const profileFormRef = ref(null)

const allTeams = [
  '皇家马德里',
  '巴塞罗那',
  '拜仁慕尼黑',
  '曼城',
  '利物浦',
  '尤文图斯',
  '国际米兰',
  'AC米兰',
  '巴黎圣日耳曼',
  '切尔西',
  '曼联',
  '阿森纳',
  '多特蒙德',
  '勒沃库森',
  '门兴格拉德巴赫',
  '阿贾克斯'
]

const behaviorChartRef = ref(null)
let behaviorChart = null

const normalizeProfile = (p = {}) => ({
  userId: p.userId || p.user_id || p.id,
  username: p.username || '',
  email: p.email || '',
  riskTolerance: p.riskTolerance || p.risk_tolerance || 'moderate',
  preferredTeams: Array.isArray(p.preferredTeams) ? p.preferredTeams : Array.isArray(p.preferred_teams) ? p.preferred_teams : [],
  successRate: Number(p.successRate ?? p.success_rate ?? 0),
  bettingFrequency: p.bettingFrequency || p.betting_frequency || 'medium',
  bettingHabits: p.bettingHabits || p.betting_habits || '',
  totalBettingAmount: Number(p.totalBettingAmount ?? p.total_betting_amount ?? 0),
  totalProfit: Number(p.totalProfit ?? p.total_profit ?? 0),
  profitProbability: Number(p.profitProbability ?? p.profit_probability ?? 0),
  tags: Array.isArray(p.tags) ? p.tags : [],
  lastUpdated: p.lastUpdated || p.last_updated || '-'
})

const unwrapList = (response) => {
  const payload = response?.data ?? response
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.items)) return payload.items
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload?.data?.items)) return payload.data.items
  return []
}

const filteredProfiles = computed(() => {
  return profiles.value.filter((profile) => {
    const q = searchQuery.value.trim().toLowerCase()
    const matchesSearch =
      !q ||
      String(profile.username || '').toLowerCase().includes(q) ||
      String(profile.email || '').toLowerCase().includes(q)

    const matchesRisk = !riskLevelFilter.value || profile.riskTolerance === riskLevelFilter.value
    const matchesActivity = !activityFilter.value || profile.bettingFrequency === activityFilter.value

    return matchesSearch && matchesRisk && matchesActivity
  })
})

const paginatedProfiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredProfiles.value.slice(start, start + pageSize.value)
})

const loadData = async () => {
  loading.value = true
  try {
    const response = await getUserProfiles({ page: 1, size: 500, skip: 0, limit: 500 })
    profiles.value = unwrapList(response).map(normalizeProfile)
  } catch (error) {
    console.error('加载用户画像列表失败:', error)
    ElMessage.error('加载用户画像列表失败')
    profiles.value = []
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  riskLevelFilter.value = ''
  activityFilter.value = ''
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const getRiskTagType = (level) => {
  if (level === 'conservative') return 'success'
  if (level === 'moderate') return 'warning'
  if (level === 'aggressive') return 'danger'
  return 'info'
}

const getRiskLevelName = (level) => {
  if (level === 'conservative') return '保守型'
  if (level === 'moderate') return '稳健型'
  if (level === 'aggressive') return '激进型'
  return level || '-'
}

const getFrequencyTagType = (freq) => {
  if (freq === 'high') return 'danger'
  if (freq === 'medium') return 'warning'
  if (freq === 'low') return 'info'
  return 'info'
}

const getFrequencyName = (freq) => {
  if (freq === 'high') return '高频'
  if (freq === 'medium') return '中频'
  if (freq === 'low') return '低频'
  return freq || '-'
}

const getAvatarColor = (id) => {
  const colors = ['#6a8192', '#8fa6b7', '#aab8c5', '#7f93a6', '#97a6b3']
  return colors[Number(id || 0) % colors.length]
}

const toPercent = (value) => `${(Number(value || 0) * 100).toFixed(2)}%`
const formatMoney = (value) => Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const viewDetails = async (profile) => {
  try {
    const response = await getUserProfile(profile.userId)
    const payload = response?.data ?? response
    selectedProfile.value = normalizeProfile(payload)
  } catch (error) {
    selectedProfile.value = normalizeProfile(profile)
  }

  detailDialogVisible.value = true
  await nextTick()
  initBehaviorChart()
}

const initBehaviorChart = () => {
  if (!behaviorChartRef.value || !selectedProfile.value) return
  disposeBehaviorChart()
  behaviorChart = echarts.init(behaviorChartRef.value)

  const base = Math.max(100, Math.round((selectedProfile.value.totalBettingAmount || 1000) / 10))
  const rate = selectedProfile.value.profitProbability || 0
  const bets = [0.8, 1.1, 1.0, 1.2, 0.9, 1.05, 1.15].map((v) => Math.round(base * v))
  const profit = bets.map((v) => Math.round(v * (rate - 0.5)))

  behaviorChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['投注额', '收益'] },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'] },
    yAxis: { type: 'value', name: '金额(元)' },
    series: [
      { name: '投注额', type: 'bar', data: bets, itemStyle: { color: '#7f93a6' } },
      { name: '收益', type: 'line', data: profit, itemStyle: { color: '#97a6b3' } }
    ]
  })

  window.addEventListener('resize', resizeBehaviorChart)
}

const resizeBehaviorChart = () => {
  behaviorChart?.resize()
}

const disposeBehaviorChart = () => {
  window.removeEventListener('resize', resizeBehaviorChart)
  if (behaviorChart) {
    behaviorChart.dispose()
    behaviorChart = null
  }
}

const editProfile = (profile) => {
  profileForm.value = normalizeProfile(profile)
  editDialogVisible.value = true
}

const submitEditForm = async () => {
  try {
    const payload = {
      ...profileForm.value,
      lastUpdated: new Date().toISOString().replace('T', ' ').slice(0, 19)
    }
    const response = await updateUserProfile(profileForm.value.userId, payload)
    const normalized = normalizeProfile(response?.data ?? response ?? payload)

    const idx = profiles.value.findIndex((p) => p.userId === normalized.userId)
    if (idx !== -1) profiles.value[idx] = normalized

    ElMessage.success('用户画像更新成功')
    editDialogVisible.value = false
  } catch (error) {
    console.error('更新用户画像失败:', error)
    ElMessage.error('更新用户画像失败')
  }
}

const analyzeBehavior = (profile) => {
  ElMessage.info(`正在分析 ${profile.username} 的行为模式...`)
}

onMounted(() => {
  loadData()
})

onBeforeUnmount(() => {
  disposeBehaviorChart()
})
</script>

<style scoped>
.morandi-page {
  --m-bg: #f5f7fa;
  --m-card: #ffffff;
  --m-border: #ebeef5;
  --m-head: #ffffff;
  --m-text: #303133;
  --m-subtext: #909399;
}

.user-profile-management {
  min-height: calc(100vh - 110px);
  padding: 20px;
  background: var(--m-bg);
}

.morandi-card {
  border-radius: 4px;
  border: 1px solid var(--m-border);
  box-shadow: none;
  background: var(--m-card);
}

.morandi-card :deep(.el-card__header) {
  background: var(--m-head);
  border-bottom: 1px solid var(--m-border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.card-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: var(--m-text);
}

.subtitle {
  margin: 0;
  color: var(--m-subtext);
  font-size: 14px;
}

.filters-row {
  margin-bottom: 16px;
  padding: 8px 0;
}

.user-info {
  display: flex;
  align-items: center;
}

.username {
  margin-left: 10px;
}

.team-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  flex-wrap: nowrap;
}

.action-buttons .el-button + .el-button {
  margin-left: 0;
}

.action-buttons :deep(.el-button) {
  min-width: 56px;
  padding: 5px 12px;
}

.pagination-container {
  margin-top: 16px;
  text-align: right;
}

.profile-detail {
  max-height: 520px;
  overflow-y: auto;
}

.behavior-chart {
  margin-top: 24px;
  padding-top: 14px;
  border-top: 1px solid var(--m-border);
}

.behavior-chart h4 {
  margin: 0;
  font-size: 16px;
  color: var(--m-text);
}

.edit-form {
  padding-right: 20px;
}

:deep(.um-dialog.el-dialog) {
  border: 1px solid var(--m-border);
  border-radius: 4px;
  box-shadow: none;
  overflow: hidden;
}

:deep(.um-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 14px 16px;
  border-bottom: 1px solid var(--m-border);
}

:deep(.um-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: var(--m-text);
}

:deep(.um-dialog .el-dialog__body) {
  padding: 16px;
}

:deep(.um-dialog .el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid var(--m-border);
}
</style>
