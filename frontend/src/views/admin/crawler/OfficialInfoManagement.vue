<template>
  <div class="official-info-management">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队官方信息" name="teams">
        <entity-official-info-table
          :entity-type="'team'"
          :columns="['website', 'twitter', 'facebook', 'instagram', 'weibo']"
          @verify="handleVerify"
          @discover="handleDiscover"
          @update="handleUpdate"
        />
      </el-tab-pane>
      <el-tab-pane label="联赛官方信息" name="leagues">
        <entity-official-info-table
          :entity-type="'league'"
          :columns="['website', 'twitter', 'facebook', 'instagram']"
          @verify="handleVerify"
          @discover="handleDiscover"
          @update="handleUpdate"
        />
      </el-tab-pane>
    </el-tabs>

    <div class="verification-controls">
      <el-button type="primary" @click="handleVerifyAll">
        <el-icon><Refresh /></el-icon>
        全量验证
      </el-button>
      <el-button @click="handleDiscoverAll">
        <el-icon><Search /></el-icon>
        全量发现
      </el-button>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新摘要
      </el-button>

      <div class="verification-status">
        <span :class="{ 'status-valid': verificationSummary.valid > 0 }">有效: {{ verificationSummary.valid }}</span>
        <span :class="{ 'status-invalid': verificationSummary.invalid > 0 }">无效: {{ verificationSummary.invalid }}</span>
        <span :class="{ 'status-warning': verificationSummary.needs_update > 0 }">
          需更新: {{ verificationSummary.needs_update }}
        </span>
        <span>总数: {{ verificationSummary.total }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { Refresh, Search } from '@element-plus/icons-vue'
import EntityOfficialInfoTable from './components/EntityOfficialInfoTable.vue'
import {
  discoverOfficialInfo,
  discoverOfficialInfoAll,
  getOfficialInfoSummary,
  updateOfficialInfo,
  verifyOfficialInfo,
  verifyOfficialInfoAll
} from '@/api/entityMapping'

export default {
  name: 'OfficialInfoManagement',
  components: {
    EntityOfficialInfoTable,
    Refresh,
    Search
  },
  data() {
    return {
      activeTab: 'teams',
      verificationSummary: {
        total: 0,
        valid: 0,
        invalid: 0,
        needs_update: 0,
        last_verified: ''
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const summaryData = await getOfficialInfoSummary()
        this.verificationSummary = summaryData?.summary || this.verificationSummary
      } catch (error) {
        this.$message.error('加载官方信息摘要失败')
      }
    },
    async handleVerify(entityType, entityId) {
      try {
        await verifyOfficialInfo(entityType, entityId)
        this.$message.success('验证任务已提交')
        await this.loadData()
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
        const entityType = this.activeTab === 'teams' ? 'teams' : 'leagues'
        await verifyOfficialInfoAll(entityType)
        this.$message.success('全量验证任务已提交')
        await this.loadData()
      } catch (error) {
        this.$message.error('提交全量验证任务失败')
      }
    },
    async handleDiscoverAll() {
      try {
        const entityType = this.activeTab === 'teams' ? 'teams' : 'leagues'
        await discoverOfficialInfoAll(entityType)
        this.$message.success('全量发现任务已提交')
        await this.loadData()
      } catch (error) {
        this.$message.error('提交全量发现任务失败')
      }
    },
    refreshData() {
      this.loadData()
    }
  }
}
</script>

<style scoped>
.official-info-management {
  padding: 20px;
}

.verification-controls {
  display: flex;
  align-items: center;
  margin: 20px 0;
  gap: 10px;
  flex-wrap: wrap;
}

.verification-status {
  display: flex;
  gap: 12px;
  margin-left: auto;
  font-size: 14px;
  flex-wrap: wrap;
}

.verification-status span {
  padding: 2px 8px;
  border-radius: 4px;
}

.status-valid {
  color: #67c23a;
}

.status-invalid {
  color: #f56c6c;
}

.status-warning {
  color: #e6a23c;
}
</style>
