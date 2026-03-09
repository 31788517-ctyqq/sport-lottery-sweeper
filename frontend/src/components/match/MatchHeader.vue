<template>
  <div :class="headerClasses">
    <!-- 联赛信息 -->
    <div class="match-header__league">
      <div v-if="leagueLogo" class="match-header__league-logo">
        <img :src="leagueLogo" :alt="leagueName" />
      </div>
      <div class="match-header__league-info">
        <h3 class="match-header__league-name">{{ leagueName }}</h3>
        <div v-if="round" class="match-header__league-round">{{ round }}</div>
      </div>
    </div>

    <!-- 比赛状态和时间 -->
    <div class="match-header__status">
      <!-- 状态标签 -->
      <span :class="['match-header__status-tag', `match-header__status-tag--${status}`]">
        {{ statusText }}
      </span>

      <!-- 时间显示 -->
      <div class="match-header__time">
        <template v-if="isLive">
          <span class="match-header__live-indicator"></span>
          <span class="match-header__live-text">{{ liveTime || '进行中' }}</span>
        </template>
        
        <template v-else-if="isScheduled">
          <div class="match-header__schedule">
            <div class="match-header__date">{{ formattedDate }}</div>
            <div class="match-header__time-value">{{ formattedTime }}</div>
          </div>
          
          <!-- 倒计时 -->
          <div v-if="showCountdown && countdown" class="match-header__countdown">
            <span v-if="countdown.days > 0">{{ countdown.days }}天</span>
            <span>{{ countdown.hours.toString().padStart(2, '0') }}</span>:
            <span>{{ countdown.minutes.toString().padStart(2, '0') }}</span>:
            <span>{{ countdown.seconds.toString().padStart(2, '0') }}</span>
          </div>
        </template>
        
        <template v-else-if="isFinished">
          <div class="match-header__finished-time">
            <span>已结束</span>
            <span class="match-header__finish-time">{{ finishedTime }}</span>
          </div>
        </template>
      </div>
    </div>

    <!-- 额外信息 -->
    <div v-if="extraInfo" class="match-header__extra">
      <span class="match-header__extra-text">{{ extraInfo }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { formatDate, formatTime, getCountdown } from '@/utils/date'

const props = defineProps({
  status: {
    type: String,
    default: 'scheduled',
    validator: (value) => ['scheduled', 'live', 'finished', 'postponed', 'cancelled', 'delayed'].includes(value)
  },
  date: {
    type: [String, Date],
    default: ''
  },
  time: {
    type: [String, Date],
    default: ''
  },
  league: {
    type: [String, Object],
    default: ''
  },
  round: {
    type: String,
    default: ''
  },
  leagueLogo: {
    type: String,
    default: ''
  },
  liveTime: {
    type: String,
    default: ''
  },
  finishedTime: {
    type: String,
    default: ''
  },
  showCountdown: {
    type: Boolean,
    default: true
  },
  extraInfo: {
    type: String,
    default: ''
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const countdown = ref(null)
let countdownInterval = null

// 计算属性
const leagueName = computed(() => {
  if (typeof props.league === 'string') return props.league
  return props.league?.name || ''
})

const statusText = computed(() => {
  const statusMap = {
    scheduled: '未开始',
    live: '直播中',
    finished: '已结束',
    postponed: '延期',
    cancelled: '取消',
    delayed: '延迟'
  }
  return statusMap[props.status] || '未知'
})

const isLive = computed(() => props.status === 'live')
const isScheduled = computed(() => props.status === 'scheduled')
const isFinished = computed(() => props.status === 'finished')

const formattedDate = computed(() => {
  if (!props.date) return ''
  return formatDate(props.date, 'MM/dd ddd')
})

const formattedTime = computed(() => {
  if (!props.time) return ''
  return formatTime(props.time, 'HH:mm')
})

const headerClasses = computed(() => ({
  'match-header': true,
  'match-header--compact': props.compact,
  'match-header--live': isLive.value,
  'match-header--scheduled': isScheduled.value,
  'match-header--finished': isFinished.value
}))

// 更新倒计时
const updateCountdown = () => {
  if (!props.date || !props.time || !isScheduled.value) {
    countdown.value = null
    return
  }
  
  const matchDateTime = new Date(`${props.date}T${props.time}`)
  countdown.value = getCountdown(matchDateTime)
}

// 生命周期
onMounted(() => {
  if (isScheduled.value && props.showCountdown) {
    updateCountdown()
    countdownInterval = setInterval(updateCountdown, 1000)
  }
})

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})

// 监听状态变化
watch(() => props.status, (newStatus) => {
  if (newStatus !== 'scheduled' && countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  } else if (newStatus === 'scheduled' && props.showCountdown) {
    updateCountdown()
    countdownInterval = setInterval(updateCountdown, 1000)
  }
})

watch(() => [props.date, props.time], () => {
  if (isScheduled.value && props.showCountdown) {
    updateCountdown()
  }
})
</script>

<style scoped>
.match-header {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-border-light);
}

.match-header--compact {
  gap: var(--spacing-2);
  padding-bottom: var(--spacing-2);
}

.match-header__league {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.match-header__league-logo {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.match-header__league-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.match-header__league-info {
  flex: 1;
  overflow: hidden;
}

.match-header__league-name {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.match-header__league-round {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.match-header__status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-3);
}

.match-header__status-tag {
  padding: 4px 8px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.match-header__status-tag--scheduled {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.match-header__status-tag--live {
  background-color: var(--color-danger);
  color: white;
  animation: pulse 2s infinite;
}

.match-header__status-tag--finished {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.match-header__status-tag--postponed,
.match-header__status-tag--cancelled,
.match-header__status-tag--delayed {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.match-header__time {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.match-header--live .match-header__time {
  color: var(--color-danger);
  font-weight: 600;
}

.match-header__live-indicator {
  width: 8px;
  height: 8px;
  background-color: var(--color-danger);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.match-header__live-text {
  font-weight: 600;
}

.match-header__schedule {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.match-header__date {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-header__time-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.match-header__countdown {
  display: flex;
  align-items: center;
  gap: 2px;
  font-family: 'Monospace', monospace;
  font-size: var(--font-size-xs);
  color: var(--color-warning-dark);
  background-color: var(--color-warning-light);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  margin-left: var(--spacing-2);
}

.match-header__finished-time {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.match-header__finish-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-header__extra {
  margin-top: var(--spacing-1);
}

.match-header__extra-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background-color: var(--color-bg-secondary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  display: inline-block;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .match-header__status {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-2);
  }
  
  .match-header__time {
    width: 100%;
    justify-content: space-between;
  }
  
  .match-header__schedule {
    flex-direction: row;
    align-items: center;
    gap: var(--spacing-2);
  }
  
  .match-header__countdown {
    margin-left: 0;
    margin-top: var(--spacing-1);
  }
}
</style>