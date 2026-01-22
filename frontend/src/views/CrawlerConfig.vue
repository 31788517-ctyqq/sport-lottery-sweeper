<template>
  <el-main>
    <div class="page-header">
      <h2>爬虫配置</h2>
      <p class="subtitle">管理数据源与抓取规则</p>
    </div>

    <el-card shadow="never" class="table-card">
      <template #header>
        <el-row justify="space-between" align="middle">
          <span>配置列表</span>
          <el-button type="primary" :icon="Plus">新增</el-button>
        </el-row>
      </template>
      <el-table :data="configList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sourceName" label="数据源名称" />
        <el-table-column prop="urlPattern" label="URL规则" />
        <el-table-column prop="interval" label="抓取间隔(分钟)" />
        <el-table-column prop="enabled" label="启用">
          <template #default="scope">
            <el-tag :type="scope.row.enabled ? 'success' : 'info'">{{ scope.row.enabled ? '是' : '否' }}</el-tag>
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

const configList = ref([
  { id: 1, sourceName: '500彩票网', urlPattern: 'https://www.500.com/*', interval: 60, enabled: true },
  { id: 2, sourceName: '新浪体育', urlPattern: 'https://sports.sina.com.cn/*', interval: 120, enabled: false },
  { id: 3, sourceName: '腾讯体育', urlPattern: 'https://sports.qq.com/*', interval: 30, enabled: true }
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