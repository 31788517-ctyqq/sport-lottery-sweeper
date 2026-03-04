<template>
  <BaseCard
    :class="cardClasses"
    :hoverable="hoverable"
    :clickable="clickable"
    @click="$emit('click', match)"
  >
    <!-- 头部：比赛状态和时间 -->
    <template v-slot:header>
      <MatchHeader
        :status="match.status"
        :time="match.time"
        :date="match.date"
        :league="match.league"
        :round="match.round"
        :live="isLive"
        :show-countdown="showCountdown"
      />
    </template>

    <!-- 内容：球队和赔率 -->
    <div class="match-card__content">
      <!-- 球队信息 -->
      <MatchTeams
        :home-team="match.homeTeam"
        :away-team="match.awayTeam"
        :home-score="match.homeScore"
        :away-score="match.awayScore"
        :home-odds="match.homeOdds"
        :away-odds="match.awayOdds"
        :show-odds="showOdds"
        :compact="compact"
      />

      <!-- 赔率信息（如果启用） -->
      <div v-if="showOddsDetails" class="match-card__odds">
        <MatchOdds
          :odds="match.odds"
          :type="oddsType"
          :compact="compact"
          :show-change="showOddsChange"
        />
      </div>

      <!-- 统计摘要 -->
      <div v-if="showStatsSummary" class="match-card__stats-summary">
        <MatchStats
          :stats="match.stats"
          :show="statsToShow"
          :compact="compact"
          :type="statsType"
        />
      </div>

      <!-- 情报标签 -->
      <div v-if="match.intelligence?.length > 0 && showIntelTags" class="match-card__intel-tags">
        <IntelTags :tags="match.intelligence" :limit="intelTagsLimit" />
      </div>
    </div>

    <!-- 底部：操作按钮和额外信息 -->
    <template v-if="showFooter" v-slot:footer>
      <div class="match-card__footer">
        <div class="match-card__footer-left">
          <!-- 收藏按钮 -->
          <button
            v-if="showFavorite"
            :class="['match-card__favorite', { 'match-card__favorite--active': isFavorite }]"
            @click.stop="toggleFavorite"
            aria-label="收藏比赛"
          >
            <svg :class="['match-card__favorite-icon', { 'animate-pulse': favoriting }]" width="18" height="18" viewBox="0 0 24 24">
              <path v-if="isFavorite" fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              <path v-else fill="currentColor" d="M16.5 3c-1.74 0-3.41.81-4.5 2.09C10.91 3.81 9.24 3 7.5 3 4.42 3 2 5.42 2 8.5c0 3.78 3.4 6.86 8.55 11.54L12 21.35l1.45-1.32C18.6 15.36 22 12.28 22 8.5 22 5.42 19.58 3 16.5 3zm-4.4 15.55l-.1.1-.1-.1C7.14 14.24 4 11.39 4 8.5 4 6.5 5.5 5 7.5 5c1.54 0 3.04.99 3.57 2.36h1.87C13.46 5.99 14.96 5 16.5 5c2 0 3.5 1.5 3.5 3.5 0 2.89-3.14 5.74-7.9 10.05z"/>
            </svg>
            <span v-if="!compact">收藏</span>
          </button>

          <!-- 情报数量 -->
          <div v-if="match.intelligenceCount > 0" class="match-card__intel-count">
            <span class="match-card__intel-badge">{{ match.intelligenceCount }}</span>
            <span v-if="!compact">条情报</span>
          </div>
        </div>

        <div class="match-card__footer-right">
          <!-- 更多操作按钮 -->
          <button
            v-if="showMoreActions"
            class="match-card__more-actions"
            @click.stop="$emit('more-actions', match)"
            aria-label="更多操作"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
              <circle cx="6" cy="12" r="1.5" fill="currentColor"/>
              <circle cx="18" cy="12" r="1.5" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </div>
    </template>

    <!-- 角标 -->
    <div v-if="badges.length > 0" class="match-card__badges">
      <span
        v-for="badge in badges"
        :key="badge.type"
        :class="['match-card__badge', `match-card__badge--${badge.type}`]"
      >
        {{ badge.text }}
      </span>
    </div>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="match-card__loading">
      <LoadingSpinner size="small" />
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseCard from '../common/BaseCard.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import MatchHeader from './MatchHeader.vue'
import MatchTeams from './MatchTeams.vue'
import MatchOdds from './MatchOdds.vue'
import MatchStats from './MatchStats.vue'
import IntelTags from '../intelligence/IntelTags.vue'

