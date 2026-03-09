<template>
  <div class="dashboard-stats">
    <h2 class="dashboard-title">仪表板统计</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="errorMessage" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ errorMessage }}</p>
      <button @click="loadDashboardStats" class="retry-button">重试</button>
    </div>

    <!-- 数据展示 -->
    <div v-else class="stats-grid">
      <!-- 总比赛数 -->
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalMatches || 0 }}</div>
          <div class="stat-label">总比赛数</div>
        </div>
      </div>

      <!-- 今日比赛 -->
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.todayMatches || 0 }}</div>
          <div class="stat-label">今日比赛</div>
        </div>
      </div>

      <!-- 活跃用户 -->
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.activeUsers || 0 }}</div>
          <div class="stat-label">活跃用户</div>
        </div>
      </div>

      <!-- 系统健康度 -->
      <div class="stat-card">
        <div class="stat-icon">💚</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.systemHealth || 0 }}%</div>
          <div class="stat-label">系统健康度</div>
        </div>
      </div>
    </div>

    <!-- 刷新按钮 -->
    <div class="refresh-section">
      <button @click="loadDashboardStats" class="refresh-button" :disabled="loading">
        <span v-if="loading">🔄</span>
        <span v-else>🔄</span>
        刷新数据
      </button>
      <span class="last-update">
        最后更新: {{ lastUpdateTime || '暂无数据' }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '@/api/example.js'

// 响应式数据
const loading = ref(false)
const errorMessage = ref('')
const stats = ref({})
const lastUpdateTime = ref('')

// 加载仪表板统计数据
const loadDashboardStats = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const result = await getDashboardStats()
    
    if (result.code === 200) {
      stats.value = result.data || {}
      lastUpdateTime.value = new Date().toLocaleString('zh-CN')
      console.log('仪表板数据:', stats.value)
      
      // 触发数据更新事件
      emit('stats-loaded', stats.value)
    } else {
      errorMessage.value = result.message || '获取数据失败'
    }
  } catch (error) {
    console.error('加载仪表板数据错误:', error)
    errorMessage.value = error.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 格式化数字显示
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// 计算健康度颜色
const getHealthColor = (health: number): string => {
  if (health >= 80) return '#28a745'
  if (health >= 60) return '#ffc107'
  return '#dc3545'
}

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardStats()
})

// 定义事件
const emit = defineEmits(['stats-loaded'])

// 暴露方法给父组件
defineExpose({
  loadDashboardStats,
  stats,
  loading
})
</script>

<style scoped>
.dashboard-stats {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.dashboard-title {
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
  font-weight: 700;
  text-align: center;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-button {
  background-color: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

.retry-button:hover {
  background-color: #5a6fd8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 48px;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.refresh-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.refresh-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s ease;
}

.refresh-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.last-update {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .dashboard-stats {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .refresh-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
}
</style>