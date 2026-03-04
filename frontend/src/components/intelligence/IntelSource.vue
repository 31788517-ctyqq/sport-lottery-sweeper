<template>
  <div :class="sourceClasses" @click="handleClick">
    <!-- 来源图标/Logo -->
    <div v-if="showLogo && source.logo" class="intel-source__logo">
      <img
        :src="source.logo"
        :alt="source.name"
        @error="handleImageError"
        class="intel-source__logo-img"
      />
    </div>

    <div class="intel-source__content">
      <!-- 来源名称 -->
      <div class="intel-source__name">
        <span class="intel-source__name-text">{{ source.name }}</span>
        
        <!-- 验证状态 -->
        <span v-if="showVerified && source.verified" class="intel-source__verified">
          <svg width="14" height="14" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/>
          </svg>
        </span>
      </div>

      <!-- 来源类型 -->
      <div v-if="showType && source.type" class="intel-source__type">
        <span class="intel-source__type-label">{{ getTypeLabel(source.type) }}</span>
      </div>

      <!-- 可信度 -->
      <div v-if="showCredibility && source.credibility !== undefined" class="intel-source__credibility">
        <span class="intel-source__credibility-label">可信度:</span>
        <span class="intel-source__credibility-value">
          {{ formatCredibility(source.credibility) }}
        </span>
        <div v-if="showCredibilityBar" class="intel-source__credibility-bar">
          <div
            class="intel-source__credibility-fill"
            :style="{ width: `${source.credibility * 10}%` }"
            :class="getCredibilityClass(source.credibility)"
          ></div>
        </div>
      </div>

      <!-- 来源网址 -->
      <div v-if="showUrl && source.url" class="intel-source__url">
        <a
          :href="source.url"
          target="_blank"
          rel="noopener noreferrer"
          class="intel-source__url-link"
          @click.stop
        >
          {{ formatUrl(source.url) }}
          <svg width="12" height="12" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
          </svg>
        </a>
      </div>

      <!-- 发布时间 -->
      <div v-if="showTimestamp && source.timestamp" class="intel-source__timestamp">
        <span class="intel-source__timestamp-label">发布时间:</span>
        <span class="intel-source__timestamp-value">{{ formatTimestamp(source.timestamp) }}</span>
      </div>

      <!-- 来源描述 -->
      <div v-if="showDescription && source.description" class="intel-source__description">
        {{ source.description }}
      </div>

      <!-- 统计信息 -->
      <div v-if="showStats" class="intel-source__stats">
        <div v-if="source.accuracy !== undefined" class="intel-source__stat">
          <span class="intel-source__stat-label">准确率:</span>
          <span class="intel-source__stat-value">{{ (source.accuracy * 100).toFixed(1) }}%</span>
        </div>
        
        <div v-if="source.totalReports !== undefined" class="intel-source__stat">
          <span class="intel-source__stat-label">报告数:</span>
          <span class="intel-source__stat-value">{{ source.totalReports }}</span>
        </div>
        
        <div v-if="source.successRate !== undefined" class="intel-source__stat">
          <span class="intel-source__stat-label">成功率:</span>
          <span class="intel-source__stat-value">{{ (source.successRate * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="showActions" class="intel-source__actions">
      <button
        v-if="showFollowButton"
        :class="['intel-source__follow', { 'intel-source__follow--active': source.isFollowing }]"
        @click.stop="toggleFollow"
        aria-label="关注来源"
      >
        <span v-if="source.isFollowing">已关注</span>
        <span v-else>关注</span>
      </button>
      
      <button
        v-if="showMoreButton"
        class="intel-source__more"
        @click.stop="$emit('more-actions', source)"
        aria-label="更多操作"
      >
        <svg width="16" height="16" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
          <circle cx="6" cy="12" r="1.5" fill="currentColor"/>
          <circle cx="18" cy="12" r="1.5" fill="currentColor"/>
        </svg>
      </button>
    </div>

    <!-- 角标 -->
    <div v-if="showBadge && source.badge" class="intel-source__badge">
      <span :class="['intel-source__badge-text', `intel-source__badge-text--${source.badge.type || 'default'}`]">
        {{ source.badge.text }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDateTime } from '@/utils/date'

const props = defineProps({
  source: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      name: '',
      type: 'media',
      logo: '',
      url: '',
      credibility: 0.5,
      verified: false,
      description: '',
      timestamp: '',
      accuracy: null,
      totalReports: null,
      successRate: null,
      isFollowing: false,
      badge: null
    })
  },
  compact: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: true
  },
  showLogo: {
    type: Boolean,
    default: true
  },
  showType: {
    type: Boolean,
    default: true
  },
  showCredibility: {
    type: Boolean,
    default: true
  },
  showCredibilityBar: {
    type: Boolean,
    default: true
  },
  showVerified: {
    type: Boolean,
    default: true
  },
  showUrl: {
    type: Boolean,
    default: false
  },
  showTimestamp: {
    type: Boolean,
    default: true
  },
  showDescription: {
    type: Boolean,
    default: false
  },
  showStats: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: false
  },
  showFollowButton: {
    type: Boolean,
    default: true
  },
  showMoreButton: {
    type: Boolean,
    default: false
  },
  showBadge: {
    type: Boolean,
    default: true
  },
  credibilityFormat: {
    type: String,
    default: 'percentage', // 'percentage', 'rating', 'text'
    validator: (value) => ['percentage', 'rating', 'text'].includes(value)
  }
})

const emit = defineEmits(['click', 'follow', 'unfollow', 'more-actions'])

