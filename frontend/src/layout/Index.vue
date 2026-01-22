<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">管理后台</div>
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><House /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-sub-menu index="/admin/users">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/admin/users/frontend">前台用户</el-menu-item>
          <el-menu-item index="/admin/users/backend">后台用户</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/admin/match-schedule">
          <template #title>
            <el-icon><Timer /></el-icon>
            <span>比赛赛程</span>
          </template>
          <el-menu-item index="/admin/match-schedule/lottery">竞彩赛程</el-menu-item>
          <el-menu-item index="/admin/match-schedule/spider">爬虫赛程</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/admin/data">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-sub-menu index="/admin/intelligence">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>情报管理</span>
          </template>
          <el-menu-item index="/admin/intelligence">情报概览</el-menu-item>
          <el-menu-item index="/admin/intelligence/data-intelligence">数据情报</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/admin/crawler">
          <template #title>
            <el-icon><SetUp /></el-icon>
            <span>爬虫管理</span>
          </template>
          <el-menu-item index="/admin/crawler/source-config">源配置</el-menu-item>
          <el-menu-item index="/admin/crawler/data-source">数据源管理</el-menu-item>
          <el-menu-item index="/admin/crawler/task-scheduler">任务调度</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/admin/sp">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>足球SP管理</span>
          </template>
          <el-menu-item index="/admin/sp/data-sources">数据源管理</el-menu-item>
          <el-menu-item index="/admin/sp/matches">比赛信息管理</el-menu-item>
          <el-menu-item index="/admin/sp/records">SP值管理</el-menu-item>
          <el-menu-item index="/admin/sp/analysis">数据分析与洞察</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/admin/draw-prediction">
          <template #title>
            <el-icon><Platform /></el-icon>
            <span>平局预测管理</span>
          </template>
          <el-menu-item index="/admin/draw-prediction/data-feature">数据特征工程</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/model-train-eval">模型训练与评估</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/manage-deploy">模型管理与部署</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/prediction-monitor">预测监控</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/admin/system">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部 Header -->
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title || '当前页' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="user-info">
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ user?.username || '管理员' }}
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
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/user'
import { House, User, Timer, DataAnalysis, Document, SetUp, Setting, ArrowDown, Monitor, Calendar, Platform } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const logout = () => {
  authStore.clearAuth()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}
.sidebar {
  background-color: #304156;
}
.logo {
  color: #fff;
  font-size: 18px;
  text-align: center;
  padding: 16px;
  font-weight: bold;
}
.menu {
  border-right: none;
}
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ebeef5;
}
.breadcrumb {
  font-size: 14px;
}
.user-info {
  cursor: pointer;
}
.main {
  background: #f0f2f5;
  padding: 20px;
}
</style>