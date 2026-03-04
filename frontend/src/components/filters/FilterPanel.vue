<template>
  <div :class="panelClasses">
    <!-- 面板头部 -->
    <div v-if="showHeader" class="filter-panel__header">
      <div class="filter-panel__header-content">
        <h3 class="filter-panel__title">{{ title }}</h3>
        <div v-if="subtitle" class="filter-panel__subtitle">{{ subtitle }}</div>
      </div>
      
      <div class="filter-panel__header-actions">
        <!-- 清空筛选按钮 -->
        <button
          v-if="showClearButton"
          class="filter-panel__clear"
          :disabled="!hasActiveFilters || loading"
          @click="clearAllFilters"
        >
          {{ clearButtonText }}
        </button>
        
        <!-- 收起/展开按钮 -->
        <button
          v-if="collapsible"
          class="filter-panel__toggle"
          @click="toggleCollapse"
          aria-label="收起/展开筛选面板"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            :class="{ 'filter-panel__toggle-icon--collapsed': isCollapsed }"
          >
            <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 筛选内容 -->
    <div v-show="!isCollapsed || !collapsible" class="filter-panel__content">
      <!-- 筛选标签组 -->
      <div class="filter-panel__groups">
        <!-- 每个筛选组 -->
        <div
          v-for="(group, groupIndex) in visibleFilterGroups"
          :key="group.id || groupIndex"
          :class="['filter-panel__group', `filter-panel__group--${group.type || 'default'}`]"
        >
          <!-- 筛选组头部 -->
          <div class="filter-panel__group-header" @click="toggleGroupCollapse(group)">
            <div class="filter-panel__group-title">
              <h4 class="filter-panel__group-title-text">{{ group.title }}</h4>
              <span v-if="group.description" class="filter-panel__group-description">
                {{ group.description }}
              </span>
            </div>
            
            <div class="filter-panel__group-actions">
              <!-- 组内已选数量 -->
              <span v-if="getSelectedCount(group) > 0" class="filter-panel__group-count">
                {{ getSelectedCount(group) }}
              </span>
              
              <!-- 组收起按钮 -->
              <svg
                v-if="group.collapsible !== false"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                :class="['filter-panel__group-toggle', { 'filter-panel__group-toggle--collapsed': isGroupCollapsed(group) }]"
              >
                <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
              </svg>
            </div>
          </div>

          <!-- 筛选组内容 -->
          <transition name="slide-down">
            <div
              v-show="!isGroupCollapsed(group) || group.collapsible === false"
              class="filter-panel__group-content"
            >
              <!-- 搜索框（如果组支持搜索） -->
              <div v-if="group.searchable" class="filter-panel__group-search">
                <BaseInput
                  v-model="groupSearchQueries[group.id]"
                  placeholder="搜索..."
                  size="small"
                  prepend-icon="search"
                  clearable
                  @clear="clearGroupSearch(group)"
                />
              </div>

              <!-- 筛选选项 -->
              <div class="filter-panel__options">
                <!-- 根据类型渲染不同的筛选组件 -->
                <template v-if="group.type === 'checkbox'">
                  <div class="filter-panel__checkbox-options">
                    <label
                      v-for="option in getFilteredOptions(group)"
                      :key="option.value"
                      :class="['filter-panel__checkbox-option', { 'filter-panel__checkbox-option--disabled': option.disabled }]"
                    >
                      <input
                        type="checkbox"
                        :value="option.value"
                        :disabled="option.disabled || loading"
                        :checked="isOptionSelected(group, option)"
                        @change="toggleOption(group, option, $event)"
                      />
                      <span class="filter-panel__checkbox-label">
                        {{ option.label }}
                      </span>
                      <span v-if="option.count !== undefined" class="filter-panel__option-count">
                        {{ option.count }}
                      </span>
                    </label>
                  </div>
                </template>

                <template v-else-if="group.type === 'radio'">
                  <div class="filter-panel__radio-options">
                    <label
                      v-for="option in getFilteredOptions(group)"
                      :key="option.value"
                      :class="['filter-panel__radio-option', { 'filter-panel__radio-option--disabled': option.disabled }]"
                    >
                      <input
                        type="radio"
                        :name="group.id"
                        :value="option.value"
                        :disabled="option.disabled || loading"
                        :checked="isOptionSelected(group, option)"
                        @change="selectOption(group, option, $event)"
                      />
                      <span class="filter-panel__radio-label">
                        {{ option.label }}
                      </span>
                      <span v-if="option.count !== undefined" class="filter-panel__option-count">
                        {{ option.count }}
                      </span>
                    </label>
                  </div>
                </template>

                <template v-else-if="group.type === 'select'">
                  <div class="filter-panel__select-group">
                    <BaseSelect
                      v-model="selectedOptions[group.id]"
                      :options="group.options"
                      :placeholder="group.placeholder || '请选择'"
                      :multiple="group.multiple || false"
                      :searchable="group.searchable || false"
                      :clearable="group.clearable || true"
                      size="small"
                      full-width
                      @change="(value) => handleSelectChange(group, value)"
                    />
                  </div>
                </template>

                <template v-else-if="group.type === 'range'">
                  <div class="filter-panel__range-group">
                    <div class="filter-panel__range-inputs">
                      <BaseInput
                        v-model.number="rangeValues[group.id].min"
                        :placeholder="group.minPlaceholder || '最小值'"
                        type="number"
                        size="small"
                        :min="group.min"
                        :max="rangeValues[group.id].max"
                        @input="handleRangeInput(group, 'min')"
                      />
                      <span class="filter-panel__range-separator">-</span>
                      <BaseInput
                        v-model.number="rangeValues[group.id].max"
                        :placeholder="group.maxPlaceholder || '最大值'"
                        type="number"
                        size="small"
                        :min="rangeValues[group.id].min"
                        :max="group.max"
                        @input="handleRangeInput(group, 'max')"
                      />
                    </div>
                    
                    <!-- 范围滑块 -->
                    <div v-if="group.showSlider" class="filter-panel__range-slider">
                      <input
                        type="range"
                        :min="group.min"
                        :max="group.max"
                        :step="group.step || 1"
                        v-model.number="rangeValues[group.id].min"
                        class="filter-panel__range-slider-min"
                        @input="handleRangeSlider(group, 'min')"
                      />
                      <input
                        type="range"
                        :min="group.min"
                        :max="group.max"
                        :step="group.step || 1"
                        v-model.number="rangeValues[group.id].max"
                        class="filter-panel__range-slider-max"
                        @input="handleRangeSlider(group, 'max')"
                      />
                    </div>
                    
                    <!-- 范围值显示 -->
                    <div v-if="group.showValues" class="filter-panel__range-values">
                      {{ rangeValues[group.id].min }} - {{ rangeValues[group.id].max }}
                      <span v-if="group.unit">{{ group.unit }}</span>
                    </div>
                  </div>
                </template>

                <template v-else-if="group.type === 'date'">
                  <div class="filter-panel__date-group">
                    <div class="filter-panel__date-inputs">
                      <BaseInput
                        v-model="dateValues[group.id].start"
                        :placeholder="group.startPlaceholder || '开始日期'"
                        type="date"
                        size="small"
                        @change="handleDateChange(group, 'start')"
                      />
                      <span class="filter-panel__date-separator">至</span>
                      <BaseInput
                        v-model="dateValues[group.id].end"
                        :placeholder="group.endPlaceholder || '结束日期'"
                        type="date"
                        size="small"
                        :min="dateValues[group.id].start"
                        @change="handleDateChange(group, 'end')"
                      />
                    </div>
                  </div>
                </template>

                <template v-else-if="group.type === 'tags'">
                  <div class="filter-panel__tags-group">
                    <IntelTags
                      :tags="getFilteredOptions(group)"
                      :selected-tags="selectedOptions[group.id] || []"
                      :multiple="group.multiple !== false"
                      :limit="group.limit"
                      :size="group.tagSize || 'small'"
                      :show-count="group.showCount || false"
                      @tag-select="(tags) => handleTagsChange(group, tags)"
                    />
                  </div>
                </template>

                <template v-else>
                  <!-- 默认类型：checkbox -->
                  <div class="filter-panel__checkbox-options">
                    <label
                      v-for="option in getFilteredOptions(group)"
                      :key="option.value"
                      :class="['filter-panel__checkbox-option', { 'filter-panel__checkbox-option--disabled': option.disabled }]"
                    >
                      <input
                        type="checkbox"
                        :value="option.value"
                        :disabled="option.disabled || loading"
                        :checked="isOptionSelected(group, option)"
                        @change="toggleOption(group, option, $event)"
                      />
                      <span class="filter-panel__checkbox-label">
                        {{ option.label }}
                      </span>
                      <span v-if="option.count !== undefined" class="filter-panel__option-count">
                        {{ option.count }}
                      </span>
                    </label>
                  </div>
                </template>
              </div>

              <!-- 无选项时显示 -->
              <div v-if="getFilteredOptions(group).length === 0" class="filter-panel__no-options">
                暂无选项
              </div>

              <!-- 显示更多按钮 -->
              <button
                v-if="group.showMoreButton && getFilteredOptions(group).length < group.options.length"
                class="filter-panel__show-more"
                @click="showAllOptions(group)"
              >
                显示全部 {{ group.options.length }} 个选项
              </button>

              <!-- 组操作按钮 -->
              <div v-if="group.actions" class="filter-panel__group-actions-bottom">
                <button
                  v-for="action in group.actions"
                  :key="action.id"
                  :class="['filter-panel__group-action', `filter-panel__group-action--${action.type}`]"
                  @click="handleGroupAction(group, action)"
                >
                  {{ action.label }}
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="filter-panel__loading">
        <LoadingSpinner size="small" text="加载筛选选项..." />
      </div>

      <!-- 无筛选组时显示 -->
      <div v-if="!loading && visibleFilterGroups.length === 0" class="filter-panel__empty">
        <EmptyState
          :title="emptyTitle"
          :description="emptyDescription"
          icon="🔍"
          variant="compact"
        />
      </div>
    </div>

    <!-- 面板底部 -->
    <div v-if="showFooter && (!isCollapsed || !collapsible)" class="filter-panel__footer">
      <div class="filter-panel__footer-left">
        <!-- 筛选摘要 -->
        <FilterSummary
          v-if="showSummary"
          :filters="activeFilters"
          :result-count="resultCount"
          :show-count="showResultCount"
          @clear="clearAllFilters"
        />
      </div>
      
      <div class="filter-panel__footer-right">
        <!-- 取消按钮 -->
        <BaseButton
          v-if="showCancelButton"
          variant="outline"
          size="small"
          @click="$emit('cancel')"
        >
          {{ cancelButtonText }}
        </BaseButton>
        
        <!-- 应用按钮 -->
        <BaseButton
          v-if="showApplyButton"
          variant="primary"
          size="small"
          :loading="applying"
          @click="applyFilters"
        >
          {{ applyButtonText }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import BaseInput from '../common/BaseInput.vue'
import BaseSelect from '../common/BaseSelect.vue'
import BaseButton from '../common/BaseButton.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import EmptyState from '../common/EmptyState.vue'
import IntelTags from '../intelligence/IntelTags.vue'
import FilterSummary from './FilterSummary.vue'

const props = defineProps({
  filters: {
    type: Array,
    default: () => []
  },
  activeFilters: {
    type: Object,
    default: () => ({})
  },
  title: {
    type: String,
    default: '筛选条件'
  },
  subtitle: {
    type: String,
    default: ''
  },
  collapsible: {
    type: Boolean,
    default: false
  },
  collapsedByDefault: {
    type: Boolean,
    default: false
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showClearButton: {
    type: Boolean,
    default: true
  },
  showCancelButton: {
    type: Boolean,
    default: false
  },
  showApplyButton: {
    type: Boolean,
    default: true
  },
  showSummary: {
    type: Boolean,
    default: true
  },
  showResultCount: {
    type: Boolean,
    default: true
  },
  resultCount: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  applying: {
    type: Boolean,
    default: false
  },
  clearButtonText: {
    type: String,
    default: '清空筛选'
  },
  cancelButtonText: {
    type: String,
    default: '取消'
  },
  applyButtonText: {
    type: String,
    default: '应用筛选'
  },
  emptyTitle: {
    type: String,
    default: '无筛选条件'
  },
  emptyDescription: {
    type: String,
    default: '暂无可用的筛选条件'
  },
  maxVisibleOptions: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits([
  'update:activeFilters',
  'filter-change',
  'apply',
  'cancel',
  'clear',
  'group-action'
])

// 响应式状态
const isCollapsed = ref(props.collapsedByDefault)
const collapsedGroups = ref({})
const groupSearchQueries = ref({})
const selectedOptions = ref({})
const rangeValues = ref({})
const dateValues = ref({})
const visibleOptionsLimit = ref({})

// 计算属性
const panelClasses = computed(() => ({
  'filter-panel': true,
  'filter-panel--collapsible': props.collapsible,
  'filter-panel--collapsed': isCollapsed.value,
  'filter-panel--loading': props.loading,
  'filter-panel--has-active-filters': hasActiveFilters.value
}))

const visibleFilterGroups = computed(() => {
  return props.filters.filter(group => !group.hidden)
})

const hasActiveFilters = computed(() => {
  return Object.keys(props.activeFilters).length > 0
})

// 方法
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleGroupCollapse = (group) => {
  if (group.collapsible === false) return
  
  const groupId = group.id || group.title
  if (collapsedGroups.value[groupId]) {
    delete collapsedGroups.value[groupId]
  } else {
    collapsedGroups.value[groupId] = true
  }
}

const isGroupCollapsed = (group) => {
  const groupId = group.id || group.title
  return collapsedGroups.value[groupId] || false
}

const getSelectedCount = (group) => {
  const groupId = group.id || group.title
  const selected = selectedOptions.value[groupId]
  
  if (!selected) return 0
  
  if (Array.isArray(selected)) {
    return selected.length
  }
  
  // 对于范围筛选
  if (group.type === 'range') {
    const range = rangeValues.value[groupId]
    if (range && (range.min !== undefined || range.max !== undefined)) {
      return 1
    }
  }
  
  // 对于日期筛选
  if (group.type === 'date') {
    const date = dateValues.value[groupId]
    if (date && (date.start || date.end)) {
      return 1
    }
  }
  
  return selected ? 1 : 0
}

const getFilteredOptions = (group) => {
  let options = group.options || []
  
  // 应用搜索
  const searchQuery = groupSearchQueries.value[group.id]
  if (searchQuery && group.searchable) {
    const query = searchQuery.toLowerCase()
    options = options.filter(option => 
      option.label.toLowerCase().includes(query) ||
      option.value.toString().toLowerCase().includes(query)
    )
  }
  
  // 应用数量限制
  const limit = visibleOptionsLimit.value[group.id] || props.maxVisibleOptions
  return options.slice(0, limit)
}

const isOptionSelected = (group, option) => {
  const groupId = group.id || group.title
  const selected = selectedOptions.value[groupId]
  
  if (!selected) return false
  
  if (Array.isArray(selected)) {
    return selected.includes(option.value)
  }
  
  return selected === option.value
}

const toggleOption = (group, option, event) => {
  const groupId = group.id || group.title
  const isChecked = event.target.checked
  
  if (!selectedOptions.value[groupId]) {
    selectedOptions.value[groupId] = []
  }
  
  if (isChecked) {
    if (group.multiple !== false) {
      selectedOptions.value[groupId].push(option.value)
    } else {
      selectedOptions.value[groupId] = [option.value]
    }
  } else {
    selectedOptions.value[groupId] = selectedOptions.value[groupId].filter(
      val => val !== option.value
    )
  }
  
  updateActiveFilters(group)
}

const selectOption = (group, option, event) => {
  const groupId = group.id || group.title
  const isChecked = event.target.checked
  
  if (isChecked) {
    selectedOptions.value[groupId] = option.value
    updateActiveFilters(group)
  }
}

const handleSelectChange = (group, value) => {
  const groupId = group.id || group.title
  selectedOptions.value[groupId] = value
  updateActiveFilters(group)
}

const handleRangeInput = (group, type) => {
  const groupId = group.id || group.title
  updateActiveFilters(group)
}

const handleRangeSlider = (group, type) => {
  const groupId = group.id || group.title
  updateActiveFilters(group)
}

const handleDateChange = (group, type) => {
  const groupId = group.id || group.title
  updateActiveFilters(group)
}

const handleTagsChange = (group, tags) => {
  const groupId = group.id || group.title
  selectedOptions.value[groupId] = tags
  updateActiveFilters(group)
}

const updateActiveFilters = (group) => {
  const groupId = group.id || group.title
  let filterValue
  
  // 根据筛选类型格式化值
  if (group.type === 'range') {
    const range = rangeValues.value[groupId]
    if (range && (range.min !== undefined || range.max !== undefined)) {
      filterValue = { ...range }
    }
  } else if (group.type === 'date') {
    const date = dateValues.value[groupId]
    if (date && (date.start || date.end)) {
      filterValue = { ...date }
    }
  } else {
    filterValue = selectedOptions.value[groupId]
  }
  
  // 更新活动筛选
  const newActiveFilters = { ...props.activeFilters }
  
  if (filterValue && 
      (!Array.isArray(filterValue) || filterValue.length > 0) &&
      (typeof filterValue !== 'object' || Object.keys(filterValue).length > 0)) {
    newActiveFilters[groupId] = {
      ...group,
      value: filterValue
    }
  } else {
    delete newActiveFilters[groupId]
  }
  
  emit('update:activeFilters', newActiveFilters)
  emit('filter-change', { group, value: filterValue })
}

const clearGroupSearch = (group) => {
  groupSearchQueries.value[group.id] = ''
}

const showAllOptions = (group) => {
  const groupId = group.id || group.title
  visibleOptionsLimit.value[groupId] = group.options.length
}

const handleGroupAction = (group, action) => {
  emit('group-action', { group, action })
}

const applyFilters = () => {
  emit('apply', props.activeFilters)
}

const clearAllFilters = () => {
  // 清空所有选择
  selectedOptions.value = {}
  rangeValues.value = {}
  dateValues.value = {}
  groupSearchQueries.value = {}
  visibleOptionsLimit.value = {}
  collapsedGroups.value = {}
  
  // 发出清空事件
  emit('update:activeFilters', {})
  emit('clear')
}

// 初始化
const initializeFilters = () => {
  props.filters.forEach(group => {
    const groupId = group.id || group.title
    
    // 初始化范围值
    if (group.type === 'range') {
      rangeValues.value[groupId] = {
        min: group.min || 0,
        max: group.max || 100
      }
    }
    
    // 初始化日期值
    if (group.type === 'date') {
      dateValues.value[groupId] = {
        start: '',
        end: ''
      }
    }
    
    // 初始化可见选项限制
    if (group.options && group.options.length > props.maxVisibleOptions) {
      visibleOptionsLimit.value[groupId] = props.maxVisibleOptions
    }
  })
}

// 监听筛选器变化
watch(() => props.filters, () => {
  initializeFilters()
}, { immediate: true })

// 监听活动筛选变化
watch(() => props.activeFilters, (newActiveFilters) => {
  // 更新内部状态以反映活动筛选
  Object.entries(newActiveFilters).forEach(([groupId, filter]) => {
    if (filter.value) {
      selectedOptions.value[groupId] = filter.value
    }
  })
}, { deep: true })

// 暴露方法
defineExpose({
  collapse: () => { isCollapsed.value = true },
  expand: () => { isCollapsed.value = false },
  clearAll: clearAllFilters,
  apply: applyFilters
})
</script>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.filter-panel--collapsible {
  transition: all 0.3s ease;
}

.filter-panel--collapsed {
  max-height: 60px;
  overflow: hidden;
}

.filter-panel--has-active-filters {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.filter-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-5) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.filter-panel__header-content {
  flex: 1;
  min-width: 0;
}

.filter-panel__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-panel__subtitle {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.filter-panel__header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-shrink: 0;
}

.filter-panel__clear {
  padding: var(--spacing-1) var(--spacing-3);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-panel__clear:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-panel__clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-panel__toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-panel__toggle:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.filter-panel__toggle-icon--collapsed {
  transform: rotate(180deg);
}

.filter-panel__content {
  flex: 1;
  overflow-y: auto;
  max-height: 600px;
}

.filter-panel__groups {
  display: flex;
  flex-direction: column;
}

.filter-panel__group {
  border-bottom: 1px solid var(--color-border-light);
}

.filter-panel__group:last-child {
  border-bottom: none;
}

.filter-panel__group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4) var(--spacing-6);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.filter-panel__group-header:hover {
  background-color: var(--color-bg-secondary);
}

.filter-panel__group-title {
  flex: 1;
  min-width: 0;
}

.filter-panel__group-title-text {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-panel__group-description {
  display: block;
  margin-top: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.filter-panel__group-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex-shrink: 0;
}

.filter-panel__group-count {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: white;
  background-color: var(--color-primary);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  min-width: 20px;
  text-align: center;
}

.filter-panel__group-toggle {
  transition: transform 0.3s ease;
}

.filter-panel__group-toggle--collapsed {
  transform: rotate(180deg);
}

.filter-panel__group-content {
  padding: 0 var(--spacing-6) var(--spacing-4);
}

.filter-panel__group-search {
  margin-bottom: var(--spacing-3);
}

.filter-panel__options {
  margin-bottom: var(--spacing-3);
}

/* 复选框选项样式 */
.filter-panel__checkbox-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.filter-panel__checkbox-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) 0;
  cursor: pointer;
  user-select: none;
}

.filter-panel__checkbox-option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-panel__checkbox-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--color-border);
  appearance: none;
  cursor: pointer;
  position: relative;
}

.filter-panel__checkbox-option input[type="checkbox"]:checked {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.filter-panel__checkbox-option input[type="checkbox"]:checked::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filter-panel__checkbox-option input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.filter-panel__checkbox-label {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.filter-panel__option-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  min-width: 24px;
  text-align: center;
}

/* 单选框选项样式 */
.filter-panel__radio-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.filter-panel__radio-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) 0;
  cursor: pointer;
  user-select: none;
}

