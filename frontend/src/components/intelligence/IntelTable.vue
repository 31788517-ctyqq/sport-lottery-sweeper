<template>
  <div :class="tableClasses">
    <!-- 表格标题和操作 -->
    <div v-if="showHeader" class="intel-table__header">
      <div class="intel-table__header-left">
        <h3 v-if="title" class="intel-table__title">{{ title }}</h3>
        <div v-if="description" class="intel-table__description">{{ description }}</div>
      </div>
      
      <div class="intel-table__header-right">
        <!-- 搜索框 -->
        <div v-if="searchable" class="intel-table__search">
          <BaseInput
            v-model="searchQuery"
            placeholder="搜索情报..."
            size="small"
            prepend-icon="search"
            clearable
            @clear="searchQuery = ''"
          />
        </div>
        
        <!-- 筛选按钮 -->
        <div v-if="showFilters" class="intel-table__filters">
          <button
            class="intel-table__filter-button"
            @click="showFilterPanel = !showFilterPanel"
            :class="{ 'intel-table__filter-button--active': hasActiveFilters }"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/>
            </svg>
            筛选
            <span v-if="hasActiveFilters" class="intel-table__filter-count">{{ activeFilterCount }}</span>
          </button>
        </div>
        
        <!-- 刷新按钮 -->
        <button
          v-if="showRefresh"
          class="intel-table__refresh"
          @click="refreshData"
          :disabled="loading"
          aria-label="刷新数据"
        >
          <LoadingSpinner v-if="loading" size="small" />
          <svg v-else width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
        </button>
        
        <!-- 更多操作 -->
        <div v-if="showMoreActions" class="intel-table__more-actions">
          <BaseButton
            variant="outline"
            size="small"
            icon-right="more-vert"
            @click="showActionMenu = !showActionMenu"
          >
            操作
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- 筛选面板 -->
    <transition name="slide-down">
      <div v-if="showFilterPanel && showFilters" class="intel-table__filter-panel">
        <div class="intel-table__filter-content">
          <!-- 权重筛选 -->
          <div v-if="filtersConfig.weight" class="intel-table__filter-group">
            <div class="intel-table__filter-label">权重</div>
            <div class="intel-table__filter-options">
              <label
                v-for="option in weightOptions"
                :key="option.value"
                class="intel-table__filter-option"
              >
                <input
                  type="checkbox"
                  :value="option.value"
                  v-model="filters.weight"
                  @change="applyFilters"
                />
                <span class="intel-table__filter-option-text">{{ option.label }}</span>
              </label>
            </div>
          </div>
          
          <!-- 类型筛选 -->
          <div v-if="filtersConfig.type" class="intel-table__filter-group">
            <div class="intel-table__filter-label">类型</div>
            <div class="intel-table__filter-options">
              <label
                v-for="option in typeOptions"
                :key="option.value"
                class="intel-table__filter-option"
              >
                <input
                  type="checkbox"
                  :value="option.value"
                  v-model="filters.type"
                  @change="applyFilters"
                />
                <span class="intel-table__filter-option-text">{{ option.label }}</span>
              </label>
            </div>
          </div>
          
          <!-- 来源筛选 -->
          <div v-if="filtersConfig.source" class="intel-table__filter-group">
            <div class="intel-table__filter-label">来源</div>
            <div class="intel-table__filter-options">
              <label
                v-for="option in sourceOptions"
                :key="option.value"
                class="intel-table__filter-option"
              >
                <input
                  type="checkbox"
                  :value="option.value"
                  v-model="filters.source"
                  @change="applyFilters"
                />
                <span class="intel-table__filter-option-text">{{ option.label }}</span>
              </label>
            </div>
          </div>
          
          <!-- 状态筛选 -->
          <div v-if="filtersConfig.status" class="intel-table__filter-group">
            <div class="intel-table__filter-label">状态</div>
            <div class="intel-table__filter-options">
              <label
                v-for="option in statusOptions"
                :key="option.value"
                class="intel-table__filter-option"
              >
                <input
                  type="checkbox"
                  :value="option.value"
                  v-model="filters.status"
                  @change="applyFilters"
                />
                <span class="intel-table__filter-option-text">{{ option.label }}</span>
              </label>
            </div>
          </div>
          
          <!-- 时间范围筛选 -->
          <div v-if="filtersConfig.dateRange" class="intel-table__filter-group">
            <div class="intel-table__filter-label">时间范围</div>
            <div class="intel-table__date-range">
              <BaseInput
                v-model="filters.startDate"
                type="date"
                placeholder="开始日期"
                size="small"
                @change="applyFilters"
              />
              <span class="intel-table__date-separator">至</span>
              <BaseInput
                v-model="filters.endDate"
                type="date"
                placeholder="结束日期"
                size="small"
                @change="applyFilters"
              />
            </div>
          </div>
          
          <!-- 筛选操作 -->
          <div class="intel-table__filter-actions">
            <BaseButton
              variant="outline"
              size="small"
              @click="clearFilters"
            >
              清空筛选
            </BaseButton>
            <BaseButton
              variant="primary"
              size="small"
              @click="showFilterPanel = false"
            >
              应用筛选
            </BaseButton>
          </div>
        </div>
      </div>
    </transition>

    <!-- 表格内容 -->
    <div class="intel-table__container">
      <table class="intel-table__table">
        <!-- 表头 -->
        <thead class="intel-table__thead">
          <tr class="intel-table__tr">
            <!-- 多选列 -->
            <th v-if="selectable" class="intel-table__th intel-table__th--select">
              <label class="intel-table__select-all">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                />
              </label>
            </th>
            
            <!-- 动态列 -->
            <th
              v-for="column in visibleColumns"
              :key="column.key"
              :class="['intel-table__th', `intel-table__th--${column.key}`, { 'intel-table__th--sortable': column.sortable }]"
              :style="{ width: column.width }"
              @click="column.sortable ? sortBy(column.key) : null"
            >
              <div class="intel-table__th-content">
                <span class="intel-table__th-text">{{ column.title }}</span>
                
                <!-- 排序指示器 -->
                <span v-if="column.sortable" class="intel-table__sort-indicator">
                  <svg
                    v-if="sortColumn === column.key && sortDirection === 'asc'"
                    width="12" height="12" viewBox="0 0 24 24"
                  >
                    <path fill="currentColor" d="M7 14l5-5 5 5z"/>
                  </svg>
                  <svg
                    v-else-if="sortColumn === column.key && sortDirection === 'desc'"
                    width="12" height="12" viewBox="0 0 24 24"
                  >
                    <path fill="currentColor" d="M7 10l5 5 5-5z"/>
                  </svg>
                  <svg v-else width="12" height="12" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M7 10l5 5 5-5z"/>
                  </svg>
                </span>
              </div>
            </th>
            
            <!-- 操作列 -->
            <th v-if="showActions" class="intel-table__th intel-table__th--actions">
              操作
            </th>
          </tr>
        </thead>

        <!-- 表格主体 -->
        <tbody class="intel-table__tbody">
          <!-- 加载状态 -->
          <tr v-if="loading && data.length === 0" class="intel-table__tr intel-table__tr--loading">
            <td :colspan="visibleColumns.length + (selectable ? 1 : 0) + (showActions ? 1 : 0)">
              <div class="intel-table__loading">
                <LoadingSpinner size="large" text="加载中..." />
              </div>
            </td>
          </tr>
          
          <!-- 无数据状态 -->
          <tr v-else-if="filteredData.length === 0" class="intel-table__tr intel-table__tr--empty">
            <td :colspan="visibleColumns.length + (selectable ? 1 : 0) + (showActions ? 1 : 0)">
              <EmptyState
                :title="emptyTitle"
                :description="emptyDescription"
                icon="📊"
                variant="compact"
              />
            </td>
          </tr>
          
          <!-- 数据行 -->
          <tr
            v-else
            v-for="item in paginatedData"
            :key="item.id"
            :class="[
              'intel-table__tr',
              'intel-table__tr--data',
              { 'intel-table__tr--selected': isSelected(item) },
              { 'intel-table__tr--clickable': clickableRows }
            ]"
            @click="clickableRows ? $emit('row-click', item) : null"
          >
            <!-- 多选单元格 -->
            <td v-if="selectable" class="intel-table__td intel-table__td--select">
              <label class="intel-table__select-item">
                <input
                  type="checkbox"
                  :checked="isSelected(item)"
                  @click.stop="toggleSelect(item)"
                />
              </label>
            </td>
            
            <!-- 动态数据单元格 -->
            <td
              v-for="column in visibleColumns"
              :key="column.key"
              :class="['intel-table__td', `intel-table__td--${column.key}`]"
            >
              <!-- 自定义单元格渲染 -->
              <slot
                :name="`cell-${column.key}`"
                :item="item"
                :value="getCellValue(item, column.key)"
                :column="column"
              >
                <!-- 默认单元格渲染 -->
                <div class="intel-table__cell-content">
                  <template v-if="column.type === 'weight'">
                    <IntelWeight
                      :weight="getCellValue(item, column.key)"
                      :size="column.weightSize || 'small'"
                      :show-label="column.showWeightLabel"
                    />
                  </template>
                  
                  <template v-else-if="column.type === 'source'">
                    <IntelSource
                      v-if="getCellValue(item, column.key)"
                      :source="getCellValue(item, column.key)"
                      :compact="true"
                      :show-credibility="column.showSourceCredibility"
                    />
                  </template>
                  
                  <template v-else-if="column.type === 'tags'">
                    <IntelTags
                      v-if="getCellValue(item, column.key)"
                      :tags="getCellValue(item, column.key)"
                      :limit="column.tagsLimit || 2"
                      :size="column.tagsSize || 'small'"
                      :compact="true"
                    />
                  </template>
                  
                  <template v-else-if="column.type === 'status'">
                    <span :class="['intel-table__status', `intel-table__status--${getCellValue(item, column.key)}`]">
                      {{ getStatusLabel(getCellValue(item, column.key)) }}
                    </span>
                  </template>
                  
                  <template v-else-if="column.type === 'date'">
                    <div class="intel-table__date">
                      {{ formatDate(getCellValue(item, column.key), column.dateFormat) }}
                    </div>
                  </template>
                  
                  <template v-else-if="column.type === 'boolean'">
                    <span :class="['intel-table__boolean', `intel-table__boolean--${getCellValue(item, column.key) ? 'true' : 'false'}`]">
                      {{ getCellValue(item, column.key) ? column.trueText || '是' : column.falseText || '否' }}
                    </span>
                  </template>
                  
                  <template v-else-if="column.type === 'actions'">
                    <div class="intel-table__cell-actions">
                      <slot name="cell-actions" :item="item">
                        <!-- 默认操作按钮 -->
                        <button
                          v-if="column.showViewButton"
                          class="intel-table__action-btn intel-table__action-btn--view"
                          @click.stop="$emit('view', item)"
                          title="查看详情"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24">
                            <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                          </svg>
                        </button>
                      </slot>
                    </div>
                  </template>
                  
                  <template v-else>
                    <div class="intel-table__text">
                      {{ getCellValue(item, column.key) }}
                    </div>
                  </template>
                </div>
              </slot>
            </td>
            
            <!-- 操作单元格 -->
            <td v-if="showActions" class="intel-table__td intel-table__td--actions">
              <div class="intel-table__actions">
                <slot name="actions" :item="item">
                  <!-- 默认操作按钮 -->
                  <button
                    class="intel-table__action-btn intel-table__action-btn--edit"
                    @click.stop="$emit('edit', item)"
                    title="编辑"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                    </svg>
                  </button>
                  
                  <button
                    class="intel-table__action-btn intel-table__action-btn--delete"
                    @click.stop="$emit('delete', item)"
                    title="删除"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                    </svg>
                  </button>
                </slot>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 表格底部 -->
    <div v-if="showFooter" class="intel-table__footer">
      <div class="intel-table__footer-left">
        <!-- 选中项信息 -->
        <div v-if="selectable && selectedItems.length > 0" class="intel-table__selection-info">
          已选中 {{ selectedItems.length }} 项
          <button
            class="intel-table__clear-selection"
            @click="clearSelection"
          >
            清空
          </button>
        </div>
        
        <!-- 分页信息 -->
        <div v-if="showPagination" class="intel-table__pagination-info">
          显示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredData.length) }} 条，共 {{ filteredData.length }} 条
        </div>
      </div>
      
      <div class="intel-table__footer-right">
        <!-- 分页控件 -->
        <div v-if="showPagination && filteredData.length > pageSize" class="intel-table__pagination">
          <button
            class="intel-table__pagination-btn intel-table__pagination-btn--prev"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/>
            </svg>
          </button>
          
          <div class="intel-table__pagination-pages">
            <button
              v-for="page in visiblePages"
              :key="page"
              :class="['intel-table__pagination-page', { 'intel-table__pagination-page--active': page === currentPage }]"
              @click="currentPage = page"
            >
              {{ page === '...' ? page : page }}
            </button>
          </div>
          
          <button
            class="intel-table__pagination-btn intel-table__pagination-btn--next"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
        
        <!-- 每页数量选择 -->
        <div v-if="showPageSize" class="intel-table__page-size">
          <label class="intel-table__page-size-label">每页显示:</label>
          <select
            v-model="pageSize"
            class="intel-table__page-size-select"
            @change="currentPage = 1"
          >
            <option v-for="size in pageSizeOptions" :key="size" :value="size">
              {{ size }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- 操作菜单 -->
    <div v-if="showActionMenu && showMoreActions" class="intel-table__action-menu">
      <div class="intel-table__action-menu-content">
        <button class="intel-table__action-menu-item" @click="$emit('export')">
          <svg width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
          导出数据
        </button>
        <button class="intel-table__action-menu-item" @click="$emit('print')">
          <svg width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
          </svg>
          打印
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseInput from '../common/BaseInput.vue'
import BaseButton from '../common/BaseButton.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import EmptyState from '../common/EmptyState.vue'
import IntelWeight from './IntelWeight.vue'
import IntelSource from './IntelSource.vue'
import IntelTags from './IntelTags.vue'
import { formatDate } from '@/utils/date'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  selectable: {
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
  showActions: {
    type: Boolean,
    default: true
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  showMoreActions: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  showPageSize: {
    type: Boolean,
    default: true
  },
  clickableRows: {
    type: Boolean,
    default: false
  },
  searchable: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyTitle: {
    type: String,
    default: '暂无数据'
  },
  emptyDescription: {
    type: String,
    default: '暂无情报数据，请尝试其他筛选条件'
  },
  pageSize: {
    type: Number,
    default: 10
  },
  pageSizeOptions: {
    type: Array,
    default: () => [10, 25, 50, 100]
  },
  filtersConfig: {
    type: Object,
    default: () => ({
      weight: true,
      type: true,
      source: true,
      status: true,
      dateRange: true
    })
  },
  defaultSort: {
    type: Object,
    default: () => ({
      column: 'publishedAt',
      direction: 'desc'
    })
  }
})

const emit = defineEmits([
  'row-click',
  'select',
  'select-all',
  'deselect-all',
  'sort',
  'filter',
  'refresh',
  'view',
  'edit',
  'delete',
  'export',
  'print'
])

// 响应式状态
const searchQuery = ref('')
const sortColumn = ref(props.defaultSort.column)
const sortDirection = ref(props.defaultSort.direction)
const selectedItems = ref([])
const currentPage = ref(1)
const pageSize = ref(props.pageSize)
const showFilterPanel = ref(false)
const showActionMenu = ref(false)

// 筛选状态
const filters = ref({
  weight: [],
  type: [],
  source: [],
  status: [],
  startDate: '',
  endDate: ''
})

// 计算属性
const tableClasses = computed(() => ({
  'intel-table': true,
  'intel-table--selectable': props.selectable,
  'intel-table--loading': props.loading,
  'intel-table--filtered': hasActiveFilters.value
}))

const visibleColumns = computed(() => {
  return props.columns.filter(column => !column.hidden)
})

const filteredData = computed(() => {
  let result = [...props.data]
  
  // 应用搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => {
      return Object.values(item).some(value => {
        if (typeof value === 'string') {
          return value.toLowerCase().includes(query)
        }
        return false
      })
    })
  }
  
  // 应用筛选
  if (hasActiveFilters.value) {
    result = result.filter(item => {
      // 权重筛选
      if (filters.value.weight.length > 0) {
        const weightLevel = getWeightLevel(item.weight)
        if (!filters.value.weight.includes(weightLevel)) return false
      }
      
      // 类型筛选
      if (filters.value.type.length > 0) {
        if (!filters.value.type.includes(item.type)) return false
      }
      
      // 来源筛选
      if (filters.value.source.length > 0) {
        const sourceId = item.source?.id || item.source
        if (!filters.value.source.includes(sourceId)) return false
      }
      
      // 状态筛选
      if (filters.value.status.length > 0) {
        if (!filters.value.status.includes(item.status)) return false
      }
      
      // 时间范围筛选
      if (filters.value.startDate || filters.value.endDate) {
        const itemDate = new Date(item.publishedAt)
        
        if (filters.value.startDate) {
          const startDate = new Date(filters.value.startDate)
          if (itemDate < startDate) return false
        }
        
        if (filters.value.endDate) {
          const endDate = new Date(filters.value.endDate)
          endDate.setHours(23, 59, 59, 999)
          if (itemDate > endDate) return false
        }
      }
      
      return true
    })
  }
  
  // 应用排序
  if (sortColumn.value) {
    result.sort((a, b) => {
      const aValue = getCellValue(a, sortColumn.value)
      const bValue = getCellValue(b, sortColumn.value)
      
      if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1
      if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1
      return 0
    })
  }
  
  return result
})

