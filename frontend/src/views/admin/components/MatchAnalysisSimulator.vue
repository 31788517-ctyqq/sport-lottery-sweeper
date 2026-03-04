<template>
  <div class="match-analysis-simulator">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">比赛分析模拟器</span>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>

      <div class="simulator-content">
        <!-- 模拟控制面板 -->
        <div class="control-panel">
          <el-row :gutter="20" class="control-row">
            <el-col :span="6">
              <el-form-item label="联赛类型:">
                <el-select v-model="simulationConfig.leagueType" placeholder="选择联赛类型" style="width: 100%">
                  <el-option label="足球" value="football"></el-option>
                  <el-option label="篮球" value="basketball"></el-option>
                  <el-option label="网球" value="tennis"></el-option>
                  <el-option label="混合" value="mixed"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="比赛数量:">
                <el-input-number 
                  v-model="simulationConfig.matchCount" 
                  :min="10" 
                  :max="1000" 
                  :step="10"
                  style="width: 100%"
                ></el-input-number>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="分析深度:">
                <el-select v-model="simulationConfig.analysisDepth" placeholder="选择分析深度" style="width: 100%">
                  <el-option label="快速" value="quick"></el-option>
                  <el-option label="标准" value="standard"></el-option>
                  <el-option label="深度" value="deep"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="策略模式:">
                <el-select v-model="simulationConfig.strategyMode" placeholder="选择策略模式" style="width: 100%">
                  <el-option label="保守" value="conservative"></el-option>
                  <el-option label="平衡" value="balanced"></el-option>
                  <el-option label="激进" value="aggressive"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" class="control-row">
            <el-col :span="12">
              <el-form-item label="数据源:">
                <el-checkbox-group v-model="simulationConfig.dataSources">
                  <el-checkbox value="official">官方数据</el-checkbox>
                  <el-checkbox value="thirdParty">第三方数据</el-checkbox>
                  <el-checkbox value="historical">历史数据</el-checkbox>
                  <el-checkbox value="realTime">实时数据</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="分析选项:">
                <el-checkbox-group v-model="simulationConfig.analysisOptions">
                  <el-checkbox value="odds">赔率分析</el-checkbox>
                  <el-checkbox value="stats">数据统计</el-checkbox>
                  <el-checkbox value="trends">趋势分析</el-checkbox>
                  <el-checkbox value="predictions">预测模型</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
          </el-row>

          <div class="action-buttons">
            <el-button type="primary" size="large" @click="startSimulation" :loading="isSimulating">
              <el-icon><VideoPlay /></el-icon>
              开始模拟
            </el-button>
            <el-button size="large" @click="pauseSimulation" :disabled="!isSimulating">
              <el-icon><VideoPause /></el-icon>
              暂停
            </el-button>
            <el-button size="large" @click="stopSimulation" :disabled="!isSimulating">
              <el-icon><CircleClose /></el-icon>
              停止
            </el-button>
            <el-button size="large" @click="resetSimulation">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </div>
        </div>

        <!-- 进度显示 -->
        <div v-if="isSimulating || simulationProgress > 0" class="progress-section">
          <el-progress :percentage="simulationProgress" :stroke-width="8" />
          <div class="progress-info">
            <span>已处理: {{ processedMatches }} / {{ simulationConfig.matchCount }} 场比赛</span>
            <span>预计剩余时间: {{ estimatedTimeRemaining }}</span>
          </div>
        </div>

        <!-- 实时结果展示 -->
        <div v-if="simulationResults.length > 0" class="results-section">
          <el-divider content-position="left">模拟结果</el-divider>
          
          <!-- 统计概览 -->
          <div class="stats-overview">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="总场次" :value="simulationResults.length" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="平均准确率" :value="averageAccuracy" suffix="%" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="高置信度预测" :value="highConfidencePredictions" suffix="场" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="处理速度" :value="processingSpeed" suffix="场/秒" />
              </el-col>
            </el-row>
          </div>

          <!-- 结果表格 -->
          <el-table 
            :data="simulationResults.slice(0, 50)" 
            style="width: 100%; margin-top: 20px;"
            height="400"
            v-loading="isSimulating"
          >
            <el-table-column prop="matchId" label="比赛ID" width="100" />
            <el-table-column prop="league" label="联赛" width="120" />
            <el-table-column prop="homeTeam" label="主队" width="120" />
            <el-table-column prop="awayTeam" label="客队" width="120" />
            <el-table-column prop="predictedResult" label="预测结果" width="100">
              <template #default="scope">
                <el-tag :type="getResultTypeColor(scope.row.predictedResult)">
                  {{ scope.row.predictedResult }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.confidence" 
                  :stroke-width="6" 
                  style="width: 60px;"
                />
              </template>
            </el-table-column>
            <el-table-column prop="odds" label="赔率" width="120">
              <template #default="scope">
                <span>{{ scope.row.odds }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="riskLevel" label="风险等级" width="100">
              <template #default="scope">
                <el-tag :type="getRiskTypeColor(scope.row.riskLevel)" size="small">
                  {{ scope.row.riskLevel }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
                <el-button size="small" type="success" @click="exportResult(scope.row)">导出</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="simulationResults.length > 50" class="more-results">
            显示前50条结果，共{{ simulationResults.length }}条记录
          </div>
        </div>

        <!-- 图表分析 -->
        <div v-if="simulationResults.length > 0" class="charts-section">
          <el-divider content-position="left">图表分析</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-container">
                <h4>预测准确率分布</h4>
                <div class="chart-placeholder">图表加载中...</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-container">
                <h4>风险等级分布</h4>
                <div class="chart-placeholder">图表加载中...</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  VideoPlay, 
  VideoPause, 
  CircleClose, 
  RefreshLeft 
} from '@element-plus/icons-vue'

// 响应式数据
const isSimulating = ref(false)
const simulationProgress = ref(0)
const processedMatches = ref(0)
const simulationResults = ref([])

// 模拟配置
const simulationConfig = reactive({
  leagueType: 'football',
  matchCount: 100,
  analysisDepth: 'standard',
  strategyMode: 'balanced',
  dataSources: ['official', 'historical'],
  analysisOptions: ['odds', 'stats', 'predictions']
})

// 计算属性
const averageAccuracy = computed(() => {
  if (simulationResults.value.length === 0) return 0
  const total = simulationResults.value.reduce((sum, result) => sum + result.confidence, 0)
  return Math.round(total / simulationResults.value.length)
})

const highConfidencePredictions = computed(() => {
  return simulationResults.value.filter(result => result.confidence >= 80).length
})

const processingSpeed = computed(() => {
  if (processedMatches.value === 0) return 0
  return Math.round(processedMatches.value / (simulationProgress.value || 1) * 100)
})

const estimatedTimeRemaining = computed(() => {
  if (simulationProgress.value === 0) return '--'
  const remaining = 100 - simulationProgress.value
  const seconds = Math.round((remaining / simulationProgress.value) * 10)
  if (seconds < 60) return `${seconds}秒`
  return `${Math.round(seconds / 60)}分钟`
})

// 方法
const refreshData = async () => {
  ElMessage.success('数据已刷新')
}

const startSimulation = async () => {
  isSimulating.value = true
  simulationProgress.value = 0
  processedMatches.value = 0
  simulationResults.value = []
  
  ElMessage.info('开始比赛分析模拟...')
  
  // 模拟进度更新
  const interval = setInterval(() => {
    if (simulationProgress.value >= 100) {
      clearInterval(interval)
      finishSimulation()
      return
    }
    
    simulationProgress.value += Math.random() * 5
    if (simulationProgress.value > 100) simulationProgress.value = 100
    
    // 模拟处理结果
    const newMatches = Math.floor(Math.random() * 5) + 1
    for (let i = 0; i < newMatches; i++) {
      simulationResults.value.push(generateMockResult())
    }
    processedMatches.value = simulationResults.value.length
    
  }, 200)
}

const pauseSimulation = () => {
  isSimulating.value = false
  ElMessage.info('模拟已暂停')
}

const stopSimulation = () => {
  isSimulating.value = false
  simulationProgress.value = 0
  processedMatches.value = 0
  simulationResults.value = []
  ElMessage.info('模拟已停止')
}

const resetSimulation = () => {
  stopSimulation()
  simulationConfig.leagueType = 'football'
  simulationConfig.matchCount = 100
  simulationConfig.analysisDepth = 'standard'
  simulationConfig.strategyMode = 'balanced'
  simulationConfig.dataSources = ['official', 'historical']
  simulationConfig.analysisOptions = ['odds', 'stats', 'predictions']
  ElMessage.success('模拟器已重置')
}

const finishSimulation = () => {
  isSimulating.value = false
  ElMessage.success(`模拟完成！共处理${simulationResults.value.length}场比赛`)
}

const generateMockResult = () => {
  const teams = [
    ['曼联', '切尔西'], ['巴萨', '皇马'], ['拜仁', '多特'], ['尤文', '国米'],
    ['湖人', '勇士'], ['热火', '凯尔特人'], ['公牛', '尼克斯'], ['火箭', '马刺']
  ]
  const randomTeam = teams[Math.floor(Math.random() * teams.length)]
  const results = ['胜', '平', '负']
  const riskLevels = ['低', '中', '高']
  
  return {
    matchId: Math.floor(Math.random() * 10000),
    league: simulationConfig.leagueType === 'football' ? '英超' : 'NBA',
    homeTeam: randomTeam[0],
    awayTeam: randomTeam[1],
    predictedResult: results[Math.floor(Math.random() * results.length)],
    confidence: Math.floor(Math.random() * 40) + 60, // 60-100%
    odds: (Math.random() * 3 + 1).toFixed(2),
    riskLevel: riskLevels[Math.floor(Math.random() * riskLevels.length)]
  }
}

const getResultTypeColor = (result) => {
  const colors = {
    '胜': 'success',
    '平': 'warning',
    '负': 'danger'
  }
  return colors[result] || 'info'
}

const getRiskTypeColor = (risk) => {
  const colors = {
    '低': 'success',
    '中': 'warning',
    '高': 'danger'
  }
  return colors[risk] || 'info'
}

const viewDetails = (result) => {
  ElMessage.info(`查看比赛详情: ${result.homeTeam} vs ${result.awayTeam}`)
}

const exportResult = (result) => {
  ElMessage.success(`导出分析结果: ${result.homeTeam} vs ${result.awayTeam}`)
}

// 生命周期
onMounted(() => {
  console.log('比赛分析模拟器已加载')
})
</script>

<style scoped>
.match-analysis-simulator {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
}

.simulator-content {
  min-height: 500px;
}

.control-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.control-row {
  margin-bottom: 15px;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

.action-buttons .el-button {
  margin: 0 10px;
}

.progress-section {
  margin: 20px 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.results-section {
  margin: 20px 0;
}

.stats-overview {
  margin: 20px 0;
}

.charts-section {
  margin: 20px 0;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.chart-container h4 {
  margin: 0 0 20px 0;
  color: #303133;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  color: #909399;
}

.more-results {
  text-align: center;
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .control-panel .el-col {
    margin-bottom: 10px;
  }
  
  .action-buttons .el-button {
    margin: 5px;
    font-size: 12px;
  }
}
</style>