.filter-panel__radio-option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-panel__radio-option input[type="radio"] {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  appearance: none;
  cursor: pointer;
  position: relative;
}

.filter-panel__radio-option input[type="radio"]:checked {
  border-color: var(--color-primary);
}

.filter-panel__radio-option input[type="radio"]:checked::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 6px;
  height: 6px;
  background-color: var(--color-primary);
  border-radius: 50%;
}

.filter-panel__radio-option input[type="radio"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.filter-panel__radio-label {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

/* 下拉选择样式 */
.filter-panel__select-group {
  margin-bottom: var(--spacing-3);
}

/* 范围筛选样式 */
.filter-panel__range-group {
  margin-bottom: var(--spacing-4);
}

.filter-panel__range-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-3);
}

.filter-panel__range-separator {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.filter-panel__range-slider {
  position: relative;
  height: 20px;
  margin-bottom: var(--spacing-3);
}

.filter-panel__range-slider-min,
.filter-panel__range-slider-max {
  position: absolute;
  width: 100%;
  height: 4px;
  background: transparent;
  pointer-events: none;
  appearance: none;
}

.filter-panel__range-slider-min::-webkit-slider-thumb,
.filter-panel__range-slider-max::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  pointer-events: all;
}

.filter-panel__range-slider-min::-moz-range-thumb,
.filter-panel__range-slider-max::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  border: none;
}

