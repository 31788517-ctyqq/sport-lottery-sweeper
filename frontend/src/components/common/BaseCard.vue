<!-- AI_WORKING: coder1 @2026-01-26T11:30:00 - 添加工具栏模式支持，包括headerVariant、toolbarAlign、titleAlign等属性 -->
<template>
  <div 
    :class="[
      'base-card',
      `base-card--${variant}`,
      { 'base-card--clickable': clickable },
      { 'base-card--hoverable': hoverable },
      { 'base-card--shadow': shadow },
      { 'base-card--border': border },
      { 'base-card--loading': loading }
    ]"
    :style="cardStyle"
    @click="handleClick"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="base-card__loading">
      <slot name="loading">
        <div class="loading-spinner"></div>
        <span v-if="loadingText">{{ loadingText }}</span>
      </slot>
    </div>
    
    <!-- 卡片头部 -->
    <div v-if="showHeader" class="base-card__header" :class="`base-card__header--${headerVariant}`">
      <slot name="header">
        <!-- 简单模式（默认） -->
        <div v-if="headerVariant === 'simple'" class="base-card__header-content">
          <div v-if="icon" class="base-card__icon">
            <i :class="icon"></i>
          </div>
          <div class="base-card__title">
            <h3 v-if="title">{{ title }}</h3>
            <p v-if="subtitle" class="base-card__subtitle">{{ subtitle }}</p>
          </div>
          <div class="base-card__header-actions">
            <slot name="header-actions"></slot>
          </div>
        </div>
        
        <!-- 工具栏模式 -->
        <div v-else class="base-card__header-toolbar">
          <div class="base-card__header-title" :style="{ textAlign: titleAlign }">
            <slot name="toolbar-title">
              <h3 v-if="title">{{ title }}</h3>
              <p v-if="subtitle" class="base-card__subtitle">{{ subtitle }}</p>
            </slot>
          </div>
          
          <div 
            class="base-card__header-tools" 
            :style="{ 
              justifyContent: toolbarAlign === 'right' ? 'flex-end' : toolbarAlign,
              padding: toolbarPadding,
              borderTop: showToolbarBorder ? '1px solid var(--border-color-light, #ebeef5)' : 'none'
            }"
          >
            <slot name="toolbar">
              <!-- 默认显示 header-actions 插槽内容以保持兼容 -->
              <slot name="header-actions"></slot>
            </slot>
          </div>
        </div>
      </slot>
    </div>
    
    <!-- 卡片内容 -->
    <div v-if="!loading" class="base-card__body">
      <slot name="default"></slot>
      <div v-if="$slots['empty'] && isEmpty" class="base-card__empty">
        <slot name="empty"></slot>
      </div>
    </div>
    
    <!-- 卡片底部 -->
    <div v-if="showFooter" class="base-card__footer">
      <slot name="footer"></slot>
    </div>
    
    <!-- 卡片边框 -->
    <div v-if="border" class="base-card__border"></div>
  </div>
</template>

<script setup>
import { computed, defineEmits } from 'vue'

// 组件属性
const props = defineProps({
  // 基本属性
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  
  // 样式变体
  variant: {
    type: String,
    default: 'default', // 'default', 'primary', 'secondary', 'success', 'warning', 'danger', 'info'
    validator: (value) => ['default', 'primary', 'secondary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  
  // 交互属性
  clickable: {
    type: Boolean,
    default: false
  },
  hoverable: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: '加载中...'
  },
  
  // 显示控制
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: false
  },
  isEmpty: {
    type: Boolean,
    default: false
  },
  
  // 头部变体
  headerVariant: {
    type: String,
    default: 'simple', // 'simple' | 'toolbar'
    validator: (value) => ['simple', 'toolbar'].includes(value)
  },
  toolbarAlign: {
    type: String,
    default: 'right',
    validator: (value) => ['left', 'center', 'right'].includes(value)
  },
  titleAlign: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'center', 'right'].includes(value)
  },
  toolbarPadding: {
    type: String,
    default: '0 0 0 1rem'
  },
  showToolbarBorder: {
    type: Boolean,
    default: false
  },
  
  // 样式控制
  shadow: {
    type: Boolean,
    default: true
  },
  border: {
    type: Boolean,
    default: true
  },
  borderRadius: {
    type: [String, Number],
    default: '0.5rem'
  },
  padding: {
    type: [String, Number],
    default: '1.5rem'
  },
  margin: {
    type: [String, Number],
    default: ''
  },
  maxWidth: {
    type: [String, Number],
    default: ''
  },
  minHeight: {
    type: [String, Number],
    default: ''
  },
  backgroundColor: {
    type: String,
    default: ''
  }
})

// 事件
const emit = defineEmits(['click'])

// 计算属性
const cardStyle = computed(() => {
  const style = {}
  
  if (props.borderRadius) {
    style.borderRadius = typeof props.borderRadius === 'number' ? `${props.borderRadius}px` : props.borderRadius
  }
  
  if (props.padding) {
    style.padding = typeof props.padding === 'number' ? `${props.padding}px` : props.padding
  }
  
  if (props.margin) {
    style.margin = typeof props.margin === 'number' ? `${props.margin}px` : props.margin
  }
  
  if (props.maxWidth) {
    style.maxWidth = typeof props.maxWidth === 'number' ? `${props.maxWidth}px` : props.maxWidth
  }
  
  if (props.minHeight) {
    style.minHeight = typeof props.minHeight === 'number' ? `${props.minHeight}px` : props.minHeight
  }
  
  if (props.backgroundColor) {
    style.backgroundColor = props.backgroundColor
  }
  
  return style
})

// 方法
const handleClick = (event) => {
  if (props.clickable && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-card {
  position: relative;
  background-color: var(--bg-card);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.base-card--clickable {
  cursor: pointer;
}

.base-card--hoverable:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
}

.base-card--shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.base-card--border {
  border: 1px solid var(--border-color);
}

.base-card__loading {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.base-card__header {
  padding: 1.25rem 1.5rem 0.75rem;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.base-card__header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.base-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: var(--primary);
  font-size: 1.25rem;
}

.base-card__title {
  flex: 1;
}

.base-card__title h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.base-card__subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.base-card__header-actions {
  display: flex;
  gap: 0.5rem;
}

.base-card__body {
  flex: 1;
  padding: 1.5rem;
  overflow: auto;
}

.base-card__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-secondary);
  text-align: center;
}

.base-card__footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.base-card__border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background-color: var(--primary);
}

/* 头部变体样式 */
.base-card__header--toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.base-card__header-toolbar {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
}

.base-card__header-title {
  flex: 1;
}

.base-card__header-title h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.base-card__header-tools {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* 变体样式 */
.base-card--primary .base-card__border {
  background-color: var(--primary);
}

.base-card--secondary .base-card__border {
  background-color: var(--secondary);
}

.base-card--success .base-card__border {
  background-color: var(--success);
}

.base-card--warning .base-card__border {
  background-color: var(--warning);
}

.base-card--danger .base-card__border {
  background-color: var(--danger);
}

.base-card--info .base-card__border {
  background-color: var(--info);
}

/* 响应式 */
@media (max-width: 768px) {
  .base-card__header {
    padding: 1rem;
  }
  
  .base-card__body {
    padding: 1rem;
  }
  
  .base-card__footer {
    padding: 0.75rem 1rem;
  }
}
/* AI_DONE: coder1 @2026-01-26T11:32:00 */
</style>