<template>
  <div :class="['empty-state', `empty-state--${size}`, `empty-state--${variant}`]">
    <!-- 图标 -->
    <div v-if="icon || $slots.icon" class="empty-state__icon">
      <slot name="icon">
        <component v-if="icon" :is="icon" :size="iconSize" />
      </slot>
    </div>

    <!-- 图片 -->
    <img
      v-if="imageSrc"
      :src="imageSrc"
      :alt="imageAlt"
      class="empty-state__image"
    />

    <!-- 内容 -->
    <div class="empty-state__content">
      <!-- 标题 -->
      <h3 v-if="title" class="empty-state__title">
        {{ title }}
      </h3>

      <!-- 描述 -->
      <p v-if="description" class="empty-state__description">
        {{ description }}
      </p>

      <!-- 额外内容 -->
      <div v-if="$slots.default" class="empty-state__extra">
        <slot></slot>
      </div>

      <!-- 操作按钮 -->
      <div v-if="$slots.actions || actionText" class="empty-state__actions">
        <slot name="actions">
          <BaseButton
            v-if="actionText"
            :variant="actionVariant"
            :size="buttonSize"
            @click="handleAction"
          >
            {{ actionText }}
          </BaseButton>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  },
  imageSrc: {
    type: String,
    default: ''
  },
  imageAlt: {
    type: String,
    default: '空状态'
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'compact', 'detailed', 'minimal'].includes(value)
  },
  actionText: {
    type: String,
    default: ''
  },
  actionVariant: {
    type: String,
    default: 'primary'
  },
  centered: {
    type: Boolean,
    default: true
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['action'])

// 计算图标尺寸
const iconSize = computed(() => {
  const sizes = {
    small: 48,
    medium: 64,
    large: 80
  }
  return sizes[props.size] || 64
})

// 计算按钮尺寸
const buttonSize = computed(() => {
  const sizes = {
    small: 'small',
    medium: 'medium',
    large: 'large'
  }
  return sizes[props.size] || 'medium'
})

// 处理操作按钮点击
const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-state--centered {
  margin: 0 auto;
}

.empty-state--full-width {
  width: 100%;
}

/* 尺寸变体 */
.empty-state--small {
  padding: var(--spacing-6);
  gap: var(--spacing-4);
}

.empty-state--medium {
  padding: var(--spacing-8);
  gap: var(--spacing-6);
}

.empty-state--large {
  padding: var(--spacing-12);
  gap: var(--spacing-8);
}

/* 布局变体 */
.empty-state--compact {
  padding: var(--spacing-4);
  gap: var(--spacing-3);
}

.empty-state--compact .empty-state__icon {
  margin-bottom: var(--spacing-2);
}

.empty-state--compact .empty-state__title {
  font-size: var(--font-size-base);
}

.empty-state--compact .empty-state__description {
  font-size: var(--font-size-sm);
}

.empty-state--detailed {
  text-align: left;
  align-items: flex-start;
}

.empty-state--detailed .empty-state__icon {
  align-self: flex-start;
}

.empty-state--minimal {
  padding: var(--spacing-4);
  gap: var(--spacing-2);
}

.empty-state--minimal .empty-state__icon {
  opacity: 0.5;
}

.empty-state--minimal .empty-state__title {
  font-size: var(--font-size-sm);
  font-weight: normal;
}

.empty-state--minimal .empty-state__description {
  display: none;
}

/* 图标 */
.empty-state__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--icon-size, 64px);
  height: var(--icon-size, 64px);
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-4);
  opacity: 0.6;
}

.empty-state--small .empty-state__icon {
  --icon-size: 48px;
  margin-bottom: var(--spacing-3);
}

.empty-state--medium .empty-state__icon {
  --icon-size: 64px;
  margin-bottom: var(--spacing-4);
}

.empty-state--large .empty-state__icon {
  --icon-size: 80px;
  margin-bottom: var(--spacing-6);
}

/* 图片 */
.empty-state__image {
  max-width: 100%;
  height: auto;
  margin-bottom: var(--spacing-6);
  opacity: 0.8;
}

.empty-state--small .empty-state__image {
  max-height: 120px;
  margin-bottom: var(--spacing-4);
}

.empty-state--medium .empty-state__image {
  max-height: 160px;
  margin-bottom: var(--spacing-6);
}

.empty-state--large .empty-state__image {
  max-height: 200px;
  margin-bottom: var(--spacing-8);
}

/* 内容 */
.empty-state__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  max-width: 400px;
}

.empty-state--detailed .empty-state__content {
  max-width: 500px;
}

/* 标题 */
.empty-state__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.empty-state--small .empty-state__title {
  font-size: var(--font-size-base);
}

.empty-state--medium .empty-state__title {
  font-size: var(--font-size-lg);
}

.empty-state--large .empty-state__title {
  font-size: var(--font-size-xl);
}

/* 描述 */
.empty-state__description {
  margin: 0;
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.empty-state--small .empty-state__description {
  font-size: var(--font-size-sm);
}

.empty-state--medium .empty-state__description {
  font-size: var(--font-size-base);
}

.empty-state--large .empty-state__description {
  font-size: var(--font-size-lg);
}

/* 额外内容 */
.empty-state__extra {
  margin-top: var(--spacing-2);
}

.empty-state--detailed .empty-state__extra {
  margin-top: var(--spacing-4);
}

/* 操作按钮 */
.empty-state__actions {
  margin-top: var(--spacing-4);
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
}

.empty-state--detailed .empty-state__actions {
  justify-content: flex-start;
}

.empty-state--compact .empty-state__actions {
  margin-top: var(--spacing-3);
}

/* 主题变体 */
.empty-state--primary .empty-state__icon {
  color: var(--color-primary);
}

.empty-state--secondary .empty-state__icon {
  color: var(--color-secondary);
}

.empty-state--success .empty-state__icon {
  color: var(--color-success);
}

.empty-state--warning .empty-state__icon {
  color: var(--color-warning);
}

.empty-state--danger .empty-state__icon {
  color: var(--color-danger);
}

/* 边框变体 */
.empty-state--bordered {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background-color: var(--color-bg-secondary);
}

.empty-state--bordered.empty-state--primary {
  border-color: var(--color-primary-light);
  background-color: rgba(var(--color-primary-rgb), 0.05);
}

.empty-state--bordered.empty-state--secondary {
  border-color: var(--color-secondary-light);
  background-color: rgba(var(--color-secondary-rgb), 0.05);
}

.empty-state--bordered.empty-state--success {
  border-color: var(--color-success-light);
  background-color: rgba(var(--color-success-rgb), 0.05);
}

.empty-state--bordered.empty-state--warning {
  border-color: var(--color-warning-light);
  background-color: rgba(var(--color-warning-rgb), 0.05);
}

.empty-state--bordered.empty-state--danger {
  border-color: var(--color-danger-light);
  background-color: rgba(var(--color-danger-rgb), 0.05);
}

/* 响应式 */
@media (max-width: 640px) {
  .empty-state {
    padding: var(--spacing-6);
  }
  
  .empty-state--large {
    padding: var(--spacing-8);
  }
  
  .empty-state__icon {
    --icon-size: 48px;
  }
  
  .empty-state__actions {
    flex-direction: column;
    width: 100%;
  }
  
  .empty-state__actions .base-button {
    width: 100%;
  }
}
</style>