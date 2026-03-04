<template>
  <div class="page-container">
    <el-row :gutter="16" style="margin-bottom: 16px;">
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ stats.total }}</div><div class="stat-label">总数据源</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ stats.online }}</div><div class="stat-label">在线</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ stats.offline }}</div><div class="stat-label">离线</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ stats.errorRate }}%</div><div class="stat-label">错误率</div></div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-bottom: 16px;">
      <el-col :span="8">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ poolHealth.ipActive }}/{{ poolHealth.ipTarget }}</div><div class="stat-label">IP 可用/目标 (缺口 {{ poolHealth.ipGap }})</div></div></el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ poolHealth.headerDomains }}/{{ poolHealth.lowQualityHeaders }}</div><div class="stat-label">Headers 域名/低质量总数</div></div></el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover"><div class="stat-card"><div class="stat-value">{{ poolHealth.bindingCoverage }}%</div><div class="stat-label">数据源 Header 绑定覆盖率</div></div></el-card>
      </el-col>
    </el-row>

    <el-card class="box-card" style="margin-bottom: 16px;">
      <div class="sync-status-bar">
        <div class="sync-status-main">
          <div class="sync-status-title">Kaggle 自动同步状态</div>
          <div class="sync-status-meta">
            <span>最新版本: {{ syncStatus.latest_issue_no || '-' }}</span>
            <span>最后成功版本: {{ syncStatus.last_success_issue_no || '-' }}</span>
            <span>最后同步时间: {{ formatDate(syncStatus.last_sync_at) }}</span>
            <span>下次同步时间: {{ formatDate(syncStatus.next_sync_at) }}</span>
          </div>
          <div v-if="syncStatus.last_error" class="sync-status-error">最近错误: {{ syncStatus.last_error }}</div>
        </div>
        <div class="sync-status-actions">
          <el-tag :type="syncStatusTagType">{{ syncStatus.sync_status || 'idle' }}</el-tag>
          <el-button type="primary" size="small" :loading="syncStatus.runningNow" @click="runSourceSyncNow">立即同步</el-button>
          <el-button type="warning" size="small" :loading="syncStatus.runningMergeBackfill" @click="runMergeBackfillNow">合并回填</el-button>
        </div>
      </div>
    </el-card>

    <el-card class="box-card" style="margin-bottom: 16px;">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="handleAdd">+ 新增数据源</el-button>
          <el-button type="success" @click="handleAdd100qiu">+ 快速新增</el-button>
        </div>
        <div class="filter-section">
          <el-select v-model="filters.category" placeholder="选择分类" clearable style="width: 130px;" @change="loadData">
            <el-option label="比赛数据" value="match_data" />
            <el-option label="情报数据" value="intelligence_data" />
            <el-option label="赔率数据" value="odds_data" />
          </el-select>
          <el-select v-model="filters.status" placeholder="选择状态" clearable style="width: 130px;" @change="loadData">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
          </el-select>
          <el-input v-model="filters.search" placeholder="搜索名称或 dataset_slug" style="width: 220px;" @keyup.enter="loadData" />
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </el-card>

    <el-card class="box-card">
      <template #header><span class="card-header">数据源管理</span></template>

      <el-table :data="tableData" border style="width: 100%" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="source_id" label="dataset_slug" min-width="220" show-overflow-tooltip />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="分类" width="110">
          <template #default="scope">{{ getCategory(scope.row) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'online' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latest_version" label="最新版本" width="120" />
        <el-table-column prop="last_synced_version" label="已同步版本" width="120" />
        <el-table-column prop="last_sync_at" label="最后同步" width="170">
          <template #default="scope">{{ formatDate(scope.row.last_sync_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="checkHealth(scope.row)">健康检查</el-button>
            <el-button v-if="is100qiuDataSource(scope.row)" size="small" type="success" :loading="fetchingIds.includes(scope.row.id)" @click="handleFetch(scope.row)">抓取</el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">停用</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="selectedIds.length > 0" class="batch-actions">
        已选择 {{ selectedIds.length }} 项
        <el-button type="danger" size="small" @click="batchDelete" style="margin-left: 12px;">批量停用</el-button>
        <el-button size="small" @click="selectedIds = []">取消选择</el-button>
      </div>

      <div class="pagination">
        <el-pagination
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
        />
      </div>
    </el-card>
  </div>

  <el-dialog v-model="addDialogVisible" title="新增 Kaggle 数据源" width="520px">
    <el-form :model="formData" label-width="120px" class="dialog-form">
      <el-form-item label="显示名称">
        <el-input v-model="formData.name" placeholder="可选" />
      </el-form-item>
      <el-form-item label="dataset_slug" required>
        <el-input v-model="formData.url" placeholder="owner/dataset" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="formData.category" style="width: 100%;">
          <el-option label="比赛数据" value="match_data" />
          <el-option label="情报数据" value="intelligence_data" />
          <el-option label="赔率数据" value="odds_data" />
        </el-select>
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

  <el-dialog v-model="add100qiuDialogVisible" title="快速新增数据源" width="520px">
    <el-form :model="form100qiuData" label-width="120px" class="dialog-form">
      <el-form-item label="dataset_slug" required>
        <el-input v-model="form100qiuData.date_time" placeholder="owner/dataset" />
      </el-form-item>
      <el-form-item label="同步频率(分钟)">
        <el-input-number v-model="form100qiuData.update_frequency" :min="60" :max="10080" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="add100qiuDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="save100qiuDataSource">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="editDialogVisible" title="编辑数据源" width="560px">
    <el-form :model="editFormData" label-width="120px" class="dialog-form">
      <el-tabs v-model="editActiveTab">
        <el-tab-pane label="基础信息" name="basic">
          <el-form-item label="显示名称" required>
            <el-input v-model="editFormData.name" />
          </el-form-item>
          <el-form-item label="dataset_slug">
            <el-input v-model="editFormData.url" disabled />
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="editFormData.category" style="width: 100%;">
              <el-option label="比赛数据" value="match_data" />
              <el-option label="情报数据" value="intelligence_data" />
              <el-option label="赔率数据" value="odds_data" />
            </el-select>
          </el-form-item>
          <el-form-item label="同步频率(分钟)">
            <el-input-number v-model="editFormData.update_frequency" :min="60" :max="10080" />
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
              placeholder="选择请求头"
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
                <el-tag :type="scope.row.enabled ? 'success' : 'info'">{{ scope.row.enabled ? '启用' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button size="small" @click="toggleBinding(scope.row)">{{ scope.row.enabled ? '禁用' : '启用' }}</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { bindHeadersToDataSource, getHeaderBindings, getHeadersList, getHeaderStats, unbindHeadersFromDataSource } from '@/api/headers'
import { getIpStats } from '@/api/ipPool'
import {
  createKaggleDataset,
  getKaggleDatasetPreview,
  getKaggleDatasets,
  getKaggleSyncStatus,
  rebuildKaggleDataset,
  runKaggleMergeBackfillNow,
  runKaggleSyncNow,
  updateKaggleDataset
} from '@/api/modules/kaggle-sync'

const tableData = ref([])
const allRows = ref([])
const fetchingIds = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedIds = ref([])
const editActiveTab = ref('basic')
const headerBindings = ref([])
const bindHeaderForm = ref({
  headerIds: [],
  priorityOverride: null
})
const headerOptions = ref([])

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
  runningNow: false,
  runningMergeBackfill: false
})

