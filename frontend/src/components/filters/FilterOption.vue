<template>
  <div :class="optionClasses" @click="handleClick">
    <!-- 选项左侧 -->
    <div class="filter-option__left">
      <!-- 选择器 -->
      <div class="filter-option__selector" @click.stop="handleSelectorClick">
        <!-- 复选框 -->
        <div v-if="type === 'checkbox'" class="filter-option__checkbox">
          <input
            type="checkbox"
            :id="inputId"
            :checked="selected"
            :disabled="disabled || loading"
            @change="handleCheckboxChange"
          />
          <span class="filter-option__checkbox-checkmark"></span>
        </div>
        
        <!-- 单选框 -->
        <div v-else-if="type === 'radio'" class="filter-option__radio">
          <input
            type="radio"
            :id="inputId"
            :name="groupName"
            :value="value"
            :checked="selected"
            :disabled="disabled || loading"
            @change="handleRadioChange"
          />
          <span class="filter-option__radio-dot"></span>
        </div>
        
        <!-- 开关 -->
        <div v-else-if="type === 'switch'" class="filter-option__switch">
          <input
            type="checkbox"
            :id="inputId"
            :checked="selected"
            :disabled="disabled || loading"
            @change="handleSwitchChange"
          />
          <span class="filter-option__switch-slider"></span>
        </div>
      </div>
      
      <!-- 图标 -->
      <div v-if="icon" class="filter-option__icon">
        <component :is="icon" :size="iconSize" />
      </div>
      
      <!-- 标签内容 -->
      <div class="filter-option__content">
        <label :for="inputId" class="filter-option__label">
          <span class="filter-option__text">{{ label }}</span>
          <span v-if="badge" class="filter-option__badge">
            {{ badge }}
          </span>
        </label>
        
        <!-- 描述 -->
        <div v-if="description" class="filter-option__description">
          {{ description }}
        </div>
        
        <!-- 额外信息 -->
        <div v-if="extraInfo" class="filter-option__extra">
          {{ extraInfo }}
        </div>
      </div>
    </div>
    
    <!-- 选项右侧 -->
    <div class="filter-option__right">
      <!-- 计数 -->
      <div v-if="showCount && count !== undefined" class="filter-option__count">
        {{ formatCount(count) }}
      </div>
      
      <!-- 值显示 -->
      <div v-if="showValue && valueDisplay" class="filter-option__value">
        {{ valueDisplay }}
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="filter-option__loading">
        <div class="filter-option__loading-spinner"></div>
      </div>
      
      <!-- 操作按钮 -->
      <div v-if="showActions" class="filter-option__actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  option: {
    type: Object,
    default: () => ({
      id: '',
      label: '',
      value: '',
      type: 'checkbox',
      selected: false,
      disabled: false,
      icon: null,
      description: '',
      extraInfo: '',
      count: undefined,
      badge: ''
    })
  },
  type: {
    type: String,
    default: 'checkbox',
    validator: (value) => ['checkbox', 'radio', 'switch'].includes(value)
  },
  label: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number, Boolean],
    default: ''
  },
  selected: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  icon: {
    type: Object,
    default: null
  },
  description: {
    type: String,
    default: ''
  },
  extraInfo: {
    type: String,
    default: ''
  },
  badge: {
    type: String,
    default: ''
  },
  count: {
    type: Number,
    default: undefined
  },
  groupName: {
    type: String,
    default: ''
  },
  showCount: {
    type: Boolean,
    default: true
  },
  showValue: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: false
  },
  valueDisplay: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'compact', 'detailed'].includes(value)
  },
  highlight: {
    type: Boolean,
    default: false
  },
  interactive: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['select', 'deselect', 'change', 'click'])

// 计算属性
const optionClasses = computed(() => ({
  'filter-option': true,
  [`filter-option--${props.size}`]: true,
  [`filter-option--${props.variant}`]: true,
  [`filter-option--${props.type}`]: true,
  'filter-option--selected': props.selected,
  'filter-option--disabled': props.disabled,
  'filter-option--loading': props.loading,
  'filter-option--highlight': props.highlight,
  'filter-option--interactive': props.interactive,
  'filter-option--has-icon': !!props.icon,
  'filter-option--has-description': !!props.description
}))

const inputId = computed(() => {
  return `filter-option-${props.option.id || props.value || Math.random().toString(36).substr(2, 9)}`
})

const iconSize = computed(() => {
  const sizes = {
    small: 16,
    medium: 20,
    large: 24
  }
  return sizes[props.size] || 20
})

