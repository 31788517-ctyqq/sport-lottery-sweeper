<template>
  <div class="data-filter">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Filter /></el-icon>
            数据筛选器
          </span>
          <div class="card-actions">
            <el-button 
              type="primary" 
              :icon="Refresh" 
              circle 
              size="small"
              @click="resetFilters"
              title="重置筛选"
            />
            <el-button 
              :icon="settings.showAdvanced ? ArrowUp : ArrowDown" 
              circle 
              size="small"
              @click="toggleAdvanced"
              title="高级选项"
            />
          </div>
        </div>
      </template>

      <!-- 基础筛选 -->
      <div class="basic-filters">
        <el-row :gutter="16" class="filter-row">
          <!-- 搜索框 -->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-input
              v-model="filters.keyword"
              placeholder="关键词搜索"
              clearable
              @input="handleFilterChange"
              @clear="handleFilterChange"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>

          <!-- 分类筛选 -->
          <el-col :xs="12" :sm="8" :md="6" :lg="4">
            <el-select
              v-model="filters.category"
              placeholder="分类"
              clearable
              @change="handleFilterChange"
            >
              <el-option label="全部分类" value="" />
              <el-option label="足球赛事" value="football" />
              <el-option label="篮球赛事" value="basketball" />
              <el-option label="网球赛事" value="tennis" />
              <el-option label="其他赛事" value="other" />
            </el-select>
          </el-col>

          <!-- 状态筛选 -->
          <el-col :xs="12" :sm="8" :md="6" :lg="4">
            <el-select
              v-model="filters.status"
              placeholder="状态"
              clearable
              @change="handleFilterChange"
            >
              <el-option label="全部状态" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="暂停" value="paused" />
              <el-option label="完成" value="completed" />
              <el-option label="异常" value="error" />
            </el-select>
          </el-col>

          <!-- 时间范围 -->
          <el-col :xs="24" :sm="12" :md="12" :lg="6">
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleFilterChange"
              style="width: 100%"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 高级筛选 -->
      <div v-if="settings.showAdvanced" class="advanced-filters">
        <el-divider content-position="left">高级筛选</el-divider>
        
        <el-row :gutter="16" class="filter-row">
          <!-- 数值范围筛选 -->
          <el-col :xs="24" :sm="12" :md="8">
            <div class="range-filter">
              <label class="range-label">数值范围</label>
              <div class="range-inputs">
                <el-input-number
                  v-model="filters.numberRange.min"
                  placeholder="最小值"
                  :min="0"
                  :max="filters.numberRange.max || 999999"
                  size="small"
                  @change="handleFilterChange"
                  style="width: 45%"
                />
                <span class="range-separator">-</span>
                <el-input-number
                  v-model="filters.numberRange.max"
                  placeholder="最大值"
                  :min="filters.numberRange.min || 0"
                  :max="999999"
                  size="small"
                  @change="handleFilterChange"
                  style="width: 45%"
                />
              </div>
            </div>
          </el-col>

          <!-- 多选筛选 -->
          <el-col :xs="24" :sm="12" :md="8">
            <div class="multi-select-filter">
              <label class="multi-label">标签筛选</label>
              <el-select
                v-model="filters.tags"
                multiple
                collapse-tags
                placeholder="选择标签"
                size="small"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option label="热门" value="hot" />
                <el-option label="推荐" value="recommended" />
                <el-option label="新品" value="new" />
                <el-option label="限时" value="limited" />
                <el-option label="特价" value="discount" />
              </el-select>
            </div>
          </el-col>

          <!-- 布尔筛选 -->
          <el-col :xs="24" :sm="12" :md="8">
            <div class="boolean-filter">
              <label class="boolean-label">特殊选项</label>
              <div class="boolean-options">
                <el-checkbox v-model="filters.options.verified" @change="handleFilterChange">
                  已验证
                </el-checkbox>
                <el-checkbox v-model="filters.options.featured" @change="handleFilterChange">
                  精选
                </el-checkbox>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 排序选项 -->
        <el-row :gutter="16" class="sort-row">
          <el-col :xs="24" :sm="12">
            <div class="sort-filter">
              <label class="sort-label">排序方式</label>
              <el-select
                v-model="filters.sortBy"
                placeholder="选择排序"
                size="small"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option label="默认排序" value="default" />
                <el-option label="创建时间 ↑" value="created_asc" />
                <el-option label="创建时间 ↓" value="created_desc" />
                <el-option label="更新时间 ↑" value="updated_asc" />
                <el-option label="更新时间 ↓" value="updated_desc" />
                <el-option label="名称 A-Z" value="name_asc" />
                <el-option label="名称 Z-A" value="name_desc" />
              </el-select>
            </div>
          </el-col>
          
          <el-col :xs="12" :sm="6">
            <div class="limit-filter">
              <label class="limit-label">每页数量</label>
              <el-select
                v-model="filters.limit"
                size="small"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option label="10条" :value="10" />
                <el-option label="20条" :value="20" />
                <el-option label="50条" :value="50" />
                <el-option label="100条" :value="100" />
              </el-select>
            </div>
          </el-col>
          
          <el-col :xs="12" :sm="6">
            <div class="view-mode-filter">
              <label class="view-label">视图模式</label>
              <el-radio-group v-model="settings.viewMode" @change="handleViewModeChange">
                <el-radio-button label="table">表格</el-radio-button>
                <el-radio-button label="card">卡片</el-radio-button>
                <el-radio-button label="list">列表</el-radio-button>
              </el-radio-group>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 活跃筛选条件显示 -->
      <div v-if="hasActiveFilters" class="active-filters">
        <el-divider content-position="left">当前筛选条件</el-divider>
        <div class="filter-tags">
          <el-tag
            v-for="filter in activeFilterTags"
            :key="filter.key"
            closable
            @close="removeFilter(filter.key)"
            class="filter-tag"
          >
            <strong>{{ filter.label }}:</strong> {{ filter.value }}
          </el-tag>
          
          <el-button 
            type="text" 
            size="small" 
            @click="resetFilters"
            class="clear-all-btn"
          >
            清除全部
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Filter, Refresh, Search, ArrowUp, ArrowDown 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  initialFilters: {
    type: Object,
    default: () => ({})
  },
  enableViewMode: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['filter-change', 'reset', 'view-mode-change'])

