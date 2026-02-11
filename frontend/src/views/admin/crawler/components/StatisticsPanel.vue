<template>
  <div class="statistics-panel">
    <el-card>
      <template #header>
        <div class="statistics-header">
          <el-icon><TrendCharts /></el-icon>
          <span>执行统计概览</span>
        </div>
      </template>
      
      <!-- 成功率图表 -->
      <div class="statistics-section">
        <div class="section-title">成功率分布</div>
        <div class="chart-container">
          <div class="chart-placeholder">
            <!-- 这里可以使用ECharts或Chart.js，暂时用占位符 -->
            <div class="pie-chart-placeholder">
              <div class="pie-chart">
                <div class="success-slice" :style="{ '--percentage': stats.successRate + '%' }"></div>
                <div class="failure-slice" :style="{ '--percentage': stats.failureRate + '%' }"></div>
              </div>
              <div class="pie-chart-legend">
                <div class="legend-item">
                  <span class="legend-color success"></span>
                  <span class="legend-label">成功: {{ stats.successRate }}%</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color failure"></span>
                  <span class="legend-label">失败: {{ stats.failureRate }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 关键指标 -->
      <div class="statistics-section">
        <div class="section-title">关键指标</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <div class="metric-item">
              <div class="metric-label">运行中任务</div>
              <div class="metric-value">{{ stats.runningTasks }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="metric-item">
              <div class="metric-label">今日执行数</div>
              <div class="metric-value">{{ stats.todayExecutions || 0 }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="metric-item">
              <div class="metric-label">平均耗时</div>
              <div class="metric-value">{{ stats.avgExecutionTime || 0 }}s</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="metric-item">
              <div class="metric-label">最长耗时</div>
              <div class="metric-value">{{ stats.maxExecutionTime || 0 }}s</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 问题分布 -->
      <div class="statistics-section">
        <div class="section-title">问题分布</div>
        <div class="issues-list">
          <div class="issue-item" v-for="issue in stats.topIssues" :key="issue.type">
            <div class="issue-type">{{ issue.type }}</div>
            <div class="issue-count">{{ issue.count }}次</div>
            <el-progress 
              :percentage="issue.percentage" 
              :stroke-width="8"
              :show-text="false"
              :color="getIssueColor(issue.type)"
            />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      successRate: 0,
      failureRate: 0,
      runningTasks: 0,
      todayExecutions: 0,
      avgExecutionTime: 0,
      maxExecutionTime: 0,
      topIssues: []
    })
  }
})

// 获取问题类型的颜色
const getIssueColor = (issueType) => {
  const colorMap = {
    '网络超时': '#E6A23C',
    '解析失败': '#F56C6C',
    '验证码': '#409EFF',
    '数据缺失': '#909399',
    '其他': '#67C23A'
  }
  return colorMap[issueType] || '#409EFF'
}
</script>

<style scoped>
.statistics-panel {
  height: 100%;
}

.statistics-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.statistics-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 12px;
  padding-left: 4px;
  border-left: 3px solid #409EFF;
}

.chart-container {
  background: #fafafa;
  border-radius: 6px;
  padding: 16px;
  min-height: 200px;
}

.pie-chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.pie-chart {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    #67C23A 0% calc(var(--percentage, 0%)),
    #F56C6C calc(var(--percentage, 0%)) 100%
  );
  position: relative;
}

.pie-chart-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.success {
  background-color: #67C23A;
}

.legend-color.failure {
  background-color: #F56C6C;
}

.legend-label {
  font-size: 12px;
  color: #606266;
}

.metric-item {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.issue-item {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
}

.issue-type {
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.issue-count {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}
</style>