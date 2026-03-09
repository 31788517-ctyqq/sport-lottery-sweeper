<template>
  <div class="generic-table">
    <div class="table-header" v-if="showHeader || $slots.header">
      <slot name="header">
        <div class="header-content">
          <h3 v-if="title">{{ title }}</h3>
          <div class="header-actions">
            <el-button 
              v-if="showRefresh" 
              icon="Refresh" 
              @click="handleRefresh"
              :loading="loading"
            >
              刷新
            </el-button>
            <el-button 
              v-if="showAdd" 
              type="primary" 
              icon="Plus"
              @click="$emit('add')"
            >
              新增
            </el-button>
          </div>
        </div>
      </slot>
    </div>

    <el-table 
      :data="tableData" 
      :loading="loading"
      :border="true"
      :stripe="true"
      @selection-change="handleSelectionChange"
      @sort-change="$emit('sort-change', $event)"
      v-bind="$attrs"
    >
      <!-- 选择列 -->
      <el-table-column 
        v-if="showSelection" 
        type="selection" 
        width="55" 
      />

      <!-- 序号列 -->
      <el-table-column 
        v-if="showIndex" 
        type="index" 
        label="#" 
        width="60" 
        align="center"
      />

      <!-- 动态列 -->
      <el-table-column 
        v-for="column in columns" 
        :key="column.prop"
        v-bind="getColumnProps(column)"
      >
        <template #default="scope">
          <!-- 自定义渲染 -->
          <slot 
            :name="`column-${column.prop}`" 
            :row="scope.row" 
            :value="scope.row[column.prop]"
            :column="column"
          >
            <!-- 根据类型渲染 -->
            <template v-if="column.type === 'status'">
              <el-tag 
                :type="getStatusTagType(scope.row[column.prop], column.statusMap)" 
                disable-transitions
              >
                {{ getStatusText(scope.row[column.prop], column.statusMap) }}
              </el-tag>
            </template>
            
            <template v-else-if="column.type === 'date'">
              {{ formatDate(scope.row[column.prop]) }}
            </template>
            
            <template v-else-if="column.type === 'operation'">
              <div class="operation-buttons">
                <el-button 
                  v-for="btn in column.buttons" 
                  :key="btn.action"
                  :type="btn.type || 'primary'"
                  :icon="btn.icon"
                  :disabled="btn.disabled ? btn.disabled(scope.row) : false"
                  size="small"
                  @click="btn.handler(scope.row)"
                >
                  {{ btn.text }}
                </el-button>
              </div>
            </template>
            
            <template v-else>
              {{ scope.row[column.prop] }}
            </template>
          </slot>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="table-footer" v-if="pagination">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :layout="pagination.layout || 'total, sizes, prev, pager, next, jumper'"
        :total="pagination.total"
        @size-change="$emit('size-change', $event)"
        @current-change="$emit('current-change', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElTable, ElTableColumn, ElPagination, ElButton, ElTag } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'

// 定义组件属性
defineOptions({
  inheritAttrs: false
})

const props = defineProps({
  // 表格数据
  tableData: {
    type: Array,
    default: () => []
  },
  // 列配置
  columns: {
    type: Array,
    required: true
  },
  // 分页信息
  pagination: {
    type: Object,
    default: null
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 是否显示标题
  title: {
    type: String,
    default: ''
  },
  // 是否显示选择框
  showSelection: {
    type: Boolean,
    default: false
  },
  // 是否显示序号
  showIndex: {
    type: Boolean,
    default: false
  },
  // 是否显示头部
  showHeader: {
    type: Boolean,
    default: true
  },
  // 是否显示刷新按钮
  showRefresh: {
    type: Boolean,
    default: true
  },
  // 是否显示新增按钮
  showAdd: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits([
  'selection-change',
  'refresh',
  'add',
  'size-change',
  'current-change',
  'sort-change'
])

// 处理选择变化
const handleSelectionChange = (selection) => {
  emit('selection-change', selection)
}

// 处理刷新
const handleRefresh = () => {
  emit('refresh')
}

// 获取列属性
const getColumnProps = (column) => {
  // 如果是操作列，特殊处理
  if (column.type === 'operation') {
    return {
      fixed: column.fixed || 'right',
      width: column.width || 200,
      label: column.label || '操作',
      align: column.align || 'center'
    }
  }

  // 返回基本属性
  return {
    prop: column.prop,
    label: column.label,
    width: column.width,
    minWidth: column.minWidth,
    fixed: column.fixed,
    sortable: column.sortable,
    align: column.align || 'left',
    formatter: column.formatter
  }
}

// 获取状态标签类型
const getStatusTagType = (value, statusMap) => {
  if (!statusMap) return 'info'
  const statusItem = statusMap.find(item => item.value === value)
  return statusItem ? statusItem.type || 'info' : 'info'
}

// 获取状态文本
const getStatusText = (value, statusMap) => {
  if (!statusMap) return value
  const statusItem = statusMap.find(item => item.value === value)
  return statusItem ? statusItem.label : value
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.generic-table {
  padding: 20px;
}

.table-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.operation-buttons {
  display: flex;
  gap: 8px;
}

.table-footer {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>