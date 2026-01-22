<template>
  <div class="filter-toolbar">
    <div class="filter-section">
      <div 
        v-for="filter in quickFilters" 
        :key="filter.id"
        :class="['filter-chip', { active: currentType === filter.id }]"
        @click="handleQuickFilter(filter.id)"
      >
        <i :class="filter.icon"></i>
        <span>{{ filter.label }}</span>
      </div>
    </div>
    <div class="filter-actions">
      <div class="last-update">最后更新: {{ lastUpdateTime }}</div>
      <div class="sort-toggle">
        <span>排序:</span>
        <button 
          :class="['sort-btn', { active: currentSort === 'time' }]" 
          @click="setSort('time')"
        >
          时间
        </button>
        <button 
          :class="['sort-btn', { active: currentSort === 'weight' }]" 
          @click="setSort('weight')"
        >
          权重
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAppStore } from '../stores';

export default {
  name: 'FilterToolbar',
  setup() {
    const store = useAppStore();
    
    const quickFilters = [
      { id: 'all', label: '全部', icon: 'fas fa-list', type: 'all' },
      { id: 'injury', label: '伤病', icon: 'fas fa-user-injured', type: 'injury' },
      { id: 'sp', label: '赔率', icon: 'fas fa-chart-line', type: 'sp' },
      { id: 'prediction', label: '预测', icon: 'fas fa-crystal-ball', type: 'prediction' },
      { id: 'weather', label: '天气', icon: 'fas fa-cloud-sun', type: 'weather' },
      { id: 'tactics', label: '战术', icon: 'fas fa-chess-board', type: 'tactics' },
      { id: 'mockData', label: '生成新数据', icon: 'fas fa-database', type: 'mock' }
    ];
    
    const currentType = computed(() => store.currentType || 'all');
    const currentSort = computed(() => store.currentSort);
    const lastUpdateTime = computed(() => store.lastUpdateTime);
    
    const handleQuickFilter = (filterId) => {
      if (filterId === 'mockData') {
        store.generateMockData();
        return;
      }
      
      store.currentType = filterId;
    };
    
    const setSort = (sortType) => {
      store.setSort(sortType);
    };
    
    return {
      quickFilters,
      currentType,
      currentSort,
      lastUpdateTime,
      handleQuickFilter,
      setSort
    };
  }
};
</script>

<style scoped>
.filter-toolbar {
  background: var(--bg-header);
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 56px;
  z-index: 900;
}

.filter-section {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.filter-section::-webkit-scrollbar {
  display: none;
}

.filter-chip {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-sub);
  padding: 8px 16px;
  border-radius: 20px;
  white-space: nowrap;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-chip.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.filter-chip i {
  font-size: 12px;
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.last-update {
  font-size: 12px;
  color: var(--text-sub);
}

.sort-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-sub);
}

.sort-btn {
  padding: 4px 12px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-sub);
  font-size: 12px;
  cursor: pointer;
}

.sort-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
</style>