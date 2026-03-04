<template>
  <div :class="wrapperClasses">
    <!-- 标签 -->
    <label
      v-if="label"
      :for="id"
      :class="['base-select__label', { 'base-select__label--required': required }]"
    >
      {{ label }}
    </label>

    <!-- 选择框容器 -->
    <div class="base-select__container" @click="toggleDropdown">
      <!-- 已选值显示 -->
      <div class="base-select__selected">
        <div v-if="selectedOption" class="base-select__selected-content">
          <!-- 选中项左侧图标 -->
          <component
            v-if="selectedOption.icon"
            :is="selectedOption.icon"
            :size="16"
            class="base-select__selected-icon"
          />
          <!-- 选中项文本 -->
          <span class="base-select__selected-text">{{ selectedOption.label }}</span>
        </div>
        <span v-else class="base-select__placeholder">{{ placeholder }}</span>
      </div>

      <!-- 下拉箭头 -->
      <span class="base-select__arrow" :class="{ 'base-select__arrow--open': isOpen }">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>

      <!-- 清除按钮 -->
      <button
        v-if="clearable && modelValue && !disabled"
        type="button"
        class="base-select__clear"
        @click.stop="handleClear"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
          <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- 加载状态 -->
      <div v-if="loading" class="base-select__loading">
        <div class="base-select__spinner"></div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="errorMessage" class="base-select__error">
      {{ errorMessage }}
    </div>

    <!-- 下拉菜单 -->
    <transition name="slide-fade">
      <div
        v-if="isOpen && !disabled"
        ref="dropdownRef"
        :class="['base-select__dropdown', `base-select__dropdown--${position}`]"
        :style="dropdownStyles"
      >
        <!-- 搜索框（如果启用搜索） -->
        <div v-if="searchable" class="base-select__search">
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            :placeholder="searchPlaceholder"
            class="base-select__search-input"
            @click.stop
            @keydown="handleSearchKeydown"
          />
        </div>

        <!-- 选项列表 -->
        <div class="base-select__options">
          <div
            v-for="(option, index) in filteredOptions"
            :key="option.value"
            :class="[
              'base-select__option',
              {
                'base-select__option--selected': isOptionSelected(option),
                'base-select__option--disabled': option.disabled,
                'base-select__option--focused': focusedIndex === index
              }
            ]"
            @click.stop="selectOption(option)"
            @mouseenter="focusedIndex = index"
          >
            <!-- 选项左侧图标 -->
            <component
              v-if="option.icon"
              :is="option.icon"
              :size="16"
              class="base-select__option-icon"
            />
            
            <!-- 选项文本 -->
            <span class="base-select__option-text">{{ option.label }}</span>
            
            <!-- 选中标记 -->
            <span v-if="isOptionSelected(option)" class="base-select__option-check">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </div>

          <!-- 无选项状态 -->
          <div v-if="filteredOptions.length === 0" class="base-select__empty">
            {{ emptyText }}
          </div>
        </div>

        <!-- 分组选项 -->
        <template v-if="grouped">
          <div
            v-for="(group, groupName) in groupedOptions"
            :key="groupName"
            class="base-select__group"
          >
            <div class="base-select__group-label">{{ groupName }}</div>
            <div class="base-select__group-options">
              <div
                v-for="option in group"
                :key="option.value"
                :class="[
                  'base-select__option',
                  {
                    'base-select__option--selected': isOptionSelected(option),
                    'base-select__option--disabled': option.disabled,
                    'base-select__option--focused': false
                  }
                ]"
                @click.stop="selectOption(option)"
              >
                <component
                  v-if="option.icon"
                  :is="option.icon"
                  :size="16"
                  class="base-select__option-icon"
                />
                <span class="base-select__option-text">{{ option.label }}</span>
                <span v-if="isOptionSelected(option)" class="base-select__option-check">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Array],
    default: null
  },
  options: {
    type: Array,
    default: () => []
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请选择'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: Boolean,
    default: false
  },
  errorMessage: {
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
    validator: (value) => ['default', 'filled', 'outlined'].includes(value)
  },
  clearable: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  searchable: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: '搜索...'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  grouped: {
    type: Boolean,
    default: false
  },
  position: {
    type: String,
    default: 'bottom',
    validator: (value) => ['bottom', 'top'].includes(value)
  },
  emptyText: {
    type: String,
    default: '无选项'
  },
  optionLabel: {
    type: String,
    default: 'label'
  },
  optionValue: {
    type: String,
    default: 'value'
  },
  optionDisabled: {
    type: String,
    default: 'disabled'
  },
  maxHeight: {
    type: String,
    default: '200px'
  },
  id: {
    type: String,
    default: () => `select-${Math.random().toString(36).substr(2, 9)}`
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'open', 'close', 'search'])

