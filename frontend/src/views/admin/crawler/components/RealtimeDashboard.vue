<template>
  <div class="realtime-dashboard">
    <el-row :gutter="20">
      <!-- 当前运行任务数 -->
      <el-col :span="4">
        <el-card class="metric-card" shadow="hover">
          <template #header>
            <div class="metric-header">
              <el-icon><Clock /></el-icon>
              <span class="metric-title">运行中任务</span>
            </div>
          </template>
          <div class="metric-content">
            <div class="metric-value" :class="{ 'warning': metrics.runningTasks > 10 }">
              {{ metrics.runningTasks }}
            </div>
            <div class="metric-label">当前执行中</div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 今日任务总数 -->
      <el-col :span="4">
        <el-card class="metric-card" shadow="hover">
          <template #header>
            <div class="metric-header">
              <el-icon><Calendar /></el-icon>
              <span class="metric-title">今日任务</span>
            </div>
          </template>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.todayTotal }}</div>
            <div class="metric-label">今日总计</div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 今日成功任务数 -->
      <el-col :span="4">
        <el-card class="metric-card" shadow="hover">
          <template #header>
            <div class="metric-header">
              <el-icon><Check /></el-icon>
              <span class="metric-title">今日成功</span>
            </div>
          </template>
          <div class="metric-content">
            <div class="metric-value success">{{ metrics.todaySuccess }}</div>
            <div class="metric-label">成功执行</div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 成功率 -->
      <el-col :span="4">
        <el-card class="metric-card" shadow="hover">
          <template #header>
            <div class="metric-header">
              <el-icon><TrendCharts /></el-icon>
              <span class="metric-title">成功率</span>
            </div>
          </template>
          <div class="metric-content">
            <div class="metric-value" :class="{ 'danger': metrics.successRate < 90 }">
              {{ metrics.successRate.toFixed(2) }}%
            </div>
            <div class="metric-label">今日成功率</div>
            <el-progress 
              :percentage="metrics.successRate" 
              :color="getProgressColor(metrics.successRate)"
              :show-text="false"
            />
          </div>
        </el-card>
      </el-col>
      
      <!-- 平均耗时 -->
      <el-col :span="4">
        <el-card class="metric-card" shadow="hover">
          <template #header>
            <div class="metric-header">
              <el-icon><Timer /></el-icon>
              <span class="metric-title">平均耗时</span>
            </div>
          </template>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.avgDuration.toFixed(2) }}s</div>
            <div class="metric-label">平均执行时间</div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 最近一小时错误率 -->
      <el-col :span="4">
        <el-card class="metric-card" shadow="hover">
          <template #header>
            <div class="metric-header">
              <el-icon><Warning /></el-icon>
              <span class="metric-title">错误率</span>
            </div>
          </template>
          <div class="metric-content">
            <div class="metric-value" :class="{ 'danger': metrics.hourlyErrorRate > 5 }">
              {{ metrics.hourlyErrorRate.toFixed(2) }}%
            </div>
            <div class="metric-label">最近一小时</div>
            <el-progress 
              :percentage="metrics.hourlyErrorRate" 
              :color="getErrorProgressColor(metrics.hourlyErrorRate)"
              :show-text="false"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  Clock,
  Calendar,
  Check,
  TrendCharts,
  Timer,
  Warning
} from '@element-plus/icons-vue'

const props = defineProps({
  metrics: {
    type: Object,
    required: true,
    default: () => ({
      runningTasks: 0,
      todayTotal: 0,
      todaySuccess: 0,
      successRate: 0,
      avgDuration: 0,
      hourlyErrorRate: 0
    })
  }
})

const getProgressColor = (percentage) => {
  if (percentage >= 95) return '#67C23A'
  if (percentage >= 85) return '#E6A23C'
  return '#F56C6C'
}

const getErrorProgressColor = (percentage) => {
  if (percentage <= 5) return '#67C23A'
  if (percentage <= 10) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style scoped>
.realtime-dashboard {
  margin-bottom: 20px;
}

.metric-card {
  height: 140px;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-header .el-icon {
  font-size: 18px;
  color: #409EFF;
}

.metric-title {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.metric-content {
  padding: 10px 0;
  text-align: center;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.metric-value.success {
  color: #67C23A;
}

.metric-value.warning {
  color: #E6A23C;
}

.metric-value.danger {
  color: #F56C6C;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
}

::v-deep .el-progress {
  margin-top: 10px;
}
</style>