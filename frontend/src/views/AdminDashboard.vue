<template>
  <div class="dashboard-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📈 管理后台仪表板</h1>
      <p class="page-description">系统概览和关键指标监控</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon matches">
          <i class="icon-calendar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">比赛总数</div>
          <div class="stat-value">{{ stats.total_matches || 0 }}</div>
          <div class="stat-change positive">+{{ stats.new_matches_today || 0 }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon intelligence">
          <i class="icon-brain"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">情报记录</div>
          <div class="stat-value">{{ stats.total_intelligence || 0 }}</div>
          <div class="stat-change positive">+{{ stats.new_intelligence_today || 0 }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon crawler">
          <i class="icon-spider"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">爬虫配置</div>
          <div class="stat-value">{{ stats.total_crawlers || 0 }}</div>
          <div class="stat-change neutral">{{ stats.active_crawlers || 0 }} 个运行中</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon users">
          <i class="icon-users"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">系统用户</div>
          <div class="stat-value">{{ stats.total_users || 0 }}</div>
          <div class="stat-change positive">+{{ stats.new_users_today || 0 }} 今日新增</div>
        </div>
      </div>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索比赛、情报或配置..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.timeRange" @change="handleTimeRangeChange">
          <option value="today">今日</option>
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="all">全部</option>
        </select>
        
        <select v-model="filters.contentType" @change="handleContentTypeChange">
          <option value="all">全部类型</option>
          <option value="matches">比赛数据</option>
          <option value="intelligence">情报分析</option>
          <option value="crawler">爬虫配置</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="navigateTo('/admin/matches')">
          <span>⚽</span> 管理比赛
        </button>
        <button class="action-btn secondary" @click="navigateTo('/admin/intelligence')">
          <span>🧠</span> 查看情报
        </button>
        <button class="action-btn tertiary" @click="navigateTo('/admin/crawler-config')">
          <span>🕷️</span> 配置爬虫
        </button>
      </div>
    </div>

    <!-- 最近活动列表 -->
    <div class="recent-activities">
      <div class="section-header">
        <h2>📋 最近活动</h2>
        <div class="view-all">
          <button @click="navigateTo('/admin/data')">查看全部</button>
        </div>
      </div>
      
      <div class="activity-list">
        <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
          <div class="activity-icon" :class="activity.type">
            <i :class="getActivityIcon(activity.type)"></i>
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-description">{{ activity.description }}</div>
            <div class="activity-time">{{ formatTime(activity.created_at) }}</div>
          </div>
          <div class="activity-actions">
            <button class="btn-view" @click="handleViewActivity(activity)">查看</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态卡片 -->
    <div class="system-status-grid">
      <div class="status-card">
        <div class="status-header">
          <h3>🔧 系统状态</h3>
          <span class="status-indicator online"></span>
        </div>
        <div class="status-content">
          <div class="status-item">
            <span class="label">后端服务:</span>
            <span class="value online">正常运行</span>
          </div>
          <div class="status-item">
            <span class="label">数据库连接:</span>
            <span class="value online">已连接</span>
          </div>
          <div class="status-item">
            <span class="label">爬虫服务:</span>
            <span class="value" :class="stats.active_crawlers > 0 ? 'online' : 'warning'">
              {{ stats.active_crawlers > 0 ? '运行中' : '未启动' }}
            </span>
          </div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-header">
          <h3>📊 数据概览</h3>
        </div>
        <div class="status-content">
          <div class="status-item">
            <span class="label">今日抓取:</span>
            <span class="value highlight">{{ stats.matches_crawled_today || 0 }} 条</span>
          </div>
          <div class="status-item">
            <span class="label">情报准确率:</span>
            <span class="value highlight">{{ stats.intelligence_accuracy || 'N/A' }}</span>
          </div>
          <div class="status-item">
            <span class="label">系统负载:</span>
            <span class="value normal">{{ stats.system_load || '正常' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 统计数据
const stats = reactive({
  total_matches: 0,
  new_matches_today: 0,
  total_intelligence: 0,
  new_intelligence_today: 0,
  total_crawlers: 0,
  active_crawlers: 0,
  total_users: 0,
  new_users_today: 0,
  matches_crawled_today: 0,
  intelligence_accuracy: 'N/A',
  system_load: '正常'
})

// 搜索和筛选
const searchKeyword = ref('')
const filters = reactive({
  timeRange: 'today',
  contentType: 'all'
})

// 最近活动
const recentActivities = ref([])

// 导航函数
const navigateTo = (path) => {
  router.push(path)
}

// 搜索处理
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
  // 实现搜索逻辑
}

const handleTimeRangeChange = () => {
  console.log('时间范围:', filters.timeRange)
  loadStats()
}

const handleContentTypeChange = () => {
  console.log('内容类型:', filters.contentType)
}

// 查看活动详情
const handleViewActivity = (activity) => {
  console.log('查看活动:', activity)
  // 根据活动类型跳转到相应页面
}

// 获取活动图标
const getActivityIcon = (type) => {
  const icons = {
    match: 'icon-calendar',
    intelligence: 'icon-brain',
    crawler: 'icon-spider',
    user: 'icon-users',
    system: 'icon-settings'
  }
  return icons[type] || 'icon-default'
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用实际的API
    // const response = await fetch('/api/admin/dashboard/stats')
    // const data = await response.json()
    
    // 模拟数据
    Object.assign(stats, {
      total_matches: 1250,
      new_matches_today: 15,
      total_intelligence: 890,
      new_intelligence_today: 8,
      total_crawlers: 12,
      active_crawlers: 8,
      total_users: 156,
      new_users_today: 3,
      matches_crawled_today: 245,
      intelligence_accuracy: '82.5%',
      system_load: '正常'
    })

    // 模拟最近活动
    recentActivities.value = [
      {
        id: 1,
        type: 'match',
        title: '新增比赛数据',
        description: '添加了英超联赛的3场比赛信息',
        created_at: new Date(Date.now() - 1800000).toISOString()
      },
      {
        id: 2,
        type: 'intelligence',
        title: '智能分析完成',
        description: '完成了今日比赛情报的AI分析',
        created_at: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: 3,
        type: 'crawler',
        title: '爬虫任务执行',
        description: '足球数据源爬虫成功抓取了最新数据',
        created_at: new Date(Date.now() - 7200000).toISOString()
      }
    ]
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard-container {
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

.stat-icon.matches {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.intelligence {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.crawler {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.users {
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

/* 最近活动样式 */
.recent-activities {
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

.view-all button {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.activity-list {
  padding: 0;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f9fafb;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-icon.match {
  background: #ede9fe;
  color: #7c3aed;
}

.activity-icon.intelligence {
  background: #fce7f3;
  color: #db2777;
}

.activity-icon.crawler {
  background: #dbeafe;
  color: #2563eb;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.activity-description {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #9ca3af;
}

.activity-actions {
  display: flex;
  gap: 8px;
}

.btn-view {
  padding: 6px 12px;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.btn-view:hover {
  background: #e5e7eb;
}

/* 系统状态网格 */
.system-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #10b981;
}

.status-content {
  space-y: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.status-item .label {
  color: #6b7280;
  font-size: 14px;
}

.status-item .value {
  font-weight: 500;
  font-size: 14px;
}

.status-item .value.online {
  color: #10b981;
}

.status-item .value.warning {
  color: #f59e0b;
}

.status-item .value.highlight {
  color: #3b82f6;
  font-weight: 600;
}

.status-item .value.normal {
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .system-status-grid {
    grid-template-columns: 1fr;
  }
}
</style>