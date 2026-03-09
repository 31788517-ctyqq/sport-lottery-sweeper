<template>
  <div class="match-card" :data-match-id="match.id" :data-league="match.leagueId">
    <div class="match-card-header" @click="toggleExpand">
      <div class="match-meta">
        <div class="match-id">{{ match.id }}</div>
        <div class="match-league" :class="match.leagueColor">{{ match.league }}</div>
        <div class="match-time">{{ formatDate(match.time) }}</div>
      </div>
      
      <div class="match-teams">
        <div class="team">
          <div class="team-logo">{{ match.homeTeamShort }}</div>
          <div class="team-name">{{ match.homeTeam }}</div>
          <div class="team-form">
            <span 
              v-for="(result, index) in match.homeForm" 
              :key="'home-' + index"
              :class="`form-${result.toLowerCase()}`"
            >
              {{ result }}
            </span>
          </div>
        </div>
        
        <div class="vs-separator">VS</div>
        
        <div class="team">
          <div class="team-logo">{{ match.awayTeamShort }}</div>
          <div class="team-name">{{ match.awayTeam }}</div>
          <div class="team-form">
            <span 
              v-for="(result, index) in match.awayForm" 
              :key="'away-' + index"
              :class="`form-${result.toLowerCase()}`"
            >
              {{ result }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="match-stats">
        <div class="stat-item">
          <div class="stat-label">情报</div>
          <div class="stat-value">{{ intelligence.length }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">权重</div>
          <div class="stat-value">{{ avgWeight.toFixed(1) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">新</div>
          <div class="stat-value">{{ newIntelCount }}</div>
        </div>
      </div>
      
      <div class="match-toggle">
        <i class="fas fa-chevron-down"></i>
      </div>
    </div>
    
    <div class="intelligence-content" v-if="expanded">
      <div v-if="intelligence.length === 0" class="empty-state" style="padding: 40px 20px;">
        <div class="empty-icon">
          <i class="far fa-newspaper"></i>
        </div>
        <p class="empty-description">暂无相关情报</p>
      </div>
      <div v-else>
        <!-- 预测模块 -->
        <div 
          v-for="pred in match.predictions" 
          :key="pred.id"
          class="prediction-module"
        >
          <div class="prediction-header">
            <i :class="pred.icon" class="prediction-icon"></i>
            <h4 class="prediction-title">{{ pred.type }}预测</h4>
          </div>
          <div class="prediction-content">
            <div class="prediction-text">{{ pred.prediction }}</div>
            <div class="prediction-stats">
              <div class="prediction-stat">
                <div class="prediction-stat-label">置信度</div>
                <div class="prediction-stat-value">{{ pred.confidence }}%</div>
              </div>
              <div class="prediction-stat">
                <div class="prediction-stat-label">来源</div>
                <div class="prediction-stat-value">{{ pred.source }}</div>
              </div>
            </div>
          </div>
          <div class="prediction-source">
            <i class="far fa-clock"></i>
            <span>{{ formatTimeAgo(pred.timestamp) }}</span>
          </div>
        </div>
        
        <!-- SP数据表格（如果有SP情报） -->
        <div 
          v-if="spIntel && match.spData" 
          class="intel-item"
        >
          <div class="intel-header">
            <span class="intel-time">{{ formatTime(new Date(spIntel.timestamp)) }}</span>
          </div>
          <div class="intel-tags">
            <span class="intel-tag tag-sp">
              <i class="fas fa-chart-line"></i>
              <span>赔率变化</span>
            </span>
            <span class="source-badge" :class="`source-${spIntel.source}`">{{ getSourceName(spIntel.source) }}</span>
          </div>
          <div class="intel-summary">{{ spIntel.summary }}</div>
          <table class="sp-table">
            <thead>
              <tr>
                <th>公司</th>
                <th>胜</th>
                <th>平</th>
                <th>负</th>
                <th>变化</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="[company, odds] in Object.entries(match.spData)" :key="company">
                <td>{{ company }}</td>
                <td>
                  {{ odds.win.latest }}
                  <span 
                    v-if="getSPChange(odds.win.initial, odds.win.latest)" 
                    :class="`sp-change ${getSPChange(odds.win.initial, odds.win.latest).direction}`"
                  >
                    {{ getSPChange(odds.win.initial, odds.win.latest).symbol }}{{ getSPChange(odds.win.initial, odds.win.latest).amount }}
                  </span>
                </td>
                <td>
                  {{ odds.draw.latest }}
                  <span 
                    v-if="getSPChange(odds.draw.initial, odds.draw.latest)" 
                    :class="`sp-change ${getSPChange(odds.draw.initial, odds.draw.latest).direction}`"
                  >
                    {{ getSPChange(odds.draw.initial, odds.draw.latest).symbol }}{{ getSPChange(odds.draw.initial, odds.draw.latest).amount }}
                  </span>
                </td>
                <td>
                  {{ odds.loss.latest }}
                  <span 
                    v-if="getSPChange(odds.loss.initial, odds.loss.latest)" 
                    :class="`sp-change ${getSPChange(odds.loss.initial, odds.loss.latest).direction}`"
                  >
                    {{ getSPChange(odds.loss.initial, odds.loss.latest).symbol }}{{ getSPChange(odds.loss.initial, odds.loss.latest).amount }}
                  </span>
                </td>
                <td>{{ getSPTrend(odds) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="intel-footer">
            <div class="intel-source">
              <i class="far fa-clock"></i>
              <span>{{ formatTimeAgo(spIntel.timestamp) }}</span>
            </div>
            <div class="intel-weight">
              <span class="weight-label">权重</span>
              <div class="weight-badge" :class="getWeightClass(spIntel.weight)">{{ spIntel.weight.toFixed(1) }}</div>
            </div>
          </div>
        </div>
        
        <!-- 其他情报 -->
        <div 
          v-for="intel in otherIntelligence" 
          :key="intel.id"
          class="intel-item"
          :class="{ new: intel.isNew }"
        >
          <span v-if="intel.isNew" class="new-badge">NEW</span>
          <div class="intel-header">
            <span class="intel-time">{{ formatTime(new Date(intel.timestamp)) }}</span>
          </div>
          <div class="intel-tags">
            <span class="intel-tag" :class="`tag-${intel.type}`">
              <i :class="intel.typeIcon"></i>
              <span>{{ intel.typeName }}</span>
            </span>
            <span class="source-badge" :class="`source-${intel.source}`">{{ intel.sourceName }}</span>
          </div>
          <div class="intel-summary">{{ intel.summary }}</div>
          <div class="intel-content">{{ intel.content }}</div>
          <div class="intel-footer">
            <div class="intel-source">
              <i class="far fa-clock"></i>
              <span>{{ formatTimeAgo(intel.timestamp) }}</span>
            </div>
            <div class="intel-weight">
              <span class="weight-label">权重</span>
              <div class="weight-badge" :class="getWeightClass(intel.weight)">{{ intel.weight.toFixed(1) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useAppStore } from '../stores';

export default {
  name: 'MatchCard',
  props: {
    match: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const store = useAppStore();
    const expanded = ref(false);
    
    const intelligence = computed(() => {
      return store.intelligence[props.match.id] || [];
    });
    
    const avgWeight = computed(() => {
      if (intelligence.value.length === 0) return 0;
      const totalWeight = intelligence.value.reduce((sum, intel) => sum + intel.weight, 0);
      return totalWeight / intelligence.value.length;
    });
    
    const newIntelCount = computed(() => {
      return intelligence.value.filter(intel => intel.isNew).length;
    });
    
    const spIntel = computed(() => {
      return intelligence.value.find(intel => intel.type === 'sp');
    });
    
    const otherIntelligence = computed(() => {
      return intelligence.value.filter(intel => intel.type !== 'sp');
    });
    
    const toggleExpand = () => {
      expanded.value = !expanded.value;
    };
    
    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit'
      }) + ' ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        });
    };
    
    const formatTime = (date) => {
      if (!(date instanceof Date)) {
        date = new Date(date);
      }
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    };
    
    const formatTimeAgo = (timeString) => {
      const time = new Date(timeString);
      const now = new Date();
      const diffMs = now - time;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);
      
      if (diffMins < 1) return '刚刚';
      if (diffMins < 60) return `${diffMins}分钟前`;
      if (diffHours < 24) return `${diffHours}小时前`;
      if (diffDays < 7) return `${diffDays}天前`;
      return time.toLocaleDateString('zh-CN');
    };
    
    const getWeightClass = (weight) => {
      if (weight >= 8.0) return 'weight-high';
      if (weight >= 6.0) return 'weight-medium';
      return 'weight-low';
    };
    
    const getSourceName = (source) => {
      const sourceObj = store.mockConfig.sources.find(s => s.id === source);
      return sourceObj ? sourceObj.name : source;
    };
    
    const getSPChange = (initial, latest) => {
      const initialNum = parseFloat(initial);
      const latestNum = parseFloat(latest);
      const change = latestNum - initialNum;
      
      if (change === 0) return null;
      
      const direction = change < 0 ? 'down' : 'up';
      const symbol = direction === 'down' ? '↓' : '↑';
      const absChange = Math.abs(change).toFixed(2);
      
      return { direction, symbol, amount: absChange };
    };
    
    const getSPTrend = (odds) => {
      const winChange = parseFloat(odds.win.latest) - parseFloat(odds.win.initial);
      const drawChange = parseFloat(odds.draw.latest) - parseFloat(odds.draw.initial);
      const lossChange = parseFloat(odds.loss.latest) - parseFloat(odds.loss.initial);
      
      if (winChange < 0 && lossChange > 0) return '倾向主胜';
      if (lossChange < 0 && winChange > 0) return '倾向客胜';
      if (drawChange < 0) return '倾向平局';
      
      return '趋势不明';
    };
    
    return {
      expanded,
      intelligence,
      avgWeight,
      newIntelCount,
      spIntel,
      otherIntelligence,
      toggleExpand,
      formatDate,
      formatTime,
      formatTimeAgo,
      getWeightClass,
      getSourceName,
      getSPChange,
      getSPTrend
    };
  }
};
</script>

<style scoped>
.match-card {
  background: var(--bg-card);
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.match-card.expanded {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.match-card-header {
  padding: 16px;
  cursor: pointer;
  user-select: none;
  position: relative;
}

.match-card-header:active {
  background: rgba(255, 255, 255, 0.05);
}

.match-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.match-id {
  font-size: 11px;
  color: var(--text-sub);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.match-league {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.league-premier { background: rgba(255, 107, 107, 0.1); color: var(--league-premier); }
.league-laliga { background: rgba(78, 205, 196, 0.1); color: var(--league-laliga); }
.league-seriea { background: rgba(69, 183, 209, 0.1); color: var(--league-seriea); }
.league-bundesliga { background: rgba(150, 206, 180, 0.1); color: var(--league-bundesliga); }
.league-ligue1 { background: rgba(254, 202, 87, 0.1); color: var(--league-ligue1); }
.league-champions { background: rgba(255, 159, 243, 0.1); color: var(--league-champions); }

.match-time {
  font-size: 13px;
  color: var(--text-light);
  font-weight: 500;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 16px 0;
  padding: 0 8px;
}

.team {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.team-logo {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--text-light);
}

.team-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  text-align: center;
}

.team-form {
  font-size: 11px;
  color: var(--text-sub);
  display: flex;
  gap: 2px;
}

.form-win { color: #7ee787; }
.form-draw { color: var(--warning); }
.form-loss { color: var(--danger); }

.vs-separator {
  font-size: 13px;
  color: var(--text-sub);
  padding: 0 16px;
  font-weight: 600;
}

.match-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-sub);
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-light);
}

.match-toggle {
  position: absolute;
  right: 16px;
  top: 16px;
  color: var(--text-sub);
  transition: transform 0.3s;
}

.match-card.expanded .match-toggle {
  transform: rotate(180deg);
}

.intelligence-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border-top: 1px solid var(--border-color);
}

.match-card.expanded .intelligence-content {
  max-height: 2000px;
}

.prediction-module {
  padding: 16px;
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.15), rgba(88, 166, 255, 0.05));
  border-bottom: 1px solid rgba(88, 166, 255, 0.3);
}

.prediction-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.prediction-icon {
  color: var(--primary);
  font-size: 18px;
}

.prediction-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary);
}

