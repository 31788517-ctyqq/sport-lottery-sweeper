<template>
  <div class="intelligence-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>筛选管理</h2>
      <p class="page-description">管理数据筛选规则和筛选任务</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
        新建筛选规则
      </el-button>
      <el-button type="success" :icon="VideoPlay" @click="startBatchScreening">
        批量筛选
      </el-button>
      <el-button type="info" :icon="Download" @click="exportResults">
        导出结果
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.activeRules }}</div>
              <div class="stats-label">活跃规则</div>
            </div>
            <el-icon class="stats-icon"><Filter /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.completedTasks }}</div>
              <div class="stats-label">已完成任务</div>
            </div>
            <el-icon class="stats-icon"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.pendingTasks }}</div>
              <div class="stats-label">待执行任务</div>
            </div>
            <el-icon class="stats-icon"><Clock /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalResults }}</div>
              <div class="stats-label">筛选结果</div>
            </div>
            <el-icon class="stats-icon"><DataAnalysis /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- Screening Rules Tab -->
      <el-tab-pane label="筛选规则" name="rules">
        <div class="tab-content">
          <!-- Search and Filter -->
          <div class="search-section">
            <el-form :model="searchForm" inline>
              <el-form-item label="规则名称">
                <el-input 
                  v-model="searchForm.name" 
                  placeholder="请输入规则名称"
                  clearable
                  style="width: 200px"
                />
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px">
                  <el-option label="启用" value="active" />
                  <el-option label="停用" value="inactive" />
                  <el-option label="测试中" value="testing" />
                </el-select>
              </el-form-item>
              <el-form-item label="创建时间">
                <el-date-picker
                  v-model="searchForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  style="width: 240px"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="searchRules">查询</el-button>
                <el-button @click="resetSearch">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- Rules Table -->
          <el-table 
            :data="filteredRules" 
            style="width: 100%"
            v-loading="loading"
          >
            <el-table-column prop="name" label="规则名称" min-width="150">
              <template #default="scope">
                <el-link type="primary" @click="viewRuleDetail(scope.row)">{{ scope.row.name }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="筛选类型" width="100">
              <template #default="scope">
                <el-tag :type="getRuleTypeColor(scope.row.type)">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="getStatusColor(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="matchCount" label="匹配数据量" width="120" />
            <el-table-column prop="createdAt" label="创建时间" width="160" />
            <el-table-column prop="lastExecuted" label="最后执行" width="160" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="editRule(scope.row)">编辑</el-button>
                <el-button size="small" type="success" @click="executeRule(scope.row)">执行</el-button>
                <el-button size="small" type="danger" @click="deleteRule(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- Screening Tasks Tab -->
      <el-tab-pane label="筛选任务" name="tasks">
        <div class="tab-content">
          <!-- Task Statistics -->
          <el-row :gutter="16" class="task-stats">
            <el-col :span="6">
              <el-statistic title="今日任务" :value="taskStats.today" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功任务" :value="taskStats.success" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败任务" :value="taskStats.failed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="平均耗时" :value="taskStats.avgDuration" suffix="s" />
            </el-col>
          </el-row>

          <!-- Tasks Timeline -->
          <el-card class="timeline-card">
            <template #header>
              <span>任务执行时间线</span>
            </template>
            <el-timeline>
              <el-timeline-item
                v-for="task in recentTasks"
                :key="task.id"
                :timestamp="task.timestamp"
                :type="getTaskTimelineType(task.status)"
              >
                <div class="timeline-content">
                  <h4>{{ task.name }}</h4>
                  <p>{{ task.description }}</p>
                  <el-tag :type="getStatusColor(task.status)" size="small">{{ task.status }}</el-tag>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Results Analysis Tab -->
      <el-tab-pane label="结果分析" name="results">
        <div class="tab-content">
          <!-- Charts Section -->
          <el-row :gutter="20" class="charts-section">
            <el-col :span="12">
              <el-card>
                <template #header>筛选结果分布</template>
                <div ref="resultChart" style="height: 300px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>规则效果对比</template>
                <div ref="effectChart" style="height: 300px;"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Top Results Table -->
          <el-card class="top-results-card">
            <template #header>热门筛选结果</template>
            <el-table :data="topResults" style="width: 100%">
              <el-table-column prop="rank" label="排名" width="80" />
              <el-table-column prop="result" label="筛选结果" min-width="200" />
              <el-table-column prop="matchCount" label="匹配次数" width="120" />
              <el-table-column prop="accuracy" label="准确率" width="100">
                <template #default="scope">
                  {{ scope.row.accuracy }}%
                </template>
              </el-table-column>
              <el-table-column prop="ruleName" label="关联规则" min-width="150" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Rule Templates Tab -->
      <el-tab-pane label="规则模板" name="templates">
        <div class="tab-content">
          <div class="template-grid">
            <el-card 
              v-for="template in ruleTemplates" 
              :key="template.id"
              class="template-card"
              @click="useTemplate(template)"
            >
              <template #header>
                <div class="template-header">
                  <span>{{ template.name }}</span>
                  <el-tag size="small" type="info">{{ template.category }}</el-tag>
                </div>
              </template>
              <p class="template-desc">{{ template.description }}</p>
              <div class="template-meta">
                <span>使用次数: {{ template.usageCount }}</span>
                <span>成功率: {{ template.successRate }}%</span>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="isEditing ? '编辑筛选规则' : '新建筛选规则'"
      width="800px"
    >
      <el-form :model="ruleForm" :rules="ruleFormRules" ref="ruleFormRef" label-width="120px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="筛选类型" prop="type">
          <el-select v-model="ruleForm.type" placeholder="请选择筛选类型">
            <el-option label="条件筛选" value="condition" />
            <el-option label="模糊匹配" value="fuzzy" />
            <el-option label="正则匹配" value="regex" />
            <el-option label="机器学习" value="ml" />
          </el-select>
        </el-form-item>
        <el-form-item label="规则配置" prop="config">
          <el-input 
            v-model="ruleForm.config" 
            type="textarea" 
            :rows="6"
            placeholder="请输入JSON格式的规则配置"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="ruleForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入规则描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveRule">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, VideoPlay, Download, Filter, CircleCheck, Clock, DataAnalysis,
  RefreshLeft, Setting, Document 
} from '@element-plus/icons-vue'

