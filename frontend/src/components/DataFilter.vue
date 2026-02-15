<template>
  <div class="data-filter">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Filter /></el-icon>
            鏁版嵁绛涢€夊櫒
          </span>
          <div class="card-actions">
            <el-button 
              type="primary" 
              :icon="Refresh" 
              circle 
              size="small"
              @click="resetFilters"
              title="閲嶇疆绛涢€?
            />
            <el-button 
              :icon="settings.showAdvanced ? ArrowUp : ArrowDown" 
              circle 
              size="small"
              @click="toggleAdvanced"
              title="楂樼骇閫夐」"
            />
          </div>
        </div>
      </template>

      <!-- 鍩虹绛涢€?-->
      <div class="basic-filters">
        <el-row :gutter="16" class="filter-row">
          <!-- 鎼滅储妗?-->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-input
              v-model="filters.keyword"
              placeholder="鍏抽敭璇嶆悳绱?
              clearable
              @input="handleFilterChange"
              @clear="handleFilterChange"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>

          <!-- 鍒嗙被绛涢€?-->
          <el-col :xs="12" :sm="8" :md="6" :lg="4">
            <el-select
              v-model="filters.category"
              placeholder="鍒嗙被"
              clearable
              @change="handleFilterChange"
            >
              <el-option label="鍏ㄩ儴鍒嗙被" value="" />
              <el-option label="瓒崇悆璧涗簨" value="football" />
              <el-option label="绡悆璧涗簨" value="basketball" />
              <el-option label="缃戠悆璧涗簨" value="tennis" />
              <el-option label="鍏朵粬璧涗簨" value="other" />
            </el-select>
          </el-col>

          <!-- 鐘舵€佺瓫閫?-->
          <el-col :xs="12" :sm="8" :md="6" :lg="4">
            <el-select
              v-model="filters.status"
              placeholder="鐘舵€?
              clearable
              @change="handleFilterChange"
            >
              <el-option label="鍏ㄩ儴鐘舵€? value="" />
              <el-option label="娲昏穬" value="active" />
              <el-option label="鏆傚仠" value="paused" />
              <el-option label="瀹屾垚" value="completed" />
              <el-option label="寮傚父" value="error" />
            </el-select>
          </el-col>

          <!-- 鏃堕棿鑼冨洿 -->
          <el-col :xs="24" :sm="12" :md="12" :lg="6">
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="鑷?
              start-placeholder="寮€濮嬫棩鏈?
              end-placeholder="缁撴潫鏃ユ湡"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleFilterChange"
              style="width: 100%"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 楂樼骇绛涢€?-->
      <div v-if="settings.showAdvanced" class="advanced-filters">
        <el-divider content-position="left">楂樼骇绛涢€?/el-divider>
        
        <el-row :gutter="16" class="filter-row">
          <!-- 鏁板€艰寖鍥寸瓫閫?-->
          <el-col :xs="24" :sm="12" :md="8">
            <div class="range-filter">
              <label class="range-label">鏁板€艰寖鍥?/label>
              <div class="range-inputs">
                <el-input-number
                  v-model="filters.numberRange.min"
                  placeholder="鏈€灏忓€?
                  :min="0"
                  :max="filters.numberRange.max || 999999"
                  size="small"
                  @change="handleFilterChange"
                  style="width: 45%"
                />
                <span class="range-separator">-</span>
                <el-input-number
                  v-model="filters.numberRange.max"
                  placeholder="鏈€澶у€?
                  :min="filters.numberRange.min || 0"
                  :max="999999"
                  size="small"
                  @change="handleFilterChange"
                  style="width: 45%"
                />
              </div>
            </div>
          </el-col>

          <!-- 澶氶€夌瓫閫?-->
          <el-col :xs="24" :sm="12" :md="8">
            <div class="multi-select-filter">
              <label class="multi-label">鏍囩绛涢€?/label>
              <el-select
                v-model="filters.tags"
                multiple
                collapse-tags
                placeholder="閫夋嫨鏍囩"
                size="small"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option label="鐑棬" value="hot" />
                <el-option label="鎺ㄨ崘" value="recommended" />
                <el-option label="鏂板搧" value="new" />
                <el-option label="闄愭椂" value="limited" />
                <el-option label="鐗逛环" value="discount" />
              </el-select>
            </div>
          </el-col>

          <!-- 甯冨皵绛涢€?-->
          <el-col :xs="24" :sm="12" :md="8">
            <div class="boolean-filter">
              <label class="boolean-label">鐗规畩閫夐」</label>
              <div class="boolean-options">
                <el-checkbox v-model="filters.options.verified" @change="handleFilterChange">
                  宸查獙璇?                </el-checkbox>
                <el-checkbox v-model="filters.options.featured" @change="handleFilterChange">
                  绮鹃€?                </el-checkbox>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 鎺掑簭閫夐」 -->
        <el-row :gutter="16" class="sort-row">
          <el-col :xs="24" :sm="12">
            <div class="sort-filter">
              <label class="sort-label">鎺掑簭鏂瑰紡</label>
              <el-select
                v-model="filters.sortBy"
                placeholder="閫夋嫨鎺掑簭"
                size="small"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option label="榛樿鎺掑簭" value="default" />
                <el-option label="鍒涘缓鏃堕棿 鈫? value="created_asc" />
                <el-option label="鍒涘缓鏃堕棿 鈫? value="created_desc" />
                <el-option label="鏇存柊鏃堕棿 鈫? value="updated_asc" />
                <el-option label="鏇存柊鏃堕棿 鈫? value="updated_desc" />
                <el-option label="鍚嶇О A-Z" value="name_asc" />
                <el-option label="鍚嶇О Z-A" value="name_desc" />
              </el-select>
            </div>
          </el-col>
          
          <el-col :xs="12" :sm="6">
            <div class="limit-filter">
              <label class="limit-label">姣忛〉鏁伴噺</label>
              <el-select
                v-model="filters.limit"
                size="small"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option label="10鏉? :value="10" />
                <el-option label="20鏉? :value="20" />
                <el-option label="50鏉? :value="50" />
                <el-option label="100鏉? :value="100" />
              </el-select>
            </div>
          </el-col>
          
          <el-col :xs="12" :sm="6">
            <div class="view-mode-filter">
              <label class="view-label">瑙嗗浘妯″紡</label>
              <el-radio-group v-model="settings.viewMode" @change="handleViewModeChange">
                <el-radio-button value="table">琛ㄦ牸</el-radio-button>
                <el-radio-button value="card">鍗＄墖</el-radio-button>
                <el-radio-button value="list">鍒楄〃</el-radio-button>
              </el-radio-group>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 娲昏穬绛涢€夋潯浠舵樉绀?-->
      <div v-if="hasActiveFilters" class="active-filters">
        <el-divider content-position="left">褰撳墠绛涢€夋潯浠?/el-divider>
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
            type="link" 
            size="small" 
            @click="resetFilters"
            class="clear-all-btn"
          >
            娓呴櫎鍏ㄩ儴
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

