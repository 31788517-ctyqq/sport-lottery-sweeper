<template>
  <nav
    class="breadcrumb"
    :class="breadcrumbClasses"
    aria-label="面包屑导航"
  >
    <!-- 分隔符前缀 -->
    <div v-if="showHomeIcon" class="breadcrumb-home">
      <router-link to="/" class="home-link" :title="homeTitle">
        <i class="home-icon fas fa-home"></i>
        <span v-if="showHomeText" class="home-text">{{ homeText }}</span>
      </router-link>
      <span v-if="items.length > 0" class="separator">
        {{ separator }}
      </span>
    </div>

    <!-- 面包屑项 -->
    <ol class="breadcrumb-list">
      <li
        v-for="(item, index) in visibleItems"
        :key="item.path || item.id"
        class="breadcrumb-item"
      >
        <!-- 链接项 -->
        <template v-if="index < visibleItems.length - 1">
          <router-link
            v-if="item.path"
            :to="item.path"
            class="breadcrumb-link"
            :title="item.text"
          >
            <i v-if="item.icon" :class="item.icon" class="item-icon"></i>
            <span class="item-text">{{ item.text }}</span>
          </router-link>
          
          <a
            v-else-if="item.href"
            :href="item.href"
            class="breadcrumb-link"
            :title="item.text"
            :target="item.target"
          >
            <i v-if="item.icon" :class="item.icon" class="item-icon"></i>
            <span class="item-text">{{ item.text }}</span>
          </a>
          
          <span v-else class="breadcrumb-text">
            <i v-if="item.icon" :class="item.icon" class="item-icon"></i>
            <span class="item-text">{{ item.text }}</span>
          </span>
          
          <span class="separator">{{ separator }}</span>
        </template>

        <!-- 当前页项（最后一项） -->
        <template v-else>
          <span class="breadcrumb-current">
            <i v-if="item.icon" :class="item.icon" class="current-icon"></i>
            <span class="current-text">{{ item.text }}</span>
          </span>
        </template>
      </li>
    </ol>

    <!-- 折叠按钮（当项数超过限制时） -->
    <div
      v-if="showCollapse && items.length > maxVisibleItems"
      class="breadcrumb-collapse"
    >
      <button
        class="collapse-btn"
        @click="toggleCollapse"
        :aria-label="collapseLabel"
      >
        <i :class="collapseIcon" class="collapse-icon"></i>
        <span v-if="showCollapseText" class="collapse-text">
          {{ collapseText }}
        </span>
      </button>
      
      <!-- 折叠菜单 -->
      <transition name="slide-down">
        <div
          v-if="showCollapseMenu"
          class="collapse-menu"
          v-click-outside="closeCollapseMenu"
        >
          <div class="collapse-menu-header">
            <span class="menu-title">导航路径</span>
            <button
              class="menu-close"
              @click="closeCollapseMenu"
              aria-label="关闭菜单"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
          <ul class="collapse-menu-list">
            <li
              v-for="item in collapsedItems"
              :key="item.path || item.id"
              class="collapse-menu-item"
            >
              <router-link
                v-if="item.path"
                :to="item.path"
                class="collapse-menu-link"
                @click="closeCollapseMenu"
              >
                <i v-if="item.icon" :class="item.icon" class="menu-icon"></i>
                <span class="menu-text">{{ item.text }}</span>
              </router-link>
              
              <a
                v-else-if="item.href"
                :href="item.href"
                class="collapse-menu-link"
                :target="item.target"
                @click="closeCollapseMenu"
              >
                <i v-if="item.icon" :class="item.icon" class="menu-icon"></i>
                <span class="menu-text">{{ item.text }}</span>
              </a>
              
              <span v-else class="collapse-menu-text">
                <i v-if="item.icon" :class="item.icon" class="menu-icon"></i>
                <span class="menu-text">{{ item.text }}</span>
              </span>
            </li>
          </ul>
        </div>
      </transition>
    </div>

    <!-- 操作按钮 -->
    <div v-if="showActions && actions.length > 0" class="breadcrumb-actions">
      <div class="actions-container">
        <button
          v-for="action in actions"
          :key="action.id"
          class="action-btn"
          :class="action.class"
          @click="action.handler"
          :title="action.title"
          :disabled="action.disabled"
        >
          <i v-if="action.icon" :class="action.icon" class="action-icon"></i>
          <span v-if="action.text" class="action-text">{{ action.text }}</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBreakpoints } from '@/composables/useBreakpoints'
import type { BreadcrumbItem, BreadcrumbAction } from '@/types/navigation'

