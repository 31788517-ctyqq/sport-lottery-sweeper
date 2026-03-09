<template>
  <div class="match-list" id="matchList">
    <div 
      v-for="[dateLabel, matches] in Object.entries(groupedMatches)" 
      :key="dateLabel"
      class="date-section"
    >
      <div class="date-title">
        <span>{{ dateLabel }}</span>
        <span class="match-count">{{ matches.length }}场比赛</span>
      </div>
      
      <MatchCard 
        v-for="match in matches" 
        :key="match.id"
        :match="match"
      />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAppStore } from '../stores';
import MatchCard from './MatchCard.vue';

export default {
  name: 'MatchList',
  components: {
    MatchCard
  },
  setup() {
    const store = useAppStore();
    
    const groupedMatches = computed(() => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const afterTomorrow = new Date(tomorrow);
      afterTomorrow.setDate(afterTomorrow.getDate() + 1);
      
      const thisWeek = new Date(today);
      thisWeek.setDate(thisWeek.getDate() + 7);
      
      const groups = {
        '今日比赛': [],
        '明日比赛': [],
        '本周比赛': [],
        '未来比赛': []
      };
      
      const filteredMatches = store.filteredMatches;
      
      filteredMatches.forEach(match => {
        const matchDate = new Date(match.time);
        const matchTime = matchDate.getTime();
        
        if (matchTime >= today.getTime() && matchTime < tomorrow.getTime()) {
          groups['今日比赛'].push(match);
        } else if (matchTime >= tomorrow.getTime() && matchTime < afterTomorrow.getTime()) {
          groups['明日比赛'].push(match);
        } else if (matchTime >= afterTomorrow.getTime() && matchTime < thisWeek.getTime()) {
          groups['本周比赛'].push(match);
        } else {
          groups['未来比赛'].push(match);
        }
      });
      
      // 移除空的分组
      Object.keys(groups).forEach(key => {
        if (groups[key].length === 0) {
          delete groups[key];
        }
      });
      
      return groups;
    });
    
    return {
      groupedMatches
    };
  }
};
</script>

<style scoped>
.match-list {
  padding: 16px;
}

.date-section {
  margin-bottom: 24px;
}

.date-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid var(--primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.match-count {
  font-size: 12px;
  color: var(--text-sub);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 12px;
}
</style>