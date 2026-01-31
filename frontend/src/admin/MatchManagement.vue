<template>
  <div class="match-management">
    <el-card>
      <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick">
        <el-tab-pane label="竞彩赛程管理" name="jingcai">
          <JingcaiMatchManagement ref="jingcaiRef" />
        </el-tab-pane>
        <el-tab-pane label="北单赛程管理" name="beidan">
          <BeidanMatchManagement ref="beidanRef" />
        </el-tab-pane>
        <el-tab-pane label="赛程配置管理" name="config">
          <LeagueConfigManagement ref="configRef" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ref, defineAsyncComponent } from 'vue'

// 异步加载子组件，优化初始加载性能
export default {
  name: 'MatchManagement',
  components: {
    JingcaiMatchManagement: defineAsyncComponent(() => import('./JingcaiMatchManagement.vue')),
    BeidanMatchManagement: defineAsyncComponent(() => import('./BeidanMatchManagement.vue')),
    LeagueConfigManagement: defineAsyncComponent(() => import('./LeagueConfigManagement.vue'))
  },
  setup() {
    const activeTab = ref('jingcai')
    const jingcaiRef = ref(null)
    const beidanRef = ref(null)
    const configRef = ref(null)
    
    const handleTabClick = (tab) => {
      console.log('切换到标签页:', tab.name)
    }
    
    return {
      activeTab,
      jingcaiRef,
      beidanRef,
      configRef,
      handleTabClick
    }
  }
}
</script>

<style scoped>
.match-management {
  padding: 20px;
}

.el-card {
  min-height: 600px;
}

.el-tabs--card >>> .el-tabs__content {
  padding: 20px 0;
}
</style>