// Props
interface Props {
  items?: BreadcrumbItem[]
  separator?: string
  showHomeIcon?: boolean
  showHomeText?: boolean
  homeText?: string
  homeTitle?: string
  maxVisibleItems?: number
  showCollapse?: boolean
  collapseText?: string
  variant?: 'default' | 'light' | 'dark' | 'transparent'
  size?: 'sm' | 'md' | 'lg'
  truncate?: boolean
  showActions?: boolean
  actions?: BreadcrumbAction[]
}

const props = withDefaults(defineProps<Props>(), {
  items: undefined,
  separator: '/',
  showHomeIcon: true,
  showHomeText: false,
  homeText: '首页',
  homeTitle: '返回首页',
  maxVisibleItems: 4,
  showCollapse: true,
  collapseText: '...',
  variant: 'default',
  size: 'md',
  truncate: true,
  showActions: false,
  actions: () => []
})

// Emits
const emit = defineEmits<{
  'item-click': [item: BreadcrumbItem]
  'action-click': [action: BreadcrumbAction]
  'collapse-toggle': [collapsed: boolean]
}>()

// Router
const route = useRoute()
const router = useRouter()

// Composables
const { isMobile } = useBreakpoints()

// State
const showCollapseMenu = ref(false)
const isCollapsed = ref(false)

// Computed
const breadcrumbClasses = computed(() => ({
  [`breadcrumb-${props.variant}`]: true,
  [`breadcrumb-${props.size}`]: true,
  'breadcrumb-truncate': props.truncate,
  'breadcrumb-mobile': isMobile.value
}))

const collapseLabel = computed(() => {
  return isCollapsed.value ? '展开面包屑' : '折叠面包屑'
})

const collapseIcon = computed(() => {
  return isCollapsed.value ? 'fas fa-ellipsis-h' : 'fas fa-ellipsis-v'
})

const collapseText = computed(() => {
  return isCollapsed.value ? '展开' : props.collapseText
})

const defaultItems = computed<BreadcrumbItem[]>(() => {
  // 根据当前路由自动生成面包屑
  const pathArray = route.path.split('/').filter(Boolean)
  const items: BreadcrumbItem[] = []
  
  let currentPath = ''
  pathArray.forEach((segment, index) => {
    currentPath += `/${segment}`
    items.push({
      path: currentPath,
      text: formatSegment(segment),
      icon: getSegmentIcon(segment, index, pathArray.length)
    })
  })
  
  return items
})

const breadcrumbItems = computed(() => {
  return props.items && props.items.length > 0 ? props.items : defaultItems.value
})

const visibleItems = computed(() => {
  if (!isCollapsed.value || breadcrumbItems.value.length <= props.maxVisibleItems) {
    return breadcrumbItems.value
  }
  
  // 显示首尾项，中间项折叠
  const startCount = Math.floor((props.maxVisibleItems - 1) / 2)
  const endCount = props.maxVisibleItems - startCount - 1
  
  const startItems = breadcrumbItems.value.slice(0, startCount)
  const endItems = breadcrumbItems.value.slice(-endCount)
  
  return [...startItems, ...endItems]
})

const collapsedItems = computed(() => {
  if (!isCollapsed.value) return []
  
  const startCount = Math.floor((props.maxVisibleItems - 1) / 2)
  const endCount = props.maxVisibleItems - startCount - 1
  
  return breadcrumbItems.value.slice(startCount, breadcrumbItems.value.length - endCount)
})

const showCollapseText = computed(() => {
  return !isMobile.value || props.size !== 'sm'
})

// Methods
const formatSegment = (segment: string): string => {
  // 将URL路径段转换为友好的文本
  return segment
    .replace(/-/g, ' ')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

const getSegmentIcon = (segment: string, index: number, total: number): string => {
  // 根据路径段返回对应的图标
  const icons: Record<string, string> = {
    'admin': 'fas fa-cog',
    'user': 'fas fa-user',
    'settings': 'fas fa-cog',
    'profile': 'fas fa-user-circle',
    'matches': 'fas fa-futbol',
    'intelligence': 'fas fa-chart-line',
    'analysis': 'fas fa-chart-bar',
    'favorites': 'fas fa-heart',
    'history': 'fas fa-history',
    'search': 'fas fa-search'
  }
  
  if (icons[segment]) {
    return icons[segment]
  }
  
  // 默认图标
  return index === total - 1 ? 'fas fa-file-alt' : 'fas fa-folder'
}

const toggleCollapse = () => {
  if (breadcrumbItems.value.length <= props.maxVisibleItems) {
    return
  }
  
  if (isMobile.value && props.showCollapse) {
    showCollapseMenu.value = !showCollapseMenu.value
  } else {
    isCollapsed.value = !isCollapsed.value
    emit('collapse-toggle', isCollapsed.value)
  }
}

const closeCollapseMenu = () => {
  showCollapseMenu.value = false
}

const handleItemClick = (item: BreadcrumbItem) => {
  emit('item-click', item)
}

const handleActionClick = (action: BreadcrumbAction) => {
  emit('action-click', action)
  if (action.handler) {
    action.handler()
  }
}

const handleClickOutside = (event: MouseEvent) => {
  const collapseMenu = document.querySelector('.collapse-menu')
  const collapseBtn = document.querySelector('.collapse-btn')
  
  if (collapseMenu && 
      !collapseMenu.contains(event.target as Node) &&
      !collapseBtn?.contains(event.target as Node)) {
    closeCollapseMenu()
  }
}

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && showCollapseMenu.value) {
    closeCollapseMenu()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscapeKey)
})

