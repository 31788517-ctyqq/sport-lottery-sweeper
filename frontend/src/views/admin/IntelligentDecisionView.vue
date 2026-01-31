<template>
  <div class="intelligent-decision">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>智能决策管理</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="对冲策略管理" name="hedging">
          <div class="tab-content">
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="6">
                <el-input v-model="searchQuery" placeholder="搜索策略名称" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="strategyStatus" placeholder="策略状态">
                  <el-option label="全部" value="" />
                  <el-option label="启用" value="enabled" />
                  <el-option label="停用" value="disabled" />
                </el-select>
              </el-col>
              <el-col :span="12">
                <el-button type="primary" @click="addStrategy">新增策略</el-button>
                <el-button @click="applyFilters">应用筛选</el-button>
              </el-col>
            </el-row>
            
            <el-table :data="hedgingStrategies" style="width: 100%">
              <el-table-column prop="name" label="策略名称" width="200"></el-table-column>
              <el-table-column prop="description" label="描述" min-width="200"></el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'enabled' ? 'success' : 'info'">
                    {{ row.status === 'enabled' ? '启用' : '停用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="riskThreshold" label="风险阈值" width="120"></el-table-column>
              <el-table-column prop="profitability" label="盈利能力" width="120">
                <template #default="{ row }">
                  <span :class="row.profitability > 0 ? 'profit-positive' : 'profit-negative'">
                    {{ row.profitability > 0 ? '+' : '' }}{{ row.profitability }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="lastRun" label="上次执行" width="180"></el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="editStrategy(row)">编辑</el-button>
                  <el-button size="small" type="primary" @click="executeStrategy(row)">立即执行</el-button>
                  <el-button size="small" @click="toggleStatus(row)">
                    {{ row.status === 'enabled' ? '停用' : '启用' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-pagination
              class="pagination"
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              @current-change="handlePageChange"
              layout="total, prev, pager, next, jumper"
            />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="推荐系统管理" name="recommendations">
          <div class="tab-content">
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="6">
                <el-input v-model="recommendationSearch" placeholder="搜索推荐算法" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="algorithmType" placeholder="算法类型">
                  <el-option label="全部" value="" />
                  <el-option label="协同过滤" value="collaborative" />
                  <el-option label="内容推荐" value="content" />
                  <el-option label="混合推荐" value="hybrid" />
                </el-select>
              </el-col>
              <el-col :span="12">
                <el-button type="primary" @click="addAlgorithm">新增算法</el-button>
                <el-button @click="applyRecommendationFilters">应用筛选</el-button>
              </el-col>
            </el-row>
            
            <el-table :data="recommendationAlgorithms" style="width: 100%">
              <el-table-column prop="name" label="算法名称" width="200"></el-table-column>
              <el-table-column prop="type" label="类型" width="150">
                <template #default="{ row }">
                  <el-tag>
                    {{ row.type === 'collaborative' ? '协同过滤' : 
                       row.type === 'content' ? '内容推荐' : 
                       row.type === 'hybrid' ? '混合推荐' : '未知' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="accuracy" label="准确率" width="120">
                <template #default="{ row }">
                  {{ row.accuracy }}%
                </template>
              </el-table-column>
              <el-table-column prop="coverage" label="覆盖率" width="120">
                <template #default="{ row }">
                  {{ row.coverage }}%
                </template>
              </el-table-column>
              <el-table-column prop="performanceScore" label="性能评分" width="120">
                <template #default="{ row }">
                  <el-rate v-model="row.performanceScore" :max="5" disabled />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="editAlgorithm(row)">编辑</el-button>
                  <el-button size="small" type="primary" @click="testAlgorithm(row)">测试</el-button>
                  <el-button size="small" @click="configureAlgorithm(row)">配置</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-pagination
              class="pagination"
              :current-page="recommendationCurrentPage"
              :page-size="recommendationPageSize"
              :total="recommendationTotal"
              @current-change="handleRecommendationPageChange"
              layout="total, prev, pager, next, jumper"
            />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="风险控制" name="risk-control">
          <div class="tab-content">
            <el-alert title="风险控制模块" type="info" :closable="false" style="margin-bottom: 20px;" />
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>风险阈值配置</span>
                  </template>
                  
                  <el-form :model="riskConfig" label-width="120px">
                    <el-form-item label="最大单笔投注">
                      <el-input-number v-model="riskConfig.maxBetAmount" :min="0" :step="10" />
                      <span>元</span>
                    </el-form-item>
                    
                    <el-form-item label="单日最大亏损">
                      <el-input-number v-model="riskConfig.dailyLossLimit" :min="0" :step="100" />
                      <span>元</span>
                    </el-form-item>
                    
                    <el-form-item label="单场最大投注比例">
                      <el-slider v-model="riskConfig.maxBetRatio" :max="100" />
                      <span>{{ riskConfig.maxBetRatio }}%</span>
                    </el-form-item>
                    
                    <el-form-item label="风控等级">
                      <el-radio-group v-model="riskConfig.riskLevel">
                        <el-radio label="low">低风险</el-radio>
                        <el-radio label="medium">中风险</el-radio>
                        <el-radio label="high">高风险</el-radio>
                      </el-radio-group>
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button type="primary" @click="saveRiskConfig">保存配置</el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>
              
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>风险监控</span>
                  </template>
                  
                  <div class="risk-metrics">
                    <div class="metric-item">
                      <div class="metric-label">当前风险值</div>
                      <div class="metric-value high-risk">85</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-label">今日投注总额</div>
                      <div class="metric-value">¥2,450</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-label">今日盈亏</div>
                      <div class="metric-value positive">+¥320</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-label">触发风控次数</div>
                      <div class="metric-value">3</div>
                    </div>
                  </div>
                </el-card>
                
                <el-card style="margin-top: 20px;">
                  <template #header>
                    <span>风险事件日志</span>
                  </template>
                  
                  <el-timeline>
                    <el-timeline-item timestamp="2026-01-30 03:15:22" placement="top">
                      <el-card>
                        <h4>触发风控规则</h4>
                        <p>单笔投注超过阈值 - ¥1,500</p>
                      </el-card>
                    </el-timeline-item>
                    <el-timeline-item timestamp="2026-01-30 02:45:10" placement="top">
                      <el-card>
                        <h4>异常行为检测</h4>
                        <p>短时间内多次高频操作</p>
                      </el-card>
                    </el-timeline-item>
                    <el-timeline-item timestamp="2026-01-30 01:30:05" placement="top">
                      <el-card>
                        <h4>风险提醒</h4>
                        <p>当前风险等级较高，请注意控制投注</p>
                      </el-card>
                    </el-timeline-item>
                  </el-timeline>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('hedging')

// 对冲策略管理相关数据
const hedgingStrategies = ref([
  { id: 1, name: '基础对冲策略', description: '基于赔率差异的对冲策略', status: 'enabled', riskThreshold: '2%', profitability: 3.2, lastRun: '2026-01-30 03:15:22' },
  { id: 2, name: '动态风险对冲', description: '根据市场波动动态调整的对冲策略', status: 'enabled', riskThreshold: '5%', profitability: -1.5, lastRun: '2026-01-30 02:45:10' },
  { id: 3, name: '多市场套利', description: '跨平台套利策略', status: 'disabled', riskThreshold: '3%', profitability: 5.8, lastRun: '2026-01-30 01:30:05' },
  { id: 4, name: '高频交易策略', description: '快速捕捉市场机会的策略', status: 'enabled', riskThreshold: '1%', profitability: 2.1, lastRun: '2026-01-30 00:45:30' }
])

const searchQuery = ref('')
const strategyStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(4)

// 推荐系统管理相关数据
const recommendationAlgorithms = ref([
  { id: 1, name: '协同过滤推荐', type: 'collaborative', accuracy: 85.2, coverage: 78.5, performanceScore: 4.2 },
  { id: 2, name: '内容基础推荐', type: 'content', accuracy: 79.8, coverage: 85.2, performanceScore: 3.8 },
  { id: 3, name: '混合推荐算法', type: 'hybrid', accuracy: 91.5, coverage: 82.1, performanceScore: 4.6 }
])

const recommendationSearch = ref('')
const algorithmType = ref('')
const recommendationCurrentPage = ref(1)
const recommendationPageSize = ref(10)
const recommendationTotal = ref(3)

// 风险控制相关数据
const riskConfig = ref({
  maxBetAmount: 1000,
  dailyLossLimit: 5000,
  maxBetRatio: 10,
  riskLevel: 'medium'
})

const handlePageChange = (page) => {
  currentPage.value = page
}

const handleRecommendationPageChange = (page) => {
  recommendationCurrentPage.value = page
}

const applyFilters = () => {
  // 实际实现中会根据筛选条件过滤数据
  ElMessage.success('应用筛选条件')
}

const applyRecommendationFilters = () => {
  // 实际实现中会根据筛选条件过滤推荐算法
  ElMessage.success('应用筛选条件')
}

const addStrategy = () => {
  ElMessage.info('新增对冲策略')
}

const editStrategy = (strategy) => {
  ElMessage.info(`编辑策略: ${strategy.name}`)
}

const executeStrategy = async (strategy) => {
  try {
    await ElMessageBox.confirm(
      `确定要立即执行策略 "${strategy.name}" 吗？`,
      '确认执行',
      { type: 'warning' }
    )
    ElMessage.success(`已发送执行指令给策略: ${strategy.name}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败')
    }
  }
}

const toggleStatus = (strategy) => {
  strategy.status = strategy.status === 'enabled' ? 'disabled' : 'enabled'
  ElMessage.success(`策略 ${strategy.name} 状态已更新为 ${strategy.status === 'enabled' ? '启用' : '停用'}`)
}

const addAlgorithm = () => {
  ElMessage.info('新增推荐算法')
}

const editAlgorithm = (algorithm) => {
  ElMessage.info(`编辑算法: ${algorithm.name}`)
}

const testAlgorithm = (algorithm) => {
  ElMessage.info(`测试算法: ${algorithm.name}`)
}

const configureAlgorithm = (algorithm) => {
  ElMessage.info(`配置算法: ${algorithm.name}`)
}

const saveRiskConfig = () => {
  ElMessage.success('风险配置已保存')
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tab-content {
  padding: 20px 0;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.profit-positive {
  color: green;
}

.profit-negative {
  color: red;
}

.risk-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.metric-item {
  text-align: center;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.metric-value.high-risk {
  color: #f56c6c;
}

.metric-value.positive {
  color: #67c23a;
}

.intelligent-decision {
  padding: 20px;
}
</style>