<template>
  <div class="data-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 数据管理</h1>
      <p class="page-description">管理比赛数据、联赛信息和球队资料</p>
    </div>

    <!-- 标签页 -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.value"
        :class="['tab-btn', { 'active': activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <!-- 比赛数据管理 -->
    <div v-show="activeTab === 'matches'" class="tab-content">
      <div class="toolbar">
        <div class="search-box">
          <input 
            v-model="matchFilters.search"
            type="text"
            placeholder="搜索比赛..."
            @keyup.enter="loadMatches"
          />
          <button class="search-btn" @click="loadMatches">
            <span>🔍</span> 搜索
          </button>
        </div>
        
        <div class="filters">
          <select v-model="matchFilters.league" @change="loadMatches">
            <option value="">全部联赛</option>
            <option v-for="league in leagues" :key="league" :value="league">
              {{ league }}
            </option>
          </select>
          
          <select v-model="matchFilters.status" @change="loadMatches">
            <option value="">全部状态</option>
            <option value="upcoming">即将开始</option>
            <option value="in_progress">进行中</option>
            <option value="finished">已结束</option>
            <option value="postponed">推迟</option>
          </select>
        </div>

        <button class="create-btn" @click="handleCreateMatch">
          <span>➕</span> 添加比赛
        </button>
      </div>

      <!-- 比赛列表 -->
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>比赛时间</th>
              <th>联赛</th>
              <th>主队</th>
              <th>客队</th>
              <th>比分</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="match in matches" :key="match.id">
              <td>{{ formatDate(match.match_time) }}</td>
              <td>{{ match.league_name }}</td>
              <td>{{ match.home_team }}</td>
              <td>{{ match.away_team }}</td>
              <td>
                <span v-if="match.status === 'finished'">
                  {{ match.home_score }} : {{ match.away_score }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span :class="['badge', 'status-' + match.status]">
                  {{ getStatusText(match.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="btn-edit" @click="handleEditMatch(match)">编辑</button>
                <button class="btn-delete" @click="handleDeleteMatch(match.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="matches.length === 0" class="empty-state">
          <p>暂无比赛数据</p>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button :disabled="matchPagination.page <= 1" @click="handleMatchPageChange(matchPagination.page - 1)">
          上一页
        </button>
        <span>第 {{ matchPagination.page }} / {{ matchPagination.pages }} 页</span>
        <button :disabled="matchPagination.page >= matchPagination.pages" @click="handleMatchPageChange(matchPagination.page + 1)">
          下一页
        </button>
      </div>
    </div>

    <!-- 联赛管理 -->
    <div v-show="activeTab === 'leagues'" class="tab-content">
      <div class="toolbar">
        <button class="create-btn" @click="handleCreateLeague">
          <span>➕</span> 添加联赛
        </button>
      </div>

      <div class="grid-cards">
        <div v-for="league in leaguesList" :key="league.id" class="league-card">
          <div class="league-icon">🏆</div>
          <h3>{{ league.name }}</h3>
          <p class="league-country">{{ league.country }}</p>
          <div class="league-stats">
            <span>⚽ {{ league.teams_count || 0 }} 支球队</span>
            <span>📅 {{ league.matches_count || 0 }} 场比赛</span>
          </div>
          <div class="card-actions">
            <button class="btn-edit" @click="handleEditLeague(league)">编辑</button>
            <button class="btn-delete" @click="handleDeleteLeague(league.id)">删除</button>
          </div>
        </div>
      </div>

      <div v-if="leaguesList.length === 0" class="empty-state">
        <p>暂无联赛数据</p>
      </div>
    </div>

    <!-- 球队管理 -->
    <div v-show="activeTab === 'teams'" class="tab-content">
      <div class="toolbar">
        <div class="search-box">
          <input 
            v-model="teamFilters.search"
            type="text"
            placeholder="搜索球队..."
            @keyup.enter="loadTeams"
          />
          <button class="search-btn" @click="loadTeams">
            <span>🔍</span> 搜索
          </button>
        </div>

        <button class="create-btn" @click="handleCreateTeam">
          <span>➕</span> 添加球队
        </button>
      </div>

      <div class="grid-cards">
        <div v-for="team in teams" :key="team.id" class="team-card">
          <div class="team-logo">
            <span>{{ team.name.charAt(0) }}</span>
          </div>
          <h3>{{ team.name }}</h3>
          <p class="team-league">{{ team.league_name }}</p>
          <div class="team-stats">
            <div class="stat-item">
              <span class="stat-label">胜</span>
              <span class="stat-value">{{ team.wins || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平</span>
              <span class="stat-value">{{ team.draws || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">负</span>
              <span class="stat-value">{{ team.losses || 0 }}</span>
            </div>
          </div>
          <div class="card-actions">
            <button class="btn-edit" @click="handleEditTeam(team)">编辑</button>
            <button class="btn-delete" @click="handleDeleteTeam(team.id)">删除</button>
          </div>
        </div>
      </div>

      <div v-if="teams.length === 0" class="empty-state">
        <p>暂无球队数据</p>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <div v-if="showEditDialog" class="dialog-overlay" @click="closeEditDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>{{ dialogTitle }}</h3>
          <button class="close-btn" @click="closeEditDialog">×</button>
        </div>
        <div class="dialog-body">
          <p class="coming-soon">功能开发中，敬请期待...</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeEditDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'

export default {
  name: 'DataManagement',
  setup() {
    const activeTab = ref('matches')
    const showEditDialog = ref(false)
    const dialogTitle = ref('')
    
    const tabs = [
      { value: 'matches', label: '比赛数据', icon: '⚽' },
      { value: 'leagues', label: '联赛管理', icon: '🏆' },
      { value: 'teams', label: '球队管理', icon: '👥' }
    ]

    // 比赛相关
    const matches = ref([])
    const matchFilters = reactive({
      search: '',
      league: '',
      status: ''
    })
    const matchPagination = reactive({
      page: 1,
      size: 20,
      total: 0,
      pages: 0
    })

    // 联赛相关
    const leaguesList = ref([])
    const leagues = ref(['英超', '西甲', '意甲', '德甲', '法甲'])

    // 球队相关
    const teams = ref([])
    const teamFilters = reactive({
      search: ''
    })

    // 加载模拟数据
    const loadMatches = () => {
      // 模拟数据
      matches.value = [
        {
          id: 1,
          match_time: new Date().toISOString(),
          league_name: '英超',
          home_team: '曼联',
          away_team: '利物浦',
          home_score: 2,
          away_score: 1,
          status: 'finished'
        },
        {
          id: 2,
          match_time: new Date(Date.now() + 86400000).toISOString(),
          league_name: '西甲',
          home_team: '皇马',
          away_team: '巴萨',
          status: 'upcoming'
        }
      ]
      matchPagination.total = matches.value.length
      matchPagination.pages = Math.ceil(matches.value.length / matchPagination.size)
    }

    const loadTeams = () => {
      teams.value = [
        { id: 1, name: '曼联', league_name: '英超', wins: 15, draws: 5, losses: 3 },
        { id: 2, name: '利物浦', league_name: '英超', wins: 18, draws: 4, losses: 1 },
        { id: 3, name: '皇马', league_name: '西甲', wins: 20, draws: 2, losses: 1 }
      ]
    }

    const loadLeagues = () => {
      leaguesList.value = [
        { id: 1, name: '英格兰足球超级联赛', country: '英格兰', teams_count: 20, matches_count: 380 },
        { id: 2, name: '西班牙足球甲级联赛', country: '西班牙', teams_count: 20, matches_count: 380 },
        { id: 3, name: '意大利足球甲级联赛', country: '意大利', teams_count: 20, matches_count: 380 }
      ]
    }

    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    }

    const getStatusText = (status) => {
      const statusMap = {
        upcoming: '即将开始',
        in_progress: '进行中',
        finished: '已结束',
        postponed: '推迟'
      }
      return statusMap[status] || status
    }

    const handleCreateMatch = () => {
      dialogTitle.value = '添加比赛'
      showEditDialog.value = true
    }

    const handleEditMatch = (match) => {
      dialogTitle.value = '编辑比赛'
      showEditDialog.value = true
    }

    const handleDeleteMatch = (id) => {
      if (confirm('确定要删除这场比赛吗？')) {
        alert('删除成功')
        loadMatches()
      }
    }

    const handleCreateLeague = () => {
      dialogTitle.value = '添加联赛'
      showEditDialog.value = true
    }

    const handleEditLeague = (league) => {
      dialogTitle.value = '编辑联赛'
      showEditDialog.value = true
    }

    const handleDeleteLeague = (id) => {
      if (confirm('确定要删除这个联赛吗？')) {
        alert('删除成功')
        loadLeagues()
      }
    }

    const handleCreateTeam = () => {
      dialogTitle.value = '添加球队'
      showEditDialog.value = true
    }

    const handleEditTeam = (team) => {
      dialogTitle.value = '编辑球队'
      showEditDialog.value = true
    }

    const handleDeleteTeam = (id) => {
      if (confirm('确定要删除这支球队吗？')) {
        alert('删除成功')
        loadTeams()
      }
    }

    const handleMatchPageChange = (page) => {
      matchPagination.page = page
      loadMatches()
    }

    const closeEditDialog = () => {
      showEditDialog.value = false
    }

    onMounted(() => {
      loadMatches()
      loadLeagues()
      loadTeams()
    })

    return {
      activeTab,
      tabs,
      matches,
      matchFilters,
      matchPagination,
      leaguesList,
      leagues,
      teams,
      teamFilters,
      showEditDialog,
      dialogTitle,
      formatDate,
      getStatusText,
      loadMatches,
      loadTeams,
      handleCreateMatch,
      handleEditMatch,
      handleDeleteMatch,
      handleCreateLeague,
      handleEditLeague,
      handleDeleteLeague,
      handleCreateTeam,
      handleEditTeam,
      handleDeleteTeam,
      handleMatchPageChange,
      closeEditDialog
    }
  }
}
</script>

<style scoped>
.data-management-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: white;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #f8fafc;
  color: #475569;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tab-icon {
  font-size: 18px;
}

.tab-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px 0 0 8px;
  font-size: 14px;
}

.search-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.filters {
  display: flex;
  gap: 10px;
}

.filters select {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
}

.create-btn {
  padding: 10px 20px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.data-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

th {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  font-size: 14px;
  color: #1e293b;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-upcoming { background: #dbeafe; color: #1e40af; }
.status-in_progress { background: #fef3c7; color: #92400e; }
.status-finished { background: #d1fae5; color: #065f46; }
.status-postponed { background: #fecaca; color: #991b1b; }

.text-muted {
  color: #94a3b8;
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.btn-edit, .btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.btn-edit {
  background: #dbeafe;
  color: #1e40af;
}

.btn-delete {
  background: #fecaca;
  color: #991b1b;
}

.grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.league-card, .team-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s;
}

.league-card:hover, .team-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.league-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.team-logo {
  width: 60px;
  height: 60px;
  margin: 0 auto 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: white;
}

h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.league-country, .team-league {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 16px 0;
}

.league-stats, .team-stats {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #64748b;
}

.team-stats {
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.pagination button {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #475569;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dialog-overlay {
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

.dialog-content {
  background: white;
  border-radius: 12px;
  width: 500px;
  max-width: 90%;
}

.dialog-header {
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #94a3b8;
}

.dialog-body {
  padding: 30px;
}

.coming-soon {
  text-align: center;
  font-size: 16px;
  color: #64748b;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}

.btn-secondary {
  padding: 8px 20px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #475569;
}
</style>
