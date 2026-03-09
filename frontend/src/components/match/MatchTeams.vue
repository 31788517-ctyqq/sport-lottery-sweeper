<template>
  <div :class="teamsClasses">
    <!-- 主队信息 -->
    <div class="match-teams__team match-teams__team--home">
      <!-- 队徽 -->
      <div class="match-teams__team-logo">
        <img
          :src="homeTeam.logo"
          :alt="homeTeam.name"
          @error="handleImageError"
        />
      </div>
      
      <!-- 队名和赔率 -->
      <div class="match-teams__team-info">
        <!-- 队名 -->
        <div class="match-teams__team-name">
          <span class="match-teams__team-name-full">{{ homeTeam.name }}</span>
          <span v-if="showShortName && homeTeam.shortName" class="match-teams__team-name-short">
            {{ homeTeam.shortName }}
          </span>
        </div>
        
        <!-- 赔率（如果启用） -->
        <div v-if="showOdds && homeOdds" class="match-teams__team-odds">
          <span class="match-teams__odds-value">{{ formatOdds(homeOdds) }}</span>
          <span v-if="showOddsChange && homeOddsChange" 
                :class="['match-teams__odds-change', getOddsChangeClass(homeOddsChange)]">
            {{ formatOddsChange(homeOddsChange) }}
          </span>
        </div>
      </div>
      
      <!-- 比分（如果已开始） -->
      <div v-if="showScore && homeScore !== null" class="match-teams__team-score">
        <span :class="['match-teams__score-value', { 'match-teams__score-value--winning': isHomeWinning }]">
          {{ homeScore }}
        </span>
      </div>
    </div>

    <!-- VS 分隔符 -->
    <div class="match-teams__vs">
      <span class="match-teams__vs-text">VS</span>
      <div v-if="showScore" class="match-teams__score-separator">
        <span class="match-teams__score-separator-text">{{ homeScore !== null && awayScore !== null ? ':' : 'VS' }}</span>
      </div>
    </div>

    <!-- 客队信息 -->
    <div class="match-teams__team match-teams__team--away">
      <!-- 比分（如果已开始） -->
      <div v-if="showScore && awayScore !== null" class="match-teams__team-score">
        <span :class="['match-teams__score-value', { 'match-teams__score-value--winning': isAwayWinning }]">
          {{ awayScore }}
        </span>
      </div>
      
      <!-- 队名和赔率 -->
      <div class="match-teams__team-info">
        <!-- 队名 -->
        <div class="match-teams__team-name">
          <span class="match-teams__team-name-full">{{ awayTeam.name }}</span>
          <span v-if="showShortName && awayTeam.shortName" class="match-teams__team-name-short">
            {{ awayTeam.shortName }}
          </span>
        </div>
        
        <!-- 赔率（如果启用） -->
        <div v-if="showOdds && awayOdds" class="match-teams__team-odds">
          <span class="match-teams__odds-value">{{ formatOdds(awayOdds) }}</span>
          <span v-if="showOddsChange && awayOddsChange" 
                :class="['match-teams__odds-change', getOddsChangeClass(awayOddsChange)]">
            {{ formatOddsChange(awayOddsChange) }}
          </span>
        </div>
      </div>
      
      <!-- 队徽 -->
      <div class="match-teams__team-logo">
        <img
          :src="awayTeam.logo"
          :alt="awayTeam.name"
          @error="handleImageError"
        />
      </div>
    </div>

    <!-- 平局赔率 -->
    <div v-if="showDrawOdds && drawOdds" class="match-teams__draw-odds">
      <div class="match-teams__draw-label">平局</div>
      <div class="match-teams__draw-value">
        {{ formatOdds(drawOdds) }}
        <span v-if="showOddsChange && drawOddsChange" 
              :class="['match-teams__odds-change', getOddsChangeClass(drawOddsChange)]">
          {{ formatOddsChange(drawOddsChange) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  homeTeam: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      name: '',
      logo: '',
      shortName: ''
    })
  },
  awayTeam: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      name: '',
      logo: '',
      shortName: ''
    })
  },
  homeScore: {
    type: [Number, String],
    default: null
  },
  awayScore: {
    type: [Number, String],
    default: null
  },
  homeOdds: {
    type: [Number, String],
    default: null
  },
  awayOdds: {
    type: [Number, String],
    default: null
  },
  drawOdds: {
    type: [Number, String],
    default: null
  },
  homeOddsChange: {
    type: Number,
    default: null
  },
  awayOddsChange: {
    type: Number,
    default: null
  },
  drawOddsChange: {
    type: Number,
    default: null
  },
  showScore: {
    type: Boolean,
    default: true
  },
  showOdds: {
    type: Boolean,
    default: true
  },
  showDrawOdds: {
    type: Boolean,
    default: false
  },
  showShortName: {
    type: Boolean,
    default: true
  },
  showOddsChange: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  reverse: {
    type: Boolean,
    default: false
  }
})

