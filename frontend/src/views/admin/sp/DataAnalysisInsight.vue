<template>
  <div class="data-analysis-insight">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <h2>数据分析与洞察</h2>
        <p class="subtitle">深度分析SP数据，发现规律和趋势</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button type="success" @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 分析维度选择 -->
    <el-card class="dimension-card">
      <template #header>
        <span>分析维度</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="分析类型:">
            <el-select v-model="analysisParams.analysis_type" placeholder="请选择分析类型" @change="loadAnalysisData">
              <el-option label="SP分布统计" value="distribution" />
              <el-option label="SP变动分析" value="movement" />
              <el-option label="公司对比分析" value="comparison" />
              <el-option label="赛果关联分析" value="correlation" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="时间范围:">
            <el-date-picker
              v-model="analysisParams.date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="loadAnalysisData"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="联赛筛选:">
            <el-select v-model="analysisParams.leagues" placeholder="请选择联赛" multiple collapse-tags @change="loadAnalysisData">
              <el-option label="全部联赛" value="" />
              <el-option label="英超" value="Premier League" />
              <el-option label="西甲" value="La Liga" />
              <el-option label="德甲" value="Bundesliga" />
              <el-option label="意甲" value="Serie A" />
              <el-option label="法甲" value="Ligue 1" />
              <el-option label="中超" value="Chinese Super League" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="盘口类型:">
            <el-select v-model="analysisParams.handicap_types" placeholder="请选择盘口类型" multiple collapse-tags @change="loadAnalysisData">
              <el-option label="全部" value="" />
              <el-option label="不让球" value="no_handicap" />
              <el-option label="让球" value="handicap" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 分析内容区域 -->
    <div class="analysis-content">
      <!-- SP分布统计 -->
      <el-row :gutter="20" v-if="analysisParams.analysis_type === 'distribution'">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>SP值分布直方图</span>
            </template>
            <div ref="distributionChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="stats-card">
            <template #header>
              <span>分布统计摘要</span>
            </template>
            <div v-if="distributionStats" class="stats-content">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="总记录数">{{ distributionStats.total_records }}</el-descriptions-item>
                <el-descriptions-item label="平均值">{{ distributionStats.average_value }}</el-descriptions-item>
                <el-descriptions-item label="中位数">{{ distributionStats.median_value }}</el-descriptions-item>
                <el-descriptions-item label="标准差">{{ distributionStats.std_deviation }}</el-descriptions-item>
                <el-descriptions-item label="最小值">{{ distributionStats.min_value }}</el-descriptions-item>
                <el-descriptions-item label="最大值">{{ distributionStats.max_value }}</el-descriptions-item>
              </el-descriptions>
              
              <h4 style="margin: 20px 0 10px 0;">常见SP值区间:</h4>
              <div class="common-ranges">
                <el-tag v-for="range in distributionStats.common_ranges" :key="range.range" class="range-tag">
                  {{ range.range }}: {{ range.count }}条 ({{ range.percentage }}%)
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- SP变动分析 -->
      <el-row :gutter="20" v-if="analysisParams.analysis_type === 'movement'">
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <span>SP值变动趋势</span>
            </template>
            <div ref="movementChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="insight-card">
            <template #header>
              <span>变动洞察</span>
            </template>
            <div v-if="movementInsights" class="insight-content">
              <div class="insight-item">
                <h4>📈 最大涨幅</h4>
                <p>{{ movementInsights.largest_increase.sp_value_change }} ({{ movementInsights.largest_increase.match_info }})</p>
              </div>
              <div class="insight-item">
                <h4>📉 最大跌幅</h4>
                <p>{{ movementInsights.largest_decrease.sp_value_change }} ({{ movementInsights.largest_decrease.match_info }})</p>
              </div>
              <div class="insight-item">
                <h4>⚡ 高频变动</h4>
                <p>{{ movementInsights.high_frequency_matches.length }}场比赛SP值变动超过5次</p>
              </div>
              <div class="insight-item">
                <h4>🔍 异常模式</h4>
                <p>{{ movementInsights.anomalous_patterns.pattern_description }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 公司对比分析 -->
      <el-row :gutter="20" v-if="analysisParams.analysis_type === 'comparison'">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>各公司SP值对比</span>
            </template>
            <div ref="comparisonChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="ranking-card">
            <template #header>
              <span>公司排名</span>
            </template>
            <div v-if="companyRanking" class="ranking-content">
              <el-table :data="companyRanking.companies" style="width: 100%">
                <el-table-column prop="rank" label="排名" width="60">
                  <template #default="scope">
                    <el-tag :type="scope.row.rank <= 3 ? 'success' : 'info'">{{ scope.row.rank }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="company_name" label="公司名称" />
                <el-table-column prop="avg_accuracy" label="平均准确率" width="100">
                  <template #default="scope">
                    {{ (scope.row.avg_accuracy * 100).toFixed(1) }}%
                  </template>
                </el-table-column>
                <el-table-column prop="avg_deviation" label="平均偏差" width="100" />
              </el-table>
              
              <div class="ranking-summary">
                <h4>关键发现:</h4>
                <ul>
                  <li v-for="finding in companyRanking.key_findings" :key="finding">{{ finding }}</li>
                </ul>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 赛果关联分析 -->
      <el-row :gutter="20" v-if="analysisParams.analysis_type === 'correlation'">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>SP值与赛果关联度</span>
            </template>
            <div ref="correlationChart" style="height: 400px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="correlation-insight-card">
            <template #header>
              <span>关联分析洞察</span>
            </template>
            <div v-if="correlationInsights" class="correlation-content">
              <div class="correlation-score">
                <el-progress 
                  type="dashboard" 
                  :percentage="correlationInsights.correlation_coefficient * 100"
                  :color="getCorrelationColor(correlationInsights.correlation_coefficient)"
                >
                  <template #default>
                    <span class="progress-text">{{ (correlationInsights.correlation_coefficient * 100).toFixed(1) }}%</span>
                  </template>
                </el-progress>
                <p class="score-label">相关系数</p>
              </div>
              
              <div class="prediction-rules">
                <h4>预测规律:</h4>
                <div v-for="rule in correlationInsights.prediction_rules" :key="rule.rule" class="rule-item">
                  <el-tag :type="rule.confidence > 0.7 ? 'success' : 'warning'">{{ rule.rule }}</el-tag>
                  <span class="confidence">置信度: {{ (rule.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>
              
              <div class="sample-info">
                <h4>样本信息:</h4>
                <p>样本数量: {{ correlationInsights.sample_size }}</p>
                <p>置信水平: {{ (correlationInsights.confidence_level * 100).toFixed(1) }}%</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 智能推荐 -->
    <el-card class="recommendation-card">
      <template #header>
        <span>智能推荐</span>
      </template>
      <div v-if="recommendations.length > 0" class="recommendations-content">
        <el-alert
          v-for="(rec, index) in recommendations"
          :key="index"
          :title="rec.title"
          :description="rec.description"
          :type="rec.type"
          show-icon
          :closable="false"
          class="recommendation-item"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getSPDistributionAnalysis, getSPMovementAnalysis, getCompanyComparisonAnalysis, getSPResultCorrelationAnalysis } from '@/api/sp'

// 响应式数据
const analysisParams = reactive({
  analysis_type: 'distribution',
  date_range: [],
  leagues: [],
  handicap_types: []
})

const distributionStats = ref(null)
const movementInsights = ref(null)
const companyRanking = ref(null)
const correlationInsights = ref(null)
const recommendations = ref([])

// 图表相关
const distributionChart = ref(null)
const movementChart = ref(null)
const comparisonChart = ref(null)
const correlationChart = ref(null)
let charts = {}

// 方法
const loadAnalysisData = async () => {
  try {
    let response
    switch (analysisParams.analysis_type) {
      case 'distribution':
        response = await getSPDistributionAnalysis(formatAnalysisParams())
        distributionStats.value = response.data.statistics
        await nextTick()
        renderDistributionChart(response.data.distribution_data)
        break
      case 'movement':
        response = await getSPMovementAnalysis(formatAnalysisParams())
        movementInsights.value = response.data.insights
        await nextTick()
        renderMovementChart(response.data.movement_data)
        break
      case 'comparison':
        response = await getCompanyComparisonAnalysis(formatAnalysisParams())
        companyRanking.value = response.data.ranking
        await nextTick()
        renderComparisonChart(response.data.comparison_data)
        break
      case 'correlation':
        response = await getSPResultCorrelationAnalysis(formatAnalysisParams())
        correlationInsights.value = response.data.correlation_analysis
        recommendations.value = response.data.recommendations
        await nextTick()
        renderCorrelationChart(response.data.correlation_data)
        break
    }
  } catch (error) {
    ElMessage.error('加载分析数据失败')
  }
}

const formatAnalysisParams = () => {
  const params = { ...analysisParams }
  if (params.date_range && params.date_range.length === 2) {
    params.date_from = params.date_range[0]
    params.date_to = params.date_range[1]
    delete params.date_range
  }
  return params
}

const refreshData = () => {
  loadAnalysisData()
  ElMessage.success('数据已刷新')
}

const exportReport = () => {
  ElMessage.info('报告导出功能开发中...')
}

// 图表渲染方法
const renderDistributionChart = (data) => {
  if (!distributionChart.value) return
  
  if (charts.distribution) {
    charts.distribution.dispose()
  }
  
  charts.distribution = echarts.init(distributionChart.value)
  
  const option = {
    title: {
      text: 'SP值分布统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.bins.map(item => item.range)
    },
    yAxis: {
      type: 'value',
      name: '频次'
    },
    series: [{
      name: '频次',
      type: 'bar',
      data: data.bins.map(item => item.count),
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  
  charts.distribution.setOption(option)
}

const renderMovementChart = (data) => {
  if (!movementChart.value) return
  
  if (charts.movement) {
    charts.movement.dispose()
  }
  
  charts.movement = echarts.init(movementChart.value)
  
  const option = {
    title: {
      text: 'SP值变动趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['SP值', '变动幅度'],
      top: '10%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.dates
    },
    yAxis: [
      {
        type: 'value',
        name: 'SP值'
      },
      {
        type: 'value',
        name: '变动幅度'
      }
    ],
    series: [
      {
        name: 'SP值',
        type: 'line',
        data: data.sp_values,
        smooth: true
      },
      {
        name: '变动幅度',
        type: 'bar',
        yAxisIndex: 1,
        data: data.changes
      }
    ]
  }
  
  charts.movement.setOption(option)
}

const renderComparisonChart = (data) => {
  if (!comparisonChart.value) return
  
  if (charts.comparison) {
    charts.comparison.dispose()
  }
  
  charts.comparison = echarts.init(comparisonChart.value)
  
  const option = {
    title: {
      text: '各公司SP值对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: data.companies,
      top: '10%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.match_ids
    },
    yAxis: {
      type: 'value',
      name: 'SP值'
    },
    series: data.companies.map((company, index) => ({
      name: company,
      type: 'line',
      data: data.values[index],
      smooth: true
    }))
  }
  
  charts.comparison.setOption(option)
}

const renderCorrelationChart = (data) => {
  if (!correlationChart.value) return
  
  if (charts.correlation) {
    charts.correlation.dispose()
  }
  
  charts.correlation = echarts.init(correlationChart.value)
  
  const option = {
    title: {
      text: 'SP值与赛果关联分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'point'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'SP值'
    },
    yAxis: {
      type: 'value',
      name: '赛果相关性'
    },
    series: [{
      name: '数据点',
      type: 'scatter',
      data: data.scatter_data,
      symbolSize: 8
    }]
  }
  
  charts.correlation.setOption(option)
}

// 辅助方法
const getCorrelationColor = (correlation) => {
  if (correlation >= 0.7) return '#67C23A'
  if (correlation >= 0.4) return '#E6A23C'
  return '#F56C6C'
}

// 生命周期
onMounted(() => {
  loadAnalysisData()
  
  // 监听窗口大小变化，调整图表
  window.addEventListener('resize', () => {
    Object.values(charts).forEach(chart => {
      if (chart) chart.resize()
    })
  })
})
</script>

<style scoped>
.data-analysis-insight {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.dimension-card {
  margin-bottom: 20px;
}

.analysis-content {
  margin-bottom: 20px;
}

.chart-card, .stats-card, .insight-card, .ranking-card, .correlation-insight-card {
  margin-bottom: 20px;
}

.stats-content {
  padding: 10px 0;
}

.common-ranges {
  margin-top: 15px;
}

.range-tag {
  margin: 2px;
}

.insight-content {
  padding: 10px 0;
}

.insight-item {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.insight-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.insight-item p {
  margin: 0;
  color: #606266;
}

.ranking-content {
  padding: 10px 0;
}

.ranking-summary {
  margin-top: 20px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 6px;
}

.ranking-summary h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.ranking-summary ul {
  margin: 0;
  padding-left: 20px;
}

.ranking-summary li {
  margin-bottom: 5px;
  color: #606266;
}

.correlation-content {
  padding: 20px 0;
  text-align: center;
}

.correlation-score {
  margin-bottom: 30px;
}

.progress-text {
  font-size: 18px;
  font-weight: bold;
}

.score-label {
  margin: 10px 0 0 0;
  color: #909399;
}

.prediction-rules {
  margin-bottom: 30px;
}

.prediction-rules h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.confidence {
  font-size: 12px;
  color: #909399;
}

.sample-info {
  text-align: left;
}

.sample-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.sample-info p {
  margin: 5px 0;
  color: #606266;
}

.recommendation-card {
  margin-bottom: 20px;
}

.recommendations-content {
  padding: 10px 0;
}

.recommendation-item {
  margin-bottom: 10px;
}

:deep(.el-descriptions) {
  margin: 15px 0;
}

:deep(.el-progress--dashboard) {
  display: inline-block;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .analysis-content .el-row {
    flex-direction: column;
  }
  
  .analysis-content .el-col {
    width: 100%;
    margin-bottom: 20px;
  }
}
</style>