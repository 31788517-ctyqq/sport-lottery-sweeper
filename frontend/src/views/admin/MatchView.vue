<template>
  <div class="match-view">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>⚽ 比赛视图</h3>
            <p class="subtitle">比赛详情、数据和分析</p>
          </div>
          <div class="header-actions">
            <el-date-picker
              v-model="dateFilter"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
            <el-button type="primary" @click="loadMatches">加载比赛</el-button>
          </div>
        </div>
      </template>

      <!-- 比赛筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索联赛/队伍" @keyup.enter="searchMatches" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="leagueFilter" placeholder="联赛筛选" style="width: 100%;" @change="filterMatches">
            <el-option label="全部联赛" value="" />
            <el-option label="英超" value="英超" />
            <el-option label="西甲" value="西甲" />
            <el-option label="德甲" value="德甲" />
            <el-option label="意甲" value="意甲" />
            <el-option label="法甲" value="法甲" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 100%;" @change="filterMatches">
            <el-option label="全部状态" value="" />
            <el-option label="未开始" value="scheduled" />
            <el-option label="进行中" value="live" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchMatches">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 比赛列表 -->
      <el-table 
        :data="displayedMatches" 
        style="width: 100%" 
        stripe 
        @row-click="selectMatch"
        v-loading="loading"
        row-key="id"
        :expand-row-keys="expandedRows"
      >
        <el-table-column type="expand">
          <template #default="props">
            <el-row :gutter="20">
              <el-col :span="12">
                <h4>详细数据</h4>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="主队排名">
                    {{ props.row.homeTeamRank }}
                  </el-descriptions-item>
                  <el-descriptions-item label="客队排名">
                    {{ props.row.awayTeamRank }}
                  </el-descriptions-item>
                  <el-descriptions-item label="主队近期战绩">
                    {{ props.row.homeRecentRecord }}
                  </el-descriptions-item>
                  <el-descriptions-item label="客队近期战绩">
                    {{ props.row.awayRecentRecord }}
                  </el-descriptions-item>
                  <el-descriptions-item label="历史交锋">
                    {{ props.row.headToHead }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-col>
              <el-col :span="12">
                <h4>AI预测</h4>
                <div class="prediction-section">
                  <el-progress 
                    :percentage="props.row.prediction.homeWin * 100" 
                    :stroke-width="20" 
                    :color="progressColors"
                    :format='() => `主胜 ${(props.row.prediction.homeWin * 100).toFixed(1)}%`'
                  />
                  <el-progress 
                    :percentage="props.row.prediction.draw * 100" 
                    :stroke-width="20" 
                    :color="progressColors"
                    :format='() => `平局 ${(props.row.prediction.draw * 100).toFixed(1)}%`'
                  />
                  <el-progress 
                    :percentage="props.row.prediction.awayWin * 100" 
                    :stroke-width="20" 
                    :color="progressColors"
                    :format='() => `客胜 ${(props.row.prediction.awayWin * 100).toFixed(1)}%`'
                  />
                  <div class="confidence-level">
                    预测置信度: <el-tag type="success">{{ (props.row.prediction.confidence * 100).toFixed(1) }}%</el-tag>
                  </div>
                </div>
              </el-col>
            </el-row>
          </template>
        </el-table-column>
        
        <el-table-column prop="matchTime" label="时间" width="120" />
        <el-table-column prop="league" label="联赛" width="120" />
        <el-table-column label="主队" width="150">
          <template #default="scope">
            <div class="team-cell">
              <span>{{ scope.row.homeTeam }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="比分" width="100" align="center">
          <template #default="scope">
            <div class="score-cell">
              <span v-if="scope.row.status === 'finished'">{{ scope.row.score }}</span>
              <span v-else-if="scope.row.status === 'live'" class="live-status">LIVE {{ scope.row.score }}</span>
              <span v-else>-:-</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="客队" width="150">
          <template #default="scope">
            <div class="team-cell">
              <span>{{ scope.row.awayTeam }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="SP值" width="150">
          <template #default="scope">
            <div class="sp-values">
              <el-tag size="small" type="primary">主:{{ scope.row.sp.home }}</el-tag>
              <el-tag size="small" type="warning">平:{{ scope.row.sp.draw }}</el-tag>
              <el-tag size="small" type="primary">客:{{ scope.row.sp.away }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="欧洲赔率" width="180">
          <template #default="scope">
            <div class="odd-values">
              <el-tag size="small" type="info">主:{{ scope.row.euroOdd.home }}</el-tag>
              <el-tag size="small" type="info">平:{{ scope.row.euroOdd.draw }}</el-tag>
              <el-tag size="small" type="info">客:{{ scope.row.euroOdd.away }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click.stop="viewMatchDetails(scope.row)">详情</el-button>
            <el-button size="small" type="primary" @click.stop="analyzeMatch(scope.row)">分析</el-button>
            <el-button size="small" type="success" @click.stop="generatePrediction(scope.row)">预测</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalMatches"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <!-- 比赛详情对话框 -->
      <el-dialog v-model="detailDialogVisible" title="比赛详情" width="800px">
        <div v-if="selectedMatch" class="match-detail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="比赛时间">{{ selectedMatch.matchTime }}</el-descriptions-item>
            <el-descriptions-item label="联赛">{{ selectedMatch.league }}</el-descriptions-item>
            <el-descriptions-item label="主队">{{ selectedMatch.homeTeam }}</el-descriptions-item>
            <el-descriptions-item label="客队">{{ selectedMatch.awayTeam }}</el-descriptions-item>
            <el-descriptions-item label="比分" :span="2">
              {{ selectedMatch.status === 'finished' ? selectedMatch.score : 'VS' }}
            </el-descriptions-item>
            <el-descriptions-item label="SP值">
              主:{{ selectedMatch.sp.home }} | 平:{{ selectedMatch.sp.draw }} | 客:{{ selectedMatch.sp.away }}
            </el-descriptions-item>
            <el-descriptions-item label="欧洲赔率">
              主:{{ selectedMatch.euroOdd.home }} | 平:{{ selectedMatch.euroOdd.draw }} | 客:{{ selectedMatch.euroOdd.away }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(selectedMatch.status)">
                {{ getStatusLabel(selectedMatch.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="比赛场地">{{ selectedMatch.venue || '待定' }}</el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <h4>AI预测分析</h4>
          <div class="prediction-analysis">
            <div class="prediction-bars">
              <div class="prediction-bar">
                <span>主胜: {{ (selectedMatch.prediction.homeWin * 100).toFixed(1) }}%</span>
                <el-progress 
                  :percentage="selectedMatch.prediction.homeWin * 100" 
                  :color="progressColors" 
                  :show-text="false"
                />
              </div>
              <div class="prediction-bar">
                <span>平局: {{ (selectedMatch.prediction.draw * 100).toFixed(1) }}%</span>
                <el-progress 
                  :percentage="selectedMatch.prediction.draw * 100" 
                  :color="progressColors" 
                  :show-text="false"
                />
              </div>
              <div class="prediction-bar">
                <span>客胜: {{ (selectedMatch.prediction.awayWin * 100).toFixed(1) }}%</span>
                <el-progress 
                  :percentage="selectedMatch.prediction.awayWin * 100" 
                  :color="progressColors" 
                  :show-text="false"
                />
              </div>
            </div>
            <div class="confidence-info">
              <p><strong>置信度:</strong> {{ (selectedMatch.prediction.confidence * 100).toFixed(1) }}%</p>
              <p><strong>预测依据:</strong> {{ selectedMatch.prediction.reasoning }}</p>
            </div>
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedMatch = ref(null)
const expandedRows = ref([])

// 表格数据
const matches = ref([
  {
    id: 1,
    matchTime: '2023-05-21 20:00',
    league: '英超',
    homeTeam: '曼城',
    awayTeam: '阿森纳',
    score: '3:1',
    sp: { home: 2.1, draw: 3.2, away: 3.5 },
    euroOdd: { home: 2.05, draw: 3.15, away: 3.45 },
    status: 'finished',
    homeTeamRank: 1,
    awayTeamRank: 2,
    homeRecentRecord: 'W W D W W',
    awayRecentRecord: 'W D W W L',
    headToHead: '曼城 3胜 2平 1负 阿森纳',
    venue: '伊蒂哈德球场',
    prediction: {
      homeWin: 0.52,
      draw: 0.28,
      awayWin: 0.20,
      confidence: 0.85,
      reasoning: '基于近期状态、历史交锋和赔率数据的综合分析'
    }
  },
  {
    id: 2,
    matchTime: '2023-05-22 19:30',
    league: '西甲',
    homeTeam: '巴塞罗那',
    awayTeam: '皇家马德里',
    score: '2:1',
    sp: { home: 2.5, draw: 3.1, away: 2.8 },
    euroOdd: { home: 2.45, draw: 3.05, away: 2.75 },
    status: 'finished',
    homeTeamRank: 2,
    awayTeamRank: 1,
    homeRecentRecord: 'W L W W W',
    awayRecentRecord: 'W W D W L',
    headToHead: '巴萨 4胜 3平 3负 皇马',
    venue: '诺坎普球场',
    prediction: {
      homeWin: 0.42,
      draw: 0.30,
      awayWin: 0.28,
      confidence: 0.78,
      reasoning: '德比大战，实力相当，主场优势略显'
    }
  },
  {
    id: 3,
    matchTime: '2023-05-23 21:00',
    league: '德甲',
    homeTeam: '拜仁慕尼黑',
    awayTeam: '多特蒙德',
    score: '-:-',
    sp: { home: 1.8, draw: 3.5, away: 4.2 },
    euroOdd: { home: 1.78, draw: 3.45, away: 4.15 },
    status: 'scheduled',
    homeTeamRank: 1,
    awayTeamRank: 2,
    homeRecentRecord: 'W W W D W',
    awayRecentRecord: 'L W W W D',
    headToHead: '拜仁 5胜 2平 1负 多特',
    venue: '安联竞技场',
    prediction: {
      homeWin: 0.65,
      draw: 0.22,
      awayWin: 0.13,
      confidence: 0.82,
      reasoning: '拜仁主场强势，实力占优'
    }
  },
  {
    id: 4,
    matchTime: '2023-05-23 15:00',
    league: '意甲',
    homeTeam: 'AC米兰',
    awayTeam: '国际米兰',
    score: '1:1',
    sp: { home: 2.7, draw: 3.0, away: 2.6 },
    euroOdd: { home: 2.65, draw: 2.95, away: 2.55 },
    status: 'live',
    homeTeamRank: 3,
    awayTeamRank: 1,
    homeRecentRecord: 'D W L W D',
    awayRecentRecord: 'W W W L W',
    headToHead: '米兰 2胜 4平 2负 国米',
    venue: '圣西罗球场',
    prediction: {
      homeWin: 0.35,
      draw: 0.35,
      awayWin: 0.30,
      confidence: 0.75,
      reasoning: '米兰城德比，实力接近，平局概率较高'
    }
  }
])

// 筛选和分页数据
const displayedMatches = ref([...matches.value])
const currentPage = ref(1)
const pageSize = ref(10)
const totalMatches = ref(matches.value.length)
const searchQuery = ref('')
const leagueFilter = ref('')
const statusFilter = ref('')
const dateFilter = ref('2023-05-23')

// 进度条颜色
const progressColors = ['#13ce66', '#1890ff', '#f2637b']

// 方法
const getStatusLabel = (status) => {
  const statuses = {
    scheduled: '未开始',
    live: '进行中',
    finished: '已结束'
  }
  return statuses[status] || status
}

const getStatusType = (status) => {
  const types = {
    scheduled: 'info',
    live: 'warning',
    finished: 'success'
  }
  return types[status] || 'info'
}

const loadMatches = () => {
  // 模拟加载比赛数据
  loading.value = true
  setTimeout(() => {
    loading.value = false
    applyFilters()
    ElMessage.success(`加载了 ${matches.value.length} 场比赛`)
  }, 800)
}

const searchMatches = () => {
  applyFilters()
}

const filterMatches = () => {
  applyFilters()
}

const resetFilters = () => {
  searchQuery.value = ''
  leagueFilter.value = ''
  statusFilter.value = ''
  applyFilters()
}

const applyFilters = () => {
  let result = [...matches.value]
  
  // 应用搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(match => 
      match.league.toLowerCase().includes(query) || 
      match.homeTeam.toLowerCase().includes(query) ||
      match.awayTeam.toLowerCase().includes(query)
    )
  }
  
  // 应用联赛筛选
  if (leagueFilter.value) {
    result = result.filter(match => match.league === leagueFilter.value)
  }
  
  // 应用状态筛选
  if (statusFilter.value) {
    result = result.filter(match => match.status === statusFilter.value)
  }
  
  displayedMatches.value = result
  totalMatches.value = result.length
}

const selectMatch = (row) => {
  // 切换展开行
  if (expandedRows.value.includes(row.id)) {
    expandedRows.value = expandedRows.value.filter(id => id !== row.id)
  } else {
    expandedRows.value = [row.id]
  }
}

const viewMatchDetails = (match) => {
  selectedMatch.value = match
  detailDialogVisible.value = true
}

const analyzeMatch = (match) => {
  ElMessage.info(`正在分析比赛: ${match.homeTeam} VS ${match.awayTeam}`)
  // 这里可以调用实际的分析API
}

const generatePrediction = (match) => {
  ElMessage.success(`已为比赛生成预测: ${match.homeTeam} VS ${match.awayTeam}`)
  // 这里可以调用实际的预测API
}

const handleSizeChange = (size) => {
  pageSize.value = size
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 初始化数据
onMounted(() => {
  applyFilters()
})
</script>

<style scoped>
.card-container {
  margin: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div:first-child h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.team-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-cell {
  font-weight: bold;
  color: #303133;
}

.live-status {
  color: #e74c3c;
  font-weight: bold;
}

.sp-values, .odd-values {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.match-detail {
  padding: 20px 0;
}

.prediction-analysis {
  margin-top: 20px;
}

.prediction-bars {
  margin-bottom: 20px;
}

.prediction-bar {
  margin-bottom: 10px;
}

.confidence-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.confidence-level {
  margin-top: 10px;
  text-align: right;
}
</style>