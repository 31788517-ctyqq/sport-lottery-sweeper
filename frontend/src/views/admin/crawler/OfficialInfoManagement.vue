<template>
  <div class="official-info-management">
    <div class="toolbar">
      <el-button type="primary" @click="handleVerifyAll">
        <el-icon><Refresh /></el-icon>
        全量验证
      </el-button>
      <el-button @click="handleDiscoverAll">
        <el-icon><Search /></el-icon>
        全量发现
      </el-button>
      <el-button type="success" :loading="enrichLoading" @click="handleTriggerEnrich">
        <el-icon><MagicStick /></el-icon>
        自动补全
      </el-button>

      <el-input-number v-model="enrichLimit" :min="1" :max="2000" size="small" />
      <el-switch v-model="enrichOnlyMissing" active-text="仅缺失" inactive-text="全部实体" />
      <el-input-number
        v-model="enrichConfidence"
        :min="0"
        :max="1"
        :step="0.05"
        :precision="2"
        size="small"
      />

      <el-switch
        v-model="tableOnlyMissing"
        active-text="列表仅看缺失"
        inactive-text="列表显示全部"
        @change="handleTableFilterChange"
      />

      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
    </div>

    <div class="summary-cards">
      <el-card shadow="never" class="summary-card">
        <div class="summary-title">官方信息概览</div>
        <div class="summary-item">总数：{{ verificationSummary.total }}</div>
        <div class="summary-item summary-valid">有效：{{ verificationSummary.valid }}</div>
        <div class="summary-item summary-invalid">无效：{{ verificationSummary.invalid }}</div>
        <div class="summary-item summary-warning">待更新：{{ verificationSummary.needs_update }}</div>
        <div class="summary-item">有效率：{{ toPercent(verificationSummary.valid_rate) }}</div>
        <div class="summary-item">陈旧率：{{ toPercent(verificationSummary.stale_rate) }}</div>
      </el-card>

      <el-card shadow="never" class="summary-card">
        <div class="summary-title">自动补全状态</div>
        <div class="summary-item">运行中：{{ enrichStatus.is_running ? '是' : '否' }}</div>
        <div class="summary-item">待处理：{{ enrichStatus.summary?.pending || 0 }}</div>
        <div class="summary-item summary-valid">成功：{{ enrichStatus.summary?.success || 0 }}</div>
        <div class="summary-item summary-invalid">失败：{{ enrichStatus.summary?.failed || 0 }}</div>
        <div class="summary-item summary-warning">缺失：{{ enrichStatus.summary?.missing || 0 }}</div>
        <div class="summary-item">最近结束：{{ enrichStatus.last_finished_at || '-' }}</div>
      </el-card>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队官方信息" name="teams">
        <entity-official-info-table
          :key="`teams-${tableRefreshKey}`"
          :entity-type="'team'"
          :only-missing="tableOnlyMissing"
          :columns="['website', 'twitter', 'facebook', 'instagram', 'weibo']"
          @verify="handleVerify"
          @discover="handleDiscover"
          @update="handleUpdate"
        />
      </el-tab-pane>
      <el-tab-pane label="联赛官方信息" name="leagues">
        <entity-official-info-table
          :key="`leagues-${tableRefreshKey}`"
          :entity-type="'league'"
          :only-missing="tableOnlyMissing"
          :columns="['website', 'twitter', 'facebook', 'instagram']"
          @verify="handleVerify"
          @discover="handleDiscover"
          @update="handleUpdate"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { MagicStick, Refresh, Search } from '@element-plus/icons-vue'
import EntityOfficialInfoTable from './components/EntityOfficialInfoTable.vue'
import {
  discoverOfficialInfo,
  discoverOfficialInfoAll,
  getOfficialInfoEnrichStatus,
  getOfficialInfoSummary,
  triggerOfficialInfoEnrich,
  updateOfficialInfo,
  verifyOfficialInfo,
  verifyOfficialInfoAll
} from '@/api/entityMapping'

