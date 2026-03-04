<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon class="logo-icon"><Trophy /></el-icon>
          <span v-if="!collapsed" class="logo-text">扫盘系统</span>
        </div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
        background-color="#001529"
        text-color="#fff"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>
        
        <el-sub-menu index="match-management">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>比赛管理</span>
          </template>
          <el-menu-item index="/matches">比赛列表</el-menu-item>
          <el-menu-item index="/matches/create">创建比赛</el-menu-item>
          <el-menu-item index="/live-matches">直播比赛</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="prediction-management">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>预测分析</span>
          </template>
          <el-menu-item index="/predictions/draw">平局预测</el-menu-item>
          <el-menu-item index="/predictions/history">预测历史</el-menu-item>
          <el-menu-item index="/predictions/accuracy">准确率统计</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="intelligence-management">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>情报管理</span>
          </template>
          <el-menu-item index="/intelligence">情报列表</el-menu-item>
          <el-menu-item index="/intelligence/create">添加情报</el-menu-item>
          <el-menu-item index="/intelligence/sources">情报源</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="odds-management" v-if="authStore.isAdmin">
          <template #title>
            <el-icon><Money /></el-icon>
            <span>赔率管理</span>
          </template>
          <el-menu-item index="/odds">赔率列表</el-menu-item>
          <el-menu-item index="/odds/companies">博彩公司</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="user-management" v-if="authStore.isAdmin">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/admin/users">用户列表</el-menu-item>
          <el-menu-item index="/admin/users/create">创建用户</el-menu-item>
          <el-menu-item index="/admin/roles">角色管理</el-menu-item>
          <el-menu-item index="/admin/permissions">权限管理</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="system-management" v-if="authStore.isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/system/config">系统配置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button 
            type="link" 
            @click="toggleSidebar" 
            class="collapse-btn"
          >
            <el-icon>
              <Fold v-if="!collapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>
          
          <breadcrumb class="breadcrumb" />
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="authStore.userInfo?.avatar">
                {{ authStore.userInfo?.nickname?.charAt(0) || authStore.userInfo?.username?.charAt(0) }}
              </el-avatar>
              <span class="username">{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">账户设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component, route }">
          <transition name="fade-transform" mode="out-in">
            <keep-alive :include="cachedViews">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Breadcrumb from './Breadcrumb.vue'
import {
  Trophy, House, Calendar, TrendCharts, Document, 
  Money, User, Setting, Fold, Expand, ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏折叠状态
const collapsed = ref(false)

// 缓存的视图
const cachedViews = ref(['DashboardView'])

// 计算属性
const sidebarWidth = computed(() => collapsed.value ? '64px' : '240px')
const activeMenu = computed(() => route.path)

// 切换侧边栏
const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      await authStore.logout()
      router.push('/login')
      break
  }
}

onMounted(async () => {
  await authStore.initializeAuth()
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
}

.sidebar {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #1d2a3a;
}

.logo {
  display: flex;
  align-items: center;
  color: white;
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: 18px;
  margin-right: 20px;
  padding: 0;
  height: auto;
}

.breadcrumb {
  margin-left: 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #333;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 过渡动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -240px;
    z-index: 1000;
    transition: left 0.3s;
  }
  
  .sidebar.show {
    left: 0;
  }
  
  .main-content {
    padding: 10px;
  }
}
</style>
