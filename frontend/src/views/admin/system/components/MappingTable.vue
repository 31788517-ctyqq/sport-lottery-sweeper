<template>
  <div class="mapping-table-container">
    <el-table :data="tableData" stripe style="width: 100%" empty-text="暂无数据">
      <el-table-column prop="id" label="业务ID" width="180" />
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
      <el-table-column label="来源别名" min-width="240">
        <template #default="{ row }">
          <div v-if="row.source_aliases">
            <div
              v-for="(aliases, source) in row.source_aliases"
              :key="source"
              class="source-alias"
            >
              <strong>{{ source }}:</strong>
              {{ Array.isArray(aliases) ? aliases.join(', ') : aliases }}
            </div>
          </div>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="编辑映射" width="680px">
      <el-form :model="currentRow" label-width="100px">
        <el-form-item label="业务ID">
          <el-input v-model="currentRow.id" disabled />
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
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getEntityMappings, updateEntityMapping } from '@/api/entityMapping'

const parseCsvField = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value !== 'string') return []
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
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
      tableData: [],
      dialogVisible: false,
      currentRow: {}
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
        this.$message.error('获取映射数据失败')
      }
    },
    buildAliasString(sourceAliases) {
      if (!sourceAliases || typeof sourceAliases !== 'object') return ''
      return Object.entries(sourceAliases)
        .map(([source, aliases]) => `${source}:${Array.isArray(aliases) ? aliases.join(',') : aliases}`)
        .join(';')
    },
    handleEdit(row) {
      this.currentRow = JSON.parse(JSON.stringify(row))
      this.currentRow.zh = this.formatArrayField(this.currentRow.zh)
      this.currentRow.en = this.formatArrayField(this.currentRow.en)
      this.currentRow.jp = this.formatArrayField(this.currentRow.jp)
      this.currentRow.source_aliases_str = this.buildAliasString(this.currentRow.source_aliases)
      this.dialogVisible = true
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
    async handleSave() {
      const updateData = {
        ...this.currentRow,
        zh: parseCsvField(this.currentRow.zh),
        en: parseCsvField(this.currentRow.en),
        jp: parseCsvField(this.currentRow.jp),
        source_aliases: this.parseSourceAliases()
      }

      delete updateData.id
      delete updateData.source_aliases_str

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

.source-alias {
  margin-bottom: 4px;
  font-size: 12px;
}
</style>
