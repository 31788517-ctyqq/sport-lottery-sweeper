<template>
  <div class="intelligence-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>采集管理</h2>
      <p class="page-description">管理数据采集任务和采集源配置</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="showCreateSourceDialog = true">
        新建采集源
      </el-button>
      <el-button type="success" :icon="VideoPlay" @click="startCollection">
        启动采集
      </el-button>
      <el-button type="warning" :icon="RefreshLeft" @click="refreshSources">
        刷新状态
      </el-button>
      <el-button type="info" :icon="Setting" @click="configureSchedule">
        调度配置
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.activeSources }}</div>
              <div class="stats-label">活跃采集源</div>
            </div>
            <el-icon class="stats-icon"><Connection /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.todayCollected }}</div>
              <div class="stats-label">今日采集量</div>
            </div>
            <el-icon class="stats-icon"><Upload /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.successRate }}%</div>
              <div class="stats-label">成功率</div>
            </div>
            <el-icon class="stats-icon"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.queueLength }}</div>
              <div class="stats-label">队列长度</div>
            </div>
            <el-icon class="stats-icon"><List /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- Collection Sources Tab -->
      <el-tab-pane label="采集源管理" name="sources">
        <div class="tab-content">
          <!-- Source Categories -->
          <div class="category-filter">
            <el-button-group>
              <el-button 
                v-for="category in categories" 
                :key="category.key"
                :type="selectedCategory === category.key ? 'primary' : ''"
                @click="selectedCategory = category.key"
              >
                {{ category.label }}
              </el-button>
            </el-button-group>
          </div>

          <!-- Sources Grid -->
          <div class="sources-grid">
            <el-card 
              v-for="source in filteredSources" 
              :key="source.id"
              class="source-card"
            >
              <template #header>
                <div class="source-header">
                  <div class="source-info">
                    <h4>{{ source.name }}</h4>
                    <el-tag :type="getSourceTypeColor(source.type)" size="small">{{ source.type }}</el-tag>
                  </div>
                  <el-tag :type="getStatusColor(source.status)" size="small">{{ source.status }}</el-tag>
                </div>
              </template>
              
              <div class="source-content">
                <p class="source-desc">{{ source.description }}</p>
                
                <div class="source-meta">
                  <div class="meta-item">
                    <span class="label">URL:</span>
                    <el-link :href="source.url" target="_blank" type="primary">{{ source.url }}</el-link>
                  </div>
                  <div class="meta-item">
                    <span class="label">更新频率:</span>
                    <span>{{ source.frequency }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">最后采集:</span>
                    <span>{{ source.lastCollected }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="label">数据量:</span>
                    <span>{{ source.dataCount }} 条</span>
                  </div>
                </div>
              </div>

              <div class="source-actions">
                <el-button size="small" @click="editSource(source)">编辑</el-button>
                <el-button 
                  size="small" 
                  :type="source.status === 'active' ? 'warning' : 'success'"
                  @click="toggleSource(source)"
                >
                  {{ source.status === 'active' ? '停用' : '启用' }}
                </el-button>
                <el-button size="small" type="primary" @click="collectNow(source)">立即采集</el-button>
                <el-button size="small" type="danger" @click="deleteSource(source)">删除</el-button>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- Collection Tasks Tab -->
      <el-tab-pane label="采集任务" name="tasks">
        <div class="tab-content">
          <!-- Task Monitor -->
          <el-row :gutter="16" class="task-monitor">
            <el-col :span="8">
              <el-card class="monitor-card">
                <div class="monitor-value">{{ taskStats.running }}</div>
                <div class="monitor-label">运行中任务</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="monitor-card">
                <div class="monitor-value">{{ taskStats.queued }}</div>
                <div class="monitor-label">排队中任务</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="monitor-card">
                <div class="monitor-value">{{ taskStats.errors }}</div>
                <div class="monitor-label">错误任务</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Real-time Log -->
          <el-card class="log-card">
            <template #header>
              <div class="log-header">
                <span>实时日志</span>
                <div class="log-controls">
                  <el-button size="small" @click="clearLogs">清空</el-button>
                  <el-button size="small" @click="downloadLogs">下载</el-button>
                </div>
              </div>
            </template>
            <div class="log-content">
              <div 
                v-for="log in realtimeLogs" 
                :key="log.id"
                class="log-entry"
                :class="`log-${log.level}`"
              >
                <span class="log-time">{{ log.time }}</span>
                <span class="log-source">[{{ log.source }}]</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Data Pipeline Tab -->
      <el-tab-pane label="数据管道" name="pipeline">
        <div class="tab-content">
          <!-- Pipeline Visualization -->
          <el-card class="pipeline-card">
            <template #header>数据处理管道</template>
            <div class="pipeline-flow">
              <div 
                v-for="(step, index) in pipelineSteps" 
                :key="index"
                class="pipeline-step"
                :class="{ active: step.active, completed: step.completed }"
              >
                <div class="step-icon">
                  <el-icon><component :is="step.icon" /></el-icon>
                </div>
                <div class="step-content">
                  <h5>{{ step.name }}</h5>
                  <p>{{ step.description }}</p>
                  <div class="step-status">
                    <el-progress :percentage="step.progress" :stroke-width="4" />
                  </div>
                </div>
                <div class="step-arrow" v-if="index < pipelineSteps.length - 1">
                  <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Pipeline Config -->
          <el-card class="config-card">
            <template #header>管道配置</template>
            <el-form :model="pipelineConfig" label-width="140px">
              <el-form-item label="并发数量">
                <el-slider 
                  v-model="pipelineConfig.concurrency" 
                  :min="1" 
                  :max="10" 
                  :marks="{ 1: '1', 5: '5', 10: '10' }"
                />
              </el-form-item>
              <el-form-item label="超时设置">
                <el-input-number 
                  v-model="pipelineConfig.timeout" 
                  :min="30" 
                  :max="300" 
                  :step="30"
                />
                <span style="margin-left: 8px;">秒</span>
              </el-form-item>
              <el-form-item label="重试次数">
                <el-input-number 
                  v-model="pipelineConfig.retries" 
                  :min="0" 
                  :max="5"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="savePipelineConfig">保存配置</el-button>
                <el-button @click="resetPipelineConfig">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Quality Control Tab -->
      <el-tab-pane label="质量控制" name="quality">
        <div class="tab-content">
          <!-- Quality Metrics -->
          <el-row :gutter="20" class="quality-metrics">
            <el-col :span="6">
              <el-card class="metric-card">
                <div class="metric-value">{{ qualityMetrics.completeness }}%</div>
                <div class="metric-label">完整性</div>
                <el-progress :percentage="qualityMetrics.completeness" :color="getQualityColor(qualityMetrics.completeness)" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="metric-card">
                <div class="metric-value">{{ qualityMetrics.accuracy }}%</div>
                <div class="metric-label">准确性</div>
                <el-progress :percentage="qualityMetrics.accuracy" :color="getQualityColor(qualityMetrics.accuracy)" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="metric-card">
                <div class="metric-value">{{ qualityMetrics.consistency }}%</div>
                <div class="metric-label">一致性</div>
                <el-progress :percentage="qualityMetrics.consistency" :color="getQualityColor(qualityMetrics.consistency)" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="metric-card">
                <div class="metric-value">{{ qualityMetrics.timeliness }}%</div>
                <div class="metric-label">及时性</div>
                <el-progress :percentage="qualityMetrics.timeliness" :color="getQualityColor(qualityMetrics.timeliness)" />
              </el-card>
            </el-col>
          </el-row>

          <!-- Quality Issues -->
          <el-card class="issues-card">
            <template #header>质量问题</template>
            <el-table :data="qualityIssues" style="width: 100%">
              <el-table-column prop="severity" label="严重程度" width="100">
                <template #default="scope">
                  <el-tag :type="getSeverityColor(scope.row.severity)">{{ scope.row.severity }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="问题类型" width="120" />
              <el-table-column prop="description" label="问题描述" min-width="200" />
              <el-table-column prop="affectedCount" label="影响数量" width="100" />
              <el-table-column prop="detectedAt" label="检测时间" width="160" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="viewIssue(scope.row)">查看</el-button>
                  <el-button size="small" type="primary" @click="fixIssue(scope.row)">修复</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Source Dialog -->
    <el-dialog 
      v-model="showCreateSourceDialog" 
      :title="isEditing ? '编辑采集源' : '新建采集源'"
      width="700px"
    >
      <el-form :model="sourceForm" :rules="sourceFormRules" ref="sourceFormRef" label-width="120px">
        <el-form-item label="源名称" prop="name">
          <el-input v-model="sourceForm.name" placeholder="请输入采集源名称" />
        </el-form-item>
        <el-form-item label="源类型" prop="type">
          <el-select v-model="sourceForm.type" placeholder="请选择源类型">
            <el-option label="API接口" value="api" />
            <el-option label="网页爬虫" value="web" />
            <el-option label="数据库" value="database" />
            <el-option label="文件导入" value="file" />
          </el-select>
        </el-form-item>
        <el-form-item label="源地址" prop="url">
          <el-input v-model="sourceForm.url" placeholder="请输入源地址" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="sourceForm.category" placeholder="请选择分类">
            <el-option v-for="cat in categories" :key="cat.key" :label="cat.label" :value="cat.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="更新频率" prop="frequency">
          <el-select v-model="sourceForm.frequency" placeholder="请选择更新频率">
            <el-option label="实时" value="realtime" />
            <el-option label="每小时" value="hourly" />
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="sourceForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入采集源描述"
          />
        </el-form-item>
        <el-form-item label="配置信息" prop="config">
          <el-input 
            v-model="sourceForm.config" 
            type="textarea" 
            :rows="4"
            placeholder="请输入JSON格式的额外配置信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateSourceDialog = false">取消</el-button>
          <el-button type="primary" @click="saveSource">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, VideoPlay, RefreshLeft, Setting, Connection, Upload, CircleCheck, List,
  Edit, Delete, ArrowRight, Link, Calendar, Document
} from '@element-plus/icons-vue'

// Reactive data
const activeTab = ref('sources')
const showCreateSourceDialog = ref(false)
const isEditing = ref(false)
const selectedCategory = ref('all')

// Stats data
const stats = reactive({
  activeSources: 8,
  todayCollected: 15420,
  successRate: 96.5,
  queueLength: 23
})

// Categories
const categories = ref([
  { key: 'all', label: '全部' },
  { key: 'official', label: '官方数据源' },
  { key: 'partner', label: '合作伙伴' },
  { key: 'public', label: '公开数据' },
  { key: 'internal', label: '内部系统' }
])

// Source form
const sourceForm = reactive({
  name: '',
  type: '',
  url: '',
  category: '',
  frequency: '',
  description: '',
  config: ''
})

const sourceFormRules = {
  name: [{ required: true, message: '请输入源名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择源类型', trigger: 'change' }],
  url: [{ required: true, message: '请输入源地址', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

// Mock data
const sources = ref([
  {
    id: 1,
    name: '官方赛事API',
    type: 'api',
    category: 'official',
    status: 'active',
    url: 'https://api.sports.com/v1/matches',
    frequency: '实时',
    description: '获取官方赛事数据和实时比分',
    lastCollected: '2024-01-23 10:30:00',
    dataCount: 8540
  },
  {
    id: 2,
    name: '合作伙伴数据',
    type: 'api',
    category: 'partner',
    status: 'active',
    url: 'https://partner.api.com/sports',
    frequency: '每小时',
    description: '合作伙伴提供的扩展赛事数据',
    lastCollected: '2024-01-23 09:00:00',
    dataCount: 3240
  },
  {
    id: 3,
    name: '公开数据源',
    type: 'web',
    category: 'public',
    status: 'inactive',
    url: 'https://public-data.com/sports',
    frequency: '每日',
    description: '从公开网站爬取的体育数据',
    lastCollected: '2024-01-22 08:00:00',
    dataCount: 1280
  }
])

const taskStats = reactive({
  running: 3,
  queued: 7,
  errors: 1
})

const realtimeLogs = ref([
  { id: 1, time: '10:30:15', source: '官方赛事API', level: 'info', message: '开始采集数据' },
  { id: 2, time: '10:30:18', source: '官方赛事API', level: 'success', message: '成功采集 50 条数据' },
  { id: 3, time: '10:30:20', source: '合作伙伴数据', level: 'info', message: '连接超时，准备重试' },
  { id: 4, time: '10:30:25', source: '合作伙伴数据', level: 'error', message: '重试失败，跳过本次采集' }
])

const pipelineSteps = ref([
  { name: '数据抓取', description: '从源地址获取原始数据', icon: 'Download', active: true, completed: false, progress: 80 },
  { name: '数据清洗', description: '清理无效和重复数据', icon: 'Brush', active: false, completed: false, progress: 0 },
  { name: '格式转换', description: '转换为标准数据格式', icon: 'Operation', active: false, completed: false, progress: 0 },
  { name: '质量检查', description: '验证数据完整性和准确性', icon: 'CircleCheck', active: false, completed: false, progress: 0 },
  { name: '入库存储', description: '保存到数据库', icon: 'Document', active: false, completed: false, progress: 0 }
])

const pipelineConfig = reactive({
  concurrency: 5,
  timeout: 120,
  retries: 3
})

const qualityMetrics = reactive({
  completeness: 94,
  accuracy: 97,
  consistency: 91,
  timeliness: 89
})

const qualityIssues = ref([
  { severity: 'high', type: '数据缺失', description: '部分比赛缺少赔率信息', affectedCount: 23, detectedAt: '2024-01-23 09:15:00' },
  { severity: 'medium', type: '格式错误', description: '日期格式不统一', affectedCount: 156, detectedAt: '2024-01-23 08:30:00' },
  { severity: 'low', type: '重复数据', description: '检测到重复的比分记录', affectedCount: 12, detectedAt: '2024-01-23 07:45:00' }
])

// Computed
const filteredSources = computed(() => {
  if (selectedCategory.value === 'all') return sources.value
  return sources.value.filter(source => source.category === selectedCategory.value)
})

// Methods
const getSourceTypeColor = (type) => {
  const colors = { api: 'primary', web: 'success', database: 'warning', file: 'info' }
  return colors[type] || 'info'
}

const getStatusColor = (status) => {
  const colors = { active: 'success', inactive: 'danger', testing: 'warning' }
  return colors[status] || 'info'
}

const getSeverityColor = (severity) => {
  const colors = { high: 'danger', medium: 'warning', low: 'info' }
  return colors[severity] || 'info'
}

const getQualityColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#e6a23c'
  return '#f56c6c'
}

const editSource = (source) => {
  isEditing.value = true
  Object.assign(sourceForm, source)
  showCreateSourceDialog.value = true
}

const toggleSource = (source) => {
  const newStatus = source.status === 'active' ? 'inactive' : 'active'
  source.status = newStatus
  ElMessage.success(`采集源已${newStatus === 'active' ? '启用' : '停用'}`)
}

const collectNow = (source) => {
  ElMessage.info(`开始采集: ${source.name}`)
}

const deleteSource = (source) => {
  ElMessageBox.confirm(`确定要删除采集源"${source.name}"吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  })
}

const startCollection = () => {
  ElMessage.info('启动批量采集任务')
}

const refreshSources = () => {
  ElMessage.success('刷新完成')
}

const configureSchedule = () => {
  ElMessage.info('打开调度配置')
}

const clearLogs = () => {
  realtimeLogs.value = []
  ElMessage.success('日志已清空')
}

const downloadLogs = () => {
  ElMessage.info('下载日志文件')
}

const saveSource = () => {
  ElMessage.success(isEditing.value ? '采集源更新成功' : '采集源创建成功')
  showCreateSourceDialog.value = false
  resetSourceForm()
}

const resetSourceForm = () => {
  Object.assign(sourceForm, {
    name: '',
    type: '',
    url: '',
    category: '',
    frequency: '',
    description: '',
    config: ''
  })
  isEditing.value = false
}

const savePipelineConfig = () => {
  ElMessage.success('管道配置已保存')
}

const resetPipelineConfig = () => {
  Object.assign(pipelineConfig, {
    concurrency: 5,
    timeout: 120,
    retries: 3
  })
}

const viewIssue = (issue) => {
  ElMessage.info(`查看质量问题: ${issue.type}`)
}

const fixIssue = (issue) => {
  ElMessage.success(`开始修复: ${issue.type}`)
}

onMounted(() => {
  console.log('Collection Management mounted')
})
</script>

<style scoped>
.intelligence-management-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  position: relative;
  overflow: hidden;
}

.stats-content {
  position: relative;
  z-index: 2;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 48px;
  color: #409eff;
  opacity: 0.1;
  z-index: 1;
}

.management-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 20px;
}

.category-filter {
  margin-bottom: 20px;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.source-card {
  transition: all 0.3s;
}

.source-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.source-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.source-content {
  margin: 16px 0;
}

.source-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.source-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.meta-item .label {
  color: #909399;
  width: 60px;
  flex-shrink: 0;
}

.source-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.task-monitor {
  margin-bottom: 20px;
}

.monitor-card {
  text-align: center;
}

.monitor-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.monitor-label {
  color: #606266;
  font-size: 14px;
}

.log-card {
  margin-top: 16px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-controls {
  display: flex;
  gap: 8px;
}

.log-content {
  height: 300px;
  overflow-y: auto;
  background: #1e1e1e;
  color: #fff;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-entry {
  margin-bottom: 4px;
  line-height: 1.4;
}

.log-time {
  color: #888;
}

.log-source {
  color: #ffd700;
  margin: 0 4px;
}

.log-info .log-message { color: #fff; }
.log-success .log-message { color: #52c41a; }
.log-warning .log-message { color: #faad14; }
.log-error .log-message { color: #f5222d; }

.pipeline-card {
  margin-bottom: 20px;
}

.pipeline-flow {
  display: flex;
  align-items: center;
  padding: 20px 0;
}

.pipeline-step {
  display: flex;
  align-items: center;
  flex: 1;
}

.step-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: #999;
}

.pipeline-step.active .step-icon {
  background: #409eff;
  color: white;
}

.pipeline-step.completed .step-icon {
  background: #67c23a;
  color: white;
}

.step-content h5 {
  margin: 0 0 8px 0;
  color: #303133;
}

.step-content p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.step-arrow {
  margin: 0 20px;
  font-size: 24px;
  color: #ddd;
}

.config-card {
  margin-top: 20px;
}

.quality-metrics {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.metric-label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 12px;
}

.issues-card {
  margin-top: 20px;
}
</style>