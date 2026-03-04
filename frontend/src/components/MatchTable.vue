<template>
  <div class="match-table-container">
    <h3>实时比赛数据</h3>
    <table class="match-table">
      <thead>
        <tr>
          <th>主队</th>
          <th>客队</th>
          <th>比赛时间</th>
          <th>状态</th>
        </tr>
      </thead>
      <tbody id="match-table-body">
        <tr v-for="match in matches" :key="match.id">
          <td>{{ match.homeTeam }}</td>
          <td>{{ match.awayTeam }}</td>
          <td>{{ formatDateTime(match.time) }}</td>
          <td>{{ match.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAppStore } from '../stores';

export default {
  name: 'MatchTable',
  setup() {
    const store = useAppStore();
    
    const matches = computed(() => {
      // 只显示一部分比赛数据用于展示
      return store.matches.slice(0, 5).map(match => ({
        id: match.id,
        homeTeam: match.homeTeam,
        awayTeam: match.awayTeam,
        time: match.time,
        status: match.status
      }));
    });
    
    const formatDateTime = (timeString) => {
      const date = new Date(timeString);
      return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    };
    
    return {
      matches,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.match-table-container {
  padding: 16px;
  margin-top: 16px;
}

.match-table-container h3 {
  margin-bottom: 12px;
  color: var(--text-main);
}

.match-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-card);
  border-radius: 8px;
  overflow: hidden;
}

.match-table th,
.match-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.match-table th {
  background: var(--bg-header);
  color: var(--text-main);
  font-weight: 600;
}

.match-table tr:last-child td {
  border-bottom: none;
}
</style>