// 计算属性
const teamsClasses = computed(() => ({
  'match-teams': true,
  'match-teams--compact': props.compact,
  'match-teams--reverse': props.reverse,
  'match-teams--with-score': props.showScore && props.homeScore !== null && props.awayScore !== null,
  'match-teams--with-odds': props.showOdds
}))

const isHomeWinning = computed(() => {
  if (props.homeScore === null || props.awayScore === null) return false
  return props.homeScore > props.awayScore
})

const isAwayWinning = computed(() => {
  if (props.homeScore === null || props.awayScore === null) return false
  return props.awayScore > props.homeScore
})

const isDraw = computed(() => {
  if (props.homeScore === null || props.awayScore === null) return false
  return props.homeScore === props.awayScore
})

// 方法
const formatOdds = (odds) => {
  if (odds === null || odds === undefined) return '-'
  const num = parseFloat(odds)
  return isNaN(num) ? odds : num.toFixed(2)
}

const formatOddsChange = (change) => {
  if (change === null || change === undefined) return ''
  const prefix = change > 0 ? '+' : ''
  return prefix + change.toFixed(2)
}

const getOddsChangeClass = (change) => {
  if (change === null || change === undefined) return ''
  return change > 0 ? 'match-teams__odds-change--up' : 
         change < 0 ? 'match-teams__odds-change--down' : 
         'match-teams__odds-change--same'
}

const handleImageError = (event) => {
  event.target.src = '/images/teams/default.svg'
}
</script>

<style scoped>
.match-teams {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--spacing-4);
  align-items: center;
}

.match-teams--compact {
  gap: var(--spacing-2);
}

.match-teams--reverse .match-teams__team--home {
  order: 3;
}

.match-teams--reverse .match-teams__team--away {
  order: 1;
}

.match-teams--reverse .match-teams__vs {
  order: 2;
}

.match-teams__team {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.match-teams--compact .match-teams__team {
  gap: var(--spacing-2);
}

.match-teams__team--home {
  justify-content: flex-end;
  text-align: right;
}

.match-teams__team--away {
  justify-content: flex-start;
  text-align: left;
}

.match-teams__team-logo {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.match-teams--compact .match-teams__team-logo {
  width: 32px;
  height: 32px;
}

.match-teams__team-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.match-teams__team-info {
  flex: 1;
  min-width: 0;
}

.match-teams__team-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.match-teams--compact .match-teams__team-name {
  gap: 1px;
}

.match-teams__team-name-full {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.match-teams--compact .match-teams__team-name-full {
  font-size: var(--font-size-sm);
}

.match-teams__team-name-short {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-teams__team-odds {
  margin-top: var(--spacing-1);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.match-teams--compact .match-teams__team-odds {
  margin-top: 2px;
}

.match-teams__odds-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-primary);
  background-color: var(--color-bg-secondary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  min-width: 40px;
  text-align: center;
}

.match-teams__odds-change {
  font-size: var(--font-size-xs);
  padding: 1px 4px;
  border-radius: var(--radius-xs);
}

.match-teams__odds-change--up {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.match-teams__odds-change--down {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
}

.match-teams__odds-change--same {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-secondary);
}

.match-teams__team-score {
  width: 36px;
  flex-shrink: 0;
}

.match-teams--compact .match-teams__team-score {
  width: 28px;
}

.match-teams__score-value {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-text-primary);
  text-align: center;
  line-height: 1;
}

.match-teams--compact .match-teams__score-value {
  font-size: var(--font-size-lg);
}

.match-teams__score-value--winning {
  color: var(--color-success);
}

.match-teams--with-score .match-teams__score-value {
  color: var(--color-text-secondary);
}

.match-teams--with-score .match-teams__score-value--winning {
  color: var(--color-success);
}

.match-teams__vs {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  color: var(--color-text-secondary);
  padding: 0 var(--spacing-2);
}

.match-teams--compact .match-teams__vs {
  gap: var(--spacing-1);
}

.match-teams__vs-text {
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.match-teams__score-separator {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text-secondary);
}

.match-teams--compact .match-teams__score-separator {
  font-size: var(--font-size-base);
}

.match-teams__draw-odds {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-3);
  padding-top: var(--spacing-3);
  border-top: 1px dashed var(--color-border-light);
}

.match-teams--compact .match-teams__draw-odds {
  margin-top: var(--spacing-2);
  padding-top: var(--spacing-2);
}

.match-teams__draw-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.match-teams__draw-value {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-primary);
  background-color: var(--color-bg-secondary);
  padding: 4px 12px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* 响应式 */
@media (max-width: 640px) {
  .match-teams {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .match-teams__team {
    gap: var(--spacing-3);
  }
  
  .match-teams__team--home,
  .match-teams__team--away {
    justify-content: center;
    text-align: center;
  }
  
  .match-teams__vs {
    order: 2;
    flex-direction: row;
    justify-content: center;
    gap: var(--spacing-4);
  }
  
  .match-teams__draw-odds {
    order: 3;
  }
}
</style>