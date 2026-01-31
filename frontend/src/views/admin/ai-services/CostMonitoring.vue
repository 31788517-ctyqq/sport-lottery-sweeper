<template>
  <div class="cost-monitoring">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>💰 成本监控</h3>
            <p class="subtitle">AI服务月度成本趋势及关键指标统计</p>
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
            <el-button type="primary" @click="refreshData">刷新数据</el-button>
          </div>
        </div>
      </template>

      <!-- 统计概览 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <i class="el-icon-wallet" />
              </div>
              <div class="stat-info">
                <div class="stat-label">本月总成本</div>
                <div class="stat-value">¥{{ totalMonthlyCost.toFixed(2) }}</div>
                <div class="stat-change">
                  <i :class="costTrend >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="costTrend >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(costTrend) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <i class="el-icon-data-analysis" />
              </div>
              <div class="stat-info">
                <div class="stat-label">总请求数</div>
                <div class="stat-value">{{ totalRequests }}</div>
                <div class="stat-change">
                  <i :class="requestTrend >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="requestTrend >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(requestTrend) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <i class="el-icon-timer" />
              </div>
              <div class="stat-info">
                <div class="stat-label">平均响应时间</div>
                <div class="stat-value">{{ avgResponseTime.toFixed(2) }}s</div>
                <div class="stat-change">
                  <i :class="responseTimeTrend >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="responseTimeTrend >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(responseTimeTrend) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <i class="el-icon-success-filled" />
              </div>
              <div class="stat-info">
                <div class="stat-label">成功率</div>
                <div class="stat-value">{{ successRate }}%</div>
                <div class="stat-change">
                  <i :class="successRateTrend >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="successRateTrend >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(successRateTrend) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 成本趋势图表 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span>📈 AI服务月度成本趋势</span>
            <el-radio-group v-model="chartPeriod" size="small">
              <el-radio-button label="月">月</el-radio-button>
              <el-radio-button label="周">周</el-radio-button>
              <el-radio-button label="日">日</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="costChartRef" class="chart-container" style="height: 400px;" />
      </el-card>

      <!-- 成本分布图表 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>📊 按提供商成本分布</span>
            </template>
            <div ref="providerCostChartRef" class="chart-container" style="height: 300px;" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>📊 按服务类型成本分布</span>
            </template>
            <div ref="serviceTypeChartRef" class="chart-container" style="height: 300px;" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细数据表格 -->
      <el-card class="data-table-card" style="margin-top: 20px;">
        <template #header>
          <div class="table-header">
            <span>📋 详细成本数据</span>
            <el-button type="primary" @click="exportData">导出数据</el-button>
          </div>
        </template>
        <el-table :data="detailedCostData" style="width: 100%" stripe>
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="provider" label="提供商" width="120">
            <template #default="scope">
              <el-tag :type="getProviderTagType(scope.row.provider)">
                {{ scope.row.provider }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="serviceType" label="服务类型" width="120">
            <template #default="scope">
              <el-tag :type="getServiceTypeTag(scope.row.serviceType)">
                {{ scope.row.serviceType }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="model" label="模型" width="150" />
          <el-table-column prop="requests" label="请求数" width="100" />
          <el-table-column prop="cost" label="成本(¥)" width="120">
            <template #default="scope">
              {{ scope.row.cost.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="avgResponseTime" label="平均响应(s)" width="130">
            <template #default="scope">
              {{ scope.row.avgResponseTime.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="successRate" label="成功率(%)" width="120">
            <template #default="scope">
              {{ scope.row.successRate }}%
            </template>
          </el-table-column>
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
const chartPeriod = ref('月')
const totalMonthlyCost = ref(0)
const totalRequests = ref(0)
const avgResponseTime = ref(0)
const successRate = ref(0)

// 趋势数据
const costTrend = ref(5.2)
const requestTrend = ref(8.7)
const responseTimeTrend = ref(-2.1)
const successRateTrend = ref(1.5)

// 图表引用
const costChartRef = ref(null)
const providerCostChartRef = ref(null)
const serviceTypeChartRef = ref(null)

// 详细成本数据
const detailedCostData = ref([
  { date: '2026-01-01', provider: 'openai', serviceType: '远程', model: 'gpt-4', requests: 1200, cost: 24.50, avgResponseTime: 1.25, successRate: 98.5 },
  { date: '2026-01-01', provider: 'anthropic', serviceType: '远程', model: 'claude-3', requests: 980, cost: 12.30, avgResponseTime: 1.50, successRate: 97.8 },
  { date: '2026-01-01', provider: '本地服务', serviceType: '本地', model: 'llama2', requests: 2400, cost: 0.00, avgResponseTime: 0.85, successRate: 96.2 },
  { date: '2026-01-02', provider: 'google', serviceType: '远程', model: 'gemini-pro', requests: 750, cost: 8.70, avgResponseTime: 1.80, successRate: 96.5 },
  { date: '2026-01-02', provider: '本地服务', serviceType: '本地', model: 'mistral', requests: 1800, cost: 0.00, avgResponseTime: 0.75, successRate: 97.1 },
  { date: '2026-01-03', provider: 'openai', serviceType: '远程', model: 'gpt-3.5', requests: 1500, cost: 12.20, avgResponseTime: 0.95, successRate: 98.2 },
  { date: '2026-01-03', provider: '本地服务', serviceType: '本地', model: 'phi2', requests: 2100, cost: 0.00, avgResponseTime: 0.65, successRate: 97.8 }
])

// 方法
const refreshData = () => {
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

const getProviderTagType = (provider) => {
  const types = {
    openai: 'primary',
    anthropic: 'success',
    google: 'warning',
    azure: 'info',
    '本地服务': 'danger'
  }
  return types[provider] || 'info'
}

const getServiceTypeTag = (type) => {
  return type === '本地' ? 'danger' : 'primary'
}

// 更新图表
const updateCharts = async () => {
  await nextTick()
  
  // 成本趋势图
  if (costChartRef.value) {
    const chart = echarts.init(costChartRef.value)
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
        data: ['远程服务', '本地服务', '总计']
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
          data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '成本 (¥)',
          axisLabel: {
            formatter: '¥{value}'
          }
        }
      ],
      series: [
        {
          name: '远程服务',
          type: 'line',
          stack: '总量',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [220, 182, 191, 234, 290, 330, 310]
        },
        {
          name: '本地服务',
          type: 'line',
          stack: '总量',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [150, 232, 201, 154, 190, 330, 410]
        },
        {
          name: '总计',
          type: 'line',
          lineStyle: {
            type: 'dashed'
          },
          emphasis: {
            focus: 'series'
          },
          data: [370, 414, 392, 388, 480, 660, 720]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 提供商成本分布图（饼状图）
  if (providerCostChartRef.value) {
    const chart = echarts.init(providerCostChartRef.value)
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
          name: '成本分布',
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
            { value: 45, name: 'OpenAI' },
            { value: 25, name: 'Anthropic' },
            { value: 15, name: 'Google' },
            { value: 10, name: 'Azure' },
            { value: 5, name: '本地服务' }
          ]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }

  // 服务类型成本分布图
  if (serviceTypeChartRef.value) {
    const chart = echarts.init(serviceTypeChartRef.value)
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
          name: '服务类型分布',
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
            { value: 95, name: '远程服务' },
            { value: 5, name: '本地服务' }
          ]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }
}

onMounted(() => {
  // 初始化统计数据
  totalMonthlyCost.value = 55.70
  totalRequests.value = 8730
  avgResponseTime.value = 1.12
  successRate.value = 97.4
  
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

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

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

.bg-blue { background: #409eff; }
.bg-green { background: #67c23a; }
.bg-orange { background: #e6a23c; }
.bg-purple { background: #9013fe; }

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