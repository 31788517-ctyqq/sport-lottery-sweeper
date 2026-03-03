<template>
  <div class="official-info-table-container">
    <el-table :data="tableData" stripe style="width: 100%" empty-text="暂无数据">
      <el-table-column prop="id" label="业务ID" width="180" />
      <el-table-column prop="zh" label="中文名称" min-width="160">
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
        min-width="180"
      >
        <template #default="{ row }">
          <div v-if="row.official_info && row.official_info[col]" class="url-cell">
            <el-link :href="row.official_info[col]" target="_blank" underline="never">
              {{ getDomain(row.official_info[col]) }}
            </el-link>
            <div class="status-indicator verified">已配置</div>
          </div>
          <span v-else class="not-set">未设置</span>
        </template>
      </el-table-column>

      <el-table-column label="验证状态" width="120">
        <template #default="{ row }">
          <div class="status-indicator" :class="row.official_info?.verified ? 'verified' : 'not-verified'">
            {{ row.official_info?.verified ? '已验证' : '未验证' }}
          </div>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="$emit('verify', entityType, row.id)">验证</el-button>
          <el-button size="small" @click="$emit('discover', entityType, row.id)">发现</el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="编辑官方信息" width="720px">
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
    }
  },
  data() {
    return {
      tableData: [],
      dialogVisible: false,
      currentRow: {
        official_info: {}
      }
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    formatArrayField(value) {
      if (Array.isArray(value)) return value.join(', ')
      return value || '-'
    },
    async fetchData() {
      try {
        const mappings = await getEntityMappings(this.entityType)
        this.tableData = Object.entries(mappings || {}).map(([id, data]) => ({ id, ...data }))
      } catch (error) {
        this.$message.error('获取官方信息数据失败')
      }
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
</style>
