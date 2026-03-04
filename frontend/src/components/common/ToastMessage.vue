<template>
  <teleport to="#toast-container">
    <transition-group name="toast-list" tag="div" class="toast-message__container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast-message', `toast-message--${toast.type}`]"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        @mouseenter="pauseToast(toast.id)"
        @mouseleave="resumeToast(toast.id)"
      >
        <!-- 图标 -->
        <div class="toast-message__icon">
          <component :is="getToastIcon(toast.type)" :size="20" />
        </div>

        <!-- 内容 -->
        <div class="toast-message__content">
          <div v-if="toast.title" class="toast-message__title">{{ toast.title }}</div>
          <div class="toast-message__message">{{ toast.message }}</div>
        </div>

        <!-- 关闭按钮 -->
        <button
          v-if="toast.closable"
          type="button"
          class="toast-message__close"
          @click="removeToast(toast.id)"
          aria-label="关闭通知"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 进度条 -->
        <div v-if="toast.showProgress && toast.duration" class="toast-message__progress">
          <div
            class="toast-message__progress-bar"
            :style="{
              animationDuration: `${toast.duration}ms`,
              animationPlayState: toast.paused ? 'paused' : 'running'
            }"
          ></div>
        </div>
      </div>
    </transition-group>
  </teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 导入图标组件（实际项目中应该导入真实的图标）
const ToastIcons = {
  info: { template: '<div class="toast-icon-info">ℹ️</div>' },
  success: { template: '<div class="toast-icon-success">✅</div>' },
  warning: { template: '<div class="toast-icon-warning">⚠️</div>' },
  error: { template: '<div class="toast-icon-error">❌</div>' }
}

// Toast 状态管理
const toasts = ref([])
let toastId = 0
const timers = new Map()

// 默认配置
const defaultConfig = {
  type: 'info',
  duration: 5000,
  closable: true,
  showProgress: true,
  position: 'top-right'
}

// 获取 Toast 图标
const getToastIcon = (type) => {
  return ToastIcons[type] || ToastIcons.info
}

// 添加 Toast
const addToast = (config) => {
  const id = ++toastId
  const toastConfig = {
    ...defaultConfig,
    ...config,
    id,
    createdAt: Date.now(),
    paused: false,
    remainingTime: config.duration || defaultConfig.duration
  }

  toasts.value.push(toastConfig)

  // 设置自动关闭定时器
  if (toastConfig.duration > 0) {
    const timer = setTimeout(() => {
      removeToast(id)
    }, toastConfig.duration)
    
    timers.set(id, timer)
  }

  // 限制最大数量
  const maxToasts = config.maxToasts || 5
  if (toasts.value.length > maxToasts) {
    removeToast(toasts.value[0].id)
  }

  return id
}

// 移除 Toast
const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
    
    // 清除定时器
    const timer = timers.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.delete(id)
    }
  }
}

// 暂停 Toast
const pauseToast = (id) => {
  const toast = toasts.value.find(t => t.id === id)
  if (toast && toast.duration > 0) {
    const timer = timers.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.delete(id)
      
      // 计算剩余时间
      const elapsed = Date.now() - toast.createdAt
      toast.remainingTime = toast.duration - elapsed
      toast.paused = true
    }
  }
}

// 恢复 Toast
const resumeToast = (id) => {
  const toast = toasts.value.find(t => t.id === id)
  if (toast && toast.remainingTime > 0) {
    toast.createdAt = Date.now() - (toast.duration - toast.remainingTime)
    toast.paused = false
    
    const timer = setTimeout(() => {
      removeToast(id)
    }, toast.remainingTime)
    
    timers.set(id, timer)
  }
}

// 清空所有 Toast
const clearAllToasts = () => {
  toasts.value.forEach(toast => {
    const timer = timers.get(toast.id)
    if (timer) {
      clearTimeout(timer)
    }
  })
  
  timers.clear()
  toasts.value = []
}

