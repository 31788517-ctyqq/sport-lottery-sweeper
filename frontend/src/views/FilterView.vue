<template>
  <div class="filter-view">
    <div class="filter-panels" id="filterPanels">
      <!-- 情报分类筛选 -->
      <div class="filter-panel expanded" id="intelTypePanel">
        <div class="filter-header" @click="toggleFilterPanel('intelType')">
          <div class="filter-title">
            <i class="fas fa-tags"></i>
            情报分类
            <span class="filter-count" id="intelTypeCount">{{ selectedIntelTypes.length }}</span>
          </div>
          <div class="filter-toggle">
            <i class="fas fa-chevron-down" :class="{ rotated: panelStates.intelTypeExpanded }"></i>
          </div>
        </div>
        <div class="filter-content" v-show="panelStates.intelTypeExpanded">
          <div class="filter-options">
            <div 
              v-for="type in intelligenceTypes" 
              :key="type.id"
              class="filter-option"
              :class="{ selected: selectedIntelTypes.includes(type.id) }"
              @click="toggleFilter('intelTypes', type.id)"
            >
              <i :class="type.icon"></i>
              <span>{{ type.name }}</span>
            </div>
          </div>
          <div class="filter-actions-bar">
            <button class="filter-action-btn clear" @click="clearFilter('intelTypes')">
              <i class="fas fa-times"></i> 清除
            </button>
            <button class="filter-action-btn apply" @click="applyFilters">
              <i class="fas fa-check"></i> 应用筛选
            </button>
          </div>
        </div>
      </div>

      <!-- 联赛分类筛选 -->
      <div class="filter-panel" id="leaguePanel">
        <div class="filter-header" @click="toggleFilterPanel('league')">
          <div class="filter-title">
            <i class="fas fa-trophy"></i>
            联赛分类
            <span class="filter-count" id="leagueCount">{{ selectedLeagues.length }}</span>
          </div>
          <div class="filter-toggle">
            <i class="fas fa-chevron-down" :class="{ rotated: panelStates.leagueExpanded }"></i>
          </div>
        </div>
        <div class="filter-content" v-show="panelStates.leagueExpanded">
          <div class="filter-options">
            <div 
              v-for="league in leagues" 
              :key="league.id"
              class="filter-option"
              :class="{ selected: selectedLeagues.includes(league.id) }"
              @click="toggleFilter('leagues', league.id)"
            >
              <i :class="league.icon"></i>
              <span>{{ league.name }}</span>
            </div>
          </div>
          <div class="filter-actions-bar">
            <button class="filter-action-btn clear" @click="clearFilter('leagues')">
              <i class="fas fa-times"></i> 清除
            </button>
            <button class="filter-action-btn apply" @click="applyFilters">
              <i class="fas fa-check"></i> 应用筛选
            </button>
          </div>
        </div>
      </div>

      <!-- 信息来源筛选 -->
      <div class="filter-panel" id="sourcePanel">
        <div class="filter-header" @click="toggleFilterPanel('source')">
          <div class="filter-title">
            <i class="fas fa-newspaper"></i>
            信息来源
            <span class="filter-count" id="sourceCount">{{ selectedSources.length }}</span>
          </div>
          <div class="filter-toggle">
            <i class="fas fa-chevron-down" :class="{ rotated: panelStates.sourceExpanded }"></i>
          </div>
        </div>
        <div class="filter-content" v-show="panelStates.sourceExpanded">
          <div class="filter-options">
            <div 
              v-for="source in sources" 
              :key="source.id"
              class="filter-option"
              :class="{ selected: selectedSources.includes(source.id) }"
              @click="toggleFilter('sources', source.id)"
            >
              <i :class="source.icon"></i>
              <span>{{ source.name }}</span>
            </div>
          </div>
          <div class="filter-actions-bar">
            <button class="filter-action-btn clear" @click="clearFilter('sources')">
              <i class="fas fa-times"></i> 清除
            </button>
            <button class="filter-action-btn apply" @click="applyFilters">
              <i class="fas fa-check"></i> 应用筛选
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选摘要 -->
    <div class="filter-summary" v-if="hasActiveFilters">
      <div class="summary-title">已选择的筛选条件</div>
      <div class="summary-tags">
        <div 
          v-for="typeId in selectedIntelTypes" 
          :key="'type-' + typeId"
          class="summary-tag"
        >
          <i :class="getIntelTypeName(typeId).icon"></i>
          <span>{{ getIntelTypeName(typeId).name }}</span>
          <i class="fas fa-times" @click="removeFilterTag('intelTypes', typeId)"></i>
        </div>
        
        <div 
          v-for="leagueId in selectedLeagues" 
          :key="'league-' + leagueId"
          class="summary-tag"
        >
          <i :class="getLeagueName(leagueId).icon"></i>
          <span>{{ getLeagueName(leagueId).name }}</span>
          <i class="fas fa-times" @click="removeFilterTag('leagues', leagueId)"></i>
        </div>
        
        <div 
          v-for="sourceId in selectedSources" 
          :key="'source-' + sourceId"
          class="summary-tag"
        >
          <i :class="getSourceName(sourceId).icon"></i>
          <span>{{ getSourceName(sourceId).name }}</span>
          <i class="fas fa-times" @click="removeFilterTag('sources', sourceId)"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 模拟数据
