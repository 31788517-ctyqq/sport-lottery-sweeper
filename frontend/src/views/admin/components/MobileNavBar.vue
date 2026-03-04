<template>
  <nav class="mobile-nav-bar" :class="{ 'has-safe-area': hasSafeArea }">
    <div class="nav-items">
      <button
        v-for="item in navItems"
        :key="item.id"
        class="nav-item"
        :class="{ active: activeTab === item.id }"
        @click="handleItemClick(item)"
        :aria-label="item.label"
      >
        <div class="nav-icon">
          <i :class="item.icon"></i>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </div>
        <span class="nav-label">{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'filter'
  },
  // 是否显示徽章
  showBadges: {
    type: Boolean,
    default: true
  },
  // 自定义导航项
  customItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['tab-change'])

// 导航项配置
const defaultNavItems = [
  {
    id: 'filter',
    label: '筛选',
    icon: 'el-icon-filter',
    route: '/m/beidan-filter',
    badge: null
  },
  {
    id: 'results',
    label: '结果',
    icon: 'el-icon-tickets',
    route: '/m/beidan-filter/results',
    badge: null
  },
  {
    id: 'stats',
    label: '统计',
    icon: 'el-icon-data-analysis',
    route: '/m/beidan-filter/stats',
    badge: null
  },
  {
    id: 'strategies',
    label: '策略',
    icon: 'el-icon-setting',
    route: '/m/beidan-filter/strategies',
    badge: null
  },
  {
    id: 'export',
    label: '导出',
    icon: 'el-icon-download',
    route: '/m/beidan-filter/export',
    badge: null
  }
]

// 合并自定义导航项
const navItems = computed(() => {
  if (props.customItems.length > 0) {
    return props.customItems
  }
  return defaultNavItems
})

// 安全区域检测
const hasSafeArea = ref(false)

// 方法
const handleItemClick = (item) => {
  if (item.id !== props.activeTab) {
    emit('tab-change', item.id)
  }
}

// 更新徽章
const updateBadge = (tabId, count) => {
  const item = navItems.value.find(item => item.id === tabId)
  if (item) {
    if (count > 0 && props.showBadges) {
      item.badge = count > 99 ? '99+' : count.toString()
    } else {
      item.badge = null
    }
  }
}

// 检测安全区域
const checkSafeArea = () => {
  hasSafeArea.value = CSS.supports('padding-bottom: env(safe-area-inset-bottom)')
}

// 生命周期
onMounted(() => {
  checkSafeArea()
})

// 暴露方法给父组件
defineExpose({
  updateBadge
})
</script>

<style scoped>
.mobile-nav-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: var(--z-fixed);
  background-color: var(--bg-card);
  border-top: 1px solid var(--border-color);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.mobile-nav-bar.has-safe-area {
  padding-bottom: env(safe-area-inset-bottom);
}

.nav-items {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 72px;
  max-height: 72px;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  min-height: 72px;
  border: none;
  background: transparent;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transition: all 0.2s ease;
  position: relative;
  padding: 8px 4px;
  border-radius: var(--radius-md);
}

.nav-item:hover {
  background-color: var(--bg-secondary);
}

.nav-item:active {
  background-color: var(--border-color);
  transform: scale(0.95);
}

.nav-item.active {
  color: var(--primary);
}

.nav-item.active .nav-icon {
  color: var(--primary);
}

.nav-item.active .nav-label {
  color: var(--primary);
  font-weight: var(--font-weight-medium);
}

.nav-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-bottom: 4px;
  font-size: 20px;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.nav-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: var(--danger);
  color: var(--white);
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  border: 2px solid var(--bg-card);
}

.nav-label {
  font-size: 12px;
  color: var(--text-secondary);
  transition: color 0.2s ease;
  line-height: 1.2;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .nav-items {
    height: 68px;
    padding: 0 4px;
  }
  
  .nav-item {
    min-height: 68px;
    padding: 6px 2px;
  }
  
  .nav-icon {
    width: 24px;
    height: 24px;
    font-size: 18px;
    margin-bottom: 3px;
  }
  
  .nav-label {
    font-size: 11px;
  }
}

@media (max-width: 375px) {
  .nav-items {
    height: 64px;
  }
  
  .nav-item {
    min-height: 64px;
  }
  
  .nav-icon {
    width: 22px;
    height: 22px;
    font-size: 16px;
    margin-bottom: 2px;
  }
  
  .nav-label {
    font-size: 10px;
  }
}

/* 触摸优化 */
@media (hover: none) and (pointer: coarse) {
  .nav-item:hover {
    background-color: transparent;
  }
  
  .nav-item:active {
    background-color: var(--border-color);
  }
  
  .nav-item {
    min-height: 72px;
    min-width: 64px;
  }
}

/* 深色主题适配 */
[data-theme="dark"] .mobile-nav-bar {
  background-color: var(--bg-card);
  border-top-color: var(--border-dark);
}

[data-theme="dark"] .nav-item:hover {
  background-color: var(--bg-secondary);
}

[data-theme="dark"] .nav-item:active {
  background-color: var(--border-dark);
}

/* 高对比度主题适配 */
[data-theme="high-contrast"] .mobile-nav-bar {
  border-top: 2px solid var(--border-dark);
}

[data-theme="high-contrast"] .nav-item.active {
  outline: 2px solid var(--primary);
  outline-offset: -2px;
}
</style>