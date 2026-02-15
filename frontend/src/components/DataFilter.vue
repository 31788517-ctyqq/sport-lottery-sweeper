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
              title="重置筛选"
              @click="resetFilters"
            />
            <el-button
              :icon="settings.showAdvanced ? ArrowUp : ArrowDown"
              circle
              size="small"
              title="高级选项"
              @click="settings.showAdvanced = !settings.showAdvanced"
            />
          </div>
        </div>
      </template>

      <el-row :gutter="16" class="filter-row">
        <el-col :xs="24" :sm="12" :md="8">
          <el-input
            v-model="filters.keyword"
            placeholder="关键词搜索"
            clearable
            @input="emitFilterChange"
            @clear="emitFilterChange"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>

        <el-col :xs="12" :sm="6" :md="4">
          <el-select
            v-model="filters.category"
            placeholder="分类"
            clearable
            @change="emitFilterChange"
          >
            <el-option label="全部分类" value="" />
            <el-option label="足球赛事" value="football" />
            <el-option label="篮球赛事" value="basketball" />
            <el-option label="网球赛事" value="tennis" />
            <el-option label="其他赛事" value="other" />
          </el-select>
        </el-col>

        <el-col :xs="12" :sm="6" :md="4">
          <el-select
            v-model="filters.status"
            placeholder="状态"
            clearable
            @change="emitFilterChange"
          >
            <el-option label="全部状态" value="" />
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="paused" />
            <el-option label="完成" value="completed" />
            <el-option label="异常" value="error" />
          </el-select>
        </el-col>

        <el-col :xs="24" :sm="12" :md="8">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            @change="emitFilterChange"
          />
        </el-col>
      </el-row>

      <el-row v-if="settings.showAdvanced" :gutter="16" class="filter-row">
        <el-col :xs="12" :sm="6">
          <el-select v-model="filters.sortBy" placeholder="排序" @change="emitFilterChange">
            <el-option label="默认排序" value="default" />
            <el-option label="创建时间升序" value="created_asc" />
            <el-option label="创建时间降序" value="created_desc" />
            <el-option label="名称 A-Z" value="name_asc" />
            <el-option label="名称 Z-A" value="name_desc" />
          </el-select>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-select v-model="filters.limit" placeholder="每页数量" @change="emitFilterChange">
            <el-option label="10条" :value="10" />
            <el-option label="20条" :value="20" />
            <el-option label="50条" :value="50" />
            <el-option label="100条" :value="100" />
          </el-select>
        </el-col>

        <el-col v-if="enableViewMode" :xs="24" :sm="12">
          <el-radio-group v-model="settings.viewMode" @change="handleViewModeChange">
            <el-radio-button label="table">表格</el-radio-button>
            <el-radio-button label="card">卡片</el-radio-button>
            <el-radio-button label="list">列表</el-radio-button>
          </el-radio-group>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { ArrowDown, ArrowUp, Filter, Refresh, Search } from '@element-plus/icons-vue'

const props = defineProps({
  initialFilters: {
    type: Object,
    default: () => ({})
  },
  enableViewMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['filter-change', 'reset', 'view-mode-change'])

const createDefaultFilters = () => ({
  keyword: '',
  category: '',
  status: '',
  dateRange: [],
  sortBy: 'default',
  limit: 20
})

const filters = reactive({
  ...createDefaultFilters(),
  ...props.initialFilters
})

const settings = reactive({
  showAdvanced: false,
  viewMode: 'table'
})

const emitFilterChange = () => {
  emit('filter-change', { ...filters })
}

const resetFilters = () => {
  Object.assign(filters, createDefaultFilters(), props.initialFilters || {})
  settings.showAdvanced = false
  emit('filter-change', { ...filters })
  emit('reset')
}

const handleViewModeChange = (mode) => {
  emit('view-mode-change', mode)
}

watch(
  () => props.initialFilters,
  (value) => {
    Object.assign(filters, createDefaultFilters(), value || {})
  },
  { deep: true }
)

defineExpose({
  filters,
  settings,
  resetFilters
})
</script>

<style scoped>
.data-filter {
  width: 100%;
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
}

.card-actions {
  display: flex;
  gap: 8px;
}

.filter-row {
  margin-bottom: 12px;
}
</style>
