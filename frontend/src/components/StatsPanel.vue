<template>
  <div class="stats-panel">
    <div class="stats-header">
      <div class="stats-title">数据概览</div>
      <div class="stats-refresh" style="font-size: 12px; color: var(--text-sub); cursor: pointer;" @click="refreshStats">
        <i class="fas fa-redo"></i> 刷新
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card-value">{{ matchStats.totalMatches }}</div>
        <div class="stat-card-label">比赛总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-value">{{ matchStats.totalIntel }}</div>
        <div class="stat-card-label">情报总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-value">{{ matchStats.newIntel }}</div>
        <div class="stat-card-label">新情报</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-value">{{ matchStats.avgIntelPerMatch }}</div>
        <div class="stat-card-label">场均情报</div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAppStore } from '../stores';

export default {
  name: 'StatsPanel',
  setup() {
    const store = useAppStore();
    
    const matchStats = computed(() => store.matchStats);
    
    const refreshStats = () => {
      store.generateMockData();
    };
    
    return {
      matchStats,
      refreshStats
    };
  }
};
</script>

<style scoped>
.stats-panel {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  margin: 16px;
  border: 1px solid var(--border-color);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stats-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
}

.stat-card-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.stat-card-label {
  font-size: 12px;
  color: var(--text-sub);
}
</style>