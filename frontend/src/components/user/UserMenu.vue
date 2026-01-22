<template>
  <div class="user-menu" v-click-outside="closeMenu">
    <!-- 触发按钮 -->
    <button
      class="menu-trigger"
      :class="{ 'menu-open': isOpen }"
      @click="toggleMenu"
      aria-label="用户菜单"
    >
      <UserAvatar
        :src="user?.avatar"
        :username="user?.username"
        :size="36"
        show-status
      />
      <span class="username" v-if="showUsername">
        {{ user?.username || '未登录' }}
      </span>
      <i
        class="menu-icon"
        :class="isOpen ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"
      ></i>
    </button>

    <!-- 下拉菜单 -->
    <transition name="slide-down">
      <div v-if="isOpen" class="menu-dropdown">
        <!-- 用户信息区 -->
        <div class="user-info" v-if="user">
          <UserAvatar
            :src="user.avatar"
            :username="user.username"
            :size="48"
            class="dropdown-avatar"
          />
          <div class="user-details">
            <div class="username">{{ user.username }}</div>
            <div class="user-email">{{ user.email }}</div>
            <UserLevel :level="user.level" size="sm" />
          </div>
        </div>

        <!-- 未登录状态 -->
        <div v-else class="guest-info">
          <div class="guest-message">欢迎访问！</div>
          <div class="guest-action">
            请先登录以使用完整功能
          </div>
        </div>

        <div class="menu-divider"></div>

        <!-- 菜单项 -->
        <nav class="menu-items">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="menu-item"
            @click="closeMenu"
          >
            <i :class="item.icon" class="menu-item-icon"></i>
            <span class="menu-item-text">{{ item.text }}</span>
            <span v-if="item.badge" class="menu-badge">
              {{ item.badge }}
            </span>
          </router-link>
        </nav>

        <div class="menu-divider"></div>

        <!-- 操作按钮 -->
        <div class="menu-actions">
          <BaseButton
            v-if="user"
            variant="outline"
            size="sm"
            @click="handleLogout"
            class="logout-btn"
          >
            <i class="fas fa-sign-out-alt"></i>
            退出登录
          </BaseButton>
          
          <template v-else>
            <BaseButton
              variant="primary"
              size="sm"
              @click="handleLogin"
              class="login-btn"
            >
              <i class="fas fa-sign-in-alt"></i>
              立即登录
            </BaseButton>
            <BaseButton
              variant="outline"
              size="sm"
              @click="handleRegister"
            >
              <i class="fas fa-user-plus"></i>
              注册
            </BaseButton>
          </template>
        </div>

        <!-- 快捷设置 -->
        <div class="quick-settings" v-if="user">
          <div class="settings-title">快捷设置</div>
          <div class="settings-items">
            <label class="setting-item">
              <input
                type="checkbox"
                v-model="quickSettings.darkMode"
                @change="toggleDarkMode"
              />
              <span>深色模式</span>
            </label>
            <label class="setting-item">
              <input
                type="checkbox"
                v-model="quickSettings.notifications"
                @change="toggleNotifications"
              />
              <span>接收通知</span>
            </label>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { useThemeStore } from '@/store/modules/settings'
import { storeToRefs } from 'pinia'
import UserAvatar from './UserAvatar.vue'
import UserLevel from './UserLevel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import { useAuth } from '@/composables/useAuth'
import type { MenuItem } from '@/types/user'

// Props
interface Props {
  showUsername?: boolean
  position?: 'left' | 'right'
}

const props = withDefaults(defineProps<Props>(), {
  showUsername: true,
  position: 'right'
})

// Emits
const emit = defineEmits<{
  'menu-item-click': [item: MenuItem]
  'login-click': []
  'logout-click': []
  'register-click': []
}>()

// Store
const userStore = useUserStore()
const themeStore = useThemeStore()
const { currentUser } = storeToRefs(userStore)
const { isDarkMode } = storeToRefs(themeStore)

// Router
const router = useRouter()

// Composables
const { logout } = useAuth()