// 鍝嶅簲寮忔暟鎹?const settings = reactive({
  showAdvanced: false,
  viewMode: 'table'
})

// 绛涢€夊櫒鏁版嵁
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

// 鍒濆鍖栫瓫閫夊櫒
const initializeFilters = () => {
  if (props.initialFilters && Object.keys(props.initialFilters).length > 0) {
    Object.assign(filters, props.initialFilters)
  }
}

// 璁＄畻灞炴€?const hasActiveFilters = computed(() => {
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
    tags.push({ key: 'keyword', label: '鍏抽敭璇?, value: filters.keyword })
  }
  
  if (filters.category) {
    const categoryMap = {
      football: '瓒崇悆璧涗簨',
      basketball: '绡悆璧涗簨',
      tennis: '缃戠悆璧涗簨',
      other: '鍏朵粬璧涗簨'
    }
    tags.push({ key: 'category', label: '鍒嗙被', value: categoryMap[filters.category] || filters.category })
  }
  
  if (filters.status) {
    const statusMap = {
      active: '娲昏穬',
      paused: '鏆傚仠',
      completed: '瀹屾垚',
      error: '寮傚父'
    }
    tags.push({ key: 'status', label: '鐘舵€?, value: statusMap[filters.status] || filters.status })
  }
  
  if (filters.dateRange.length > 0) {
    const [start, end] = filters.dateRange
    tags.push({ key: 'dateRange', label: '鏃堕棿鑼冨洿', value: `${start} ~ ${end}` })
  }
  
  if (filters.numberRange.min !== null || filters.numberRange.max !== null) {
    const min = filters.numberRange.min ?? '鏃?
    const max = filters.numberRange.max ?? '鏃?
    tags.push({ key: 'numberRange', label: '鏁板€艰寖鍥?, value: `${min} ~ ${max}` })
  }
  
  if (filters.tags.length > 0) {
    tags.push({ key: 'tags', label: '鏍囩', value: filters.tags.join(', ') })
  }
  
  if (filters.options.verified) {
    tags.push({ key: 'verified', label: '閫夐」', value: '宸查獙璇? })
  }
  
  if (filters.options.featured) {
    tags.push({ key: 'featured', label: '閫夐」', value: '绮鹃€? })
  }
  
  if (filters.sortBy !== 'default') {
    const sortMap = {
      created_asc: '鍒涘缓鏃堕棿 鈫?,
      created_desc: '鍒涘缓鏃堕棿 鈫?,
      updated_asc: '鏇存柊鏃堕棿 鈫?,
      updated_desc: '鏇存柊鏃堕棿 鈫?,
      name_asc: '鍚嶇О A-Z',
      name_desc: '鍚嶇О Z-A'
    }
    tags.push({ key: 'sortBy', label: '鎺掑簭', value: sortMap[filters.sortBy] || filters.sortBy })
  }
  
  return tags
})

// 鏂规硶
const handleFilterChange = () => {
  // 闃叉姈澶勭悊
  clearTimeout(handleFilterChange.timeout)
  handleFilterChange.timeout = setTimeout(() => {
    emit('filter-change', { ...filters })
  }, 300)
}

const resetFilters = () => {
  // 閲嶇疆鎵€鏈夌瓫閫夋潯浠?  Object.assign(filters, {
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
  
  ElMessage.success('绛涢€夋潯浠跺凡閲嶇疆')
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

// 鐩戝惉鍒濆鍊煎彉鍖?watch(() => props.initialFilters, () => {
  initializeFilters()
}, { deep: true })

// 鐩戝惉瑙嗗浘妯″紡鍚敤鐘舵€?watch(() => props.enableViewMode, (enabled) => {
  if (!enabled) {
    settings.viewMode = 'table'
  }
})

// 鍒濆鍖?initializeFilters()

// 鏆撮湶鏂规硶鍜屾暟鎹?defineExpose({
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