// 响应式数据
const settings = reactive({
  showAdvanced: false,
  viewMode: 'table'
})

// 筛选器数据
const filters = reactive({
  keyword: '',
  category: '',
  status: '',
  dateRange: [],
  numberRange: {
    min: null,
    max: null
  },
  tags: [],
  options: {
    verified: false,
    featured: false
  },
  sortBy: 'default',
  limit: 20
})

// 初始化筛选器
const initializeFilters = () => {
  if (props.initialFilters && Object.keys(props.initialFilters).length > 0) {
    Object.assign(filters, props.initialFilters)
  }
}

// 计算属性
const hasActiveFilters = computed(() => {
  return (
    filters.keyword ||
    filters.category ||
    filters.status ||
    filters.dateRange.length > 0 ||
    filters.numberRange.min !== null ||
    filters.numberRange.max !== null ||
    filters.tags.length > 0 ||
    filters.options.verified ||
    filters.options.featured ||
    filters.sortBy !== 'default'
  )
})

const activeFilterTags = computed(() => {
  const tags = []
  
  if (filters.keyword) {
    tags.push({ key: 'keyword', label: '关键词', value: filters.keyword })
  }
  
  if (filters.category) {
    const categoryMap = {
      football: '足球赛事',
      basketball: '篮球赛事',
      tennis: '网球赛事',
      other: '其他赛事'
    }
    tags.push({ key: 'category', label: '分类', value: categoryMap[filters.category] || filters.category })
  }
  
  if (filters.status) {
    const statusMap = {
      active: '活跃',
      paused: '暂停',
      completed: '完成',
      error: '异常'
    }
    tags.push({ key: 'status', label: '状态', value: statusMap[filters.status] || filters.status })
  }
  
  if (filters.dateRange.length > 0) {
    const [start, end] = filters.dateRange
    tags.push({ key: 'dateRange', label: '时间范围', value: `${start} ~ ${end}` })
  }
  
  if (filters.numberRange.min !== null || filters.numberRange.max !== null) {
    const min = filters.numberRange.min ?? '无'
    const max = filters.numberRange.max ?? '无'
    tags.push({ key: 'numberRange', label: '数值范围', value: `${min} ~ ${max}` })
  }
  
  if (filters.tags.length > 0) {
    tags.push({ key: 'tags', label: '标签', value: filters.tags.join(', ') })
  }
  
  if (filters.options.verified) {
    tags.push({ key: 'verified', label: '选项', value: '已验证' })
  }
  
  if (filters.options.featured) {
    tags.push({ key: 'featured', label: '选项', value: '精选' })
  }
  
  if (filters.sortBy !== 'default') {
    const sortMap = {
      created_asc: '创建时间 ↑',
      created_desc: '创建时间 ↓',
      updated_asc: '更新时间 ↑',
      updated_desc: '更新时间 ↓',
      name_asc: '名称 A-Z',
      name_desc: '名称 Z-A'
    }
    tags.push({ key: 'sortBy', label: '排序', value: sortMap[filters.sortBy] || filters.sortBy })
  }
  
  return tags
})

