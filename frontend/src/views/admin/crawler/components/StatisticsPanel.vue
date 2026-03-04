<template>
  <div class="statistics-panel">
    <el-card>
      <template #header>
        <div class="statistics-header">
          <el-icon><TrendCharts /></el-icon>
          <span>执行统计概览</span>
        </div>
      </template>

      <div class="statistics-section">
        <div class="section-title">成功率分布</div>
        <div class="chart-container">
          <div class="pie-chart-placeholder">
            <div class="pie-chart" :style="{ '--percentage': `${stats.successRate}%` }" />
            <div class="pie-chart-legend">
              <div class="legend-item">
                <span class="legend-color success" />
                <span class="legend-label">成功: {{ stats.successRate }}%</span>
              </div>
              <div class="legend-item">
                <span class="legend-color failure" />
                <span class="legend-label">失败: {{ stats.failureRate }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="statistics-section">
        <div class="section-title">关键指标</div>
        <el-row :gutter="10">
          <el-col :span="12"><div class="metric-item"><div class="metric-label">运行中任务</div><div class="metric-value">{{ stats.runningTasks }}</div></div></el-col>
          <el-col :span="12"><div class="metric-item"><div class="metric-label">今日执行数</div><div class="metric-value">{{ stats.todayExecutions || 0 }}</div></div></el-col>
          <el-col :span="12"><div class="metric-item"><div class="metric-label">平均耗时</div><div class="metric-value">{{ stats.avgExecutionTime || 0 }}s</div></div></el-col>
          <el-col :span="12"><div class="metric-item"><div class="metric-label">最长耗时</div><div class="metric-value">{{ stats.maxExecutionTime || 0 }}s</div></div></el-col>
        </el-row>
      </div>

      <div class="statistics-section">
        <div class="section-title">问题分布</div>
        <div class="issues-list">
          <div class="issue-item" v-for="issue in stats.topIssues" :key="issue.type">
            <div class="issue-type">{{ issue.type }}</div>
            <div class="issue-count">{{ issue.count }} 次</div>
            <el-progress
              :percentage="issue.percentage"
              :stroke-width="8"
              :show-text="false"
              :color="getIssueColor(issue.type)"
            />
          </div>
          <el-empty v-if="!stats.topIssues || stats.topIssues.length === 0" description="暂无问题数据" :image-size="60" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { TrendCharts } from '@element-plus/icons-vue'

defineProps({
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

const getIssueColor = (issueType) => {
  const colorMap = {
    网络超时: '#e6a23c',
    解析失败: '#f56c6c',
    验证码: '#409eff',
    数据缺失: '#909399',
    其他: '#67c23a'
  }
  return colorMap[issueType] || '#409eff'
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
  border-left: 3px solid #409eff;
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
  background: conic-gradient(#67c23a 0% var(--percentage, 0%), #f56c6c var(--percentage, 0%) 100%);
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
  background-color: #67c23a;
}

.legend-color.failure {
  background-color: #f56c6c;
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