const filters = ref({
  category: '',
  status: '',
  search: ''
})

const addDialogVisible = ref(false)
const add100qiuDialogVisible = ref(false)
const editDialogVisible = ref(false)
const formData = ref({
  name: '',
  type: 'api',
  url: '',
  category: 'match_data',
  config: {},
  status: 'online'
})
const form100qiuData = ref({
  date_time: '',
  update_frequency: 360
})
const editFormData = ref({
  id: null,
  name: '',
  url: '',
  category: 'match_data',
  status: 'online',
  is100qiu: false,
  date_time: '',
  update_frequency: 360,
  source_slug: ''
})

const isValidDatasetSlug = (value) => /^[^/\s]+\/[^/\s]+$/.test(String(value || '').trim())

const parseCategory = (config) => {
  if (config && typeof config === 'object') {
    return String(config.category || 'match_data')
  }
  return 'match_data'
}

const normalizeDataset = (item) => {
  const enabled = Boolean(item.enabled)
  const hasError = Boolean(item.last_error_message)
  const slug = String(item.dataset_slug || '')
  const runVersion = String(item.last_synced_version || item.latest_version || '')
  return {
    id: item.id,
    source_id: slug,
    source_type: 'kaggle',
    name: item.display_name || slug,
    url: slug,
    status: enabled ? 'online' : 'offline',
    error_rate: hasError ? 1 : 0,
    created_at: item.created_at,
    updated_at: item.updated_at,
    dataset_slug: slug,
    latest_version: item.latest_version || '',
    last_synced_version: item.last_synced_version || '',
    last_sync_at: item.last_sync_at || '',
    run_version: runVersion,
    sync_interval_hours: Number(item.sync_interval_hours || 6),
    last_error_message: item.last_error_message || '',
    config: item.config && typeof item.config === 'object'
      ? item.config
      : { category: 'match_data' }
  }
}

