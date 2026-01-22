<template>
  <div class="user-level" :class="levelClasses" :title="levelTooltip">
    <!-- 图标模式 -->
    <div v-if="mode === 'icon'" class="level-icon">
      <i :class="levelIcon"></i>
      <span v-if="showLabel" class="level-label">
        {{ levelName }}
      </span>
    </div>

    <!-- 徽章模式 -->
    <div v-else-if="mode === 'badge'" class="level-badge">
      <span class="level-number">Lv.{{ level }}</span>
      <span v-if="showLabel" class="level-name">{{ levelName }}</span>
    </div>

    <!-- 进度条模式 -->
    <div v-else class="level-progress">
      <div class="level-info">
        <span class="level-name">{{ levelName }}</span>
        <span class="level-exp">
          {{ currentExp.toLocaleString() }} / {{ nextLevelExp.toLocaleString() }}
        </span>
      </div>
      
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="progressStyle"
          :class="{ 'progress-animated': animate }"
        ></div>
      </div>
      
      <div v-if="showNextLevel" class="next-level-info">
        下一等级：{{ nextLevelName }} 
        <span class="exp-needed">
          （还需 {{ expNeeded.toLocaleString() }} 经验）
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

// Props
interface Props {
  level: number
  currentExp?: number
  mode?: 'icon' | 'badge' | 'progress'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  showLabel?: boolean
  showNextLevel?: boolean
  animate?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  level: 1,
  currentExp: 0,
  mode: 'badge',
  size: 'md',
  showLabel: true,
  showNextLevel: false,
  animate: false,
  clickable: false
})

// Emits
const emit = defineEmits<{
  'level-click': []
}>()

// 等级配置
const levelConfig = ref([
  { level: 1, name: '新秀', icon: 'fas fa-seedling', color: '#95a5a6', minExp: 0, maxExp: 100 },
  { level: 2, name: '学徒', icon: 'fas fa-graduation-cap', color: '#3498db', minExp: 100, maxExp: 500 },
  { level: 3, name: '专家', icon: 'fas fa-user-tie', color: '#9b59b6', minExp: 500, maxExp: 2000 },
  { level: 4, name: '大师', icon: 'fas fa-crown', color: '#f1c40f', minExp: 2000, maxExp: 10000 },
  { level: 5, name: '宗师', icon: 'fas fa-trophy', color: '#e74c3c', minExp: 10000, maxExp: 50000 },
  { level: 6, name: '传说', icon: 'fas fa-fire', color: '#e67e22', minExp: 50000, maxExp: 200000 },
  { level: 7, name: '神话', icon: 'fas fa-star', color: '#1abc9c', minExp: 200000, maxExp: 1000000 },
  { level: 8, name: '不朽', icon: 'fas fa-infinity', color: '#2ecc71', minExp: 1000000, maxExp: Infinity }
])

// Computed
const currentLevelConfig = computed(() => {
  return levelConfig.value.find(config => config.level === props.level) || levelConfig.value[0]
})

const nextLevelConfig = computed(() => {
  const nextLevel = props.level + 1
  return levelConfig.value.find(config => config.level === nextLevel)
})

const levelName = computed(() => currentLevelConfig.value.name)
const levelIcon = computed(() => currentLevelConfig.value.icon)
const levelColor = computed(() => currentLevelConfig.value.color)

const levelClasses = computed(() => ({
  [`level-${props.mode}`]: true,
  [`level-${props.size}`]: true,
  'level-clickable': props.clickable,
  [`level-${props.level}`]: true
}))

const levelTooltip = computed(() => {
  return `${levelName.value} (Lv.${props.level}) - ${props.currentExp}经验`
})

const nextLevelExp = computed(() => {
  return currentLevelConfig.value.maxExp
})

const expNeeded = computed(() => {
  return Math.max(0, nextLevelExp.value - props.currentExp)
})

const progressPercentage = computed(() => {
  const range = nextLevelExp.value - currentLevelConfig.value.minExp
  const progress = props.currentExp - currentLevelConfig.value.minExp
  return Math.min(100, Math.max(0, (progress / range) * 100))
})

const progressStyle = computed(() => ({
  width: `${progressPercentage.value}%`,
  backgroundColor: levelColor.value
}))

const nextLevelName = computed(() => {
  return nextLevelConfig.value?.name || '已满级'
})

// Methods
const handleClick = () => {
  if (props.clickable) {
    emit('level-click')
  }
}

// Watch
watch(() => props.level, (newLevel, oldLevel) => {
  if (newLevel > oldLevel) {
    // 等级提升效果
    console.log(`等级提升！从 Lv.${oldLevel} 到 Lv.${newLevel}`)
  }
}, { immediate: true })
</script>

<style scoped>
.user-level {
  display: inline-flex;
  align-items: center;
  font-family: var(--font-family-base);
}

.level-clickable {
  cursor: pointer;
}

.level-clickable:hover {
  opacity: 0.8;
}

/* 图标模式 */
.level-icon {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-primary);
}

.level-icon i {
  color: v-bind(levelColor);
}

.level-label {
  font-weight: 500;
  font-size: 0.875rem;
}

/* 徽章模式 */
.level-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, v-bind(levelColor), color-mix(in srgb, v-bind(levelColor) 80%, black));
  color: white;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.level-number {
  font-size: 0.75rem;
  opacity: 0.9;
}

.level-name {
  font-size: 0.75rem;
}

/* 进度条模式 */
.level-progress {
  width: 100%;
  min-width: 200px;
}

.level-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.level-info .level-name {
  font-weight: 600;
  color: v-bind(levelColor);
}

.level-info .level-exp {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.progress-animated {
  background: linear-gradient(
    90deg,
    v-bind(levelColor),
    color-mix(in srgb, v-bind(levelColor) 60%, white),
    v-bind(levelColor)
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.next-level-info {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.exp-needed {
  font-size: 0.7rem;
  opacity: 0.8;
}

/* 尺寸变体 */
.level-xs .level-number {
  font-size: 0.625rem;
}

.level-xs .level-name {
  font-size: 0.625rem;
}

.level-xs .progress-bar {
  height: 4px;
}

.level-sm .level-number {
  font-size: 0.7rem;
}

.level-sm .level-name {
  font-size: 0.7rem;
}

.level-sm .progress-bar {
  height: 5px;
}

.level-md .level-number {
  font-size: 0.75rem;
}

.level-md .level-name {
  font-size: 0.75rem;
}

.level-md .progress-bar {
  height: 6px;
}

.level-lg .level-number {
  font-size: 0.875rem;
}

.level-lg .level-name {
  font-size: 0.875rem;
}

.level-lg .progress-bar {
  height: 8px;
}

/* 等级颜色变体 */
.level-1 .level-badge {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
}

.level-2 .level-badge {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.level-3 .level-badge {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
}

.level-4 .level-badge {
  background: linear-gradient(135deg, #f1c40f, #f39c12);
}

.level-5 .level-badge {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.level-6 .level-badge {
  background: linear-gradient(135deg, #e67e22, #d35400);
}

.level-7 .level-badge {
  background: linear-gradient(135deg, #1abc9c, #16a085);
}

.level-8 .level-badge {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

@media (max-width: 640px) {
  .level-progress {
    min-width: 160px;
  }
}
</style>