<template>
  <div class="match-view-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">⚽ 比赛详情</h1>
      <p class="page-description">查看比赛详细信息、统计数据和相关分析</p>
    </div>

    <!-- 比赛基本信息 -->
    <div class="match-info-section">
      <div class="match-header">
        <div class="match-teams">
          <div class="team home-team">
            <img :src="matchInfo.homeTeam.logo" :alt="matchInfo.homeTeam.name" class="team-logo" v-if="matchInfo.homeTeam.logo" />
            <div v-else class="team-logo-placeholder">{{ matchInfo.homeTeam.name.substring(0, 1) }}</div>
            <h2 class="team-name">{{ matchInfo.homeTeam.name }}</h2>
          </div>
          <div class="vs-separator">VS</div>
          <div class="team away-team">
            <h2 class="team-name">{{ matchInfo.awayTeam.name }}</h2>
            <img :src="matchInfo.awayTeam.logo" :alt="matchInfo.awayTeam.name" class="team-logo" v-if="matchInfo.awayTeam.logo" />
            <div v-else class="team-logo-placeholder">{{ matchInfo.awayTeam.name.substring(0, 1) }}</div>
          </div>
        </div>
        <div class="match-details">
          <div class="match-meta">
            <div class="meta-item">
              <span class="meta-label">联赛:</span>
              <span class="meta-value">{{ matchInfo.league }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">日期:</span>
              <span class="meta-value">{{ formatDate(matchInfo.date) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">时间:</span>
              <span class="meta-value">{{ formatTime(matchInfo.date) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">场馆:</span>
              <span class="meta-value">{{ matchInfo.venue }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">状态:</span>
              <span class="status-badge" :class="matchInfo.status">{{ statusLabels[matchInfo.status] }}</span>
            </div>
          </div>
          <div class="match-score">
            <div class="score-display">
              <span class="home-score">{{ matchInfo.homeScore }}</span>
              <span class="score-separator">-</span>
              <span class="away-score">{{ matchInfo.awayScore }}</span>
            </div>
            <div class="match-status">{{ statusLabels[matchInfo.status] }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 比赛导航 -->
    <div class="match-navigation">
      <nav class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['tab-button', { active: activeTab === tab.key }]"
          @click="changeTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- 比赛统计 -->
    <div v-if="activeTab === 'stats'" class="match-stats-section">
      <div class="section-header">
        <h2>📊 比赛统计</h2>
      </div>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.possession.home }}%</div>
          <div class="stat-label">{{ matchInfo.homeTeam.name }} 控球率</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: matchStats.possession.home + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.possession.away }}%</div>
          <div class="stat-label">{{ matchInfo.awayTeam.name }} 控球率</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: matchStats.possession.away + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.shots.home }}</div>
          <div class="stat-label">{{ matchInfo.homeTeam.name }} 射门</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill shots" :style="{ width: calculatePercentage(matchStats.shots.home, matchStats.shots.home + matchStats.shots.away) + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.shots.away }}</div>
          <div class="stat-label">{{ matchInfo.awayTeam.name }} 射门</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill shots" :style="{ width: calculatePercentage(matchStats.shots.away, matchStats.shots.home + matchStats.shots.away) + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.shotsOnTarget.home }}</div>
          <div class="stat-label">{{ matchInfo.homeTeam.name }} 射正</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill target" :style="{ width: calculatePercentage(matchStats.shotsOnTarget.home, matchStats.shotsOnTarget.home + matchStats.shotsOnTarget.away) + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.shotsOnTarget.away }}</div>
          <div class="stat-label">{{ matchInfo.awayTeam.name }} 射正</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill target" :style="{ width: calculatePercentage(matchStats.shotsOnTarget.away, matchStats.shotsOnTarget.home + matchStats.shotsOnTarget.away) + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.fouls.home }}</div>
          <div class="stat-label">{{ matchInfo.homeTeam.name }} 犯规</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill fouls" :style="{ width: calculatePercentage(matchStats.fouls.home, matchStats.fouls.home + matchStats.fouls.away) + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ matchStats.fouls.away }}</div>
          <div class="stat-label">{{ matchInfo.awayTeam.name }} 犯规</div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill fouls" :style="{ width: calculatePercentage(matchStats.fouls.away, matchStats.fouls.home + matchStats.fouls.away) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 比赛事件 -->
    <div v-if="activeTab === 'events'" class="match-events-section">
      <div class="section-header">
        <h2>📋 比赛事件</h2>
      </div>
      <div class="events-timeline">
        <div 
          v-for="event in matchEvents" 
          :key="event.id"
          :class="['event-item', event.team === 'home' ? 'home-event' : 'away-event']"
        >
          <div class="event-time">{{ event.minute }}'</div>
          <div class="event-content">
            <div class="event-type">{{ eventTypeLabels[event.type] }}</div>
            <div class="event-player">{{ event.player }}</div>
            <div class="event-description">{{ event.description }}</div>
          </div>
          <div class="event-team">{{ event.team === 'home' ? matchInfo.homeTeam.name : matchInfo.awayTeam.name }}</div>
        </div>
      </div>
    </div>

    <!-- 预测分析 -->
    <div v-if="activeTab === 'predictions'" class="predictions-section">
      <div class="section-header">
        <h2>🔮 预测分析</h2>
      </div>
      <div class="predictions-grid">
        <div class="prediction-card">
          <h3>赛前预测</h3>
          <div class="prediction-item">
            <span>胜平负概率:</span>
            <div class="probabilities">
              <div class="prob-item">
                <span>{{ matchPredictions.preMatch.homeWin }}%</span>
                <span>{{ matchInfo.homeTeam.name }}</span>
              </div>
              <div class="prob-item">
                <span>{{ matchPredictions.preMatch.draw }}%</span>
                <span>平局</span>
              </div>
              <div class="prob-item">
                <span>{{ matchPredictions.preMatch.awayWin }}%</span>
                <span>{{ matchInfo.awayTeam.name }}</span>
              </div>
            </div>
          </div>
          <div class="prediction-outcome">
            <span>预测结果: {{ matchPredictions.preMatch.result }}</span>
            <span class="confidence">置信度: {{ matchPredictions.preMatch.confidence }}%</span>
          </div>
        </div>
        
        <div class="prediction-card">
          <h3>实时预测</h3>
          <div class="prediction-item">
            <span>当前胜平负概率:</span>
            <div class="probabilities">
              <div class="prob-item">
                <span>{{ matchPredictions.live.homeWin }}%</span>
                <span>{{ matchInfo.homeTeam.name }}</span>
              </div>
              <div class="prob-item">
                <span>{{ matchPredictions.live.draw }}%</span>
                <span>平局</span>
              </div>
              <div class="prob-item">
                <span>{{ matchPredictions.live.awayWin }}%</span>
                <span>{{ matchInfo.awayTeam.name }}</span>
              </div>
            </div>
          </div>
          <div class="prediction-outcome">
            <span>预测结果: {{ matchPredictions.live.result }}</span>
            <span class="confidence">置信度: {{ matchPredictions.live.confidence }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 相关数据 -->
    <div v-if="activeTab === 'data'" class="related-data-section">
      <div class="section-header">
        <h2>📋 相关数据</h2>
      </div>
      <div class="data-grid">
        <div class="data-card">
          <h3>历史对战</h3>
          <div class="data-content">
            <p>最近5次交锋:</p>
            <ul>
              <li v-for="h2h in historicalData.headToHead" :key="h2h.id">
                {{ formatDate(h2h.date) }}: {{ h2h.homeTeam }} {{ h2h.homeScore }} - {{ h2h.awayScore }} {{ h2h.awayTeam }} ({{ h2h.tournament }})
              </li>
            </ul>
          </div>
        </div>
        
        <div class="data-card">
          <h3>{{ matchInfo.homeTeam.name }} 近期战绩</h3>
          <div class="data-content">
            <p>最近5场比赛:</p>
            <ul>
              <li v-for="recent in historicalData.homeRecent" :key="recent.id">
                {{ formatDate(recent.date) }}: {{ recent.opponent }} {{ recent.result }} ({{ recent.tournament }})
              </li>
            </ul>
          </div>
        </div>
        
        <div class="data-card">
          <h3>{{ matchInfo.awayTeam.name }} 近期战绩</h3>
          <div class="data-content">
            <p>最近5场比赛:</p>
            <ul>
              <li v-for="recent in historicalData.awayRecent" :key="recent.id">
                {{ formatDate(recent.date) }}: {{ recent.opponent }} {{ recent.result }} ({{ recent.tournament }})
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// 当前选中的标签页
const activeTab = ref('stats')

// 标签页配置
const tabs = [
  { key: 'stats', label: '比赛统计' },
  { key: 'events', label: '比赛事件' },
  { key: 'predictions', label: '预测分析' },
  { key: 'data', label: '相关数据' }
]

// 切换标签页
const changeTab = (tabKey) => {
  activeTab.value = tabKey
}

// 比赛基本信息
const matchInfo = reactive({
  id: 1,
  homeTeam: {
    name: '曼城',
    logo: '/logos/man_city.png'
  },
  awayTeam: {
    name: '阿森纳',
    logo: '/logos/arsenal.png'
  },
  league: '英超',
  date: new Date(Date.now() - 3600000), // 一小时前
  venue: '伊蒂哈德球场',
  homeScore: 3,
  awayScore: 1,
  status: 'finished'
})

// 比赛状态标签
const statusLabels = {
  scheduled: '已安排',
  live: '进行中',
  finished: '已完成',
  postponed: '推迟',
  cancelled: '取消'
}

// 比赛统计
const matchStats = reactive({
  possession: {
    home: 62,
    away: 38
  },
  shots: {
    home: 14,
    away: 8
  },
  shotsOnTarget: {
    home: 7,
    away: 3
  },
  fouls: {
    home: 12,
    away: 15
  },
  corners: {
    home: 6,
    away: 4
  },
  offsides: {
    home: 2,
    away: 1
  },
  saves: {
    home: 2,
    away: 5
  }
})

// 比赛事件
const matchEvents = [
  {
    id: 1,
    minute: 23,
    type: 'goal',
    player: '哈兰德',
    team: 'home',
    description: '右路传中，哈兰德头球破门'
  },
  {
    id: 2,
    minute: 38,
    type: 'yellow_card',
    player: '厄德高',
    team: 'away',
    description: '战术犯规'
  },
  {
    id: 3,
    minute: 56,
    type: 'goal',
    player: '福登',
    team: 'home',
    description: '禁区外远射得手'
  },
  {
    id: 4,
    minute: 67,
    type: 'goal',
    player: '萨卡',
    team: 'away',
    description: '反击单刀破门'
  },
  {
    id: 5,
    minute: 81,
    type: 'substitution',
    player: '阿尔瓦雷斯',
    team: 'home',
    description: '替换福登上场'
  },
  {
    id: 6,
    minute: 89,
    type: 'goal',
    player: '阿尔瓦雷斯',
    team: 'home',
    description: '补时锁定胜局'
  }
]

// 比赛事件类型标签
const eventTypeLabels = {
  goal: '进球',
  yellow_card: '黄牌',
  red_card: '红牌',
  substitution: '换人',
  penalty: '点球',
  offside: '越位'
}

// 预测分析
const matchPredictions = reactive({
  preMatch: {
    homeWin: 52,
    draw: 28,
    awayWin: 20,
    result: '主胜',
    confidence: 78
  },
  live: {
    homeWin: 78,
    draw: 18,
    awayWin: 4,
    result: '主胜',
    confidence: 85
  }
})

// 历史数据
const historicalData = reactive({
  headToHead: [
    { id: 1, date: new Date(Date.now() - 86400000 * 30), homeTeam: '曼城', awayTeam: '阿森纳', homeScore: 2, awayScore: 1, tournament: '英超' },
    { id: 2, date: new Date(Date.now() - 86400000 * 200), homeTeam: '阿森纳', awayTeam: '曼城', homeScore: 3, awayScore: 1, tournament: '英超' },
    { id: 3, date: new Date(Date.now() - 86400000 * 380), homeTeam: '曼城', awayTeam: '阿森纳', homeScore: 2, awayScore: 2, tournament: '英超' },
    { id: 4, date: new Date(Date.now() - 86400000 * 420), homeTeam: '阿森纳', awayTeam: '曼城', homeScore: 0, awayScore: 1, tournament: '足总杯' },
    { id: 5, date: new Date(Date.now() - 86400000 * 500), homeTeam: '曼城', awayTeam: '阿森纳', homeScore: 3, awayScore: 0, tournament: '英超' }
  ],
  homeRecent: [
    { id: 1, date: new Date(Date.now() - 86400000 * 7), opponent: '利物浦', result: '胜 2-1', tournament: '英超' },
    { id: 2, date: new Date(Date.now() - 86400000 * 14), opponent: '多特蒙德', result: '胜 2-0', tournament: '欧冠' },
    { id: 3, date: new Date(Date.now() - 86400000 * 21), opponent: '富勒姆', result: '胜 5-0', tournament: '英超' },
    { id: 4, date: new Date(Date.now() - 86400000 * 28), opponent: '皇家马德里', result: '负 1-3', tournament: '欧冠' },
    { id: 5, date: new Date(Date.now() - 86400000 * 35), opponent: '西汉姆联', result: '胜 3-1', tournament: '英超' }
  ],
  awayRecent: [
    { id: 1, date: new Date(Date.now() - 86400000 * 7), opponent: '纽卡斯尔', result: '胜 2-0', tournament: '英超' },
    { id: 2, date: new Date(Date.now() - 86400000 * 14), opponent: '曼城', result: '负 1-3', tournament: '英超' },
    { id: 3, date: new Date(Date.now() - 86400000 * 21), opponent: '伯恩茅斯', result: '胜 3-2', tournament: '英超' },
    { id: 4, date: new Date(Date.now() - 86400000 * 28), opponent: '曼联', result: '胜 1-0', tournament: '英超' },
    { id: 5, date: new Date(Date.now() - 86400000 * 35), opponent: '埃弗顿', result: '胜 2-0', tournament: '英超' }
  ]
})

// 工具函数
const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString()
}

const formatTime = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const calculatePercentage = (value, total) => {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}
</script>

<style scoped>
.match-view-container {
  padding: 24px;
  max-width: 1200px;
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

/* 比赛信息部分 */
.match-info-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.match-header {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
}

.team {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.team-logo {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
}

.team-logo-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
}

.team-name {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  text-align: center;
}

.vs-separator {
  font-size: 24px;
  font-weight: 700;
  color: #6b7280;
}

.match-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.match-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  width: 100%;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.meta-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.match-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 16px;
}

.home-score, .away-score {
  font-size: 48px;
  font-weight: 700;
  color: #1f2937;
  min-width: 60px;
  text-align: center;
}

.score-separator {
  font-size: 32px;
  font-weight: 600;
  color: #9ca3af;
}

.match-status {
  font-size: 18px;
  font-weight: 600;
  color: #059669;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-badge.finished {
  background: #dcfce7;
  color: #166534;
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

.status-badge.scheduled {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.postponed {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #b91c1c;
}

/* 比赛导航 */
.match-navigation {
  background: white;
  border-radius: 12px;
  padding: 0 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.tabs {
  display: flex;
  gap: 2px;
}

.tab-button {
  padding: 12px 20px;
  border: none;
  background: transparent;
  font-size: 16px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.tab-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab-button.active {
  background: #3b82f6;
  color: white;
}

/* 内容区域通用样式 */
.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

/* 比赛统计 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.stat-progress {
  margin-top: 10px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  width: 0;
  transition: width 0.5s ease;
}

.progress-fill.shots {
  background: #10b981;
}

.progress-fill.target {
  background: #8b5cf6;
}

.progress-fill.fouls {
  background: #ef4444;
}

/* 比赛事件 */
.events-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.event-item.home-event {
  border-left: 4px solid #3b82f6;
}

.event-item.away-event {
  border-left: 4px solid #ef4444;
}

.event-time {
  font-weight: 700;
  font-size: 16px;
  color: #1f2937;
  min-width: 40px;
  margin-right: 16px;
}

.event-content {
  flex: 1;
}

.event-type {
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.event-player {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.event-description {
  font-size: 14px;
  color: #6b7280;
}

.event-team {
  font-weight: 500;
  color: #6b7280;
  text-align: right;
  min-width: 100px;
}

/* 预测分析 */
.predictions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.prediction-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.prediction-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.prediction-item {
  margin-bottom: 16px;
}

.probabilities {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.prob-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e5e7eb;
}

.prob-item:last-child {
  border-bottom: none;
}

.prediction-outcome {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 12px;
  border-top: 1px dashed #e5e7eb;
}

.confidence {
  color: #059669;
  font-weight: 500;
  font-size: 14px;
}

/* 相关数据 */
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.data-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.data-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.data-content p {
  margin: 0 0 12px 0;
  color: #6b7280;
}

.data-content ul {
  margin: 0;
  padding-left: 20px;
}

.data-content li {
  margin-bottom: 8px;
  color: #4b5563;
}

@media (max-width: 768px) {
  .match-view-container {
    padding: 16px;
  }
  
  .match-teams {
    flex-direction: column;
    gap: 16px;
  }
  
  .match-meta {
    grid-template-columns: 1fr;
  }
  
  .tabs {
    flex-wrap: wrap;
  }
  
  .tab-button {
    flex: 1;
    padding: 10px 8px;
    font-size: 14px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .predictions-grid {
    grid-template-columns: 1fr;
  }
  
  .data-grid {
    grid-template-columns: 1fr;
  }
  
  .event-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .event-team {
    text-align: left;
  }
}
</style>