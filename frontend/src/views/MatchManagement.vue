<template>
  <div class="match-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">⚽ 比赛管理</h1>
      <p class="page-description">管理比赛信息、赛程和相关数据</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索比赛..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="upcoming">未开始</option>
          <option value="live">进行中</option>
          <option value="finished">已完成</option>
          <option value="postponed">推迟</option>
          <option value="cancelled">取消</option>
        </select>
        
        <select v-model="filters.league" @change="handleFilterChange">
          <option value="">全部联赛</option>
          <option value="premier">英超</option>
          <option value="la_liga">西甲</option>
          <option value="bundesliga">德甲</option>
          <option value="serie_a">意甲</option>
          <option value="ligue_1">法甲</option>
        </select>
        
        <select v-model="filters.season" @change="handleFilterChange">
          <option value="">全部赛季</option>
          <option value="2023-2024">2023-2024</option>
          <option value="2022-2023">2022-2023</option>
          <option value="2021-2022">2021-2022</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="createNewMatch">
          <span>➕</span> 新增比赛
        </button>
        <button class="action-btn secondary" @click="refreshMatches">
          <span>🔄</span> 刷新
        </button>
        <button class="action-btn tertiary" @click="syncWithDataSource">
          <span>📡</span> 同步数据
        </button>
      </div>
    </div>

    <!-- 比赛统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="icon-total">⚽</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">总比赛数</div>
          <div class="stat-value">{{ stats.totalMatches }}</div>
          <div class="stat-change positive">+{{ stats.newToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon upcoming">
          <i class="icon-upcoming">⏰</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">即将开始</div>
          <div class="stat-value">{{ stats.upcomingCount }}</div>
          <div class="stat-change neutral">{{ stats.liveCount }} 场进行中</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon finished">
          <i class="icon-finished">✅</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">已完成</div>
          <div class="stat-value">{{ stats.finishedCount }}</div>
          <div class="stat-change positive">+{{ stats.completedToday }} 今日完成</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon accuracy">
          <i class="icon-accuracy">🎯</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">数据准确率</div>
          <div class="stat-value">{{ stats.dataAccuracy }}%</div>
          <div class="stat-change positive">{{ stats.dataUpdatedToday }} 条更新</div>
        </div>
      </div>
    </div>

    <!-- 比赛列表 -->
    <div class="matches-section">
      <div class="section-header">
        <h2>📋 比赛列表</h2>
        <div class="matches-stats">
          <span class="stat-item">显示: {{ filteredMatches.length }} 场</span>
          <span class="stat-item total">总计: {{ allMatches.length }} 场</span>
        </div>
      </div>
      
      <div class="matches-table-container">
        <table class="matches-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" /></th>
              <th>比赛</th>
              <th>联赛</th>
              <th>比分</th>
              <th>状态</th>
              <th>开赛时间</th>
              <th>场馆</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="match in paginatedMatches" :key="match.id" :class="{ selected: match.selected }">
              <td><input type="checkbox" v-model="match.selected" /></td>
              <td class="match-info-cell">
                <div class="match-info">
                  <div class="team home-team">
                    <span class="team-name">{{ match.homeTeam }}</span>
                    <img :src="match.homeTeamLogo" :alt="match.homeTeam" class="team-logo" v-if="match.homeTeamLogo" />
                  </div>
                  <div class="match-vs">VS</div>
                  <div class="team away-team">
                    <img :src="match.awayTeamLogo" :alt="match.awayTeam" class="team-logo" v-if="match.awayTeamLogo" />
                    <span class="team-name">{{ match.awayTeam }}</span>
                  </div>
                </div>
                <div class="match-date">{{ formatDate(match.matchDate) }}</div>
              </td>
              <td>{{ leagueNames[match.league] || match.league }}</td>
              <td>
                <div class="score-display">
                  <span class="home-score">{{ match.homeScore }}</span>
                  <span class="score-separator">-</span>
                  <span class="away-score">{{ match.awayScore }}</span>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="match.status">
                  {{ statusLabels[match.status] }}
                </span>
              </td>
              <td>{{ formatDateTime(match.matchDate) }}</td>
              <td>{{ match.venue || '未知' }}</td>
              <td>
                <button class="action-btn view" @click="viewMatch(match)">👁️</button>
                <button class="action-btn edit" @click="editMatch(match)">✏️</button>
                <button class="action-btn update" @click="updateMatchResult(match)" v-if="match.status === 'live' || (match.status === 'upcoming' && match.canBeUpdated)">🔄</button>
                <button class="action-btn delete" @click="deleteMatch(match)">🗑️</button>
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

    <!-- 添加/编辑比赛对话框 -->
    <div v-if="showMatchModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingMatch ? '编辑比赛' : '新增比赛' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group half-width">
              <label>主队 *</label>
              <input 
                v-model="currentMatch.homeTeam" 
                type="text" 
                placeholder="输入主队名称"
              />
            </div>
            
            <div class="form-group half-width">
              <label>客队 *</label>
              <input 
                v-model="currentMatch.awayTeam" 
                type="text" 
                placeholder="输入客队名称"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>联赛 *</label>
              <select v-model="currentMatch.league">
                <option value="premier">英超</option>
                <option value="la_liga">西甲</option>
                <option value="bundesliga">德甲</option>
                <option value="serie_a">意甲</option>
                <option value="ligue_1">法甲</option>
                <option value="other">其他</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>赛季</label>
              <select v-model="currentMatch.season">
                <option value="2023-2024">2023-2024</option>
                <option value="2022-2023">2022-2023</option>
                <option value="2021-2022">2021-2022</option>
                <option value="2020-2021">2020-2021</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>开赛时间</label>
              <input 
                v-model="currentMatch.matchDate" 
                type="datetime-local"
              />
            </div>
            
            <div class="form-group half-width">
              <label>场馆</label>
              <input 
                v-model="currentMatch.venue" 
                type="text" 
                placeholder="比赛场馆"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>主队得分</label>
              <input 
                v-model.number="currentMatch.homeScore" 
                type="number" 
                min="0"
                :disabled="currentMatch.status !== 'finished'"
              />
            </div>
            
            <div class="form-group half-width">
              <label>客队得分</label>
              <input 
                v-model.number="currentMatch.awayScore" 
                type="number" 
                min="0"
                :disabled="currentMatch.status !== 'finished'"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>状态 *</label>
              <select v-model="currentMatch.status">
                <option value="upcoming">未开始</option>
                <option value="live">进行中</option>
                <option value="finished">已完成</option>
                <option value="postponed">推迟</option>
                <option value="cancelled">取消</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>主队Logo URL</label>
              <input 
                v-model="currentMatch.homeTeamLogo" 
                type="text" 
                placeholder="主队队徽URL"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>备注</label>
            <textarea 
              v-model="currentMatch.notes" 
              placeholder="比赛备注信息"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveMatch"
            :disabled="!isValidMatch"
          >
            {{ editingMatch ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 比赛详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>比赛详情 - {{ selectedMatch.homeTeam }} VS {{ selectedMatch.awayTeam }}</h3>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">比赛</div>
            <div class="detail-value">{{ selectedMatch.homeTeam }} VS {{ selectedMatch.awayTeam }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">联赛</div>
            <div class="detail-value">{{ leagueNames[selectedMatch.league] || selectedMatch.league }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">赛季</div>
            <div class="detail-value">{{ selectedMatch.season }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">开赛时间</div>
            <div class="detail-value">{{ formatDateTime(selectedMatch.matchDate) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">场馆</div>
            <div class="detail-value">{{ selectedMatch.venue || '未知' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">比分</div>
            <div class="detail-value">
              {{ selectedMatch.homeScore }} - {{ selectedMatch.awayScore }}
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <span class="status-badge" :class="selectedMatch.status">
                {{ statusLabels[selectedMatch.status] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">创建时间</div>
            <div class="detail-value">{{ formatDateTime(selectedMatch.createdAt) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">更新时间</div>
            <div class="detail-value">{{ formatDateTime(selectedMatch.updatedAt) }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">备注</div>
            <div class="detail-value">{{ selectedMatch.notes || '无备注' }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">相关数据</div>
            <div class="detail-value">
              <div class="data-stats">
                <p>这场比赛的相关数据统计：</p>
                <ul>
                  <li>观众人数：{{ selectedMatch.attendance || '待定' }}</li>
                  <li>黄牌数：{{ selectedMatch.yellowCards || 0 }}</li>
                  <li>红牌数：{{ selectedMatch.redCards || 0 }}</li>
                  <li>角球数：{{ selectedMatch.corners || '待统计' }}</li>
                  <li>控球率：{{ selectedMatch.possession || '待统计' }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeDetailModal">关闭</button>
          <button class="btn primary" @click="editMatch(selectedMatch)">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 模拟比赛数据
const allMatches = ref([
  {
    id: 1,
    homeTeam: '曼城',
    awayTeam: '切尔西',
    league: 'premier',
    season: '2023-2024',
    matchDate: new Date(Date.now() + 86400000),
    venue: '伊蒂哈德球场',
    homeScore: 0,
    awayScore: 0,
    status: 'upcoming',
    homeTeamLogo: '/logos/man_city.png',
    awayTeamLogo: '/logos/chelsea.png',
    notes: '重要比赛，需重点监控',
    attendance: 53400,
    yellowCards: 3,
    redCards: 0,
    corners: 6,
    possession: '62%-38%',
    createdAt: new Date(Date.now() - 86400000),
    updatedAt: new Date(Date.now() - 43200000)
  },
  {
    id: 2,
    homeTeam: '巴塞罗那',
    awayTeam: '皇家马德里',
    league: 'la_liga',
    season: '2023-2024',
    matchDate: new Date(Date.now() + 172800000),
    venue: '诺坎普球场',
    homeScore: 2,
    awayScore: 1,
    status: 'finished',
    homeTeamLogo: '/logos/barcelona.png',
    awayTeamLogo: '/logos/real_madrid.png',
    notes: '经典国家德比',
    attendance: 99354,
    yellowCards: 5,
    redCards: 1,
    corners: 11,
    possession: '58%-42%',
    createdAt: new Date(Date.now() - 172800000),
    updatedAt: new Date(Date.now() - 86400000)
  },
  {
    id: 3,
    homeTeam: '拜仁慕尼黑',
    awayTeam: '多特蒙德',
    league: 'bundesliga',
    season: '2023-2024',
    matchDate: new Date(Date.now() + 259200000),
    venue: '安联竞技场',
    homeScore: 1,
    awayScore: 1,
    status: 'live',
    homeTeamLogo: '/logos/bayern.png',
    awayTeamLogo: '/logos/dortmund.png',
    notes: '正在进行中，实时更新比分',
    attendance: 75000,
    yellowCards: 2,
    redCards: 0,
    corners: 7,
    possession: '65%-35%',
    createdAt: new Date(Date.now() - 3600000),
    updatedAt: new Date(Date.now() - 1800000)
  },
  {
    id: 4,
    homeTeam: '尤文图斯',
    awayTeam: 'AC米兰',
    league: 'serie_a',
    season: '2023-2024',
    matchDate: new Date(Date.now() + 345600000),
    venue: '安联球场',
    homeScore: 0,
    awayScore: 0,
    status: 'upcoming',
    homeTeamLogo: '/logos/juventus.png',
    awayTeamLogo: '/logos/ac_milan.png',
    notes: '意甲焦点战',
    attendance: 41507,
    yellowCards: 4,
    redCards: 0,
    corners: 5,
    possession: '54%-46%',
    createdAt: new Date(Date.now() - 7200000),
    updatedAt: new Date(Date.now() - 3600000)
  },
  {
    id: 5,
    homeTeam: '巴黎圣日耳曼',
    awayTeam: '马赛',
    league: 'ligue_1',
    season: '2023-2024',
    matchDate: new Date(Date.now() - 86400000),
    venue: '王子公园球场',
    homeScore: 3,
    awayScore: 1,
    status: 'finished',
    homeTeamLogo: '/logos/psg.png',
    awayTeamLogo: '/logos/marseille.png',
    notes: '巴黎主场获胜',
    attendance: 47123,
    yellowCards: 2,
    redCards: 0,
    corners: 8,
    possession: '68%-32%',
    createdAt: new Date(Date.now() - 259200000),
    updatedAt: new Date(Date.now() - 172800000)
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  status: '',
  league: '',
  season: ''
})

// 统计数据
const stats = ref({
  totalMatches: 0,
  newToday: 0,
  upcomingCount: 0,
  liveCount: 0,
  finishedCount: 0,
  completedToday: 0,
  dataAccuracy: 0,
  dataUpdatedToday: 0
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 比赛模态框
const showMatchModal = ref(false)
const editingMatch = ref(null)
const currentMatch = ref({
  id: null,
  homeTeam: '',
  awayTeam: '',
  league: 'premier',
  season: '2023-2024',
  matchDate: new Date(Date.now() + 86400000),
  venue: '',
  homeScore: 0,
  awayScore: 0,
  status: 'upcoming',
  homeTeamLogo: '',
  awayTeamLogo: '',
  notes: '',
  attendance: null,
  yellowCards: 0,
  redCards: 0,
  corners: null,
  possession: null,
  createdAt: new Date(),
  updatedAt: new Date()
})

// 详情模态框
const showDetailModal = ref(false)
const selectedMatch = ref({})

// 计算属性
const filteredMatches = computed(() => {
  let matches = [...allMatches.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    matches = matches.filter(match => 
      match.homeTeam.toLowerCase().includes(keyword) ||
      match.awayTeam.toLowerCase().includes(keyword) ||
      match.venue.toLowerCase().includes(keyword) ||
      match.league.toLowerCase().includes(keyword) ||
      leagueNames[match.league]?.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.status) {
    matches = matches.filter(match => match.status === filters.value.status)
  }
  
  if (filters.value.league) {
    matches = matches.filter(match => match.league === filters.value.league)
  }
  
  if (filters.value.season) {
    matches = matches.filter(match => match.season === filters.value.season)
  }
  
  return matches
})

const paginatedMatches = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMatches.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredMatches.value.length / pageSize.value)
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
  upcoming: '未开始',
  live: '进行中',
  finished: '已完成',
  postponed: '推迟',
  cancelled: '取消'
}

const isValidMatch = computed(() => {
  return currentMatch.value.homeTeam.trim() !== '' && 
         currentMatch.value.awayTeam.trim() !== '' &&
         currentMatch.value.league !== '' &&
         currentMatch.value.matchDate !== null
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

const refreshMatches = () => {
  console.log('刷新比赛列表')
  currentPage.value = 1
}

const createNewMatch = () => {
  editingMatch.value = null
  currentMatch.value = {
    id: null,
    homeTeam: '',
    awayTeam: '',
    league: 'premier',
    season: '2023-2024',
    matchDate: new Date(Date.now() + 86400000),
    venue: '',
    homeScore: 0,
    awayScore: 0,
    status: 'upcoming',
    homeTeamLogo: '',
    awayTeamLogo: '',
    notes: '',
    attendance: null,
    yellowCards: 0,
    redCards: 0,
    corners: null,
    possession: null,
    createdAt: new Date(),
    updatedAt: new Date()
  }
  showMatchModal.value = true
}

const editMatch = (match) => {
  editingMatch.value = match
  currentMatch.value = { ...match }
  showMatchModal.value = true
}

const closeModal = () => {
  showMatchModal.value = false
  editingMatch.value = null
}

const saveMatch = () => {
  if (!isValidMatch.value) return
  
  if (editingMatch.value) {
    // 更新现有比赛
    const index = allMatches.value.findIndex(m => m.id === editingMatch.value.id)
    if (index !== -1) {
      allMatches.value[index] = { ...currentMatch.value, id: editingMatch.value.id }
    }
  } else {
    // 添加新比赛
    const newId = Math.max(...allMatches.value.map(m => m.id)) + 1
    allMatches.value.push({
      ...currentMatch.value,
      id: newId,
      createdAt: new Date(),
      updatedAt: new Date()
    })
  }
  
  closeModal()
}

const viewMatch = (match) => {
  selectedMatch.value = match
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedMatch.value = {}
}

const deleteMatch = (match) => {
  if (confirm(`确定要删除 "${match.homeTeam} VS ${match.awayTeam}" 的比赛吗？`)) {
    const index = allMatches.value.indexOf(match)
    if (index !== -1) {
      allMatches.value.splice(index, 1)
    }
  }
}

const updateMatchResult = (match) => {
  console.log(`更新比赛结果: ${match.homeTeam} VS ${match.awayTeam}`)
  // 在实际应用中，这里会打开一个更新比分的对话框
  alert(`更新比赛: ${match.homeTeam} ${match.homeScore} - ${match.awayScore} ${match.awayTeam}`)
}

const syncWithDataSource = () => {
  console.log('同步数据源...')
  // 在实际应用中，这里会调用API同步最新的比赛数据
  alert('正在从数据源同步比赛数据...')
}

const toggleSelectAll = () => {
  const isSelected = paginatedMatches.value.some(item => item.selected)
  paginatedMatches.value.forEach(item => item.selected = !isSelected)
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

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 初始化数据
onMounted(() => {
  console.log('Match Management 页面已加载')
  
  // 计算统计数据
  stats.value.totalMatches = allMatches.value.length
  stats.value.newToday = allMatches.value.filter(m => 
    new Date(m.createdAt).toDateString() === new Date().toDateString()
  ).length
  stats.value.upcomingCount = allMatches.value.filter(m => m.status === 'upcoming').length
  stats.value.liveCount = allMatches.value.filter(m => m.status === 'live').length
  stats.value.finishedCount = allMatches.value.filter(m => m.status === 'finished').length
  stats.value.completedToday = allMatches.value.filter(m => 
    m.status === 'finished' && new Date(m.updatedAt).toDateString() === new Date().toDateString()
  ).length
  stats.value.dataAccuracy = 98.5
  stats.value.dataUpdatedToday = allMatches.value.filter(m => 
    new Date(m.updatedAt).toDateString() === new Date().toDateString()
  ).length
})
</script>

<style scoped>
.match-management-container {
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

.action-btn.update {
  background: #a78bfa;
  color: white;
  padding: 6px 10px;
}

.action-btn.update:hover {
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

.stat-icon.upcoming {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.finished {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.accuracy {
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

.stat-change.neutral {
  color: #6b7280;
}

/* 比赛区样式 */
.matches-section {
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

.matches-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.matches-table-container {
  overflow-x: auto;
}

.matches-table {
  width: 100%;
  border-collapse: collapse;
}

.matches-table th,
.matches-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.matches-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.matches-table tbody tr:hover {
  background-color: #f9fafb;
}

.matches-table tbody tr.selected {
  background-color: #e0f2fe;
}

.match-info-cell {
  min-width: 200px;
}

.match-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.team {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.team-name {
  font-weight: 600;
  color: #1f2937;
}

.team-logo {
  width: 24px;
  height: 24px;
  object-fit: cover;
}

.match-vs {
  color: #6b7280;
  font-size: 12px;
  font-weight: bold;
}

.match-date {
  font-size: 12px;
  color: #6b7280;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.home-score, .away-score {
  font-weight: 700;
  font-size: 16px;
  min-width: 24px;
  text-align: center;
}

.score-separator {
  color: #6b7280;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.upcoming {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.live {
  background: #fecaca;
  color: #b91c1c;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.status-badge.finished {
  background: #dcfce7;
  color: #166534;
}

.status-badge.postponed {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #b91c1c;
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

.form-row {
  display: flex;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group.half-width {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1f2937;
}

.form-group input,
.form-group select,
.form-group textarea {
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
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-row.full-width {
  flex-direction: column;
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

.data-stats ul {
  padding-left: 20px;
  margin: 10px 0;
}

.data-stats li {
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
  .match-management-container {
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
  
  .matches-table {
    min-width: 800px;
  }
  
  .matches-table th,
  .matches-table td {
    padding: 8px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
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