<template>
  <el-card class="result-card">
    <template #header>
      <div class="card-header">
        <span>筛选结果</span>
        <div class="header-actions">
          <el-button @click="onExportResults('excel')">导出 Excel</el-button>
          <el-button @click="onExportResults('csv')">导出 CSV</el-button>
          <el-button @click="onToggleStats">
            {{ showStats ? '隐藏统计' : '显示统计' }}
          </el-button>
        </div>
      </div>
    </template>

    <el-table
      :data="pagedResults"
      style="width: 100%"
      v-loading="loading"
      @sort-change="onHandleSortChange"
    >
      <el-table-column prop="line_id" label="比赛ID" width="120" sortable>
        <template #default="{ row }">{{ formatMatchId(row.line_id) }}</template>
      </el-table-column>
      <el-table-column prop="home_team" label="主队" width="120">
        <template #default="{ row }">{{ displayValue(row.home_team) }}</template>
      </el-table-column>
      <el-table-column prop="score" label="比分/半场" width="120">
        <template #default="{ row }">{{ formatScoreHalf(row) }}</template>
      </el-table-column>
      <el-table-column prop="away_team" label="客队" width="120">
        <template #default="{ row }">{{ displayValue(row.away_team) }}</template>
      </el-table-column>
      <el-table-column prop="league" label="联赛" width="120">
        <template #default="{ row }">{{ displayValue(row.league) }}</template>
      </el-table-column>
      <el-table-column prop="match_time" label="比赛时间" width="170">
        <template #default="{ row }">{{ formatMatchTime(row.match_time) }}</template>
      </el-table-column>
      <el-table-column prop="power_diff" label="ΔP" width="80" sortable>
        <template #default="{ row }">{{ displayValue(row.power_diff) }}</template>
      </el-table-column>
      <el-table-column prop="delta_wp" label="ΔWP" width="100" sortable>
        <template #default="{ row }">{{ displayValue(row.delta_wp) }}</template>
      </el-table-column>
      <el-table-column prop="p_level" label="P级" width="80" sortable>
        <template #default="{ row }">
          <el-tag v-if="row.p_level" :type="getPLevelTagType(row.p_level)">P{{ row.p_level }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="power_home" label="主队实力" width="100" sortable>
        <template #default="{ row }">{{ displayValue(row.power_home) }}</template>
      </el-table-column>
      <el-table-column prop="power_away" label="客队实力" width="100" sortable>
        <template #default="{ row }">{{ displayValue(row.power_away) }}</template>
      </el-table-column>
      <el-table-column prop="win_pan_home" label="主队赢盘" width="100" sortable>
        <template #default="{ row }">{{ displayValue(row.win_pan_home) }}</template>
      </el-table-column>
      <el-table-column prop="win_pan_away" label="客队赢盘" width="100" sortable>
        <template #default="{ row }">{{ displayValue(row.win_pan_away) }}</template>
      </el-table-column>
      <el-table-column prop="home_feature" label="主队特征" width="120">
        <template #default="{ row }">{{ displayValue(row.home_feature) }}</template>
      </el-table-column>
      <el-table-column prop="away_feature" label="客队特征" width="120">
        <template #default="{ row }">{{ displayValue(row.away_feature) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="onOpenAnalysis(row)">分析</el-button>
        </template>
      </el-table-column>

      <template #empty>
        <div class="empty-state">
          没有符合条件的比赛场次
        </div>
      </template>
    </el-table>

    <el-pagination
      @size-change="onHandleSizeChange"
      @current-change="onHandleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[10, 20, 50, 100]"
      :page-size="pageSize"
      :total="totalResults"
      layout="slot, sizes, prev, pager, next, jumper"
      prev-text="上一页"
      next-text="下一页"
      style="margin-top: 20px; text-align: right;"
    >
      <span class="pagination-total">共 {{ totalResults }} 条</span>
    </el-pagination>
  </el-card>
</template>

<script>
import { defineComponent } from 'vue'
import {
  ElCard,
  ElTable,
  ElTableColumn,
  ElTag,
  ElPagination,
  ElButton
} from 'element-plus'

export default defineComponent({
  name: 'ResultsSection',
  components: {
    ElCard,
    ElTable,
    ElTableColumn,
    ElTag,
    ElPagination,
    ElButton
  },
  props: {
    pagedResults: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      required: true
    },
    showStats: {
      type: Boolean,
      required: true
    },
    totalResults: {
      type: Number,
      required: true
    },
    currentPage: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      required: true
    }
  },
  emits: [
    'toggleStats',
    'exportResults',
    'handleSortChange',
    'handleSizeChange',
    'handleCurrentChange',
    'openAnalysis'
  ],
  setup(props, { emit }) {
    const formatMatchId = (value) => {
      if (value === null || value === undefined || value === '') return '-'
      return String(value)
    }

    const formatMatchTime = (value) => {
      if (value === null || value === undefined || value === '') return '-'
      const raw = String(value).trim()
      if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw
      if (/^\d{4}-\d{2}-\d{2}[T\s]00:00:00(?:\.000)?(?:Z)?$/.test(raw)) {
        return raw.slice(0, 10)
      }
      const date = value instanceof Date ? value : new Date(value)
      if (Number.isNaN(date.getTime())) return String(value)
      const pad = (num) => String(num).padStart(2, '0')
      return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
    }

    const displayValue = (value) => {
      if (value === null || value === undefined || value === '') return '-'
      return value
    }

    const formatScoreHalf = (row) => {
      const full = displayValue(row?.score)
      const half = displayValue(row?.half_score)
      if (full === '-' && half === '-') return '-'
      return `${full}/${half}`
    }

    const getPLevelTagType = (level) => {
      switch (level) {
        case 1:
          return 'success'
        case 2:
          return 'primary'
        case 3:
          return 'warning'
        case 4:
          return 'danger'
        case 5:
          return 'info'
        default:
          return 'info'
      }
    }

    const onToggleStats = () => emit('toggleStats')
    const onExportResults = (format) => emit('exportResults', format)
    const onHandleSortChange = (params) => emit('handleSortChange', params)
    const onHandleSizeChange = (size) => emit('handleSizeChange', size)
    const onHandleCurrentChange = (page) => emit('handleCurrentChange', page)
    const onOpenAnalysis = (row) => emit('openAnalysis', row)

    return {
      formatMatchId,
      formatMatchTime,
      displayValue,
      formatScoreHalf,
      getPLevelTagType,
      onToggleStats,
      onExportResults,
      onHandleSortChange,
      onHandleSizeChange,
      onHandleCurrentChange,
      onOpenAnalysis
    }
  }
})
</script>

<style scoped>
.result-card {
  margin-bottom: 24px;
  border: 1px solid #d6d2cb;
  background: #fbfaf8;
  box-shadow: 0 14px 24px rgba(107, 103, 99, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.result-card .el-table {
  margin-bottom: 12px;
  border-radius: 0;
  overflow: visible;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #8b8680;
}

.pagination-total {
  margin-right: 12px;
  color: #6b6763;
  font-size: 13px;
}
</style>