const props = defineProps({
  match: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      status: 'scheduled',
      date: '',
      time: '',
      league: {
        id: '',
        name: '',
        logo: ''
      },
      round: '',
      homeTeam: {
        id: '',
        name: '',
        logo: '',
        shortName: ''
      },
      awayTeam: {
        id: '',
        name: '',
        logo: '',
        shortName: ''
      },
      homeScore: null,
      awayScore: null,
      homeOdds: null,
      awayOdds: null,
      odds: {},
      stats: {},
      intelligence: [],
      intelligenceCount: 0,
      isFavorite: false
    })
  },
  compact: {
    type: Boolean,
    default: false
  },
  hoverable: {
    type: Boolean,
    default: true
  },
  clickable: {
    type: Boolean,
    default: true
  },
  showOdds: {
    type: Boolean,
    default: true
  },
  showOddsDetails: {
    type: Boolean,
    default: false
  },
  showStatsSummary: {
    type: Boolean,
    default: true
  },
  showIntelTags: {
    type: Boolean,
    default: true
  },
  showFavorite: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showMoreActions: {
    type: Boolean,
    default: false
  },
  showCountdown: {
    type: Boolean,
    default: true
  },
  oddsType: {
    type: String,
    default: '1x2', // '1x2', 'asian', 'over-under'
  },
  statsType: {
    type: String,
    default: 'summary', // 'summary', 'detailed', 'advanced'
  },
  statsToShow: {
    type: Array,
    default: () => ['shots', 'possession', 'corners']
  },
  intelTagsLimit: {
    type: Number,
    default: 3
  },
  showOddsChange: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'favorite', 'unfavorite', 'more-actions'])

const favoriting = ref(false)

// 计算属性
const isLive = computed(() => props.match.status === 'live')
const isFinished = computed(() => props.match.status === 'finished')
const isScheduled = computed(() => props.match.status === 'scheduled')

const cardClasses = computed(() => ({
  'match-card': true,
  'match-card--compact': props.compact,
  'match-card--live': isLive.value,
  'match-card--finished': isFinished.value,
  'match-card--scheduled': isScheduled.value,
  'match-card--clickable': props.clickable,
  'match-card--loading': props.loading
}))

const isFavorite = computed(() => props.match.isFavorite)

const badges = computed(() => {
  const badges = []
  
  if (isLive.value) {
    badges.push({ type: 'live', text: '直播中' })
  }
  
  if (props.match.intelligenceCount > 5) {
    badges.push({ type: 'hot', text: '热门' })
  }
  
  if (props.match.odds && props.match.odds.riskLevel === 'high') {
    badges.push({ type: 'risk', text: '高风险' })
  }
  
  return badges
})

// 方法
const toggleFavorite = async () => {
  if (favoriting.value) return
  
  favoriting.value = true
  
  if (isFavorite.value) {
    emit('unfavorite', props.match)
  } else {
    emit('favorite', props.match)
  }
  
  // 模拟API调用延迟
  setTimeout(() => {
    favoriting.value = false
  }, 300)
}
</script>

<style scoped>
.match-card {
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
}

.match-card--compact {
  padding: var(--spacing-3) !important;
}

.match-card--live {
  border-left: 3px solid var(--color-danger);
  background: linear-gradient(90deg, rgba(var(--color-danger-rgb), 0.05) 0%, transparent 100%);
}

.match-card--finished {
  border-left: 3px solid var(--color-success);
}

.match-card--scheduled {
  border-left: 3px solid var(--color-primary);
}

.match-card--clickable {
  cursor: pointer;
}

.match-card--clickable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.match-card__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.match-card--compact .match-card__content {
  gap: var(--spacing-3);
}

.match-card__odds {
  margin-top: var(--spacing-2);
}

.match-card__stats-summary {
  margin-top: var(--spacing-3);
}

.match-card__intel-tags {
  margin-top: var(--spacing-3);
}

.match-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3) 0 0;
  border-top: 1px solid var(--color-border-light);
}

.match-card--compact .match-card__footer {
  padding: var(--spacing-2) 0 0;
}

.match-card__footer-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.match-card__footer-right {
  display: flex;
  align-items: center;
}

.match-card__favorite {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  font-size: var(--font-size-sm);
}

.match-card__favorite:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-primary);
}

.match-card__favorite--active {
  color: var(--color-danger);
}

.match-card__favorite--active:hover {
  color: var(--color-danger-dark);
}

.match-card__favorite-icon {
  transition: all 0.2s ease;
}

.animate-pulse {
  animation: pulse 0.6s ease-in-out;
}

.match-card__intel-count {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.match-card__intel-badge {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.match-card__more-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.match-card__more-actions:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.match-card__badges {
  position: absolute;
  top: var(--spacing-3);
  right: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  z-index: 2;
}

.match-card__badge {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: var(--shadow-sm);
}

.match-card__badge--live {
  background-color: var(--color-danger);
  color: white;
}

.match-card__badge--hot {
  background-color: var(--color-warning);
  color: white;
}

.match-card__badge--risk {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
}

.match-card__loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .match-card {
    margin: 0 var(--spacing-2);
  }
  
  .match-card__footer {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-2);
  }
  
  .match-card__footer-right {
    width: 100%;
    justify-content: flex-end;
  }
  
  .match-card__badges {
    top: var(--spacing-2);
    right: var(--spacing-2);
  }
}
</style>