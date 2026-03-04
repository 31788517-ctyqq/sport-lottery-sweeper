<template>
  <div class="sp-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 SP数据管理</h1>
      <p class="page-description">管理体育赛事的SP数据，包括赔率、指数和概率分析</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索SP数据..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.type" @change="handleFilterChange">
          <option value="">全部类型</option>
          <option value="win">胜</option>
          <option value="draw">平</option>
          <option value="lose">负</option>
          <option value="handicap">让球</option>
        </select>
        
        <select v-model="filters.sport" @change="handleFilterChange">
          <option value="">全部运动</option>
          <option value="football">足球</option>
          <option value="basketball">篮球</option>
          <option value="tennis">网球</option>
        </select>
        
        <select v-model="filters.provider" @change="handleFilterChange">
          <option value="">全部供应商</option>
          <option value="bet365">Bet365</option>
          <option value="williamhill">William Hill</option>
          <option value="ladbrokes">Ladbrokes</option>
          <option value="pinnacle">Pinnacle</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="createNewSPData">
          <span>➕</span> 新增SP数据
        </button>
        <button class="action-btn secondary" @click="refreshSPData">
          <span>🔄</span> 刷新
        </button>
        <button class="action-btn tertiary" @click="exportSPData">
          <span>📤</span> 导出数据
        </button>
      </div>
    </div>

    <!-- SP数据统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="icon-total">🔢</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">总SP数据</div>
          <div class="stat-value">{{ stats.totalSPData }}</div>
          <div class="stat-change positive">+{{ stats.newToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon active">
          <i class="icon-active">⚡</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">活跃SP</div>
          <div class="stat-value">{{ stats.activeSP }}</div>
          <div class="stat-change neutral">{{ stats.expiredSP }} 已过期</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon accuracy">
          <i class="icon-accuracy">🎯</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">准确率</div>
          <div class="stat-value">{{ stats.accuracyRate }}%</div>
          <div class="stat-change positive">+{{ stats.improvement }}% 提升</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon provider">
          <i class="icon-provider">🏢</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">供应商数</div>
          <div class="stat-value">{{ stats.providersCount }}</div>
          <div class="stat-change neutral">{{ stats.topProvider }} 主导</div>
        </div>
      </div>
    </div>

    <!-- SP数据列表 -->
    <div class="sp-data-section">
      <div class="section-header">
        <h2>📋 SP数据列表</h2>
        <div class="sp-data-stats">
          <span class="stat-item">显示: {{ filteredSPData.length }} 条</span>
          <span class="stat-item total">总计: {{ allSPData.length }} 条</span>
        </div>
      </div>
      
      <div class="sp-data-table-container">
        <table class="sp-data-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" /></th>
              <th>赛事</th>
              <th>类型</th>
              <th>SP值</th>
              <th>变化趋势</th>
              <th>供应商</th>
              <th>更新时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sp in paginatedSPData" :key="sp.id" :class="{ selected: sp.selected }">
              <td><input type="checkbox" v-model="sp.selected" /></td>
              <td class="match-info-cell">
                <div class="match-info">
                  <div class="team home-team">
                    <span class="team-name">{{ sp.homeTeam }}</span>
                  </div>
                  <div class="match-vs">VS</div>
                  <div class="team away-team">
                    <span class="team-name">{{ sp.awayTeam }}</span>
                  </div>
                </div>
                <div class="match-date">{{ formatDate(sp.matchDate) }}</div>
              </td>
              <td>
                <span class="type-badge" :class="sp.type">
                  {{ typeLabels[sp.type] }}
                </span>
              </td>
              <td>
                <div class="sp-value-display">
                  <span class="sp-value">{{ sp.spValue }}</span>
                  <span class="sp-change" :class="sp.changeDirection">
                    {{ sp.changeDirection === 'up' ? '↑' : sp.changeDirection === 'down' ? '↓' : '-' }} {{ sp.changeValue }}
                  </span>
                </div>
              </td>
              <td>
                <div class="trend-graph">
                  <div class="trend-line" :style="{ width: sp.trendWidth + '%' }"></div>
                  <div class="trend-indicator" :class="sp.trendDirection">
                    {{ sp.trendDirection === 'up' ? '↗' : sp.trendDirection === 'down' ? '↘' : '→' }}
                  </div>
                </div>
              </td>
              <td>{{ sp.providerName }}</td>
              <td>{{ formatDateTime(sp.updatedAt) }}</td>
              <td>
                <span class="status-badge" :class="sp.status">
                  {{ statusLabels[sp.status] }}
                </span>
              </td>
              <td>
                <button class="action-btn view" @click="viewSPData(sp)">👁️</button>
                <button class="action-btn edit" @click="editSPData(sp)">✏️</button>
                <button class="action-btn update" @click="updateSPData(sp)">🔄</button>
                <button class="action-btn delete" @click="deleteSPData(sp)">🗑️</button>
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

    <!-- 添加/编辑SP数据对话框 -->
    <div v-if="showSPModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingSPData ? '编辑SP数据' : '新增SP数据' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group half-width">
              <label>主队 *</label>
              <input 
                v-model="currentSPData.homeTeam" 
                type="text" 
                placeholder="输入主队名称"
              />
            </div>
            
            <div class="form-group half-width">
              <label>客队 *</label>
              <input 
                v-model="currentSPData.awayTeam" 
                type="text" 
                placeholder="输入客队名称"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>比赛日期</label>
              <input 
                v-model="currentSPData.matchDate" 
                type="datetime-local"
              />
            </div>
            
            <div class="form-group half-width">
              <label>SP类型 *</label>
              <select v-model="currentSPData.type">
                <option value="win">胜</option>
                <option value="draw">平</option>
                <option value="lose">负</option>
                <option value="handicap">让球</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>SP值 *</label>
              <input 
                v-model.number="currentSPData.spValue" 
                type="number" 
                step="0.01"
                min="0"
                placeholder="输入SP值"
              />
            </div>
            
            <div class="form-group half-width">
              <label>供应商 *</label>
              <select v-model="currentSPData.provider">
                <option value="bet365">Bet365</option>
                <option value="williamhill">William Hill</option>
                <option value="ladbrokes">Ladbrokes</option>
                <option value="pinnacle">Pinnacle</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>变化值</label>
              <input 
                v-model.number="currentSPData.changeValue" 
                type="number" 
                step="0.01"
                placeholder="变化数值"
              />
            </div>
            
            <div class="form-group half-width">
              <label>变化方向</label>
              <select v-model="currentSPData.changeDirection">
                <option value="up">上升</option>
                <option value="down">下降</option>
                <option value="same">不变</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>状态 *</label>
              <select v-model="currentSPData.status">
                <option value="active">活跃</option>
                <option value="expired">过期</option>
                <option value="suspended">暂停</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>趋势方向</label>
              <select v-model="currentSPData.trendDirection">
                <option value="up">上升</option>
                <option value="down">下降</option>
                <option value="stable">稳定</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>备注</label>
            <textarea 
              v-model="currentSPData.notes" 
              placeholder="SP数据备注信息"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveSPData"
            :disabled="!isValidSPData"
          >
            {{ editingSPData ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- SP数据详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>SP数据详情 - {{ selectedSPData.homeTeam }} VS {{ selectedSPData.awayTeam }}</h3>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">主队</div>
            <div class="detail-value">{{ selectedSPData.homeTeam }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">客队</div>
            <div class="detail-value">{{ selectedSPData.awayTeam }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">SP类型</div>
            <div class="detail-value">
              <span class="type-badge" :class="selectedSPData.type">
                {{ typeLabels[selectedSPData.type] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">SP值</div>
            <div class="detail-value">{{ selectedSPData.spValue }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">变化值</div>
            <div class="detail-value">{{ selectedSPData.changeValue }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">变化方向</div>
            <div class="detail-value">{{ selectedSPData.changeDirection === 'up' ? '上升' : selectedSPData.changeDirection === 'down' ? '下降' : '不变' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">供应商</div>
            <div class="detail-value">{{ selectedSPData.providerName }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">趋势方向</div>
            <div class="detail-value">{{ selectedSPData.trendDirection === 'up' ? '上升' : selectedSPData.trendDirection === 'down' ? '下降' : '稳定' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <span class="status-badge" :class="selectedSPData.status">
                {{ statusLabels[selectedSPData.status] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">更新时间</div>
            <div class="detail-value">{{ formatDateTime(selectedSPData.updatedAt) }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">备注</div>
            <div class="detail-value">{{ selectedSPData.notes || '无备注' }}</div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">分析指标</div>
            <div class="detail-value">
              <div class="analysis-stats">
                <p>SP数据分析指标：</p>
                <ul>
                  <li>历史波动范围：{{ selectedSPData.volatilityRange || 'N/A' }}</li>
                  <li>平均变化幅度：{{ selectedSPData.avgChange || 'N/A' }}</li>
                  <li>市场共识度：{{ selectedSPData.marketAgreement || 'N/A' }}%</li>
                  <li>异常检测：{{ selectedSPData.anomalyDetection || 'N/A' }}</li>
                  <li>趋势持续性：{{ selectedSPData.trendConsistency || 'N/A' }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeDetailModal">关闭</button>
          <button class="btn primary" @click="editSPData(selectedSPData)">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 模拟SP数据
const allSPData = ref([
  {
    id: 1,
    homeTeam: '曼城',
    awayTeam: '切尔西',
    type: 'win',
    spValue: 1.85,
    changeValue: 0.05,
    changeDirection: 'up',
    provider: 'bet365',
    providerName: 'Bet365',
    trendDirection: 'up',
    trendWidth: 75,
    status: 'active',
    matchDate: new Date(Date.now() + 86400000),
    updatedAt: new Date(Date.now() - 3600000),
    volatilityRange: '1.75-1.95',
    avgChange: 0.03,
    marketAgreement: 87,
    anomalyDetection: '正常',
    trendConsistency: '高',
    notes: '近期走势强劲，赔率下调'
  },
  {
    id: 2,
    homeTeam: '巴塞罗那',
    awayTeam: '皇家马德里',
    type: 'draw',
    spValue: 3.40,
    changeValue: 0.10,
    changeDirection: 'down',
    provider: 'pinnacle',
    providerName: 'Pinnacle',
    trendDirection: 'down',
    trendWidth: 30,
    status: 'active',
    matchDate: new Date(Date.now() + 172800000),
    updatedAt: new Date(Date.now() - 7200000),
    volatilityRange: '3.20-3.60',
    avgChange: 0.05,
    marketAgreement: 75,
    anomalyDetection: '正常',
    trendConsistency: '中',
    notes: '平局赔率有所下调'
  },
  {
    id: 3,
    homeTeam: '拜仁慕尼黑',
    awayTeam: '多特蒙德',
    type: 'lose',
    spValue: 4.20,
    changeValue: 0.00,
    changeDirection: 'same',
    provider: 'williamhill',
    providerName: 'William Hill',
    trendDirection: 'stable',
    trendWidth: 50,
    status: 'expired',
    matchDate: new Date(Date.now() - 86400000),
    updatedAt: new Date(Date.now() - 172800000),
    volatilityRange: '4.00-4.40',
    avgChange: 0.02,
    marketAgreement: 92,
    anomalyDetection: '正常',
    trendConsistency: '高',
    notes: '比赛已结束，数据过期'
  },
  {
    id: 4,
    homeTeam: '尤文图斯',
    awayTeam: 'AC米兰',
    type: 'handicap',
    spValue: 1.95,
    changeValue: 0.03,
    changeDirection: 'up',
    provider: 'ladbrokes',
    providerName: 'Ladbrokes',
    trendDirection: 'up',
    trendWidth: 65,
    status: 'active',
    matchDate: new Date(Date.now() + 259200000),
    updatedAt: new Date(Date.now() - 1800000),
    volatilityRange: '1.85-2.05',
    avgChange: 0.04,
    marketAgreement: 82,
    anomalyDetection: '正常',
    trendConsistency: '中',
    notes: '让球盘口，关注度较高'
  },
  {
    id: 5,
    homeTeam: '巴黎圣日耳曼',
    awayTeam: '马赛',
    type: 'win',
    spValue: 1.45,
    changeValue: 0.02,
    changeDirection: 'down',
    provider: 'bet365',
    providerName: 'Bet365',
    trendDirection: 'down',
    trendWidth: 40,
    status: 'active',
    matchDate: new Date(Date.now() + 345600000),
    updatedAt: new Date(Date.now() - 5400000),
    volatilityRange: '1.40-1.50',
    avgChange: 0.01,
    marketAgreement: 95,
    anomalyDetection: '正常',
    trendConsistency: '高',
    notes: '主队实力占优，赔率稳定'
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  type: '',
  sport: '',
  provider: ''
})

// 统计数据
const stats = ref({
  totalSPData: 0,
  newToday: 0,
  activeSP: 0,
  expiredSP: 0,
  accuracyRate: 0,
  improvement: 0,
  providersCount: 0,
  topProvider: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// SP数据模态框
const showSPModal = ref(false)
const editingSPData = ref(null)
const currentSPData = ref({
  id: null,
  homeTeam: '',
  awayTeam: '',
  type: 'win',
  spValue: 0,
  changeValue: 0,
  changeDirection: 'same',
  provider: 'bet365',
  providerName: 'Bet365',
  trendDirection: 'stable',
  trendWidth: 50,
  status: 'active',
  matchDate: new Date(Date.now() + 86400000),
  updatedAt: new Date(),
  volatilityRange: '',
  avgChange: 0,
  marketAgreement: 0,
  anomalyDetection: '',
  trendConsistency: '',
  notes: ''
})

// 详情模态框
const showDetailModal = ref(false)
const selectedSPData = ref({})

// 计算属性
const filteredSPData = computed(() => {
  let data = [...allSPData.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(sp => 
      sp.homeTeam.toLowerCase().includes(keyword) ||
      sp.awayTeam.toLowerCase().includes(keyword) ||
      sp.provider.toLowerCase().includes(keyword) ||
      sp.type.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.type) {
    data = data.filter(sp => sp.type === filters.value.type)
  }
  
  if (filters.value.sport) {
    // 模拟运动类型筛选，实际上SP数据没有存储sport字段
    // 在实际应用中，这里会有sport字段
  }
  
  if (filters.value.provider) {
    data = data.filter(sp => sp.provider === filters.value.provider)
  }
  
  return data
})

const paginatedSPData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSPData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredSPData.value.length / pageSize.value)
})

const typeLabels = {
  win: '胜',
  draw: '平',
  lose: '负',
  handicap: '让球'
}

const statusLabels = {
  active: '活跃',
  expired: '过期',
  suspended: '暂停'
}

const isValidSPData = computed(() => {
  return currentSPData.value.homeTeam.trim() !== '' && 
         currentSPData.value.awayTeam.trim() !== '' &&
         currentSPData.value.type !== '' &&
         currentSPData.value.spValue > 0 &&
         currentSPData.value.provider !== ''
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

const refreshSPData = () => {
  console.log('刷新SP数据')
  currentPage.value = 1
}

const createNewSPData = () => {
  editingSPData.value = null
  currentSPData.value = {
    id: null,
    homeTeam: '',
    awayTeam: '',
    type: 'win',
    spValue: 0,
    changeValue: 0,
    changeDirection: 'same',
    provider: 'bet365',
    providerName: 'Bet365',
    trendDirection: 'stable',
    trendWidth: 50,
    status: 'active',
    matchDate: new Date(Date.now() + 86400000),
    updatedAt: new Date(),
    volatilityRange: '',
    avgChange: 0,
    marketAgreement: 0,
    anomalyDetection: '',
    trendConsistency: '',
    notes: ''
  }
  showSPModal.value = true
}

const editSPData = (sp) => {
  editingSPData.value = sp
  currentSPData.value = { ...sp }
  showSPModal.value = true
}

const closeModal = () => {
  showSPModal.value = false
  editingSPData.value = null
}

const saveSPData = () => {
  if (!isValidSPData.value) return
  
  if (editingSPData.value) {
    // 更新现有SP数据
    const index = allSPData.value.findIndex(s => s.id === editingSPData.value.id)
    if (index !== -1) {
      allSPData.value[index] = { ...currentSPData.value, id: editingSPData.value.id }
    }
  } else {
    // 添加新SP数据
    const newId = Math.max(...allSPData.value.map(s => s.id)) + 1
    allSPData.value.push({
      ...currentSPData.value,
      id: newId,
      updatedAt: new Date()
    })
  }
  
  closeModal()
}

const viewSPData = (sp) => {
  selectedSPData.value = sp
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedSPData.value = {}
}

const deleteSPData = (sp) => {
  if (confirm(`确定要删除 "${sp.homeTeam} VS ${sp.awayTeam}" 的SP数据吗？`)) {
    const index = allSPData.value.indexOf(sp)
    if (index !== -1) {
      allSPData.value.splice(index, 1)
    }
  }
}

const updateSPData = (sp) => {
  console.log(`更新SP数据: ${sp.homeTeam} VS ${sp.awayTeam}`)
  // 在实际应用中，这里会打开一个更新SP值的对话框
  alert(`更新SP数据: ${sp.homeTeam} VS ${sp.awayTeam}，当前值: ${sp.spValue}`)
}

const exportSPData = () => {
  console.log('导出SP数据...')
  // 在实际应用中，这里会导出数据到文件
  alert('正在导出SP数据...')
}

const toggleSelectAll = () => {
  const isSelected = paginatedSPData.value.some(item => item.selected)
  paginatedSPData.value.forEach(item => item.selected = !isSelected)
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
  console.log('SP Management 页面已加载')
  
  // 计算统计数据
  stats.value.totalSPData = allSPData.value.length
  stats.value.newToday = allSPData.value.filter(sp => 
    new Date(sp.updatedAt).toDateString() === new Date().toDateString()
  ).length
  stats.value.activeSP = allSPData.value.filter(sp => sp.status === 'active').length
  stats.value.expiredSP = allSPData.value.filter(sp => sp.status === 'expired').length
  stats.value.accuracyRate = 94.5
  stats.value.improvement = 2.3
  stats.value.providersCount = [...new Set(allSPData.value.map(sp => sp.provider))].length
  stats.value.topProvider = 'Bet365'
})
</script>

<style scoped>
.sp-management-container {
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

.stat-icon.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.accuracy {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.provider {
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

/* SP数据区样式 */
.sp-data-section {
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

.sp-data-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.sp-data-table-container {
  overflow-x: auto;
}

.sp-data-table {
  width: 100%;
  border-collapse: collapse;
}

.sp-data-table th,
.sp-data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.sp-data-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.sp-data-table tbody tr:hover {
  background-color: #f9fafb;
}

.sp-data-table tbody tr.selected {
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

.match-vs {
  color: #6b7280;
  font-size: 12px;
  font-weight: bold;
}

.match-date {
  font-size: 12px;
  color: #6b7280;
}

.sp-value-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sp-value {
  font-weight: 700;
  font-size: 16px;
  min-width: 40px;
}

.sp-change {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.sp-change.up {
  color: #059669;
  background: #dcfce7;
}

.sp-change.down {
  color: #b91c1c;
  background: #fee2e2;
}

.type-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.win {
  background: #dbeafe;
  color: #1d4ed8;
}

.type-badge.draw {
  background: #d1fae5;
  color: #065f46;
}

.type-badge.lose {
  background: #fef3c7;
  color: #92400e;
}

.type-badge.handicap {
  background: #ddd6fe;
  color: #5b21b6;
}

.trend-graph {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-line {
  height: 6px;
  background: #3b82f6;
  border-radius: 3px;
  min-width: 50px;
}

.trend-indicator {
  font-size: 16px;
}

.trend-indicator.up {
  color: #059669;
}

.trend-indicator.down {
  color: #b91c1c;
}

.trend-indicator.stable {
  color: #6b7280;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.expired {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.suspended {
  background: #fef3c7;
  color: #92400e;
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

.analysis-stats ul {
  padding-left: 20px;
  margin: 10px 0;
}

.analysis-stats li {
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
  .sp-management-container {
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
  
  .sp-data-table {
    min-width: 800px;
  }
  
  .sp-data-table th,
  .sp-data-table td {
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