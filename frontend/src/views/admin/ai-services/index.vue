<template>
  <div class="ai-services-main">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <div>
            <h3>🤖 AI服务管理</h3>
            <p class="subtitle">统一管理本地和远程AI服务、智能体、模型等</p>
          </div>
        </div>
      </template>

      <!-- AI服务概览 -->
      <el-row :gutter="20" class="overview-stats">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <i class="el-icon-office-building" />
              </div>
              <div class="stat-info">
                <div class="stat-label">本地服务</div>
                <div class="stat-value">3</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <i class="el-icon-position" />
              </div>
              <div class="stat-info">
                <div class="stat-label">远程服务</div>
                <div class="stat-value">4</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <i class="el-icon-timer" />
              </div>
              <div class="stat-info">
                <div class="stat-label">智能体</div>
                <div class="stat-value">6</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-purple">
                <i class="el-icon-setting" />
              </div>
              <div class="stat-info">
                <div class="stat-label">模型</div>
                <div class="stat-value">4</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 快速访问 -->
      <el-card class="quick-access-card">
        <template #header>
          <div class="card-header">
            <h4>⚡ 快速访问</h4>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="6" v-for="item in quickAccessItems" :key="item.title">
            <el-card 
              class="quick-access-item" 
              @click="navigateTo(item.route)"
            >
              <div class="access-icon">
                <i :class="item.icon" class="access-icon-inner" />
              </div>
              <div class="access-title">{{ item.title }}</div>
              <div class="access-desc">{{ item.desc }}</div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>

      <!-- 最近活动 -->
      <el-card class="recent-activity-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <h4>📋 最近活动</h4>
          </div>
        </template>
        
        <el-table :data="recentActivities" style="width: 100%">
          <el-table-column prop="time" label="时间" width="150" />
          <el-table-column prop="action" label="操作" width="200" />
          <el-table-column prop="details" label="详情" />
        </el-table>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 快速访问项目
const quickAccessItems = ref([
  {
    title: '本地AI服务',
    desc: '管理本地AI服务（ClawDBot、Ollama等）',
    icon: 'el-icon-office-building',
    route: '/admin/ai-services/local'
  },
  {
    title: '远程AI服务',
    desc: '管理远程AI服务提供商（OpenAI、Anthropic等）',
    icon: 'el-icon-position',
    route: '/admin/ai-services/remote'
  },
  {
    title: '成本监控',
    desc: '监控AI服务成本和使用情况',
    icon: 'el-icon-wallet',
    route: '/admin/ai-services/costs'
  },
  {
    title: '智能体管理',
    desc: '管理各类AI智能体',
    icon: 'el-icon-avatar',
    route: '/admin/ai-services/agents'
  },
  {
    title: '预测模型管理',
    desc: '管理预测模型和准确率',
    icon: 'el-icon-data-analysis',
    route: '/admin/ai-services/models'
  },
  {
    title: '对话助手',
    desc: '使用AI对话助手',
    icon: 'el-icon-chat-line',
    route: '/admin/ai-services/conversation'
  },
  {
    title: '配置管理',
    desc: 'AI服务配置管理',
    icon: 'el-icon-setting',
    route: '/admin/ai-services/config'
  },
  {
    title: '全部服务',
    desc: '查看所有AI服务状态',
    icon: 'el-icon-monitor',
    route: '/admin/ai-services/local'
  }
])

// 最近活动数据
const recentActivities = ref([
  { time: '2026-01-30 05:25', action: '添加新模型', details: '比赛结果预测模型 v1.2.4 已添加' },
  { time: '2026-01-30 05:20', action: '更新配置', details: '成本预算更新为 ¥600' },
  { time: '2026-01-30 05:15', action: '智能体重启', details: '赔率监控智能体已重启' },
  { time: '2026-01-30 05:10', action: '服务测试', details: 'ClawDBot-Primary 服务测试成功' },
  { time: '2026-01-30 05:05', action: '模型训练', details: '情感分析模型完成新一轮训练' }
])

// 导航方法
const navigateTo = (route) => {
  router.push(route)
  ElMessage.success(`正在跳转到 ${route}`)
}
</script>

<style scoped>
.card-container {
  margin: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header > div:first-child h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.overview-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.bg-blue { background: #409eff; }
.bg-green { background: #67c23a; }
.bg-orange { background: #e6a23c; }
.bg-purple { background: #9013fe; }

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.quick-access-card {
  margin-top: 20px;
}

.quick-access-item {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.quick-access-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.access-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #409eff, #73aaf5);
}

.access-icon-inner {
  font-size: 28px;
  color: white;
}

.access-title {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 16px;
}

.access-desc {
  font-size: 12px;
  color: #909399;
}

.recent-activity-card {
  margin-top: 20px;
}
</style>