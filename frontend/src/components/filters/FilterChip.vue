<template>
  <span :class="chipClasses" :title="chipTitle">
    <!-- 图标 -->
    <span v-if="icon" class="filter-chip__icon">
      <component :is="icon" :size="16" />
    </span>
    
    <!-- 标签文本 -->
    <span class="filter-chip__label">{{ label }}</span>
    
    <!-- 值（如果有） -->
    <span v-if="value" class="filter-chip__value">{{ formatValue(value) }}</span>
    
    <!-- 计数（如果有） -->
    <span v-if="showCount && count !== undefined" class="filter-chip__count">
      {{ count }}
    </span>
    
    <!-- 关闭按钮 -->
    <button
      v-if="removable"
      class="filter-chip__remove"
      @click="handleRemove"
      aria-label="移除筛选"
    >
      <svg width="12" height="12" viewBox="0 0 24 24">
        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>
    </button>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  filter: {
    type: Object,
    default: () => ({
      id: '',
      label: '',
      value: null,
      type: 'default',
      group: ''
    })
  },
  label: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number, Array, Object],
    default: null
  },
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'secondary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  icon: {
    type: Object,
    default: null
  },
  removable: {
    type: Boolean,
    default: true
  },
  clickable: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'outlined', 'filled', 'dashed'].includes(value)
  },
  showCount: {
    type: Boolean,
    default: false
  },
  count: {
    type: Number,
    default: undefined
  },
  maxWidth: {
    type: String,
    default: '200px'
  }
})

const emit = defineEmits(['remove', 'click'])

// 计算属性
const chipClasses = computed(() => ({
  'filter-chip': true,
  [`filter-chip--${props.size}`]: true,
  [`filter-chip--${props.variant}`]: true,
  [`filter-chip--${props.type}`]: true,
  'filter-chip--removable': props.removable,
  'filter-chip--clickable': props.clickable,
  'filter-chip--disabled': props.disabled,
  'filter-chip--has-value': props.value !== null && props.value !== undefined && props.value !== ''
}))

const chipTitle = computed(() => {
  let title = props.label
  if (props.value) {
    title += `: ${formatValue(props.value, true)}`
  }
  if (props.filter?.description) {
    title += `\n${props.filter.description}`
  }
  return title
})

// 方法
const formatValue = (value, full = false) => {
  if (value === null || value === undefined) return ''
  
  if (Array.isArray(value)) {
    if (full || value.length <= 3) {
      return value.join(', ')
    } else {
      return `${value.length} 个选项`
    }
  }
  
  if (typeof value === 'object') {
    if (value.min !== undefined && value.max !== undefined) {
      return `${value.min} - ${value.max}`
    }
    if (value.start && value.end) {
      return `${value.start} 至 ${value.end}`
    }
    return JSON.stringify(value)
  }
  
  return String(value)
}

const handleRemove = () => {
  if (!props.disabled && props.removable) {
    emit('remove', props.filter)
  }
}

const handleClick = () => {
  if (!props.disabled && props.clickable) {
    emit('click', props.filter)
  }
}
</script>

<style scoped>
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all 0.2s ease;
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: v-bind(maxWidth);
}

/* 尺寸 */
.filter-chip--small {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
  gap: var(--spacing-1);
}

.filter-chip--medium {
  padding: 4px 12px;
  font-size: var(--font-size-sm);
  gap: var(--spacing-2);
}

.filter-chip--large {
  padding: 6px 16px;
  font-size: var(--font-size-base);
  gap: var(--spacing-3);
}

/* 变体 */
.filter-chip--default {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.filter-chip--outlined {
  background-color: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.filter-chip--filled {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.filter-chip--dashed {
  background-color: transparent;
  color: var(--color-text-primary);
  border: 1px dashed var(--color-border);
}

/* 类型 */
.filter-chip--primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.filter-chip--outlined.filter-chip--primary {
  background-color: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.filter-chip--secondary {
  background-color: var(--color-secondary-light);
  color: var(--color-secondary-dark);
}

.filter-chip--outlined.filter-chip--secondary {
  background-color: transparent;
  color: var(--color-secondary);
  border-color: var(--color-secondary);
}

.filter-chip--success {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.filter-chip--outlined.filter-chip--success {
  background-color: transparent;
  color: var(--color-success);
  border-color: var(--color-success);
}

.filter-chip--warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.filter-chip--outlined.filter-chip--warning {
  background-color: transparent;
  color: var(--color-warning);
  border-color: var(--color-warning);
}

.filter-chip--danger {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
}

.filter-chip--outlined.filter-chip--danger {
  background-color: transparent;
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.filter-chip--info {
  background-color: var(--color-info-light);
  color: var(--color-info-dark);
}

.filter-chip--outlined.filter-chip--info {
  background-color: transparent;
  color: var(--color-info);
  border-color: var(--color-info);
}

/* 状态 */
.filter-chip--clickable {
  cursor: pointer;
}

.filter-chip--clickable:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.filter-chip--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-chip--disabled:hover {
  transform: none;
  box-shadow: none;
}

.filter-chip__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.filter-chip__label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 1;
  min-width: 0;
}

.filter-chip__value {
  font-weight: 600;
  margin-left: 2px;
  flex-shrink: 0;
}

.filter-chip__count {
  font-size: var(--font-size-xs);
  background-color: rgba(0, 0, 0, 0.1);
  padding: 1px 6px;
  border-radius: var(--radius-full);
  margin-left: var(--spacing-1);
  flex-shrink: 0;
}

.filter-chip--outlined .filter-chip__count {
  background-color: transparent;
  border: 1px solid currentColor;
}

.filter-chip__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: transparent;
  border: none;
  border-radius: 50%;
  color: inherit;
  opacity: 0.7;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
  margin-left: var(--spacing-1);
}

.filter-chip__remove:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.1);
}

.filter-chip--outlined .filter-chip__remove:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.filter-chip--disabled .filter-chip__remove {
  cursor: not-allowed;
}

/* 动画 */
@keyframes chip-in {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.filter-chip {
  animation: chip-in 0.2s ease;
}
</style>