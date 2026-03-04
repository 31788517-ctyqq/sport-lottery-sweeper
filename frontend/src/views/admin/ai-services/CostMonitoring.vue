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
        <el-col :xs="24" :sm="12" :md="6">
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
                    {{ Math.abs(costTrend).toFixed(1) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <i class="el-icon-data-analysis" />
              </div>
              <div class="stat-info">
                <div class="stat-label">总请求数</div>
                <div class="stat-value">{{ totalRequests.toLocaleString() }}</div>
                <div class="stat-change">
                  <i :class="requestTrend >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="requestTrend >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(requestTrend).toFixed(1) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
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
                    {{ Math.abs(responseTimeTrend).toFixed(1) }}%
                  </span>
                  <span class="compared-text">较上月</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <i class="el-icon-success-filled" />
              </div>
              <div class="stat-info">
                <div class="stat-label">成功率</div>
                <div class="stat-value">{{ successRate.toFixed(1) }}%</div>
                <div class="stat-change">
                  <i :class="successRateTrend >= 0 ? 'el-icon-top-right' : 'el-icon-bottom-right'" />
                  <span :class="successRateTrend >= 0 ? 'positive' : 'negative'">
                    {{ Math.abs(successRateTrend).toFixed(1) }}%
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
              <el-radio-button value="月">月</el-radio-button>
              <el-radio-button value="周">周</el-radio-button>
              <el-radio-button value="日">日</el-radio-button>
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
import { getLLMProvidersStats } from '@/api/llm-providers'

// 响应式数据
const dateRange = ref([])
const chartPeriod = ref('月')
const totalMonthlyCost = ref(0)
const totalRequests = ref(0)
const avgResponseTime = ref(0)
const successRate = ref(0)

// 趋势数据
const costTrend = ref(0)
const requestTrend = ref(0)
const responseTimeTrend = ref(0)
const successRateTrend = ref(0)

// 图表引用
const costChartRef = ref(null)
const providerCostChartRef = ref(null)
const serviceTypeChartRef = ref(null)

// 详细成本数据
const detailedCostData = ref([])

// 加载统计数据
const loadStatsData = async () => {
  try {
    const response = await getLLMProvidersStats()
    if (response.data) {
      const stats = response.data
      
      // 更新统计概览
      totalMonthlyCost.value = stats.monthly_cost || 0
      totalRequests.value = stats.total_requests || 0
      // 注意：后端目前没有提供avgResponseTime和successRate，使用模拟值
      avgResponseTime.value = 1.2 // 模拟平均响应时间
      successRate.value = 98.5 // 模拟成功率
      
      // 计算趋势（这里使用简单逻辑，实际应该从历史数据计算）
      costTrend.value = Math.random() * 10 - 5 // 随机趋势
      requestTrend.value = Math.random() * 10 - 3
      responseTimeTrend.value = -(Math.random() * 5) // 响应时间通常改善
      successRateTrend.value = Math.random() * 3
      
      // 构建详细数据（基于提供商统计）
      detailedCostData.value = []
      
      // 这里需要从后端获取更详细的按提供商的统计数据
      // 目前后端只提供汇总数据，所以使用模拟数据展示结构
      if (stats.type_stats) {
        Object.entries(stats.type_stats).forEach(([providerType, count]) => {
          detailedCostData.value.push({
            date: new Date().toISOString().split('T')[0],
            provider: providerType.toLowerCase(),
            serviceType: '远程',
            model: providerType === 'OPENAI' ? 'gpt-4' : 
                   providerType === 'ZHIPUAI' ? 'glm-4' :
                   providerType === 'ALIBABA' ? 'qwen-max' : 'unknown',
            requests: Math.floor(Math.random() * 1000) + 500,
            cost: stats.monthly_cost * (Math.random() * 0.3 + 0.1),
            avgResponseTime: 0.8 + Math.random() * 1.5,
            successRate: 95 + Math.random() * 5
          })
        })
      }
      
      // 如果没有类型统计，使用默认数据
      if (detailedCostData.value.length === 0) {
        detailedCostData.value = [
          { date: new Date().toISOString().split('T')[0], provider: 'zhipuai', serviceType: '远程', model: 'glm-4', requests: 1200, cost: totalMonthlyCost.value * 0.6, avgResponseTime: 1.25, successRate: 98.5 },
          { date: new Date().toISOString().split('T')[0], provider: 'alibaba', serviceType: '远程', model: 'qwen-max', requests: 800, cost: totalMonthlyCost.value * 0.4, avgResponseTime: 1.50, successRate: 97.8 }
        ]
      }
      
      updateCharts()
      ElMessage.success('成本统计数据加载成功')
    }
  } catch (error) {
    console.error('加载成本统计数据失败:', error)
    ElMessage.error('加载成本统计数据失败，请检查网络连接')
    
    // 使用模拟数据作为备选
    totalMonthlyCost.value = 24.50
    totalRequests.value = 2000
    avgResponseTime.value = 1.2
    successRate.value = 98.5
    costTrend.value = 5.2
    requestTrend.value = 8.7
    responseTimeTrend.value = -2.1
    successRateTrend.value = 1.5
    
    detailedCostData.value = [
      { date: '2026-02-10', provider: 'zhipuai', serviceType: '远程', model: 'glm-4', requests: 1200, cost: 15.30, avgResponseTime: 1.25, successRate: 98.5 },
      { date: '2026-02-10', provider: 'alibaba', serviceType: '远程', model: 'qwen-max', requests: 800, cost: 9.20, avgResponseTime: 1.50, successRate: 97.8 }
    ]
    
    updateCharts()
  }
}

// 方法
const refreshData = () => {
  loadStatsData()
}

const onDateRangeChange = (val) => {
  console.log('日期范围变更:', val)
  // TODO: 实现按日期范围过滤的API调用
  updateCharts()
}

const exportData = () => {
  // 导出CSV格式数据
  const headers = ['日期', '提供商', '服务类型', '模型', '请求数', '成本(¥)', '平均响应(s)', '成功率(%)']
  const rows = detailedCostData.value.map(item => [
    item.date,
    item.provider,
    item.serviceType,
    item.model,
    item.requests,
    item.cost.toFixed(2),
    item.avgResponseTime.toFixed(2),
    item.successRate
  ])
  
  const csvContent = [headers, ...rows].map(e => e.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `ai-cost-data-${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('数据导出成功')
}

const getProviderTagType = (provider) => {
  const types = {
    openai: 'primary',
    zhipuai: 'success',
    alibaba: 'warning',
    google: 'info',
    '本地服务': 'danger'
  }
  return types[provider.toLowerCase()] || 'info'
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
          stack: 'Total',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [120, 132, 101, 134, 90, 230, 210]
        },
        {
          name: '本地服务',
          type: 'line',
          stack: 'Total',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [220, 182, 191, 234, 290, 330, 310]
        },
        {
          name: '总计',
          type: 'line',
          stack: 'Total',
          areaStyle: {},
          emphasis: {
            focus: 'series'
          },
          data: [340, 314, 292, 368, 380, 560, 520]
        }
      ]
    })

    // 添加防抖处理的resize监听器
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
  }
  
  // 提供商成本分布图
  if (providerCostChartRef.value) {
    const providerChart = echarts.init(providerCostChartRef.value)
    const providerData = detailedCostData.value.map(item => ({
      name: item.provider,
      value: item.cost
    }))
    
    providerChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: '提供商成本分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: providerData.length > 0 ? providerData : [
            { name: '智谱AI', value: 15.30 },
            { name: '通义千问', value: 9.20 }
          ]
        }
      ]
    })
    window.addEventListener('resize', () => providerChart.resize())
  }
  
  // 服务类型成本分布图
  if (serviceTypeChartRef.value) {
    const serviceChart = echarts.init(serviceTypeChartRef.value)
    serviceChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: '服务类型成本分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { name: '远程', value: totalMonthlyCost.value },
            { name: '本地', value: 0 }
          ]
        }
      ]
    })
    window.addEventListener('resize', () => serviceChart.resize())
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStatsData()
})
</script>

<style scoped>
.cost-monitoring {
  padding: 20px;
}

.card-container {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
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
  flex-wrap: wrap;
}

/* 修复：移除固定高度，使用最小高度和自动调整 */
.stat-card {
  min-height: 120px;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  /* 确保内容不会溢出 */
  overflow: visible !important;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 15px;
  /* 确保内容区域不会产生滚动条 */
  overflow: hidden;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 12px;
  font-size: 20px;
  flex-shrink: 0;
}

.bg-blue { background: #409eff; }
.bg-green { background: #67c23a; }
.bg-orange { background: #e6a23c; }
.bg-purple { background: #9013fe; }

.stat-info {
  flex: 1;
  min-width: 0;
  /* 防止文本溢出 */
  word-break: break-word;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 2px 0;
  /* 确保大数字不会换行导致布局问题 */
  white-space: nowrap;
}

.stat-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}

.compared-text {
  color: #909399;
  margin-left: 4px;
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
  min-height: 300px;
}

.data-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 添加响应式设计 */
@media (max-width: 768px) {
  .stat-card {
    min-height: 100px;
    margin-bottom: 10px;
  }
  
  .stat-content {
    padding: 10px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .el-col {
    margin-bottom: 10px;
  }
}
</style>