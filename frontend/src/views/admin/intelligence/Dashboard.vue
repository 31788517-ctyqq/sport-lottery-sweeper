<template>
  <div class="intelligence-dashboard">
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <span>情报分析仪表板</span>
        </div>
      </template>
      
      <div class="dashboard-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ stats.todayTotal }}</div>
                <div class="stat-title">今日情报总量</div>
              </div>
              <div class="stat-icon bg-blue">
                <i class="el-icon-data-analysis"></i>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ stats.successRate }}%</div>
                <div class="stat-title">准确率</div>
              </div>
              <div class="stat-icon bg-green">
                <i class="el-icon-circle-check"></i>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ stats.activeSources }}</div>
                <div class="stat-title">活跃数据源</div>
              </div>
              <div class="stat-icon bg-purple">
                <i class="el-icon-connection"></i>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ stats.intelTypes }}</div>
                <div class="stat-title">情报类型</div>
              </div>
              <div class="stat-icon bg-orange">
                <i class="el-icon-menu"></i>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <span>近期情报趋势</span>
            </template>
            <div ref="trendChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <span>情报来源分布</span>
            </template>
            <div ref="sourceChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="recent-data-card" style="margin-top: 20px;">
        <template #header>
          <span>最新情报数据</span>
          <el-button type="primary" size="small" @click="refreshData">刷新</el-button>
        </template>
        
        <el-table :data="recentData" style="width: 100%" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="source" label="来源" width="120" />
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="content" label="内容摘要" show-overflow-tooltip />
          <el-table-column prop="confidence" label="可信度" width="100">
            <template #default="scope">
              <el-tag 
                :type="getConfidenceLevel(scope.row.confidence)" 
                size="small"
              >
                {{ scope.row.confidence }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180" />
        </el-table>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getIntelligenceList, getIntelligenceStats } from '@/api/intelligence'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const stats = ref({
  todayTotal: 0,
  successRate: 0,
  activeSources: 0,
  intelTypes: 0
})

const recentData = ref([])
const trendChartRef = ref(null)
const sourceChartRef = ref(null)
let trendChart = null
let sourceChart = null

const refreshData = async () => {
  try {
    // 模拟获取数据
    const mockStats = {
      todayTotal: Math.floor(Math.random() * 1000) + 500,
      successRate: (Math.random() * 10 + 90).toFixed(1),
      activeSources: Math.floor(Math.random() * 50) + 200,
      intelTypes: Math.floor(Math.random() * 20) + 70
    }
    stats.value = mockStats
    
    // 生成模拟的最近数据
    recentData.value = Array.from({ length: 10 }, (_, idx) => ({
      id: idx + 1,
      source: ['数据源A', '数据源B', '数据源C', '数据源D'][idx % 4],
      type: ['技术分析', '基本面分析', '市场情绪', '赔率变动'][idx % 4],
      content: `比赛ID ${Math.floor(Math.random() * 1000)} 的情报数据，包含详细分析...`,
      confidence: Math.floor(Math.random() * 40) + 60,
      createdAt: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString()
    }))
    
    await nextTick()
    renderCharts()
    ElMessage.success('数据刷新成功')
  } catch (err) {
    console.error('获取数据失败:', err)
    ElMessage.error('获取数据失败')
  }
}

const getConfidenceLevel = (confidence) => {
  if (confidence >= 85) return 'success'
  if (confidence >= 70) return 'warning'
  return 'danger'
}

const renderCharts = () => {
  // 渲染趋势图
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    const trendOption = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['新增情报', '有效情报']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '新增情报',
          type: 'line',
          stack: '总量',
          data: [120, 132, 101, 134, 90, 230, 210]
        },
        {
          name: '有效情报',
          type: 'line',
          stack: '总量',
          data: [220, 182, 191, 234, 290, 330, 310]
        }
      ]
    }
    trendChart.setOption(trendOption)
  }
  
  // 渲染来源分布图
  if (sourceChartRef.value) {
    sourceChart = echarts.init(sourceChartRef.value)
    const sourceOption = {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '情报来源',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: '官方数据' },
            { value: 735, name: '社区分享' },
            { value: 580, name: '专业机构' },
            { value: 484, name: '实时监测' },
            { value: 300, name: '其他' }
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
    }
    sourceChart.setOption(sourceOption)
  }
}

const handleResize = () => {
  if (trendChart) {
    trendChart.resize()
  }
  if (sourceChart) {
    sourceChart.resize()
  }
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await refreshData()
})

// 组件卸载时清理图表实例
onUnmounted(() => {
  if (trendChart) {
    trendChart.dispose()
  }
  if (sourceChart) {
    sourceChart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.intelligence-dashboard {
  padding: 20px;
}

.dashboard-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
}

.stat-content .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-content .stat-title {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.bg-blue {
  background: linear-gradient(135deg, #73a7ff, #4a7dff);
}

.bg-green {
  background: linear-gradient(135deg, #67c23a, #529b2e);
}

.bg-purple {
  background: linear-gradient(135deg, #a068f1, #8a47e0);
}

.bg-orange {
  background: linear-gradient(135deg, #f79d2d, #e67612);
}

.chart-card {
  min-height: 350px;
}

.chart-container {
  width: 100%;
}
</style>