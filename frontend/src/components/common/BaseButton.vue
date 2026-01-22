<template>
  <button
    :class="[
      'base-button',
      `base-button--${variant}`,
      `base-button--${size}`,
      {
        'base-button--block': block,
        'base-button--loading': loading,
        'base-button--disabled': disabled,
        'base-button--outline': outline,
        'base-button--rounded': rounded
      }
    ]"
    :type="type"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- 加载状态 -->
    <span v-if="loading" class="base-button__loading">
      <i class="base-button__loading-icon"></i>
      <span v-if="loadingText">{{ loadingText }}</span>
    </span>
    
    <!-- 按钮图标 -->
    <span v-if="icon && !loading" class="base-button__icon">
      <i :class="icon"></i>
    </span>
    
    <!-- 按钮文本 -->
    <span class="base-button__content">
      <slot>{{ label }}</slot>
    </span>
    
    <!-- 按钮尾部图标 -->
    <span v-if="trailingIcon && !loading" class="base-button__trailing-icon">
      <i :class="trailingIcon"></i>
    </span>
  </button>
</template>

<script setup>
import { defineEmits } from 'vue'

// 组件属性
const props = defineProps({
  // 基本属性
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'button', // 'button', 'submit', 'reset'
    validator: (value) => ['button', 'submit', 'reset'].includes(value)
  },
  
  // 样式变体
  variant: {
    type: String,
    default: 'primary', // 'primary', 'secondary', 'success', 'warning', 'danger', 'info', 'ghost', 'link'
    validator: (value) => ['primary', 'secondary', 'success', 'warning', 'danger', 'info', 'ghost', 'link'].includes(value)
  },
  
  // 大小
  size: {
    type: String,
    default: 'medium', // 'small', 'medium', 'large'
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  
  // 图标
  icon: {
    type: String,
    default: ''
  },
  trailingIcon: {
    type: String,
    default: ''
  },
  
  // 状态
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  
  // 样式控制
  block: {
    type: Boolean,
    default: false
  },
  outline: {
    type: Boolean,
    default: false
  },
  rounded: {
    type: Boolean,
    default: false
  }
})

// 事件
const emit = defineEmits(['click'])

// 方法
const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: var(--font-medium);
  transition: all var(--transition-fast);
  user-select: none;
  white-space: nowrap;
  vertical-align: middle;
  border: 1px solid transparent;
  cursor: pointer;
}

.base-button:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 尺寸 */
.base-button--small {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  border-radius: var(--radius-sm);
}

.base-button--medium {
  padding: 0.5rem 1rem;
  font-size: var(--text-base);
  border-radius: var(--radius);
}

.base-button--large {
  padding: 0.75rem 1.5rem;
  font-size: var(--text-lg);
  border-radius: var(--radius-md);
}

/* 块级按钮 */
.base-button--block {
  display: flex;
  width: 100%;
}

/* 圆角按钮 */
.base-button--rounded {
  border-radius: var(--radius-full);
}

/* 加载状态 */
.base-button__loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.base-button__loading-icon {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 图标 */
.base-button__icon,
.base-button__trailing-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 内容 */
.base-button__content {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 变体样式 - 实心按钮 */
.base-button--primary {
  background-color: var(--primary);
  color: var(--white);
}

.base-button--primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.base-button--secondary {
  background-color: var(--secondary);
  color: var(--white);
}

.base-button--secondary:hover:not(:disabled) {
  background-color: var(--secondary-dark);
}

.base-button--success {
  background-color: var(--success);
  color: var(--white);
}

.base-button--success:hover:not(:disabled) {
  background-color: var(--success-dark);
}

.base-button--warning {
  background-color: var(--warning);
  color: var(--gray-900);
}

.base-button--warning:hover:not(:disabled) {
  background-color: var(--warning-dark);
}

.base-button--danger {
  background-color: var(--danger);
  color: var(--white);
}

.base-button--danger:hover:not(:disabled) {
  background-color: var(--danger-dark);
}

.base-button--info {
  background-color: var(--info);
  color: var(--white);
}

.base-button--info:hover:not(:disabled) {
  background-color: var(--info-dark);
}

/* 变体样式 - 描边按钮 */
.base-button--primary.base-button--outline {
  background-color: transparent;
  color: var(--primary);
  border-color: var(--primary);
}

.base-button--primary.base-button--outline:hover:not(:disabled) {
  background-color: var(--primary);
  color: var(--white);
}

.base-button--secondary.base-button--outline {
  background-color: transparent;
  color: var(--secondary);
  border-color: var(--secondary);
}

.base-button--secondary.base-button--outline:hover:not(:disabled) {
  background-color: var(--secondary);
  color: var(--white);
}

.base-button--success.base-button--outline {
  background-color: transparent;
  color: var(--success);
  border-color: var(--success);
}

.base-button--success.base-button--outline:hover:not(:disabled) {
  background-color: var(--success);
  color: var(--white);
}

.base-button--warning.base-button--outline {
  background-color: transparent;
  color: var(--warning);
  border-color: var(--warning);
}

.base-button--warning.base-button--outline:hover:not(:disabled) {
  background-color: var(--warning);
  color: var(--gray-900);
}

.base-button--danger.base-button--outline {
  background-color: transparent;
  color: var(--danger);
  border-color: var(--danger);
}

.base-button--danger.base-button--outline:hover:not(:disabled) {
  background-color: var(--danger);
  color: var(--white);
}

.base-button--info.base-button--outline {
  background-color: transparent;
  color: var(--info);
  border-color: var(--info);
}

.base-button--info.base-button--outline:hover:not(:disabled) {
  background-color: var(--info);
  color: var(--white);
}

/* 幽灵按钮 */
.base-button--ghost {
  background-color: transparent;
  color: var(--text-primary);
}

.base-button--ghost:hover:not(:disabled) {
  background-color: var(--gray-200);
}

[data-theme="dark"] .base-button--ghost:hover:not(:disabled) {
  background-color: var(--gray-700);
}

/* 链接按钮 */
.base-button--link {
  background-color: transparent;
  color: var(--primary);
  padding: 0;
  border: none;
  text-decoration: underline;
}

.base-button--link:hover:not(:disabled) {
  color: var(--primary-dark);
  text-decoration: none;
}

/* 响应式 */
@media (max-width: 768px) {
  .base-button--large {
    padding: 0.625rem 1.25rem;
    font-size: var(--text-base);
  }
}
</style>