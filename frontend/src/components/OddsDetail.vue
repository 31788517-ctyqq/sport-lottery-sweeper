<template>
  <div class="odds-detail">
    <!-- 赔率概览 -->
    <el-card header="赔率概览" class="overview-card" v-if="oddsData">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-label">主胜赔率</div>
            <div class="metric-value highlight">{{ oddsData.homeWin || '--' }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-label">平局赔率</div>
            <div class="metric-value highlight">{{ oddsData.draw || '--' }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-label">客胜赔率</div>
            <div class="metric-value highlight">{{ oddsData.awayWin || '--' }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-label">返还率</div>
            <div class="metric-value">{{ oddsData.returnRate || '--' }}%</div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <div class="metric-item">
            <div class="metric-label">数据源</div>
            <div class="metric-value">{{ oddsData.sourceName }}</div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="metric-item">
            <div class="metric-label">更新时间</div>
            <div class="metric-value">{{ oddsData.lastUpdated }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 赔率变化趋势 -->
    <el-card header="赔率变化趋势" class="chart-card">
      <div ref="oddsChart" class="odds-chart" style="height: 300px;"></div>
    </el-card>

    <!-- 详细赔率信息 -->
    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="欧赔详情" name="european">
        <el-table :data="europeanOdds" border style="width: 100%">
          <el-table-column prop="company" label="公司" width="120" />
          <el-table-column prop="homeWin" label="主胜" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.homeWin }}</span>
              <el-tag :type="scope.row.homeWinChange > 0 ? 'danger' : 'success'" size="small">
                {{ scope.row.homeWinChange > 0 ? '↑' : '↓' }}{{ Math.abs(scope.row.homeWinChange) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="draw" label="平局" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.draw }}</span>
              <el-tag :type="scope.row.drawChange > 0 ? 'danger' : 'success'" size="small">
                {{ scope.row.drawChange > 0 ? '↑' : '↓' }}{{ Math.abs(scope.row.drawChange) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="awayWin" label="客胜" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.awayWin }}</span>
              <el-tag :type="scope.row.awayWinChange > 0 ? 'danger' : 'success'" size="small">
                {{ scope.row.awayWinChange > 0 ? '↑' : '↓' }}{{ Math.abs(scope.row.awayWinChange) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="returnRate" label="返还率" width="80" />
          <el-table-column prop="updateTime" label="更新时间" width="150" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="亚盘详情" name="asian">
        <el-table :data="asianOdds" border style="width: 100%">
          <el-table-column prop="company" label="公司" width="120" />
          <el-table-column prop="handicap" label="让球" width="100" />
          <el-table-column prop="upperOdds" label="上盘" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.upperOdds }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="lowerOdds" label="下盘" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.lowerOdds }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="waterLevel" label="水位" width="80">
            <template #default="scope">
              <el-progress :percentage="scope.row.waterLevel" :color="getWaterLevelColor(scope.row.waterLevel)" />
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" width="150" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="大小球" name="overunder">
        <el-table :data="overUnderOdds" border style="width: 100%">
          <el-table-column prop="company" label="公司" width="120" />
          <el-table-column prop="line" label="大小球线" width="100" />
          <el-table-column prop="overOdds" label="大球" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.overOdds }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="underOdds" label="小球" width="100">
            <template #default="scope">
              <span class="odds-value">{{ scope.row.underOdds }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="popularLine" label="热门线" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.popularLine ? 'success' : 'info'" size="small">
                {{ scope.row.popularLine ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" width="150" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="赔率分析" name="analysis">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card header="赔率分布">
              <div ref="distributionChart" class="mini-chart" style="height: 250px;"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card header="市场热度">
              <div ref="heatmapChart" class="mini-chart" style="height: 250px;"></div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card header="AI分析建议" style="margin-top: 20px;">
          <el-alert
            v-for="analysis in aiAnalysis"
            :key="analysis.id"
            :title="analysis.title"
            :type="analysis.type"
            :description="analysis.description"
            show-icon
            class="analysis-alert"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 操作按钮 -->
    <div class="detail-actions">
      <el-button @click="handleCompare">赔率对比</el-button>
      <el-button type="primary" @click="handleRefresh">刷新赔率</el-button>
      <el-button type="success" @click="handleExport">导出赔率</el-button>
      <el-button type="warning" @click="handleAlert">设置预警</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  oddsData: {
    type: Object,
    default: null
  }
})

// 响应式数据
const activeTab = ref('european')
const oddsChart = ref(null)
const distributionChart = ref(null)
const heatmapChart = ref(null)

// 欧洲赔率数据
const europeanOdds = ref([])

// 亚洲赔率数据
const asianOdds = ref([])

// 大小球数据
const overUnderOdds = ref([])

// AI分析数据
const aiAnalysis = ref([])

// 初始化赔率数据
onMounted(() => {
  if (props.oddsData) {
    initOddsData()
    initCharts()
  }
})

// 初始化赔率数据
const initOddsData = () => {
  // 模拟欧洲赔率数据
  europeanOdds.value = [
    { company: '威廉希尔', homeWin: 2.50, draw: 3.20, awayWin: 2.80, returnRate: 92.5, homeWinChange: 0.05, drawChange: -0.02, awayWinChange: 0.03, updateTime: '2024-01-15 14:30' },
    { company: '立博', homeWin: 2.45, draw: 3.25, awayWin: 2.85, returnRate: 93.1, homeWinChange: -0.02, drawChange: 0.01, awayWinChange: 0.04, updateTime: '2024-01-15 14:25' },
    { company: 'Bet365', homeWin: 2.55, draw: 3.15, awayWin: 2.75, returnRate: 92.8, homeWinChange: 0.08, drawChange: -0.05, awayWinChange: -0.01, updateTime: '2024-01-15 14:28' },
    { company: '澳门', homeWin: 2.48, draw: 3.22, awayWin: 2.82, returnRate: 92.9, homeWinChange: 0.01, drawChange: 0.00, awayWinChange: 0.02, updateTime: '2024-01-15 14:32' }
  ]
  
  // 模拟亚洲赔率数据
  asianOdds.value = [
    { company: '威廉希尔', handicap: '-0.25', upperOdds: 1.85, lowerOdds: 2.00, waterLevel: 65, updateTime: '2024-01-15 14:30' },
    { company: '立博', handicap: '-0.25', upperOdds: 1.88, lowerOdds: 1.98, waterLevel: 70, updateTime: '2024-01-15 14:25' },
    { company: 'Bet365', handicap: '-0.5', upperOdds: 1.90, lowerOdds: 1.95, waterLevel: 60, updateTime: '2024-01-15 14:28' },
    { company: '澳门', handicap: '-0.25', upperOdds: 1.86, lowerOdds: 1.99, waterLevel: 68, updateTime: '2024-01-15 14:32' }
  ]
  
  // 模拟大小球数据
  overUnderOdds.value = [
    { company: '威廉希尔', line: '2.5', overOdds: 1.85, underOdds: 1.95, popularLine: true, updateTime: '2024-01-15 14:30' },
    { company: '立博', line: '2.5', overOdds: 1.88, underOdds: 1.92, popularLine: true, updateTime: '2024-01-15 14:25' },
    { company: 'Bet365', line: '2/2.5', overOdds: 1.90, underOdds: 1.90, popularLine: false, updateTime: '2024-01-15 14:28' },
    { company: '澳门', line: '2.5', overOdds: 1.87, underOdds: 1.93, popularLine: true, updateTime: '2024-01-15 14:32' }
  ]
  
  // 模拟AI分析数据
  aiAnalysis.value = [
    { id: 1, title: '赔率趋势分析', type: 'info', description: '主胜赔率整体呈上升趋势，市场对主队信心增强。建议关注临场赔率变化。' },
    { id: 2, title: '价值投注机会', type: 'success', description: '发现Bet365平局赔率相对偏高，存在一定价值投注机会。' },
    { id: 3, title: '风险提示', type: 'warning', description: '多家公司同时下调客胜赔率，需警惕客队获胜可能性增加。' }
  ]
}

// 初始化图表
const initCharts = () => {
  nextTick(() => {
    initOddsTrendChart()
    initDistributionChart()
    initHeatmapChart()
  })
}

// 初始化赔率趋势图
const initOddsTrendChart = () => {
  if (!oddsChart.value) return
  
  const chart = echarts.init(oddsChart.value)
  const option = {
    title: {
      text: '赔率变化趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['主胜', '平局', '客胜'],
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00']
    },
    yAxis: {
      type: 'value',
      inverse: true
    },
    series: [
      {
        name: '主胜',
        type: 'line',
        data: [2.60, 2.58, 2.55, 2.52, 2.50, 2.48, 2.50],
        smooth: true,
        lineStyle: { color: '#67C23A' }
      },
      {
        name: '平局',
        type: 'line',
        data: [3.15, 3.18, 3.20, 3.22, 3.20, 3.25, 3.20],
        smooth: true,
        lineStyle: { color: '#E6A23C' }
      },
      {
        name: '客胜',
        type: 'line',
        data: [2.70, 2.75, 2.78, 2.80, 2.82, 2.78, 2.80],
        smooth: true,
        lineStyle: { color: '#F56C6C' }
      }
    ]
  }
  chart.setOption(option)
}

// 初始化分布图
const initDistributionChart = () => {
  if (!distributionChart.value) return
  
  const chart = echarts.init(distributionChart.value)
  const option = {
    title: {
      text: '赔率分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: [
          { value: 35, name: '主胜' },
          { value: 30, name: '平局' },
          { value: 35, name: '客胜' }
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
  chart.setOption(option)
}

// 初始化热力图
const initHeatmapChart = () => {
  if (!heatmapChart.value) return
  
  const chart = echarts.init(heatmapChart.value)
  const hours = ['09', '10', '11', '12', '13', '14', '15']
  const days = ['威廉希尔', '立博', 'Bet365', '澳门']
  const data = []
  
  for (let i = 0; i < hours.length; i++) {
    for (let j = 0; j < days.length; j++) {
      data.push([i, j, Math.floor(Math.random() * 100)])
    }
  }
  
  const option = {
    title: {
      text: '市场热度',
      left: 'center'
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      height: '50%',
      top: '15%'
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%'
    },
    series: [{
      name: '热度',
      type: 'heatmap',
      data: data,
      label: {
        show: true
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  chart.setOption(option)
}

// 获取水位颜色
const getWaterLevelColor = (level) => {
  if (level >= 70) return '#67C23A'
  if (level >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 事件处理
const handleCompare = () => {
  ElMessage.info('打开赔率对比功能')
}

const handleRefresh = () => {
  ElMessage.success('刷新赔率数据')
}

const handleExport = () => {
  ElMessage.info('导出赔率数据')
}

const handleAlert = () => {
  ElMessage.info('设置赔率预警')
}
</script>

<style scoped lang="scss">

.odds-detail {
  padding: 20px;

  .overview-card {
    margin-bottom: 20px;

    .metric-item {
      text-align: center;
      padding: 15px 0;

      .metric-label {
        font-size: 14px;
        color: #606266;
        margin-bottom: 8px;
      }

      .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;

        &.highlight {
          color: #409EFF;
        }
      }
    }
  }

  .chart-card {
    margin-bottom: 20px;
  }

  .detail-tabs {
    margin-bottom: 20px;
  }

  .odds-value {
    font-weight: bold;
    color: #409EFF;
  }

  .mini-chart {
    width: 100%;
  }

  .analysis-alert {
    margin-bottom: 15px;
  }

  .detail-actions {
    margin-top: 30px;
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }

  // 响应式设计
  @media (max-width: 768px) {
    padding: 10px;

    .overview-card .el-col {
      margin-bottom: 15px;
    }

    .detail-actions {
      .el-button {
        margin-bottom: 10px;
        width: 100%;
      }
    }
  }
}
</style>