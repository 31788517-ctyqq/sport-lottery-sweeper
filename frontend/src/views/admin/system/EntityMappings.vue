<template>
  <div class="entity-mappings">
    <el-row :gutter="12" class="overview-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="overview-card">
          <div class="overview-label">同步成功率（7天）</div>
          <div class="overview-value">{{ syncSuccessRateText }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="overview-card">
          <div class="overview-label">最近失败</div>
          <div class="overview-value overview-text">{{ lastFailureText }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="overview-card">
          <div class="overview-label">待审冲突数</div>
          <div class="overview-value">{{ pendingConflictsText }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="overview-card">
          <div class="overview-label">补全队列</div>
          <div class="overview-value overview-text">{{ enrichQueueText }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="sync-card" shadow="never">
      <div class="sync-meta">
        <span>同步状态：{{ syncStatusText }}</span>
        <span>最近启动：{{ syncStatus?.last_started_at || '-' }}</span>
        <span>最近完成：{{ syncStatus?.last_finished_at || '-' }}</span>
        <span>下次执行：{{ syncStatus?.next_sync_at || '-' }}</span>
      </div>
      <div v-if="syncStatus?.last_error_message" class="sync-error">
        最近错误：{{ syncStatus.last_error_message }}
      </div>
      <div class="sync-actions">
        <el-button
          size="small"
          type="primary"
          :loading="syncTriggerLoading"
          @click="handleTriggerSync"
        >
          立即同步
        </el-button>
        <el-button
          size="small"
          type="warning"
          plain
          :loading="enrichTriggerLoading"
          @click="handleTriggerEnrich"
        >
          立即补全
        </el-button>
        <el-button size="small" :loading="opsOverviewLoading" @click="handleRefreshOps">
          刷新状态
        </el-button>
      </div>
    </el-card>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队映射" name="teams">
        <mapping-table
          :entity-type="'team'"
          :columns="['zh', 'en', 'source_aliases']"
          @update="handleTableUpdated"
        />
      </el-tab-pane>
      <el-tab-pane label="联赛映射" name="leagues">
        <mapping-table
          :entity-type="'league'"
          :columns="['zh', 'en', 'source_aliases']"
          @update="handleTableUpdated"
        />
      </el-tab-pane>
    </el-tabs>

    <div class="mapping-documentation">
      <h3>映射规则说明</h3>
      <ul>
        <li>系统优先展示数据库中的实体映射，静态配置仅作兜底。</li>
        <li>来源别名格式：<code>source_a:a1,a2;source_b:b1,b2</code>。</li>
        <li>点击“立即同步”后，后台会从比赛库聚合球队/联赛别名并自动回填。</li>
        <li>点击“立即补全”后，将触发官方信息缺失实体的自动补全过程。</li>
      </ul>
    </div>
  </div>
</template>

<script>
import MappingTable from './components/MappingTable.vue'
import {
  getEntityMappingSyncStatus,
  triggerEntityMappingSync,
  getEntityMappingOpsOverview,
  triggerOfficialInfoEnrich
} from '@/api/entityMapping'

export default {
  name: 'EntityMappings',
  components: { MappingTable },
  data() {
    return {
      activeTab: 'teams',
      syncStatus: null,
      opsOverview: null,
      syncTriggerLoading: false,
      enrichTriggerLoading: false,
      opsOverviewLoading: false
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
    },
    syncSuccessRateText() {
      const value = Number(this.opsOverview?.sync_success_rate_7d)
      if (Number.isNaN(value)) return '-'
      return `${value.toFixed(2)}%`
    },
    lastFailureText() {
      const message = this.opsOverview?.last_failed_message
      const at = this.opsOverview?.last_failed_at
      if (!message && !at) return '无'
      return at ? `${at}` : message
    },
    pendingConflictsText() {
      const value = Number(this.opsOverview?.pending_conflicts)
      if (Number.isNaN(value)) return '-'
      return String(value)
    },
    enrichQueueText() {
      const pending = Number(this.opsOverview?.official_enrich_pending || 0)
      const running = !!this.opsOverview?.official_enrich_running
      return running ? `运行中（待处理 ${pending}）` : `待处理 ${pending}`
    }
  },
  async mounted() {
    await Promise.all([this.loadSyncStatus(), this.loadOpsOverview()])
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
    async loadOpsOverview() {
      this.opsOverviewLoading = true
      try {
        const resp = await getEntityMappingOpsOverview()
        this.opsOverview = resp || null
      } catch (error) {
        this.opsOverview = null
        this.$message.warning('运营概览获取失败')
      } finally {
        this.opsOverviewLoading = false
      }
    },
    async handleRefreshOps() {
      await Promise.all([this.loadSyncStatus(), this.loadOpsOverview()])
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
        await this.handleRefreshOps()
      }
    },
    async handleTriggerEnrich() {
      this.enrichTriggerLoading = true
      try {
        const resp = await triggerOfficialInfoEnrich({
          entity_type: 'all',
          limit: 200,
          only_missing: true,
          min_confidence: 0.6
        })
        const started = !!resp?.started
        this.$message.success(started ? '已触发官方信息补全任务' : (resp?.message || '补全任务正在运行'))
      } catch (error) {
        this.$message.error('触发补全失败')
      } finally {
        this.enrichTriggerLoading = false
        await this.loadOpsOverview()
      }
    },
    async handleTableUpdated() {
      await this.loadOpsOverview()
    }
  }
}
</script>

<style scoped>
.entity-mappings {
  padding: 20px;
}

.overview-row {
  margin-bottom: 12px;
}

.overview-card {
  min-height: 92px;
}

.overview-label {
  font-size: 13px;
  color: #7a8599;
}

.overview-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 700;
  color: #2f3a4f;
}

.overview-text {
  font-size: 16px;
  font-weight: 600;
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

.sync-error {
  margin-bottom: 10px;
  color: #d9534f;
  font-size: 13px;
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