.prediction-content {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.prediction-text {
  font-size: 14px;
  color: var(--text-main);
  line-height: 1.6;
  margin-bottom: 8px;
}

.prediction-stats {
  display: flex;
  gap: 16px;
}

.prediction-stat {
  flex: 1;
}

.prediction-stat-label {
  font-size: 11px;
  color: var(--text-sub);
  margin-bottom: 2px;
}

.prediction-stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}

.prediction-source {
  font-size: 12px;
  color: var(--text-sub);
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 6px;
}

.intel-item {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
}

.intel-item:last-child {
  border-bottom: none;
}

.intel-item.new {
  background: rgba(35, 134, 54, 0.05);
  border-left: 4px solid var(--success);
}

.new-badge {
  position: absolute;
  top: 12px;
  right: 16px;
  background: var(--success);
  color: white;
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(35, 134, 54, 0.3);
}

.intel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.intel-time {
  font-size: 12px;
  color: var(--text-sub);
  font-family: 'Courier New', monospace;
}

.intel-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.intel-tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-sp { background: rgba(240, 136, 62, 0.15); color: var(--tag-sp); }
.tag-injury { background: rgba(248, 81, 73, 0.15); color: var(--tag-injury); }
.tag-weather { background: rgba(88, 166, 255, 0.15); color: var(--tag-weather); }
.tag-referee { background: rgba(163, 113, 247, 0.15); color: var(--tag-referee); }
.tag-motive { background: rgba(240, 136, 62, 0.15); color: var(--tag-motive); }
.tag-tactics { background: rgba(126, 231, 135, 0.15); color: var(--tag-tactics); }
.tag-coach { background: rgba(126, 231, 135, 0.15); color: var(--tag-coach); }
.tag-history { background: rgba(139, 148, 158, 0.15); color: var(--tag-history); }
.tag-prediction { background: rgba(88, 166, 255, 0.15); color: var(--tag-prediction); }
.tag-atmosphere { background: rgba(240, 136, 62, 0.15); color: var(--tag-atmosphere); }

