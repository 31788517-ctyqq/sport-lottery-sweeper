<template>
  <div class="risk-control-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>风险控制管理</h3>
            <p class="subtitle">设置和管理风险控制参数，保障系统安全和合规运营</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="saveConfig" icon="Check">保存配置</el-button>
            <el-button @click="loadConfig" :loading="loading" icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="config-card">
            <template #header>
              <div class="config-title">
                <i class="icon icon-config" />
                <span>风险控制配置</span>
              </div>
            </template>
            
            <el-form :model="riskConfig" label-width="150px">
              <el-form-item label="最大单笔投注金额">
                <el-input-number 
                  v-model="riskConfig.maxBetAmount" 
                  :min="0" 
                  :step="100" 
                  :precision="2"
                  style="width: 100%;"
                />
                <span class="unit">元</span>
              </el-form-item>
              
              <el-form-item label="单日最大投注限额">
                <el-input-number 
                  v-model="riskConfig.dailyBetLimit" 
                  :min="0" 
                  :step="500" 
                  :precision="2"
                  style="width: 100%;"
                />
                <span class="unit">元</span>
              </el-form-item>
              
              <el-form-item label="单日最大亏损限额">
                <el-input-number 
                  v-model="riskConfig.dailyLossLimit" 
                  :min="0" 
                  :step="500" 
                  :precision="2"
                  style="width: 100%;"
                />
                <span class="unit">元</span>
              </el-form-item>
              
              <el-form-item label="单场比赛投注占比上限">
                <el-slider 
                  v-model="riskConfig.maxBetRatio" 
                  :min="0" 
                  :max="100" 
                  :step="0.1"
                  style="width: calc(100% - 80px);"
                />
                <span class="unit">{{ riskConfig.maxBetRatio }}%</span>
              </el-form-item>
              
              <el-form-item label="风控等级">
                <el-radio-group v-model="riskConfig.riskLevel">
                  <el-radio value="low">低风险</el-radio>
                  <el-radio value="medium">中风险</el-radio>
                  <el-radio value="high">高风险</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="触发风控阈值">
                <el-slider 
                  v-model="riskConfig.triggerThreshold" 
                  :min="0" 
                  :max="1" 
                  :step="0.01"
                  :format-tooltip="val => `${(val * 100).toFixed(2)}%`"
                  style="width: calc(100% - 80px);"
                />
                <span class="unit">{{ (riskConfig.triggerThreshold * 100).toFixed(2) }}%</span>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="metrics-card">
            <template #header>
              <div class="config-title">
                <i class="icon icon-metrics" />
                <span>风险指标监控</span>
              </div>
            </template>
            
            <div class="risk-metrics">
              <div class="metric-item">
                <div class="metric-label">当前风险值</div>
                <div :class="['metric-value', getRiskLevelClass(riskMetrics.currentRiskValue)]">
                  {{ riskMetrics.currentRiskValue }}%
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-label">今日投注总额</div>
                <div class="metric-value">¥{{ riskMetrics.todayTotalBet.toLocaleString() }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">今日盈亏</div>
                <div :class="['metric-value', riskMetrics.todayProfit >= 0 ? 'positive' : 'negative']">
                  {{ riskMetrics.todayProfit >= 0 ? '+' : '' }}¥{{ Math.abs(riskMetrics.todayProfit).toLocaleString() }}
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-label">触发风控次数</div>
                <div class="metric-value">{{ riskMetrics.riskTriggerCount }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">异常行为次数</div>
                <div class="metric-value">{{ riskMetrics.anomalyCount }}</div>
              </div>
            </div>
            
            <el-progress 
              :percentage="riskMetrics.currentRiskValue" 
              :color="getRiskProgressColor(riskMetrics.currentRiskValue)"
              :stroke-width="20"
              style="margin-top: 20px;"
            />
          </el-card>
          
          <el-card class="events-card" style="margin-top: 20px;">
            <template #header>
              <div class="config-title">
                <i class="icon icon-events" />
                <span>风险事件日志</span>
              </div>
            </template>
            
            <el-timeline>
              <el-timeline-item 
                v-for="(event, index) in riskEvents" 
                :key="index" 
                :timestamp="event.timestamp" 
                :type="event.type"
                placement="top"
              >
                <el-card>
                  <h4>{{ event.title }}</h4>
                  <p>{{ event.description }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 风险控制配置
const riskConfig = ref({
  maxBetAmount: 5000.00,
  dailyBetLimit: 20000.00,
  dailyLossLimit: 5000.00,
  maxBetRatio: 10.0,
  riskLevel: 'medium',
  triggerThreshold: 0.8
})

// 风险指标
const riskMetrics = ref({
  currentRiskValue: 75,
  todayTotalBet: 12500.50,
  todayProfit: -1200.75,
  riskTriggerCount: 3,
  anomalyCount: 5
})

// 风险事件
const riskEvents = ref([
  { 
    timestamp: '2026-01-30 03:15:22', 
    title: '触发风控规则', 
    description: '单笔投注超过阈值 - ¥6,500',
    type: 'danger'
  },
  { 
    timestamp: '2026-01-30 02:45:10', 
    title: '异常行为检测', 
    description: '短时间内多次高频操作',
    type: 'warning'
  },
  { 
    timestamp: '2026-01-30 01:30:05', 
    title: '风险提醒', 
    description: '当前风险等级较高，请注意控制投注',
    type: 'primary'
  },
  { 
    timestamp: '2026-01-29 23:45:30', 
    title: '大额投注', 
    description: '用户ID: 1001 投注 ¥8,000',
    type: 'warning'
  }
])

const loading = ref(false)

// 获取风险等级对应的CSS类
const getRiskLevelClass = (value) => {
  if (value >= 80) return 'high-risk'
  if (value >= 60) return 'medium-risk'
  return 'low-risk'
}

// 获取风险进度条颜色
const getRiskProgressColor = (value) => {
  if (value >= 80) return '#f56c6c' // 红色
  if (value >= 60) return '#e6a23c' // 黄色
  return '#67c23a' // 绿色
}

// 加载配置
const loadConfig = async () => {
  loading.value = true
  // 模拟API调用
  setTimeout(() => {
    loading.value = false
    ElMessage.success('配置加载成功')
  }, 800)
}

// 保存配置
const saveConfig = async () => {
  loading.value = true
  // 模拟API调用
  setTimeout(() => {
    loading.value = false
    ElMessage.success('风险控制配置已保存')
  }, 800)
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.card-container {
  margin: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.config-title {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.icon::before {
  margin-right: 8px;
  font-size: 18px;
}

.config-card, .metrics-card, .events-card {
  margin-bottom: 20px;
}

.unit {
  margin-left: 10px;
  color: #909399;
}

.risk-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.metric-item {
  text-align: center;
  padding: 10px 0;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.metric-value.high-risk {
  color: #f56c6c;
}

.metric-value.medium-risk {
  color: #e6a23c;
}

.metric-value.low-risk {
  color: #67c23a;
}

.metric-value.positive {
  color: #67c23a;
}

.metric-value.negative {
  color: #f56c6c;
}

.events-card .el-card__body {
  padding: 0;
}
</style>