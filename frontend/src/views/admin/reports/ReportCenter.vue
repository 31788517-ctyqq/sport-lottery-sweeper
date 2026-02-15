<template>
  <div class="report-center">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">报告中心</span>
          <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick">
            <el-tab-pane label="自动报告" name="auto"></el-tab-pane>
            <el-tab-pane label="自定义报告" name="custom"></el-tab-pane>
            <el-tab-pane label="模板管理" name="templates"></el-tab-pane>
            <el-tab-pane label="报告分发" name="distribution"></el-tab-pane>
          </el-tabs>
        </div>
      </template>

      <!-- 自动报告 -->
      <div v-if="activeTab === 'auto'" class="tab-content">
        <div class="section-header">
          <h3>自动生成的报告</h3>
          <el-button type="primary" size="small" @click="refreshAutoReports">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        
        <el-table :data="autoReports" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="报告标题" min-width="200">
            <template #default="scope">
              <el-link type="primary" @click="viewReport(scope.row)">{{ scope.row.title }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="120">
            <template #default="scope">
              <el-tag :type="getReportTypeColor(scope.row.type)">{{ scope.row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="generatedAt" label="生成时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.generatedAt) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusColor(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="viewReport(scope.row)">查看</el-button>
              <el-button size="small" type="success" @click="downloadReport(scope.row)">下载</el-button>
              <el-button size="small" type="info" @click="shareReport(scope.row)">分享</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 自定义报告 -->
      <div v-if="activeTab === 'custom'" class="tab-content">
        <div class="section-header">
          <h3>自定义报告生成</h3>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建自定义报告
          </el-button>
        </div>
        
        <el-form :model="customReportForm" label-width="120px" class="custom-form">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="报告名称">
                <el-input v-model="customReportForm.name" placeholder="请输入报告名称"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="报告类型">
                <el-select v-model="customReportForm.type" placeholder="选择报告类型">
                  <el-option label="数据分析报告" value="analysis"></el-option>
                  <el-option label="运营报告" value="operation"></el-option>
                  <el-option label="监控报告" value="monitor"></el-option>
                  <el-option label="统计报告" value="statistics"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="数据源">
                <el-select v-model="customReportForm.dataSource" placeholder="选择数据源" multiple>
                  <el-option label="用户数据" value="users"></el-option>
                  <el-option label="比赛数据" value="matches"></el-option>
                  <el-option label="爬虫任务" value="tasks"></el-option>
                  <el-option label="系统日志" value="logs"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="customReportForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                ></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="定时生成">
                <el-switch v-model="customReportForm.scheduled"></el-switch>
                <el-select v-if="customReportForm.scheduled" v-model="customReportForm.scheduleType" style="margin-left: 10px; width: 120px;">
                  <el-option label="每日" value="daily"></el-option>
                  <el-option label="每周" value="weekly"></el-option>
                  <el-option label="每月" value="monthly"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <el-button type="primary" @click="generateCustomReport">生成报告</el-button>
            <el-button @click="resetCustomForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 模板管理 -->
      <div v-if="activeTab === 'templates'" class="tab-content">
        <div class="section-header">
          <h3>报告模板管理</h3>
          <el-button type="primary" @click="showTemplateDialog = true">
            <el-icon><Plus /></el-icon>
            新建模板
          </el-button>
        </div>
        
        <el-table :data="templates" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="模板名称" min-width="150"></el-table-column>
          <el-table-column prop="category" label="分类" width="120">
            <template #default="scope">
              <el-tag>{{ scope.row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200"></el-table-column>
          <el-table-column prop="updatedAt" label="更新时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.updatedAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="editTemplate(scope.row)">编辑</el-button>
              <el-button size="small" type="success" @click="useTemplate(scope.row)">使用</el-button>
              <el-button size="small" type="danger" @click="deleteTemplate(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 报告分发 -->
      <div v-if="activeTab === 'distribution'" class="tab-content">
        <div class="section-header">
          <h3>报告分发管理</h3>
          <el-button type="primary" @click="showDistributionDialog = true">
            <el-icon><Plus /></el-icon>
            新建分发规则
          </el-button>
        </div>
        
        <el-table :data="distributionRules" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="规则名称" min-width="150"></el-table-column>
          <el-table-column prop="reportType" label="报告类型" width="120">
            <template #default="scope">
              <el-tag>{{ scope.row.reportType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="recipients" label="接收者" min-width="200">
            <template #default="scope">
              <el-tag v-for="recipient in scope.row.recipients" :key="recipient" size="small" style="margin: 2px;">
                {{ recipient }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="frequency" label="频率" width="100">
            <template #default="scope">
              {{ scope.row.frequency }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="scope">
              <el-switch v-model="scope.row.enabled" @change="toggleDistribution(scope.row)"></el-switch>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="editDistribution(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteDistribution(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 创建自定义报告对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建自定义报告" width="60%" :before-close="closeCreateDialog">
      <p>自定义报告创建功能开发中...</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeCreateDialog">取消</el-button>
          <el-button type="primary" @click="closeCreateDialog">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 模板编辑对话框 -->
    <el-dialog v-model="showTemplateDialog" title="模板管理" width="50%" :before-close="closeTemplateDialog">
      <p>模板编辑功能开发中...</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeTemplateDialog">取消</el-button>
          <el-button type="primary" @click="closeTemplateDialog">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 分发规则对话框 -->
    <el-dialog v-model="showDistributionDialog" title="分发规则管理" width="50%" :before-close="closeDistributionDialog">
      <p>分发规则管理功能开发中...</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDistributionDialog">取消</el-button>
          <el-button type="primary" @click="closeDistributionDialog">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

// 响应式数据
const activeTab = ref('auto')
const loading = ref(false)
const showCreateDialog = ref(false)
const showTemplateDialog = ref(false)
const showDistributionDialog = ref(false)

// 自动报告数据
const autoReports = ref([
  {
    id: 1,
    title: '每日系统健康报告 - 2024-02-14',
    type: '系统健康',
    generatedAt: '2024-02-14 09:00:00',
    status: '已完成'
  },
  {
    id: 2,
    title: '周度用户活跃度分析',
    type: '用户分析',
    generatedAt: '2024-02-12 18:00:00',
    status: '已完成'
  },
  {
    id: 3,
    title: '爬虫任务执行报告',
    type: '任务监控',
    generatedAt: '2024-02-14 08:30:00',
    status: '进行中'
  }
])

// 自定义报告表单
const customReportForm = reactive({
  name: '',
  type: '',
  dataSource: [],
  dateRange: [],
  scheduled: false,
  scheduleType: 'daily'
})

// 模板数据
const templates = ref([
  {
    id: 1,
    name: '系统健康日报',
    category: '系统',
    description: '包含系统运行状态、性能指标和健康检查的日报模板',
    updatedAt: '2024-02-14 10:00:00'
  },
  {
    id: 2,
    name: '用户行为分析周报',
    category: '用户',
    description: '用户注册、活跃度、行为模式的周度分析报告',
    updatedAt: '2024-02-13 15:30:00'
  }
])

// 分发规则数据
const distributionRules = ref([
  {
    id: 1,
    name: '系统管理员日报推送',
    reportType: '系统健康',
    recipients: ['admin@company.com', 'ops@company.com'],
    frequency: '每日',
    enabled: true
  },
  {
    id: 2,
    name: '管理层周报分发',
    reportType: '综合分析',
    recipients: ['manager@company.com'],
    frequency: '每周',
    enabled: true
  }
])

// 方法
const handleTabClick = (tab) => {
  console.log('切换到标签:', tab.name)
}

const refreshAutoReports = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('报告列表已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const viewReport = (report) => {
  ElMessage.info(`查看报告: ${report.title}`)
}

const downloadReport = (report) => {
  ElMessage.success(`开始下载: ${report.title}`)
}

const shareReport = (report) => {
  ElMessage.info(`分享报告: ${report.title}`)
}

const generateCustomReport = async () => {
  if (!customReportForm.name || !customReportForm.type) {
    ElMessage.warning('请填写完整的报告信息')
    return
  }
  ElMessage.success('自定义报告生成任务已提交')
  resetCustomForm()
}

const resetCustomForm = () => {
  Object.assign(customReportForm, {
    name: '',
    type: '',
    dataSource: [],
    dateRange: [],
    scheduled: false,
    scheduleType: 'daily'
  })
}

const editTemplate = (template) => {
  ElMessage.info(`编辑模板: ${template.name}`)
}

const useTemplate = (template) => {
  ElMessage.success(`使用模板: ${template.name}`)
  activeTab.value = 'custom'
}

const deleteTemplate = (template) => {
  ElMessage.info(`删除模板: ${template.name}`)
}

const editDistribution = (rule) => {
  ElMessage.info(`编辑分发规则: ${rule.name}`)
}

const toggleDistribution = (rule) => {
  ElMessage.success(`${rule.name} ${rule.enabled ? '已启用' : '已禁用'}`)
}

const deleteDistribution = (rule) => {
  ElMessage.info(`删除分发规则: ${rule.name}`)
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
}

const closeTemplateDialog = () => {
  showTemplateDialog.value = false
}

const closeDistributionDialog = () => {
  showDistributionDialog.value = false
}

const getReportTypeColor = (type) => {
  const colors = {
    '系统健康': 'success',
    '用户分析': 'primary',
    '任务监控': 'warning',
    '数据分析': 'info'
  }
  return colors[type] || 'default'
}

const getStatusColor = (status) => {
  const colors = {
    '已完成': 'success',
    '进行中': 'warning',
    '失败': 'danger',
    '待处理': 'info'
  }
  return colors[status] || 'default'
}

const formatDateTime = (datetime) => {
  return datetime
}

// 生命周期
onMounted(() => {
  console.log('报告中心已加载')
})
</script>

<style scoped>
.report-center {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-right: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

.tab-content {
  min-height: 400px;
}

.custom-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.dialog-footer {
  text-align: right;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>