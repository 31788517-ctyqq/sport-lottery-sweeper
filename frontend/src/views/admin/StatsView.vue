<template>
  <div class="stats-view">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>📊 数据统计</h3>
            <p class="subtitle">系统各项数据的统计分析</p>
          </div>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="onDateRangeChange"
            />
            <el-button type="primary" @click="refreshStats">刷新数据</el-button>
          </div>
        </div>
      </template>

      <!-- 统计概览卡片 -->
      <el-row :gutter="20" class="overview-stats">
        <el-col :span="6">
          <el-card class="stat-card primary">
            <div class="stat-content">
              <div class="stat-icon bg-primary">
                <i class="el-icon-user" />
              </div>
              <div class="stat-info">
                <div class="stat-label">总用户数</div>
                <div class="stat-value">{{ stats.totalUsers }}</div>
                <div class="stat-change">
                  <i :class="stats.userGrowth >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="stats.userGrowth >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(stats.userGrowth) }}%
                  </span>
                  <span class="compared-text">较上周</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card success">
            <div class="stat-content">
              <div class="stat-icon bg-success">
                <i class="el-icon-football" />
              </div>
              <div class="stat-info">
                <div class="stat-label">比赛数据</div>
                <div class="stat-value">{{ stats.totalMatches }}</div>
                <div class="stat-change">
                  <i :class="stats.matchGrowth >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="stats.matchGrowth >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(stats.matchGrowth) }}%
                  </span>
                  <span class="compared-text">较上周</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card warning">
            <div class="stat-content">
              <div class="stat-icon bg-warning">
                <i class="el-icon-data-analysis" />
              </div>
              <div class="stat-info">
                <div class="stat-label">情报记录</div>
                <div class="stat-value">{{ stats.totalIntelligence }}</div>
                <div class="stat-change">
                  <i :class="stats.intelligenceGrowth >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="stats.intelligenceGrowth >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(stats.intelligenceGrowth) }}%
                  </span>
                  <span class="compared-text">较上周</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card danger">
            <div class="stat-content">
              <div class="stat-icon bg-danger">
                <i class="el-icon-mouse" />
              </div>
              <div class="stat-info">
                <div class="stat-label">对冲机会</div>
                <div class="stat-value">{{ stats.totalHedges }}</div>
                <div class="stat-change">
                  <i :class="stats.hedgeGrowth >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="stats.hedgeGrowth >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(stats.hedgeGrowth) }}%
                  </span>
                  <span class="compared-text">较上周</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>📈 活动趋势图</span>
                <el-radio-group v-model="trendPeriod" size="small">
                  <el-radio-button value="day">日</el-radio-button>
                  <el-radio-button value="week">周</el-radio-button>
                  <el-radio-button value="month">月</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="trendChart" class="chart-container" style="height: 400px;" />
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <span>🏆 预测准确率</span>
            </template>
            <div ref="accuracyChart" class="chart-container" style="height: 400px;" />
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>🎯 对冲策略表现</span>
            </template>
            <div ref="hedgeChart" class="chart-container" style="height: 300px;" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>🧠 AI服务使用情况</span>
            </template>
            <div ref="aiUsageChart" class="chart-container" style="height: 300px;" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细数据表格 -->
      <el-card class="data-table-card" style="margin-top: 20px;">
        <template #header>
          <div class="table-header">
            <span>📋 详细统计数据</span>
            <el-button type="primary" @click="exportData">导出数据</el-button>
          </div>
        </template>
        <el-table :data="detailedStats" style="width: 100%" stripe>
          <el-table-column prop="date" label="日期" width="150" />
          <el-table-column prop="usersActive" label="活跃用户" width="120" />
          <el-table-column prop="matchesProcessed" label="处理比赛" width="120" />
          <el-table-column prop="intelligenceAdded" label="新增情报" width="120" />
          <el-table-column prop="predictionsMade" label="预测次数" width="120" />
          <el-table-column prop="hedgesIdentified" label="对冲识别" width="120" />
          <el-table-column prop="accuracyRate" label="准确率(%)" width="120" />
        </el-table>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// 响应式数据
const dateRange = ref([])
const trendPeriod = ref('week')
const stats = ref({
  totalUsers: 1250,
  userGrowth: 5.2,
  totalMatches: 12840,
  matchGrowth: 8.7,
  totalIntelligence: 8934,
  intelligenceGrowth: 12.3,
  totalHedges: 421,
  hedgeGrowth: 3.8
})

