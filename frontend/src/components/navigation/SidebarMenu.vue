<template>
  <aside class="sidebar-menu" :class="{ open: isOpen }">
    <div class="sidebar-header">
      <div class="logo-container">
        <i class="fas fa-futbol logo-icon"></i>
        <h2 class="logo-text">竞彩扫盘</h2>
      </div>
      <button class="close-btn" @click="closeMenu">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <nav class="sidebar-nav">
      <div 
        v-for="item in menuItems" 
        :key="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        @click="navigateTo(item.path)"
      >
        <i :class="item.icon" class="nav-icon"></i>
        <span class="nav-text">{{ item.text }}</span>
      </div>
    </nav>
    
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="avatar">
          <i class="fas fa-user"></i>
        </div>
        <div class="user-details">
          <div class="username">用户</div>
          <div class="user-level">VIP会员</div>
        </div>
      </div>
    </div>
  </aside>
  
  <div v-if="isOpen" class="sidebar-overlay" @click="closeMenu"></div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isOpen = ref(false)

// 菜单项
const menuItems = [
  { path: '/', text: '首页', icon: 'fas fa-home' },
  { path: '/matches', text: '比赛列表', icon: 'fas fa-futbol' },
  { path: '/analysis', text: '数据分析', icon: 'fas fa-chart-bar' },
  { path: '/intelligence', text: '情报中心', icon: 'fas fa-newspaper' },
  { path: '/favorites', text: '我的收藏', icon: 'fas fa-star' },
  { path: '/settings', text: '系统设置', icon: 'fas fa-cog' }
]

// 方法
const navigateTo = (path) => {
  router.push(path)
  closeMenu()
}

const isActive = (path) => {
  return route.path === path
}

const openMenu = () => {
  isOpen.value = true
  document.body.style.overflow = 'hidden'
}

const closeMenu = () => {
  isOpen.value = false
  document.body.style.overflow = ''
}

// 提供给父组件使用
defineExpose({
  openMenu,
  closeMenu
})
</script>

<style scoped>
.sidebar-menu {
  position: fixed;
  top: 0;
  left: 0;
  width: 280px;
  height: 100%;
  background: var(--bg-card);
  z-index: 1001;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
}

.sidebar-menu.open {
  transform: translateX(0);
}

.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-header);
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo-icon {
  font-size: 24px;
  color: var(--primary);
  margin-right: 10px;
}

.logo-text {
  color: var(--text-main);
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-sub);
  font-size: 18px;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s;
}

.nav-item:hover,
.nav-item.active {
  background: rgba(88, 166, 255, 0.1);
  color: var(--primary);
}

.nav-icon {
  margin-right: 12px;
  width: 20px;
  text-align: center;
}

.nav-text {
  font-size: 16px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-header);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(88, 166, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  font-size: 18px;
}

.user-details {
  flex: 1;
}

.username {
  color: var(--text-main);
  font-weight: 500;
  margin-bottom: 4px;
}

.user-level {
  color: var(--text-sub);
  font-size: 12px;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}
</style>