.source-badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-sub);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.source-official { background: rgba(126, 231, 135, 0.15); color: var(--source-official); }
.source-media { background: rgba(88, 166, 255, 0.15); color: var(--source-media); }
.source-social { background: rgba(163, 113, 247, 0.15); color: var(--source-social); }
.source-bookmaker { background: rgba(240, 136, 62, 0.15); color: var(--source-bookmaker); }

.intel-content {
  font-size: 14px;
  color: var(--text-light);
  line-height: 1.6;
  margin-bottom: 12px;
}

.intel-summary {
  font-size: 13px;
  color: var(--text-main);
  font-weight: 500;
  margin-bottom: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border-left: 3px solid var(--primary);
}

.intel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.intel-source {
  font-size: 12px;
  color: var(--text-sub);
  display: flex;
  align-items: center;
  gap: 6px;
}

.intel-weight {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-label {
  font-size: 12px;
  color: var(--text-sub);
}

.weight-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.weight-high { background: rgba(248, 81, 73, 0.2); color: var(--weight-high); border: 2px solid rgba(248, 81, 73, 0.4); }
.weight-medium { background: rgba(240, 136, 62, 0.2); color: var(--weight-medium); border: 2px solid rgba(240, 136, 62, 0.4); }
.weight-low { background: rgba(139, 148, 158, 0.2); color: var(--weight-low); border: 2px solid rgba(139, 148, 158, 0.4); }

.sp-table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 12px;
}

.sp-table th, .sp-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.sp-table th {
  color: var(--text-sub);
  font-weight: 600;
}

.sp-table td {
  color: var(--text-light);
}

.sp-change {
  font-weight: 600;
}

.sp-change.up {
  color: #7ee787;
}

.sp-change.down {
  color: var(--danger);
}

.empty-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--text-sub);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
  color: var(--text-sub);
  opacity: 0.5;
}

.empty-description {
  font-size: 14px;
  color: var(--text-sub);
  line-height: 1.5;
}
</style>