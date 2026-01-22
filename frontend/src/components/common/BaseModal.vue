<template>
  <teleport to="body">
    <transition name="modal">
      <div
        v-if="visible"
        :class="['base-modal', `base-modal--${size}`]"
        @click.self="handleBackdropClick"
      >
        <!-- 遮罩层 -->
        <div class="base-modal__backdrop"></div>

        <!-- 模态框内容 -->
        <div
          ref="modalRef"
          :class="['base-modal__content', { 'base-modal__content--centered': centered }]"
          :style="modalStyles"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="descriptionId"
        >
          <!-- 头部 -->
          <header v-if="showHeader" class="base-modal__header">
            <div class="base-modal__header-content">
              <!-- 标题 -->
              <h2 :id="titleId" class="base-modal__title">
                <slot name="title">{{ title }}</slot>
              </h2>
              
              <!-- 副标题 -->
              <p v-if="subtitle" :id="descriptionId" class="base-modal__subtitle">
                {{ subtitle }}
              </p>
            </div>

            <!-- 关闭按钮 -->
            <button
              v-if="closable"
              type="button"
              class="base-modal__close"
              @click="handleClose"
              aria-label="关闭模态框"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </header>

          <!-- 内容区域 -->
          <div class="base-modal__body">
            <slot></slot>
          </div>

          <!-- 底部 -->
          <footer v-if="showFooter" class="base-modal__footer">
            <slot name="footer">
              <div class="base-modal__footer-actions">
                <!-- 取消按钮 -->
                <BaseButton
                  v-if="showCancel"
                  variant="outline"
                  @click="handleCancel"
                  :disabled="loading"
                >
                  {{ cancelText }}
                </BaseButton>
                
                <!-- 确认按钮 -->
                <BaseButton
                  v-if="showConfirm"
                  variant="primary"
                  @click="handleConfirm"
                  :loading="loading"
                  :disabled="confirmDisabled"
                >
                  {{ confirmText }}
                </BaseButton>
              </div>
            </slot>
          </footer>

          <!-- 加载状态 -->
          <div v-if="loading" class="base-modal__loading">
            <LoadingSpinner size="large" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large', 'extra-large', 'full'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  },
  maskClosable: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showCancel: {
    type: Boolean,
    default: true
  },
  showConfirm: {
    type: Boolean,
    default: true
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  loading: {
    type: Boolean,
    default: false
  },
  confirmDisabled: {
    type: Boolean,
    default: false
  },
  centered: {
    type: Boolean,
    default: true
  },
  width: {
    type: [String, Number],
    default: null
  },
  maxWidth: {
    type: [String, Number],
    default: null
  },
  maxHeight: {
    type: String,
    default: '80vh'
  },
  zIndex: {
    type: Number,
    default: 1000
  },
  lockScroll: {
    type: Boolean,
    default: true
  },
  beforeClose: {
    type: Function,
    default: null
  }
})

const emit = defineEmits([
  'update:modelValue',
  'open',
  'close',
  'confirm',
  'cancel',
  'after-close'
])

const visible = ref(props.modelValue)
const modalRef = ref(null)
const titleId = `modal-title-${Math.random().toString(36).substr(2, 9)}`
const descriptionId = `modal-description-${Math.random().toString(36).substr(2, 9)}`

// 计算模态框样式
const modalStyles = computed(() => ({
  width: props.width ? (typeof props.width === 'number' ? `${props.width}px` : props.width) : null,
  maxWidth: props.maxWidth ? (typeof props.maxWidth === 'number' ? `${props.maxWidth}px` : props.maxWidth) : null,
  maxHeight: props.maxHeight,
  zIndex: props.zIndex + 1
}))

// 监听 modelValue 变化
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
})

// 监听 visible 变化
watch(visible, (newValue) => {
  if (newValue) {
    // 打开模态框
    emit('open')
    if (props.lockScroll) {
      lockBodyScroll()
    }
    // 聚焦模态框
    nextTick(() => {
      modalRef.value?.focus()
    })
  } else {
    // 关闭模态框
    if (props.lockScroll) {
      unlockBodyScroll()
    }
    emit('after-close')
  }
  
  emit('update:modelValue', newValue)
})

// 处理关闭
const handleClose = async () => {
  if (props.beforeClose) {
    try {
      await props.beforeClose()
      closeModal()
    } catch (error) {
      // 用户取消了关闭
      return
    }
  } else {
    closeModal()
  }
}