// 创建快捷方法
const toast = {
  info: (message, title = '', config = {}) => 
    addToast({ ...config, type: 'info', message, title }),
  
  success: (message, title = '', config = {}) => 
    addToast({ ...config, type: 'success', message, title }),
  
  warning: (message, title = '', config = {}) => 
    addToast({ ...config, type: 'warning', message, title }),
  
  error: (message, title = '', config = {}) => 
    addToast({ ...config, type: 'error', message, title }),
  
  remove: removeToast,
  clearAll: clearAllToasts
}

// 确保容器存在
const ensureContainer = () => {
  let container = document.getElementById('toast-container')
  if (!container) {
    container = document.createElement('div')
    container.id = 'toast-container'
    container.className = 'toast-container'
    document.body.appendChild(container)
  }
  return container
}

// 生命周期
onMounted(() => {
  ensureContainer()
})

onUnmounted(() => {
  clearAllToasts()
  const container = document.getElementById('toast-container')
  if (container) {
    container.remove()
  }
})

// 暴露 API
defineExpose({
  toast,
  addToast,
  removeToast,
  clearAllToasts
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  z-index: var(--z-index-toast, 9999);
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  width: 100%;
  max-width: 400px;
  max-height: 100vh;
  overflow-y: auto;
  padding: var(--spacing-4);
  box-sizing: border-box;
}

.toast-container[data-position="top-right"] {
  top: 0;
  right: 0;
  align-items: flex-end;
}

.toast-container[data-position="top-left"] {
  top: 0;
  left: 0;
  align-items: flex-start;
}

.toast-container[data-position="top-center"] {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  align-items: center;
}

.toast-container[data-position="bottom-right"] {
  bottom: 0;
  right: 0;
  align-items: flex-end;
}

.toast-container[data-position="bottom-left"] {
  bottom: 0;
  left: 0;
  align-items: flex-start;
}

.toast-container[data-position="bottom-center"] {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  align-items: center;
}

.toast-message {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  pointer-events: auto;
  max-width: 400px;
  animation: toast-in 0.3s ease-out;
  border-left: 4px solid transparent;
}

.toast-message--info {
  border-left-color: var(--color-info);
  background-color: var(--color-bg-info);
}

.toast-message--success {
  border-left-color: var(--color-success);
  background-color: var(--color-bg-success);
}

.toast-message--warning {
  border-left-color: var(--color-warning);
  background-color: var(--color-bg-warning);
}

.toast-message--error {
  border-left-color: var(--color-danger);
  background-color: var(--color-bg-danger);
}

.toast-message__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

.toast-message--info .toast-message__icon {
  color: var(--color-info);
}

.toast-message--success .toast-message__icon {
  color: var(--color-success);
}

.toast-message--warning .toast-message__icon {
  color: var(--color-warning);
}

.toast-message--error .toast-message__icon {
  color: var(--color-danger);
}

.toast-message__content {
  flex: 1;
  min-width: 0;
}

.toast-message__title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-1);
  line-height: 1.4;
}

.toast-message__message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.toast-message__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.toast-message__close:hover {
  opacity: 1;
}

.toast-message__progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  overflow: hidden;
}

.toast-message__progress-bar {
  height: 100%;
  background-color: currentColor;
  opacity: 0.7;
  animation: progress linear forwards;
  transform-origin: left;
}

.toast-message--info .toast-message__progress-bar {
  background-color: var(--color-info);
}

.toast-message--success .toast-message__progress-bar {
  background-color: var(--color-success);
}

.toast-message--warning .toast-message__progress-bar {
  background-color: var(--color-warning);
}

.toast-message--error .toast-message__progress-bar {
  background-color: var(--color-danger);
}

/* 动画 */
@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}

.toast-list-enter-from,
.toast-list-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.toast-list-leave-active {
  position: absolute;
}

/* 响应式 */
@media (max-width: 640px) {
  .toast-container {
    max-width: 100%;
    padding: var(--spacing-2);
  }
  
  .toast-message {
    max-width: 100%;
    width: 100%;
  }
}
</style>

<style>
/* 全局样式 */
.toast-container {
  font-family: var(--font-family-base);
}

/* 如果需要全局使用，可以在 main.js 中注册 */
</style>