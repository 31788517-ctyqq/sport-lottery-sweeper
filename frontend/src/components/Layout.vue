<template>
  <div class="app-layout">
    <!-- Sidebar Navigation -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="logo">
        <div class="logo-text">
          <h2>Sports Sweeper</h2>
          <span>体育彩票扫盘系统</span>
        </div>
      </div>

      <!-- Navigation Menu -->
      <el-menu
        :default-active="activeMenu"
        class="nav-menu"
        :collapse="sidebarCollapsed"
        @select="handleMenuSelect"
        router
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><House /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>
        
        <el-sub-menu index="intelligence">
          <template #title>
            <el-icon><Collection /></el-icon>
            <span>情报管理</span>
          </template>
          <el-menu-item index="/admin/intelligence/dashboard">情报仪表板</el-menu-item>
          <el-menu-item index="/admin/intelligence/collection">数据采集管理</el-menu-item>
          <el-menu-item index="/admin/intelligence/model">模型管理</el-menu-item>
          <el-menu-item index="/admin/intelligence/weight">权重管理</el-menu-item>
          <el-menu-item index="/admin/intelligence/graph">图谱管理</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- Main Content -->
    <div class="main-container" :class="{ 'expanded': sidebarCollapsed }">
      <!-- Header -->
      <div class="header">
        <div class="header-left">
          <el-button 
            type="link" 
            :icon="sidebarCollapsed ? Expand : Fold" 
            @click="toggleSidebar"
            class="collapse-btn"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- Real-time Status -->
          <el-badge :value="realtimeStatus.onlineUsers" class="status-item">
            <el-icon><UserFilled /></el-icon>
          </el-badge>
          
          <el-badge :value="realtimeStatus.systemHealth" :type="getHealthType(realtimeStatus.systemHealth)" class="status-item">
            <el-icon><CircleCheck /></el-icon>
          </el-badge>

          <!-- User Profile -->
          <el-dropdown @command="handleUserCommand">
            <span class="user-profile">
              <el-avatar :size="32" :src="userAvatar" v-if="hasAvatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-avatar :size="32" v-else>
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">管理员</span>
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
      </div>

      <!-- Content Area -->
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  House, Collection, User, Setting, Expand, Fold, UserFilled, 
  CircleCheck, ArrowDown, Bell, Search 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 添加响应式数据
const hasAvatar = ref(false)
const userAvatar = ref('/avatar.png') // 默认头像

// Sidebar state
const sidebarCollapsed = ref(false)

// Realtime status
const realtimeStatus = reactive({
  onlineUsers: 0,
  systemHealth: 100
})

// Breadcrumbs
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    title: item.meta.title,
    path: item.path
  }))
})

// Active menu
const activeMenu = computed(() => route.path)

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleMenuSelect = (index) => {
  console.log('Menu selected:', index)
}

const getHealthType = (health) => {
  if (health >= 90) return 'success'
  if (health >= 70) return 'warning'
  return 'danger'
}

const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('打开个人资料')
      break
    case 'settings':
      ElMessage.info('打开账户设置')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('token')
        router.push('/login')
        ElMessage.success('已退出登录')
      })
      break
  }
}

// Simulate realtime updates
let statusTimer = null
onMounted(() => {
  statusTimer = setInterval(() => {
    realtimeStatus.onlineUsers = Math.floor(Math.random() * 100) + 50
    realtimeStatus.systemHealth = Math.floor(Math.random() * 20) + 80
  }, 30000)
})

onUnmounted(() => {
  if (statusTimer) {
    clearInterval(statusTimer)
  }
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #001529 0%, #002140 100%);
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-bottom: 1px solid #333;
}

.logo-text h2 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.logo-text span {
  color: #b0b3b8;
  font-size: 12px;
}

.nav-menu {
  border-right: none;
  background: transparent;
}

.nav-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 6px;
}

.nav-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s;
}

.header {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 18px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-item {
  cursor: pointer;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-profile:hover {
  background-color: #f5f5f5;
}

.username {
  color: #333;
  font-weight: 500;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f5f5;
}

:deep(.el-breadcrumb__inner) {
  color: #666;
  font-weight: normal;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #333;
  font-weight: 600;
}
</style>
