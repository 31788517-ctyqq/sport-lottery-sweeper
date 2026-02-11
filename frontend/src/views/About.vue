<template>
  <div class="about-container">
    <el-card class="about-card">
      <template #header>
        <div class="card-header">
          <span>关于我们</span>
        </div>
      </template>
      
      <div class="about-content">
        <h2>体育彩票扫盘系统</h2>
        <p>这是一个专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。</p>
        
        <h3>系统特点</h3>
        <ul>
          <li>基于三维精算模型的智能筛选算法</li>
          <li>实时数据采集与处理</li>
          <li>多维度数据分析与可视化</li>
          <li>灵活的策略配置与管理</li>
          <li>高可用性和可扩展性</li>
        </ul>
        
        <h3>技术架构</h3>
        <ul>
          <li><strong>前端</strong>: Vue 3 + Vite + TypeScript + Element Plus</li>
          <li><strong>后端</strong>: Python 3.11 + FastAPI + Uvicorn</li>
          <li><strong>数据库</strong>: SQLite (开发环境) / PostgreSQL (生产环境)</li>
          <li><strong>缓存</strong>: Redis 7+</li>
          <li><strong>异步任务</strong>: Celery + Redis/RabbitMQ</li>
        </ul>
        
        <h3>联系我们</h3>
        <p>如有任何问题或建议，请通过以下方式联系我们：</p>
        <ul>
          <li>邮箱：<a href="mailto:support@example.com">support@example.com</a></li>
          <li>电话：400-123-4567</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'About'
};
</script>

<style scoped>
.about-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 100px);
}

.about-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.about-content h2 {
  color: #303133;
  margin-bottom: 16px;
}

.about-content h3 {
  color: #606266;
  margin: 20px 0 12px;
}

.about-content p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.about-content ul {
  color: #606266;
  padding-left: 20px;
  margin-bottom: 16px;
}

.about-content li {
  margin-bottom: 8px;
  line-height: 1.5;
}
</style>