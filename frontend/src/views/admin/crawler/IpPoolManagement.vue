<template>
  <div class="ip-pool-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>IP池管理</h3>
            <p class="subtitle">管理代理IP池，并支持按“获取地址”自动重新爬取</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addIp">新增IP</el-button>
            <el-button type="success" :loading="recrawling" @click="handleRecrawl">自动爬取</el-button>
            <el-button @click="openSourceDialog">获取地址编辑</el-button>
            <el-button @click="refreshList">刷新</el-button>
            <el-button @click="testAllIps">测试全部</el-button>
            <el-button :disabled="selectedIds.length === 0" @click="batchTest">批量测试</el-button>
            <el-button :disabled="selectedIds.length === 0" type="danger" @click="batchDelete">批量删除</el-button>
            <el-button @click="exportIps">导出</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="IP地址">
          <el-input v-model="queryParams.ipAddress" placeholder="请输入IP地址" clearable />
        </el-form-item>
        <el-form-item label="端口">
          <el-input v-model="queryParams.port" placeholder="请输入端口" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="可用" value="available" />
            <el-option label="不可用" value="unavailable" />
            <el-option label="待测试" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="ipList" style="width: 100%" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="ipAddress" label="IP地址" width="150" />
        <el-table-column prop="port" label="端口" width="90" />
        <el-table-column prop="protocol" label="协议" width="90">
          <template #default="scope">
            <el-tag :type="getProtocolTagType(scope.row.protocol)">
              {{ scope.row.protocol }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="地理位置" width="140" />
        <el-table-column prop="responseTime" label="响应时间(ms)" width="120">
          <template #default="scope">
            <span :class="getResponseTimeClass(scope.row.responseTime)">
              {{ scope.row.responseTime }} ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="successRate" label="成功率" width="120">
          <template #default="scope">
            <el-progress
              :percentage="scope.row.successRate"
              :color="getSuccessRateColor(scope.row.successRate)"
              :show-text="false"
              :stroke-width="10"
            />
            <span>{{ scope.row.successRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源地址" min-width="180" show-overflow-tooltip />
        <el-table-column prop="anonymity" label="匿名级别" width="100" />
        <el-table-column prop="score" label="评分" width="80" />
        <el-table-column prop="lastChecked" label="最近验证" width="170">
          <template #default="scope">
            {{ formatTime(scope.row.lastChecked) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="failReason" label="失败原因" min-width="130" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="使用次数" width="90" />
        <el-table-column prop="lastUsed" label="最后使用" width="170">
          <template #default="scope">
            {{ formatTime(scope.row.lastUsed) || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="testIpRow(scope.row)">测试</el-button>
            <el-button size="small" @click="editIp(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteIpRow(scope.row)">删除</el-button>
            <el-button size="small" :type="scope.row.isEnabled ? 'info' : 'success'" @click="toggleStatus(scope.row)">
              {{ scope.row.isEnabled ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="520px">
      <el-form :model="currentIp" :rules="ipRules" ref="ipFormRef" label-width="96px">
        <el-form-item label="IP地址" prop="ipAddress">
          <el-input v-model="currentIp.ipAddress" placeholder="请输入IP地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="currentIp.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="协议" prop="protocol">
          <el-select v-model="currentIp.protocol" placeholder="请选择协议">
            <el-option label="HTTP" value="http" />
            <el-option label="HTTPS" value="https" />
            <el-option label="SOCKS5" value="socks5" />
          </el-select>
        </el-form-item>
        <el-form-item label="地理位置">
          <el-input v-model="currentIp.location" placeholder="可选" />
        </el-form-item>
        <el-form-item label="来源地址">
          <el-input v-model="currentIp.source" placeholder="如: https://example.com/proxy-list" />
        </el-form-item>
        <el-form-item label="匿名级别">
          <el-input v-model="currentIp.anonymity" placeholder="透明/匿名/高匿" />
        </el-form-item>
        <el-form-item label="评分">
          <el-input-number v-model="currentIp.score" :min="0" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="失败原因">
          <el-input v-model="currentIp.failReason" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveIp">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="sourceDialogVisible" title="获取地址管理" width="900px">
      <div class="source-toolbar">
        <el-button type="primary" @click="openSourceEdit()">新增地址</el-button>
        <span class="source-summary">可用地址 {{ enabledSourceCount }} / {{ sourceList.length }}</span>
      </div>
      <el-table :data="sourceList" v-loading="sourceLoading">
        <el-table-column prop="source" label="获取地址" min-width="380" show-overflow-tooltip />
        <el-table-column prop="enabled" label="启用自动爬取" width="130">
          <template #default="scope">
            <el-switch :model-value="scope.row.enabled" @change="toggleSourceEnabled(scope.row, $event)" />
          </template>
        </el-table-column>
        <el-table-column prop="count" label="已获取IP数" width="110" />
        <el-table-column prop="activeCount" label="可用IP数" width="110" />
        <el-table-column prop="lastChecked" label="最近采集" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.lastChecked) || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="openSourceEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeSource(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="sourceDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="sourceEditVisible" :title="sourceEditForm.oldSource ? '编辑获取地址' : '新增获取地址'" width="520px">
      <el-form :model="sourceEditForm" label-width="110px">
        <el-form-item label="获取地址">
          <el-input v-model="sourceEditForm.newSource" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="启用自动爬取">
          <el-switch v-model="sourceEditForm.enabled" />
        </el-form-item>
        <el-form-item label="同步旧IP来源">
          <el-switch v-model="sourceEditForm.applyToExistingIps" :disabled="!sourceEditForm.oldSource" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sourceEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSourceEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  addSourceAddress,
  batchDeleteIps,
  batchTestIps,
  createIp,
  deleteIp,
  deleteSourceAddress,
  getIpPoolList,
  getSourceAddresses,
  recrawlIps,
  testIp,
  updateIp,
  updateSourceAddress
} from '@/api/ipPool'

const loading = ref(false)
const recrawling = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const ipFormRef = ref()
const selectedIds = ref([])
const ipList = ref([])

const sourceDialogVisible = ref(false)
const sourceEditVisible = ref(false)
const sourceLoading = ref(false)
const sourceList = ref([])

const sourceEditForm = reactive({
  oldSource: '',
  newSource: '',
  enabled: true,
  applyToExistingIps: true
})

const queryParams = reactive({
  ipAddress: '',
  port: '',
  status: ''
})

const currentIp = reactive({
  id: null,
  ipAddress: '',
  port: null,
  protocol: 'http',
  location: '',
  responseTime: 0,
  successRate: 0,
  status: 'pending',
  source: '',
  anonymity: '',
  score: null,
  failReason: '',
  isEnabled: true
})

const ipRules = {
  ipAddress: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    { pattern: /^([0-9]{1,3}\.){3}[0-9]{1,3}$/, message: '请输入正确的IP格式', trigger: 'blur' }
  ],
  port: [{ required: true, message: '请输入端口号', trigger: 'blur' }]
}

const enabledSourceCount = computed(() => sourceList.value.filter((x) => x.enabled).length)

const toBackendStatus = (status) => {
  if (status === 'available') return 'active'
  if (status === 'unavailable') return 'inactive'
  return status
}

const toFrontendStatus = (status) => {
  if (status === 'active') return 'available'
  if (status === 'inactive' || status === 'banned') return 'unavailable'
  return status
}

const formatTime = (v) => {
  if (!v || v === '-') return ''
  try {
    return new Date(v).toLocaleString('zh-CN', { hour12: false })
  } catch (e) {
    return v
  }
}

const getIpList = async () => {
  loading.value = true
  try {
    const res = await getIpPoolList({
      page: currentPage.value,
      size: pageSize.value,
      status: queryParams.status ? toBackendStatus(queryParams.status) : undefined,
      search: queryParams.ipAddress || queryParams.port || undefined
    })
    const payload = res.data || res
    const data = payload.items ? payload : (payload.data || {})
    const items = data.items || []
    total.value = data.total || 0
    ipList.value = items.map((item) => {
      const normalizedStatus = toFrontendStatus(item.status)
      return {
        ...item,
        status: normalizedStatus,
        responseTime: item.responseTime ?? 0,
        successRate: item.successRate ?? 0,
        lastChecked: item.lastChecked || '',
        isEnabled: item.isEnabled ?? normalizedStatus === 'available'
      }
    })
  } catch (error) {
    console.error(error)
    ElMessage.error('获取IP池失败')
  } finally {
    loading.value = false
  }
}

const loadSourceList = async () => {
  sourceLoading.value = true
  try {
    const res = await getSourceAddresses()
    const payload = res.data || res
    const data = payload.items ? payload : (payload.data || {})
    sourceList.value = data.items || []
  } catch (error) {
    console.error(error)
    ElMessage.error('获取地址列表加载失败')
  } finally {
    sourceLoading.value = false
  }
}

const openSourceDialog = async () => {
  sourceDialogVisible.value = true
  await loadSourceList()
}

const openSourceEdit = (row = null) => {
  sourceEditForm.oldSource = row?.source || ''
  sourceEditForm.newSource = row?.source || ''
  sourceEditForm.enabled = row?.enabled ?? true
  sourceEditForm.applyToExistingIps = true
  sourceEditVisible.value = true
}

const saveSourceEdit = async () => {
  const source = (sourceEditForm.newSource || '').trim()
  if (!source) {
    ElMessage.warning('请输入获取地址')
    return
  }
  try {
    if (sourceEditForm.oldSource) {
      await updateSourceAddress({
        old_source: sourceEditForm.oldSource,
        new_source: source,
        enabled: sourceEditForm.enabled,
        apply_to_existing_ips: sourceEditForm.applyToExistingIps
      })
      ElMessage.success('地址更新成功')
    } else {
      await addSourceAddress({ source, enabled: sourceEditForm.enabled })
      ElMessage.success('地址新增成功')
    }
    sourceEditVisible.value = false
    await loadSourceList()
    await getIpList()
  } catch (error) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '地址保存失败')
  }
}

const toggleSourceEnabled = async (row, val) => {
  try {
    await updateSourceAddress({
      old_source: row.source,
      new_source: row.source,
      enabled: val,
      apply_to_existing_ips: false
    })
    row.enabled = val
    ElMessage.success(val ? '已启用该地址自动爬取' : '已禁用该地址自动爬取')
  } catch (error) {
    console.error(error)
    ElMessage.error('状态更新失败')
    row.enabled = !val
  }
}

const removeSource = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt(
      '输入 yes 表示同时删除该地址已抓取的IP，留空仅删除地址配置',
      '删除获取地址',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        inputPlaceholder: 'yes / 留空',
        inputPattern: /^(|yes)$/i,
        inputErrorMessage: '只能输入 yes 或留空'
      }
    )
    const deleteRelatedIps = String(value || '').toLowerCase() === 'yes'
    await deleteSourceAddress({
      source: row.source,
      delete_related_ips: deleteRelatedIps
    })
    ElMessage.success(deleteRelatedIps ? '地址与关联IP已删除' : '地址配置已删除')
    await loadSourceList()
    await getIpList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('删除失败')
    }
  }
}