const isOpen = ref(false)
const searchQuery = ref('')
const focusedIndex = ref(-1)
const dropdownRef = ref(null)
const searchInputRef = ref(null)

// 计算选中的选项
const selectedOption = computed(() => {
  if (!props.modelValue) return null
  
  if (props.multiple) {
    // 多选情况
    return props.options.find(option => 
      Array.isArray(props.modelValue) && 
      props.modelValue.includes(option[props.optionValue])
    )
  } else {
    // 单选情况
    return props.options.find(option => 
      option[props.optionValue] === props.modelValue
    )
  }
})

// 计算过滤后的选项
const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options.filter(option => !option.disabled)
  }
  
  return props.options.filter(option => {
    const label = option[props.optionLabel] || option.label || ''
    return label.toLowerCase().includes(searchQuery.value.toLowerCase()) && !option.disabled
  })
})

// 计算分组选项
const groupedOptions = computed(() => {
  if (!props.grouped) return {}
  
  return props.options.reduce((groups, option) => {
    const group = option.group || '默认分组'
    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(option)
    return groups
  }, {})
})

// 计算下拉菜单样式
const dropdownStyles = computed(() => ({
  maxHeight: props.maxHeight
}))

// 计算包装类名
const wrapperClasses = computed(() => ({
  'base-select': true,
  [`base-select--${props.size}`]: true,
  [`base-select--${props.variant}`]: true,
  'base-select--disabled': props.disabled,
  'base-select--error': props.error || props.errorMessage,
  'base-select--open': isOpen.value,
  'base-select--multiple': props.multiple
}))

// 检查选项是否被选中
const isOptionSelected = (option) => {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && 
           props.modelValue.includes(option[props.optionValue])
  }
  return props.modelValue === option[props.optionValue]
}

// 切换下拉菜单
const toggleDropdown = () => {
  if (props.disabled || props.loading) return
  
  isOpen.value = !isOpen.value
  
  if (isOpen.value) {
    emit('open')
    // 聚焦搜索框（如果启用搜索）
    if (props.searchable) {
      nextTick(() => {
        searchInputRef.value?.focus()
      })
    }
    // 添加全局点击事件监听
    document.addEventListener('click', handleClickOutside)
  } else {
    emit('close')
    document.removeEventListener('click', handleClickOutside)
  }
}

// 选择选项
const selectOption = (option) => {
  if (option.disabled) return
  
  if (props.multiple) {
    const currentValue = Array.isArray(props.modelValue) ? props.modelValue : []
    const optionValue = option[props.optionValue]
    
    let newValue
    if (currentValue.includes(optionValue)) {
      // 取消选中
      newValue = currentValue.filter(v => v !== optionValue)
    } else {
      // 添加选中
      newValue = [...currentValue, optionValue]
    }
    
    emit('update:modelValue', newValue)
    emit('change', newValue)
  } else {
    // 单选
    emit('update:modelValue', option[props.optionValue])
    emit('change', option[props.optionValue])
    // 关闭下拉菜单
    closeDropdown()
  }
}

// 清除选中
const handleClear = () => {
  if (props.disabled) return
  
  const newValue = props.multiple ? [] : null
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

// 处理搜索框按键
const handleSearchKeydown = (event) => {
  // 阻止事件冒泡，避免触发下拉菜单关闭
  event.stopPropagation()
  
  // 箭头键导航
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    navigateOptions(event.key)
  }
  
  // Enter键选择
  if (event.key === 'Enter' && focusedIndex.value >= 0) {
    event.preventDefault()
    const option = filteredOptions.value[focusedIndex.value]
    if (option && !option.disabled) {
      selectOption(option)
    }
  }
  
  // Escape键关闭
  if (event.key === 'Escape') {
    closeDropdown()
  }
}

