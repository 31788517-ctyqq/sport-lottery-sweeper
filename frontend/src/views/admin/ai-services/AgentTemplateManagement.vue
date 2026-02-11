<template>
  <div class="agent-template-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>📋 智能体模板管理</h3>
            <p class="subtitle">管理智能体模板，支持快速创建和配置智能体</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addTemplate">创建模板</el-button>
            <el-button @click="refreshTemplates">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-input v-model="searchQuery" placeholder="搜索模板名称" @keyup.enter="searchTemplates" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="typeFilter" placeholder="模板类型" style="width: 100%;" @change="filterTemplates">
            <el-option label="全部类型" value="" />
            <el-option label="监控" value="monitor" />
            <el-option label="推荐" value="recommendation" />
            <el-option label="预测" value="prediction" />
            <el-option label="分析" value="analysis" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="publishedFilter" placeholder="发布状态" style="width: 100%;" @change="filterTemplates">
            <el-option label="全部状态" value="" />
            <el-option label="已发布" value="true" />
            <el-option label="未发布" value="false" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="searchTemplates">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>

      <!-- 批量操作工具栏 -->
      <div v-if="selectedTemplates.length > 0" class="batch-operations">
        <el-alert
          :title="`已选择 ${selectedTemplates.length} 个模板`"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px;"
        />
        <div class="batch-buttons">
          <el-button 
            type="success" 
            size="small" 
            @click="publishSelected"
            :disabled="!hasUnpublishedTemplates"
          >
            <i class="el-icon-video-play"></i>
            批量发布
          </el-button>
          <el-button 
            type="warning" 
            size="small" 
            @click="unpublishSelected"
            :disabled="!hasPublishedTemplates"
          >
            <i class="el-icon-video-pause"></i>
            批量取消发布
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            @click="deleteSelected"
            :disabled="selectedTemplates.length === 0"
          >
            <i class="el-icon-delete"></i>
            批量删除
          </el-button>
          <el-button 
            size="small" 
            @click="clearSelection"
          >
            <i class="el-icon-close"></i>
            取消选择
          </el-button>
        </div>
      </div>

      <!-- 模板表格 -->
      <el-table 
        :data="filteredTemplates" 
        style="width: 100%" 
        stripe 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="150" />
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="template_type" label="类型" width="150">
          <template #default="scope">
            <el-tag :type="getTemplateTypeTag(scope.row.template_type)">
              {{ scope.row.template_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="published" label="发布状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.published ? 'success' : 'info'">
              {{ scope.row.published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="120" />
        <el-table-column prop="success_rate" label="成功率" width="120">
          <template #default="scope">
            {{ scope.row.success_rate }}%
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="120">
          <template #default="scope">
            <el-tag :type="getDifficultyTag(scope.row.difficulty)">
              {{ scope.row.difficulty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewTemplateDetail(scope.row)">详情</el-button>
            <el-button 
              size="small" 
              :type="scope.row.published ? 'warning' : 'success'"
              @click="toggleTemplatePublish(scope.row)"
            >
              {{ scope.row.published ? '取消发布' : '发布' }}
            </el-button>
            <el-button size="small" type="primary" @click="editTemplate(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalTemplates"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <!-- 添加/编辑模板对话框 -->
      <el-dialog 
        v-model="templateDialogVisible" 
        :title="editingTemplate ? '编辑模板' : '创建模板'" 
        width="600px"
      >
        <el-form :model="templateForm" :rules="templateRules" ref="templateFormRef" label-width="100px">
          <el-form-item label="模板名称" prop="name">
            <el-input v-model="templateForm.name" placeholder="输入模板名称" />
          </el-form-item>
          
          <el-form-item label="模板类型" prop="template_type">
            <el-select v-model="templateForm.template_type" placeholder="选择模板类型" style="width: 100%;">
              <el-option label="监控" value="monitor" />
              <el-option label="推荐" value="recommendation" />
              <el-option label="预测" value="prediction" />
              <el-option label="分析" value="analysis" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input 
              v-model="templateForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="输入模板描述（可选）"
            />
          </el-form-item>
          
          <el-form-item label="分类">
            <el-input v-model="templateForm.category" placeholder="输入分类（可选）" />
          </el-form-item>
          
          <el-form-item label="标签">
            <el-select
              v-model="templateForm.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入标签"
              style="width: 100%;"
            >
              <el-option
                v-for="tag in availableTags"
                :key="tag"
                :label="tag"
                :value="tag"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="难度级别">
            <el-select v-model="templateForm.difficulty" placeholder="选择难度级别">
              <el-option label="简单" value="easy" />
              <el-option label="中等" value="medium" />
              <el-option label="困难" value="hard" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="智能体配置">
            <el-input 
              v-model="templateForm.agent_config_str"
              type="textarea"
              :rows="4"
              placeholder="输入智能体配置（JSON格式）"
            />
          </el-form-item>
          
          <el-form-item label="链配置">
            <el-input 
              v-model="templateForm.chain_config_str"
              type="textarea"
              :rows="4"
              placeholder="输入链配置（JSON格式）"
            />
          </el-form-item>
          
          <el-form-item label="是否发布">
            <el-switch v-model="templateForm.published" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="templateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate">确定</el-button>
        </template>
      </el-dialog>

      <!-- 模板详情对话框 -->
      <el-dialog 
        v-model="templateDetailDialogVisible" 
        title="模板详情"
        width="800px"
      >
        <div v-if="currentTemplateDetail" class="template-detail-container">
          <!-- 基本信息 -->
          <el-card class="detail-section" shadow="never">
            <template #header>
              <div class="detail-header">
                <span>基本信息</span>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="useTemplate(currentTemplateDetail)"
                >
                  使用此模板
                </el-button>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="模板ID">{{ currentTemplateDetail.id }}</el-descriptions-item>
              <el-descriptions-item label="名称">{{ currentTemplateDetail.name }}</el-descriptions-item>
              <el-descriptions-item label="类型">
                <el-tag :type="getTemplateTypeTag(currentTemplateDetail.template_type)">
                  {{ currentTemplateDetail.template_type }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="发布状态">
                <el-tag :type="currentTemplateDetail.published ? 'success' : 'info'">
                  {{ currentTemplateDetail.published ? '已发布' : '未发布' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="分类">{{ currentTemplateDetail.category || '未分类' }}</el-descriptions-item>
              <el-descriptions-item label="难度">
                <el-tag :type="getDifficultyTag(currentTemplateDetail.difficulty)">
                  {{ currentTemplateDetail.difficulty }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="使用次数">{{ currentTemplateDetail.usage_count }}</el-descriptions-item>
              <el-descriptions-item label="成功率">{{ currentTemplateDetail.success_rate }}%</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ currentTemplateDetail.created_at }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ currentTemplateDetail.updated_at }}</el-descriptions-item>
              <el-descriptions-item label="描述" span="2">
                {{ currentTemplateDetail.description || '无描述' }}
              </el-descriptions-item>
              <el-descriptions-item label="标签" span="2">
                <el-tag 
                  v-for="tag in currentTemplateDetail.tags" 
                  :key="tag"
                  style="margin-right: 5px; margin-bottom: 5px;"
                >
                  {{ tag }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 配置预览 -->
          <el-card class="detail-section" shadow="never" style="margin-top: 20px;">
            <template #header>
              <span>配置预览</span>
            </template>
            <el-tabs>
              <el-tab-pane label="智能体配置">
                <pre class="config-preview">{{ JSON.stringify(currentTemplateDetail.agent_config, null, 2) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="链配置">
                <pre class="config-preview">{{ JSON.stringify(currentTemplateDetail.chain_config, null, 2) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="工具配置">
                <pre class="config-preview">{{ JSON.stringify(currentTemplateDetail.tool_config, null, 2) }}</pre>
              </el-tab-pane>
            </el-tabs>
          </el-card>

          <!-- 使用统计 -->
          <el-card class="detail-section" shadow="never" style="margin-top: 20px;">
            <template #header>
              <div class="detail-header">
                <span>使用统计</span>
                <el-button size="small" @click="viewUsageStatistics(currentTemplateDetail)">查看详细统计</el-button>
              </div>
            </template>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="metric-item">
                  <div class="metric-label">总使用次数</div>
                  <div class="metric-value">{{ currentTemplateDetail.usage_count }}</div>
                  <el-progress :percentage="Math.min(currentTemplateDetail.usage_count / 100 * 100, 100)" :stroke-width="6" />
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-item">
                  <div class="metric-label">平均成功率</div>
                  <div class="metric-value">{{ currentTemplateDetail.success_rate }}%</div>
                  <el-progress :percentage="currentTemplateDetail.success_rate" :stroke-width="6" status="success" />
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-item">
                  <div class="metric-label">平均执行时间</div>
                  <div class="metric-value">{{ currentTemplateDetail.avg_execution_time }}ms</div>
                  <el-progress :percentage="Math.min(currentTemplateDetail.avg_execution_time / 1000 * 100, 100)" :stroke-width="6" status="warning" />
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>
        
        <template #footer>
          <el-button @click="templateDetailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="editTemplate(currentTemplateDetail)">编辑</el-button>
          <el-button 
            :type="currentTemplateDetail?.published ? 'warning' : 'success'"
            @click="toggleTemplatePublish(currentTemplateDetail)"
          >
            {{ currentTemplateDetail?.published ? '取消发布' : '发布' }}
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import agentApi from '@/api/agent'

// AI_WORKING: coder1 @2026-02-01T14:30:00 - 创建智能体模板管理前端界面
// AI_WORKING: coder1 @2026-02-01T14:48:00 - 集成真实API，优化界面
// 响应式数据
const loading = ref(false)
const templateDialogVisible = ref(false)
const templateDetailDialogVisible = ref(false)
const editingTemplate = ref(null)

// 模板数据（从API获取）
const templates = ref([])

// 筛选和分页数据
const filteredTemplates = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalTemplates = ref(0)
const searchQuery = ref('')
const typeFilter = ref('')
const publishedFilter = ref('')

// 选中模板
const selectedTemplates = ref([])

// 模板表单
const templateForm = reactive({
  id: '',
  name: '',
  template_type: '',
  description: '',
  category: '',
  tags: [],
  difficulty: 'medium',
  agent_config_str: '',
  chain_config_str: '',
  published: false
})

const templateRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  template_type: [
    { required: true, message: '请选择模板类型', trigger: 'change' }
  ]
}

// 当前模板详情
const currentTemplateDetail = ref(null)

// 可用标签
const availableTags = ref(['监控', '推荐', '预测', '分析', '基础', '高级', '标准', '综合', '实时', '批量', '自动'])

// 计算属性
const hasUnpublishedTemplates = computed(() => {
  return selectedTemplates.value.some(template => !template.published)
})

const hasPublishedTemplates = computed(() => {
  return selectedTemplates.value.some(template => template.published)
})

// 方法
const getTemplateTypeTag = (type) => {
  const types = {
    monitor: 'primary',
    recommendation: 'success',
    prediction: 'warning',
    analysis: 'info'
  }
  return types[type] || 'info'
}

const getDifficultyTag = (difficulty) => {
  const types = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return types[difficulty] || 'info'
}

// 获取模板列表
const fetchTemplates = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...(typeFilter.value && { template_type: typeFilter.value }),
      ...(publishedFilter.value !== '' && { published: publishedFilter.value === 'true' }),
      ...(searchQuery.value && { name: searchQuery.value })
    }
    
    const response = await agentApi.agentTemplate.getTemplates(params)
    templates.value = response.templates || []
    totalTemplates.value = response.total || 0
    applyFilters()
  } catch (error) {
    console.error('获取模板列表失败:', error)
    ElMessage.error('获取模板列表失败，请检查网络连接或API服务')
    templates.value = []
  } finally {
    loading.value = false
  }
}

const addTemplate = () => {
  editingTemplate.value = null
  Object.assign(templateForm, {
    id: '',
    name: '',
    template_type: '',
    description: '',
    category: '',
    tags: [],
    difficulty: 'medium',
    agent_config_str: '',
    chain_config_str: '',
    published: false
  })
  templateDialogVisible.value = true
}

const editTemplate = (template) => {
  editingTemplate.value = template
  Object.assign(templateForm, {
    id: template.id,
    name: template.name,
    template_type: template.template_type,
    description: template.description || '',
    category: template.category || '',
    tags: template.tags || [],
    difficulty: template.difficulty || 'medium',
    agent_config_str: JSON.stringify(template.agent_config || {}, null, 2),
    chain_config_str: JSON.stringify(template.chain_config || {}, null, 2),
    published: template.published || false
  })
  templateDialogVisible.value = true
}

const viewTemplateDetail = (template) => {
  currentTemplateDetail.value = template
  templateDetailDialogVisible.value = true
}

const useTemplate = (template) => {
  ElMessage.success(`已选择模板 "${template.name}"，开始创建智能体...`)
  // 实际应用中这里可以跳转到智能体创建页面
}

const viewUsageStatistics = (template) => {
  ElMessage.info(`查看 ${template.name} 的使用统计...`)
}

const toggleTemplatePublish = async (template) => {
  try {
    const actionText = template.published ? '取消发布' : '发布'
    
    await ElMessageBox.confirm(
      `确定要${actionText}模板 "${template.name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: template.published ? 'warning' : 'success'
      }
    )
    
    if (template.published) {
      await agentApi.agentTemplate.unpublishTemplate(template.id)
      template.published = false
    } else {
      await agentApi.agentTemplate.publishTemplate(template.id)
      template.published = true
    }
    
    template.updated_at = new Date().toISOString().slice(0, 19).replace('T', ' ')
    ElMessage.success(`模板已${template.published ? '发布' : '取消发布'}`)
    
    // 刷新列表
    fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发布/取消发布失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

const saveTemplate = async () => {
  // 验证表单
  const formRef = templateFormRef.value
  if (!formRef) return
  
  try {
    await formRef.validate()
  } catch (error) {
    return
  }
  
  // 验证JSON格式
  let agentConfig = {}
  let chainConfig = {}
  try {
    if (templateForm.agent_config_str) {
      agentConfig = JSON.parse(templateForm.agent_config_str)
    }
    if (templateForm.chain_config_str) {
      chainConfig = JSON.parse(templateForm.chain_config_str)
    }
  } catch (error) {
    ElMessage.error('配置JSON格式错误')
    return
  }
  
  loading.value = true
  try {
    const templateData = {
      name: templateForm.name,
      template_type: templateForm.template_type,
      description: templateForm.description,
      category: templateForm.category,
      tags: templateForm.tags,
      difficulty: templateForm.difficulty,
      agent_config: agentConfig,
      chain_config: chainConfig,
      published: templateForm.published
    }
    
    if (editingTemplate.value) {
      // 编辑现有模板
      await agentApi.agentTemplate.updateTemplate(templateForm.id, templateData)
      ElMessage.success('模板更新成功')
    } else {
      // 添加新模板
      await agentApi.agentTemplate.createTemplate(templateData)
      ElMessage.success('模板添加成功')
    }
    
    templateDialogVisible.value = false
    fetchTemplates()
  } catch (error) {
    console.error('保存模板失败:', error)
    ElMessage.error(`保存失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const searchTemplates = () => {
  currentPage.value = 1
  fetchTemplates()
}

const filterTemplates = () => {
  currentPage.value = 1
  fetchTemplates()
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  publishedFilter.value = ''
  currentPage.value = 1
  fetchTemplates()
}

const applyFilters = () => {
  let result = [...templates.value]
  
  // 前端筛选（辅助筛选，主要筛选已在API层完成）
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(template => 
      template.name.toLowerCase().includes(query) || 
      (template.description && template.description.toLowerCase().includes(query))
    )
  }
  
  if (typeFilter.value) {
    result = result.filter(template => template.template_type === typeFilter.value)
  }
  
  if (publishedFilter.value !== '') {
    const published = publishedFilter.value === 'true'
    result = result.filter(template => template.published === published)
  }
  
  filteredTemplates.value = result
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTemplates()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchTemplates()
}

// 批量操作方法
const handleSelectionChange = (selection) => {
  selectedTemplates.value = selection
}

const publishSelected = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要发布选中的 ${selectedTemplates.value.length} 个模板吗？`,
      '确认发布',
      { type: 'warning' }
    )
    
    const publishPromises = selectedTemplates.value
      .filter(template => !template.published)
      .map(template => agentApi.agentTemplate.publishTemplate(template.id))
    
    await Promise.all(publishPromises)
    
    ElMessage.success(`已成功发布 ${publishPromises.length} 个模板`)
    clearSelection()
    fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量发布失败:', error)
      ElMessage.error('批量发布失败')
    }
  }
}

const unpublishSelected = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要取消发布选中的 ${selectedTemplates.value.length} 个模板吗？`,
      '确认取消发布',
      { type: 'warning' }
    )
    
    const unpublishPromises = selectedTemplates.value
      .filter(template => template.published)
      .map(template => agentApi.agentTemplate.unpublishTemplate(template.id))
    
    await Promise.all(unpublishPromises)
    
    ElMessage.success(`已成功取消发布 ${unpublishPromises.length} 个模板`)
    clearSelection()
    fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量取消发布失败:', error)
      ElMessage.error('批量取消发布失败')
    }
  }
}

const deleteSelected = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTemplates.value.length} 个模板吗？此操作不可恢复。`,
      '确认删除',
      { type: 'error' }
    )
    
    const deletePromises = selectedTemplates.value
      .map(template => agentApi.agentTemplate.deleteTemplate(template.id))
    
    await Promise.all(deletePromises)
    
    ElMessage.success(`已成功删除 ${deletePromises.length} 个模板`)
    clearSelection()
    fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const clearSelection = () => {
  selectedTemplates.value = []
}

const refreshTemplates = () => {
  fetchTemplates()
  ElMessage.success('模板列表已刷新')
}

// 初始化数据
onMounted(() => {
  fetchTemplates()
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

/* 模板详情对话框样式 */
.template-detail-container {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-item {
  text-align: center;
  padding: 15px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.config-preview {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  overflow-x: auto;
  max-height: 300px;
}

.batch-operations {
  margin-bottom: 20px;
}

.batch-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
<!-- AI_DONE: coder1 @2026-02-01T14:30:00 -->