<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">数据源管理</span>
        <el-select v-model="filterStatus" placeholder="筛选状态" size="small" style="width:120px; float:right; margin-left:10px;">
          <el-option label="全部" value="" />
          <el-option label="在线" value="online" />
          <el-option label="离线" value="offline" />
        </el-select>
      </template>

      <el-table :data="filteredTableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="数据源名称" />
        <el-table-column prop="url" label="地址" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status==='online'?'success':'danger'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="success_rate" label="成功率(%)" width="100" />
        <el-table-column prop="response_time" label="响应时间(ms)" width="120" />
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button size="small" @click="checkHealth(scope.row.id)">健康检查</el-button>
            <el-button size="small" :type="scope.row.status==='online'?'warning':'success'" @click="toggleStatus(scope.row)">
              {{ scope.row.status==='online'?'停用':'启用' }}
            </el-button>
            <!-- 100qiu数据源特有的获取按钮 -->
            <el-button 
              v-if="scope.row.name && scope.row.name.includes('100qiu')" 
              size="small" 
              type="success" 
              @click="handleFetch(scope.row.id)"
              :loading="fetchingIds.includes(scope.row.id)"
            >
              获取
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="healthDialogVisible" title="健康检查" width="400px">
      <p>状态: <strong>{{ healthResult.status }}</strong></p>
      <p v-if="healthResult.status==='online'">响应时间: {{ healthResult.response_time_ms }} ms</p>
      <p v-if="healthResult.status_code">状态码: {{ healthResult.status_code }}</p>
      <template #footer>
        <el-button @click="healthDialogVisible=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSources as listSources, healthCheck, updateStatus } from '@/api/crawlerSource'

// 添加100qiu API调用
const fetch100qiu = async (id) => {
  const response = await fetch(`/api/v1/data-source-100qiu/${id}/fetch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include'
  })
  return response.json()
}

const tableData = ref([])
const filterStatus = ref('')
const healthDialogVisible = ref(false)
const healthResult = ref({})
const fetchingIds = ref([])

const filteredTableData = computed(() => {
  if (!filterStatus.value) return tableData.value
  return tableData.value.filter(item => item.status === filterStatus.value)
})

const loadData = async () => {
  const res = await listSources()
  tableData.value = res.data || []
}

const checkHealth = async (id) => {
  const res = await healthCheck(id)
  healthResult.value = res.data || {}
  healthDialogVisible.value = true
}

const toggleStatus = async (row) => {
  const newStatus = row.status === 'online' ? 'offline' : 'online'
  await updateStatus(row.id, { status: newStatus })
  ElMessage.success(`已${newStatus==='online'?'启用':'停用'}`)
  loadData()
}

// 100qiu数据源获取功能
const handleFetch = async (id) => {
  fetchingIds.value.push(id)
  try {
    const response = await fetch100qiu(id)
    
    // 检查响应格式 - 这里是关键修复点
    if (response.success) {
      // 新的响应格式: { success, message, total_fetched, sample_data }
      ElMessage.success(`获取成功，获取数量：${response.total_fetched}；${response.message}`)
    } else {
      throw new Error('获取失败')
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
    fetchingIds.value = fetchingIds.value.filter(itemId => itemId !== id)
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.card-header {
  font-weight: bold;
  font-size: 18px;
}
</style>