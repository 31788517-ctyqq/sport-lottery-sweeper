<template>
  <div class="mapping-table-container">
    <div class="filter-bar">
      <el-input
        v-model="filters.search"
        clearable
        :placeholder="text.searchPlaceholder"
        style="width: 280px"
        @input="handleSearchInput"
        @clear="handleFilterChange"
      />

      <el-select
        v-model="filters.reviewStatus"
        clearable
        :placeholder="text.reviewStatusPlaceholder"
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
        :active-text="text.onlyConflictOn"
        :inactive-text="text.onlyConflictOff"
        @change="handleFilterChange"
      />

      <el-button size="small" type="primary" :loading="loading" @click="fetchData">{{ text.buttonRefresh }}</el-button>
      <el-button
        v-if="requestMode === 'all'"
        size="small"
        type="warning"
        plain
        @click="handleShowConflicts"
      >
        {{ text.buttonConflictList }}
      </el-button>
      <el-button v-else size="small" plain @click="handleShowAll">{{ text.buttonBackAll }}</el-button>

      <el-divider direction="vertical" />

      <el-tag type="info">{{ text.selectedCountPrefix }} {{ selectedCount }} {{ text.selectedCountSuffix }}</el-tag>
      <el-button
        size="small"
        type="success"
        plain
        :loading="batchActionLoading"
        :disabled="selectedCount === 0"
        @click="handleBatchReviewReviewed"
      >
        {{ text.buttonBatchMarkReviewed }}
      </el-button>
      <el-button
        size="small"
        type="warning"
        plain
        :disabled="selectedCount < 2"
        @click="handleBatchMergeSuggestion"
      >
        {{ text.buttonBatchMergeSuggestion }}
      </el-button>
    </div>

    <div class="summary-row" v-if="requestMode === 'conflicts' || filters.onlyConflicts">
      <el-tag type="danger">{{ text.conflictTotalPrefix }}{{ conflictSummary.total_conflicts }}</el-tag>
      <el-tag type="warning">{{ text.conflictPendingPrefix }}{{ conflictSummary.pending_conflicts }}</el-tag>
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
      <el-table-column prop="id" :label="text.colBizId" width="120" />
      <el-table-column prop="display_name" :label="text.colDisplayName" min-width="180" />
      <el-table-column prop="zh" :label="text.colZhName" min-width="180">
        <template #default="{ row }">
          <span>{{ formatArrayField(row.zh) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="en" :label="text.colEnName" min-width="180">
        <template #default="{ row }">
          <span>{{ formatArrayField(row.en) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="jp" :label="text.colJpName" min-width="180">
        <template #default="{ row }">
          <span>{{ formatArrayField(row.jp) }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="text.colSourceAliases" min-width="260">
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
      <el-table-column prop="alias_count" :label="text.colAliasCount" width="90" />
      <el-table-column :label="text.colConflictCount" width="90">
        <template #default="{ row }">
          <el-tag :type="(row.conflict_count || 0) > 0 ? 'danger' : 'success'">
            {{ row.conflict_count || 0 }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="text.colQualityScore" width="100">
        <template #default="{ row }">
          {{ formatQuality(row.quality_score) }}
        </template>
      </el-table-column>
      <el-table-column :label="text.colReviewStatus" width="110">
        <template #default="{ row }">
          <el-tag :type="reviewTagType(row.review_status)">
            {{ reviewStatusLabel(row.review_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="text.colActions" width="190" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button size="small" @click="handleEdit(row)">{{ text.actionEdit }}</el-button>
            <el-button
              v-if="(row.conflict_count || 0) > 0 || row.review_status === 'pending_review'"
              size="small"
              type="success"
              plain
              @click="handleMarkReviewed(row)"
            >
              {{ text.actionMarkReviewed }}
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

    <el-dialog v-model="dialogVisible" :title="text.dialogEditTitle" width="760px">
      <el-form :model="currentRow" label-width="110px">
        <el-form-item :label="text.fieldBizId">
          <el-input v-model="currentRow.id" disabled />
        </el-form-item>
        <el-form-item :label="text.fieldDisplayName">
          <el-input v-model="currentRow.display_name" />
        </el-form-item>
        <el-form-item :label="text.fieldZhName">
          <el-input v-model="currentRow.zh" :placeholder="text.inputMultipleByComma" />
        </el-form-item>
        <el-form-item :label="text.fieldEnName">
          <el-input v-model="currentRow.en" :placeholder="text.inputMultipleByComma" />
        </el-form-item>
        <el-form-item :label="text.fieldJpName">
          <el-input v-model="currentRow.jp" :placeholder="text.inputMultipleByComma" />
        </el-form-item>
        <el-form-item :label="text.fieldSourceAliases">
          <el-input
            v-model="currentRow.source_aliases_str"
            type="textarea"
            :rows="4"
            :placeholder="text.inputSourceAliasFormat"
          />
        </el-form-item>
        <el-form-item :label="text.fieldReviewStatus">
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
        <el-button @click="dialogVisible = false">{{ text.buttonCancel }}</el-button>
        <el-button type="primary" @click="handleSave">{{ text.buttonSave }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessageBox } from 'element-plus'
import { MAPPING_TABLE_TEXT } from '../constants/entityMappingText'
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
      text: MAPPING_TABLE_TEXT,
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
        { label: MAPPING_TABLE_TEXT.reviewAutoAccepted, value: 'auto_accepted' },
        { label: MAPPING_TABLE_TEXT.reviewPending, value: 'pending_review' },
        { label: MAPPING_TABLE_TEXT.reviewReviewed, value: 'reviewed' }
      ]
    }
  },
  computed: {
    selectedCount() {
      return Array.isArray(this.selectedRows) ? this.selectedRows.length : 0
    },
    tableEmptyText() {
      return this.tableErrorText || this.text.emptyTable
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
        auto_accepted: this.text.reviewAutoAccepted,
        pending_review: this.text.reviewPending,
        reviewed: this.text.reviewReviewed
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
        this.tableErrorText = this.text.toastLoadFailed
        this.$message.error(this.text.toastLoadFailed)
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
        this.$message.warning(this.text.toastNeedSelection)
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
          this.$message.error(this.text.toastBatchReviewFailed)
        }
      } catch (error) {
        this.$message.error(this.text.toastBatchReviewFailed)
      } finally {
        this.batchActionLoading = false
      }
    },
    async handleBatchMergeSuggestion() {
      if (this.selectedCount < 2) {
        this.$message.warning(this.text.toastNeedTwoSelections)
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
        this.$message.info(this.text.toastBatchMergeHint)
        return
      }

      await ElMessageBox.alert(suggestions.join('\n'), this.text.buttonBatchMergeSuggestion, {
        confirmButtonText: this.text.buttonAcknowledge,
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
        this.$message.success(this.text.toastReviewSuccess)
        await this.fetchData()
        this.$emit('update')
      } catch (error) {
        this.$message.error(this.text.toastReviewFailed)
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
        this.$message.success(this.text.toastSaveSuccess)
        this.dialogVisible = false
        await this.fetchData()
        this.$emit('update')
      } catch (error) {
        this.$message.error(this.text.toastSaveFailed)
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
