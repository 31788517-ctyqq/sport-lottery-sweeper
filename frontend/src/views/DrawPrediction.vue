<template>
  <div class="draw-prediction-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">🔮 预测分析</h1>
      <p class="page-description">比赛结果预测与分析</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索预测..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="pending">待分析</option>
          <option value="analyzing">分析中</option>
          <option value="completed">已完成</option>
          <option value="archived">已归档</option>
        </select>
        
        <select v-model="filters.league" @change="handleFilterChange">
          <option value="">全部联赛</option>
          <option value="premier">英超</option>
          <option value="la_liga">西甲</option>
          <option value="bundesliga">德甲</option>
          <option value="serie_a">意甲</option>
          <option value="ligue_1">法甲</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="createNewPrediction">
          <span>➕</span> 新建预测
        </button>
        <button class="action-btn secondary" @click="refreshPredictions">
          <span>🔄</span> 刷新
        </button>
        <button class="action-btn tertiary" @click="runBatchAnalysis">
          <span>⚙️</span> 批量分析
        </button>
      </div>
    </div>

    <!-- 预测统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="icon-total">📊</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">总预测数</div>
          <div class="stat-value">{{ stats.totalPredictions }}</div>
          <div class="stat-change positive">+{{ stats.newToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon accuracy">
          <i class="icon-accuracy">🎯</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">准确率</div>
          <div class="stat-value">{{ stats.accuracyRate }}%</div>
          <div class="stat-change" :class="accuracyTrendClass">{{ stats.accuracyTrend }}%</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon win">
          <i class="icon-win">✅</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">胜率</div>
          <div class="stat-value">{{ stats.winRate }}%</div>
          <div class="stat-change positive">+{{ stats.winTrend }}%</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon processing">
          <i class="icon-processing">⚡</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">分析中</div>
          <div class="stat-value">{{ stats.analyzingCount }}</div>
          <div class="stat-change neutral">{{ stats.completedToday }} 今日完成</div>
        </div>
      </div>
    </div>

    <!-- 预测列表 -->
    <div class="predictions-section">
      <div class="section-header">
        <h2>📋 预测列表</h2>
        <div class="predictions-stats">
          <span class="stat-item">显示: {{ filteredPredictions.length }} 条</span>
          <span class="stat-item total">总计: {{ allPredictions.length }} 条</span>
        </div>
      </div>
      
      <div class="predictions-table-container">
        <table class="predictions-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" /></th>
              <th>比赛</th>
              <th>联赛</th>
              <th>预测主队胜率</th>
              <th>预测平局率</th>
              <th>预测客队胜率</th>
              <th>置信度</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prediction in paginatedPredictions" :key="prediction.id" :class="{ selected: prediction.selected }">
              <td><input type="checkbox" v-model="prediction.selected" /></td>
              <td>
                <div class="match-info">
                  <span class="home-team">{{ prediction.homeTeam }}</span>
                  <span class="vs">VS</span>
                  <span class="away-team">{{ prediction.awayTeam }}</span>
                </div>
              </td>
              <td>{{ leagueNames[prediction.league] || prediction.league }}</td>
              <td>{{ prediction.homeWinRate }}%</td>
              <td class="draw-rate">{{ prediction.drawRate }}%</td>
              <td>{{ prediction.awayWinRate }}%</td>
              <td>
                <span class="confidence-badge" :class="getConfidenceClass(prediction.confidence)">
                  {{ prediction.confidence }}%
                </span>
              </td>
              <td>
                <span class="status-badge" :class="prediction.status">
                  {{ statusLabels[prediction.status] }}
                </span>
              </td>
              <td>{{ formatDate(prediction.createdAt) }}</td>
              <td>
                <button class="action-btn view" @click="viewPrediction(prediction)">👁️</button>
                <button class="action-btn edit" @click="editPrediction(prediction)">✏️</button>
                <button class="action-btn analyze" @click="analyzePrediction(prediction)" v-if="prediction.status !== 'completed'">🔍</button>
                <button class="action-btn delete" @click="deletePrediction(prediction)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button 
          class="pagination-btn" 
          @click="prevPage" 
          :disabled="currentPage === 1"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button 
          class="pagination-btn" 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 添加/编辑预测对话框 -->
    <div v-if="showPredictionModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingPrediction ? '编辑预测' : '新建预测' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>联赛 *</label>
            <select v-model="currentPrediction.league">
              <option value="premier">英超</option>
              <option value="la_liga">西甲</option>
              <option value="bundesliga">德甲</option>
              <option value="serie_a">意甲</option>
              <option value="ligue_1">法甲</option>
              <option value="other">其他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>主队 *</label>
            <input 
              v-model="currentPrediction.homeTeam" 
              type="text" 
              placeholder="输入主队名称"
            />
          </div>
          
          <div class="form-group">
            <label>客队 *</label>
            <input 
              v-model="currentPrediction.awayTeam" 
              type="text" 
              placeholder="输入客队名称"
            />
          </div>
          
          <div class="form-group">
            <label>预测日期</label>
            <input 
              v-model="currentPrediction.predictionDate" 
              type="date"
            />
          </div>
          
          <div class="form-group">
            <label>预测主队胜率 (%)</label>
            <input 
              v-model.number="currentPrediction.homeWinRate" 
              type="number" 
              min="0" 
              max="100"
              placeholder="输入主队胜率"
            />
          </div>
          
          <div class="form-group">
            <label>预测平局率 (%)</label>
            <input 
              v-model.number="currentPrediction.drawRate" 
              type="number" 
              min="0" 
              max="100"
              placeholder="输入平局率"
            />
          </div>
          
          <div class="form-group">
            <label>预测客队胜率 (%)</label>
            <input 
              v-model.number="currentPrediction.awayWinRate" 
              type="number" 
              min="0" 
              max="100"
              placeholder="输入客队胜率"
            />
          </div>
          
          <div class="form-group">
            <label>置信度 (%)</label>
            <input 
              v-model.number="currentPrediction.confidence" 
              type="number" 
              min="0" 
              max="100"
              placeholder="输入置信度"
            />
          </div>
          
          <div class="form-group">
            <label>状态</label>
            <select v-model="currentPrediction.status">
              <option value="pending">待分析</option>
              <option value="analyzing">分析中</option>
              <option value="completed">已完成</option>
              <option value="archived">已归档</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="savePrediction"
            :disabled="!isValidPrediction"
          >
            {{ editingPrediction ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 预测详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>预测详情 - {{ selectedPrediction.homeTeam }} VS {{ selectedPrediction.awayTeam }}</h3>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">联赛</div>
            <div class="detail-value">{{ leagueNames[selectedPrediction.league] || selectedPrediction.league }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">比赛</div>
            <div class="detail-value">{{ selectedPrediction.homeTeam }} VS {{ selectedPrediction.awayTeam }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">预测日期</div>
            <div class="detail-value">{{ formatDate(selectedPrediction.predictionDate) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">主队胜率</div>
            <div class="detail-value">{{ selectedPrediction.homeWinRate }}%</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">平局率</div>
            <div class="detail-value">{{ selectedPrediction.drawRate }}%</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">客队胜率</div>
            <div class="detail-value">{{ selectedPrediction.awayWinRate }}%</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">置信度</div>
            <div class="detail-value">
              <span class="confidence-badge" :class="getConfidenceClass(selectedPrediction.confidence)">
                {{ selectedPrediction.confidence }}%
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <span class="status-badge" :class="selectedPrediction.status">
                {{ statusLabels[selectedPrediction.status] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">创建时间</div>
            <div class="detail-value">{{ formatDate(selectedPrediction.createdAt) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">更新时间</div>
            <div class="detail-value">{{ formatDate(selectedPrediction.updatedAt) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">分析详情</div>
            <div class="detail-value">
              <div class="analysis-details">
                <p>基于历史数据、球队状态、伤病情况等因素的综合分析：</p>
                <ul>
                  <li>主队近期状态：{{ selectedPrediction.analysis?.homeForm || '良好' }}</li>
                  <li>客队近期状态：{{ selectedPrediction.analysis?.awayForm || '一般' }}</li>
                  <li>历史交锋：{{ selectedPrediction.analysis?.headToHead || '主队占优' }}</li>
                  <li>关键球员：{{ selectedPrediction.analysis?.keyPlayers || '无重大伤病' }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeDetailModal">关闭</button>
          <button class="btn primary" @click="editPrediction(selectedPrediction)">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 模拟预测数据
const allPredictions = ref([
  {
    id: 1,
    homeTeam: '曼城',
    awayTeam: '切尔西',
    league: 'premier',
    homeWinRate: 65,
    drawRate: 20,
    awayWinRate: 15,
    confidence: 85,
    status: 'completed',
    predictionDate: new Date(Date.now() + 86400000),
    createdAt: new Date(Date.now() - 86400000),
    updatedAt: new Date(Date.now() - 43200000),
    analysis: {
      homeForm: '极佳',
      awayForm: '良好',
      headToHead: '主队占优',
      keyPlayers: '无重大伤病'
    }
  },
  {
    id: 2,
    homeTeam: '巴塞罗那',
    awayTeam: '皇家马德里',
    league: 'la_liga',
    homeWinRate: 45,
    drawRate: 30,
    awayWinRate: 25,
    confidence: 78,
    status: 'completed',
    predictionDate: new Date(Date.now() + 172800000),
    createdAt: new Date(Date.now() - 172800000),
    updatedAt: new Date(Date.now() - 86400000),
    analysis: {
      homeForm: '良好',
      awayForm: '优秀',
      headToHead: '势均力敌',
      keyPlayers: '双方主力齐整'
    }
  },
  {
    id: 3,
    homeTeam: '拜仁慕尼黑',
    awayTeam: '多特蒙德',
    league: 'bundesliga',
    homeWinRate: 70,
    drawRate: 18,
    awayWinRate: 12,
    confidence: 90,
    status: 'analyzing',
    predictionDate: new Date(Date.now() + 259200000),
    createdAt: new Date(Date.now() - 3600000),
    updatedAt: new Date(Date.now() - 1800000),
    analysis: {
      homeForm: '优秀',
      awayForm: '良好',
      headToHead: '主队历史优势明显',
      keyPlayers: '主队主力前锋伤愈复出'
    }
  },
  {
    id: 4,
    homeTeam: '尤文图斯',
    awayTeam: 'AC米兰',
    league: 'serie_a',
    homeWinRate: 40,
    drawRate: 35,
    awayWinRate: 25,
    confidence: 72,
    status: 'pending',
    predictionDate: new Date(Date.now() + 345600000),
    createdAt: new Date(Date.now() - 7200000),
    updatedAt: new Date(Date.now() - 3600000),
    analysis: {
      homeForm: '一般',
      awayForm: '良好',
      headToHead: '主队稍占优势',
      keyPlayers: '客队中场核心缺阵'
    }
  },
  {
    id: 5,
    homeTeam: '巴黎圣日耳曼',
    awayTeam: '马赛',
    league: 'ligue_1',
    homeWinRate: 75,
    drawRate: 15,
    awayWinRate: 10,
    confidence: 88,
    status: 'completed',
    predictionDate: new Date(Date.now() - 86400000),
    createdAt: new Date(Date.now() - 259200000),
    updatedAt: new Date(Date.now() - 172800000),
    analysis: {
      homeForm: '极佳',
      awayForm: '一般',
      headToHead: '主队绝对优势',
      keyPlayers: '主队三叉戟状态火热'
    }
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  status: '',
  league: ''
})

// 统计数据
const stats = ref({
  totalPredictions: 0,
  newToday: 0,
  accuracyRate: 0,
  accuracyTrend: 0,
  winRate: 0,
  winTrend: 0,
  analyzingCount: 0,
  completedToday: 0
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 预测模态框
const showPredictionModal = ref(false)
const editingPrediction = ref(null)
const currentPrediction = ref({
  id: null,
  homeTeam: '',
  awayTeam: '',
  league: 'premier',
  homeWinRate: 33,
  drawRate: 33,
  awayWinRate: 34,
  confidence: 50,
  status: 'pending',
  predictionDate: new Date(Date.now() + 86400000)
})

// 详情模态框
const showDetailModal = ref(false)
const selectedPrediction = ref({})

// 计算属性
const filteredPredictions = computed(() => {
  let predictions = [...allPredictions.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    predictions = predictions.filter(pred => 
      pred.homeTeam.toLowerCase().includes(keyword) ||
      pred.awayTeam.toLowerCase().includes(keyword) ||
      pred.league.toLowerCase().includes(keyword) ||
      leagueNames[pred.league]?.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.status) {
    predictions = predictions.filter(pred => pred.status === filters.value.status)
  }
  
  if (filters.value.league) {
    predictions = predictions.filter(pred => pred.league === filters.value.league)
  }
  
  return predictions
})

const paginatedPredictions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPredictions.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredPredictions.value.length / pageSize.value)
})

const leagueNames = {
  premier: '英超',
  la_liga: '西甲',
  bundesliga: '德甲',
  serie_a: '意甲',
  ligue_1: '法甲',
  other: '其他'
}

const statusLabels = {
  pending: '待分析',
  analyzing: '分析中',
  completed: '已完成',
  archived: '已归档'
}

const isValidPrediction = computed(() => {
  return currentPrediction.value.homeTeam.trim() !== '' && 
         currentPrediction.value.awayTeam.trim() !== '' &&
         currentPrediction.value.league !== '' &&
         currentPrediction.value.homeWinRate !== null &&
         currentPrediction.value.drawRate !== null &&
         currentPrediction.value.awayWinRate !== null
})

const accuracyTrendClass = computed(() => {
  return stats.value.accuracyTrend >= 0 ? 'positive' : 'negative'
})

// 方法
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
  currentPage.value = 1
}

const handleFilterChange = () => {
  console.log('筛选条件改变:', filters.value)
  currentPage.value = 1
}

const refreshPredictions = () => {
  console.log('刷新预测列表')
  currentPage.value = 1
}

const createNewPrediction = () => {
  editingPrediction.value = null
  currentPrediction.value = {
    id: null,
    homeTeam: '',
    awayTeam: '',
    league: 'premier',
    homeWinRate: 33,
    drawRate: 33,
    awayWinRate: 34,
    confidence: 50,
    status: 'pending',
    predictionDate: new Date(Date.now() + 86400000),
    createdAt: new Date(),
    updatedAt: new Date()
  }
  showPredictionModal.value = true
}

const editPrediction = (prediction) => {
  editingPrediction.value = prediction
  currentPrediction.value = { ...prediction }
  showPredictionModal.value = true
}

const closeModal = () => {
  showPredictionModal.value = false
  editingPrediction.value = null
}

const savePrediction = () => {
  if (!isValidPrediction.value) return
  
  if (editingPrediction.value) {
    // 更新现有预测
    const index = allPredictions.value.findIndex(p => p.id === editingPrediction.value.id)
    if (index !== -1) {
      allPredictions.value[index] = { ...currentPrediction.value, id: editingPrediction.value.id }
    }
  } else {
    // 添加新预测
    const newId = Math.max(...allPredictions.value.map(p => p.id)) + 1
    allPredictions.value.push({
      ...currentPrediction.value,
      id: newId,
      createdAt: new Date(),
      updatedAt: new Date()
    })
  }
  
  closeModal()
}

const viewPrediction = (prediction) => {
  selectedPrediction.value = prediction
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedPrediction.value = {}
}

const deletePrediction = (prediction) => {
  if (confirm(`确定要删除 "${prediction.homeTeam} VS ${prediction.awayTeam}" 的预测吗？`)) {
    const index = allPredictions.value.indexOf(prediction)
    if (index !== -1) {
      allPredictions.value.splice(index, 1)
    }
  }
}

const analyzePrediction = (prediction) => {
  console.log(`开始分析预测: ${prediction.homeTeam} VS ${prediction.awayTeam}`)
  prediction.status = 'analyzing'
  prediction.updatedAt = new Date()
  
  // 模拟分析过程
  setTimeout(() => {
    prediction.status = 'completed'
    prediction.updatedAt = new Date()
  }, 3000)
}

const runBatchAnalysis = () => {
  console.log('开始批量分析...')
  // 模拟批量分析过程
  allPredictions.value.forEach(pred => {
    if (pred.status === 'pending') {
      pred.status = 'analyzing'
      pred.updatedAt = new Date()
      
      // 模拟分析完成后更新状态
      setTimeout(() => {
        pred.status = 'completed'
        pred.updatedAt = new Date()
      }, 2000)
    }
  })
}

const toggleSelectAll = () => {
  const isSelected = paginatedPredictions.value.some(item => item.selected)
  paginatedPredictions.value.forEach(item => item.selected = !isSelected)
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 80) return 'high'
  if (confidence >= 60) return 'medium'
  return 'low'
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 初始化数据
onMounted(() => {
  console.log('Draw Prediction 页面已加载')
  
  // 计算统计数据
  stats.value.totalPredictions = allPredictions.value.length
  stats.value.newToday = allPredictions.value.filter(p => 
    new Date(p.createdAt).toDateString() === new Date().toDateString()
  ).length
  stats.value.accuracyRate = 78.5
  stats.value.accuracyTrend = 2.3
  stats.value.winRate = 65.2
  stats.value.winTrend = 1.5
  stats.value.analyzingCount = allPredictions.value.filter(p => p.status === 'analyzing').length
  stats.value.completedToday = allPredictions.value.filter(p => 
    p.status === 'completed' && new Date(p.updatedAt).toDateString() === new Date().toDateString()
  ).length
})
</script>

<style scoped>
.draw-prediction-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 工具栏样式 */
.toolbar {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 10px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-btn:hover {
  background: #2563eb;
}

.filters {
  display: flex;
  gap: 12px;
}

.filters select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn.primary {
  background: #10b981;
  color: white;
}

.action-btn.primary:hover {
  background: #059669;
}

.action-btn.secondary {
  background: #6366f1;
  color: white;
}

.action-btn.secondary:hover {
  background: #4f46e5;
}

.action-btn.tertiary {
  background: #f59e0b;
  color: white;
}

.action-btn.tertiary:hover {
  background: #d97706;
}

.action-btn.view {
  background: #e5e7eb;
  color: #374151;
  padding: 6px 10px;
}

.action-btn.view:hover {
  background: #d1d5db;
}

.action-btn.edit {
  background: #94a3b8;
  color: white;
  padding: 6px 10px;
}

.action-btn.edit:hover {
  background: #64748b;
}

.action-btn.analyze {
  background: #a78bfa;
  color: white;
  padding: 6px 10px;
}

.action-btn.analyze:hover {
  background: #8b5cf6;
}

.action-btn.delete {
  background: #ef4444;
  color: white;
  padding: 6px 10px;
}

.action-btn.delete:hover {
  background: #dc2626;
}

/* 统计卡片样式 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.accuracy {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.win {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.processing {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.negative {
  color: #ef4444;
}

.stat-change.neutral {
  color: #6b7280;
}

/* 预测区域样式 */
.predictions-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.section-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.predictions-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.predictions-table-container {
  overflow-x: auto;
}

.predictions-table {
  width: 100%;
  border-collapse: collapse;
}

.predictions-table th,
.predictions-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.predictions-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.predictions-table tbody tr:hover {
  background-color: #f9fafb;
}

.predictions-table tbody tr.selected {
  background-color: #e0f2fe;
}

.match-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.home-team {
  font-weight: 600;
  color: #1f2937;
}

.vs {
  color: #6b7280;
  font-size: 12px;
}

.away-team {
  font-weight: 600;
  color: #1f2937;
}

.draw-rate {
  color: #f59e0b;
  font-weight: 600;
}

.confidence-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.confidence-badge.high {
  background: #dcfce7;
  color: #166534;
}

.confidence-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.confidence-badge.low {
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.analyzing {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.archived {
  background: #ddd6fe;
  color: #6d28d9;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.2);
}

.large-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #9ca3af;
}

.close-btn:hover {
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1f2937;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-label {
  width: 120px;
  font-weight: 600;
  color: #374151;
}

.detail-value {
  flex: 1;
  color: #6b7280;
}

.analysis-details ul {
  padding-left: 20px;
  margin: 10px 0;
}

.analysis-details li {
  margin-bottom: 8px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn.cancel:hover {
  background: #e5e7eb;
}

.btn.primary {
  background: #3b82f6;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn.primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .draw-prediction-container {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .predictions-table {
    min-width: 600px;
  }
  
  .predictions-table th,
  .predictions-table td {
    padding: 8px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
  
  .modal-content {
    width: 95vw;
  }
  
  .large-modal {
    width: 95vw;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: auto;
    margin-bottom: 4px;
  }
}
</style>