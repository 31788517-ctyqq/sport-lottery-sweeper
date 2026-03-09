<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">任务调度</span>
      </template>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="source_id" label="数据源ID" width="100" />
        <el-table-column prop="cron_expr" label="Cron表达式" />
        <el-table-column prop="next_run_time" label="下次执行时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260">
          <template #default="scope">
            <el-button size="small" @click="triggerTask(scope.row.id)">立即执行</el-button>
            <el-button size="small" @click="viewLogs(scope.row.id)">查看日志</el-button>
            <el-button size="small" :type="scope.row.status==='paused'?'success':'warning'" @click="togglePause(scope.row)">
              {{ scope.row.status==='paused'?'恢复':'暂停' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="logDialogVisible" title="执行日志" width="600px">
      <el-table :data="logData" border size="small">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="level" label="级别" width="80">
          <template #default="scope">
            <el-tag :type="levelTagType(scope.row.level)" size="small">{{ scope.row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="msg" label="消息" />
      </el-table>
      <template #footer>
        <el-button @click="logDialogVisible=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listTasks, triggerTask as apiTriggerTask, getLogs } from '@/api/crawlerTask'

const tableData = ref([])
const logDialogVisible = ref(false)
const logData = ref([])

const statusTagType = (status) => {
  return status === 'running' ? 'primary' : status === 'paused' ? 'warning' : 'info'
}
const levelTagType = (level) => {
  return level === 'ERROR' ? 'danger' : level === 'WARNING' ? 'warning' : 'success'
}

const loadData = async () => {
  const res = await listTasks()
  tableData.value = res.data || []
}

const triggerTask = async (id) => {
  await apiTriggerTask(id)
  ElMessage.success('任务已触发')
}

const viewLogs = async (id) => {
  const res = await getLogs(id)
  logData.value = res.data || []
  logDialogVisible.value = true
}

const togglePause = async (row) => {
  const newStatus = row.status === 'paused' ? 'idle' : 'paused'
  // 这里用 updateTask 接口，需要补上对应 API，暂时用 ElMessage 提示
  ElMessage.info(`已${newStatus==='paused'?'暂停':'恢复'}任务 ${row.id}（需后端支持）`)
  // 实际应调用 updateTask(row.id, {status: newStatus}).then(loadData)
}

const handleDelete = () => {
  ElMessage.info('删除功能待实现')
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