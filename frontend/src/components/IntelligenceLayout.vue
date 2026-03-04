<template>
  <div class="intelligence-layout">
    <!-- Intelligence Management Sidebar -->
    <div class="intelligence-sidebar">
      <div class="sidebar-header">
        <h3>情报管理</h3>
      </div>
      <el-menu 
        :default-active="activeMenu" 
        class="intelligence-menu"
        @select="handleMenuSelect"
        router
      >
        <el-menu-item index="/admin/intelligence/screening">
          <el-icon><TrendCharts /></el-icon>
          <span>信息筛选</span>
        </el-menu-item>
        <el-menu-item index="/admin/intelligence/collection">
          <el-icon><Download /></el-icon>
          <span>信息采集</span>
        </el-menu-item>
        <el-menu-item index="/admin/intelligence/model">
          <el-icon><Cpu /></el-icon>
          <span>情报模型</span>
        </el-menu-item>
        <el-menu-item index="/admin/intelligence/weight">
          <el-icon><ScaleToOriginal /></el-icon>
          <span>情报权重</span>
        </el-menu-item>
        <el-menu-item index="/admin/intelligence/graph">
          <el-icon><Share /></el-icon>
          <span>情报图谱</span>
        </el-menu-item>
        <el-menu-item index="/admin/intelligence/data-intelligence">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据情报</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- Main Content Area -->
    <div class="intelligence-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  TrendCharts, Download, Cpu, ScaleToOriginal, Share, DataAnalysis
} from '@element-plus/icons-vue'

const route = useRoute()

// Active menu based on current route
const activeMenu = computed(() => route.path)

const handleMenuSelect = (index) => {
  console.log('Selected menu:', index)
}
</script>

<style scoped>
.intelligence-layout {
  display: flex;
  height: 100%;
  background: #f5f5f5;
}

.intelligence-sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.intelligence-menu {
  flex: 1;
  border-right: none;
}

.intelligence-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 6px;
}

.intelligence-menu .el-menu-item:hover {
  background-color: #f0f9ff;
  color: #409eff;
}

.intelligence-menu .el-menu-item.is-active {
  background-color: #409eff;
  color: white;
}

.intelligence-menu .el-menu-item .el-icon {
  margin-right: 8px;
}

.intelligence-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>