const paginatedData = computed(() => {
  if (!props.showPagination) return filteredData.value
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / pageSize.value)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  
  if (totalPages.value <= maxVisible) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage.value <= 3) {
      pages.push(1, 2, 3, 4, '...', totalPages.value)
    } else if (currentPage.value >= totalPages.value - 2) {
      pages.push(1, '...', totalPages.value - 3, totalPages.value - 2, totalPages.value - 1, totalPages.value)
    } else {
      pages.push(1, '...', currentPage.value - 1, currentPage.value, currentPage.value + 1, '...', totalPages.value)
    }
  }
  
  return pages
})

const isAllSelected = computed(() => {
  if (filteredData.value.length === 0) return false
  return filteredData.value.every(item => isSelected(item))
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(value => {
    if (Array.isArray(value)) return value.length > 0
    return value !== ''
  })
})

const activeFilterCount = computed(() => {
  let count = 0
  Object.values(filters.value).forEach(value => {
    if (Array.isArray(value)) {
      count += value.length
    } else if (value !== '') {
      count++
    }
  })
  return count
})

const weightOptions = computed(() => [
  { value: 'high', label: '高权重' },
  { value: 'medium', label: '中权重' },
  { value: 'low', label: '低权重' }
])

const typeOptions = computed(() => {
  const types = [...new Set(props.data.map(item => item.type))]
  return types.map(type => ({
    value: type,
    label: getTypeLabel(type)
  }))
})