const applyLocalFilters = (rows) => {
  let filtered = [...rows]
  if (filters.value.category) {
    filtered = filtered.filter((row) => parseCategory(row.config) === filters.value.category)
  }
  if (filters.value.status) {
    filtered = filtered.filter((row) => row.status === filters.value.status)
  }
  if (filters.value.search) {
    const keyword = String(filters.value.search).trim().toLowerCase()
    filtered = filtered.filter((row) => {
      const text = `${row.name} ${row.source_id} ${row.url}`.toLowerCase()
      return text.includes(keyword)
    })
  }
  return filtered
}

const paginateRows = (rows) => {
  total.value = rows.length
  const maxPage = Math.max(1, Math.ceil(rows.length / pageSize.value))
  if (currentPage.value > maxPage) {
    currentPage.value = maxPage
  }
  const start = (currentPage.value - 1) * pageSize.value
  tableData.value = rows.slice(start, start + pageSize.value)
}

const calculateStats = (rows) => {
  const totalRows = rows.length
  const onlineRows = rows.filter((item) => item.status === 'online').length
  const offlineRows = totalRows - onlineRows
  const avgErrorRate = totalRows > 0
    ? rows.reduce((sum, item) => sum + Number(item.error_rate || 0), 0) / totalRows
    : 0
  stats.value = {
    total: totalRows,
    online: onlineRows,
    offline: offlineRows,
    errorRate: Number((avgErrorRate * 100).toFixed(2))
  }
}

const loadData = async () => {
  try {
    const payload = await getKaggleDatasets({ page: 1, size: 200 })
    const items = Array.isArray(payload?.items) ? payload.items : []
    const normalized = items.map(normalizeDataset)
    allRows.value = normalized

    calculateStats(normalized)
    paginateRows(applyLocalFilters(normalized))

    await Promise.all([loadPoolHealth(), loadSourceSyncStatus()])
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('loadData failed:', error)
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
    console.error('loadPoolHealth failed:', error)
  }
}

const loadSourceSyncStatus = async () => {
  try {
    const data = await getKaggleSyncStatus()
    const latestRun = data?.latest_run || null
    const latestSuccessVersion = data?.latest_feature_backfill?.version || data?.latest_entity_merge?.version || latestRun?.version || '-'
    const runningRuns = Number(data?.running_runs || 0)
    const failedRuns = Number(data?.failed_runs || 0)
    const status = runningRuns > 0 ? 'running' : (failedRuns > 0 ? 'degraded' : 'idle')
    syncStatus.value = {
      ...syncStatus.value,
      sync_status: status,
      latest_issue_no: latestRun?.version || '-',
      last_success_issue_no: latestSuccessVersion,
      last_sync_at: latestRun?.finished_at || latestRun?.updated_at || null,
      next_sync_at: null,
      last_error: latestRun?.error_message || '',
      runningNow: false
    }
  } catch (error) {
    console.error('loadSourceSyncStatus failed:', error)
  }
}

