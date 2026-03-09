<!-- frontend/src/components/admin/DashboardCard.vue -->
<template>
  <van-grid :column-num="2" :border="false" class="dashboard-grid">
    <van-grid-item
      v-for="(stat, index) in statsData"
      :key="index"
      class="dashboard-card"
    >
      <template #icon>
        <van-icon :name="stat.icon" size="2rem" :color="stat.color" />
      </template>
      <template #text>
        <div class="stat-content">
          <h3 class="stat-value">{{ stat.value }}</h3>
          <p class="stat-label">{{ stat.label }}</p>
        </div>
      </template>
    </van-grid-item>
  </van-grid>
</template>

<script setup>
// Props
defineProps({
  statsData: {
    type: Array,
    required: true,
    default: () => []
  }
});
</script>

<style scoped>
.dashboard-grid {
  padding: var(--van-padding-xs) 0;
  background-color: var(--van-background-2);
}
.dashboard-card {
  padding: var(--van-padding-sm);
  background-color: white;
  border-radius: var(--van-radius-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: var(--van-padding-xs);
}
.stat-content {
  text-align: center;
  padding-top: var(--van-padding-xs);
}
.stat-value {
  margin: 0;
  font-size: var(--van-font-size-lg);
  font-weight: bold;
  color: var(--van-text-color);
}
.stat-label {
  margin: var(--van-padding-xs) 0 0 0;
  font-size: var(--van-font-size-sm);
  color: var(--van-gray-6);
}
</style>