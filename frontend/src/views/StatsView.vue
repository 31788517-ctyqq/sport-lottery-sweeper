<template>
  <div class="stats-view-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 数据统计分析</h1>
      <p class="page-description">展示系统各项统计数据、趋势分析和预测准确率</p>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-overview">
      <div class="stat-card primary">
        <div class="stat-icon">
          <i class="icon">⚽</i>
        </div>
        <div class="stat-content">
          <h3>总比赛数</h3>
          <p class="stat-value">{{ stats.totalMatches }}</p>
          <p class="stat-change positive">+{{ stats.newMatchesToday }} 今日新增</p>
        </div>
      </div>

      <div class="stat-card secondary">
        <div class="stat-icon">
          <i class="icon">🎯</i>
        </div>
        <div class="stat-content">
          <h3>预测准确率</h3>
          <p class="stat-value">{{ stats.predictionAccuracy }}%</p>
          <p class="stat-change positive">+{{ stats.accuracyImprovement }}% 提升</p>
        </div>
      </div>

      <div class="stat-card tertiary">
        <div class="stat-icon">
          <i class="icon">👥</i>
        </div>
        <div class="stat-content">
          <h3>活跃用户</h3>
          <p class="stat-value">{{ stats.activeUsers }}</p>
          <p class="stat-change positive">+{{ stats.newUsersThisMonth }} 本月新增</p>
        </div>
      </div>

      <div class="stat-card quaternary">
        <div class="stat-icon">
          <i class="icon">📈</i>
        </div>
        <div class="stat-content">
          <h3>数据量</h3>
          <p class="stat-value">{{ stats.totalDataPoints }}K</p>
          <p class="stat-change positive">+{{ stats.dataGrowth }}% 增长</p>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-container">
        <div class="chart-header">
          <h3>比赛数量趋势</h3>
          <div class="chart-controls">
            <select v-model="timeRange" @change="updateCharts">
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="quarter">本季度</option>
              <option value="year">本年</option>
            </select>
          </div>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <canvas id="matchesTrendChart" ref="matchesTrendChartRef" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3>预测准确率分布</h3>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <canvas id="accuracyDistributionChart" ref="accuracyDistributionChartRef" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-container wide">
        <div class="chart-header">
          <h3>各联赛数据统计</h3>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <canvas id="leagueStatsChart" ref="leagueStatsChartRef" width="800" height="300"></canvas>
          </div>
        </div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-container">
        <div class="chart-header">
          <h3>用户活跃度统计</h3>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <canvas id="userActivityChart" ref="userActivityChartRef" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3>数据增长趋势</h3>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <canvas id="dataGrowthChart" ref="dataGrowthChartRef" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-section">
      <div class="section-header">
        <h2>📋 详细统计数据</h2>
        <div class="table-controls">
          <select v-model="tableType" @change="updateTableData">
            <option value="matches">比赛统计</option>
            <option value="predictions">预测统计</option>
            <option value="users">用户统计</option>
            <option value="data">数据统计</option>
          </select>
          <button class="action-btn secondary" @click="exportTableData">导出数据</button>
        </div>
      </div>
      
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="header in tableHeaders" :key="header.key">{{ header.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in tableData" :key="index">
              <td v-for="header in tableHeaders" :key="header.key">
                <template v-if="header.type === 'date'">
                  {{ formatDate(row[header.key]) }}
                </template>
                <template v-else-if="header.type === 'percentage'">
                  {{ row[header.key] }}%
                </template>
                <template v-else-if="header.type === 'currency'">
                  ¥{{ row[header.key] }}
                </template>
                <template v-else>
                  {{ row[header.key] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 预测分析 -->
    <div class="prediction-analysis-section">
      <div class="section-header">
        <h2>🔮 预测分析</h2>
      </div>
      
      <div class="prediction-grid">
        <div class="prediction-card" v-for="prediction in predictions" :key="prediction.id">
          <div class="prediction-header">
            <h3>{{ prediction.homeTeam }} VS {{ prediction.awayTeam }}</h3>
            <span class="prediction-league">{{ prediction.league }}</span>
          </div>
          <div class="prediction-content">
            <div class="prediction-match-info">
              <div class="match-date">{{ formatDate(prediction.matchDate) }}</div>
              <div class="match-time">{{ formatTime(prediction.matchDate) }}</div>
            </div>
            <div class="prediction-odds">
              <div class="odd-item">
                <span>胜</span>
                <span class="odd-value">{{ prediction.odds.win }}</span>
              </div>
              <div class="odd-item">
                <span>平</span>
                <span class="odd-value">{{ prediction.odds.draw }}</span>
              </div>
              <div class="odd-item">
                <span>负</span>
                <span class="odd-value">{{ prediction.odds.lose }}</span>
              </div>
            </div>
            <div class="prediction-analysis-result">
              <div class="analysis-label">预测结果</div>
              <div class="analysis-value">{{ prediction.prediction }}</div>
              <div class="confidence">置信度: {{ prediction.confidence }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

// 注册所有图表组件
Chart.register(...registerables)

// 统计数据
const stats = reactive({
  totalMatches: 2458,
  newMatchesToday: 12,
  predictionAccuracy: 82.4,
  accuracyImprovement: 3.2,
  activeUsers: 1245,
  newUsersThisMonth: 87,
  totalDataPoints: 128.5,
  dataGrowth: 12.5
})

// 图表数据
const chartData = reactive({
  matchesTrend: [
    {
      label: '比赛数量',
      values: [65, 70, 80, 60, 75, 85, 90],
      color: '#3b82f6'
    },
    {
      label: '预测数量',
      values: [55, 60, 70, 50, 65, 75, 80],
      color: '#10b981'
    }
  ],
  leagueStats: [
    {
      name: '英超',
      stats: [
        { label: '比赛数量', value: 85, color: '#3b82f6' },
        { label: '准确率', value: 82, color: '#10b981' },
        { label: '更新频率', value: 90, color: '#f59e0b' }
      ]
    },
    {
      name: '西甲',
      stats: [
        { label: '比赛数量', value: 78, color: '#3b82f6' },
        { label: '准确率', value: 79, color: '#10b981' },
        { label: '更新频率', value: 85, color: '#f59e0b' }
      ]
    },
    {
      name: '德甲',
      stats: [
        { label: '比赛数量', value: 65, color: '#3b82f6' },
        { label: '准确率', value: 85, color: '#10b981' },
        { label: '更新频率', value: 80, color: '#f59e0b' }
      ]
    },
    {
      name: '意甲',
      stats: [
        { label: '比赛数量', value: 72, color: '#3b82f6' },
        { label: '准确率', value: 78, color: '#10b981' },
        { label: '更新频率', value: 75, color: '#f59e0b' }
      ]
    },
    {
      name: '法甲',
      stats: [
        { label: '比赛数量', value: 60, color: '#3b82f6' },
        { label: '准确率', value: 80, color: '#10b981' },
        { label: '更新频率', value: 70, color: '#f59e0b' }
      ]
    }
  ]
})

// 图表引用
const matchesTrendChartRef = ref(null)
const accuracyDistributionChartRef = ref(null)
const leagueStatsChartRef = ref(null)
const userActivityChartRef = ref(null)
const dataGrowthChartRef = ref(null)

// 图表实例
let matchesTrendChart = null
let accuracyDistributionChart = null
let leagueStatsChart = null
let userActivityChart = null
let dataGrowthChart = null

// 时间范围选择
const timeRange = ref('month')

// 表格类型选择
const tableType = ref('matches')

// 表格数据
const tableData = ref([])
const tableHeaders = ref([])

// 预测数据
const predictions = ref([
  {
    id: 1,
    homeTeam: '曼城',
    awayTeam: '利物浦',
    league: '英超',
    matchDate: new Date(Date.now() + 86400000),
    odds: { win: 2.3, draw: 3.2, lose: 2.8 },
    prediction: '主胜',
    confidence: 78
  },
  {
    id: 2,
    homeTeam: '巴塞罗那',
    awayTeam: '皇家马德里',
    league: '西甲',
    matchDate: new Date(Date.now() + 172800000),
    odds: { win: 2.8, draw: 3.4, lose: 2.2 },
    prediction: '客胜',
    confidence: 82
  },
  {
    id: 3,
    homeTeam: '拜仁慕尼黑',
    awayTeam: '多特蒙德',
    league: '德甲',
    matchDate: new Date(Date.now() + 259200000),
    odds: { win: 1.6, draw: 3.8, lose: 4.5 },
    prediction: '主胜',
    confidence: 85
  },
  {
    id: 4,
    homeTeam: '尤文图斯',
    awayTeam: 'AC米兰',
    league: '意甲',
    matchDate: new Date(Date.now() + 345600000),
    odds: { win: 2.9, draw: 3.1, lose: 2.4 },
    prediction: '平局',
    confidence: 72
  }
])

// 创建比赛趋势图表
const createMatchesTrendChart = () => {
  const ctx = matchesTrendChartRef.value.getContext('2d')
  
  if (matchesTrendChart) {
    matchesTrendChart.destroy()
  }
  
  matchesTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      datasets: chartData.matchesTrend.map((series, index) => ({
        label: series.label,
        data: series.values,
        borderColor: series.color,
        backgroundColor: series.color + '20',
        tension: 0.4,
        fill: true
      }))
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: '比赛数量趋势'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

// 创建准确率分布图表
const createAccuracyDistributionChart = () => {
  const ctx = accuracyDistributionChartRef.value.getContext('2d')
  
  if (accuracyDistributionChart) {
    accuracyDistributionChart.destroy()
  }
  
  accuracyDistributionChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['高准确率 (80-100%)', '中准确率 (60-79%)', '低准确率 (40-59%)', '极低准确率 (<40%)'],
      datasets: [{
        data: [40, 30, 15, 15],
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#ef4444'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: `预测准确率分布 (${stats.predictionAccuracy}%)`
        }
      }
    }
  })
}

// 创建联赛统计图表
const createLeagueStatsChart = () => {
  const ctx = leagueStatsChartRef.value.getContext('2d')
  
  if (leagueStatsChart) {
    leagueStatsChart.destroy()
  }
  
  // 准备数据
  const leagues = chartData.leagueStats.map(l => l.name)
  const datasets = []
  
  // 获取最大类别数
  const maxCategories = Math.max(...chartData.leagueStats.map(l => l.stats.length))
  
  // 为每个类别创建数据集
  for (let i = 0; i < maxCategories; i++) {
    const firstStat = chartData.leagueStats[0].stats[i]
    datasets.push({
      label: firstStat.label,
      data: chartData.leagueStats.map(l => l.stats[i]?.value || 0),
      backgroundColor: firstStat.color + '80',
      borderColor: firstStat.color,
      borderWidth: 1
    })
  }
  
  leagueStatsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: leagues,
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: '各联赛数据统计'
        }
      },
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true,
        }
      }
    }
  })
}