// State
const isOpen = ref(false)
const quickSettings = ref({
  darkMode: isDarkMode.value,
  notifications: true
})

// Computed
const user = computed(() => currentUser.value)

const menuItems = computed<MenuItem[]>(() => {
  const baseItems: MenuItem[] = [
    {
      path: '/profile',
      text: '个人中心',
      icon: 'fas fa-user-circle'
    },
    {
      path: '/favorites',
      text: '我的收藏',
      icon: 'fas fa-heart',
      badge: user.value?.stats?.favorites || 0
    },
    {
      path: '/notifications',
      text: '消息通知',
      icon: 'fas fa-bell',
      badge: user.value?.unreadNotifications || 0
    },
    {
      path: '/settings',
      text: '系统设置',
      icon: 'fas fa-cog'
    },
    {
      path: '/history',
      text: '历史记录',
      icon: 'fas fa-history'
    }
  ]

  // 管理员菜单项
  if (user.value?.role === 'admin') {
    baseItems.push({
      path: '/admin',
      text: '管理后台',
      icon: 'fas fa-tachometer-alt',
      badge: 'Admin'
    })
  }

  // 高级用户菜单项
  if (user.value?.level >= 3) {
    baseItems.splice(2, 0, {
      path: '/analysis',
      text: '数据分析',
      icon: 'fas fa-chart-line'
    })
  }

  return baseItems
})

// Methods
const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const closeMenu = () => {
  isOpen.value = false
}

const handleLogin = () => {
  closeMenu()
  emit('login-click')
  router.push('/login')
}

const handleRegister = () => {
  closeMenu()
  emit('register-click')
  router.push('/register')
}

const handleLogout = async () => {
  try {
    await logout()
    closeMenu()
    emit('logout-click')
    router.push('/')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

const toggleDarkMode = () => {
  themeStore.toggleTheme()
}

const toggleNotifications = () => {
  // 这里调用API更新通知设置
  console.log('通知设置已更新:', quickSettings.value.notifications)
}

const handleMenuItemClick = (item: MenuItem) => {
  emit('menu-item-click', item)
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isOpen.value) {
    closeMenu()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// Watch
watch(isDarkMode, (newVal) => {
  quickSettings.value.darkMode = newVal
})
</script>

<style scoped>
.user-menu {
  position: relative;
}

.menu-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: none;
  border: 1px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
}

.menu-trigger:hover {
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.menu-trigger.menu-open {
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.username {
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-icon {
  font-size: 0.75rem;
  color: var(--text-secondary);
  transition: transform 0.2s ease;
}

.menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 320px;
  margin-top: 8px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow: hidden;
}

:global(.user-menu[position="left"] .menu-dropdown) {
  right: auto;
  left: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.user-info {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 12px;
}

.dropdown-avatar {
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-details .username {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 2px;
}

.user-email {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.guest-info {
  padding: 20px;
  text-align: center;
}

.guest-message {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.guest-action {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.menu-divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 8px 0;
}

.menu-items {
  padding: 8px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
  transition: background-color 0.2s;
  position: relative;
}

.menu-item:hover {
  background-color: var(--bg-secondary);
}

.menu-item.router-link-active {
  background-color: var(--primary-light);
  color: var(--primary);
}

.menu-item.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: var(--primary);
}

.menu-item-icon {
  width: 20px;
  margin-right: 12px;
  font-size: 1rem;
  text-align: center;
}

.menu-item-text {
  flex: 1;
  font-size: 0.95rem;
}

.menu-badge {
  padding: 2px 8px;
  background-color: var(--primary);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  min-width: 24px;
  text-align: center;
}

.menu-actions {
  display: flex;
  gap: 8px;
  padding: 16px;
}

.menu-actions .login-btn,
.menu-actions .logout-btn {
  flex: 1;
}

.quick-settings {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.settings-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.settings-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  user-select: none;
}

.setting-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

@media (max-width: 640px) {
  .menu-dropdown {
    width: 280px;
  }
  
  .user-info {
    padding: 12px;
  }
}
</style>