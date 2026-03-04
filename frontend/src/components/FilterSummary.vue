<template>
  <div class="filter-summary" v-if="hasActiveFilters">
    <div class="summary-empty" v-if="!hasActiveFilters">未选择任何筛选条件</div>
    
    <!-- 情报类型标签 -->
    <div 
      v-for="typeId in filterState.intelTypes" 
      :key="'intelType-' + typeId"
      class="summary-tag"
      :class="typeId"
    >
      <i :class="getIntelTypeIcon(typeId)"></i>
      <span>{{ getIntelTypeName(typeId) }}</span>
      <i class="fas fa-times" @click="removeFilterTag('intelType', typeId)"></i>
    </div>
    
    <!-- 联赛标签 -->
    <div 
      v-for="leagueId in filterState.leagues" 
      :key="'league-' + leagueId"
      class="summary-tag"
    >
      <i class="fas fa-trophy"></i>
      <span>{{ getLeagueName(leagueId) }}</span>
      <i class="fas fa-times" @click="removeFilterTag('league', leagueId)"></i>
    </div>
    
    <!-- 信息来源标签 -->
    <div 
      v-for="sourceId in filterState.sources" 
      :key="'source-' + sourceId"
      class="summary-tag"
      :class="sourceId"
    >
      <i :class="getSourceIcon(sourceId)"></i>
      <span>{{ getSourceName(sourceId) }}</span>
      <i class="fas fa-times" @click="removeFilterTag('source', sourceId)"></i>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAppStore } from '../stores';

export default {
  name: 'FilterSummary',
  setup() {
    const store = useAppStore();
    
    const filterState = computed(() => store.filterState);
    const hasActiveFilters = computed(() => store.hasActiveFilters);
    
    const getIntelTypeIcon = (typeId) => {
      const type = store.mockConfig.intelligenceTypes.find(t => t.id === typeId);
      return type ? type.icon : 'fas fa-tag';
    };
    
    const getIntelTypeName = (typeId) => {
      const type = store.mockConfig.intelligenceTypes.find(t => t.id === typeId);
      return type ? type.name : typeId;
    };
    
    const getLeagueName = (leagueId) => {
      const league = store.mockConfig.leagues.find(l => l.id === leagueId);
      return league ? league.name : leagueId;
    };
    
    const getSourceIcon = (sourceId) => {
      const source = store.mockConfig.sources.find(s => s.id === sourceId);
      return source ? source.icon : 'fas fa-info-circle';
    };
    
    const getSourceName = (sourceId) => {
      const source = store.mockConfig.sources.find(s => s.id === sourceId);
      return source ? source.name : sourceId;
    };
    
    const removeFilterTag = (filterType, id) => {
      store.removeFilterTag(filterType, id);
    };
    
    return {
      filterState,
      hasActiveFilters,
      getIntelTypeIcon,
      getIntelTypeName,
      getLeagueName,
      getSourceIcon,
      getSourceName,
      removeFilterTag
    };
  }
};
</script>

<style scoped>
.filter-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border-color);
  min-height: 60px;
  align-items: center;
}

.summary-tag {
  background: rgba(88, 166, 255, 0.15);
  border: 1px solid rgba(88, 166, 255, 0.3);
  color: var(--primary);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: slideIn 0.3s ease-out;
}

.summary-tag i {
  font-size: 10px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.summary-tag i:hover {
  opacity: 1;
}

.summary-tag.injury {
  background: rgba(248, 81, 73, 0.15);
  border-color: rgba(248, 81, 73, 0.3);
  color: var(--tag-injury);
}

.summary-tag.weather {
  background: rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.3);
  color: var(--tag-weather);
}

.summary-tag.referee {
  background: rgba(163, 113, 247, 0.15);
  border-color: rgba(163, 113, 247, 0.3);
  color: var(--tag-referee);
}

.summary-tag.sp {
  background: rgba(240, 136, 62, 0.15);
  border-color: rgba(240, 136, 62, 0.3);
  color: var(--tag-sp);
}

.summary-tag.official {
  background: rgba(126, 231, 135, 0.15);
  border-color: rgba(126, 231, 135, 0.3);
  color: var(--source-official);
}

.summary-tag.media {
  background: rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.3);
  color: var(--source-media);
}

.summary-empty {
  font-size: 13px;
  color: var(--text-sub);
  font-style: italic;
}

@keyframes slideIn {
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
</style>