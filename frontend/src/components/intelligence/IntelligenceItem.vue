<template>
  <BaseCard :class="itemClasses" :hoverable="hoverable" :clickable="clickable" @click="$emit('click', intelligence)">
    <!-- 情报头部：标题和状态 -->
    <template v-slot:header>
      <div class="intel-item__header">
        <div class="intel-item__header-left">
          <!-- 情报类型标签 -->
          <span :class="['intel-item__type', `intel-item__type--${intelligence.type}`]">
            {{ getTypeLabel(intelligence.type) }}
          </span>
          
          <!-- 情报标题 -->
          <h3 class="intel-item__title">{{ intelligence.title }}</h3>
        </div>
        
        <div class="intel-item__header-right">
          <!-- 权重显示 -->
          <IntelWeight 
            v-if="showWeight" 
            :weight="intelligence.weight" 
            :size="weightSize" 
            :show-label="showWeightLabel"
          />
          
          <!-- 状态标签 -->
          <span v-if="intelligence.status" :class="['intel-item__status', `intel-item__status--${intelligence.status}`]">
            {{ getStatusLabel(intelligence.status) }}
          </span>
        </div>
      </div>
    </template>

    <!-- 情报内容 -->
    <div class="intel-item__content">
      <!-- 主要内容 -->
      <div class="intel-item__main">
        <p class="intel-item__description">{{ intelligence.description }}</p>
        
        <!-- 关键信息 -->
        <div v-if="intelligence.keyPoints && intelligence.keyPoints.length > 0" class="intel-item__key-points">
          <h4 class="intel-item__key-points-title">关键信息</h4>
          <ul class="intel-item__key-points-list">
            <li v-for="(point, index) in intelligence.keyPoints" :key="index" class="intel-item__key-point">
              {{ point }}
            </li>
          </ul>
        </div>
        
        <!-- 证据/引用 -->
        <div v-if="intelligence.evidence" class="intel-item__evidence">
          <div class="intel-item__evidence-title">依据</div>
          <div class="intel-item__evidence-content">{{ intelligence.evidence }}</div>
        </div>
        
        <!-- 影响分析 -->
        <div v-if="intelligence.impact && showImpact" class="intel-item__impact">
          <div class="intel-item__impact-title">影响分析</div>
          <div class="intel-item__impact-content">{{ intelligence.impact }}</div>
        </div>
      </div>

      <!-- 侧边栏信息 -->
      <div v-if="showSidebar" class="intel-item__sidebar">
        <!-- 来源信息 -->
        <IntelSource 
          v-if="intelligence.source"
          :source="intelligence.source"
          :show-credibility="showSourceCredibility"
          :compact="compact"
        />
        
        <!-- 发布时间 -->
        <div v-if="intelligence.publishedAt" class="intel-item__publish-time">
          <span class="intel-item__time-label">发布时间</span>
          <span class="intel-item__time-value">{{ formatDateTime(intelligence.publishedAt) }}</span>
        </div>
        
        <!-- 有效时间 -->
        <div v-if="intelligence.validUntil" class="intel-item__valid-until">
          <span class="intel-item__time-label">有效至</span>
          <span class="intel-item__time-value">{{ formatDateTime(intelligence.validUntil) }}</span>
        </div>
        
        <!-- 标签 -->
        <IntelTags 
          v-if="intelligence.tags && intelligence.tags.length > 0"
          :tags="intelligence.tags"
          :limit="tagsLimit"
          :size="tagsSize"
          :clickable="tagsClickable"
          @tag-click="$emit('tag-click', $event)"
        />
        
        <!-- 相关比赛 -->
        <div v-if="intelligence.relatedMatches && intelligence.relatedMatches.length > 0" class="intel-item__related-matches">
          <div class="intel-item__related-title">相关比赛</div>
          <div class="intel-item__related-list">
            <span v-for="match in intelligence.relatedMatches" :key="match.id" class="intel-item__related-match">
              {{ match.homeTeam }} vs {{ match.awayTeam }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 情报底部：操作和统计 -->
    <template v-if="showFooter" v-slot:footer>
      <div class="intel-item__footer">
        <div class="intel-item__footer-left">
          <!-- 收藏按钮 -->
          <button
            v-if="showFavorite"
            :class="['intel-item__favorite', { 'intel-item__favorite--active': intelligence.isFavorite }]"
            @click.stop="toggleFavorite"
            aria-label="收藏情报"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <path v-if="intelligence.isFavorite" fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              <path v-else fill="currentColor" d="M16.5 3c-1.74 0-3.41.81-4.5 2.09C10.91 3.81 9.24 3 7.5 3 4.42 3 2 5.42 2 8.5c0 3.78 3.4 6.86 8.55 11.54L12 21.35l1.45-1.32C18.6 15.36 22 12.28 22 8.5 22 5.42 19.58 3 16.5 3zm-4.4 15.55l-.1.1-.1-.1C7.14 14.24 4 11.39 4 8.5 4 6.5 5.5 5 7.5 5c1.54 0 3.04.99 3.57 2.36h1.87C13.46 5.99 14.96 5 16.5 5c2 0 3.5 1.5 3.5 3.5 0 2.89-3.14 5.74-7.9 10.05z"/>
            </svg>
            <span v-if="!compact">收藏</span>
          </button>

          <!-- 查看次数 -->
          <div v-if="intelligence.viewCount !== undefined" class="intel-item__views">
            <svg width="14" height="14" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
            </svg>
            <span>{{ intelligence.viewCount }}</span>
          </div>

          <!-- 点赞/有用 -->
          <button
            v-if="showVote"
            :class="['intel-item__vote', { 'intel-item__vote--active': intelligence.userVote === 'useful' }]"
            @click.stop="vote('useful')"
            aria-label="有用"
          >
            <svg width="14" height="14" viewBox="0 0 24 24">
              <path fill="currentColor" d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-1.91l-.01-.01L23 10z"/>
            </svg>
            <span>{{ intelligence.usefulCount || 0 }}</span>
          </button>

          <!-- 无用 -->
          <button
            v-if="showVote"
            :class="['intel-item__vote', 'intel-item__vote--down', { 'intel-item__vote--active': intelligence.userVote === 'useless' }]"
            @click.stop="vote('useless')"
            aria-label="无用"
          >
            <svg width="14" height="14" viewBox="0 0 24 24">
              <path fill="currentColor" d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v1.91l.01.01L1 14c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/>
            </svg>
            <span>{{ intelligence.uselessCount || 0 }}</span>
          </button>
        </div>

        <div class="intel-item__footer-right">
          <!-- 分享按钮 -->
          <button
            v-if="showShare"
            class="intel-item__share"
            @click.stop="$emit('share', intelligence)"
            aria-label="分享"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
            </svg>
          </button>

          <!-- 更多操作 -->
          <button
            v-if="showMoreActions"
            class="intel-item__more"
            @click.stop="$emit('more-actions', intelligence)"
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
    <div v-if="badges.length > 0" class="intel-item__badges">
      <span
        v-for="badge in badges"
        :key="badge.type"
        :class="['intel-item__badge', `intel-item__badge--${badge.type}`]"
      >
        {{ badge.text }}
      </span>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="intel-item__loading">
      <LoadingSpinner size="small" />
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseCard from '../common/BaseCard.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import IntelWeight from './IntelWeight.vue'
import IntelSource from './IntelSource.vue'
import IntelTags from './IntelTags.vue'
import { formatDateTime } from '@/utils/date'

const props = defineProps({
  intelligence: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      type: 'news',
      title: '',
      description: '',
      source: {},
      weight: 0,
      tags: [],
      status: 'active',
      publishedAt: '',
      validUntil: '',
      isFavorite: false,
      viewCount: 0,
      usefulCount: 0,
      uselessCount: 0,
      userVote: null,
      keyPoints: [],
      evidence: '',
      impact: '',
      relatedMatches: []
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
  showWeight: {
    type: Boolean,
    default: true
  },
  showWeightLabel: {
    type: Boolean,
    default: false
  },
  showSourceCredibility: {
    type: Boolean,
    default: true
  },
  showImpact: {
    type: Boolean,
    default: false
  },
  showSidebar: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showFavorite: {
    type: Boolean,
    default: true
  },
  showVote: {
    type: Boolean,
    default: true
  },
  showShare: {
    type: Boolean,
    default: false
  },
  showMoreActions: {
    type: Boolean,
    default: false
  },
  weightSize: {
    type: String,
    default: 'medium'
  },
  tagsLimit: {
    type: Number,
    default: 5
  },
  tagsSize: {
    type: String,
    default: 'small'
  },
  tagsClickable: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'click',
  'favorite',
  'unfavorite',
  'vote',
  'share',
  'more-actions',
  'tag-click'
])

// 计算属性
const itemClasses = computed(() => ({
  'intel-item': true,
  'intel-item--compact': props.compact,
  'intel-item--clickable': props.clickable,
  'intel-item--loading': props.loading,
  [`intel-item--${props.intelligence.type}`]: true,
  [`intel-item--weight-${getWeightLevel(props.intelligence.weight)}`]: true
}))

const badges = computed(() => {
  const badges = []
  
  if (props.intelligence.isVerified) {
    badges.push({ type: 'verified', text: '已验证' })
  }
  
  if (props.intelligence.isExclusive) {
    badges.push({ type: 'exclusive', text: '独家' })
  }
  
  if (props.intelligence.isBreaking) {
    badges.push({ type: 'breaking', text: '突发' })
  }
  
  if (props.intelligence.weight >= 8) {
    badges.push({ type: 'important', text: '重要' })
  }
  
  return badges
})

// 方法
const getTypeLabel = (type) => {
  const typeMap = {
    news: '新闻',
    injury: '伤病',
    lineup: '阵容',
    suspension: '停赛',
    weather: '天气',
    referee: '裁判',
    venue: '场地',
    manager: '教练',
    transfer: '转会',
    form: '状态',
    tactical: '战术',
    history: '历史',
    statistic: '统计',
    prediction: '预测',
    other: '其他'
  }
  return typeMap[type] || type
}

const getStatusLabel = (status) => {
  const statusMap = {
    active: '有效',
    expired: '过期',
    pending: '待确认',
    confirmed: '已确认',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

const getWeightLevel = (weight) => {
  if (weight >= 8) return 'high'
  if (weight >= 5) return 'medium'
  return 'low'
}

const toggleFavorite = () => {
  if (props.intelligence.isFavorite) {
    emit('unfavorite', props.intelligence)
  } else {
    emit('favorite', props.intelligence)
  }
}

const vote = (type) => {
  emit('vote', { intelligence: props.intelligence, type })
}
</script>

<style scoped>
.intel-item {
  position: relative;
  transition: all 0.3s ease;
}

.intel-item--compact {
  padding: var(--spacing-3) !important;
}

.intel-item--clickable {
  cursor: pointer;
}

.intel-item--clickable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.intel-item--weight-high {
  border-left: 3px solid var(--color-danger);
}

.intel-item--weight-medium {
  border-left: 3px solid var(--color-warning);
}

.intel-item--weight-low {
  border-left: 3px solid var(--color-info);
}

.intel-item__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-3);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-border-light);
}