const runSourceSyncNow = async () => {
  syncStatus.value.runningNow = true
  try {
    const result = await runKaggleSyncNow({})
    const runId = result?.run?.run_id || '-'
    ElMessage.success(`已触发同步任务: ${runId}`)
    setTimeout(() => {
      loadSourceSyncStatus()
      loadData()
    }, 1200)
  } catch (error) {
    ElMessage.error(error?.message || '触发失败')
  } finally {
    syncStatus.value.runningNow = false
  }
}

const runMergeBackfillNow = async () => {
  syncStatus.value.runningMergeBackfill = true
  try {
    const result = await runKaggleMergeBackfillNow({})
    const runId = result?.run_id || '-'
    ElMessage.success(`已触发合并回填任务: ${runId}`)
    setTimeout(() => {
      loadSourceSyncStatus()
      loadData()
    }, 1200)
  } catch (error) {
    ElMessage.error(error?.message || '触发合并回填失败')
  } finally {
    syncStatus.value.runningMergeBackfill = false
  }
}

const syncStatusTagType = computed(() => {
  const status = syncStatus.value.sync_status
  if (status === 'success') return 'success'
  if (status === 'running') return 'warning'
  if (status === 'degraded' || status === 'failed') return 'danger'
  return 'info'
})

const handlePageChange = (page) => {
  currentPage.value = page
  paginateRows(applyLocalFilters(allRows.value))
}

const resetFilters = () => {
  filters.value = {
    category: '',
    status: '',
    search: ''
  }
  currentPage.value = 1
  paginateRows(applyLocalFilters(allRows.value))
}

const getCategory = (row) => {
  const category = parseCategory(row.config)
  const categoryMap = {
    match_data: '比赛数据',
    intelligence_data: '情报数据',
    odds_data: '赔率数据'
  }
  return categoryMap[category] || '比赛数据'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const is100qiuDataSource = (row) => row?.source_type === 'kaggle'

const handleAdd = () => {
  formData.value = {
    name: '',
    type: 'api',
    url: '',
    category: 'match_data',
    config: {},
    status: 'online'
  }
  addDialogVisible.value = true
}

const handleAdd100qiu = () => {
  form100qiuData.value = {
    date_time: '',
    update_frequency: 360
  }
  add100qiuDialogVisible.value = true
}

const saveDataSource = async () => {
  try {
    if (!formData.value.url || !isValidDatasetSlug(formData.value.url)) {
      ElMessage.warning('请输入 Kaggle 数据集标识，格式 owner/dataset')
      return
    }
    const slug = String(formData.value.url).trim()
    await createKaggleDataset({
      dataset_slug: slug,
      display_name: formData.value.name || slug,
      enabled: formData.value.status === 'online',
      sync_interval_hours: 6,
      config: {
        category: formData.value.category || 'match_data'
      }
    })
    ElMessage.success('数据源创建成功')
    addDialogVisible.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(`创建失败: ${error?.message || '未知错误'}`)
    console.error('saveDataSource failed:', error)
  }
}

const save100qiuDataSource = async () => {
  try {
    if (!form100qiuData.value.date_time || !isValidDatasetSlug(form100qiuData.value.date_time)) {
      ElMessage.warning('请输入 Kaggle 数据集标识，格式 owner/dataset')
      return
    }
    const slug = String(form100qiuData.value.date_time).trim()
    const intervalHours = Math.max(1, Math.round(Number(form100qiuData.value.update_frequency || 360) / 60))
    await createKaggleDataset({
      dataset_slug: slug,
      display_name: slug,
      enabled: true,
      sync_interval_hours: intervalHours,
      config: {
        category: 'match_data'
      }
    })
    ElMessage.success('数据源创建成功')
    add100qiuDialogVisible.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(`创建失败: ${error?.message || '未知错误'}`)
    console.error('save100qiuDataSource failed:', error)
  }
}

const handleEdit = (row) => {
  editFormData.value.id = row.id
  editFormData.value.name = row.name
  editFormData.value.url = row.dataset_slug
  editFormData.value.source_slug = row.dataset_slug
  editFormData.value.status = row.status
  editFormData.value.is100qiu = false
  editFormData.value.category = parseCategory(row.config)
  editFormData.value.date_time = row.dataset_slug
  editFormData.value.update_frequency = Math.max(60, Number(row.sync_interval_hours || 6) * 60)
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
    ElMessage.warning('请填写请求头 ID')
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
  } catch {
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
  } catch {
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
  } catch {
    ElMessage.error('解绑失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确认停用数据源 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteDataSource(row.id)
  }).catch(() => {})
}

