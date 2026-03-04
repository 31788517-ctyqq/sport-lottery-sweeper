<template>
  <div class="official-info-table-container">
    <div class="table-toolbar">
      <el-input
        v-model="filters.search"
        clearable
        placeholder="搜索ID/名称"
        style="width: 280px"
        @input="handleSearchInput"
      />
      <el-select
        v-model="filters.enrichStatus"
        clearable
        placeholder="补全状态"
        style="width: 160px"
        @change="handleStatusChange"
      >
        <el-option label="待处理" value="pending" />
        <el-option label="运行中" value="running" />
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-button size="small" @click="fetchData">刷新</el-button>
    </div>

    <el-table v-loading="loading" :data="tableData" stripe style="width: 100%" empty-text="暂无数据">
      <el-table-column prop="id" label="业务ID" width="100" />
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

      <el-table-column
        v-for="col in columns"
        :key="col"
        :label="getColumnLabel(col)"
        min-width="170"
      >
        <template #default="{ row }">
          <div v-if="row.official_info && row.official_info[col]" class="url-cell">
            <el-link :href="row.official_info[col]" target="_blank" underline="hover">
              {{ getDomain(row.official_info[col]) }}
            </el-link>
            <div class="status-indicator verified">已配置</div>
          </div>
          <span v-else class="not-set">未配置</span>
        </template>
      </el-table-column>

      <el-table-column label="验证状态" width="100">
        <template #default="{ row }">
          <div class="status-indicator" :class="row.official_info?.verified ? 'verified' : 'not-verified'">
            {{ row.official_info?.verified ? '已验证' : '未验证' }}
          </div>
        </template>
      </el-table-column>

      <el-table-column label="补全状态" width="100">
        <template #default="{ row }">
          <el-tag :type="enrichTagType(row.official_enrich_status)">
            {{ enrichStatusLabel(row.official_enrich_status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="补全来源" width="100">
        <template #default="{ row }">
          <el-tag :type="sourceTagType(row.official_source_tag)">
            {{ sourceTagLabel(row.official_source_tag) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="official_last_attempt_at" label="最近尝试" min-width="170">
        <template #default="{ row }">
          <span>{{ row.official_last_attempt_at || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="official_last_success_at" label="最近成功" min-width="170">
        <template #default="{ row }">
          <span>{{ row.official_last_success_at || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="最近补全" min-width="170">
        <template #default="{ row }">
          <span>{{ lastEnrichedValue(row) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$emit('verify', entityType, row.id)">验证</el-button>
          <el-button size="small" @click="$emit('discover', entityType, row.id)">发现</el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
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
        @current-change="fetchData"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" title="编辑官方信息" width="760px">
      <el-form :model="currentRow" label-width="120px">
        <el-form-item label="业务ID">
          <el-input v-model="currentRow.id" disabled />
        </el-form-item>
        <el-form-item v-for="col in columns" :key="col" :label="getColumnLabel(col)">
          <el-input v-model="currentRow.official_info[col]" :placeholder="`请输入${getColumnLabel(col)}链接`" />
        </el-form-item>
        <el-form-item label="验证状态">
          <el-switch v-model="currentRow.official_info.verified" active-text="已验证" inactive-text="未验证" />
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
import { getEntityMappings, updateOfficialInfo } from '@/api/entityMapping'

export default {
  name: 'EntityOfficialInfoTable',
  props: {
    entityType: {
      type: String,
      required: true
    },
    columns: {
      type: Array,
      default: () => []
    },
    onlyMissing: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: false,
      searchDebounceTimer: null,
      tableData: [],
      dialogVisible: false,
      currentRow: {
        official_info: {}
      },
      filters: {
        search: '',
        enrichStatus: ''
      },
      pager: {
        page: 1,
        size: 20,
        total: 0
      }
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
  watch: {
    onlyMissing() {
      this.pager.page = 1
      this.fetchData()
    }
  },
  methods: {
    formatArrayField(value) {
      if (Array.isArray(value)) return value.join(', ')
      return value || '-'
    },
    normalizePagedData(mappings) {
      if (mappings && Array.isArray(mappings.items)) return mappings
      if (mappings && typeof mappings === 'object') {
        const items = Object.entries(mappings || {}).map(([id, data]) => ({ id, ...data }))
        return {
          items,
          total: items.length
        }
      }
      return { items: [], total: 0 }
    },
    buildParams() {
      const params = {
        paged: true,
        page: this.pager.page,
        size: this.pager.size,
        only_missing_official: this.onlyMissing
      }
      if (this.filters.search.trim()) params.search = this.filters.search.trim()
      return params
    },
    async fetchData() {
      this.loading = true
      try {
        const mappings = await getEntityMappings(this.entityType, this.buildParams())
        const pageData = this.normalizePagedData(mappings)
        let items = pageData.items || []
        if (this.filters.enrichStatus) {
          items = items.filter((item) => item.official_enrich_status === this.filters.enrichStatus)
          this.pager.total = items.length
        } else {
          this.pager.total = Number(pageData.total || 0)
        }
        this.tableData = items
      } catch (error) {
        this.$message.error('获取官方信息数据失败')
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
    handleStatusChange() {
      this.pager.page = 1
      this.fetchData()
    },
    handleSizeChange(size) {
      this.pager.size = size
      this.pager.page = 1
      this.fetchData()
    },
    getColumnLabel(col) {
      const labels = {
        website: '官网',
        twitter: 'Twitter',
        facebook: 'Facebook',
        instagram: 'Instagram',
        weibo: '微博'
      }
      return labels[col] || col
    },
    getDomain(url) {
      if (!url) return ''
      try {
        return new URL(url).hostname.replace(/^www\./, '')
      } catch (error) {
        return url
      }
    },
    enrichStatusLabel(status) {
      const mapping = {
        pending: '待处理',
        running: '运行中',
        success: '成功',
        failed: '失败'
      }
      return mapping[status] || (status || '-')
    },
    enrichTagType(status) {
      if (status === 'success') return 'success'
      if (status === 'failed') return 'danger'
      if (status === 'running') return 'warning'
      return 'info'
    },
    sourceTagLabel(tag) {
      if (tag === 'manual') return '手工'
      if (tag === 'auto') return '自动'
      return '未标注'
    },
    sourceTagType(tag) {
      if (tag === 'manual') return 'warning'
      if (tag === 'auto') return 'success'
      return 'info'
    },
    lastEnrichedValue(row) {
      return row.official_last_enriched_at || row.official_last_success_at || '-'
    },
    handleEdit(row) {
      this.currentRow = JSON.parse(JSON.stringify(row))
      if (!this.currentRow.official_info) {
        this.currentRow.official_info = {}
      }
      this.columns.forEach((column) => {
        if (!this.currentRow.official_info[column]) {
          this.currentRow.official_info[column] = ''
        }
      })
      if (typeof this.currentRow.official_info.verified !== 'boolean') {
        this.currentRow.official_info.verified = false
      }
      this.dialogVisible = true
    },
    async handleSave() {
      try {
        await updateOfficialInfo(this.entityType, this.currentRow.id, this.currentRow.official_info)
        this.$message.success('保存成功')
        this.dialogVisible = false
        await this.fetchData()
        this.$emit('update', this.entityType, this.currentRow.id, this.currentRow.official_info)
      } catch (error) {
        this.$message.error('保存失败')
      }
    }
  }
}
</script>

<style scoped>
.official-info-table-container {
  margin-top: 20px;
}

.table-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.url-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-indicator {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.status-indicator.verified {
  background: #f0f9eb;
  color: #67c23a;
}

.status-indicator.not-verified {
  background: #fef0f0;
  color: #f56c6c;
}

.not-set {
  color: #909399;
  font-style: italic;
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}
</style>