.filter-panel__range-values {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  text-align: center;
  font-weight: 600;
}

/* 日期筛选样式 */
.filter-panel__date-group {
  margin-bottom: var(--spacing-3);
}

.filter-panel__date-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.filter-panel__date-separator {
  color: var(--color-text-secondary);
  font-weight: 600;
}

/* 标签筛选样式 */
.filter-panel__tags-group {
  margin-bottom: var(--spacing-3);
}

.filter-panel__no-options {
  text-align: center;
  padding: var(--spacing-4);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.filter-panel__show-more {
  display: block;
  width: 100%;
  padding: var(--spacing-2);
  background: transparent;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.filter-panel__show-more:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-panel__group-actions-bottom {
  display: flex;
  gap: var(--spacing-2);
  margin-top: var(--spacing-3);
}

.filter-panel__group-action {
  flex: 1;
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-panel__group-action:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-panel__group-action--primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.filter-panel__group-action--primary:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.filter-panel__loading {
  padding: var(--spacing-8);
  text-align: center;
}

.filter-panel__empty {
  padding: var(--spacing-8);
}

.filter-panel__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
}

.filter-panel__footer-left {
  flex: 1;
  min-width: 0;
}

.filter-panel__footer-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-shrink: 0;
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-enter-to,
.slide-down-leave-from {
  max-height: 500px;
  opacity: 1;
  transform: translateY(0);
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-panel__header,
  .filter-panel__group-header,
  .filter-panel__group-content,
  .filter-panel__footer {
    padding-left: var(--spacing-4);
    padding-right: var(--spacing-4);
  }
  
  .filter-panel__footer {
    flex-direction: column;
    gap: var(--spacing-3);
    align-items: stretch;
  }
  
  .filter-panel__footer-right {
    width: 100%;
  }
}
</style>