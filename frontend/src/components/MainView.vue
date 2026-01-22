<template>
  <div class="main-content">
    <!-- 筛选工具栏 -->
    <FilterToolbar />

    <!-- 筛选摘要 -->
    <FilterSummary />

    <!-- 筛选面板 -->
    <div v-if="currentView === 'filter'" class="filter-panels" id="filterPanels">
      <div class="filter-panel expanded" id="intelTypePanel">
        <div class="filter-header" @click="toggleFilterPanel('intelType')">
          <div class="filter-title">
            <i class="fas fa-tags"></i>
            情报分类
            <span class="filter-count" :class="{ 'selected-count': intelTypeCount > 0 }">{{ intelTypeCount }}</span>
          </div>
          <div class="filter-toggle">
            <i class="fas fa-chevron-down"></i>
          </div>
        </div>
        <div class="filter-content" v-show="panelState.intelTypeExpanded">
          <div class="filter-options" id="intelTypeOptions">
            <div
              v-for="type in intelligenceTypes"
              :key="type.id"
              :class="['filter-option', { selected: isFilterSelected('intelType', type.id) }]"
              @click="toggleFilterOption('intelType', type.id)"
            >
              <div class="option-badge"></div>
              <i :class="type.icon" class="option-icon"></i>
              <span class="option-label">{{ type.name }}</span>
            </div>
          </div>
          <div class="filter-actions-bar">
            <button class="filter-action-btn clear" @click="clearFilter('intelType')">
              <i class="fas fa-times"></i> 清除
            </button>
            <button class="filter-action-btn apply" @click="applyFilters">
              <i class="fas fa-check"></i> 应用筛选
            </button>
          </div>
        </div>
      </div>

      <div class="filter-panel" id="leaguePanel">
        <div class="filter-header" @click="toggleFilterPanel('league')">
          <div class="filter-title">
            <i class="fas fa-trophy"></i>
            联赛分类
            <span class="filter-count" :class="{ 'selected-count': leagueCount > 0 }">{{ leagueCount }}</span>
          </div>
          <div class="filter-toggle">
            <i class="fas fa-chevron-down"></i>
          </div>
        </div>
        <div class="filter-content" v-show="panelState.leagueExpanded">
          <div class="filter-options" id="leagueOptions">
            <div
              v-for="league in leagues"
              :key="league.id"
              :class="['filter-option', league.color, { selected: isFilterSelected('league', league.id) }]"
              @click="toggleFilterOption('league', league.id)"
            >
              <div class="option-badge"></div>
              <i :class="league.icon" class="option-icon"></i>
              <span class="option-label">{{ league.name }}</span>
            </div>
          </div>
          <div class="filter-actions-bar">
            <button class="filter-action-btn clear" @click="clearFilter('league')">
              <i class="fas fa-times"></i> 清除
            </button>
            <button class="filter-action-btn apply" @click="applyFilters">
              <i class="fas fa-check"></i> 应用筛选
            </button>
          </div>
        </div>
      </div>

      <div class="filter-panel" id="sourcePanel">
        <div class="filter-header" @click="toggleFilterPanel('source')">
          <div class="filter-title">
            <i class="fas fa-newspaper"></i>
            信息来源
            <span class="filter-count" :class="{ 'selected-count': sourceCount > 0 }">{{ sourceCount }}</span>
          </div>
          <div class="filter-toggle">
            <i class="fas fa-chevron-down"></i>
          </div>
        </div>
        <div class="filter-content" v-show="panelState.sourceExpanded">
          <div class="filter-options" id="sourceOptions">
            <div
              v-for="source in sources"
              :key="source.id"
              :class="['filter-option', { selected: isFilterSelected('source', source.id) }]"
              @click="toggleFilterOption('source', source.id)"
            >
              <div class="option-badge"></div>
              <i :class="source.icon" class="option-icon"></i>
              <span class="option-label">{{ source.name }}</span>
            </div>
          </div>
          <div class="filter-actions-bar">
            <button class="filter-action-btn clear" @click="clearFilter('source')">
              <i class="fas fa-times"></i> 清除
            </button>
            <button class="filter-action-btn apply" @click="applyFilters">
              <i class="fas fa-check"></i> 应用筛选
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计面板 -->
    <StatsPanel v-if="currentView === 'home'" />

    <!-- 用户面板 -->
    <ProfilePanel v-if="currentView === 'profile'" />

    <!-- 比赛列表 -->
    <MatchList v-if="currentView === 'home'" />

    <!-- 实时比赛表格 -->
    <MatchTable v-if="currentView === 'home'" />

    <!-- 空状态 -->
    <div v-if="filteredMatches.length === 0 && currentView === 'home'" class="empty-state">
      <div class="empty-icon">
        <i class="far fa-futbol"></i>
      </div>
      <h3 class="empty-title">暂无比赛数据</h3>
      <p class="empty-description">请尝试调整筛选条件或刷新数据</p>
      <button class="filter-chip" @click="generateMockData" style="margin-top: 20px;">
        <i class="fas fa-sync-alt"></i>
        <span>刷新数据</span>
      </button>
    </div>

    <!-- 加载状态 -->
    <div class="loading-spinner" :class="{ active: loading }">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores'