const sourceOptions = computed(() => {
  const sources = props.data.map(item => item.source?.id || item.source).filter(Boolean)
  const uniqueSources = [...new Set(sources)]
  return uniqueSources.map(source => ({
    value: source,
    label: source
  }))
})

const statusOptions = computed(() => [
  { value: 'active', label: '有效' },
  { value: 'expired', label: '过期' },
  { value: 'pending', label: '待确认' },
  { value: 'confirmed', label: '已确认' }
])

// 方法
const getCellValue = (item, key) => {
  const keys = key.split('.')
  let value = item
  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = value[k]
    } else {
      return undefined
    }
  }
  return value
}

const getTypeLabel = (type) => {
  const typeMap = {
    news: '新闻',
    injury: '伤病',
    lineup: '阵容',
    suspension: '停赛',
    weather: '天气',
    referee: '裁判',
    venue: '场地',
    manager: '教练'
  }
  return typeMap[type] || type
}

const getStatusLabel = (status) => {
  const statusMap = {
    active: '有效',
    expired: '过期',
    pending: '待确认',
    confirmed: '已确认'
  }
  return statusMap[status] || status
}

const getWeightLevel = (weight) => {
  if (weight >= 8) return 'high'
  if (weight >= 5) return 'medium'
  if (weight >= 2) return 'low'
  return 'very-low'
}

const isSelected = (item) => {
  return selectedItems.value.some(selected => selected.id === item.id)
}

const toggleSelect = (item) => {
  if (isSelected(item)) {
    selectedItems.value = selectedItems.value.filter(selected => selected.id !== item.id)
  } else {
    selectedItems.value.push(item)
  }
  emit('select', selectedItems.value)
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedItems.value = []
    emit('deselect-all')
  } else {
    selectedItems.value = [...filteredData.value]
    emit('select-all', selectedItems.value)
  }
}

const clearSelection = () => {
  selectedItems.value = []
}

const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  emit('sort', { column: sortColumn.value, direction: sortDirection.value })
}

const applyFilters = () => {
  currentPage.value = 1
  emit('filter', { ...filters.value })
}

const clearFilters = () => {
  filters.value = {
    weight: [],
    type: [],
    source: [],
    status: [],
    startDate: '',
    endDate: ''
  }
  applyFilters()
}

const refreshData = () => {
  emit('refresh')
}

// 监听数据变化
watch(() => props.data, () => {
  currentPage.value = 1
  selectedItems.value = []
})

// 监听页面大小变化
watch(pageSize, () => {
  currentPage.value = 1
})
</script>