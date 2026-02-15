<template>
  <div class="execution-list">
    <div class="filter-toolbar">
      <el-row :gutter="10">
        <el-col :span="6">
          <el-input
            v-model="filters.taskName"
            placeholder="任务名称"
            clearable
            @clear="handleFilterChange"
            @change="handleFilterChange"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="filters.status"
            placeholder="状态筛选"
            clearable
            multiple
            @change="handleFilterChange"
          >
            <el-option label="待执行" value="PENDING" />
            <el-option label="执行中" value="RUNNING" />
            <el-option label="成功" value="SUCCESS" />
            <el-option label="失败" value="FAILED" />
            <el-option label="已取消" value="CANCELLED" />
          </el-select>
        </el-col>
        <el-col :span="12">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="filteredExecutions"
      v-loading="loading"
      style="width: 100%"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="id" label="ID" width="80" sortable="custom" />
      <el-table-column prop="taskName" label="任务名称" min-width="150" />
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small" effect="plain">
            {{ getStatusText(row.status) }}
          </el-tag>
          <div v-if="row.status === 'RUNNING'">
            <el-progress
              :percentage="row.progress"
              :color="getProgressColor(row.progress)"
              :show-text="false"
              :stroke-width="4"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="100">
        <template #default="{ row }">
          <span v-if="row.status === 'RUNNING'">{{ row.progress }}%</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="startedAt" label="开始时间" width="160" sortable="custom">
        <template #default="{ row }">
          {{ formatDateTime(row.startedAt) }}
        </template>
      </el-table-column>
      <el-table-column prop="endedAt" label="结束时间" width="160">
        <template #default="{ row }">
          {{ row.endedAt ? formatDateTime(row.endedAt) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="100" sortable="custom">
        <template #default="{ row }">
          {{ row.duration ? `${row.duration}s` : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="recordsProcessed" label="处理记录" width="100">
        <template #default="{ row }">
          {{ row.recordsProcessed || 0 }}
        </template>
      </el-table-column>
      <el-table-column prop="recordsFailed" label="失败记录" width="100">
        <template #default="{ row }">
          {{ row.recordsFailed || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            type="primary"
            @click="$emit('view-details', row.id)"
            :disabled="row.status === 'PENDING'"
          >
            日志
          </el-button>
          <el-button
            v-if="row.status === 'RUNNING'"
            size="small"
            type="danger"
            @click="$emit('cancel-execution', row.id)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalItems"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const props = defineProps({
  executions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-details', 'cancel-execution'])

const filters = ref({
  taskName: '',
  status: []
})

const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const sortBy = ref('startedAt')
const sortOrder = ref('desc')

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

const getStatusType = (status) => {
  const typeMap = {
    PENDING: 'info',
    RUNNING: 'primary',
    SUCCESS: 'success',
    FAILED: 'danger',
    CANCELLED: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    PENDING: '待执行',
    RUNNING: '执行中',
    SUCCESS: '成功',
    FAILED: '失败',
    CANCELLED: '已取消'
  }
  return textMap[status] || status
}

const getProgressColor = (percentage) => {
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 70) return '#E6A23C'
  return '#409EFF'
}

const filteredExecutions = computed(() => {
  let result = [...props.executions]

  if (filters.value.taskName) {
    const keyword = filters.value.taskName.toLowerCase()
    result = result.filter((item) => item.taskName && item.taskName.toLowerCase().includes(keyword))
  }

  if (filters.value.status.length > 0) {
    result = result.filter((item) => filters.value.status.includes(item.status))
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = dayjs(dateRange.value[0])
    const endDate = dayjs(dateRange.value[1])
    result = result.filter((item) => {
      if (!item.startedAt) return false
      const startedAt = dayjs(item.startedAt)
      return startedAt.isAfter(startDate.subtract(1, 'day')) && startedAt.isBefore(endDate.add(1, 'day'))
    })
  }

  result.sort((a, b) => {
    const aValue = a[sortBy.value]
    const bValue = b[sortBy.value]

    if (sortBy.value === 'startedAt' || sortBy.value === 'endedAt') {
      const aTime = aValue ? dayjs(aValue).valueOf() : 0
      const bTime = bValue ? dayjs(bValue).valueOf() : 0
      return sortOrder.value === 'desc' ? bTime - aTime : aTime - bTime
    }

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
    }

    return 0
  })

  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return result.slice(startIndex, endIndex)
})

const totalItems = computed(() => props.executions.length)

const handleFilterChange = () => {
  currentPage.value = 1
}

const handleDateChange = () => {
  currentPage.value = 1
}

const handleSortChange = ({ prop, order }) => {
  if (prop) {
    sortBy.value = prop
    sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  }
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}
</script>

<style scoped>
.execution-list {
  padding: 20px;
}

.filter-toolbar {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
