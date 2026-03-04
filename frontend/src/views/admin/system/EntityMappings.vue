<template>
  <div class="entity-mappings">
    <el-card class="sync-card" shadow="never">
      <div class="sync-meta">
        <span>同步状态：{{ syncStatusText }}</span>
        <span>最近启动：{{ syncStatus?.last_started_at || '-' }}</span>
        <span>最近完成：{{ syncStatus?.last_finished_at || '-' }}</span>
        <span>下次执行：{{ syncStatus?.next_sync_at || '-' }}</span>
      </div>
      <div class="sync-actions">
        <el-button size="small" :loading="syncTriggerLoading" type="primary" @click="handleTriggerSync">
          立即同步
        </el-button>
        <el-button size="small" @click="loadSyncStatus">刷新状态</el-button>
      </div>
    </el-card>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队映射" name="teams">
        <mapping-table :entity-type="'team'" :columns="['zh', 'en', 'source_aliases']" />
      </el-tab-pane>
      <el-tab-pane label="联赛映射" name="leagues">
        <mapping-table :entity-type="'league'" :columns="['zh', 'en', 'source_aliases']" />
      </el-tab-pane>
    </el-tabs>

    <div class="mapping-documentation">
      <h3>映射规则说明</h3>
      <ul>
        <li>系统优先展示数据库中的实体映射，静态配置仅作兜底。</li>
        <li>来源别名格式：<code>source_a:a1,a2;source_b:b1,b2</code>。</li>
        <li>点击“立即同步”后，后台会从比赛库聚合球队/联赛别名并自动回填。</li>
      </ul>
    </div>
  </div>
</template>

<script>
import MappingTable from './components/MappingTable.vue'
import { getEntityMappingSyncStatus, triggerEntityMappingSync } from '@/api/entityMapping'

export default {
  name: 'EntityMappings',
  components: { MappingTable },
  data() {
    return {
      activeTab: 'teams',
      syncStatus: null,
      syncTriggerLoading: false
    }
  },
  computed: {
    syncStatusText() {
      if (!this.syncStatus) return '未知'
      if (this.syncStatus.is_running) return '运行中'
      const lastRun = this.syncStatus.last_run
      if (!lastRun) return '未执行'
      if (lastRun.status === 'success') return '成功'
      if (lastRun.status === 'failed') return '失败'
      return lastRun.status || '未知'
    }
  },
  async mounted() {
    await this.loadSyncStatus()
  },
  methods: {
    async loadSyncStatus() {
      try {
        const resp = await getEntityMappingSyncStatus()
        this.syncStatus = resp || null
      } catch (error) {
        this.$message.warning('同步状态获取失败')
      }
    },
    async handleTriggerSync() {
      this.syncTriggerLoading = true
      try {
        const resp = await triggerEntityMappingSync()
        const started = !!resp?.started
        this.$message.success(started ? '已触发同步任务' : (resp?.message || '同步任务正在运行'))
      } catch (error) {
        this.$message.error('触发同步失败')
      } finally {
        this.syncTriggerLoading = false
        await this.loadSyncStatus()
      }
    }
  }
}
</script>

<style scoped>
.entity-mappings {
  padding: 20px;
}

.sync-card {
  margin-bottom: 16px;
}

.sync-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  color: #4b5a6d;
  font-size: 13px;
  margin-bottom: 10px;
}

.sync-actions {
  display: flex;
  gap: 10px;
}

.mapping-documentation {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.mapping-documentation h3 {
  margin-top: 0;
  color: #333;
}

.mapping-documentation ul {
  padding-left: 20px;
}

.mapping-documentation code {
  background-color: #eef1f5;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
