<template>
  <div class="system-settings-container">
    <el-card class="system-settings-card">
      <template #header>
        <div class="card-header">
          <h3><i class="el-icon-setting"></i> 系统设置</h3>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="settings-tabs">
        <el-tab-pane label="基础设置" name="basic">
          <BasicSettings />
        </el-tab-pane>
        <el-tab-pane label="数据配置" name="data">
          <DataSettings />
        </el-tab-pane>
        <el-tab-pane label="爬虫配置" name="crawler">
          <CrawlerSettings />
        </el-tab-pane>
        <el-tab-pane label="安全设置" name="security">
          <SecuritySettings />
        </el-tab-pane>
        <el-tab-pane label="通知设置" name="notification">
          <NotificationSettings />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import BasicSettings from './settings-components/BasicSettings.vue'
import DataSettings from './settings-components/DataSettings.vue'
import CrawlerSettings from './settings-components/CrawlerSettings.vue'
import SecuritySettings from './settings-components/SecuritySettings.vue'
import NotificationSettings from './settings-components/NotificationSettings.vue'

export default {
  name: 'SystemSettings',
  components: {
    BasicSettings,
    DataSettings,
    CrawlerSettings,
    SecuritySettings,
    NotificationSettings
  },
  setup() {
    const activeTab = ref('basic')
    
    return {
      activeTab
    }
  }
}
</script>

<style scoped>
.system-settings-container {
  padding: 20px;
}

.system-settings-card {
  min-height: 600px;
}

.settings-tabs {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>