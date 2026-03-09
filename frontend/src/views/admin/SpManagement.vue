<template>
  <div class="sp-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>足球SP管理</span>
          <el-tag type="primary">与爬虫管理同级模块</el-tag>
        </div>
      </template>
      
      <!-- 子菜单导航 -->
      <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick">
        <el-tab-pane label="数据源管理" name="data-sources">
          <DataSourceManagement />
        </el-tab-pane>
        
        <el-tab-pane label="比赛信息管理" name="matches">
          <MatchManagement />
        </el-tab-pane>
        
        <el-tab-pane label="SP值管理" name="sp-records">
          <SPRecordManagement />
        </el-tab-pane>
        
        <el-tab-pane label="数据分析与洞察" name="analysis">
          <DataAnalysisInsight />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DataSourceManagement from './sp/DataSourceManagement.vue'
import MatchManagement from './sp/MatchManagement.vue'
import SPRecordManagement from './sp/SPRecordManagement.vue'
import DataAnalysisInsight from './sp/DataAnalysisInsight.vue'

const router = useRouter()
const activeTab = ref('data-sources')

// 处理标签页点击
const handleTabClick = (tab) => {
  const tabName = tab.name
  // 可以在这里添加路由跳转逻辑
  console.log('切换到标签页:', tabName)
}

// 根据路由参数设置默认标签页
const route = router.currentRoute.value
if (route.query.tab) {
  activeTab.value = route.query.tab
}
</script>

<style scoped>
.sp-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-tabs--card >>> .el-tabs__header {
  margin: 0;
}

.el-tabs--card >>> .el-tabs__item {
  font-weight: 500;
}
</style>