const detailedStats = ref([
  { date: '2023-05-15', usersActive: 125, matchesProcessed: 24, intelligenceAdded: 42, predictionsMade: 86, hedgesIdentified: 5, accuracyRate: 82.3 },
  { date: '2023-05-16', usersActive: 132, matchesProcessed: 31, intelligenceAdded: 38, predictionsMade: 92, hedgesIdentified: 7, accuracyRate: 84.1 },
  { date: '2023-05-17', usersActive: 128, matchesProcessed: 28, intelligenceAdded: 45, predictionsMade: 89, hedgesIdentified: 4, accuracyRate: 83.7 },
  { date: '2023-05-18', usersActive: 142, matchesProcessed: 35, intelligenceAdded: 51, predictionsMade: 102, hedgesIdentified: 9, accuracyRate: 85.2 },
  { date: '2023-05-19', usersActive: 138, matchesProcessed: 32, intelligenceAdded: 47, predictionsMade: 95, hedgesIdentified: 6, accuracyRate: 84.6 },
  { date: '2023-05-20', usersActive: 145, matchesProcessed: 38, intelligenceAdded: 53, predictionsMade: 110, hedgesIdentified: 8, accuracyRate: 86.1 },
  { date: '2023-05-21', usersActive: 152, matchesProcessed: 42, intelligenceAdded: 58, predictionsMade: 118, hedgesIdentified: 11, accuracyRate: 85.8 }
])

// 图表引用
const trendChart = ref(null)
const accuracyChart = ref(null)
const hedgeChart = ref(null)
const aiUsageChart = ref(null)

// 方法
const refreshStats = () => {
  // 模拟数据刷新
  ElMessage.success('数据已刷新')
  updateCharts()
}

const onDateRangeChange = (val) => {
  console.log('日期范围变更:', val)
  updateCharts()
}

const exportData = () => {
  ElMessage.info('数据导出功能将在正式版本中实现')
}

// 更新图表
const updateCharts = async () => {
  await nextTick()
  
  // 活动趋势图
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value)
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
        data: ['活跃用户', '处理比赛', '新增情报']
      },
      toolbox: {
        feature: {
          saveAsImage: {}
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          boundaryGap: false,
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        }
      ],
      yAxis: [
        {
          type: 'value'
        }
      ],
      series: [
        {
          name: '活跃用户',
          type: 'line',
          stack: '总量',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [120, 132, 101, 134, 90, 230, 210]
        },
        {
          name: '处理比赛',
          type: 'line',
          stack: '总量',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [220, 182, 191, 234, 290, 330, 310]
        },
        {
          name: '新增情报',
          type: 'line',
          stack: '总量',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [150, 232, 201, 154, 190, 330, 410]
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
    window.addEventListener('resize', debouncedResize)
    // 第二个resize事件的修复
    let resizeTimeout2 = null;
    const debouncedResize2 = () => {
      if (resizeTimeout2) {
        clearTimeout(resizeTimeout2);
      }
      resizeTimeout2 = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    window.addEventListener('resize', debouncedResize2)
    // 第三个resize事件的修复
    let resizeTimeout3 = null;
    const debouncedResize3 = () => {
      if (resizeTimeout3) {
        clearTimeout(resizeTimeout3);
      }
      resizeTimeout3 = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    window.addEventListener('resize', debouncedResize3)
    // 第四个resize事件的修复
    let resizeTimeout4 = null;
    const debouncedResize4 = () => {
      if (resizeTimeout4) {
        clearTimeout(resizeTimeout4);
      }
      resizeTimeout4 = setTimeout(() => {
        chart?.resize();
      }, 100);
    };
    window.addEventListener('resize', debouncedResize4)
  }

  // 任务执行效率图（散点图）
  if (accuracyChart.value) {
    const chart = echarts.init(accuracyChart.value)
    chart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: '准确率',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true,
            length: 10,
            length2: 10
          },
          data: [
            { value: 85.6, name: '准确预测' },
            { value: 14.4, name: '预测偏差' }
          ]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 对冲策略表现图
  if (hedgeChart.value) {
    const chart = echarts.init(hedgeChart.value)
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {},
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        boundaryGap: [0, 0.01]
      },
      yAxis: {
        type: 'category',
        data: ['策略A', '策略B', '策略C', '策略D', '策略E']
      },
      series: [
        {
          name: '收益率',
          type: 'bar',
          data: [18203, 23489, 29034, 104970, 131744]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // AI服务使用情况
  if (aiUsageChart.value) {
    const chart = echarts.init(aiUsageChart.value)
    chart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: 'AI服务使用占比',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '60%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: true,
            length: 5,
            length2: 5
          },
          data: [
            { value: 45, name: 'OpenAI GPT-4' },
            { value: 25, name: 'Anthropic Claude' },
            { value: 15, name: '本地模型' },
            { value: 10, name: '其他' }
          ]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }
}

onMounted(() => {
  updateCharts()
})
</script>

<style scoped>
.card-container {
  margin: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div:first-child h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.overview-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card.primary { border-top: 3px solid #409eff; }
.stat-card.success { border-top: 3px solid #67c23a; }
.stat-card.warning { border-top: 3px solid #e6a23c; }
.stat-card.danger { border-top: 3px solid #f56c6c; }

.stat-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
  font-size: 24px;
}

.bg-primary { background: #409eff; }
.bg-success { background: #67c23a; }
.bg-warning { background: #e6a23c; }
.bg-danger { background: #f56c6c; }

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 5px 0;
}

.stat-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}

.compared-text {
  color: #909399;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-table-card {
  margin-top: 20px;
}
</style>