const intelligenceTypes = ref([
  { id: 'sp', name: '赔率变化', icon: 'fas fa-chart-line' },
  { id: 'news', name: '新闻资讯', icon: 'fas fa-newspaper' },
  { id: 'weather', name: '天气影响', icon: 'fas fa-cloud-sun' },
  { id: 'injury', name: '伤病报告', icon: 'fas fa-procedures' },
  { id: 'form', name: '近期状态', icon: 'fas fa-medal' }
])

const leagues = ref([
  { id: 'epl', name: '英超', icon: 'fas fa-flag' },
  { id: 'laliga', name: '西甲', icon: 'fas fa-flag' },
  { id: 'bundesliga', name: '德甲', icon: 'fas fa-flag' },
  { id: 'seriea', name: '意甲', icon: 'fas fa-flag' },
  { id: 'ligue1', name: '法甲', icon: 'fas fa-flag' }
])

const sources = ref([
  { id: 'official', name: '官方消息', icon: 'fas fa-bullhorn' },
  { id: 'reporter', name: '记者报道', icon: 'fas fa-user' },
  { id: 'analyst', name: '专家分析', icon: 'fas fa-chart-pie' },
  { id: 'fan', name: '球迷反馈', icon: 'fas fa-users' }
])

// 筛选状态
const selectedIntelTypes = ref([])
const selectedLeagues = ref([])
const selectedSources = ref([])

// 面板展开状态
const panelStates = ref({
  intelTypeExpanded: true,
  leagueExpanded: false,
  sourceExpanded: false
})

// 计算属性
const hasActiveFilters = computed(() => {
  return selectedIntelTypes.value.length > 0 || 
         selectedLeagues.value.length > 0 || 
         selectedSources.value.length > 0
})

// 方法
const toggleFilterPanel = (panelType) => {
  panelStates.value[`${panelType}Expanded`] = !panelStates.value[`${panelType}Expanded`]
}

const toggleFilter = (filterType, id) => {
  const filterArray = filterType === 'intelTypes' ? selectedIntelTypes.value :
                     filterType === 'leagues' ? selectedLeagues.value :
                     selectedSources.value
                     
  const index = filterArray.indexOf(id)
  if (index === -1) {
    filterArray.push(id)
  } else {
    filterArray.splice(index, 1)
  }
}

const clearFilter = (filterType) => {
  if (filterType === 'intelTypes') {
    selectedIntelTypes.value = []
  } else if (filterType === 'leagues') {
    selectedLeagues.value = []
  } else if (filterType === 'sources') {
    selectedSources.value = []
  }
}

const applyFilters = () => {
  // 这里可以触发筛选逻辑
  console.log('应用筛选:', {
    types: selectedIntelTypes.value,
    leagues: selectedLeagues.value,
    sources: selectedSources.value
  })
}

const removeFilterTag = (filterType, id) => {
  const filterArray = filterType === 'intelTypes' ? selectedIntelTypes.value :
                     filterType === 'leagues' ? selectedLeagues.value :
                     selectedSources.value
                     
  const index = filterArray.indexOf(id)
  if (index !== -1) {
    filterArray.splice(index, 1)
  }
}

const getIntelTypeName = (id) => {
  return intelligenceTypes.value.find(t => t.id === id) || { name: '', icon: '' }
}

const getLeagueName = (id) => {
  return leagues.value.find(l => l.id === id) || { name: '', icon: '' }
}

const getSourceName = (id) => {
  return sources.value.find(s => s.id === id) || { name: '', icon: '' }
}
</script>

<style scoped>
.filter-view {
  padding: 16px;
  background: var(--bg-body);
  min-height: 100%;
}

.filter-panels {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-panel {
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  cursor: pointer;
  background: var(--bg-header);
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-main);
}

.filter-count {
  background: var(--primary);
  color: white;
  font-size: 12px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-toggle {
  transition: transform 0.3s;
}

.filter-toggle.rotated {
  transform: rotate(180deg);
}

.filter-content {
  padding: 12px;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 12px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-option.selected {
  background: rgba(88, 166, 255, 0.2);
  color: var(--primary);
}

.filter-actions-bar {
  display: flex;
  justify-content: space-between;
}

.filter-action-btn {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-action-btn.clear {
  background: rgba(248, 81, 73, 0.1);
  color: var(--danger);
  margin-right: 8px;
}

.filter-action-btn.clear:hover {
  background: rgba(248, 81, 73, 0.2);
}

.filter-action-btn.apply {
  background: rgba(88, 166, 255, 0.2);
  color: var(--primary);
  margin-left: 8px;
}

.filter-action-btn.apply:hover {
  background: rgba(88, 166, 255, 0.3);
}

.filter-summary {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.summary-title {
  font-size: 14px;
  color: var(--text-sub);
  margin-bottom: 12px;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(88, 166, 255, 0.1);
  color: var(--primary);
  border-radius: 20px;
  font-size: 12px;
}

.summary-tag .fa-times {
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
}

.summary-tag .fa-times:hover {
  background: rgba(248, 81, 73, 0.2);
}
</style>