// 导航选项
const navigateOptions = (direction) => {
  const options = filteredOptions.value
  if (options.length === 0) return
  
  if (direction === 'ArrowDown') {
    focusedIndex.value = (focusedIndex.value + 1) % options.length
  } else if (direction === 'ArrowUp') {
    focusedIndex.value = focusedIndex.value <= 0 ? options.length - 1 : focusedIndex.value - 1
  }
  
  // 滚动到聚焦的选项
  nextTick(() => {
    const focusedElement = dropdownRef.value?.querySelector('.base-select__option--focused')
    if (focusedElement) {
      focusedElement.scrollIntoView({ block: 'nearest' })
    }
  })
}

// 关闭下拉菜单
const closeDropdown = () => {
  if (isOpen.value) {
    isOpen.value = false
    searchQuery.value = ''
    focusedIndex.value = -1
    emit('close')
    document.removeEventListener('click', handleClickOutside)
  }
}

// 处理点击外部
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
  }
}

// 监听搜索
watch(searchQuery, (newQuery) => {
  emit('search', newQuery)
  focusedIndex.value = -1
})

// 生命周期
onMounted(() => {
  if (props.searchable) {
    // 添加键盘事件监听
    document.addEventListener('keydown', handleGlobalKeydown)
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleGlobalKeydown)
})

// 全局键盘事件
const handleGlobalKeydown = (event) => {
  if (!isOpen.value) return
  
  // Escape键关闭
  if (event.key === 'Escape') {
    closeDropdown()
  }
}

// 暴露方法
defineExpose({
  open: () => toggleDropdown(),
  close: () => closeDropdown(),
  clear: () => handleClear()
})
</script>

<style scoped>
.base-select {
  position: relative;
  display: inline-block;
  width: 100%;
}

.base-select__label {
  display: block;
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.base-select__label--required::after {
  content: ' *';
  color: var(--color-danger);
}

.base-select__container {
  position: relative;
  cursor: pointer;
  background-color: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  min-height: 40px;
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-3);
}

.base-select__container:hover:not(.base-select--disabled) {
  border-color: var(--color-primary);
}

.base-select__selected {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  overflow: hidden;
}

.base-select__selected-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.base-select__selected-icon {
  color: var(--color-text-secondary);
}

.base-select__selected-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.base-select__placeholder {
  color: var(--color-text-placeholder);
}

.base-select__arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
  color: var(--color-text-secondary);
}

.base-select__arrow--open {
  transform: rotate(180deg);
}

.base-select__clear {
  position: absolute;
  right: 30px;
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
}

.base-select__clear:hover {
  opacity: 1;
}

.base-select__loading {
  position: absolute;
  right: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.base-select__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.base-select__error {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

.base-select__dropdown {
  position: absolute;
  z-index: 1000;
  width: 100%;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  margin-top: var(--spacing-1);
  overflow: hidden;
}

.base-select__dropdown--bottom {
  top: 100%;
}

.base-select__dropdown--top {
  bottom: 100%;
  margin-top: 0;
  margin-bottom: var(--spacing-1);
}

.base-select__search {
  padding: var(--spacing-2);
  border-bottom: 1px solid var(--color-border-light);
}

.base-select__search-input {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  outline: none;
}

.base-select__search-input:focus {
  border-color: var(--color-primary);
}

.base-select__options {
  max-height: 200px;
  overflow-y: auto;
}

.base-select__option {
  display: flex;
  align-items: center;
  padding: var(--spacing-2) var(--spacing-3);
  cursor: pointer;
  transition: background-color 0.2s;
  gap: var(--spacing-2);
}

.base-select__option:hover:not(.base-select__option--disabled) {
  background-color: var(--color-bg-secondary);
}

.base-select__option--selected {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

.base-select__option--focused {
  background-color: var(--color-bg-secondary);
}

.base-select__option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.base-select__option-icon {
  color: var(--color-text-secondary);
}

.base-select__option-text {
  flex: 1;
}

.base-select__option-check {
  color: var(--color-primary);
}

.base-select__empty {
  padding: var(--spacing-3);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.base-select__group {
  margin-top: var(--spacing-2);
}

.base-select__group-label {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  background-color: var(--color-bg-secondary);
  text-transform: uppercase;
}

.base-select__group-options {
  margin-top: var(--spacing-1);
}

/* 尺寸变体 */
.base-select--small .base-select__container {
  min-height: 32px;
  padding: 0 var(--spacing-2);
}

.base-select--large .base-select__container {
  min-height: 48px;
  padding: 0 var(--spacing-4);
}

/* 状态变体 */
.base-select--error .base-select__container {
  border-color: var(--color-danger);
}

.base-select--disabled .base-select__container {
  background-color: var(--color-bg-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

/* 动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>