import FilterToolbar from './FilterToolbar.vue'
import FilterSummary from './FilterSummary.vue'
import StatsPanel from './StatsPanel.vue'
import ProfilePanel from './ProfilePanel.vue'
import MatchList from './MatchList.vue'
import MatchTable from './MatchTable.vue'

const store = useAppStore()

const currentView = computed(() => store.currentView)
const panelState = computed(() => store.panelState)
const loading = computed(() => store.loading)
const filteredMatches = computed(() => store.filteredMatches)

// 计算筛选计数
const intelTypeCount = computed(() => store.filterState.intelTypes.length)
const leagueCount = computed(() => store.filterState.leagues.length)
const sourceCount = computed(() => store.filterState.sources.length)

// 模拟配置数据
const intelligenceTypes = computed(() => store.mockConfig.intelligenceTypes)
const leagues = computed(() => store.mockConfig.leagues)
const sources = computed(() => store.mockConfig.sources)

// 方法
const toggleFilterPanel = (panelType) => {
  const panel = document.getElementById(`${panelType}Panel`)
  const isExpanded = panel.classList.contains('expanded')
  
  // 收起所有面板
  closeAllFilterPanels()
  
  // 如果当前是收起的，则展开
  if (!isExpanded) {
    panel.classList.add('expanded')
    store.panelState[`${panelType}Expanded`] = true
  }
}

const closeAllFilterPanels = () => {
  document.querySelectorAll('.filter-panel').forEach(panel => {
    panel.classList.remove('expanded')
  })
  
  // 更新面板状态
  Object.keys(store.panelState).forEach(key => {
    store.panelState[key] = false
  })
}

const toggleFilterOption = (filterType, id) => {
  store.toggleFilterOption(filterType, id)
}

const isFilterSelected = (filterType, id) => {
  return store.filterState[filterType + 's'].includes(id)
}

const clearFilter = (filterType) => {
  store.clearFilter(filterType)
}

const applyFilters = () => {
  // 收起所有筛选面板
  closeAllFilterPanels()
}

const generateMockData = () => {
  store.generateMockData()
}
</script>

<style scoped>
.filter-panels {
  padding: 16px;
}

.filter-panel {
  background: var(--bg-card);
  border-radius: 16px;
  margin-bottom: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.filter-panel:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.filter-panel.expanded {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border-color: rgba(88, 166, 255, 0.3);
}

.filter-header {
  padding: 18px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01));
}

.filter-header:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
}

.filter-header:active {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.03));
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-title i {
  color: var(--primary);
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.filter-count {
  font-size: 12px;
  min-width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-sub);
  margin-left: 8px;
  transition: all 0.2s;
  padding: 0 8px;
}

.selected-count {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
}

.filter-toggle {
  color: var(--text-sub);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.filter-panel.expanded .filter-toggle {
  transform: rotate(180deg);
  background: rgba(88, 166, 255, 0.1);
  color: var(--primary);
}

.filter-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-panel.expanded .filter-content {
  max-height: 1000px;
}

.filter-options {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  background: rgba(255, 255, 255, 0.01);
}

.filter-option {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 16px 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.filter-option:active {
  transform: scale(0.98);
}

.filter-option:hover {
  border-color: rgba(88, 166, 255, 0.5);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.filter-option.selected {
  background: rgba(88, 166, 255, 0.15);
  border-color: var(--primary);
  box-shadow: 0 4px 16px rgba(88, 166, 255, 0.2);
}

.filter-option.selected::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary);
  border-radius: 14px 14px 0 0;
}

.option-icon {
  font-size: 24px;
  color: var(--text-sub);
  transition: all 0.2s;
}

.filter-option.selected .option-icon {
  color: var(--primary);
  transform: scale(1.1);
}

.option-label {
  font-size: 13px;
  color: var(--text-main);
  font-weight: 500;
  text-align: center;
  transition: all 0.2s;
}

.filter-option.selected .option-label {
  color: var(--primary);
  font-weight: 600;
}

.option-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0;
  transform: scale(0);
  transition: all 0.2s;
}

.filter-option.selected .option-badge {
  opacity: 1;
  transform: scale(1);
}

.filter-option.league-premier {
  border-left: 3px solid var(--league-premier);
}

.filter-option.league-laliga {
  border-left: 3px solid var(--league-laliga);
}

.filter-option.league-seriea {
  border-left: 3px solid var(--league-seriea);
}

.filter-option.league-bundesliga {
  border-left: 3px solid var(--league-bundesliga);
}

.filter-option.league-ligue1 {
  border-left: 3px solid var(--league-ligue1);
}

.filter-option.league-champions {
  border-left: 3px solid var(--league-champions);
}

.filter-actions-bar {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  gap: 12px;
  background: rgba(255, 255, 255, 0.02);
}

.filter-action-btn {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.filter-action-btn:active {
  transform: scale(0.98);
}

.filter-action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.filter-action-btn.apply {
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  color: white;
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
}

.filter-action-btn.apply:hover {
  box-shadow: 0 6px 20px rgba(88, 166, 255, 0.4);
}

.filter-action-btn.clear {
  background: rgba(248, 81, 73, 0.1);
  color: var(--danger);
  border-color: rgba(248, 81, 73, 0.3);
}

.filter-action-btn.clear:hover {
  background: rgba(248, 81, 73, 0.15);
}
</style>