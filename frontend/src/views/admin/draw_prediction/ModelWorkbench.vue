<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>模型工坊</span>
          <el-tag type="info">标签切换 + URL同步 + 懒加载</el-tag>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="数据与特征" name="data" />
        <el-tab-pane label="模型训练与评估" name="training" />
        <el-tab-pane label="模型管理与部署" name="deployment" />
        <el-tab-pane label="预测服务与监控" name="monitoring" />
      </el-tabs>

      <div class="tab-panel">
        <component :is="activeComponent" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const DataFeaturePanel = defineAsyncComponent(() => import('@/views/admin/draw_prediction/DrawDataFeature.vue'))
const TrainingPanel = defineAsyncComponent(() => import('@/views/admin/draw_prediction/DrawModelTrainEval.vue'))
const DeploymentPanel = defineAsyncComponent(() => import('@/views/admin/draw_prediction/DrawModelManageDeploy.vue'))
const MonitoringPanel = defineAsyncComponent(() => import('@/views/admin/draw_prediction/DrawPredictionMonitor.vue'))

const route = useRoute()
const router = useRouter()

const tabMap = {
  data: DataFeaturePanel,
  training: TrainingPanel,
  deployment: DeploymentPanel,
  monitoring: MonitoringPanel
}

const resolveTab = (value) => {
  const t = String(value || '').toLowerCase()
  return tabMap[t] ? t : 'data'
}

const activeTab = ref(resolveTab(route.query.tab))

watch(
  () => route.query.tab,
  (val) => {
    const nextTab = resolveTab(val)
    if (nextTab !== activeTab.value) {
      activeTab.value = nextTab
    }

    const rawTab = String(val || '').toLowerCase()
    if (rawTab !== nextTab) {
      router.replace({
        path: route.path,
        query: { ...route.query, tab: nextTab }
      }).catch(() => {})
    }
  },
  { immediate: true }
)

const activeComponent = computed(() => tabMap[activeTab.value] || DataFeaturePanel)

const handleTabChange = (tabName) => {
  const nextTab = resolveTab(tabName)
  const rawTab = String(route.query.tab || '').toLowerCase()
  if (activeTab.value === nextTab && rawTab === nextTab) {
    return
  }
  activeTab.value = nextTab
  router.replace({
    path: route.path,
    query: { ...route.query, tab: nextTab }
  }).catch(() => {})
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.tab-panel { margin-top: 8px; }
</style>
