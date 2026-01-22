<template>
  <div :class="summaryClasses">
    <!-- 标题 -->
    <div v-if="showTitle" class="filter-summary__header">
      <h4 class="filter-summary__title">筛选摘要</h4>
      <div v-if="lastUpdated" class="filter-summary__updated">
        更新于 {{ formatTime(lastUpdated) }}
      </div>
    </div>

    <!-- 结果数量 -->
    <div v-if="showResultCount" class="filter-summary__results">
      <span class="filter-summary__results-text">
        共找到 <strong>{{ resultCount }}</strong> 个结果
      </span>
      <span v-if="originalCount" class="filter-summary__results-original">
        (共 {{ originalCount }} 个)
      </span>
    </div>

    <!-- 筛选条件标签 -->
    <div v-if="showFilters && hasFilters" class="filter-summary__filters">
      <div class="filter-summary__filters-header">
        <span class="filter-summary__filters-title">当前筛选条件:</span>
        <button
          v-if="showClearButton"
          class="filter-summary__clear"
          @click="clearAllFilters"
          :disabled="loading"
        >
          清空全部
        </button>
      </div>
      
      <div class="filter-summary__chips">
        <!-- 每个筛选条件的标签 -->
        <FilterChip
          v-for="filter in visibleFilters"
          :key="filter.id"
          :filter="filter"
          :label="getFilterLabel(filter)"
          :value="filter.value"
          :type="getFilterType(filter)"
          :icon="filter.icon"
          :removable="removable"
          :clickable="clickable"
          :show-count="showFilterCount"
          :count="filter.count"
          @remove="$emit('filter-remove', filter)"
          @click="$emit('filter-click', filter)"
        />
      </div>
    </div>

    <!-- 筛选分组 -->
    <div v-if="showGroups && hasGroups" class="filter-summary__groups">
      <div
        v-for="group in filterGroups"
        :key="group.id"
        class="filter-summary__group"
      >
        <div class="filter-summary__group-header">
          <h5 class="filter-summary__group-title">{{ group.title }}</h5>
          <span v-if="group.selectedCount > 0" class="filter-summary__group-count">
            {{ group.selectedCount }}
          </span>
        </div>
        
        <div class="filter-summary__group-filters">
          <span
            v-for="filter in group.filters"
            :key="filter.id"
            class="filter-summary__group-filter"
          >
            {{ filter.label }}
          </span>
        </div>
      </div>
    </div>

    <!-- 筛选统计 -->
    <div v-if="showStats && hasStats" class="filter-summary__stats">
      <div class="filter-summary__stats-grid">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="filter-summary__stat"
        >
          <div class="filter-summary__stat-label">{{ stat.label }}</div>
          <div class="filter-summary__stat-value">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    <!-- 无筛选条件时显示 -->
    <div v-if="showEmptyState && !hasFilters" class="filter-summary__empty">
      <EmptyState
        :title="emptyTitle"
        :description="emptyDescription"
        icon="🔍"
        variant="compact"
        :action-text="actionText"
        @action="$emit('action')"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="filter-summary__loading">
      <LoadingSpinner size="small" text="更新筛选结果..." />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FilterChip from './FilterChip.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import EmptyState from '../common/EmptyState.vue'
import { formatTime } from '@/utils/date'

const props = defineProps({
  filters: {
    type: Array,
    default: () => []
  },
  resultCount: {
    type: Number,
    default: 0
  },
  originalCount: {
    type: Number,
    default: 0
  },
  showTitle: {
    type: Boolean,
    default: true
  },
  showResultCount: {
    type: Boolean,
    default: true
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  showGroups: {
    type: Boolean,
    default: false
  },
  showStats: {
    type: Boolean,
    default: false
  },
  showClearButton: {
    type: Boolean,
    default: true
  },
  showFilterCount: {
    type: Boolean,
    default: false
  },
  showEmptyState: {
    type: Boolean,
    default: false
  },
  removable: {
    type: Boolean,
    default: true
  },
  clickable: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  lastUpdated: {
    type: [String, Date],
    default: ''
  },
  emptyTitle: {
    type: String,
    default: '未应用筛选条件'
  },
  emptyDescription: {
    type: String,
    default: '添加筛选条件以缩小结果范围'
  },
  actionText: {
    type: String,
    default: '添加筛选'
  },
  maxVisibleFilters: {
    type: Number,
    default: 10
  },
  stats: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'clear',
  'filter-remove',
  'filter-click',
  'action'
])

// 计算属性
const summaryClasses = computed(() => ({
  'filter-summary': true,
  'filter-summary--compact': props.compact,
  'filter-summary--loading': props.loading,
  'filter-summary--has-filters': hasFilters.value,
  'filter-summary--empty': !hasFilters.value
}))

const hasFilters = computed(() => {
  return props.filters.length > 0
})

const hasGroups = computed(() => {
  return filterGroups.value.length > 0
})

const hasStats = computed(() => {
  return props.stats.length > 0
})

const visibleFilters = computed(() => {
  if (props.maxVisibleFilters && props.filters.length > props.maxVisibleFilters) {
    return props.filters.slice(0, props.maxVisibleFilters)
  }
  return props.filters
})

const filterGroups = computed(() => {
  const groups = {}
  
  props.filters.forEach(filter => {
    const groupId = filter.group || 'default'
    
    if (!groups[groupId]) {
      groups[groupId] = {
        id: groupId,
        title: filter.groupTitle || filter.group || '其他',
        filters: [],
        selectedCount: 0
      }
    }
    
    groups[groupId].filters.push(filter)
    groups[groupId].selectedCount++
  })
  
  return Object.values(groups)
})

// 方法
const getFilterLabel = (filter) => {
  return filter.label || filter.title || filter.id || '未知筛选'
}

const getFilterType = (filter) => {
  return filter.type || 'default'
}

const formatFilterValue = (value) => {
  if (value === null || value === undefined) return ''
  
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  
  if (typeof value === 'object') {
    if (value.min !== undefined && value.max !== undefined) {
      return `${value.min} - ${value.max}`
    }
    return JSON.stringify(value)
  }
  
  return String(value)
}

const clearAllFilters = () => {
  emit('clear')
}
</script>

<style scoped>
.filter-summary {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.filter-summary--compact {
  padding: var(--spacing-3);
  gap: var(--spacing-3);
}

.filter-summary--has-filters {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
}

.filter-summary__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-summary__title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-summary__updated {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.filter-summary__results {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.filter-summary__results-text {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.filter-summary__results-text strong {
  color: var(--color-primary);
  font-weight: 700;
}

.filter-summary__results-original {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.filter-summary__filters {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.filter-summary__filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-summary__filters-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
}

.filter-summary__clear {
  padding: var(--spacing-1) var(--spacing-3);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-summary__clear:hover:not(:disabled) {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.filter-summary__clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-summary__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.filter-summary__groups {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.filter-summary__group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.filter-summary__group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-summary__group-title {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.filter-summary__group-count {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: white;
  background-color: var(--color-primary);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  min-width: 20px;
  text-align: center;
}

.filter-summary__group-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.filter-summary__group-filter {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.filter-summary__stats {
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.filter-summary__stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--spacing-3);
}

.filter-summary__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-3);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.filter-summary__stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
}

.filter-summary__stat-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
}

.filter-summary__empty {
  padding: var(--spacing-6) 0;
}

.filter-summary__loading {
  padding: var(--spacing-4) 0;
  text-align: center;
}

/* 动画 */
.filter-summary {
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-summary__stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>