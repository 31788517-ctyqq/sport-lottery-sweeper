<template>
  <el-main>
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">代理总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">可用</div>
          <div class="stat-value">{{ stats.available }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">不可用</div>
          <div class="stat-value">{{ stats.unavailable }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">平均延迟</div>
          <div class="stat-value">{{ stats.avgLatency }} ms</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-input v-model="search" placeholder="搜索IP地址或协议" clearable style="width: 240px" />
        <el-button type="primary" :icon="Plus" @click="showAddDialog">新增</el-button>
        <el-button @click="loadProxies">刷新</el-button>
      </div>
    </el-card>

    <!-- 代理表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredProxyList" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="host" label="IP地址" />
        <el-table-column prop="port" label="端口" />
        <el-table-column prop="protocol" label="协议" />
        <el-table-column prop="latency" label="延迟(ms)" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === '可用' ? 'success' : 'danger'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="" size="small" style="border: none; background: transparent;" @click="handleTest(scope.row.id)">测试</el-button>
            <el-button type="" size="small" style="border: none; background: transparent; color: #f56c6c" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增代理弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增代理" width="400px">
      <el-form :model="addForm" label-width="80px" ref="addFormRef">
        <el-form-item label="IP地址" prop="host" :rules="[{ required: true, message: '请输入IP地址', trigger: 'blur' }]">
          <el-input v-model="addForm.host" />
        </el-form-item>
        <el-form-item label="端口" prop="port" :rules="[{ required: true, message: '请输入端口', trigger: 'blur' }]">
          <el-input v-model.number="addForm.port" type="number" />
        </el-form-item>
        <el-form-item label="协议">
          <el-select v-model="addForm.protocol" style="width: 100%">
            <el-option label="HTTP" value="HTTP" />
            <el-option label="HTTPS" value="HTTPS" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAdd">确定</el-button>
      </template>
    </el-dialog>
  </el-main>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getProxyList, addProxy, deleteProxy, testProxy } from '@/api/proxy'

const proxyList = ref([])
const loading = ref(false)
const addDialogVisible = ref(false)
const addFormRef = ref(null)
const search = ref('')

const stats = reactive({
  total: 45,
  available: 38,
  unavailable: 7,
  avgLatency: 120
})

const addForm = reactive({
  host: '',
  port: '',
  protocol: 'HTTP'
})

const filteredProxyList = computed(() =>
  proxyList.value.filter(row =>
    row.host.includes(search.value) || row.protocol.includes(search.value)
  )
)

async function loadProxies() {
  loading.value = true
  try {
    const res = await getProxyList()
    proxyList.value = res
  } catch (e) {
    ElMessage.error('加载代理列表失败')
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  addForm.host = ''
  addForm.port = ''
  addForm.protocol = 'HTTP'
  addDialogVisible.value = true
}

async function confirmAdd() {
  await addFormRef.value.validate()
  try {
    await addProxy(addForm)
    ElMessage.success('添加成功')
    addDialogVisible.value = false
    loadProxies()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除该代理吗？', '提示', { type: 'warning' })
    const loadingInstance = ElLoading.service({ fullscreen: true })
    await deleteProxy(id)
    loadingInstance.close()
    ElMessage.success('删除成功')
    loadProxies()
  } catch (e) {}
}

async function handleTest(id) {
  try {
    const loadingInstance = ElLoading.service({ fullscreen: true })
    const res = await testProxy(id)
    loadingInstance.close()
    ElMessage.success(`测试完成：${res.status}，延迟 ${res.latency}ms`)
    loadProxies()
  } catch (e) {
    ElMessage.error('测试失败')
  }
}

onMounted(loadProxies)
</script>

<style scoped>
.stat-row { margin-bottom: 24px; }
.stat-card { border-radius: 12px; text-align: center; }
.stat-title { color: #64748b; font-size: 14px; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #1e293b; }
.toolbar-card { border-radius: 12px; margin-bottom: 24px; }
.toolbar { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.table-card { border-radius: 12px; }
.modern-table { border-radius: 12px; overflow: hidden; }
</style>