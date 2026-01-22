<template>
  <div :class="spinnerClasses" :style="spinnerStyles" role="status" aria-label="加载中">
    <div class="loading-spinner__ring"></div>
    <span v-if="text" class="loading-spinner__text">{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large', 'x-large', 'icon'].includes(value)
  },
  color: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'warning', 'danger', 'white', 'current'].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  fullscreen: {
    type: Boolean,
    default: false
  },
  global: {
    type: Boolean,
    default: false
  },
  overlay: {
    type: Boolean,
    default: false
  },
  inline: {
    type: Boolean,
    default: false
  }
})

// 计算加载动画类名
const spinnerClasses = computed(() => ({
  'loading-spinner': true,
  [`loading-spinner--${props.size}`]: true,
  [`loading-spinner--${props.color}`]: true,
  'loading-spinner--fullscreen': props.fullscreen,
  'loading-spinner--global': props.global,
  'loading-spinner--overlay': props.overlay,
  'loading-spinner--inline': props.inline,
  'loading-spinner--with-text': props.text
}))

// 计算样式
const spinnerStyles = computed(() => {
  const styles = {}
  
  // 如果是全局加载，设置z-index
  if (props.global) {
    styles.zIndex = '9999'
  }
  
  return styles
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 尺寸变体 */
.loading-spinner--small {
  --spinner-size: 20px;
  --spinner-thickness: 2px;
  font-size: var(--font-size-xs);
}

.loading-spinner--medium {
  --spinner-size: 32px;
  --spinner-thickness: 3px;
  font-size: var(--font-size-sm);
}

.loading-spinner--large {
  --spinner-size: 48px;
  --spinner-thickness: 4px;
  font-size: var(--font-size-base);
}

.loading-spinner--x-large {
  --spinner-size: 64px;
  --spinner-thickness: 5px;
  font-size: var(--font-size-lg);
}

.loading-spinner--icon {
  --spinner-size: 20px;
  --spinner-thickness: 2px;
}

/* 颜色变体 */
.loading-spinner--primary {
  --spinner-color: var(--color-primary);
}

.loading-spinner--secondary {
  --spinner-color: var(--color-secondary);
}

.loading-spinner--success {
  --spinner-color: var(--color-success);
}

.loading-spinner--warning {
  --spinner-color: var(--color-warning);
}

.loading-spinner--danger {
  --spinner-color: var(--color-danger);
}

.loading-spinner--white {
  --spinner-color: white;
}

.loading-spinner--current {
  --spinner-color: currentColor;
}

/* 布局变体 */
.loading-spinner--fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.loading-spinner--global {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
}

.loading-spinner--overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.loading-spinner--inline {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
}

.loading-spinner--with-text {
  flex-direction: column;
  gap: var(--spacing-3);
}

/* 旋转圆环 */
.loading-spinner__ring {
  width: var(--spinner-size);
  height: var(--spinner-size);
  border: var(--spinner-thickness) solid rgba(var(--spinner-color-rgb, var(--color-primary-rgb)), 0.2);
  border-top-color: var(--spinner-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-sizing: border-box;
}

/* 文本 */
.loading-spinner__text {
  color: var(--color-text-secondary);
  font-weight: 500;
  text-align: center;
}

/* 动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 呼吸动画变体 */
.loading-spinner--pulse .loading-spinner__ring {
  animation: pulse 1.5s ease-in-out infinite;
  border-width: calc(var(--spinner-thickness) * 1.5);
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

/* 波浪动画变体 */
.loading-spinner--wave {
  display: flex;
  align-items: center;
  gap: calc(var(--spinner-size) / 6);
}

.loading-spinner--wave .loading-spinner__ring {
  width: calc(var(--spinner-size) / 3);
  height: calc(var(--spinner-size) / 3);
  border-radius: 50%;
  background-color: var(--spinner-color);
  animation: wave 1.4s ease-in-out infinite;
}

.loading-spinner--wave .loading-spinner__ring:nth-child(2) {
  animation-delay: -1.1s;
}

.loading-spinner--wave .loading-spinner__ring:nth-child(3) {
  animation-delay: -0.9s;
}

@keyframes wave {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 1;
  }
  30% {
    transform: translateY(-100%);
    opacity: 0.5;
  }
}
</style>