<template>
  <div class="spider-schedule-container">
    <el-card class="schedule-card" :body-style="{ padding: '0' }">
      <div class="card-header">
        <h3>爬虫任务安排</h3>
      </div>
      
      <div class="schedule-controls">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select v-model="selectedSource" placeholder="选择数据源" class="source-selector">
              <el-option label="竞彩官方" value="jc-official"></el-option>
              <el-option label="彩票网站" value="caipiao-site"></el-option>
              <el-option label="体育新闻" value="sports-news"></el-option>
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="loadSchedules">查询</el-button>
            <el-button @click="refreshSchedules">刷新</el-button>
          </el-col>
        </el-row>
      </div>
      
      <div class="table-wrapper">
        <el-table 
          :data="schedules" 
          stripe 
          style="width: 100%" 
          v-loading="loading"
          height="calc(100vh - 260px)"
          :header-cell-style="{background: '#f5f7fa', color: '#606266'}"
        >
          <el-table-column prop="taskId" label="任务ID" width="100"></el-table-column>
          <el-table-column prop="source" label="数据源" width="120"></el-table-column>
          <el-table-column prop="targetUrl" label="目标URL" min-width="200"></el-table-column>
          <el-table-column prop="frequency" label="频率" width="100"></el-table-column>
          <el-table-column prop="lastRun" label="最后执行" width="150"></el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" :resizable="true">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="viewDetails(row)">查看详情</el-button>
                <el-button size="small" type="primary" @click="editTask(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTask(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        ></el-pagination>
      </div>
    </el-card>
    
    <!-- 编辑任务对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑爬虫任务"
      width="50%"
      :before-close="closeEditDialog"
    >
      <el-form :model="currentTask" label-width="100px">
        <el-form-item label="数据源">
          <el-input v-model="currentTask.source" disabled></el-input>
        </el-form-item>
        <el-form-item label="目标URL">
          <el-input v-model="currentTask.targetUrl"></el-input>
        </el-form-item>
        <el-form-item label="频率">
          <el-select v-model="currentTask.frequency">
            <el-option label="每分钟" value="every_minute"></el-option>
            <el-option label="每5分钟" value="every_5_minutes"></el-option>
            <el-option label="每10分钟" value="every_10_minutes"></el-option>
            <el-option label="每30分钟" value="every_30_minutes"></el-option>
            <el-option label="每小时" value="hourly"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="currentTask.enabled"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeEditDialog">取消</el-button>
          <el-button type="primary" @click="saveTask">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'

// 数据响应式变量
const schedules = ref([])
const loading = ref(false)
const selectedSource = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showEditDialog = ref(false)
const currentTask = ref({})

// 模拟数据加载
const loadSchedules = async () => {
  loading.value = true
  
  // 模拟API请求
  setTimeout(() => {
    schedules.value = [
      { taskId: 'S001', source: '竞彩官方', targetUrl: 'https://www.example.com/schedule', frequency: '每5分钟', lastRun: '2026-01-20 14:00', status: '运行中', enabled: true },
      { taskId: 'S002', source: '彩票网站', targetUrl: 'https://www.lottery-site.com/data', frequency: '每10分钟', lastRun: '2026-01-20 13:55', status: '暂停', enabled: false },
      { taskId: 'S003', source: '体育新闻', targetUrl: 'https://www.sports-news.com/fixtures', frequency: '每小时', lastRun: '2026-01-20 13:00', status: '运行中', enabled: true },
      { taskId: 'S004', source: '竞彩官方', targetUrl: 'https://www.jc-data.com/live', frequency: '每分钟', lastRun: '2026-01-20 14:05', status: '异常', enabled: true },
      { taskId: 'S005', source: '彩票网站', targetUrl: 'https://www.cp-site.com/fixtures', frequency: '每30分钟', lastRun: '2026-01-20 13:30', status: '运行中', enabled: true },
    ]
    total.value = schedules.value.length
    loading.value = false
  }, 800)
}

// 刷新数据
const refreshSchedules = () => {
  loadSchedules()
}

// 根据状态返回标签类型
const getStatusType = (status) => {
  switch(status) {
    case '运行中': return 'success'
    case '暂停': return 'warning'
    case '异常': return 'danger'
    default: return 'info'
  }
}

// 查看详情
const viewDetails = (row) => {
  console.log('查看任务详情:', row)
  // 这里可以跳转到详情页面或打开对话框
}

// 编辑任务
const editTask = (row) => {
  currentTask.value = {...row}
  showEditDialog.value = true
}

// 删除任务
const deleteTask = (row) => {
  ElMessageBox.confirm(
    `确定要删除任务 "${row.taskId}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    schedules.value = schedules.value.filter(item => item.taskId !== row.taskId)
    ElMessage.success('删除成功')
  }).catch(() => {
    // 用户取消删除
  })
}

// 保存任务
const saveTask = () => {
  const index = schedules.value.findIndex(item => item.taskId === currentTask.value.taskId)
  if (index !== -1) {
    schedules.value[index] = {...currentTask.value}
    ElMessage.success('保存成功')
  }
  closeEditDialog()
}

// 关闭编辑对话框
const closeEditDialog = () => {
  showEditDialog.value = false
  currentTask.value = {}
}

// 分页相关方法
const handleSizeChange = (size) => {
  pageSize.value = size
  loadSchedules()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadSchedules()
}

// 页面加载时获取数据
onMounted(() => {
  loadSchedules()
})
</script>

<style scoped>
.spider-schedule-container {
  padding: 0;
  height: calc(100vh - 120px);
  width: 100%;
}

.schedule-card {
  height: 100%;
  border: none;
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  font-size: 16px;
  background-color: #fafafa;
}

.schedule-controls {
  padding: 20px;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.source-selector {
  width: 100%;
}

.table-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  height: calc(100% - 180px);
}

.el-table {
  width: 100%;
}

.pagination-wrapper {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
  background-color: #fff;
  text-align: right;
}

.dialog-footer {
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons .el-button {
  margin: 0;
}
</style>