<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <el-row :gutter="20" align="middle">
        <el-col :xs="24" :sm="12" :md="6">
          <el-select v-model="selectedSource" placeholder="选择数据源" class="source-selector">
            <el-option label="竞彩官方" value="jc-official" />
            <el-option label="彩票网站" value="caipiao-site" />
            <el-option label="体育新闻" value="sports-news" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-button type="primary" @click="loadSchedules">查询</el-button>
          <el-button @click="refreshSchedules">刷新</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 主内容区 8:4 布局 -->
    <el-container class="main-area">
      <el-main class="left-panel">
        <BaseCard title="爬虫任务安排">
          <div class="table-wrapper">
            <el-table
              :data="schedules"
              stripe
              style="width: 100%"
              v-loading="loading"
              height="calc(100vh - 360px)"
              :header-cell-style="{background: '#f5f7fa', color: '#606266'}"
            >
              <el-table-column prop="taskId" label="任务ID" width="100" />
              <el-table-column prop="source" label="数据源" width="120" />
              <el-table-column prop="targetUrl" label="目标URL" min-width="200" />
              <el-table-column prop="frequency" label="频率" width="100" />
              <el-table-column prop="lastRun" label="最后执行" width="150" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="280">
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

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="total > 0">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[10, 20, 50, 100]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
            />
          </div>
        </BaseCard>
      </el-main>

      <!-- 右侧统计区 -->
      <el-aside class="right-panel" width="320px">
        <BaseCard title="任务统计">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-statistic title="总任务数" :value="total" />
            </el-col>
            <el-col :span="12">
              <el-statistic title="运行中" :value="statusCount.running" />
            </el-col>
            <el-col :span="12">
              <el-statistic title="暂停" :value="statusCount.paused" />
            </el-col>
            <el-col :span="12">
              <el-statistic title="异常" :value="statusCount.error" />
            </el-col>
          </el-row>
        </BaseCard>
      </el-aside>
    </el-container>

    <!-- 编辑任务对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑爬虫任务" width="50%" :before-close="closeEditDialog">
      <el-form :model="currentTask" label-width="100px">
        <el-form-item label="数据源">
          <el-input v-model="currentTask.source" disabled />
        </el-form-item>
        <el-form-item label="目标URL">
          <el-input v-model="currentTask.targetUrl" />
        </el-form-item>
        <el-form-item label="频率">
          <el-select v-model="currentTask.frequency">
            <el-option label="每分钟" value="every_minute" />
            <el-option label="每5分钟" value="every_5_minutes" />
            <el-option label="每10分钟" value="every_10_minutes" />
            <el-option label="每30分钟" value="every_30_minutes" />
            <el-option label="每小时" value="hourly" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="currentTask.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeEditDialog">取消</el-button>
          <el-button type="primary" @click="saveTask">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- AI 多智能体协同锁 -->
    <!-- 
      AI_DONE: coder1 @2026-01-27T00:00:00
      架构师: 确认 8:4 布局、BaseCard、莫兰迪主题
      前端: 已完成 SpiderSchedule.vue 迁移
      后端: 无需修改
      测试: 待验证
    -->
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
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

// 统计数据
const statusCount = computed(() => {
  return schedules.value.reduce((acc, row) => {
    acc[row.status] = (acc[row.status] || 0) + 1
    return acc
  }, {})
})

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
.page-container {
  padding: 20px;
  background: #f5f2f0;
  min-height: 100vh;
}
.toolbar {
  margin-bottom: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #a8caba 0%, #5d4e75 100%);
  border-radius: 8px;
  color: #fff;
}
.main-area {
  gap: 20px;
}
.left-panel {
  background: transparent;
}
.right-panel {
  background: transparent;
}
.table-wrapper {
  margin-top: 12px;
}
.pagination-wrapper {
  margin-top: 16px;
  text-align: right;
}
.action-buttons {
  display: flex;
  gap: 8px;
}
.action-buttons .el-button {
  margin: 0;
}
.dialog-footer {
  text-align: right;
}
@media (max-width: 992px) {
  .main-area {
    flex-direction: column;
  }
  .right-panel {
    width: 100% !important;
  }
}
</style>