// 处理确认
const handleConfirm = () => {
  emit('confirm')
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
  handleClose()
}

// 处理遮罩层点击
const handleBackdropClick = () => {
  if (props.maskClosable && !props.loading) {
    handleClose()
  }
}

// 关闭模态框
const closeModal = () => {
  visible.value = false
  emit('close')
}

// 锁定页面滚动
const lockBodyScroll = () => {
  document.body.style.overflow = 'hidden'
  document.body.style.paddingRight = `${getScrollbarWidth()}px`
}

// 解锁页面滚动
const unlockBodyScroll = () => {
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
}

// 获取滚动条宽度
const getScrollbarWidth = () => {
  const outer = document.createElement('div')
  outer.style.visibility = 'hidden'
  outer.style.overflow = 'scroll'
  outer.style.width = '100px'
  outer.style.position = 'absolute'
  outer.style.top = '-9999px'
  document.body.appendChild(outer)
  
  const widthNoScroll = outer.offsetWidth
  outer.style.overflow = 'scroll'
  
  const inner = document.createElement('div')
  inner.style.width = '100%'
  outer.appendChild(inner)
  
  const widthWithScroll = inner.offsetWidth
  outer.parentNode.removeChild(outer)
  
  return widthNoScroll - widthWithScroll
}

// 键盘事件处理
const handleKeydown = (event) => {
  if (!visible.value) return
  
  // Escape 键关闭
  if (event.key === 'Escape' && props.closable && !props.loading) {
    event.preventDefault()
    handleClose()
  }
  
  // Enter 键确认
  if (event.key === 'Enter' && props.showConfirm && !props.loading) {
    event.preventDefault()
    handleConfirm()
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  
  // 如果初始状态是打开的，锁定滚动
  if (visible.value && props.lockScroll) {
    lockBodyScroll()
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  
  // 确保滚动被解锁
  if (props.lockScroll) {
    unlockBodyScroll()
  }
})

// 暴露方法
defineExpose({
  open: () => { visible.value = true },
  close: handleClose,
  confirm: handleConfirm,
  cancel: handleCancel
})
</script>

<style scoped>
.base-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: var(--z-index-modal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.base-modal__backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
}

.base-modal__content {
  position: relative;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2xl);
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  overflow: hidden;
  animation: modal-in 0.3s ease-out;
}

.base-modal__content--centered {
  margin: 0 auto;
}

/* 尺寸变体 */
.base-modal--small .base-modal__content {
  width: 90%;
  max-width: 400px;
}

.base-modal--medium .base-modal__content {
  width: 90%;
  max-width: 600px;
}

.base-modal--large .base-modal__content {
  width: 90%;
  max-width: 800px;
}

.base-modal--extra-large .base-modal__content {
  width: 90%;
  max-width: 1000px;
}

.base-modal--full .base-modal__content {
  width: 95%;
  height: 95%;
  max-width: none;
  max-height: 95vh;
}

.base-modal__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--spacing-6) var(--spacing-6) var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.base-modal__header-content {
  flex: 1;
  margin-right: var(--spacing-4);
}

.base-modal__title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.base-modal__subtitle {
  margin: var(--spacing-2) 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.base-modal__close {
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
  transition: all 0.2s;
  flex-shrink: 0;
}

.base-modal__close:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.base-modal__body {
  flex: 1;
  padding: var(--spacing-6);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.base-modal--full .base-modal__body {
  padding: 0;
}

.base-modal__footer {
  padding: var(--spacing-4) var(--spacing-6);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg-secondary);
  flex-shrink: 0;
}

.base-modal__footer-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-3);
}

.base-modal__loading {
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

/* 动画 */
@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-enter-active .base-modal__content,
.modal-leave-active .base-modal__content {
  animation: modal-in 0.3s ease-out reverse;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .base-modal__content,
.modal-leave-to .base-modal__content {
  transform: translateY(20px) scale(0.95);
}

/* 响应式 */
@media (max-width: 640px) {
  .base-modal__content {
    width: 95%;
    max-width: none;
    max-height: 90vh;
    margin: var(--spacing-2);
  }
  
  .base-modal__header,
  .base-modal__body,
  .base-modal__footer {
    padding: var(--spacing-4);
  }
  
  .base-modal__footer-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .base-modal__footer-actions .base-button {
    width: 100%;
  }
}
</style>