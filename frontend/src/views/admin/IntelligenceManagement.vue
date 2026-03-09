<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>情报管理中心</span>
        </div>
      </template>
      <div class="dashboard-content">
        <div class="stats-grid">
          <el-card class="stat-card">
            <div class="stat-info">
              <div class="stat-number">1,250</div>
              <div class="stat-label">今日新增情报</div>
            </div>
            <div class="stat-icon bg-blue">
              <i class="el-icon-data-analysis"></i>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-info">
              <div class="stat-number">98.4%</div>
              <div class="stat-label">准确率</div>
            </div>
            <div class="stat-icon bg-green">
              <i class="el-icon-success-filled"></i>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-info">
              <div class="stat-number">245</div>
              <div class="stat-label">活跃数据源</div>
            </div>
            <div class="stat-icon bg-purple">
              <i class="el-icon-connection"></i>
            </div>
          </el-card>
          
          <el-card class="stat-card">
            <div class="stat-info">
              <div class="stat-number">86</div>
              <div class="stat-label">情报类型</div>
            </div>
            <div class="stat-icon bg-orange">
              <i class="el-icon-menu"></i>
            </div>
          </el-card>
        </div>

        <div class="quick-nav">
          <h3>快速导航</h3>
          <div class="nav-grid">
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/dashboard')"
            >
              <i class="el-icon-monitor"></i>
              <div class="nav-text">仪表板</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/data-intelligence')"
            >
              <i class="el-icon-data-line"></i>
              <div class="nav-text">数据情报</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/collection-management')"
            >
              <i class="el-icon-collection-tag"></i>
              <div class="nav-text">采集管理</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/screening-management')"
            >
              <i class="el-icon-search"></i>
              <div class="nav-text">筛选管理</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/weight-management')"
            >
              <i class="el-icon-scale-to-rule"></i>
              <div class="nav-text">权重管理</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/graph-management')"
            >
              <i class="el-icon-data-board"></i>
              <div class="nav-text">图表管理</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/model-management')"
            >
              <i class="el-icon-files"></i>
              <div class="nav-text">模型管理</div>
            </el-card>
            
            <el-card 
              class="nav-item" 
              @click="$router.push('/admin/intelligence/crawler-intelligence')"
            >
              <i class="el-icon-cpu"></i>
              <div class="nav-text">爬虫情报</div>
            </el-card>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 统计数据
const stats = ref({
  todayNew: 1250,
  accuracyRate: '98.4%',
  activeSources: 245,
  intelligenceTypes: 86
})

onMounted(() => {
  console.log('Intelligence Management Dashboard loaded')
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-content {
  padding: 20px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.stat-info .stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-info .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.bg-blue {
  background: linear-gradient(135deg, #73a7ff, #4a7dff);
}

.bg-green {
  background: linear-gradient(135deg, #67c23a, #529b2e);
}

.bg-purple {
  background: linear-gradient(135deg, #a068f1, #8a47e0);
}

.bg-orange {
  background: linear-gradient(135deg, #f79d2d, #e67612);
}

.quick-nav h3 {
  margin: 20px 0 15px;
  font-size: 18px;
  font-weight: 600;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 20px;
}

.nav-item {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  padding: 20px 10px;
}

.nav-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.nav-item i {
  font-size: 28px;
  margin-bottom: 10px;
  color: #4a7dff;
}

.nav-text {
  font-size: 14px;
  color: #606266;
}
</style>