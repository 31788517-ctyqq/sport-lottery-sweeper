<template>
  <div class="dashboard-container">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="24">
        <div class="dashboard-header">
          <div class="header-content">
            <h1>🎯 智能决策仪表板</h1>
            <p class="current-time">{{ currentTime }}</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="refreshData" :loading="loading">刷新数据</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="4">
        <el-card class="stat-card match-data">
          <div class="stat-content">
            <div class="stat-icon">
              <i class="el-icon-football" />
            </div>
            <div class="stat-info">
              <div class="stat-label">比赛总数</div>
              <div class="stat-value">{{ formatNumber(stats.total_matches) }}</div>
              <div class="stat-change">
                <span class="trend-indicator up">↑ {{ stats.match_growth_rate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="4">
        <el-card class="stat-card intelligence-data">
          <div class="stat-content">
            <div class="stat-icon">
              <i class="el-icon-brain" />
            </div>
            <div class="stat-info">
              <div class="stat-label">情报记录</div>
              <div class="stat-value">{{ formatNumber(stats.total_intelligence) }}</div>
              <div class="stat-change">
                <span class="trend-indicator up">↑ {{ stats.intelligence_growth_rate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="4">
        <el-card class="stat-card crawler-status">
          <div class="stat-content">
            <div class="stat-icon">
              <i class="el-icon-cpu" />
            </div>
            <div class="stat-info">
              <div class="stat-label">爬虫配置</div>
              <div class="stat-value">{{ stats.total_crawlers }}</div>
              <div class="stat-change">
                <span class="trend-indicator stable">运行中: {{ stats.active_crawlers }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="4">
        <el-card class="stat-card prediction-accuracy">
          <div class="stat-content">
            <div class="stat-icon">
              <i class="el-icon-target" />
            </div>
            <div class="stat-info">
              <div class="stat-label">预测准确率</div>
              <div class="stat-value">{{ stats.prediction_accuracy }}%</div>
              <div class="stat-change">
                <span class="trend-indicator up">↑ {{ stats.accuracy_improvement }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="4">
        <el-card class="stat-card user-activity">
          <div class="stat-content">
            <div class="stat-icon">
              <i class="el-icon-user" />
            </div>
            <div class="stat-info">
              <div class="stat-label">系统用户</div>
              <div class="stat-value">{{ formatNumber(stats.total_users) }}</div>
              <div class="stat-change">
                <span class="trend-indicator up">↑ {{ stats.user_growth_rate }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="4">
        <el-card class="stat-card system-performance">
          <div class="stat-content">
            <div class="stat-icon">
              <i class="el-icon-wallet" />
            </div>
            <div class="stat-info">
              <div class="stat-label">AI服务成本</div>
              <div class="stat-value">¥{{ stats.ai_cost_today }}</div>
              <div class="stat-change">
                <span class="trend-indicator down">↓ {{ stats.cost_reduction }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>📈 本周活动趋势</span>
          </template>
          <div ref="activityTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🎯 预测准确率变化</span>
          </template>
          <div ref="predictionAccuracyChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>🤖 AI服务使用情况</span>
          </template>
          <div ref="aiServiceChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>💡 智能决策表现</span>
          </template>
          <div ref="decisionPerformanceChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="recent-activities">
          <template #header>
<div class="section-header">
  <span>📋 最近活动</span>
  <el-button link @click="navigateTo('/admin/logs')">查看全部</el-button>
</div>
          </template>
          
          <el-table :data="recentActivities" style="width: 100%">
            <el-table-column prop="title" label="标题" width="200" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="时间" width="150">
              <template #default="scope">
                {{ formatTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button size="small" @click="handleViewActivity(scope.row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

// 时间和状态
const currentTime = ref('')
const loading = ref(false)

// 统计数据
const stats = reactive({
  total_matches: 1250,
  match_growth_rate: 8.5,
  total_intelligence: 890,
  intelligence_growth_rate: 12.3,
  total_crawlers: 12,
  active_crawlers: 8,
  total_users: 156,
  user_growth_rate: 5.2,
  prediction_accuracy: 82.5,
  accuracy_improvement: 3.2,
  ai_cost_today: 24.50,
  cost_reduction: 7.8
})

// 最近活动
const recentActivities = ref([])

// 图表引用
const activityTrendChart = ref(null)
const predictionAccuracyChart = ref(null)
const aiServiceChart = ref(null)
const decisionPerformanceChart = ref(null)

// 图表实例
const activityTrendChartInstance = ref(null)
const predictionAccuracyChartInstance = ref(null)
const aiServiceChartInstance = ref(null)
const decisionPerformanceChartInstance = ref(null)

// 清理函数
const cleanupFunctions = ref([])

// 初始化数据
const initializeData = () => {
  // 模拟最近活动
  recentActivities.value = [
    {
      id: 1,
      type: 'prediction',
      title: 'AI预测模型更新',
      description: '完成了新一轮的模型训练和优化',
      created_at: new Date(Date.now() - 1800000).toISOString()
    },
    {
      id: 2,
      type: 'match',
      title: '新增比赛数据',
      description: '添加了英超联赛的3场比赛信息',
      created_at: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: 3,
      type: 'intelligence',
      title: '智能分析完成',
      description: '完成了今日比赛情报的AI分析',
      created_at: new Date(Date.now() - 7200000).toISOString()
    },
    {
      id: 4,
      type: 'crawler',
      title: '爬虫任务执行',
      description: '足球数据源爬虫成功抓取了最新数据',
      created_at: new Date(Date.now() - 10800000).toISOString()
    },
    {
      id: 5,
      type: 'system',
      title: '系统配置更新',
      description: '更新了安全策略和性能参数',
      created_at: new Date(Date.now() - 14400000).toISOString()
    }
  ]
}

// 导航函数
const navigateTo = (path) => {
  router.push(path)
}

// 查看活动详情
const handleViewActivity = (activity) => {
  console.log('查看活动:', activity)
  // 根据活动类型跳转到相应页面
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

// 格式化数字
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  // 模拟API调用
  setTimeout(() => {
    initializeData()
    updateCharts()
    loading.value = false
  }, 1000)
}

// 更新图表
const updateCharts = async () => {
  await nextTick()
  
  // 执行之前的清理函数
  cleanupFunctions.value.forEach(fn => fn())
  cleanupFunctions.value = []
  
  // 活动趋势图
  if (activityTrendChart.value) {
    const chart = echarts.init(activityTrendChart.value)
    activityTrendChartInstance.value = chart
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '比赛数据',
          type: 'line',
          data: [120, 132, 101, 134, 90, 230, 210],
          smooth: true,
          itemStyle: { color: '#3b82f6' }
        },
        {
          name: '情报数据',
          type: 'line',
          data: [220, 182, 191, 234, 290, 330, 310],
          smooth: true,
          itemStyle: { color: '#8b5cf6' }
        }
      ]
    })
    // 添加防抖功能以避免过多的resize事件
    let resizeTimeout = null;
    const debouncedResize = () => {
      if (resizeTimeout) {
        clearTimeout(resizeTimeout);
      }
      resizeTimeout = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    window.addEventListener('resize', debouncedResize);
    
    // 注册清理函数
    cleanupFunctions.value.push(() => {
      window.removeEventListener('resize', debouncedResize);
      if (resizeTimeout) {
        clearTimeout(resizeTimeout);
      }
      chart?.dispose();
    });
  }

  // 预测准确率变化
  if (predictionAccuracyChart.value) {
    const chart = echarts.init(predictionAccuracyChart.value)
    predictionAccuracyChartInstance.value = chart
    let resizeTimeout2 = null;
    const debouncedResize2 = () => {
      if (resizeTimeout2) {
        clearTimeout(resizeTimeout2);
      }
      resizeTimeout2 = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
      },
      yAxis: {
        type: 'value',
        max: 100,
        min: 0,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '准确率',
          type: 'line',
          data: [75, 78, 82, 81, 84, 82.5, 83.2],
          smooth: true,
          itemStyle: { color: '#f59e0b' },
          areaStyle: { opacity: 0.3 }
        }
      ]
    })
    window.addEventListener('resize', debouncedResize2)
    
    // 注册清理函数
    cleanupFunctions.value.push(() => {
      window.removeEventListener('resize', debouncedResize2);
      if (resizeTimeout2) {
        clearTimeout(resizeTimeout2);
      }
      chart?.dispose();
    });
  }

  // AI服务使用情况
  if (aiServiceChart.value) {
    const chart = echarts.init(aiServiceChart.value)
    aiServiceChartInstance.value = chart
    let resizeTimeout3 = null;
    const debouncedResize3 = () => {
      if (resizeTimeout3) {
        clearTimeout(resizeTimeout3);
      }
      resizeTimeout3 = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    chart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '服务使用占比',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 45, name: 'OpenAI GPT-4' },
            { value: 25, name: 'Anthropic Claude' },
            { value: 15, name: '本地预测模型' },
            { value: 10, name: '图像分析服务' },
            { value: 5, name: '其他' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
    window.addEventListener('resize', debouncedResize3)
    
    // 注册清理函数
    cleanupFunctions.value.push(() => {
      window.removeEventListener('resize', debouncedResize3);
      if (resizeTimeout3) {
        clearTimeout(resizeTimeout3);
      }
      chart?.dispose();
    });
  }

  // 智能决策表现
  if (decisionPerformanceChart.value) {
    const chart = echarts.init(decisionPerformanceChart.value)
    decisionPerformanceChartInstance.value = chart
    let resizeTimeout4 = null;
    const debouncedResize4 = () => {
      if (resizeTimeout4) {
        clearTimeout(resizeTimeout4);
      }
      resizeTimeout4 = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        }
      },
      legend: {
        data: ['收益', '胜率', '风险']
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
      },
      yAxis: [
        {
          type: 'value',
          name: '收益 (¥)',
          position: 'left',
          axisLine: {
            show: true
          }
        },
        {
          type: 'value',
          name: '比率 (%)',
          position: 'right',
          axisLine: {
            show: true
          }
        }
      ],
      series: [
        {
          name: '收益',
          type: 'line',
          stack: '总量',
          areaStyle: {},
          data: [1200, 1320, 1010, 1340, 900, 2300, 2100],
          itemStyle: { color: '#10b981' }
        },
        {
          name: '胜率',
          type: 'line',
          yAxisIndex: 1,
          data: [65, 70, 62, 75, 68, 78, 72],
          itemStyle: { color: '#3b82f6' }
        },
        {
          name: '风险',
          type: 'line',
          yAxisIndex: 1,
          data: [15, 12, 18, 10, 15, 8, 12],
          itemStyle: { color: '#ef4444' }
        }
      ]
    })
    window.addEventListener('resize', debouncedResize4);
    
    // 注册清理函数
    cleanupFunctions.value.push(() => {
      window.removeEventListener('resize', debouncedResize4);
      if (resizeTimeout4) {
        clearTimeout(resizeTimeout4);
      }
      chart?.dispose();
    });
  }
}

// 更新时间
const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

// 组件卸载时清理资源
onUnmounted(() => {
  cleanupFunctions.value.forEach(fn => fn())
})

// 组件挂载时初始化
onMounted(() => {
  initializeData()
  updateTime()
  setInterval(updateTime, 1000)
  updateCharts()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.current-time {
  color: #909399;
  margin: 0;
}

.stat-card {
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: visible;
}

.stat-content {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 15px;
}

.stat-info {
  text-align: left;
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-change {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.trend-indicator {
  font-weight: 500;
}

.trend-indicator.up {
  color: #67c23a;
}

.trend-indicator.down {
  color: #f56c6c;
}

.trend-indicator.stable {
  color: #909399;
}

.chart-card {
  height: 300px;
}

.chart-container {
  height: 240px;
  width: 100%;
}


.recent-activities {
  min-height: 300px;
  overflow: visible;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-card__body {
  padding: 0;
}

.stat-card .el-card__body {
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .stat-card {
    margin-bottom: 10px;
  }
  
  .chart-card {
    margin-bottom: 20px;
  }
}
</style>