.intel-item--compact .intel-item__header {
  padding-bottom: var(--spacing-2);
  gap: var(--spacing-2);
}

.intel-item__header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex: 1;
  min-width: 0;
}

.intel-item__header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex-shrink: 0;
}

.intel-item__type {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  flex-shrink: 0;
}

.intel-item__type--news {
  background-color: var(--color-info-light);
  color: var(--color-info-dark);
}

.intel-item__type--injury {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
}

.intel-item__type--lineup {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.intel-item__type--suspension {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.intel-item__type--weather {
  background-color: var(--color-secondary-light);
  color: var(--color-secondary-dark);
}

.intel-item__type--referee {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.intel-item__title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.intel-item--compact .intel-item__title {
  font-size: var(--font-size-sm);
}

.intel-item__status {
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 600;
  white-space: nowrap;
}

.intel-item__status--active {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.intel-item__status--expired {
  background-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}

.intel-item__status--pending {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.intel-item__status--confirmed {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.intel-item__status--rejected {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
}

.intel-item__content {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--spacing-6);
  padding: var(--spacing-4) 0;
}

.intel-item--compact .intel-item__content {
  grid-template-columns: 1fr;
  gap: var(--spacing-3);
  padding: var(--spacing-3) 0;
}

.intel-item__main {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.intel-item--compact .intel-item__main {
  gap: var(--spacing-3);
}

.intel-item__description {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  line-height: 1.6;
}

.intel-item--compact .intel-item__description {
  font-size: var(--font-size-sm);
}

.intel-item__key-points {
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--spacing-4);
}

.intel-item--compact .intel-item__key-points {
  padding: var(--spacing-3);
}

.intel-item__key-points-title {
  margin: 0 0 var(--spacing-3);
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.intel-item__key-points-list {
  margin: 0;
  padding-left: var(--spacing-4);
  list-style-type: disc;
}

.intel-item__key-point {
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  line-height: 1.5;
}

.intel-item__key-point:last-child {
  margin-bottom: 0;
}

.intel-item__evidence,
.intel-item__impact {
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--spacing-4);
}

.intel-item--compact .intel-item__evidence,
.intel-item--compact .intel-item__impact {
  padding: var(--spacing-3);
}

.intel-item__evidence-title,
.intel-item__impact-title {
  margin: 0 0 var(--spacing-2);
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.intel-item__evidence-content,
.intel-item__impact-content {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.intel-item__sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  border-left: 1px solid var(--color-border-light);
  padding-left: var(--spacing-6);
}

.intel-item--compact .intel-item__sidebar {
  width: 100%;
  border-left: none;
  border-top: 1px solid var(--color-border-light);
  padding-left: 0;
  padding-top: var(--spacing-4);
}

.intel-item__publish-time,
.intel-item__valid-until {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.intel-item__time-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.intel-item__time-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.intel-item__related-matches {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.intel-item__related-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.intel-item__related-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.intel-item__related-match {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  padding: var(--spacing-1) var(--spacing-2);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
}

.intel-item__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3) 0 0;
  border-top: 1px solid var(--color-border-light);
}

.intel-item--compact .intel-item__footer {
  padding: var(--spacing-2) 0 0;
}

.intel-item__footer-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.intel-item__footer-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.intel-item__favorite,
.intel-item__vote,
.intel-item__share,
.intel-item__more {
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

.intel-item__favorite:hover,
.intel-item__vote:hover,
.intel-item__share:hover,
.intel-item__more:hover {
  background-color: var(--color-bg-secondary);
}

.intel-item__favorite--active {
  color: var(--color-danger);
}

.intel-item__favorite--active:hover {
  color: var(--color-danger-dark);
}

.intel-item__vote--active {
  color: var(--color-success);
}

.intel-item__vote--down.intel-item__vote--active {
  color: var(--color-danger);
}

.intel-item__views {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.intel-item__badges {
  position: absolute;
  top: var(--spacing-3);
  right: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  z-index: 2;
}

.intel-item__badge {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: var(--shadow-sm);
}

.intel-item__badge--verified {
  background-color: var(--color-success);
  color: white;
}

.intel-item__badge--exclusive {
  background-color: var(--color-warning);
  color: white;
}

.intel-item__badge--breaking {
  background-color: var(--color-danger);
  color: white;
}

.intel-item__badge--important {
  background-color: var(--color-primary);
  color: white;
}

.intel-item__loading {
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

/* 响应式 */
@media (max-width: 768px) {
  .intel-item__content {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .intel-item__sidebar {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--color-border-light);
    padding-left: 0;
    padding-top: var(--spacing-4);
  }
  
  .intel-item__footer {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }
  
  .intel-item__footer-right {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>