// Watch
watch(isMobile, (newVal) => {
  if (newVal) {
    // 在移动端默认折叠
    isCollapsed.value = true
  }
})

watch(showCollapseMenu, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) 0;
  font-size: 0.95rem;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.breadcrumb-light {
  background-color: var(--bg-secondary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.breadcrumb-dark {
  background-color: var(--bg-inverse);
  color: var(--text-inverse);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.breadcrumb-transparent {
  background-color: transparent;
}

.breadcrumb-sm {
  font-size: 0.875rem;
  padding: var(--spacing-sm) 0;
}

.breadcrumb-md {
  font-size: 0.95rem;
  padding: var(--spacing-md) 0;
}

.breadcrumb-lg {
  font-size: 1rem;
  padding: var(--spacing-lg) 0;
}

.breadcrumb-truncate .item-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.breadcrumb-mobile.breadcrumb-truncate .item-text {
  max-width: 80px;
}

.breadcrumb-home {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.home-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.home-link:hover {
  color: var(--primary);
}

.home-icon {
  font-size: 1rem;
}

.home-text {
  font-size: 0.95rem;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: var(--spacing-sm);
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.breadcrumb-link,
.breadcrumb-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
  white-space: nowrap;
}

.breadcrumb-link:hover {
  color: var(--primary);
}

.breadcrumb-current {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-primary);
  font-weight: 500;
  white-space: nowrap;
}

.item-icon,
.current-icon {
  font-size: 0.875rem;
  flex-shrink: 0;
}

.item-text,
.current-text {
  line-height: 1.4;
}

.separator {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  user-select: none;
  flex-shrink: 0;
}

.breadcrumb-collapse {
  position: relative;
}

.collapse-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  transition: all 0.2s ease;
  font-size: 0.875rem;
}

.collapse-btn:hover {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

.collapse-icon {
  font-size: 0.875rem;
}

.collapse-text {
  font-size: 0.875rem;
}

.collapse-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  z-index: 1000;
  overflow: hidden;
}

.collapse-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.menu-title {
  font-size: 0.875rem;
}

.menu-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  font-size: 1rem;
  line-height: 1;
}

.collapse-menu-list {
  list-style: none;
  padding: var(--spacing-sm) 0;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.collapse-menu-item {
  margin: 1px 0;
}

.collapse-menu-link,
.collapse-menu-text {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--text-primary);
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.collapse-menu-link:hover {
  background-color: var(--bg-secondary);
}

.menu-icon {
  width: 16px;
  font-size: 0.875rem;
  text-align: center;
  flex-shrink: 0;
}

.menu-text {
  flex: 1;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.breadcrumb-actions {
  margin-left: auto;
}

.actions-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-btn:hover:not(:disabled) {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background-color: var(--primary);
  color: white;
  border-color: var(--primary);
}

.action-btn.primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.action-icon {
  font-size: 0.875rem;
}

.action-text {
  font-size: 0.875rem;
}

/* 过渡动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .breadcrumb {
    gap: var(--spacing-xs);
  }
  
  .breadcrumb-list {
    gap: var(--spacing-xs);
  }
  
  .breadcrumb-item {
    gap: var(--spacing-xs);
  }
  
  .breadcrumb-truncate .item-text {
    max-width: 80px;
  }
  
  .show-home-text {
    display: none;
  }
  
  .breadcrumb-actions {
    display: none;
  }
  
  .collapse-menu {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 300px;
    max-height: 80vh;
  }
}

@media (max-width: 480px) {
  .breadcrumb-truncate .item-text {
    max-width: 60px;
  }
  
  .separator {
    margin: 0 2px;
  }
  
  .action-btn .action-text {
    display: none;
  }
  
  .action-btn {
    padding: 6px;
  }
}

/* 打印样式 */
@media print {
  .breadcrumb-collapse,
  .breadcrumb-actions {
    display: none;
  }
  
  .breadcrumb-list {
    flex-wrap: nowrap;
  }
}
</style>