export default {
  name: 'OfficialInfoManagement',
  components: {
    EntityOfficialInfoTable,
    Refresh,
    Search,
    MagicStick
  },
  data() {
    return {
      activeTab: 'teams',
      tableRefreshKey: 0,
      tableOnlyMissing: false,
      enrichLoading: false,
      enrichLimit: 100,
      enrichOnlyMissing: true,
      enrichConfidence: 0.6,
      verificationSummary: {
        total: 0,
        valid: 0,
        invalid: 0,
        needs_update: 0,
        valid_rate: 0,
        stale_rate: 0,
        last_verified: ''
      },
      enrichStatus: {
        is_running: false,
        summary: {
          total: 0,
          missing: 0,
          pending: 0,
          running: 0,
          success: 0,
          failed: 0
        },
        last_started_at: null,
        last_finished_at: null
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    toPercent(value) {
      const numeric = Number(value || 0)
      if (Number.isNaN(numeric)) return '0.00%'
      return `${(numeric * 100).toFixed(2)}%`
    },
    getCurrentEntityType() {
      return this.activeTab === 'teams' ? 'teams' : 'leagues'
    },
    async loadData() {
      try {
        const [summaryData, enrichData] = await Promise.all([
          getOfficialInfoSummary(),
          getOfficialInfoEnrichStatus({ entity_type: 'all' })
        ])
        this.verificationSummary = summaryData?.summary || this.verificationSummary
        this.enrichStatus = enrichData || this.enrichStatus
      } catch (error) {
        this.$message.error('加载官方信息状态失败')
      }
    },
    async handleVerify(entityType, entityId) {
      try {
        await verifyOfficialInfo(entityType, entityId)
        this.$message.success('验证任务已提交')
        await this.loadData()
        this.tableRefreshKey += 1
      } catch (error) {
        this.$message.error('提交验证任务失败')
      }
    },
    async handleDiscover(entityType, entityId) {
      try {
        await discoverOfficialInfo(entityType, entityId)
        this.$message.success('发现任务已提交')
        await this.loadData()
      } catch (error) {
        this.$message.error('提交发现任务失败')
      }
    },
    async handleUpdate(entityType, entityId, updates) {
      try {
        await updateOfficialInfo(entityType, entityId, updates)
        await this.loadData()
      } catch (error) {
        this.$message.error('更新官方信息失败')
      }
    },
    async handleVerifyAll() {
      try {
        await verifyOfficialInfoAll(this.getCurrentEntityType())
        this.$message.success('全量验证任务已提交')
        await this.loadData()
        this.tableRefreshKey += 1
      } catch (error) {
        this.$message.error('提交全量验证任务失败')
      }
    },
    async handleDiscoverAll() {
      try {
        await discoverOfficialInfoAll(this.getCurrentEntityType())
        this.$message.success('全量发现任务已提交')
        await this.loadData()
      } catch (error) {
        this.$message.error('提交全量发现任务失败')
      }
    },
    async handleTriggerEnrich() {
      this.enrichLoading = true
      try {
        const entityType = this.getCurrentEntityType()
        const resp = await triggerOfficialInfoEnrich({
          entity_type: entityType,
          limit: this.enrichLimit,
          only_missing: this.enrichOnlyMissing,
          min_confidence: this.enrichConfidence
        })
        const message = resp?.started
          ? '自动补全任务已触发'
          : (resp?.message || '任务未触发')
        this.$message.success(message)
        await this.loadData()
      } catch (error) {
        this.$message.error('触发自动补全任务失败')
      } finally {
        this.enrichLoading = false
      }
    },
    handleTableFilterChange() {
      this.tableRefreshKey += 1
    },
    async refreshData() {
      await this.loadData()
      this.tableRefreshKey += 1
    }
  }
}
</script>

<style scoped>
.official-info-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card {
  min-height: 132px;
}

.summary-title {
  font-weight: 600;
  color: #2f3a4a;
  margin-bottom: 10px;
}

.summary-item {
  font-size: 13px;
  color: #4b5a6d;
  margin-bottom: 4px;
}

.summary-valid {
  color: #67c23a;
}

.summary-invalid {
  color: #f56c6c;
}

.summary-warning {
  color: #e6a23c;
}

@media (max-width: 1100px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
