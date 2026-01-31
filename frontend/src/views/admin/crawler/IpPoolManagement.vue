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
            <el-button type="primary" @click="addIp">添加IP</el-button>
            <el-button @click="refreshList">刷新</el-button>
            <el-button @click="testAllIps">测试全部</el-button>
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

      <el-table :data="ipList" style="width: 100%" v-loading="loading">
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
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="使用次数" width="100" />
        <el-table-column prop="lastUsed" label="最后使用" width="150" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="testIp(scope.row)">测试</el-button>
            <el-button size="small" @click="editIp(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteIp(scope.row)">删除</el-button>
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

    <!-- IP编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
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

const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

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
  isEnabled: true
})

// 表格数据
const ipList = ref([])

// IP表单验证规则
const ipRules = {
  ipAddress: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: '请输入正确的IP地址格式', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' }
  ]
}

// 获取IP列表
const getIpList = () => {
  loading.value = true
  
  // 模拟获取数据
  setTimeout(() => {
    // 根据查询条件过滤数据
    let data = mockIpData
    
    if (queryParams.ipAddress) {
      data = data.filter(item => item.ipAddress.includes(queryParams.ipAddress))
    }
    
    if (queryParams.port) {
      data = data.filter(item => String(item.port).includes(queryParams.port))
    }
    
    if (queryParams.status) {
      data = data.filter(item => item.status === queryParams.status)
    }
    
    // 计算总数
    total.value = data.length
    
    // 计算当前页数据
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    ipList.value = data.slice(start, end)
    
    loading.value = false
  }, 500)
}

// 搜索
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

// 添加IP
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
    isEnabled: true
  })
  
  dialogTitle.value = '添加IP'
  dialogVisible.value = true
}

// 编辑IP
const editIp = (row) => {
  Object.assign(currentIp, { ...row })
  dialogTitle.value = '编辑IP'
  dialogVisible.value = true
}

// 保存IP
const saveIp = () => {
  // 这里应该是实际的保存逻辑
  console.log('保存IP:', currentIp)
  dialogVisible.value = false
  ElMessage.success('保存成功')
  getIpList()
}

// 删除IP
const deleteIp = async (row) => {
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
    
    // 实际删除逻辑
    console.log('删除IP:', row)
    ElMessage.success('删除成功')
    getIpList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 测试IP
const testIp = (row) => {
  // 模拟测试过程
  ElMessage.info(`正在测试IP: ${row.ipAddress}:${row.port}`)
  
  // 模拟异步测试结果
  setTimeout(() => {
    ElMessage.success(`IP ${row.ipAddress} 测试成功`)
    // 更新列表中的IP状态
    const index = ipList.value.findIndex(ip => ip.id === row.id)
    if (index !== -1) {
      ipList.value[index].status = 'available'
      ipList.value[index].responseTime = Math.floor(Math.random() * 1000)
      ipList.value[index].successRate = Math.floor(Math.random() * 40) + 60 // 60-100%
    }
  }, 1000)
}

// 测试全部IP
const testAllIps = () => {
  ElMessage.info('开始测试全部IP...')
  
  // 模拟测试过程
  setTimeout(() => {
    ElMessage.success('全部IP测试完成')
    getIpList()
  }, 2000)
}

// 切换IP状态
const toggleStatus = (row) => {
  row.isEnabled = !row.isEnabled
  const statusText = row.isEnabled ? '启用' : '禁用'
  ElMessage.success(`IP ${statusText}成功`)
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

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'available': return '可用'
    case 'unavailable': return '不可用'
    case 'pending': return '待测试'
    default: return status
  }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'available': return 'success'
    case 'unavailable': return 'danger'
    case 'pending': return 'info'
    default: return 'info'
  }
}

// 获取协议标签类型
const getProtocolTagType = (protocol) => {
  switch (protocol) {
    case 'http': return 'primary'
    case 'https': return 'success'
    case 'socks5': return 'warning'
    default: return 'info'
  }
}

// 获取响应时间样式
const getResponseTimeClass = (time) => {
  if (time < 200) return 'text-success'
  if (time < 500) return 'text-warning'
  return 'text-danger'
}

// 获取成功率颜色
const getSuccessRateColor = (rate) => {
  if (rate >= 90) return '#67c23a' // green
  if (rate >= 70) return '#e6a23c' // yellow
  return '#f56c6c' // red
}

// 模拟数据
const mockIpData = [
  { id: 1, ipAddress: '192.168.1.100', port: 8080, protocol: 'http', location: '北京', responseTime: 150, successRate: 95, status: 'available', usageCount: 120, lastUsed: '2026-01-30 10:30:00', isEnabled: true },
  { id: 2, ipAddress: '10.0.0.50', port: 3128, protocol: 'https', location: '上海', responseTime: 210, successRate: 88, status: 'available', usageCount: 95, lastUsed: '2026-01-30 09:45:20', isEnabled: true },
  { id: 3, ipAddress: '203.0.113.25', port: 1080, protocol: 'socks5', location: '广州', responseTime: 0, successRate: 0, status: 'pending', usageCount: 0, lastUsed: '-', isEnabled: true },
  { id: 4, ipAddress: '198.51.100.75', port: 80, protocol: 'http', location: '深圳', responseTime: 320, successRate: 75, status: 'available', usageCount: 80, lastUsed: '2026-01-30 08:20:15', isEnabled: false },
  { id: 5, ipAddress: '192.0.2.45', port: 8080, protocol: 'https', location: '杭州', responseTime: 0, successRate: 0, status: 'unavailable', usageCount: 5, lastUsed: '2026-01-29 16:30:45', isEnabled: true },
  { id: 6, ipAddress: '203.0.113.15', port: 3128, protocol: 'http', location: '成都', responseTime: 180, successRate: 92, status: 'available', usageCount: 110, lastUsed: '2026-01-30 11:15:30', isEnabled: true },
  { id: 7, ipAddress: '198.51.100.120', port: 1080, protocol: 'socks5', location: '武汉', responseTime: 0, successRate: 0, status: 'pending', usageCount: 0, lastUsed: '-', isEnabled: true },
  { id: 8, ipAddress: '192.0.2.88', port: 80, protocol: 'http', location: '西安', responseTime: 0, successRate: 0, status: 'unavailable', usageCount: 3, lastUsed: '2026-01-28 14:20:10', isEnabled: false }
]

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