// 方法
const handleFilterChange = () => {
  // 防抖处理
  clearTimeout(handleFilterChange.timeout)
  handleFilterChange.timeout = setTimeout(() => {
    emit('filter-change', { ...filters })
  }, 300)
}

const resetFilters = () => {
  // 重置所有筛选条件
  Object.assign(filters, {
    keyword: '',
    category: '',
    status: '',
    dateRange: [],
    numberRange: {
      min: null,
      max: null
    },
    tags: [],
    options: {
      verified: false,
      featured: false
    },
    sortBy: 'default',
    limit: 20
  })
  
  settings.showAdvanced = false
  
  emit('filter-change', { ...filters })
  emit('reset')
  
  ElMessage.success('筛选条件已重置')
}

const removeFilter = (key) => {
  switch (key) {
    case 'keyword':
      filters.keyword = ''
      break
    case 'category':
      filters.category = ''
      break
    case 'status':
      filters.status = ''
      break
    case 'dateRange':
      filters.dateRange = []
      break
    case 'numberRange':
      filters.numberRange = { min: null, max: null }
      break
    case 'tags':
      filters.tags = []
      break
    case 'verified':
      filters.options.verified = false
      break
    case 'featured':
      filters.options.featured = false
      break
    case 'sortBy':
      filters.sortBy = 'default'
      break
  }
  
  handleFilterChange()
}

const toggleAdvanced = () => {
  settings.showAdvanced = !settings.showAdvanced
}

const handleViewModeChange = (mode) => {
  settings.viewMode = mode
  emit('view-mode-change', mode)
}

// 监听初始值变化
watch(() => props.initialFilters, () => {
  initializeFilters()
}, { deep: true })

// 监听视图模式启用状态
watch(() => props.enableViewMode, (enabled) => {
  if (!enabled) {
    settings.viewMode = 'table'
  }
})

// 初始化
initializeFilters()

// 暴露方法和数据
defineExpose({
  filters,
  settings,
  resetFilters,
  hasActiveFilters
})
</script>

<style scoped>
.data-filter {
  width: 100%;
}

.filter-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.basic-filters,
.advanced-filters {
  margin-bottom: 16px;
}

.filter-row {
  margin-bottom: 16px;
}

.range-filter,
.multi-select-filter,
.boolean-filter {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.range-label,
.multi-label,
.boolean-label,
.sort-label,
.limit-label,
.view-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: var(--el-text-color-placeholder);
}

.boolean-options {
  display: flex;
  gap: 16px;
}

.sort-row {
  align-items: end;
}

.view-mode-filter {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.active-filters {
  margin-top: 16px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
}

.filter-tag {
  margin: 0;
}

.clear-all-btn {
  margin-left: auto;
  color: var(--el-color-danger);
}

.clear-all-btn:hover {
  color: var(--el-color-danger-dark-2);
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: center;
  }
  
  .filter-row .el-col {
    margin-bottom: 12px;
  }
  
  .range-inputs {
    flex-direction: column;
    gap: 8px;
  }
  
  .range-inputs .el-input-number {
    width: 100% !important;
  }
  
  .boolean-options {
    flex-direction: column;
    gap: 8px;
  }
  
  .sort-row .el-col {
    margin-bottom: 12px;
  }
  
  .filter-tags {
    flex-direction: column;
    align-items: stretch;
  }
  
  .clear-all-btn {
    margin-left: 0;
    text-align: center;
  }
}
</style>