// 创建用户活跃度图表
const createUserActivityChart = () => {
  const ctx = userActivityChartRef.value.getContext('2d')
  
  if (userActivityChart) {
    userActivityChart.destroy()
  }
  
  userActivityChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['登录频率', '数据查询', '预测提交', '社交互动', '内容分享', '反馈提交'],
      datasets: [{
        label: '用户活跃度',
        data: [75, 65, 50, 40, 30, 20],
        fill: true,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '用户活跃度统计'
        }
      },
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 0,
          suggestedMax: 100
        }
      }
    }
  })
}

// 创建数据增长趋势图表
const createDataGrowthChart = () => {
  const ctx = dataGrowthChartRef.value.getContext('2d')
  
  if (dataGrowthChart) {
    dataGrowthChart.destroy()
  }
  
  // 生成过去30天的数据
  const days = Array.from({ length: 30 }, (_, i) => `第${30-i}天`)
  const data = Array.from({ length: 30 }, (_, i) => Math.floor(Math.random() * 100) + 50)
  
  dataGrowthChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: days,
      datasets: [{
        label: '每日新增数据量',
        data: data,
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '数据增长趋势'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

// 更新图表
const updateCharts = () => {
  console.log(`更新图表数据，时间范围: ${timeRange.value}`)
  // 在实际应用中，这里会根据时间范围重新获取数据
  createMatchesTrendChart()
  createAccuracyDistributionChart()
  createLeagueStatsChart()
  createUserActivityChart()
  createDataGrowthChart()
}

// 更新表格数据
const updateTableData = () => {
  switch(tableType.value) {
    case 'matches':
      tableHeaders.value = [
        { key: 'date', label: '日期', type: 'date' },
        { key: 'league', label: '联赛' },
        { key: 'homeTeam', label: '主队' },
        { key: 'awayTeam', label: '客队' },
        { key: 'result', label: '结果' },
        { key: 'attendance', label: '观众数' }
      ];
      tableData.value = [
        { date: new Date(Date.now() - 86400000), league: '英超', homeTeam: '曼联', awayTeam: '热刺', result: '2-1', attendance: 74000 },
        { date: new Date(Date.now() - 86400000), league: '西甲', homeTeam: '皇马', awayTeam: '贝蒂斯', result: '3-0', attendance: 68532 },
        { date: new Date(Date.now() - 172800000), league: '德甲', homeTeam: '多特', awayTeam: '莱比锡', result: '1-1', attendance: 65000 },
        { date: new Date(Date.now() - 259200000), league: '意甲', homeTeam: '国米', awayTeam: '拉齐奥', result: '2-0', attendance: 60201 },
        { date: new Date(Date.now() - 345600000), league: '法甲', homeTeam: '大巴黎', awayTeam: '马赛', result: '4-0', attendance: 47850 }
      ];
      break;
    
    case 'predictions':
      tableHeaders.value = [
        { key: 'date', label: '日期', type: 'date' },
        { key: 'league', label: '联赛' },
        { key: 'homeTeam', label: '主队' },
        { key: 'awayTeam', label: '客队' },
        { key: 'predictedOutcome', label: '预测结果' },
        { key: 'actualOutcome', label: '实际结果' },
        { key: 'accuracy', label: '准确率', type: 'percentage' }
      ];
      tableData.value = [
        { date: new Date(Date.now() - 86400000), league: '英超', homeTeam: '曼联', awayTeam: '热刺', predictedOutcome: '主胜', actualOutcome: '主胜', accuracy: 85 },
        { date: new Date(Date.now() - 86400000), league: '西甲', homeTeam: '皇马', awayTeam: '贝蒂斯', predictedOutcome: '主胜', actualOutcome: '主胜', accuracy: 90 },
        { date: new Date(Date.now() - 172800000), league: '德甲', homeTeam: '多特', awayTeam: '莱比锡', predictedOutcome: '平局', actualOutcome: '主负', accuracy: 45 },
        { date: new Date(Date.now() - 259200000), league: '意甲', homeTeam: '国米', awayTeam: '拉齐奥', predictedOutcome: '主胜', actualOutcome: '平局', accuracy: 65 },
        { date: new Date(Date.now() - 345600000), league: '法甲', homeTeam: '大巴黎', awayTeam: '马赛', predictedOutcome: '主胜', actualOutcome: '主胜', accuracy: 88 }
      ];
      break;
    
    case 'users':
      tableHeaders.value = [
        { key: 'username', label: '用户名' },
        { key: 'joinDate', label: '加入日期', type: 'date' },
        { key: 'lastActivity', label: '最后活动', type: 'date' },
        { key: 'predictionsMade', label: '预测次数' },
        { key: 'accuracy', label: '准确率', type: 'percentage' }
      ];
      tableData.value = [
        { username: 'user1', joinDate: new Date(Date.now() - 86400000 * 30), lastActivity: new Date(Date.now() - 3600000), predictionsMade: 120, accuracy: 78 },
        { username: 'user2', joinDate: new Date(Date.now() - 86400000 * 45), lastActivity: new Date(Date.now() - 7200000), predictionsMade: 98, accuracy: 82 },
        { username: 'user3', joinDate: new Date(Date.now() - 86400000 * 15), lastActivity: new Date(Date.now() - 1800000), predictionsMade: 45, accuracy: 75 },
        { username: 'user4', joinDate: new Date(Date.now() - 86400000 * 60), lastActivity: new Date(Date.now() - 86400000), predictionsMade: 210, accuracy: 85 },
        { username: 'user5', joinDate: new Date(Date.now() - 86400000 * 20), lastActivity: new Date(Date.now() - 14400000), predictionsMade: 76, accuracy: 79 }
      ];
      break;
    
    case 'data':
      tableHeaders.value = [
        { key: 'source', label: '数据源' },
        { key: 'dataType', label: '数据类型' },
        { key: 'lastUpdate', label: '最后更新', type: 'date' },
        { key: 'recordCount', label: '记录数' },
        { key: 'accuracy', label: '准确率', type: 'percentage' }
      ];
      tableData.value = [
        { source: 'SportsAPI', dataType: '比赛结果', lastUpdate: new Date(Date.now() - 1800000), recordCount: 12580, accuracy: 98.5 },
        { source: 'OddsProvider', dataType: '赔率', lastUpdate: new Date(Date.now() - 300000), recordCount: 8450, accuracy: 96.2 },
        { source: 'NewsFeed', dataType: '新闻', lastUpdate: new Date(Date.now() - 600000), recordCount: 5620, accuracy: 92.8 },
        { source: 'SocialMedia', dataType: '情绪分析', lastUpdate: new Date(Date.now() - 300000), recordCount: 12450, accuracy: 85.6 },
        { source: 'Internal', dataType: '用户预测', lastUpdate: new Date(Date.now() - 60000), recordCount: 24580, accuracy: 82.4 }
      ];
      break;
  }
}

// 导出表格数据
const exportTableData = () => {
  console.log('导出表格数据...')
  // 在实际应用中，这里会导出数据到文件
  alert(`正在导出${getTableTypeName()}数据...`)
}

// 获取表格类型名称
const getTableTypeName = () => {
  switch(tableType.value) {
    case 'matches': return '比赛';
    case 'predictions': return '预测';
    case 'users': return '用户';
    case 'data': return '数据';
    default: return '';
  }
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-';
  const d = new Date(date)
  return d.toLocaleDateString()
}

// 格式化时间
const formatTime = (date) => {
  if (!date) return '-';
  const d = new Date(date)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 初始化数据
onMounted(() => {
  console.log('Stats View 页面已加载')
  updateTableData()
  
  // 创建所有图表
  setTimeout(() => {
    createMatchesTrendChart()
    createAccuracyDistributionChart()
    createLeagueStatsChart()
    createUserActivityChart()
    createDataGrowthChart()
  }, 100)
})
</script>

<style scoped>
.stats-view-container {
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

/* 统计概览卡片 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.stat-card.primary {
  border-left: 4px solid #3b82f6;
}

.stat-card.secondary {
  border-left: 4px solid #10b981;
}

.stat-card.tertiary {
  border-left: 4px solid #8b5cf6;
}

.stat-card.quaternary {
  border-left: 4px solid #f59e0b;
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

.stat-card.primary .stat-icon {
  background: #dbeafe;
  color: #2563eb;
}

.stat-card.secondary .stat-icon {
  background: #d1fae5;
  color: #065f46;
}

.stat-card.tertiary .stat-icon {
  background: #e9d5ff;
  color: #7c2d12;
}

.stat-card.quaternary .stat-icon {
  background: #fef3c7;
  color: #92400e;
}

.stat-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #6b7280;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.stat-change {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.negative {
  color: #dc2626;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.chart-container.wide {
  grid-column: span 2;
}

.chart-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.chart-controls select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 14px;
}

.chart-content {
  padding: 20px;
}

.chart-placeholder {
  text-align: center;
  padding: 20px;
}

.line-chart {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.line-graph {
  display: flex;
  align-items: flex-end;
  height: 100px;
  gap: 5px;
  padding: 10px 0;
}

.bar {
  flex: 1;
  min-width: 15px;
  border-radius: 4px 4px 0 0;
}

.pie-chart {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 20px auto;
}

.pie-segment {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.center-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.center-label {
  font-size: 12px;
  color: #6b7280;
}

.legend {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.legend.horizontal {
  flex-direction: row;
  justify-content: center;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.bar-chart {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bar-group {
  display: flex;
  align-items: end;
  height: 120px;
  gap: 10px;
}

.bar-label {
  width: 80px;
  font-size: 12px;
  text-align: right;
  padding-right: 10px;
}

.bars {
  flex: 1;
  display: flex;
  height: 100%;
  gap: 5px;
  align-items: flex-end;
}

/* 数据表格区域 */
.data-table-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  margin-bottom: 32px;
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
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.table-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.table-controls select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.data-table tbody tr:hover {
  background-color: #f9fafb;
}

/* 预测分析区域 */
.prediction-analysis-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.prediction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.prediction-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #f9fafb;
}

.prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.prediction-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.prediction-league {
  background: #e0e7ff;
  color: #3730a3;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.prediction-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prediction-match-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #6b7280;
}

.prediction-odds {
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
}

.odd-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.odd-value {
  font-weight: 700;
  font-size: 16px;
  margin-top: 4px;
}

.prediction-analysis-result {
  border-top: 1px dashed #d1d5db;
  padding-top: 12px;
  text-align: center;
}

.analysis-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.analysis-value {
  font-weight: 700;
  font-size: 18px;
  color: #1f2937;
  margin-bottom: 4px;
}

.confidence {
  font-size: 12px;
  color: #059669;
  font-weight: 500;
}

/* 操作按钮样式 */
.action-btn {
  padding: 8px 16px;
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

.action-btn.secondary {
  background: #6366f1;
  color: white;
}

.action-btn.secondary:hover {
  background: #4f46e5;
}

@media (max-width: 768px) {
  .stats-view-container {
    padding: 16px;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .chart-container.wide {
    grid-column: span 1;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .prediction-grid {
    grid-template-columns: 1fr;
  }
  
  .data-table {
    min-width: 600px;
  }
}
</style>