// 方法
const formatCount = (count) => {
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`
  }
  return count.toString()
}

const handleClick = () => {
  if (props.disabled || props.loading || !props.interactive) return
  emit('click', props.option)
}

const handleSelectorClick = () => {
  if (props.disabled || props.loading || !props.interactive) return
  
  if (props.type === 'checkbox' || props.type === 'switch') {
    handleCheckboxChange()
  } else if (props.type === 'radio') {
    handleRadioChange()
  }
}

const handleCheckboxChange = () => {
  if (props.disabled || props.loading) return
  
  const newSelected = !props.selected
  emit('change', {
    option: props.option,
    selected: newSelected,
    value: props.value
  })
  
  if (newSelected) {
    emit('select', props.option)
  } else {
    emit('deselect', props.option)
  }
}

const handleRadioChange = () => {
  if (props.disabled || props.loading || props.selected) return
  
  emit('change', {
    option: props.option,
    selected: true,
    value: props.value
  })
  
  emit('select', props.option)
}

const handleSwitchChange = () => {
  if (props.disabled || props.loading) return
  
  const newSelected = !props.selected
  emit('change', {
    option: props.option,
    selected: newSelected,
    value: newSelected
  })
  
  if (newSelected) {
    emit('select', props.option)
  } else {
    emit('deselect', props.option)
  }
}
</script>

<style scoped>
.filter-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  cursor: default;
}

.filter-option--interactive {
  cursor: pointer;
}

.filter-option--interactive:hover:not(.filter-option--disabled):not(.filter-option--loading) {
  background-color: var(--color-bg-secondary);
}

.filter-option--selected:not(.filter-option--disabled) {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  border-left: 3px solid var(--color-primary);
}

.filter-option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-option--loading {
  opacity: 0.7;
  cursor: wait;
}

.filter-option--highlight {
  background-color: rgba(var(--color-warning-rgb), 0.1);
}

/* 尺寸 */
.filter-option--small {
  padding: var(--spacing-2) var(--spacing-3);
}

.filter-option--medium {
  padding: var(--spacing-3) var(--spacing-4);
}

.filter-option--large {
  padding: var(--spacing-4) var(--spacing-5);
}

/* 变体 */
.filter-option--compact {
  padding: var(--spacing-2);
}

.filter-option--compact .filter-option__content {
  margin-left: var(--spacing-2);
}

.filter-option--detailed .filter-option__content {
  flex: 1;
}

.filter-option__left {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex: 1;
  min-width: 0;
}

.filter-option__selector {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 复选框样式 */
.filter-option__checkbox {
  position: relative;
  width: 20px;
  height: 20px;
}

.filter-option__checkbox input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  z-index: 1;
}

.filter-option__checkbox-checkmark {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg-card);
  transition: all 0.2s ease;
}

.filter-option__checkbox input:checked ~ .filter-option__checkbox-checkmark {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.filter-option__checkbox input:checked ~ .filter-option__checkbox-checkmark::after {
  content: '';
  position: absolute;
  top: 4px;
  left: 7px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filter-option__checkbox input:disabled {
  cursor: not-allowed;
}

.filter-option__checkbox input:disabled ~ .filter-option__checkbox-checkmark {
  opacity: 0.5;
}

/* 单选框样式 */
.filter-option__radio {
  position: relative;
  width: 20px;
  height: 20px;
}

.filter-option__radio input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  z-index: 1;
}

.filter-option__radio-dot {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid var(--color-border);
  border-radius: 50%;
  background-color: var(--color-bg-card);
  transition: all 0.2s ease;
}

.filter-option__radio input:checked ~ .filter-option__radio-dot {
  border-color: var(--color-primary);
}

.filter-option__radio input:checked ~ .filter-option__radio-dot::after {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  width: 8px;
  height: 8px;
  background-color: var(--color-primary);
  border-radius: 50%;
}

.filter-option__radio input:disabled {
  cursor: not-allowed;
}

.filter-option__radio input:disabled ~ .filter-option__radio-dot {
  opacity: 0.5;
}

/* 开关样式 */
.filter-option__switch {
  position: relative;
  width: 44px;
  height: 24px;
}

.filter-option__switch input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  z-index: 1;
}

.filter-option__switch-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  transition: all 0.3s ease;
}

.filter-option__switch-slider::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.filter-option__switch input:checked ~ .filter-option__switch-slider {
  background-color: var(--color-success);
}

.filter-option__switch input:checked ~ .filter-option__switch-slider::before {
  transform: translateX(20px);
}

.filter-option__switch input:disabled {
  cursor: not-allowed;
}

.filter-option__switch input:disabled ~ .filter-option__switch-slider {
  opacity: 0.5;
}

/* 图标 */
.filter-option__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.filter-option--selected .filter-option__icon {
  color: var(--color-primary);
}

/* 内容 */
.filter-option__content {
  flex: 1;
  min-width: 0;
}

.filter-option__label {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: inherit;
}

.filter-option__text {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.filter-option--small .filter-option__text {
  font-size: var(--font-size-sm);
}

.filter-option--large .filter-option__text {
  font-size: var(--font-size-lg);
}

.filter-option__badge {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: white;
  background-color: var(--color-warning);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.filter-option__description {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.filter-option__extra {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* 右侧内容 */
.filter-option__right {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-shrink: 0;
  margin-left: var(--spacing-3);
}

.filter-option__count {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  min-width: 32px;
  text-align: center;
}

.filter-option__value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-primary);
  padding: 2px 8px;
  background-color: rgba(var(--color-primary-rgb), 0.1);
  border-radius: var(--radius-sm);
}

.filter-option__loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-option__loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.filter-option__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 动画 */
.filter-option {
  animation: fade-in 0.2s ease;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>