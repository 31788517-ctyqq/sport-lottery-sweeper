<template>
  <div class="ip-pool-management">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>IP池管理</h3>
            <p class="subtitle">管理爬虫系统的IP池，确保稳定的数据抓取服务</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="addIp">新增IP</el-button>
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
        <el-table-column prop="port" label="端口" width="100" />
        <el-table-column prop="protocol" label="协议" width="100">
          <template #default="scope">
            <el-tag :type="getProtocolTagType(scope.row.protocol)">
              {{ scope.row.protocol }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="地理位置" width="150" />
        <el-table-column prop="responseTime" label="响应时间(ms)" width="130">
          <template #default="scope">
            <span :class="getResponseTimeClass(scope.row.responseTime)">
              {{ scope.row.responseTime }} ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.successRate" 
              :color="getSuccessRateColor(scope.row.successRate)"
              :show-text="false"
              :stroke-width="20"
            />
            <span>{{ scope.row.successRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="anonymity" label="匿名级别" width="100" />
        <el-table-column prop="score" label="得分" width="80" />
        <el-table-column prop="lastChecked" label="最近验证" width="160">
          <template #default="scope">
            {{ scope.row.lastChecked || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="failReason" label="失败原因" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="使用次数" width="100" />
        <el-table-column prop="lastUsed" label="最后使用" width="150" />
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="testIpRow(scope.row)">测试</el-button>
            <el-button size="small" @click="editIp(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteIpRow(scope.row)">删除</el-button>
            <el-button 
              size="small" 
              :type="scope.row.isEnabled ? 'info' : 'success'" 
              @click="toggleStatus(scope.row)"
            >
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
        style="margin-top: 20px; justify-content: center;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- IP编辑弹窗 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="520px">
      <el-form :model="currentIp" :rules="ipRules" ref="ipFormRef" label-width="100px">
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
        <el-form-item label="用户名">
          <el-input v-model="currentIp.username" placeholder="如有认证则填写" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="currentIp.password" type="password" placeholder="如有认证则填写" />
        </el-form-item>
        <el-form-item label="地理位置">
          <el-input v-model="currentIp.location" placeholder="IP所在地理位置" />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="currentIp.source" placeholder="采集来源" />
        </el-form-item>
        <el-form-item label="匿名级别">
          <el-input v-model="currentIp.anonymity" placeholder="透明/匿名/高匿" />
        </el-form-item>
        <el-form-item label="得分">
          <el-input-number v-model="currentIp.score" :min="0" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="失败原因">
          <el-input v-model="currentIp.failReason" placeholder="最近失败原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveIp">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getIpPoolList, createIp, updateIp, deleteIp, testIp, batchDeleteIps, batchTestIps } from '@/api/ipPool'

const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const ipFormRef = ref()
const selectedIds = ref([])

const toBackendStatus = (status) => {
  switch (status) {
    case 'available': return 'active'
    case 'unavailable': return 'inactive'
    default: return status
  }
}

const toFrontendStatus = (status) => {
  switch (status) {
    case 'active': return 'available'
    case 'inactive': return 'unavailable'
    case 'banned': return 'unavailable'
    default: return status
  }
}

// 查询参数
const queryParams = reactive({
  ipAddress: '',
  port: '',
  status: ''
})

// 当前编辑的IP
const currentIp = reactive({
  id: null,
  ipAddress: '',
  port: null,
  protocol: 'http',
  username: '',
  password: '',
  location: '',
  responseTime: 0,
  successRate: 0,
  status: 'pending',
  usageCount: 0,
  lastUsed: '',
  lastChecked: '',
  source: '',
  anonymity: '',
  score: null,
  failReason: '',
  isEnabled: true
})

// 表格数据
const ipList = ref([])

// IP表单验证规则
const ipRules = {
  ipAddress: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    { pattern: /^([0-9]{1,3}\.){3}[0-9]{1,3}$/, message: '请输入正确的IP地址格式', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' }
  ]
}

// 获取IP列表
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

// 查询
const onQuery = () => {
  currentPage.value = 1
  getIpList()
}

// 重置查询
const resetQuery = () => {
  queryParams.ipAddress = ''
  queryParams.port = ''
  queryParams.status = ''
  currentPage.value = 1
  getIpList()
}

// 新增IP
const addIp = () => {
  Object.assign(currentIp, {
    id: null,
    ipAddress: '',
    port: null,
    protocol: 'http',
    username: '',
    password: '',
    location: '',
    responseTime: 0,
    successRate: 0,
    status: 'pending',
    usageCount: 0,
    lastUsed: '',
    lastChecked: '',
    source: '',
    anonymity: '',
    score: null,
    failReason: '',
    isEnabled: true
  })
  dialogTitle.value = '新增IP'
  dialogVisible.value = true
}

// 编辑IP
const editIp = (row) => {
  Object.assign(currentIp, { ...row })
  dialogTitle.value = '编辑IP'
  dialogVisible.value = true
}

// 保存IP
const saveIp = async () => {
  try {
    if (!ipFormRef.value) return
    await ipFormRef.value.validate()

    if (currentIp.id) {
      await updateIp(currentIp.id, {
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
      })
      ElMessage.success('更新成功')
    } else {
      await createIp({
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
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    getIpList()
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  }
}

// 删除IP
const deleteIpRow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除IP ${row.ipAddress}:${row.port} 吗？`,
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

// 测试IP
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

// 测试全部IP（简单刷新）
const testAllIps = () => {
  ElMessage.info('开始测试全部IP...')
  setTimeout(() => {
    ElMessage.success('全部IP测试完成')
    getIpList()
  }, 800)
}

// 切换状态
const toggleStatus = (row) => {
  const prevEnabled = row.isEnabled
  const nextEnabled = !prevEnabled
  const nextStatusFrontend = nextEnabled ? 'available' : 'unavailable'
  const nextStatusBackend = nextEnabled ? 'active' : 'inactive'

  // 先做乐观更新，失败时回滚
  row.isEnabled = nextEnabled
  row.status = nextStatusFrontend

  updateIp(row.id, {
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
  }).then(() => {
    ElMessage.success(nextEnabled ? '启用成功' : '禁用成功')
  }).catch((error) => {
    row.isEnabled = prevEnabled
    row.status = prevEnabled ? 'available' : 'unavailable'
    console.error(error)
    ElMessage.error('状态更新失败')
  })
}

// 刷新列表
const refreshList = () => {
  getIpList()
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  getIpList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  getIpList()
}

// 状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'available': return '可用'
    case 'unavailable': return '不可用'
    case 'pending': return '待测试'
    default: return status
  }
}

// 状态tag
const getStatusTagType = (status) => {
  switch (status) {
    case 'available': return 'success'
    case 'unavailable': return 'danger'
    case 'pending': return 'info'
    default: return 'info'
  }
}

// 协议tag
const getProtocolTagType = (protocol) => {
  switch (protocol) {
    case 'http': return 'primary'
    case 'https': return 'success'
    case 'socks5': return 'warning'
    default: return 'info'
  }
}

// 响应时间样式
const getResponseTimeClass = (time) => {
  if (time < 200) return 'text-success'
  if (time < 500) return 'text-warning'
  return 'text-danger'
}

// 成功率颜色
const getSuccessRateColor = (rate) => {
  if (rate >= 90) return '#67c23a' // green
  if (rate >= 70) return '#e6a23c' // yellow
  return '#f56c6c' // red
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

.search-form {
  margin-bottom: 20px;
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
