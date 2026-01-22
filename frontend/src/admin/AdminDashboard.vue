<template>
  <div class="admin-dashboard">
    <h1>管理仪表板</h1>
    <p>欢迎使用系统管理后台。</p>
    <!-- 示例卡片 -->
    <el-row :gutter="20" class="dashboard-cards">
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>总用户数</span>
          </div>
          <div class="item">1,234</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>今日活跃</span>
          </div>
          <div class="item">567</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>数据源</span>
          </div>
          <div class="item">8</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>待处理情报</span>
          </div>
          <div class="item">23</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {};
  },
  methods: {}
};
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}
.dashboard-cards .el-col {
  margin-bottom: 20px;
}
.item {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}
</style>