const handleRecrawl = async () => {
  recrawling.value = true
  try {
    await loadSourceList()
    const enabledSources = sourceList.value.filter((x) => x.enabled).map((x) => x.source)
    if (enabledSources.length === 0) {
      ElMessage.warning('没有可用的获取地址，请先在“获取地址编辑”中启用地址')
      return
    }
    const res = await recrawlIps({ only_enabled: true })
    const payload = res.data || res
    const data = payload.data || {}
    const summary = data.summary || {}
    ElMessage.success(`自动爬取完成：新增 ${summary.newCount || 0}，更新 ${summary.updatedCount || 0}`)
    await getIpList()
    if (sourceDialogVisible.value) {
      await loadSourceList()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('自动爬取失败')
  } finally {
    recrawling.value = false
  }
}

const onQuery = () => {
  currentPage.value = 1
  getIpList()
}

const resetQuery = () => {
  queryParams.ipAddress = ''
  queryParams.port = ''
  queryParams.status = ''
  currentPage.value = 1
  getIpList()
}

const addIp = () => {
  Object.assign(currentIp, {
    id: null,
    ipAddress: '',
    port: null,
    protocol: 'http',
    location: '',
    responseTime: 0,
    successRate: 0,
    status: 'pending',
    source: '',
    anonymity: '',
    score: null,
    failReason: '',
    isEnabled: true
  })
  dialogTitle.value = '新增IP'
  dialogVisible.value = true
}

const editIp = (row) => {
  Object.assign(currentIp, { ...row })
  dialogTitle.value = '编辑IP'
  dialogVisible.value = true
}

const saveIp = async () => {
  try {
    if (!ipFormRef.value) return
    await ipFormRef.value.validate()

    const payload = {
      ip: currentIp.ipAddress,
      port: currentIp.port,
      protocol: currentIp.protocol,
      location: currentIp.location,
      status: toBackendStatus(currentIp.status),
      latency_ms: currentIp.responseTime,
      success_rate: currentIp.successRate,
      source: currentIp.source,
      anonymity: currentIp.anonymity,
      score: currentIp.score,
      fail_reason: currentIp.failReason
    }

    if (currentIp.id) {
      await updateIp(currentIp.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createIp(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    getIpList()
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  }
}

const deleteIpRow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 IP ${row.ipAddress}:${row.port} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteIp(row.id)
    ElMessage.success('删除成功')
    getIpList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSelectionChange = (rows) => {
  selectedIds.value = rows.map((row) => row.id)
}

const batchTest = async () => {
  if (selectedIds.value.length === 0) return
  try {
    await batchTestIps({ ids: selectedIds.value })
    ElMessage.success('批量测试完成')
    getIpList()
  } catch (error) {
    console.error(error)
    ElMessage.error('批量测试失败')
  }
}

const batchDelete = async () => {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await batchDeleteIps({ ids: selectedIds.value })
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    getIpList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const exportIps = async () => {
  try {
    const token = localStorage.getItem('token')
    const resp = await fetch('/api/admin/ip-pools/export', {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (!resp.ok) {
      throw new Error(`导出失败: ${resp.status}`)
    }
    const blob = await resp.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'ip_pools.csv'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('导出失败')
  }
}

const testIpRow = async (row) => {
  try {
    ElMessage.info(`正在测试IP: ${row.ipAddress}:${row.port}`)
    const res = await testIp(row.id)
    const data = res.data?.data || res.data || {}
    const target = ipList.value.find((ip) => ip.id === row.id)
    if (target) {
      target.status = toFrontendStatus(data.status || 'available')
      target.responseTime = data.response_time || target.responseTime
      target.successRate = data.success_rate || target.successRate
      target.lastChecked = new Date().toISOString()
      target.isEnabled = target.status === 'available'
    }
    ElMessage.success('测试完成')
  } catch (error) {
    console.error(error)
    ElMessage.error('测试失败')
  }
}

const testAllIps = async () => {
  if (ipList.value.length === 0) return
  try {
    ElMessage.info('开始测试当前页全部IP')
    await batchTestIps({ ids: ipList.value.map((x) => x.id) })
    ElMessage.success('当前页IP测试完成')
    getIpList()
  } catch (error) {
    console.error(error)
    ElMessage.error('测试失败')
  }
}

const toggleStatus = async (row) => {
  const prevEnabled = row.isEnabled
  const nextEnabled = !prevEnabled
  const nextStatusFrontend = nextEnabled ? 'available' : 'unavailable'
  const nextStatusBackend = nextEnabled ? 'active' : 'inactive'
  row.isEnabled = nextEnabled
  row.status = nextStatusFrontend
  try {
    await updateIp(row.id, {
      ip: row.ipAddress,
      port: row.port,
      protocol: row.protocol,
      location: row.location,
      status: nextStatusBackend,
      latency_ms: row.responseTime,
      success_rate: row.successRate,
      source: row.source,
      anonymity: row.anonymity,
      score: row.score,
      fail_reason: row.failReason
    })
    ElMessage.success(nextEnabled ? '启用成功' : '禁用成功')
  } catch (error) {
    row.isEnabled = prevEnabled
    row.status = prevEnabled ? 'available' : 'unavailable'
    console.error(error)
    ElMessage.error('状态更新失败')
  }
}

const refreshList = () => {
  getIpList()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  getIpList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  getIpList()
}

const getStatusText = (status) => {
  if (status === 'available') return '可用'
  if (status === 'unavailable') return '不可用'
  if (status === 'pending') return '待测试'
  return status
}

const getStatusTagType = (status) => {
  if (status === 'available') return 'success'
  if (status === 'unavailable') return 'danger'
  if (status === 'pending') return 'info'
  return 'info'
}

const getProtocolTagType = (protocol) => {
  if (protocol === 'http') return 'primary'
  if (protocol === 'https') return 'success'
  if (protocol === 'socks5') return 'warning'
  return 'info'
}

const getResponseTimeClass = (time) => {
  if (time < 200) return 'text-success'
  if (time < 500) return 'text-warning'
  return 'text-danger'
}

const getSuccessRateColor = (rate) => {
  if (rate >= 90) return '#67c23a'
  if (rate >= 70) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  getIpList()
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
  gap: 12px;
}

.card-header h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}

.source-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.source-summary {
  color: #606266;
  font-size: 13px;
}

.text-success {
  color: #67c23a;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}
</style>
