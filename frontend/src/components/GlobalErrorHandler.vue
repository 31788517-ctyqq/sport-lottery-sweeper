<template>
  <div v-if="errorQueue.length > 0" class="error-handler-container">
    <transition-group name="error-list" tag="div" class="error-list">
      <div 
        v-for="error in errorQueue" 
        :key="error.id"
        :class="['error-item', error.type]"
      >
        <div class="error-content">
          <div class="error-icon">
            <span v-if="error.type === 'error'">❌</span>
            <span v-if="error.type === 'warning'">⚠️</span>
            <span v-if="error.type === 'info'">ℹ️</span>
            <span v-if="error.type === 'success'">✅</span>
          </div>
          <div class="error-message">
            <strong>{{ error.title }}</strong>
            <p>{{ error.message }}</p>
          </div>
          <div class="error-actions">
            <button class="close-btn" @click="removeError(error.id)">×</button>
          </div>
        </div>
        <div class="error-progress" :style="{ animationDuration: error.duration + 'ms' }"></div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getErrorMessage, isBenignBrowserError } from '@/utils/benign-browser-errors'

// 错误队列
const errorQueue = ref([])

// 添加错误到队列
const addError = (error) => {
  const newError = {
    id: Date.now() + Math.random(),
    title: error.title || '错误',
    message: error.message || error.toString(),
    type: error.type || 'error',
    duration: error.duration || 5000
  }
  
  errorQueue.value.push(newError)
  
  // 自动移除错误
  setTimeout(() => {
    removeError(newError.id)
  }, newError.duration)
}

// 移除错误
const removeError = (id) => {
  const index = errorQueue.value.findIndex(error => error.id === id)
  if (index !== -1) {
    errorQueue.value.splice(index, 1)
  }
}

// 清空所有错误
const clearErrors = () => {
  errorQueue.value = []
}

// 暴露方法
defineExpose({
  addError,
  removeError,
  clearErrors
})

// 全局错误处理器
const errorHandler = (event) => {
  const raw = event.error || event.message
  if (isBenignBrowserError(raw)) return

  addError({
    title: 'JavaScript错误',
    message: getErrorMessage(raw) || '未知错误',
    type: 'error',
    duration: 8000
  })
}

// Promise拒绝处理器
const promiseRejectionHandler = (event) => {
  if (isBenignBrowserError(event.reason)) return

  addError({
    title: 'Promise拒绝',
    message: getErrorMessage(event.reason) || '未知原因',
    type: 'error',
    duration: 8000
  })
}

// 监听全局错误
onMounted(() => {
  window.addEventListener('error', errorHandler)
  window.addEventListener('unhandledrejection', promiseRejectionHandler)
})

// 移除监听器
onUnmounted(() => {
  window.removeEventListener('error', errorHandler)
  window.removeEventListener('unhandledrejection', promiseRejectionHandler)
})
</script>

<style scoped>
.error-handler-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  max-width: 400px;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-item {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
  border-left: 4px solid #ef4444;
}

.error-item.warning {
  border-left-color: #f59e0b;
}

.error-item.info {
  border-left-color: #3b82f6;
}

.error-item.success {
  border-left-color: #10b981;
}

.error-content {
  display: flex;
  padding: 12px;
  align-items: flex-start;
  gap: 10px;
}

.error-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.error-message {
  flex: 1;
  min-width: 0;
}

.error-message strong {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  color: #1f2937;
}

.error-message p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.error-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #9ca3af;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #6b7280;
}

.error-progress {
  height: 3px;
  background: #e5e7eb;
  animation: countdown linear;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes countdown {
  from {
    width: 100%;
  }
  to {
    width: 0;
  }
}

/* 过渡效果 */
.error-list-enter-active,
.error-list-leave-active {
  transition: all 0.3s;
}

.error-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.error-list-leave-to {
  opacity: 0;
  transform: translateX(100%);
  max-height: 0;
  padding: 0;
  margin: 0;
  overflow: hidden;
}
</style>
