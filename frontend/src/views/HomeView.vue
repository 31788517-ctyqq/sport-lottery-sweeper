<template>
  <el-main>
    <div class="page-header">
      <h2>比赛管理</h2>
      <p class="subtitle">查看与管理所有比赛数据</p>
    </div>

    <el-card shadow="never" class="table-card">
      <template #header>
        <el-row justify="space-between" align="middle">
          <span>比赛列表</span>
          <el-button type="primary" :icon="Plus">新增</el-button>
        </el-row>
      </template>
      <el-table :data="matchList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="league" label="联赛" />
        <el-table-column prop="homeTeam" label="主队" />
        <el-table-column prop="awayTeam" label="客队" />
        <el-table-column prop="matchTime" label="比赛时间" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已结束' ? 'info' : 'success'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default>
            <el-button type="" size="small" style="border: none; background: transparent;">编辑</el-button>
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

const matchList = ref([
  { id: 1, league: '英超', homeTeam: '曼联', awayTeam: '切尔西', matchTime: '2025-01-25 20:00', status: '未开始' },
  { id: 2, league: '西甲', homeTeam: '巴萨', awayTeam: '皇马', matchTime: '2025-01-26 22:00', status: '未开始' },
  { id: 3, league: '德甲', homeTeam: '拜仁', awayTeam: '多特', matchTime: '2025-01-24 21:30', status: '已结束' }
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