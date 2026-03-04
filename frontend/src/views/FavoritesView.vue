<template>
  <div class="favorites-view">
    <div class="section-header">
      <h2>我的收藏</h2>
      <span class="favorites-count">({{ favorites.length }}个)</span>
    </div>
    
    <div v-if="favorites.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="far fa-star"></i>
      </div>
      <p class="empty-description">暂无收藏内容</p>
      <p class="empty-hint">点击比赛旁的星标图标可将其加入收藏</p>
    </div>
    
    <div v-else class="favorites-list">
      <div 
        v-for="match in favorites" 
        :key="match.id"
        class="match-item"
        @click="goToMatch(match.id)"
      >
        <div class="match-teams">
          <div class="match-team">
            <div class="team-flag">{{ match.homeTeam.substring(0, 1) }}</div>
            <span>{{ match.homeTeam }}</span>
          </div>
          <div class="match-vs">
            <span>VS</span>
            <small>{{ match.league }}</small>
          </div>
          <div class="match-team">
            <div class="team-flag">{{ match.awayTeam.substring(0, 1) }}</div>
            <span>{{ match.awayTeam }}</span>
          </div>
        </div>
        <div class="match-time">{{ match.time }}</div>
        <div class="match-odds">
          <span class="odd-badge">胜 {{ match.odds.homeWin }}</span>
          <span class="odd-badge">平 {{ match.odds.draw }}</span>
          <span class="odd-badge">负 {{ match.odds.awayWin }}</span>
        </div>
        <button class="favorite-btn active" @click.stop="removeFromFavorites(match.id)">
          <i class="fas fa-star"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const favorites = ref([])

// 模拟收藏数据
const mockFavorites = [
  {
    id: 1,
    homeTeam: "利物浦",
    awayTeam: "曼联",
    league: "英超联赛",
    time: "20:00",
    odds: {
      homeWin: "1.85",
      draw: "3.40",
      awayWin: "4.20"
    }
  },
  {
    id: 2,
    homeTeam: "皇马",
    awayTeam: "巴萨",
    league: "西甲联赛",
    time: "22:15",
    odds: {
      homeWin: "2.10",
      draw: "3.20",
      awayWin: "3.50"
    }
  }
]

const goToMatch = (id) => {
  router.push(`/match/${id}`)
}

const removeFromFavorites = (id) => {
  const index = favorites.value.findIndex(match => match.id === id)
  if (index !== -1) {
    favorites.value.splice(index, 1)
    // 更新本地存储
    localStorage.setItem('favorites', JSON.stringify(favorites.value))
  }
}

// 初始化数据
onMounted(() => {
  // 从本地存储加载收藏数据
  const storedFavorites = localStorage.getItem('favorites')
  if (storedFavorites) {
    favorites.value = JSON.parse(storedFavorites)
  } else {
    favorites.value = [...mockFavorites]
  }
})
</script>

<style scoped>
.favorites-view {
  padding: 16px;
  background: var(--bg-body);
  min-height: 100%;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  color: var(--text-main);
  margin: 0;
}

.favorites-count {
  font-size: 12px;
  color: var(--text-sub);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  color: var(--text-sub);
  margin-bottom: 16px;
}

.empty-description {
  color: var(--text-main);
  font-size: 16px;
  margin-bottom: 8px;
}

.empty-hint {
  color: var(--text-sub);
  font-size: 12px;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.match-item {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.match-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.match-teams {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-team {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.team-flag {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(88, 166, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: var(--primary);
}

.match-vs {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 40px;
}

.match-vs span {
  font-weight: 600;
  color: var(--primary);
}

.match-vs small {
  font-size: 10px;
  color: var(--text-sub);
}

.match-time {
  align-self: flex-start;
  padding: 4px 8px;
  background: rgba(35, 134, 54, 0.1);
  color: var(--success);
  border-radius: 4px;
  font-size: 12px;
}

.match-odds {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.odd-badge {
  background: rgba(88, 166, 255, 0.1);
  color: var(--primary);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.favorite-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-sub);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.favorite-btn.active {
  color: #FFD700;
  background: rgba(255, 215, 0, 0.2);
}

.favorite-btn:hover {
  background: rgba(255, 215, 0, 0.3);
}

/* 移动端适配 */
@media (min-width: 768px) {
  .match-item {
    flex-direction: row;
    align-items: center;
  }
  
  .match-teams {
    flex: 1;
  }
  
  .match-time {
    align-self: auto;
  }
}
</style>