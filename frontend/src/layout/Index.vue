<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">彩票扫盘系统</div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#424242"
        text-color="#e4e7ed"
        active-text-color="#409EFF"
        unique-opened
      >
        <!-- 1. 仪表台 -->
        <el-menu-item index="/admin/dashboard">
          <el-icon><House /></el-icon>
          <span>仪表台</span>
        </el-menu-item>

        <!-- 2. 用户管理 -->
        <el-sub-menu index="/admin/users">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/admin/users/list">用户列表</el-menu-item>
          <el-menu-item index="/admin/users/roles">角色与权限</el-menu-item>
          <el-menu-item index="/admin/users/departments">部门管理</el-menu-item>
          <el-menu-item index="/admin/users/profile">个人中心</el-menu-item>
          <el-menu-item index="/admin/users/profiles">用户画像管理</el-menu-item>
          <el-menu-item index="/admin/users/logs">操作日志</el-menu-item>
        </el-sub-menu>

        <!-- 新增: 精算工具中心 -->
        <el-sub-menu index="/admin/analytic-tools">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>精算工具中心</span>
          </template>
          <el-menu-item index="/admin/beidan-filter">北单三维筛选器</el-menu-item>
        </el-sub-menu>

        <!-- 3. 数据源管理 -->
        <el-sub-menu index="/admin/data-source">
          <template #title>
            <el-icon><SetUp /></el-icon>
            <span>数据源管理</span>
          </template>
          <!-- AI_WORKING: coder1 @2026-02-04 - 添加任务执行监控菜单项 -->
          <el-menu-item index="/admin/data-source/config">数据源配置</el-menu-item>
          <el-menu-item index="/admin/data-source/task-console">任务控制台</el-menu-item>
          <el-menu-item index="/admin/data-source/monitor">爬虫监控</el-menu-item>
          <el-menu-item index="/admin/data-source/data-center">数据中心</el-menu-item>
          <el-menu-item index="/admin/data-source/ip-pool">IP池管理</el-menu-item>
          <el-menu-item index="/admin/data-source/headers">请求头管理</el-menu-item>
          <el-menu-item index="/admin/data-source/task-monitor">任务执行监控</el-menu-item>
          <!-- AI_DONE: coder1 @2026-02-04 -->
        </el-sub-menu>

        <!-- 4. 比赛数据管理 -->
        <el-sub-menu index="/admin/match-data">
          <template #title>
            <el-icon><Soccer /></el-icon>
            <span>比赛数据管理</span>
          </template>
          <el-menu-item index="/admin/match-data/matches">比赛管理</el-menu-item>
          <el-menu-item index="/admin/match-data/odds">赔率管理</el-menu-item>
          <el-menu-item index="/admin/match-data/schedule/jczq">竞彩赛程</el-menu-item>
          <el-menu-item index="/admin/match-data/schedule/bd">北单赛程</el-menu-item>
          <el-menu-item index="/admin/match-data/leagues">联赛管理</el-menu-item>
        </el-sub-menu>

        <!-- 5. 平局预测管理 -->
        <el-sub-menu index="/admin/draw-prediction">
          <template #title>
            <el-icon><Histogram /></el-icon>
            <span>平局预测管理</span>
          </template>
          <el-menu-item index="/admin/draw-prediction/data-features">数据与特征管理</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/training-evaluation">模型训练与评估</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/model-deployment">模型管理与部署</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/prediction-monitoring">预测服务与监控</el-menu-item>
        </el-sub-menu>

        <!-- 6. AI服务管理 -->
        <el-sub-menu index="/admin/ai-services">
          <template #title>
            <el-icon><ChatLineRound /></el-icon>
            <span>AI服务管理</span>
          </template>
          <el-menu-item index="/admin/ai-services/local">本地AI服务</el-menu-item>
          <el-menu-item index="/admin/ai-services/remote">远程AI服务</el-menu-item>
          <el-menu-item index="/admin/ai-services/costs">成本监控</el-menu-item>
          <el-menu-item index="/admin/ai-services/agents">智能体管理</el-menu-item>
          <el-menu-item index="/admin/ai-services/models">预测模型管理</el-menu-item>
          <el-menu-item index="/admin/ai-services/conversation">对话助手</el-menu-item>
          <el-menu-item index="/admin/ai-services/config">配置管理</el-menu-item>
        </el-sub-menu>

        <!-- 7. 智能决策 -->
        <el-sub-menu index="/admin/intelligent-decision">
          <template #title>
            <el-icon><Management /></el-icon>
            <span>智能决策</span>
          </template>
          <el-menu-item index="/admin/intelligent-decision/hedging">对冲策略管理</el-menu-item>
          <el-menu-item index="/admin/intelligent-decision/recommendations">推荐系统管理</el-menu-item>
          <el-menu-item index="/admin/intelligent-decision/risk-control">风险控制</el-menu-item>
        </el-sub-menu>

        <!-- 9. 情报分析 -->
        <el-sub-menu index="/admin/intelligence">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>情报分析</span>
          </template>
          <el-menu-item index="/admin/intelligence/screening">智能筛选</el-menu-item>
          <el-menu-item index="/admin/intelligence/collection">采集管理</el-menu-item>
          <el-menu-item index="/admin/intelligence/model">模型管理</el-menu-item>
          <el-menu-item index="/admin/intelligence/weight">权重管理</el-menu-item>
          <el-menu-item index="/admin/intelligence/sentiment">情感分析</el-menu-item>
          <el-menu-item index="/admin/intelligence/multimodal">多模态分析</el-menu-item>
        </el-sub-menu>

        <!-- 11. 系统管理 -->
        <el-sub-menu index="/admin/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/system/config">系统配置</el-menu-item>
          <el-menu-item index="/admin/system/monitoring">性能监控</el-menu-item>
          <el-menu-item index="/admin/system/backup">数据备份</el-menu-item>
          <el-menu-item index="/admin/system/api">API管理</el-menu-item>
        </el-sub-menu>

        <!-- 12. 日志管理 -->
        <el-sub-menu index="/admin/logs">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>日志管理</span>
          </template>
          <el-menu-item index="/admin/logs">日志总览</el-menu-item>
          <el-menu-item index="/admin/logs/system">系统日志</el-menu-item>
          <el-menu-item index="/admin/logs/user">用户日志</el-menu-item>
          <el-menu-item index="/admin/logs/security">安全日志</el-menu-item>
          <el-menu-item index="/admin/logs/api">API日志</el-menu-item>
          <el-menu-item index="/admin/logs/ai">AI服务日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title || '当前页' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="user-info">
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ authStore.user?.username || '管理员' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  House, 
  UserFilled,
  SetUp, 
  Soccer,
  ChatLineRound,
  Management,
  Document, 
  Memo,
  Setting, 
  Tickets,
  ArrowDown,
  DataAnalysis
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const logout = () => {
  authStore.logout()
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  background: #f9fafb; /* 更柔和的页面背景 */
}