// Reactive data
const activeTab = ref('rules')
const loading = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)

// Stats data
const stats = reactive({
  activeRules: 12,
  completedTasks: 156,
  pendingTasks: 3,
  totalResults: 8945
})

// Search form
const searchForm = reactive({
  name: '',
  status: '',
  dateRange: []
})

// Pagination
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// Rule form
const ruleForm = reactive({
  name: '',
  type: '',
  config: '',
  description: ''
})

const ruleFormRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择筛选类型', trigger: 'change' }],
  config: [{ required: true, message: '请输入规则配置', trigger: 'blur' }]
}

// Mock data
const rules = ref([
  {
    id: 1,
    name: '高价值比赛筛选',
    type: 'condition',
    status: 'active',
    matchCount: 245,
    createdAt: '2024-01-20 10:30:00',
    lastExecuted: '2024-01-23 09:15:00'
  },
  {
    id: 2,
    name: '异常数据过滤',
    type: 'regex',
    status: 'active',
    matchCount: 89,
    createdAt: '2024-01-18 14:20:00',
    lastExecuted: '2024-01-23 08:30:00'
  }
])

const taskStats = reactive({
  today: 24,
  success: 22,
  failed: 2,
  avgDuration: 15.6
})

const recentTasks = ref([
  {
    id: 1,
    name: '高价值比赛筛选',
    description: '执行条件筛选规则，匹配高价值比赛数据',
    timestamp: '2024-01-23 09:15:00',
    status: 'success'
  },
  {
    id: 2,
    name: '异常数据过滤',
    description: '执行正则匹配规则，过滤异常数据',
    timestamp: '2024-01-23 08:30:00',
    status: 'success'
  }
])

const topResults = ref([
  { rank: 1, result: '英超联赛', matchCount: 156, accuracy: 95.2, ruleName: '联赛筛选规则' },
  { rank: 2, result: '主胜赔率<2.0', matchCount: 134, accuracy: 88.7, ruleName: '赔率筛选规则' },
  { rank: 3, result: '进球数>2.5', matchCount: 98, accuracy: 82.1, ruleName: '大小球筛选规则' }
])

const ruleTemplates = ref([
  {
    id: 1,
    name: '联赛筛选模板',
    category: '基础筛选',
    description: '按联赛类型进行数据筛选的通用模板',
    usageCount: 45,
    successRate: 92
  },
  {
    id: 2,
    name: '赔率范围模板',
    category: '数值筛选',
    description: '按赔率范围筛选数据的模板',
    usageCount: 32,
    successRate: 87
  }
])

// Computed
const filteredRules = computed(() => {
  return rules.value.filter(rule => {
    if (searchForm.name && !rule.name.includes(searchForm.name)) return false
    if (searchForm.status && rule.status !== searchForm.status) return false
    return true
  })
})

// Methods
const getRuleTypeColor = (type) => {
  const colors = { condition: 'primary', fuzzy: 'success', regex: 'warning', ml: 'danger' }
  return colors[type] || 'info'
}

const getStatusColor = (status) => {
  const colors = { active: 'success', inactive: 'danger', testing: 'warning', success: 'success', failed: 'danger' }
  return colors[status] || 'info'
}

const getTaskTimelineType = (status) => {
  return status === 'success' ? 'success' : status === 'failed' ? 'danger' : 'primary'
}

const searchRules = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('查询完成')
  }, 500)
}

const resetSearch = () => {
  Object.assign(searchForm, {
    name: '',
    status: '',
    dateRange: []
  })
}

const viewRuleDetail = (rule) => {
  ElMessage.info(`查看规则详情: ${rule.name}`)
}

const editRule = (rule) => {
  isEditing.value = true
  Object.assign(ruleForm, rule)
  showCreateDialog.value = true
}

const executeRule = (rule) => {
  ElMessage.success(`开始执行规则: ${rule.name}`)
}

const deleteRule = (rule) => {
  ElMessageBox.confirm(`确定要删除规则"${rule.name}"吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  })
}

const startBatchScreening = () => {
  ElMessage.info('开始批量筛选任务')
}

const exportResults = () => {
  ElMessage.info('导出筛选结果')
}

const useTemplate = (template) => {
  ElMessage.info(`使用模板: ${template.name}`)
}

const saveRule = () => {
  ElMessage.success(isEditing.value ? '规则更新成功' : '规则创建成功')
  showCreateDialog.value = false
  resetRuleForm()
}

const resetRuleForm = () => {
  Object.assign(ruleForm, {
    name: '',
    type: '',
    config: '',
    description: ''
  })
  isEditing.value = false
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
}

onMounted(() => {
  // Initialize charts and load data
  console.log('Screening Management mounted')
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

/* 添加标签样式以解决标签太靠边缘的问题 */
:deep(.el-table .el-tag) {
  margin: 0 2px;
  padding: 0 6px;
}

.search-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.task-stats {
  margin-bottom: 20px;
}

.timeline-card {
  margin-top: 16px;
}

.timeline-content h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.timeline-content p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
}

.charts-section {
  margin-bottom: 20px;
}

.top-results-card {
  margin-top: 20px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.template-card {
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.template-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}
</style>