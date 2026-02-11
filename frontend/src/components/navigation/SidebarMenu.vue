<template>
  <aside 
    class="sidebar-menu" 
    :class="{ open: isOpen, collapsed: isCollapsed && !isMobile }"
    @touchstart="onTouchStart"
    @touchend="onTouchEnd"
  >
    <div class="sidebar-header">
      <div class="logo-container">
        <i class="fas fa-futbol logo-icon"></i>
        <h2 class="logo-text" v-show="!isCollapsed || isMobile">竞彩扫盘</h2>
      </div>
      <!-- 桌面端收缩/展开按钮 -->
      <button class="collapse-btn" @click="toggleCollapse" v-show="!isMobile">
        <i :class="isCollapsed ? 'fas fa-angle-right' : 'fas fa-angle-left'"></i>
      </button>
      <button class="close-btn" @click="closeMenu" v-show="isMobile">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <nav class="sidebar-nav">
      <div 
        v-for="item in menuItems" 
        :key="item.path || item.name"
        class="nav-item"
        :class="{ active: isActive(item.path || item.children?.[0]?.path) }"
        @click="navigateTo(item.path || item.children?.[0]?.path, item)"
      >
        <i :class="item.icon" class="nav-icon"></i>
        <span class="nav-text" v-show="!isCollapsed || isMobile">{{ item.text }}</span>
        
        <!-- 子菜单 -->
        <div 
          v-if="item.children && item.children.length > 0"
          class="sub-menu"
          :class="{ visible: isSubmenuVisible[item.name] }"
        >
          <div
            v-for="child in item.children"
            :key="child.path"
            class="sub-nav-item"
            :class="{ active: isActive(child.path) }"
            @click.stop="navigateTo(child.path)"
          >
            <i :class="child.icon || 'fas fa-chevron-right'" class="nav-icon"></i>
            <span class="nav-text">{{ child.text }}</span>
          </div>
        </div>
      </div>
    </nav>
    
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="avatar">
          <i class="fas fa-user"></i>
        </div>
        <div class="user-details" v-show="!isCollapsed || isMobile">
          <div class="username">用户</div>
          <div class="user-level">VIP会员</div>
        </div>
      </div>
    </div>
  </aside>
  
  <div v-if="isOpen" class="sidebar-overlay" @click="closeMenu"></div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import menuConfig from '@/components/Sidebar/MenuConfig.js'

const router = useRouter()
const route = useRoute()
const isOpen = ref(false)
const isCollapsed = ref(false)
const isMobile = ref(false)
const isSubmenuVisible = ref({})

// 手势相关
const touchStartX = ref(0)
const SWIPE_THRESHOLD = 50 // 最小滑动距离

// 使用统一的菜单配置
const menuItems = menuConfig

const navigateTo = (path, item) => {
  if (item && item.children && item.children.length > 0) {
    // 如果是父菜单，切换子菜单显示状态
    isSubmenuVisible.value[item.name] = !isSubmenuVisible.value[item.name];
  } else if (path) {
    router.push(path)
    closeMenu()
  }
}

const isActive = (path) => {
  if (!path) return false;
  return route.path.startsWith(path) || route.path === path
}

const openMenu = () => {
  isOpen.value = true
  document.body.style.overflow = 'hidden'
}

const closeMenu = () => {
  isOpen.value = false
  document.body.style.overflow = ''
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 检测移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 手势处理
const onTouchStart = (e) => {
  touchStartX.value = e.changedTouches[0].screenX
}
const onTouchEnd = (e) => {
  const touchEndX = e.changedTouches[0].screenX
  const dx = touchEndX - touchStartX.value
  if (Math.abs(dx) > SWIPE_THRESHOLD) {
    if (dx > 0 && !isOpen.value) {
      openMenu()
    } else if (dx < 0 && isOpen.value) {
      closeMenu()
    }
  }
}

defineExpose({ openMenu, closeMenu })
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
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1), width 0.35s ease, box-shadow 0.35s ease;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
}

.sidebar-menu.open {
  transform: translateX(0);
}

.sidebar-menu.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-header);
  position: relative;
}

.logo-container {
  display: flex;
  align-items: center;
  margin-right: 12px;
}

.sidebar-menu.collapsed .logo-container {
  justify-content: center;
  margin-right: 0;
}

.logo-icon {
  font-size: 24px;
  color: var(--primary);
  margin-right: 10px;
}

.sidebar-menu.collapsed .logo-icon {
  margin-right: 0;
}

.logo-text {
  color: var(--text-main);
  margin: 0;
  font-size: 18px;
}

.collapse-btn {
  position: absolute;
  right: -12px;
  top: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-sub);
  cursor: pointer;
  z-index: 10;
}

.collapse-btn:hover {
  color: var(--primary);
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
  padding: 10px 16px;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.nav-item:hover,
.nav-item.active {
  background: rgba(88, 166, 255, 0.1);
  color: var(--primary);
}

.nav-icon {
  margin-right: 10px;
  width: 20px;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  line-height: 1;
}

.sidebar-menu.collapsed .nav-text {
  display: none;
}

.nav-text {
  font-size: 16px;
}

.sub-menu {
  position: absolute;
  left: 100%;
  top: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  min-width: 200px;
  z-index: 1002;
  display: none;
}

.sub-menu.visible {
  display: block;
}

.sub-nav-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s;
}

.sub-nav-item:hover,
.sub-nav-item.active {
  background: rgba(88, 166, 255, 0.1);
  color: var(--primary);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-header);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-menu.collapsed .user-details {
  display: none;
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
  opacity: 0;
  transition: opacity 0.25s ease, visibility 0.25s;
  visibility: hidden;
}

.sidebar-menu.open + .sidebar-overlay {
  opacity: 1;
  visibility: visible;
}

/* 响应式适配 */
@media (max-width: 480px) {
  .sidebar-menu {
    width: 100%;
    max-width: 100%;
    transform: translateX(-100%);
    box-shadow: none;
  }
  .sidebar-overlay {
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  .sidebar-menu.open + .sidebar-overlay {
    opacity: 1;
  }
  .sub-menu {
    position: static;
    width: 100%;
    box-shadow: none;
    border: none;
    border-top: 1px solid var(--border-color);
    margin-top: 10px;
  }
}

@media (min-width: 481px) and (max-width: 767px) {
  .sidebar-menu {
    width: 80%;
    max-width: 320px;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .sidebar-menu {
    width: 220px;
  }
  .sidebar-menu.open {
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }
}

@media (min-width: 1025px) {
  .sidebar-menu {
    width: 260px;
  }
}
</style>