.sidebar {
  background-color: #424242;
  /* 去掉厚重阴影，仅保留细微层次 */
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.08);
}

.logo {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  padding: 16px 8px;
  border-bottom: 1px solid #383838;
  letter-spacing: 1px;
}

.menu {
  border-right: none;
  height: calc(100vh - 60px);
  background-color: #424242;
}

.menu :deep(.el-sub-menu__title),
.menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  padding-left: 24px !important;
}

.menu :deep(.el-sub-menu .el-menu-item) {
  background-color: #2c2c2c;
  padding-left: 44px !important;
}

.menu :deep(.el-sub-menu__title) {
  color: #e4e7ed;
  font-weight: 500;
}

.menu :deep(.el-menu-item) {
  color: #acacac;
}

.menu :deep(.el-menu-item:hover),
.menu :deep(.el-sub-menu__title:hover) {
  background-color: #4a4a4a !important;
}

.menu :deep(.el-icon) {
  width: 20px;
  text-align: center;
  margin-right: 8px;
  vertical-align: middle;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 顶部导航栏 - 干净现代 */
.header {
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #e5e7eb; /* 细灰线代替厚重阴影 */
  /* 去掉 box-shadow，减少视觉压迫 */
  z-index: 10;
}

.breadcrumb {
  font-size: 15px;
  color: #374151;
}

.user-info {
  cursor: pointer;
  color: #374151;
  font-weight: 500;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 主内容区 - 轻盈背景，适当留白 */
.main {
  background: #f9fafb;
  padding: 24px;
  min-height: calc(100vh - 60px);
}
</style>