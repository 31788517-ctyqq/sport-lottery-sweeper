<template>
  <el-main>
    <div class="page-header">
      <h2>智能分析</h2>
      <p class="subtitle">查看模型预测与数据分析结果</p>
    </div>

    <el-card shadow="never" class="table-card">
      <template #header>
        <el-row justify="space-between" align="middle">
          <span>分析记录</span>
          <el-button type="primary" :icon="Plus">新增</el-button>
        </el-row>
      </template>
      <el-table :data="analysisList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model" label="模型名称" />
        <el-table-column prop="accuracy" label="准确率" />
        <el-table-column prop="createdAt" label="生成时间" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === '完成' ? 'success' : 'warning'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default>
            <el-button type="" size="small" style="border: none; background: transparent;">查看</el-button>
            <el-button type="" size="small" style="border: none; background: transparent; color: #f56c6c">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </el-main>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const analysisList = ref([
  { id: 1, model: '胜平负预测V1', accuracy: '82%', createdAt: '2025-01-20 10:00', status: '完成' },
  { id: 2, model: '进球数预测V2', accuracy: '76%', createdAt: '2025-01-19 15:30', status: '完成' },
  { id: 3, model: '半全场预测V1', accuracy: '—', createdAt: '2025-01-20 12:00', status: '运行中' }
])
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}
.page-header h2 {
  margin: 0;
  font-size: 22px;
  color: #1e293b;
}
.subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}
.table-card {
  border-radius: 12px;
}
</style>