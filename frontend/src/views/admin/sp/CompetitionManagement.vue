<template>
  <div class="competition-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>比赛管理</h2>
      <p class="page-description">管理比赛、联赛、球队数据及相关关联信息</p>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="handleAddMatch">
        新增比赛
      </el-button>
      <el-button type="success" :icon="Upload" @click="handleImport">
        批量导入
      </el-button>
      <el-button type="warning" :icon="DocumentChecked" @click="validateData">
        数据验证
      </el-button>
      <el-button type="info" :icon="Connection" @click="syncRelatedData">
        同步关联数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalMatches }}</div>
              <div class="stats-label">总比赛数</div>
            </div>
            <el-icon class="stats-icon"><Soccer /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.leagues }}</div>
              <div class="stats-label">联赛数</div>
            </div>
            <el-icon class="stats-icon"><Medal /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.teams }}</div>
              <div class="stats-label">球队数</div>
            </div>
            <el-icon class="stats-icon"><User /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.validationIssues }}%</div>
              <div class="stats-label">异常比例</div>
            </div>
            <el-icon class="stats-icon"><Warning /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- 比赛CRUD -->
      <el-tab-pane label="比赛管理" name="matches">
        <div class="tab-content">
          <el-card class="matches-card">
            <template #header>
              <div class="card-header">
                <span>比赛数据管理</span>
                <div class="header-actions">
                  <el-button size="small" @click="refreshMatches">刷新</el-button>
                  <el-button size="small" type="primary" @click="exportMatches">导出</el-button>
                </div>
              </div>
            </template>

            <div class="filters">
              <el-form :model="matchFilters" :inline="true">
                <el-form-item label="联赛">
                  <el-select v-model="matchFilters.league" placeholder="选择联赛" clearable>
                    <el-option label="英超" value="premier_league" />
                    <el-option label="西甲" value="la_liga" />
                    <el-option label="意甲" value="serie_a" />
                    <el-option label="德甲" value="bundesliga" />
                    <el-option label="法甲" value="ligue_1" />
                  </el-select>
                </el-form-item>
                <el-form-item label="主队">
                  <el-input v-model="matchFilters.homeTeam" placeholder="主队名称" clearable />
                </el-form-item>
                <el-form-item label="客队">
                  <el-input v-model="matchFilters.awayTeam" placeholder="客队名称" clearable />
                </el-form-item>
                <el-form-item label="比赛时间">
                  <el-date-picker
                    v-model="matchFilters.dateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="applyMatchFilters">筛选</el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-table 
              :data="matchData" 
              style="width: 100%" 
              v-loading="matchesLoading" 
              stripe
              @selection-change="handleSelectionChange"
            >
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="matchId" label="比赛ID" width="150" />
              <el-table-column label="对阵" min-width="200">
                <template #default="scope">
                  <div class="match-teams">
                    <span class="team home-team">{{ scope.row.homeTeam }}</span>
                    <span class="vs">VS</span>
                    <span class="team away-team">{{ scope.row.awayTeam }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="league" label="联赛" width="120" />
              <el-table-column prop="matchTime" label="比赛时间" width="160" />
              <el-table-column prop="score" label="比分" width="120">
                <template #default="scope">
                  {{ scope.row.score || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="120">
                <template #default="scope">
                  <el-tag :type="getStatusTagType(scope.row.status)">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="240" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="viewMatchDetails(scope.row)">详情</el-button>
                  <el-button size="small" type="primary" @click="editMatch(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteMatch(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="matchPagination.currentPage"
                v-model:page-size="matchPagination.pageSize"
                :total="matchPagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="handleMatchPageChange"
                @size-change="handleSizeChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 数据验证 -->
      <el-tab-pane label="数据验证" name="validation">
        <div class="tab-content">
          <el-card class="validation-card">
            <template #header>
              <div class="card-header">
                <span>数据质量验证</span>
                <div class="header-actions">
                  <el-button size="small" @click="runValidation">运行验证</el-button>
                  <el-button size="small" type="primary" @click="generateValidationReport">生成报告</el-button>
                </div>
              </div>
            </template>

            <div class="validation-summary">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="validation-item">
                    <div class="validation-title">完整度</div>
                    <el-progress :percentage="95" :color="getProgressColor(95)" />
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="validation-item">
                    <div class="validation-title">准确性</div>
                    <el-progress :percentage="92" :color="getProgressColor(92)" />
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="validation-item">
                    <div class="validation-title">一致性</div>
                    <el-progress :percentage="88" :color="getProgressColor(88)" />
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="validation-item">
                    <div class="validation-title">及时性</div>
                    <el-progress :percentage="98" :color="getProgressColor(98)" />
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="validation-issues">
              <el-table :data="validationIssuesData" style="width: 100%" v-loading="validationLoading">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="matchId" label="比赛ID" width="120" />
                <el-table-column prop="type" label="类型" width="120">
                  <template #default="scope">
                    <el-tag :type="getIssueTypeTagType(scope.row.type)">
                      {{ scope.row.typeText }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" min-width="250" />
                <el-table-column prop="severity" label="严重程度" width="100">
                  <template #default="scope">
                    <el-tag :type="getSeverityTagType(scope.row.severity)">
                      {{ scope.row.severityText }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="detectedTime" label="检测时间" width="160" />
                <el-table-column label="操作" width="150">
                  <template #default="scope">
                    <el-button size="small" @click="fixIssue(scope.row)">修复</el-button>
                    <el-button size="small" type="warning" @click="ignoreIssue(scope.row)">忽略</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 关联数据 -->
      <el-tab-pane label="关联数据" name="related">
        <div class="tab-content">
          <el-card class="related-card">
            <template #header>
              <div class="card-header">
                <div class="header-actions">
                  <el-button size="small" @click="refreshRelatedData">刷新</el-button>
                  <el-button size="small" type="primary" @click="syncWithExternal">同步外部</el-button>
                </div>
              </div>
            </template>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="related-data-card">
                  <template #header>
                    <div class="related-card-header">
                      <span>赔率数据</span>
                      <el-tag type="success">{{ relatedData.oddsCount }}</el-tag>
                    </div>
                  </template>
                  <div class="related-content">
                    <p>最新赔率更新: {{ relatedData.lastOddsUpdate }}</p>
                    <el-button size="small" type="primary" @click="viewOddsData">查看赔率</el-button>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="related-data-card">
                  <template #header>
                    <div class="related-card-header">
                      <span>情报数据</span>
                      <el-tag type="warning">{{ relatedData.intelligenceCount }}</el-tag>
                    </div>
                  </template>
                  <div class="related-content">
                    <p>最新情报更新: {{ relatedData.lastIntelligenceUpdate }}</p>
                    <el-button size="small" type="primary" @click="viewIntelligenceData">查看情报</el-button>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="related-data-card">
                  <template #header>
                    <div class="related-card-header">
                      <span>预测结果</span>
                      <el-tag type="info">{{ relatedData.predictionCount }}</el-tag>
                    </div>
                  </template>
                  <div class="related-content">
                    <p>最新预测更新: {{ relatedData.lastPredictionUpdate }}</p>
                    <el-button size="small" type="primary" @click="viewPredictionData">查看预测</el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <div class="related-data-table">
              <h4>关联数据详情</h4>
              <el-table :data="relatedData.detailList" style="width: 100%" v-loading="relatedData.loading">
                <el-table-column prop="type" label="类型" width="120" />
                <el-table-column prop="source" label="数据源" width="150" />
                <el-table-column prop="lastUpdate" label="最后更新" width="160" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="getDataStatusTagType(scope.row.status)">
                      {{ scope.row.statusText }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="records" label="记录数" width="100" />
                <el-table-column label="操作" width="150">
                  <template #default="scope">
                    <el-button size="small" @click="viewDataDetails(scope.row)">查看</el-button>
                    <el-button size="small" type="primary" @click="refreshData(scope.row)">刷新</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 编辑/新增比赛对话框 -->
    <el-dialog 
      v-model="showMatchDialog" 
      :title="isEditing ? '编辑比赛' : '新增比赛'" 
      width="60%"
      :before-close="closeMatchDialog"
    >
      <el-form :model="matchForm" :rules="matchFormRules" ref="matchFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主队" prop="homeTeam">
              <el-input v-model="matchForm.homeTeam" placeholder="请输入主队名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客队" prop="awayTeam">
              <el-input v-model="matchForm.awayTeam" placeholder="请输入客队名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联赛" prop="league">
              <el-select v-model="matchForm.league" placeholder="请选择联赛" style="width: 100%">
                <el-option label="英超" value="premier_league" />
                <el-option label="西甲" value="la_liga" />
                <el-option label="意甲" value="serie_a" />
                <el-option label="德甲" value="bundesliga" />
                <el-option label="法甲" value="ligue_1" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="比赛时间" prop="matchTime">
              <el-date-picker
                v-model="matchForm.matchTime"
                type="datetime"
                placeholder="选择比赛时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="比赛状态" prop="status">
          <el-select v-model="matchForm.status" placeholder="请选择比赛状态" style="width: 200px">
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已结束" value="finished" />
            <el-option label="取消" value="cancelled" />
            <el-option label="延期" value="postponed" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="matchForm.remarks" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeMatchDialog">取消</el-button>
          <el-button type="primary" @click="saveMatch">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Upload, 
  DocumentChecked, 
  Connection, 
  Soccer, 
  Medal, 
  User, 
  Warning 
} from '@element-plus/icons-vue'

// 激活的标签页
const activeTab = ref('matches')

// 统计数据
const stats = reactive({
  totalMatches: 1245,
  leagues: 24,
  teams: 368,
  validationIssues: 2.4
})

// 比赛相关数据
const matchData = ref([])
const matchesLoading = ref(false)
const matchFilters = reactive({
  league: '',
  homeTeam: '',
  awayTeam: '',
  dateRange: null
})
const matchPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 100
})

// 验证相关数据
const validationIssuesData = ref([])
const validationLoading = ref(false)

// 关联数据
const relatedData = reactive({
  oddsCount: 3420,
  intelligenceCount: 1240,
  predictionCount: 890,
  lastOddsUpdate: '2024-01-15 10:30:25',
  lastIntelligenceUpdate: '2024-01-15 09:45:12',
  lastPredictionUpdate: '2024-01-15 11:20:33',
  loading: false,
  detailList: []
})

// 比赛表单相关
const showMatchDialog = ref(false)
const isEditing = ref(false)
const matchForm = reactive({
  id: null,
  matchId: '',
  homeTeam: '',
  awayTeam: '',
  league: '',
  matchTime: '',
  status: 'pending',
  score: '',
  remarks: ''
})
const matchFormRef = ref(null)
const matchFormRules = {
  homeTeam: [{ required: true, message: '请输入主队名称', trigger: 'blur' }],
  awayTeam: [{ required: true, message: '请输入客队名称', trigger: 'blur' }],
  league: [{ required: true, message: '请选择联赛', trigger: 'change' }],
  matchTime: [{ required: true, message: '请选择比赛时间', trigger: 'change' }],
  status: [{ required: true, message: '请选择比赛状态', trigger: 'change' }]
}

// 选中的比赛
const selectedMatches = ref([])

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedMatches.value = selection
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  matchPagination.pageSize = size
  // 这里可以重新加载数据
}

// 方法
const handleAddMatch = () => {
  isEditing.value = false
  Object.assign(matchForm, {
    id: null,
    matchId: '',
    homeTeam: '',
    awayTeam: '',
    league: '',
    matchTime: '',
    status: 'pending',
    score: '',
    remarks: ''
  })
  showMatchDialog.value = true
}

const handleImport = () => {
  ElMessage.info('进入批量导入页面')
}

const validateData = () => {
  ElMessage.info('开始数据验证')
}

const syncRelatedData = () => {
  ElMessage.info('同步关联数据')
}

const refreshMatches = () => {
  matchesLoading.value = true
  setTimeout(() => {
    matchesLoading.value = false
    ElMessage.success('刷新完成')
  }, 1000)
}

const exportMatches = () => {
  ElMessage.info('导出比赛数据')
}

const applyMatchFilters = () => {
  ElMessage.info('应用筛选条件')
}

const handleMatchPageChange = (page) => {
  matchPagination.currentPage = page
}

const getStatusTagType = (status) => {
  switch(status) {
    case 'pending': return 'info'
    case 'ongoing': return 'warning'
    case 'finished': return 'success'
    case 'cancelled': return 'danger'
    case 'postponed': return 'info'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch(status) {
    case 'pending': return '未开始'
    case 'ongoing': return '进行中'
    case 'finished': return '已结束'
    case 'cancelled': return '取消'
    case 'postponed': return '延期'
    default: return status
  }
}

const viewMatchDetails = (match) => {
  ElMessage.info(`查看比赛详情: ${match.matchId}`)
}

const editMatch = (match) => {
  isEditing.value = true
  Object.assign(matchForm, match)
  showMatchDialog.value = true
}

const relateData = (match) => {
  ElMessage.info(`为比赛 "${match.homeTeam} VS ${match.awayTeam}" 关联数据`)
}

const deleteMatch = (match) => {
  ElMessageBox.confirm(`确定要删除比赛 "${match.homeTeam} VS ${match.awayTeam}" 吗？`, '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  })
}

const runValidation = () => {
  ElMessage.info('运行数据验证')
}

const generateValidationReport = () => {
  ElMessage.info('生成验证报告')
}

const getProgressColor = (value) => {
  if (value >= 95) return '#67C23A'
  if (value >= 85) return '#E6A23C'
  return '#F56C6C'
}

const getIssueTypeTagType = (type) => {
  switch(type) {
    case 'missing': return 'warning'
    case 'inconsistent': return 'danger'
    case 'outdated': return 'info'
    default: return 'info'
  }
}

const getSeverityTagType = (severity) => {
  switch(severity) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const fixIssue = (issue) => {
  ElMessage.success(`修复问题: ${issue.id}`)
}

const ignoreIssue = (issue) => {
  ElMessage.info(`忽略问题: ${issue.id}`)
}

const refreshRelatedData = () => {
  relatedData.loading = true
  setTimeout(() => {
    relatedData.loading = false
    ElMessage.success('刷新关联数据完成')
  }, 1000)
}

const syncWithExternal = () => {
  ElMessage.info('同步外部数据')
}

const viewOddsData = () => {
  ElMessage.info('查看赔率数据')
}

const viewIntelligenceData = () => {
  ElMessage.info('查看情报数据')
}

const viewPredictionData = () => {
  ElMessage.info('查看预测数据')
}

const getDataStatusTagType = (status) => {
  switch(status) {
    case 'ok': return 'success'
    case 'warning': return 'warning'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const viewDataDetails = (data) => {
  ElMessage.info(`查看${data.type}详情`)
}

const refreshData = (data) => {
  ElMessage.info(`刷新${data.type}数据`)
}

const closeMatchDialog = () => {
  showMatchDialog.value = false
}

const saveMatch = () => {
  ElMessage.success(isEditing.value ? '更新比赛成功' : '新增比赛成功')
  showMatchDialog.value = false
}

// 初始化数据
onMounted(() => {
  // 模拟加载初始数据
  matchData.value = [
    { 
      id: 1, 
      matchId: 'M20240115001', 
      homeTeam: '曼联', 
      awayTeam: '利物浦', 
      league: '英超', 
      matchTime: '2024-01-15 20:00:00', 
      status: 'pending',
      score: '-' 
    },
    { 
      id: 2, 
      matchId: 'M20240115002', 
      homeTeam: '巴萨', 
      awayTeam: '皇马', 
      league: '西甲', 
      matchTime: '2024-01-16 03:00:00', 
      status: 'pending',
      score: '-' 
    },
    { 
      id: 3, 
      matchId: 'M20240114001', 
      homeTeam: '拜仁', 
      awayTeam: '多特蒙德', 
      league: '德甲', 
      matchTime: '2024-01-14 22:30:00', 
      status: 'finished',
      score: '3:1' 
    },
    { 
      id: 4, 
      matchId: 'M20240114002', 
      homeTeam: '尤文图斯', 
      awayTeam: 'AC米兰', 
      league: '意甲', 
      matchTime: '2024-01-14 21:45:00', 
      status: 'ongoing',
      score: '1:0' 
    },
    { 
      id: 5, 
      matchId: 'M20240117001', 
      homeTeam: '曼城', 
      awayTeam: '切尔西', 
      league: '英超', 
      matchTime: '2024-01-17 19:30:00', 
      status: 'postponed',
      score: '-' 
    }
  ]
  
  validationIssuesData.value = [
    { 
      id: 'VI001', 
      matchId: 'M20240115001', 
      type: 'missing', 
      typeText: '数据缺失', 
      description: '比赛M20240115001缺少客队教练信息', 
      severity: 'medium', 
      severityText: '中', 
      detectedTime: '2024-01-15 09:30:15' 
    },
    { 
      id: 'VI002', 
      matchId: 'M20240115003', 
      type: 'inconsistent', 
      typeText: '数据不一致', 
      description: '比赛M20240115003的联赛信息与其他数据源不一致', 
      severity: 'high', 
      severityText: '高', 
      detectedTime: '2024-01-15 08:45:30' 
    }
  ]
  
  relatedData.detailList = [
    { 
      type: '赔率', 
      source: '竞彩网', 
      lastUpdate: '2024-01-15 10:30:25', 
      status: 'ok', 
      statusText: '正常', 
      records: 2340 
    },
    { 
      type: '情报', 
      source: '体育新闻', 
      lastUpdate: '2024-01-15 09:45:12', 
      status: 'warning', 
      statusText: '警告', 
      records: 1240 
    },
    { 
      type: '预测', 
      source: 'AI模型', 
      lastUpdate: '2024-01-15 11:20:33', 
      status: 'ok', 
      statusText: '正常', 
      records: 890 
    }
  ]
})
</script>

<style scoped>
.competition-management-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.quick-actions {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  position: relative;
  overflow: hidden;
}

.stats-content {
  float: left;
}

.stats-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 32px;
  color: #409EFF;
  opacity: 0.3;
}

.management-tabs {
  background: white;
  padding: 0;
  border-radius: 4px;
}

.tab-content {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.filters {
  margin-bottom: 0;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.team {
  font-weight: 500;
}

.home-team {
  color: #67C23A;
}

.away-team {
  color: #F56C6C;
}

.vs {
  color: #909399;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.validation-summary {
  margin-bottom: 20px;
}

.validation-item {
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  text-align: center;
}

.validation-title {
  font-weight: 500;
  margin-bottom: 10px;
}

.related-data-card {
  margin-bottom: 20px;
}

.related-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.related-content {
  text-align: center;
}

.related-content p {
  margin: 10px 0;
  color: #909399;
  font-size: 14px;
}

.related-data-table {
  margin-top: 20px;
}

.related-data-table h4 {
  margin-bottom: 15px;
  color: #303133;
}

.matches-card :deep(.el-card__body) {
  padding-left: 0;
  padding-right: 0;
  padding-top: 20px;
}

.matches-card :deep(.el-table) {
  width: 100%;
  table-layout: fixed;
}

.matches-card :deep(.el-form) {
  padding: 0 20px 20px;
}

.filters {
  margin: 0 20px 20px 20px;
}
</style>
