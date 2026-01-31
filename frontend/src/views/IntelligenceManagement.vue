<template>
  <div class="intelligence-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">🧠 智能分析管理</h1>
      <p class="page-description">管理比赛情报、分析报告和智能策略</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索情报..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.type" @change="handleFilterChange">
          <option value="">全部类型</option>
          <option value="match">比赛情报</option>
          <option value="analysis">分析报告</option>
          <option value="strategy">策略建议</option>
          <option value="trend">趋势分析</option>
        </select>
        
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="reviewing">审核中</option>
          <option value="published">已发布</option>
          <option value="archived">已归档</option>
        </select>
        
        <select v-model="filters.priority" @change="handleFilterChange">
          <option value="">全部优先级</option>
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
          <option value="critical">紧急</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="createNewIntelligence">
          <span>➕</span> 新增情报
        </button>
        <button class="action-btn secondary" @click="refreshIntelligence">
          <span>🔄</span> 刷新
        </button>
        <button class="action-btn tertiary" @click="generateReport">
          <span>📊</span> 生成报告
        </button>
      </div>
    </div>

    <!-- 智能分析统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="icon-total">🧠</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">情报总数</div>
          <div class="stat-value">{{ stats.totalIntelligence }}</div>
          <div class="stat-change positive">+{{ stats.newToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon published">
          <i class="icon-published">✅</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">已发布</div>
          <div class="stat-value">{{ stats.publishedCount }}</div>
          <div class="stat-change positive">+{{ stats.publishedToday }} 今日发布</div>
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
        <div class="stat-icon high-priority">
          <i class="icon-high-priority">⚠️</i>
        </div>
        <div class="stat-content">
          <div class="stat-label">高优先级</div>
          <div class="stat-value">{{ stats.highPriorityCount }}</div>
          <div class="stat-change neutral">{{ stats.inReviewCount }} 审核中</div>
        </div>
      </div>
    </div>

    <!-- 情报列表 -->
    <div class="intelligence-section">
      <div class="section-header">
        <h2>📋 情报列表</h2>
        <div class="intelligence-stats">
          <span class="stat-item">显示: {{ filteredIntelligence.length }} 条</span>
          <span class="stat-item total">总计: {{ allIntelligence.length }} 条</span>
        </div>
      </div>
      
      <div class="intelligence-table-container">
        <table class="intelligence-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" /></th>
              <th>标题</th>
              <th>类型</th>
              <th>联赛</th>
              <th>优先级</th>
              <th>状态</th>
              <th>作者</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedIntelligence" :key="item.id" :class="{ selected: item.selected }">
              <td><input type="checkbox" v-model="item.selected" /></td>
              <td class="title-cell">
                <div class="title-wrapper">
                  <span class="title-text">{{ item.title }}</span>
                  <span class="summary-text" v-if="item.summary">{{ item.summary.substring(0, 50) }}...</span>
                </div>
              </td>
              <td>
                <span class="type-badge" :class="item.type">
                  {{ typeLabels[item.type] }}
                </span>
              </td>
              <td>{{ leagueNames[item.league] || item.league }}</td>
              <td>
                <span class="priority-badge" :class="item.priority">
                  {{ priorityLabels[item.priority] }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="item.status">
                  {{ statusLabels[item.status] }}
                </span>
              </td>
              <td>{{ item.author }}</td>
              <td>{{ formatDate(item.createdAt) }}</td>
              <td>
                <button class="action-btn view" @click="viewIntelligence(item)">👁️</button>
                <button class="action-btn edit" @click="editIntelligence(item)">✏️</button>
                <button class="action-btn publish" @click="publishIntelligence(item)" v-if="item.status === 'draft'">เผยแพร์</button>
                <button class="action-btn archive" @click="archiveIntelligence(item)" v-if="item.status !== 'archived'">📦</button>
                <button class="action-btn delete" @click="deleteIntelligence(item)">🗑️</button>
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

    <!-- 添加/编辑情报对话框 -->
    <div v-if="showIntelligenceModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingIntelligence ? '编辑情报' : '新增情报' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>标题 *</label>
            <input 
              v-model="currentIntelligence.title" 
              type="text" 
              placeholder="输入情报标题"
            />
          </div>
          
          <div class="form-group">
            <label>摘要</label>
            <textarea 
              v-model="currentIntelligence.summary" 
              placeholder="输入情报摘要"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>类型 *</label>
              <select v-model="currentIntelligence.type">
                <option value="match">比赛情报</option>
                <option value="analysis">分析报告</option>
                <option value="strategy">策略建议</option>
                <option value="trend">趋势分析</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>优先级 *</label>
              <select v-model="currentIntelligence.priority">
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
                <option value="critical">紧急</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group half-width">
              <label>联赛</label>
              <select v-model="currentIntelligence.league">
                <option value="premier">英超</option>
                <option value="la_liga">西甲</option>
                <option value="bundesliga">德甲</option>
                <option value="serie_a">意甲</option>
                <option value="ligue_1">法甲</option>
                <option value="other">其他</option>
              </select>
            </div>
            
            <div class="form-group half-width">
              <label>状态</label>
              <select v-model="currentIntelligence.status">
                <option value="draft">草稿</option>
                <option value="reviewing">审核中</option>
                <option value="published">已发布</option>
                <option value="archived">已归档</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>详细内容</label>
            <textarea 
              v-model="currentIntelligence.content" 
              placeholder="输入情报详细内容"
              rows="6"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>关联比赛</label>
            <input 
              v-model="currentIntelligence.relatedMatch" 
              type="text" 
              placeholder="关联的比赛ID或名称"
            />
          </div>
          
          <div class="form-group">
            <label>标签</label>
            <input 
              v-model="currentIntelligence.tags" 
              type="text" 
              placeholder="用逗号分隔的标签，例如：进球,助攻,战术"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveIntelligence"
            :disabled="!isValidIntelligence"
          >
            {{ editingIntelligence ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 情报详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>情报详情 - {{ selectedIntelligence.title }}</h3>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">标题</div>
            <div class="detail-value">{{ selectedIntelligence.title }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">摘要</div>
            <div class="detail-value">{{ selectedIntelligence.summary || '无摘要' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">类型</div>
            <div class="detail-value">
              <span class="type-badge" :class="selectedIntelligence.type">
                {{ typeLabels[selectedIntelligence.type] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">联赛</div>
            <div class="detail-value">{{ leagueNames[selectedIntelligence.league] || selectedIntelligence.league }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">优先级</div>
            <div class="detail-value">
              <span class="priority-badge" :class="selectedIntelligence.priority">
                {{ priorityLabels[selectedIntelligence.priority] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <span class="status-badge" :class="selectedIntelligence.status">
                {{ statusLabels[selectedIntelligence.status] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">作者</div>
            <div class="detail-value">{{ selectedIntelligence.author }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">创建时间</div>
            <div class="detail-value">{{ formatDate(selectedIntelligence.createdAt) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">更新时间</div>
            <div class="detail-value">{{ formatDate(selectedIntelligence.updatedAt) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">关联比赛</div>
            <div class="detail-value">{{ selectedIntelligence.relatedMatch || '无' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">标签</div>
            <div class="detail-value">
              <span class="tag" v-for="tag in getTags(selectedIntelligence.tags)" :key="tag">{{ tag }}</span>
            </div>
          </div>
          <div class="detail-row full-width">
            <div class="detail-label">详细内容</div>
            <div class="detail-value content-area">{{ selectedIntelligence.content }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeDetailModal">关闭</button>
          <button class="btn primary" @click="editIntelligence(selectedIntelligence)">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 模拟情报数据
const allIntelligence = ref([
  {
    id: 1,
    title: '曼城主力后卫伤情分析',
    summary: '分析曼城主力后卫拉波尔特的伤情对球队防守的影响',
    type: 'analysis',
    league: 'premier',
    priority: 'high',
    status: 'published',
    author: '分析师张三',
    content: '根据最新医疗报告，曼城主力后卫拉波尔特的膝盖伤情比预期严重，预计缺席接下来的3场比赛。这对曼城的防线组织将产生重大影响，特别是在面对快速反击能力强的对手时。建议重点关注曼城在接下来比赛中的防守策略调整。',
    relatedMatch: '曼城 VS 切尔西',
    tags: '后卫,伤情,防守',
    createdAt: new Date(Date.now() - 86400000),
    updatedAt: new Date(Date.now() - 43200000)
  },
  {
    id: 2,
    title: '皇马VS巴萨战术预测',
    summary: '基于两队近期表现预测国家德比的战术安排',
    type: 'strategy',
    league: 'la_liga',
    priority: 'critical',
    status: 'published',
    author: '战术分析师李四',
    content: '皇马近期在安切洛蒂的带领下逐渐找回了平衡，而巴萨在哈维的调教下进攻火力十足。预计本场比赛皇马会采取稳守反击的策略，利用维尼修斯的速度冲击巴萨防线。巴萨则会主打控球，通过中场的布斯克茨组织进攻。关键对决将是皇马的边路防守与巴萨的边路进攻。',
    relatedMatch: '皇家马德里 VS 巴塞罗那',
    tags: '战术,预测,国家德比',
    createdAt: new Date(Date.now() - 172800000),
    updatedAt: new Date(Date.now() - 86400000)
  },
  {
    id: 3,
    title: '德甲冬歇期转会市场观察',
    summary: '分析德甲各队冬歇期转会市场的动作和影响',
    type: 'trend',
    league: 'bundesliga',
    priority: 'medium',
    status: 'reviewing',
    author: '转会专家王五',
    content: '德甲冬歇期转会市场相对平静，但拜仁慕尼黑签下了年轻的日本中场，多特蒙德也补充了防守力量。预计这些引援将在下半赛季发挥重要作用，特别是对球队的战术多样性和板凳深度的提升。',
    relatedMatch: '',
    tags: '转会,冬歇期,德甲',
    createdAt: new Date(Date.now() - 3600000),
    updatedAt: new Date(Date.now() - 1800000)
  },
  {
    id: 4,
    title: '意甲争冠形势分析',
    summary: '分析意甲下半程各队争冠形势和关键因素',
    type: 'analysis',
    league: 'serie_a',
    priority: 'high',
    status: 'draft',
    author: '意甲观察员赵六',
    content: '随着冬歇期的结束，意甲争冠形势愈发激烈。国际米兰在卢卡库回归后攻击力大幅提升，AC米兰则在防守端表现出色。尤文图斯虽然在转会市场上有所动作，但磨合仍需时间。下半程的关键因素将是各队的伤病情况和欧战消耗。',
    relatedMatch: '',
    tags: '争冠,意甲,分析',
    createdAt: new Date(Date.now() - 7200000),
    updatedAt: new Date(Date.now() - 3600000)
  },
  {
    id: 5,
    title: '法甲青年才俊观察',
    summary: '法甲联赛涌现的年轻球员表现及前景分析',
    type: 'trend',
    league: 'ligue_1',
    priority: 'low',
    status: 'published',
    author: '球探分析师钱七',
    content: '法甲联赛一直以培养年轻才俊著称，本赛季涌现了多名值得关注的年轻球员。朗斯的中场新星展现了出色的传球视野，摩纳哥的前锋速度快、射术精湛。这些年轻球员的崛起不仅提升了法甲的竞争力，也为欧洲豪门提供了人才储备。',
    relatedMatch: '',
    tags: '青年才俊,法甲,球探',
    createdAt: new Date(Date.now() - 259200000),
    updatedAt: new Date(Date.now() - 172800000)
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  type: '',
  status: '',
  priority: ''
})

// 统计数据
const stats = ref({
  totalIntelligence: 0,
  newToday: 0,
  publishedCount: 0,
  publishedToday: 0,
  accuracyRate: 0,
  accuracyTrend: 0,
  highPriorityCount: 0,
  inReviewCount: 0
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 情报模态框
const showIntelligenceModal = ref(false)
const editingIntelligence = ref(null)
const currentIntelligence = ref({
  id: null,
  title: '',
  summary: '',
  type: 'match',
  league: 'premier',
  priority: 'medium',
  status: 'draft',
  author: '当前用户',
  content: '',
  relatedMatch: '',
  tags: ''
})

// 详情模态框
const showDetailModal = ref(false)
const selectedIntelligence = ref({})

// 计算属性
const filteredIntelligence = computed(() => {
  let intelligence = [...allIntelligence.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    intelligence = intelligence.filter(item => 
      item.title.toLowerCase().includes(keyword) ||
      item.summary.toLowerCase().includes(keyword) ||
      item.content.toLowerCase().includes(keyword) ||
      item.tags.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.type) {
    intelligence = intelligence.filter(item => item.type === filters.value.type)
  }
  
  if (filters.value.status) {
    intelligence = intelligence.filter(item => item.status === filters.value.status)
  }
  
  if (filters.value.priority) {
    intelligence = intelligence.filter(item => item.priority === filters.value.priority)
  }
  
  return intelligence
})

const paginatedIntelligence = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredIntelligence.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredIntelligence.value.length / pageSize.value)
})

const typeLabels = {
  match: '比赛情报',
  analysis: '分析报告',
  strategy: '策略建议',
  trend: '趋势分析'
}

const priorityLabels = {
  low: '低',
  medium: '中',
  high: '高',
  critical: '紧急'
}

const statusLabels = {
  draft: '草稿',
  reviewing: '审核中',
  published: '已发布',
  archived: '已归档'
}

const leagueNames = {
  premier: '英超',
  la_liga: '西甲',
  bundesliga: '德甲',
  serie_a: '意甲',
  ligue_1: '法甲',
  other: '其他'
}

const isValidIntelligence = computed(() => {
  return currentIntelligence.value.title.trim() !== '' && 
         currentIntelligence.value.type !== '' &&
         currentIntelligence.value.priority !== ''
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

const refreshIntelligence = () => {
  console.log('刷新情报列表')
  currentPage.value = 1
}

const createNewIntelligence = () => {
  editingIntelligence.value = null
  currentIntelligence.value = {
    id: null,
    title: '',
    summary: '',
    type: 'match',
    league: 'premier',
    priority: 'medium',
    status: 'draft',
    author: '当前用户',
    content: '',
    relatedMatch: '',
    tags: ''
  }
  showIntelligenceModal.value = true
}

const editIntelligence = (item) => {
  editingIntelligence.value = item
  currentIntelligence.value = { ...item }
  showIntelligenceModal.value = true
}

const closeModal = () => {
  showIntelligenceModal.value = false
  editingIntelligence.value = null
}

const saveIntelligence = () => {
  if (!isValidIntelligence.value) return
  
  if (editingIntelligence.value) {
    // 更新现有情报
    const index = allIntelligence.value.findIndex(i => i.id === editingIntelligence.value.id)
    if (index !== -1) {
      allIntelligence.value[index] = { ...currentIntelligence.value, id: editingIntelligence.value.id }
    }
  } else {
    // 添加新情报
    const newId = Math.max(...allIntelligence.value.map(i => i.id)) + 1
    allIntelligence.value.push({
      ...currentIntelligence.value,
      id: newId,
      createdAt: new Date(),
      updatedAt: new Date()
    })
  }
  
  closeModal()
}

const viewIntelligence = (item) => {
  selectedIntelligence.value = item
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedIntelligence.value = {}
}

const deleteIntelligence = (item) => {
  if (confirm(`确定要删除 "${item.title}" 吗？`)) {
    const index = allIntelligence.value.indexOf(item)
    if (index !== -1) {
      allIntelligence.value.splice(index, 1)
    }
  }
}

const publishIntelligence = (item) => {
  item.status = 'published'
  item.updatedAt = new Date()
}

const archiveIntelligence = (item) => {
  item.status = 'archived'
  item.updatedAt = new Date()
}

const toggleSelectAll = () => {
  const isSelected = paginatedIntelligence.value.some(item => item.selected)
  paginatedIntelligence.value.forEach(item => item.selected = !isSelected)
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

const getTags = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').map(tag => tag.trim())
}

const generateReport = () => {
  console.log('生成分析报告')
  // 在实际应用中，这里会生成一个综合分析报告
  alert('正在生成智能分析报告...')
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 初始化数据
onMounted(() => {
  console.log('Intelligence Management 页面已加载')
  
  // 计算统计数据
  stats.value.totalIntelligence = allIntelligence.value.length
  stats.value.newToday = allIntelligence.value.filter(i => 
    new Date(i.createdAt).toDateString() === new Date().toDateString()
  ).length
  stats.value.publishedCount = allIntelligence.value.filter(i => i.status === 'published').length
  stats.value.publishedToday = allIntelligence.value.filter(i => 
    i.status === 'published' && new Date(i.updatedAt).toDateString() === new Date().toDateString()
  ).length
  stats.value.accuracyRate = 82.5
  stats.value.accuracyTrend = 1.2
  stats.value.highPriorityCount = allIntelligence.value.filter(i => i.priority === 'high' || i.priority === 'critical').length
  stats.value.inReviewCount = allIntelligence.value.filter(i => i.status === 'reviewing').length
})
</script>

<style scoped>
.intelligence-management-container {
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

.action-btn.publish {
  background: #10b981;
  color: white;
  padding: 6px 10px;
}

.action-btn.publish:hover {
  background: #059669;
}

.action-btn.archive {
  background: #94a3b8;
  color: white;
  padding: 6px 10px;
}

.action-btn.archive:hover {
  background: #64748b;
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

.stat-icon.published {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.accuracy {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.high-priority {
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

/* 情报区域样式 */
.intelligence-section {
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

.intelligence-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.intelligence-table-container {
  overflow-x: auto;
}

.intelligence-table {
  width: 100%;
  border-collapse: collapse;
}

.intelligence-table th,
.intelligence-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.intelligence-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.intelligence-table tbody tr:hover {
  background-color: #f9fafb;
}

.intelligence-table tbody tr.selected {
  background-color: #e0f2fe;
}

.title-cell {
  min-width: 200px;
}

.title-wrapper {
  display: flex;
  flex-direction: column;
}

.title-text {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.summary-text {
  font-size: 13px;
  color: #6b7280;
}

.type-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.match {
  background: #dbeafe;
  color: #1d4ed8;
}

.type-badge.analysis {
  background: #f0f9ff;
  color: #0369a1;
}

.type-badge.strategy {
  background: #ecfdf5;
  color: #047857;
}

.type-badge.trend {
  background: #fffbeb;
  color: #92400e;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.priority-badge.low {
  background: #e5e7eb;
  color: #374151;
}

.priority-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.priority-badge.high {
  background: #fecaca;
  color: #b91c1c;
}

.priority-badge.critical {
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.draft {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.reviewing {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-badge.published {
  background: #dcfce7;
  color: #166534;
}

.status-badge.archived {
  background: #ddd6fe;
  color: #6d28d9;
}

.tag {
  display: inline-block;
  background: #e0e7ff;
  color: #4f46e5;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-right: 6px;
  margin-bottom: 6px;
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

.form-row {
  display: flex;
  gap: 20px;
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

.content-area {
  white-space: pre-wrap;
  line-height: 1.6;
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
  .intelligence-management-container {
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
  
  .intelligence-table {
    min-width: 800px;
  }
  
  .intelligence-table th,
  .intelligence-table td {
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