const deleteDataSource = async (id) => {
  try {
    await updateKaggleDataset(id, { enabled: false })
    ElMessage.success('已停用')
    await loadData()
  } catch (error) {
    ElMessage.error(`操作失败: ${error?.message || '未知错误'}`)
    console.error('deleteDataSource failed:', error)
  }
}

const checkHealth = async (row) => {
  try {
    const preview = await getKaggleDatasetPreview(row.id, { limit: 1 })
    const html = `
      <div style="text-align:left;">
        <p><strong>dataset:</strong> ${row.dataset_slug}</p>
        <p><strong>latest_version:</strong> ${row.latest_version || '-'}</p>
        <p><strong>last_synced_version:</strong> ${row.last_synced_version || '-'}</p>
        <p><strong>match_samples:</strong> ${(preview?.match_samples || []).length}</p>
        <p><strong>team_samples:</strong> ${(preview?.team_samples || []).length}</p>
        <p><strong>league_samples:</strong> ${(preview?.league_samples || []).length}</p>
      </div>
    `
    ElMessageBox.alert(html, '健康检查', {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定'
    }).catch(() => {})
  } catch (error) {
    ElMessage.error(`健康检查失败: ${error?.message || '未知错误'}`)
  }
}

const handleFetch = async (row) => {
  fetchingIds.value.push(row.id)
  try {
    const result = await rebuildKaggleDataset(row.id, { force: true })
    const runId = result?.run?.run_id || '-'
    ElMessage.success(`已触发抓取任务: ${runId}`)
    setTimeout(() => {
      loadData()
      loadSourceSyncStatus()
    }, 1200)
  } catch (error) {
    ElMessage.error(`触发失败: ${error?.message || '未知错误'}`)
  } finally {
    fetchingIds.value = fetchingIds.value.filter((itemId) => itemId !== row.id)
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map((item) => item.id)
}

const batchDelete = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要停用的数据源')
    return
  }
  ElMessageBox.confirm(`确认停用选中的 ${selectedIds.value.length} 个数据源吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const tasks = selectedIds.value.map((id) => updateKaggleDataset(id, { enabled: false }))
      const results = await Promise.allSettled(tasks)
      const successCount = results.filter((r) => r.status === 'fulfilled').length
      const failedCount = results.length - successCount
      ElMessage.success(`停用完成: ${successCount} 成功，${failedCount} 失败`)
      selectedIds.value = []
      await loadData()
    } catch (error) {
      ElMessage.error(`批量停用失败: ${error?.message || '未知错误'}`)
    }
  }).catch(() => {})
}

const saveEditDataSource = async () => {
  try {
    if (!editFormData.value.name) {
      ElMessage.warning('请输入数据源名称')
      return
    }
    if (!editFormData.value.source_slug) {
      ElMessage.warning('缺少 dataset 标识')
      return
    }
    const intervalHours = Math.max(1, Math.round(Number(editFormData.value.update_frequency || 360) / 60))
    await updateKaggleDataset(editFormData.value.id, {
      display_name: editFormData.value.name,
      enabled: editFormData.value.status === 'online',
      sync_interval_hours: intervalHours,
      config: {
        category: editFormData.value.category || 'match_data'
      }
    })
    ElMessage.success('数据源更新成功')
    editDialogVisible.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(`更新失败: ${error?.message || '未知错误'}`)
    console.error('saveEditDataSource failed:', error)
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
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.filter-section {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.batch-actions {
  margin-top: 12px;
  padding: 10px;
  border-radius: 6px;
  background: #f5f7fa;
}

.dialog-form {
  margin-top: 8px;
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
