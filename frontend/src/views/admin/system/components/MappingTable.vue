<template>
  <div class="mapping-table-container">
    <div class="filter-bar">
      <el-input
        v-model="filters.search"
        clearable
        placeholder="搜索名称/别名/ID"
        style="width: 280px"
        @input="handleSearchInput"
        @clear="handleFilterChange"
      />

      <el-select
        v-model="filters.reviewStatus"
        clearable
        placeholder="审核状态"
        style="width: 160px"
        @change="handleFilterChange"
      >
        <el-option
          v-for="option in reviewStatusOptions"
          :key="option.value"
          :label="option.label"
          :value="option.value"
        />
      </el-select>

      <el-switch
        v-model="filters.onlyConflicts"
        active-text="仅看冲突"
        inactive-text="全部"
        @change="handleFilterChange"
      />

      <el-button size="small" type="primary" :loading="loading" @click="fetchData">刷新</el-button>
      <el-button
        v-if="requestMode === 'all'"
        size="small"
        type="warning"
        plain
        @click="handleShowConflicts"
      >
        冲突列表
      </el-button>
      <el-button v-else size="small" plain @click="handleShowAll">返回全部</el-button>

      <el-divider direction="vertical" />

      <el-tag type="info">已选 {{ selectedCount }} 项</el-tag>
      <el-button
        size="small"
        type="success"
        plain
        :loading="batchActionLoading"
        :disabled="selectedCount === 0"
        @click="handleBatchReviewReviewed"
      >
        批量标记已审
      </el-button>
      <el-button
        size="small"
        type="warning"
        plain
        :disabled="selectedCount < 2"
        @click="handleBatchMergeSuggestion"
      >
        批量合并建议
      </el-button>
    </div>

    <div class="summary-row" v-if="requestMode === 'conflicts' || filters.onlyConflicts">
      <el-tag type="danger">冲突总数：{{ conflictSummary.total_conflicts }}</el-tag>
      <el-tag type="warning">待审核：{{ conflictSummary.pending_conflicts }}</el-tag>
    </div>

    <el-table
      v-loading="loading"
      :data="tableData"
      stripe
      style="width: 100%"
      :empty-text="tableEmptyText"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="48" />
      <el-table-column prop="id" label="业务ID" width="120" />
      <el-table-column prop="display_name" label="显示名称" min-width="180" />
      <el-table-column prop="zh" label="中文名称" min-width="180">
        <template #default="{ row }">
          <span>{{ formatArrayField(row.zh) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="en" label="英文名称" min-width="180">
        <template #default="{ row }">
          <span>{{ formatArrayField(row.en) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="jp" label="日文名称" min-width="180">
        <template #default="{ row }">
          <span>{{ formatArrayField(row.jp) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="来源别名" min-width="260">
        <template #default="{ row }">
          <div v-if="row.source_aliases">
            <div v-for="(aliases, source) in row.source_aliases" :key="source" class="source-alias">
              <strong>{{ source }}:</strong>
              {{ Array.isArray(aliases) ? aliases.join(', ') : aliases }}
            </div>
          </div>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="alias_count" label="别名数" width="90" />
      <el-table-column label="冲突数" width="90">
        <template #default="{ row }">
          <el-tag :type="(row.conflict_count || 0) > 0 ? 'danger' : 'success'">
            {{ row.conflict_count || 0 }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="质量分" width="100">
        <template #default="{ row }">
          {{ formatQuality(row.quality_score) }}
        </template>
      </el-table-column>
      <el-table-column label="审核状态" width="110">
        <template #default="{ row }">
          <el-tag :type="reviewTagType(row.review_status)">
            {{ reviewStatusLabel(row.review_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="190" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              v-if="(row.conflict_count || 0) > 0 || row.review_status === 'pending_review'"
              size="small"
              type="success"
              plain
              @click="handleMarkReviewed(row)"
            >
              标记已审
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="pager.page"
        v-model:page-size="pager.size"
        :total="pager.total"
        :page-sizes="[10, 20, 50, 100]"
        background
        layout="total, sizes, prev, pager, next"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" title="编辑映射" width="760px">
      <el-form :model="currentRow" label-width="110px">
        <el-form-item label="业务ID">
          <el-input v-model="currentRow.id" disabled />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="currentRow.display_name" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="currentRow.zh" placeholder="多个名称用英文逗号分隔" />
        </el-form-item>
        <el-form-item label="英文名称">
          <el-input v-model="currentRow.en" placeholder="多个名称用英文逗号分隔" />
        </el-form-item>
        <el-form-item label="日文名称">
          <el-input v-model="currentRow.jp" placeholder="多个名称用英文逗号分隔" />
        </el-form-item>
        <el-form-item label="来源别名">
          <el-input
            v-model="currentRow.source_aliases_str"
            type="textarea"
            :rows="4"
            placeholder="格式: source_a:a1,a2;source_b:b1,b2"
          />
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="currentRow.review_status" style="width: 220px">
            <el-option
              v-for="option in reviewStatusOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessageBox } from 'element-plus'
import {
  getEntityMappings,
  getEntityMappingConflicts,
  reviewEntityMapping,
  updateEntityMapping
} from '@/api/entityMapping'

const parseCsvField = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value !== 'string') return []
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

const normalizeText = (value) =>
  String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[\s\-_/]+/g, '')

const getRowPrimaryName = (row) => {
  if (row.display_name) return row.display_name
  const zh = Array.isArray(row.zh) && row.zh.length ? row.zh[0] : ''
  if (zh) return zh
  const en = Array.isArray(row.en) && row.en.length ? row.en[0] : ''
  if (en) return en
  return row.id || '-'
}

export default {
  name: 'MappingTable',
  props: {
    entityType: {
      type: String,
      required: true
    },
    columns: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      loading: false,
      requestMode: 'all',
      tableData: [],
      dialogVisible: false,
      currentRow: {},
      searchDebounceTimer: null,
      selectedRows: [],
      batchActionLoading: false,
      tableErrorText: '',
      conflictSummary: {
        total_conflicts: 0,
        pending_conflicts: 0
      },
      filters: {
        search: '',
        reviewStatus: '',
        onlyConflicts: false
      },
      pager: {
        page: 1,
        size: 20,
        total: 0
      },
      reviewStatusOptions: [
        { label: '自动通过', value: 'auto_accepted' },
        { label: '待审核', value: 'pending_review' },
        { label: '已审核', value: 'reviewed' }
      ]
    }
  },
  computed: {
    selectedCount() {
      return Array.isArray(this.selectedRows) ? this.selectedRows.length : 0
    },
    tableEmptyText() {
      return this.tableErrorText || '暂无映射数据'
    }
  },
  watch: {
    entityType() {
      this.resetAndReload()
    }
  },
  mounted() {
    this.fetchData()
  },
  beforeUnmount() {
    if (this.searchDebounceTimer) {
      window.clearTimeout(this.searchDebounceTimer)
      this.searchDebounceTimer = null
    }
  },
  methods: {
    resetAndReload() {
      this.requestMode = 'all'
      this.filters.onlyConflicts = false
      this.selectedRows = []
      this.tableErrorText = ''
      this.conflictSummary = {
        total_conflicts: 0,
        pending_conflicts: 0
      }
      this.pager.page = 1
      this.fetchData()
    },
    formatArrayField(value) {
      if (Array.isArray(value)) return value.join(', ')
      return value || '-'
    },
    formatQuality(value) {
      const score = Number(value)
      if (Number.isNaN(score)) return '0.00'
      return score.toFixed(2)
    },
    reviewStatusLabel(value) {
      const mapping = {
        auto_accepted: '自动通过',
        pending_review: '待审核',
        reviewed: '已审核'
      }
      return mapping[value] || value || '-'
    },
    reviewTagType(value) {
      if (value === 'pending_review') return 'warning'
      if (value === 'reviewed') return 'success'
      return 'info'
    },
    buildQueryParams() {
      const params = {
        page: this.pager.page,
        size: this.pager.size,
        paged: true
      }
      if (this.filters.search) params.search = this.filters.search.trim()
      if (this.filters.reviewStatus) params.review_status = this.filters.reviewStatus
      if (this.filters.onlyConflicts || this.requestMode === 'conflicts') {
        params.only_conflicts = true
      }
      return params
    },
    normalizePagedResponse(response) {
      if (response && Array.isArray(response.items)) {
        return response
      }
      if (response && typeof response === 'object' && !Array.isArray(response)) {
        const items = Object.entries(response).map(([id, data]) => ({ id, ...data }))
        return {
          items,
          total: items.length,
          page: 1,
          size: items.length,
          has_more: false
        }
      }
      return {
        items: [],
        total: 0,
        page: 1,
        size: this.pager.size,
        has_more: false
      }
    },
    async fetchData() {
      this.loading = true
      this.tableErrorText = ''
      try {
        const params = this.buildQueryParams()
        const response =
          this.requestMode === 'conflicts'
            ? await getEntityMappingConflicts(this.entityType, params)
            : await getEntityMappings(this.entityType, params)
        const pageData = this.normalizePagedResponse(response)
        this.tableData = pageData.items || []
        this.pager.total = Number(pageData.total || 0)

        const summary = response?.summary
        if (summary && typeof summary === 'object') {
          this.conflictSummary = {
            total_conflicts: Number(summary.total_conflicts || 0),
            pending_conflicts: Number(summary.pending_conflicts || 0)
          }
        } else {
          this.conflictSummary = {
            total_conflicts: Number(response?.total || 0),
            pending_conflicts: Number(response?.pending_total || 0)
          }
        }
      } catch (error) {
        this.tableData = []
        this.pager.total = 0
        this.tableErrorText = '加载失败，请稍后重试'
        this.$message.error('获取映射数据失败')
      } finally {
        this.loading = false
      }
    },
    handleSearchInput() {
      if (this.searchDebounceTimer) {
        window.clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = window.setTimeout(() => {
        this.pager.page = 1
        this.fetchData()
      }, 300)
    },
    handleFilterChange() {
      this.pager.page = 1
      this.fetchData()
    },
    handlePageChange(page) {
      this.pager.page = page
      this.fetchData()
    },
    handleSizeChange(size) {
      this.pager.size = size
      this.pager.page = 1
      this.fetchData()
    },
    handleShowConflicts() {
      this.requestMode = 'conflicts'
      this.filters.onlyConflicts = true
      this.pager.page = 1
      this.fetchData()
    },
    handleShowAll() {
      this.requestMode = 'all'
      this.filters.onlyConflicts = false
      this.pager.page = 1
      this.fetchData()
    },
    handleSelectionChange(rows) {
      this.selectedRows = Array.isArray(rows) ? rows : []
    },
    async handleBatchReviewReviewed() {
      if (!this.selectedCount) {
        this.$message.warning('请先选择要操作的记录')
        return
      }
      this.batchActionLoading = true
      try {
        const jobs = this.selectedRows.map((row) =>
          reviewEntityMapping(this.entityType, row.id, { review_status: 'reviewed' })
        )
        const results = await Promise.allSettled(jobs)
        const successCount = results.filter((item) => item.status === 'fulfilled').length
        const failCount = results.length - successCount

        if (successCount > 0) {
          this.$message.success(`批量审核完成：成功 ${successCount} 条${failCount ? `，失败 ${failCount} 条` : ''}`)
          await this.fetchData()
          this.$emit('update')
        } else {
          this.$message.error('批量审核失败，请重试')
        }
      } catch (error) {
        this.$message.error('批量审核失败，请重试')
      } finally {
        this.batchActionLoading = false
      }
    },
    async handleBatchMergeSuggestion() {
      if (this.selectedCount < 2) {
        this.$message.warning('至少选择 2 条记录后再生成建议')
        return
      }

      const groups = {}
      this.selectedRows.forEach((row) => {
        const key = normalizeText(getRowPrimaryName(row))
        if (!key) return
        if (!groups[key]) groups[key] = []
        groups[key].push(row)
      })

      const suggestions = Object.values(groups)
        .filter((group) => group.length > 1)
        .map((group) => {
          const ids = group.map((item) => item.id).join(', ')
          const name = getRowPrimaryName(group[0])
          return `【${name}】候选记录：${ids}`
        })

      if (!suggestions.length) {
        this.$message.info('未发现明显重复项，建议按来源别名进一步人工核对')
        return
      }

      await ElMessageBox.alert(suggestions.join('\n'), '批量合并建议', {
        confirmButtonText: '我知道了',
        type: 'warning'
      })
    },
    buildAliasString(sourceAliases) {
      if (!sourceAliases || typeof sourceAliases !== 'object') return ''
      return Object.entries(sourceAliases)
        .map(([source, aliases]) => `${source}:${Array.isArray(aliases) ? aliases.join(',') : aliases}`)
        .join(';')
    },
    parseSourceAliases() {
      const raw = this.currentRow.source_aliases_str
      if (!raw || typeof raw !== 'string') return {}
      const parsed = {}
      raw
        .split(';')
        .map((item) => item.trim())
        .filter(Boolean)
        .forEach((item) => {
          const [source, aliases] = item.split(':')
          if (source && aliases) {
            parsed[source.trim()] = aliases
              .split(',')
              .map((alias) => alias.trim())
              .filter(Boolean)
          }
        })
      return parsed
    },
    handleEdit(row) {
      this.currentRow = JSON.parse(JSON.stringify(row))
      this.currentRow.zh = this.formatArrayField(this.currentRow.zh)
      this.currentRow.en = this.formatArrayField(this.currentRow.en)
      this.currentRow.jp = this.formatArrayField(this.currentRow.jp)
      this.currentRow.source_aliases_str = this.buildAliasString(this.currentRow.source_aliases)
      this.currentRow.review_status = this.currentRow.review_status || 'auto_accepted'
      this.dialogVisible = true
    },
    async handleMarkReviewed(row) {
      try {
        await reviewEntityMapping(this.entityType, row.id, { review_status: 'reviewed' })
        this.$message.success('已标记为已审核')
        await this.fetchData()
        this.$emit('update')
      } catch (error) {
        this.$message.error('标记审核失败')
      }
    },
    async handleSave() {
      const updateData = {
        display_name: this.currentRow.display_name,
        zh: parseCsvField(this.currentRow.zh),
        en: parseCsvField(this.currentRow.en),
        jp: parseCsvField(this.currentRow.jp),
        source_aliases: this.parseSourceAliases(),
        review_status: this.currentRow.review_status || 'reviewed'
      }

      try {
        await updateEntityMapping(this.entityType, this.currentRow.id, updateData)
        this.$message.success('保存成功')
        this.dialogVisible = false
        await this.fetchData()
        this.$emit('update')
      } catch (error) {
        this.$message.error('保存失败')
      }
    }
  }
}
</script>

<style scoped>
.mapping-table-container {
  margin-top: 20px;
}

.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}

.summary-row {
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
}

.source-alias {
  margin-bottom: 4px;
  font-size: 12px;
  line-height: 1.4;
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
