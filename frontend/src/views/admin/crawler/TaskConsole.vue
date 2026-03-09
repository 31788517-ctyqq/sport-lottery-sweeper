<template>
  <div class="task-center-page">
    <div class="page-header">
      <h2>任务中心</h2>
      <p>统一管理任务配置与执行监控</p>
    </div>

    <el-card class="task-center-card" shadow="never">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="任务配置" name="config">
          <TaskCenterTaskConfigTab />
        </el-tab-pane>
        <el-tab-pane label="执行监控" name="executions">
          <TaskCenterExecutionTab />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TaskCenterExecutionTab from './components/TaskCenterExecutionTab.vue'
import TaskCenterTaskConfigTab from './components/TaskCenterTaskConfigTab.vue'

const activeTab = ref('config')
</script>

<style scoped>
.task-center-page {
  padding: 0;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.page-header p {
  margin: 8px 0 0;
  color: #6b7280;
}

.task-center-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

:deep(.el-tabs__header) {
  margin: 0;
  padding: 8px 16px 0;
}

:deep(.el-tabs__content) {
  padding: 16px;
}
</style>