// 计算属性
const sourceClasses = computed(() => ({
  'intel-source': true,
  'intel-source--compact': props.compact,
  'intel-source--clickable': props.clickable,
  'intel-source--verified': props.source.verified,
  'intel-source--high-credibility': props.source.credibility >= 0.8,
  'intel-source--medium-credibility': props.source.credibility >= 0.5 && props.source.credibility < 0.8,
  'intel-source--low-credibility': props.source.credibility < 0.5
}))

// 方法
const getTypeLabel = (type) => {
  const typeMap = {
    media: '媒体',
    official: '官方',
    insider: '内幕',
    analyst: '分析师',
    bookmaker: '博彩公司',
    data: '数据源',
    community: '社区',
    other: '其他'
  }
  return typeMap[type] || type
}

const formatCredibility = (credibility) => {
  if (props.credibilityFormat === 'percentage') {
    return `${(credibility * 100).toFixed(0)}%`
  } else if (props.credibilityFormat === 'rating') {
    return credibility.toFixed(1)
  } else {
    if (credibility >= 0.8) return '非常高'
    if (credibility >= 0.6) return '高'
    if (credibility >= 0.4) return '中等'
    return '低'
  }
}

const getCredibilityClass = (credibility) => {
  if (credibility >= 0.8) return 'intel-source__credibility-fill--high'
  if (credibility >= 0.6) return 'intel-source__credibility-fill--medium'
  if (credibility >= 0.4) return 'intel-source__credibility-fill--low'
  return 'intel-source__credibility-fill--very-low'
}

const formatUrl = (url) => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace('www.', '')
  } catch {
    return url
  }
}

const formatTimestamp = (timestamp) => {
  return formatDateTime(timestamp, 'MM/dd HH:mm')
}

const handleClick = () => {
  if (props.clickable) {
    emit('click', props.source)
  }
}

const handleImageError = (event) => {
  event.target.src = '/images/sources/default.svg'
}

const toggleFollow = () => {
  if (props.source.isFollowing) {
    emit('unfollow', props.source)
  } else {
    emit('follow', props.source)
  }
}
</script>

<style scoped>
.intel-source {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.intel-source--compact {
  padding: var(--spacing-2);
  gap: var(--spacing-2);
}

.intel-source--clickable {
  cursor: pointer;
}

.intel-source--clickable:hover {
  background-color: var(--color-bg-tertiary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.intel-source--verified {
  border-left: 3px solid var(--color-success);
}

.intel-source--high-credibility {
  border-right: 3px solid var(--color-success);
}

.intel-source--medium-credibility {
  border-right: 3px solid var(--color-warning);
}

.intel-source--low-credibility {
  border-right: 3px solid var(--color-danger);
}

.intel-source__logo {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
}

.intel-source--compact .intel-source__logo {
  width: 36px;
  height: 36px;
}

.intel-source__logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

.intel-source__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.intel-source__name {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.intel-source__name-text {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.intel-source--compact .intel-source__name-text {
  font-size: var(--font-size-sm);
}

.intel-source__verified {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-success);
  flex-shrink: 0;
}

.intel-source__type {
  margin-top: 2px;
}

.intel-source__type-label {
  display: inline-block;
  padding: 2px 6px;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.intel-source__credibility {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-1);
}

.intel-source__credibility-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.intel-source__credibility-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  min-width: 40px;
}

.intel-source__credibility-bar {
  flex: 1;
  height: 6px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
  min-width: 60px;
}

.intel-source__credibility-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s ease;
}

.intel-source__credibility-fill--high {
  background-color: var(--color-success);
}

.intel-source__credibility-fill--medium {
  background-color: var(--color-warning);
}

.intel-source__credibility-fill--low {
  background-color: var(--color-danger);
}

.intel-source__credibility-fill--very-low {
  background-color: var(--color-text-tertiary);
}

.intel-source__url {
  margin-top: var(--spacing-1);
}

.intel-source__url-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.intel-source__url-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.intel-source__timestamp {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin-top: var(--spacing-1);
}

.intel-source__timestamp-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.intel-source__timestamp-value {
  font-size: var(--font-size-xs);
  color: var(--color-text-primary);
  font-weight: 500;
}

.intel-source__description {
  margin-top: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.intel-source__stats {
  display: flex;
  gap: var(--spacing-3);
  margin-top: var(--spacing-2);
  padding-top: var(--spacing-2);
  border-top: 1px solid var(--color-border-light);
}

.intel-source__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 60px;
}

.intel-source__stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.intel-source__stat-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.intel-source__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  flex-shrink: 0;
}

.intel-source__follow {
  padding: var(--spacing-1) var(--spacing-3);
  border: 1px solid var(--color-border);
  background-color: transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.intel-source__follow:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.intel-source__follow--active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.intel-source__follow--active:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.intel-source__more {
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

.intel-source__more:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.intel-source__badge {
  position: absolute;
  top: -6px;
  right: -6px;
  z-index: 1;
}

.intel-source__badge-text {
  display: inline-block;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: var(--shadow-sm);
}

.intel-source__badge-text--official {
  background-color: var(--color-success);
  color: white;
}

.intel-source__badge-text--verified {
  background-color: var(--color-primary);
  color: white;
}

.intel-source__badge-text--premium {
  background-color: var(--color-warning);
  color: white;
}

.intel-source__badge-text--recommended {
  background-color: var(--color-info);
  color: white;
}

/* 响应式 */
@media (max-width: 640px) {
  .intel-source {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-2);
  }
  
  .intel-source__logo {
    width: 40px;
    height: 40px;
  }
  
  .intel-source__actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>