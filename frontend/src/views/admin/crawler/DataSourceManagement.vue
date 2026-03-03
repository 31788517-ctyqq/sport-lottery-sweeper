<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总数据源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.online }}</div>
            <div class="stat-label">在线源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.offline }}</div>
            <div class="stat-label">离线源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.errorRate }}%</div>
            <div class="stat-label">错误率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ poolHealth.ipActive }}/{{ poolHealth.ipTarget }}</div>
            <div class="stat-label">IP可用/目标（缺口 {{ poolHealth.ipGap }}）</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ poolHealth.headerDomains }}/{{ poolHealth.lowQualityHeaders }}</div>
            <div class="stat-label">Headers域名数/低质量总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ poolHealth.bindingCoverage }}%</div>
            <div class="stat-label">数据源Header绑定覆盖率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="box-card" style="margin-bottom: 20px;">
      <div class="sync-status-bar">
        <div class="sync-status-main">
          <div class="sync-status-title">100球自动同步状态</div>
          <div class="sync-status-meta">
            <span>500w最新期号：{{ syncStatus.latest_issue_no || '-' }}</span>
            <span>100球最后成功期号：{{ syncStatus.last_success_issue_no || '-' }}</span>
            <span>上次成功时间：{{ formatDate(syncStatus.last_sync_at) }}</span>
            <span>下次同步时间：{{ formatDate(syncStatus.next_sync_at) }}</span>
          </div>
          <div v-if="syncStatus.last_error" class="sync-status-error">
            最近错误：{{ syncStatus.last_error }}
          </div>
        </div>
        <div class="sync-status-actions">
          <el-tag :type="syncStatusTagType">{{ syncStatus.sync_status || 'idle' }}</el-tag>
          <el-button
            type="primary"
            size="small"
            :loading="syncStatus.runningNow"
            @click="runSourceSyncNow"
          >
            立即同步
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 工具栏和筛选栏 -->
    <el-card class="box-card" style="margin-bottom: 20px;">
      <div class="toolbar">
        <el-button type="primary" @click="handleAdd">+ 新增数据源</el-button>
        <el-button type="success" @click="handleAdd100qiu">+ 创建100球数据源</el-button>
        
        <!-- 筛选条件 -->
        <div class="filter-section">
          <el-select v-model="filters.category" placeholder="选择分类" clearable style="width: 120px; margin-left: 20px;">
            <el-option label="比赛数据" value="match_data"></el-option>
            <el-option label="情报数据" value="intelligence_data"></el-option>
            <el-option label="赔率数据" value="odds_data"></el-option>
          </el-select>
          
          <el-select v-model="filters.status" placeholder="选择状态" clearable style="width: 120px; margin-left: 10px;">
            <el-option label="在线" value="online"></el-option>
            <el-option label="离线" value="offline"></el-option>
          </el-select>
          
          <el-input 
            v-model="filters.search" 
            placeholder="搜索名称或源ID..." 
            style="width: 200px; margin-left: 10px;"
            @keyup.enter="loadData"
          />
          
          <el-button icon="el-icon-search" @click="loadData" style="margin-left: 10px;">搜索</el-button>
          <el-button @click="resetFilters" style="margin-left: 10px;">重置</el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="box-card">
      <template #header>
        <span class="card-header">数据源管理</span>
      </template>

      <el-table :data="tableData" border style="width: 100%" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" :show-overflow-tooltip="false">
          <template #default="scope">
            <span style="white-space: nowrap;">{{ scope.row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source_id" label="源ID" width="100" />
        <el-table-column prop="name" label="数据源名称" min-width="150" />
        <el-table-column label="分类" width="100">
          <template #default="scope">
            {{ getCategory(scope.row) }}
          </template>
        </el-table-column>
        <el-table-column prop="url" label="地址" show-overflow-tooltip min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status==='online'?'success':'danger'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_rate" label="错误率" width="100">
          <template #default="scope">
            {{ (scope.row.error_rate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320">
          <template #default="scope">
            <el-button size="small" @click="checkHealth(scope.row)">健康检查</el-button>
            <el-button 
              v-if="is100qiuDataSource(scope.row)" 
              size="small" 
              type="success" 
              @click="handleFetch(scope.row)"
              :loading="fetchingIds.includes(scope.row.id)"
            >
              获取
            </el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 批量操作栏 -->
      <div class="batch-actions" v-if="selectedIds.length > 0" style="margin-top: 10px; padding: 10px; background-color: #f5f7fa; border-radius: 4px;">
        已选择 {{ selectedIds.length }} 项
        <el-button type="danger" size="small" @click="batchDelete" style="margin-left: 20px;">批量删除</el-button>
        <el-button size="small" @click="selectedIds = []">取消选择</el-button>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" style="margin-top: 20px;">
        <el-pagination
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
        ></el-pagination>
      </div>
    </el-card>
  </div>

  <!-- 新增数据源弹窗 -->
  <el-dialog v-model="addDialogVisible" title="新增数据源" width="500px">
    <el-form :model="formData" label-width="80px" class="dialog-form">
      <el-form-item label="名称" required>
        <el-input v-model="formData.name" placeholder="请输入数据源名称" />
      </el-form-item>
      <el-form-item label="分类" required>
        <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%;">
          <el-option label="比赛数据" value="match_data"></el-option>
          <el-option label="情报数据" value="intelligence_data"></el-option>
          <el-option label="赔率数据" value="odds_data"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="URL" required>
        <el-input v-model="formData.url" placeholder="请输入接口地址或文件路径" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="formData.status" active-value="online" inactive-value="offline" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="addDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveDataSource">确定</el-button>
    </template>
  </el-dialog>

  <!-- 创建100球数据源弹窗 -->
  <el-dialog v-model="add100qiuDialogVisible" title="创建100球数据源" width="500px">
    <el-form :model="form100qiuData" label-width="120px" class="dialog-form">
      <el-form-item label="date_time" required>
        <el-input v-model="form100qiuData.date_time" placeholder="请输入date_time参数（如：260155）" />
      </el-form-item>
      <el-form-item label="更新频率(分钟)">
        <el-input-number v-model="form100qiuData.update_frequency" :min="1" :max="1440" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="add100qiuDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save100qiuDataSource">确定</el-button>
    </template>
  </el-dialog>

  <!-- 编辑数据源弹窗 -->
  <el-dialog v-model="editDialogVisible" title="编辑数据源" width="500px">
    <el-form :model="editFormData" label-width="80px" class="dialog-form">
      <el-tabs v-model="editActiveTab">
        <el-tab-pane label="基础信息" name="basic">
      <el-form-item label="名称" required>
        <el-input v-model="editFormData.name" placeholder="请输入数据源名称" />
      </el-form-item>
      
      <el-form-item v-if="!editFormData.is100qiu" label="分类" required>
        <el-select v-model="editFormData.category" placeholder="请选择分类" style="width: 100%;">
          <el-option label="比赛数据" value="match_data"></el-option>
          <el-option label="情报数据" value="intelligence_data"></el-option>
          <el-option label="赔率数据" value="odds_data"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item v-if="editFormData.is100qiu" label="date_time" required>
        <el-input v-model="editFormData.date_time" placeholder="请输入date_time参数（如：260155）" />
      </el-form-item>
      
      <el-form-item v-if="editFormData.is100qiu" label="更新频率(分钟)">
        <el-input-number v-model="editFormData.update_frequency" :min="1" :max="1440" />
      </el-form-item>
      
      <el-form-item label="URL" required>
        <el-input v-model="editFormData.url" placeholder="请输入接口地址或文件路径" />
      </el-form-item>
      
      <el-form-item label="状态">
        <el-switch v-model="editFormData.status" active-value="online" inactive-value="offline" />
      </el-form-item>
        </el-tab-pane>
        <el-tab-pane label="请求头绑定" name="headers">
          <div class="bind-header-actions">
            <el-select
              v-model="bindHeaderForm.headerIds"
              multiple
              filterable
              remote
              :remote-method="loadHeaderOptions"
              placeholder="选择请求头（可搜索）"
              style="width: 320px;"
            >
              <el-option
                v-for="item in headerOptions"
                :key="item.id"
                :label="`${item.name} (${item.domain})`"
                :value="item.id"
              />
            </el-select>
            <el-select v-model="bindHeaderForm.priorityOverride" placeholder="优先级覆盖" style="width: 140px;">
              <el-option label="高" :value="3" />
              <el-option label="中" :value="2" />
              <el-option label="低" :value="1" />
            </el-select>
            <el-button size="small" type="primary" @click="bindHeaders">绑定</el-button>
            <el-button size="small" @click="loadHeaderBindings">刷新绑定</el-button>
          </div>
          <el-table :data="headerBindings" size="small" style="width: 100%">
            <el-table-column prop="header.id" label="Header ID" width="90" />
            <el-table-column prop="header.name" label="名称" width="120" />
            <el-table-column prop="header.domain" label="域名" min-width="140" />
            <el-table-column prop="priorityOverride" label="优先级覆盖" width="110" />
            <el-table-column prop="enabled" label="启用" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.enabled ? 'success' : 'info'">
                  {{ scope.row.enabled ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button size="small" @click="toggleBinding(scope.row)">
                  {{ scope.row.enabled ? '禁用' : '启用' }}
                </el-button>
                <el-button size="small" type="danger" @click="removeBinding(scope.row)">解绑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-form>
    <template #footer>
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveEditDataSource">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElSwitch, ElDialog, ElTabs, ElTabPane } from 'element-plus'
import { bindHeadersToDataSource, getHeaderBindings, getHeadersList, getHeaderStats, unbindHeadersFromDataSource } from '@/api/headers'
import { getIpStats } from '@/api/ipPool'

const tableData = ref([])
const fetchingIds = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedIds = ref([]) // 批量选择的ID
const editActiveTab = ref('basic')
const headerBindings = ref([])
const bindHeaderForm = ref({
  headerIds: [],
  priorityOverride: null
})
const headerOptions = ref([])

// 统计数据
const stats = ref({
  total: 0,
  online: 0,
  offline: 0,
  errorRate: 0
})
const poolHealth = ref({
  ipActive: 0,
  ipTarget: 0,
  ipGap: 0,
  headerDomains: 0,
  lowQualityHeaders: 0,
  bindingCoverage: 0
})
const syncStatus = ref({
  sync_status: 'idle',
  latest_issue_no: '',
  last_success_issue_no: '',
  last_sync_at: null,
  next_sync_at: null,
  last_error: '',
  runningNow: false
})

// 筛选条件
const filters = ref({
  category: '',
  status: '',
  search: ''
})

// 弹窗相关
const addDialogVisible = ref(false)
const add100qiuDialogVisible = ref(false)
const editDialogVisible = ref(false) // 添加编辑弹窗
const formData = ref({
  name: '',
  type: 'api',
  url: '',
  category: '', // 添加分类字段
  config: {},
  status: 'online'
})
const form100qiuData = ref({
  date_time: '',
  update_frequency: 60
})
const editFormData = ref({
  id: null,
  name: '',
  url: '',
  category: '',
  status: 'online',
  is100qiu: false,
  date_time: '',
  update_frequency: 60
})

const loadData = async () => {
  try {
    // 构建查询参数
    const queryParams = []
    if (currentPage.value > 1) queryParams.push(`page=${currentPage.value}`)
    if (pageSize.value !== 20) queryParams.push(`size=${pageSize.value}`)
    if (filters.value.category) queryParams.push(`category=${filters.value.category}`)
    if (filters.value.status) queryParams.push(`status=${filters.value.status}`)
    if (filters.value.search) queryParams.push(`search=${encodeURIComponent(filters.value.search)}`)
    
    const queryString = queryParams.length > 0 ? '?' + queryParams.join('&') : ''
    const url = `/api/admin/sources${queryString}`
    
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include'
    })
    const data = await response.json()
    const listData = Array.isArray(data) ? data : (data.data?.items || data.items || [])
    const totalCount = Array.isArray(data) ? listData.length : (data.data?.total || data.total || listData.length)
    const ok = response.ok && (Array.isArray(data) || data.success || data.code === 200)
    
    if (ok) {
      tableData.value = listData
      total.value = totalCount
      
      // 计算统计数据
      calculateStats(listData)
      loadPoolHealth()
      loadSourceSyncStatus()
    } else {
      throw new Error(data?.message || '加载失败')
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('加载数据失败:', error)
  }
}

const loadPoolHealth = async () => {
  try {
    const [ipRes, headerRes] = await Promise.all([getIpStats(), getHeaderStats()])
    const ipPayload = ipRes?.data || ipRes || {}
    const ipData = ipPayload?.data || ipPayload || {}
    const headerPayload = headerRes?.data || headerRes || {}
    const headerData = headerPayload?.data || headerPayload || {}
    const coverage = headerData.capacity?.bindings_coverage || {}

    poolHealth.value = {
      ipActive: Number(ipData.active || 0),
      ipTarget: Number(ipData.activeTarget || 0),
      ipGap: Number(ipData.activeGap || 0),
      headerDomains: Number(headerData.capacity?.domains_count || 0),
      lowQualityHeaders: Number(headerData.capacity?.low_quality_total || 0),
      bindingCoverage: Number(coverage.coverage_rate || 0)
    }
  } catch (error) {
    console.error('加载池健康摘要失败:', error)
  }
}

const loadSourceSyncStatus = async () => {
  try {
    const response = await fetch('/api/v1/admin/source-sync/status', {
      method: 'GET',
      credentials: 'include'
    })
    const data = await response.json()
    if (response.ok && data.success && data.data) {
      syncStatus.value = {
        ...syncStatus.value,
        ...data.data,
        runningNow: false
      }
    }
  } catch (error) {
    console.error('加载自动同步状态失败:', error)
  }
}

const runSourceSyncNow = async () => {
  syncStatus.value.runningNow = true
  try {
    const response = await fetch('/api/v1/admin/source-sync/run-now', {
      method: 'POST',
      credentials: 'include'
    })
    const data = await response.json()
    if (response.ok && data.success) {
      ElMessage.success('已触发同步任务')
      setTimeout(() => {
        loadSourceSyncStatus()
        loadData()
      }, 1200)
    } else {
      throw new Error(data.message || '触发失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '触发失败')
  } finally {
    syncStatus.value.runningNow = false
  }
}

const syncStatusTagType = computed(() => {
  const status = syncStatus.value.sync_status
  if (status === 'success') return 'success'
  if (status === 'running') return 'warning'
  if (status === 'degraded' || status === 'failed') return 'danger'
  return 'info'
})

const calculateStats = (items) => {
  const total = items.length
  const online = items.filter(item => item.status === 'online').length
  const offline = items.filter(item => item.status === 'offline').length
  // 正确识别100球数据源（虽然不再在UI中显示，但用于获取功能）
  const hundredQiu = items.filter(item => 
    item.type === '100qiu' || 
    (item.config && item.config.source_type === '100qiu') ||
    (typeof item.config === 'string' && item.config.includes('"source_type":"100qiu"'))
  ).length
  const errorRates = items.map(item => item.error_rate || 0)
  const avgErrorRate = errorRates.length > 0 ? (errorRates.reduce((a, b) => a + b, 0) / errorRates.length) : 0
  
  stats.value = {
    total,
    online,
    offline,
    errorRate: parseFloat((avgErrorRate * 100).toFixed(2))
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

const resetFilters = () => {
  filters.value = {
    category: '',
    status: '',
    search: ''
  }
  currentPage.value = 1
  loadData()
}

const getCategory = (row) => {
  // 首先检查是否是100球数据源 - 显示为比赛数据
  if (row.type === '100qiu' || (row.config && row.config.source_type === '100qiu')) {
    return '比赛数据'
  }
  
  // 检查旧的100球数据源（通过名称判断）
  if (row.name && row.name.includes('100qiu')) {
    return '比赛数据'
  }
  
  // 从config中获取分类信息
  let category = '未分类'
  if (row.config && typeof row.config === 'object') {
    category = row.config.category || '未分类'
  } else if (typeof row.config === 'string') {
    try {
      const config = JSON.parse(row.config)
      category = config.category || '未分类'
    } catch (e) {
      category = '未分类'
    }
  }
  
  // 映射分类值到中文显示
  const categoryMap = {
    'match_data': '比赛数据',
    'intelligence_data': '情报数据', 
    'odds_data': '赔率数据'
  }
  
  return categoryMap[category] || category
}

const formatDate = (dateString) => {
  if (!dateString) return '从未更新'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 判断是否为100球数据源
const is100qiuDataSource = (row) => {
  // 通过source_type标记识别
  if (row.type === '100qiu') return true
  if (row.config && typeof row.config === 'object' && row.config.source_type === '100qiu') return true
  if (typeof row.config === 'string') {
    try {
      const config = JSON.parse(row.config)
      return config.source_type === '100qiu'
    } catch (e) {
      return false
    }
  }
  // 通过名称识别旧的100球数据源
  if (row.name && row.name.includes('100qiu')) return true
  return false
}

// 新增数据源弹窗
const handleAdd = () => {
  // 重置表单数据
  formData.value = {
    name: '',
    type: 'api',
    url: '',
    config: {},
    status: 'online'
  }
  addDialogVisible.value = true
}

// 创建100球数据源弹窗
const handleAdd100qiu = () => {
  // 重置100球表单数据
  form100qiuData.value = {
    date_time: '',
    update_frequency: 60
  }
  add100qiuDialogVisible.value = true
}

// 保存通用数据源
const saveDataSource = async () => {
  try {
    // 验证必填字段
    if (!formData.value.name) {
      ElMessage.warning('请输入数据源名称')
      return
    }
    if (!formData.value.category) {
      ElMessage.warning('请选择分类')
      return
    }
    if (!formData.value.url) {
      ElMessage.warning('请输入URL')
      return
    }
    
    const config = {
      category: formData.value.category
    }
    
    const response = await fetch('/api/admin/sources', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        name: formData.value.name,
        type: 'api',
        url: formData.value.url,
        config: config,
        status: formData.value.status
      })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('数据源创建成功')
      addDialogVisible.value = false
      loadData()
    } else {
      throw new Error(data.message || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建失败: ' + (error.message || '未知错误'))
    console.error('创建数据源失败:', error)
  }
}

// 保存100球数据源
const save100qiuDataSource = async () => {
  try {
    // 验证必填字段
    if (!form100qiuData.value.date_time) {
      ElMessage.warning('请输入date_time参数')
      return
    }
    
    // 验证date_time格式：应该是5-6位数字
    const date_time = form100qiuData.value.date_time.toString().trim()
    if (!/^\d{5,6}$/.test(date_time)) {
      ElMessage.warning('date_time必须是5-6位数字（如：260155）')
      return
    }
    
    const response = await fetch('/api/admin/sources', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        name: `100qiu竞彩彩票数据源-${date_time}`,
        type: 'api',  // 使用api类型，因为模型只支持api或file
        url: 'https://m.100qiu.com/api/dcListBasic',
        config: {
          date_time: date_time,
          update_frequency: form100qiuData.value.update_frequency,
          // 标记为100qiu数据源（用于功能识别）
          source_type: '100qiu',
          // 设置分类为比赛数据
          category: 'match_data'
        },
        status: 'online'
      })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('100球数据源创建成功')
      add100qiuDialogVisible.value = false
      loadData()
    } else {
      throw new Error(data.message || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建失败: ' + (error.message || '未知错误'))
    console.error('创建100球数据源失败:', error)
  }
}

const handleEdit = (row) => {
  // 使用弹窗编辑而不是跳转
  editFormData.value.id = row.id
  editFormData.value.name = row.name
  editFormData.value.url = row.url
  editFormData.value.status = row.status
  
  // 判断是否是100球数据源
  const is100qiu = is100qiuDataSource(row)
  editFormData.value.is100qiu = is100qiu
  
  if (is100qiu) {
    // 100球数据源 - 分类固定为比赛数据
    if (row.config && typeof row.config === 'object') {
      editFormData.value.date_time = row.config.date_time || ''
      editFormData.value.update_frequency = row.config.update_frequency || 60
    } else if (typeof row.config === 'string') {
      try {
        const config = JSON.parse(row.config)
        editFormData.value.date_time = config.date_time || ''
        editFormData.value.update_frequency = config.update_frequency || 60
      } catch (e) {
        editFormData.value.date_time = ''
        editFormData.value.update_frequency = 60
      }
    }
    editFormData.value.category = 'match_data' // 固定为比赛数据
  } else {
    // 普通数据源
    let category = '未分类'
    if (row.config && typeof row.config === 'object') {
      category = row.config.category || '未分类'
    } else if (typeof row.config === 'string') {
      try {
        const config = JSON.parse(row.config)
        category = config.category || '未分类'
      } catch (e) {
        category = '未分类'
      }
    }
    editFormData.value.category = category
  }
  
  editDialogVisible.value = true
  editActiveTab.value = 'basic'
  bindHeaderForm.value.headerIds = []
  bindHeaderForm.value.priorityOverride = null
  headerBindings.value = []
  loadHeaderOptions()
  loadHeaderBindings()
}

const loadHeaderOptions = async (query) => {
  try {
    const res = await getHeadersList({
      page: 1,
      size: 100,
      search: query || ''
    })
    headerOptions.value = res.data?.items || []
  } catch (error) {
    console.error('Error loading headers options:', error)
  }
}

const loadHeaderBindings = async () => {
  if (!editFormData.value?.id) {
    headerBindings.value = []
    return
  }
  try {
    const res = await getHeaderBindings({ data_source_id: Number(editFormData.value.id) })
    headerBindings.value = res.data?.dataSourceBindings || []
  } catch (error) {
    console.error('Error loading header bindings:', error)
    headerBindings.value = []
  }
}

const bindHeaders = async () => {
  if (!editFormData.value?.id) {
    ElMessage.warning('请先选择数据源')
    return
  }
  const ids = bindHeaderForm.value.headerIds || []
  if (ids.length === 0) {
    ElMessage.warning('请填写请求头ID')
    return
  }
  try {
    await bindHeadersToDataSource({
      dataSourceId: Number(editFormData.value.id),
      headerIds: ids,
      enabled: true,
      priorityOverride: bindHeaderForm.value.priorityOverride
    })
    ElMessage.success('绑定成功')
    bindHeaderForm.value.headerIds = []
    bindHeaderForm.value.priorityOverride = null
    loadHeaderBindings()
  } catch (error) {
    ElMessage.error('绑定失败')
  }
}

const toggleBinding = async (row) => {
  try {
    await bindHeadersToDataSource({
      dataSourceId: Number(editFormData.value.id),
      headerIds: [row.headerId],
      enabled: !row.enabled,
      priorityOverride: row.priorityOverride
    })
    ElMessage.success('更新成功')
    loadHeaderBindings()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const removeBinding = async (row) => {
  try {
    await unbindHeadersFromDataSource({
      dataSourceId: Number(editFormData.value.id),
      headerIds: [row.headerId]
    })
    ElMessage.success('解绑成功')
    loadHeaderBindings()
  } catch (error) {
    ElMessage.error('解绑失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除数据源 "${row.name}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 调用删除API
    deleteDataSource(row.id)
  }).catch(() => {
    // 取消操作
  })
}

const deleteDataSource = async (id) => {
  try {
    const response = await fetch(`/api/admin/sources/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      throw new Error(data.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('删除失败:', error)
  }
}

const checkHealth = async (row) => {
  try {
    const response = await fetch(`/api/admin/sources/${row.id}/health`, {
      method: 'POST',
      credentials: 'include'
    })
    const data = await response.json()
    if (data.success) {
      // 显示健康检查结果弹窗
      ElMessageBox.alert(`
        <div style="text-align: left;">
          <p><strong>状态:</strong> ${data.data.status}</p>
          <p><strong>响应时间:</strong> ${data.data.response_time_ms} ms</p>
          ${data.data.status_code ? `<p><strong>状态码:</strong> ${data.data.status_code}</p>` : ''}
          ${data.data.message ? `<p><strong>消息:</strong> ${data.data.message}</p>` : ''}
        </div>
      `, '健康检查结果', {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定'
      }).catch(() => {})
    } else {
      ElMessage.error(`健康检查失败: ${data.message}`)
    }
  } catch (error) {
    ElMessage.error('健康检查失败')
    console.error('健康检查失败:', error)
  }
}

const handleFetch = async (row) => {
  fetchingIds.value.push(row.id)
  try {
    const response = await fetch(`/api/v1/data-source-100qiu/${row.id}/fetch`, {
      method: 'POST',
      credentials: 'include'
    })
    const result = await response.json()
    
    if (result.success) {
      // 显示获取结果弹窗
      ElMessageBox.alert(`
        <div style="text-align: left;">
          <p><strong>获取成功！</strong></p>
          <p><strong>获取数量:</strong> ${result.total_fetched}</p>
          <p><strong>消息:</strong> ${result.message}</p>
          ${result.sample_data ? `<p><strong>示例数据:</strong> ${JSON.stringify(result.sample_data[0], null, 2)}</p>` : ''}
        </div>
      `, '获取结果', {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定'
      }).catch(() => {})
    } else {
      throw new Error(result.message || '获取失败')
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    let errorMessage = '获取失败'
    if (typeof error === 'string') {
      errorMessage = error
    } else if (error.message) {
      errorMessage = error.message
    }
    ElMessage.error(errorMessage)
  } finally {
    fetchingIds.value = fetchingIds.value.filter(itemId => itemId !== row.id)
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const batchDelete = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的数据源')
    return
  }
  
  ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 个数据源吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await fetch('/api/admin/sources/batch', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          ids: selectedIds.value
        })
      })
      const data = await response.json()
      if (data.success) {
        ElMessage.success(`成功删除 ${data.data.deleted_count} 个数据源`)
        selectedIds.value = []
        loadData()
      } else {
        throw new Error(data.message || '批量删除失败')
      }
    } catch (error) {
      ElMessage.error('批量删除失败: ' + (error.message || '未知错误'))
      console.error('批量删除失败:', error)
    }
  }).catch(() => {
    // 取消操作
  })
}

// 保存编辑的数据源
const saveEditDataSource = async () => {
  try {
    if (!editFormData.value.name) {
      ElMessage.warning('请输入数据源名称')
      return
    }
    if (!editFormData.value.url) {
      ElMessage.warning('请输入URL')
      return
    }
    
    let config = {}
    if (editFormData.value.is100qiu) {
      // 100球数据源
      if (!editFormData.value.date_time) {
        ElMessage.warning('请输入date_time参数')
        return
      }
      const date_time = editFormData.value.date_time.toString().trim()
      if (!/^\d{5,6}$/.test(date_time)) {
        ElMessage.warning('date_time必须是5-6位数字（如：260155）')
        return
      }
      
      config = {
        date_time: date_time,
        update_frequency: editFormData.value.update_frequency,
        source_type: '100qiu',
        // 100球属于比赛数据分类
        category: 'match_data'
      }
    } else {
      // 普通数据源
      if (!editFormData.value.category || editFormData.value.category === '未分类') {
        ElMessage.warning('请选择分类')
        return
      }
      config = {
        category: editFormData.value.category
      }
    }
    
    const response = await fetch(`/api/admin/sources/${editFormData.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        name: editFormData.value.name,
        url: editFormData.value.url,
        config: config,
        status: editFormData.value.status
      })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('数据源更新成功')
      editDialogVisible.value = false
      loadData()
    } else {
      throw new Error(data.message || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败: ' + (error.message || '未知错误'))
    console.error('更新数据源失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-section {
  display: flex;
  align-items: center;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

.dialog-form {
  margin-top: 20px;
}

.sync-status-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.sync-status-main {
  flex: 1;
  min-width: 0;
}

.sync-status-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.sync-status-meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  color: #606266;
  font-size: 13px;
}

.sync-status-error {
  margin-top: 8px;
  font-size: 13px;
  color: #f56c6c;
}

.sync-status-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bind-header-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.bind-header-actions :deep(.el-select) {
  flex: 1;
}
</style>
