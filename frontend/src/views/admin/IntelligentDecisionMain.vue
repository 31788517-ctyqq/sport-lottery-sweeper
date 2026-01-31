<template>
  <div class="intelligent-decision-main">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>智能决策系统</h3>
          <p class="subtitle">利用AI技术实现智能化决策支持，包括对冲策略、推荐系统和风险控制</p>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="decision-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <i class="icon icon-hedging" />
                <span>对冲策略管理</span>
              </div>
            </template>
            <div class="card-content">
              <p>管理各种对冲策略，监控策略执行效果，优化收益与风险平衡</p>
              <el-button 
                type="primary" 
                @click="$router.push('/admin/intelligent-decision/hedging')"
                style="margin-top: 15px;"
              >
                管理策略
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="decision-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <i class="icon icon-recommendation" />
                <span>推荐系统管理</span>
              </div>
            </template>
            <div class="card-content">
              <p>基于用户画像和历史行为，提供个性化投注建议和策略推荐</p>
              <el-button 
                type="primary" 
                @click="$router.push('/admin/intelligent-decision/recommendations')"
                style="margin-top: 15px;"
              >
                配置推荐
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="decision-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <i class="icon icon-risk" />
                <span>风险控制</span>
              </div>
            </template>
            <div class="card-content">
              <p>设置风险阈值，监控风险指标，保障资金安全和合规运营</p>
              <el-button 
                type="primary" 
                @click="$router.push('/admin/intelligent-decision/risk-control')"
                style="margin-top: 15px;"
              >
                配置风控
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="stats-card">
            <template #header>
              <div class="card-title">
                <i class="icon icon-performance" />
                <span>整体性能统计</span>
              </div>
            </template>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">125</div>
                  <div class="stat-label">策略总数</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">87%</div>
                  <div class="stat-label">成功率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">+3.2%</div>
                  <div class="stat-label">平均收益率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">42</div>
                  <div class="stat-label">活跃策略</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="stats-card">
            <template #header>
              <div class="card-title">
                <i class="icon icon-ai" />
                <span>AI服务状态</span>
              </div>
            </template>
            <div class="ai-service-status">
              <el-tag type="success" size="large" style="margin-right: 10px;">LLM服务: 正常</el-tag>
              <el-tag type="success" size="large" style="margin-right: 10px;">智能体: 运行中</el-tag>
              <el-tag type="warning" size="large">预测模型: 重启中</el-tag>
            </div>
            <div class="ai-cost">
              <p>今日AI服务成本: <strong>¥24.50</strong></p>
              <p>本月累计成本: <strong>¥680.30</strong></p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // 初始化页面数据
  console.log('智能决策主页面已加载')
})
</script>

<style scoped>
.intelligent-decision-main {
  padding: 20px;
}

.card-header h3 {
  margin: 0 0 10px 0;
  font-size: 22px;
}

.subtitle {
  color: #606266;
  margin: 0;
  font-size: 14px;
}

.decision-card {
  height: 200px;
  transition: transform 0.3s ease;
}

.decision-card:hover {
  transform: translateY(-5px);
}

.card-title {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.card-title .icon {
  margin-right: 8px;
  font-size: 18px;
}

.icon-hedging::before {
  content: "💰";
}

.icon-recommendation::before {
  content: "⭐";
}

.icon-risk::before {
  content: "🔒";
}

.icon-performance::before {
  content: "📊";
}

.icon-ai::before {
  content: "🤖";
}

.card-content {
  min-height: 100px;
}

.stats-card {
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.ai-service-status {
  margin-bottom: 15px;
}

.ai-cost p {
  margin: 5px 0;
  font-size: 14px;
}
</style>