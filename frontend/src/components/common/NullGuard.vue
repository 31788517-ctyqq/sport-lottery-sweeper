<!-- AI_WORKING: coder1 @2026-02-04T16:33:47 - 创建数据守卫组件，提供空值安全渲染 -->
<template>
  <div class="null-guard">
    <!-- 默认插槽：要保护的内容 -->
    <slot v-if="shouldRender" :data="safeData" />
    
    <!-- fallback插槽：空值时的占位内容 -->
    <slot v-else name="fallback" :data="safeData" :isEmpty="isEmpty">
      <!-- 默认fallback内容 -->
      <div class="null-guard-fallback">
        <div class="fallback-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="fallback-text">
          <h4 v-if="fallbackTitle">{{ fallbackTitle }}</h4>
          <p v-if="fallbackMessage">{{ fallbackMessage }}</p>
          <p v-else>暂无数据</p>
        </div>
      </div>
    </slot>
  </div>
</template>

<script setup>
import { computed, toRefs } from 'vue'

const props = defineProps({
  /**
   * 要保护的数据
   */
  data: {
    type: [Object, Array, String, Number, Boolean],
    default: null
  },
  
  /**
   * 是否启用空值检查
   */
  checkNull: {
    type: Boolean,
    default: true
  },
  
  /**
   * 是否启用空数组检查
   */
  checkEmptyArray: {
    type: Boolean,
    default: true
  },
  
  /**
   * 是否启用空字符串检查
   */
  checkEmptyString: {
    type: Boolean,
    default: false
  },
  
  /**
   * 是否启用零值检查（数字0）
   */
  checkZero: {
    type: Boolean,
    default: false
  },
  
  /**
   * 是否启用假值检查（false）
   */
  checkFalse: {
    type: Boolean,
    default: false
  },
  
  /**
   * 自定义验证函数，返回true表示数据有效
   * @param {*} data - 要验证的数据
   * @returns {boolean} 数据是否有效
   */
  validator: {
    type: Function,
    default: null
  },
  
  /**
   * fallback标题
   */
  fallbackTitle: {
    type: String,
    default: ''
  },
  
  /**
   * fallback消息
   */
  fallbackMessage: {
    type: String,
    default: ''
  },
  
  /**
   * 空值时的默认数据
   */
  defaultValue: {
    type: [Object, Array, String, Number, Boolean],
    default: null
  }
})

const { 
  data, 
  checkNull, 
  checkEmptyArray, 
  checkEmptyString, 
  checkZero, 
  checkFalse,
  validator,
  defaultValue
} = toRefs(props)

/**
 * 检查数据是否为空
 */
const isEmpty = computed(() => {
  const value = data.value
  
  // 自定义验证函数
  if (validator?.value) {
    return !validator.value(value)
  }
  
  // null/undefined检查
  if (checkNull.value && (value === null || value === undefined)) {
    return true
  }
  
  // 空数组检查
  if (checkEmptyArray.value && Array.isArray(value) && value.length === 0) {
    return true
  }
  
  // 空字符串检查
  if (checkEmptyString.value && typeof value === 'string' && value.trim() === '') {
    return true
  }
  
  // 零值检查
  if (checkZero.value && typeof value === 'number' && value === 0) {
    return true
  }
  
  // 假值检查
  if (checkFalse.value && typeof value === 'boolean' && value === false) {
    return true
  }
  
  // 空对象检查（可选）
  if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
    return Object.keys(value).length === 0
  }
  
  return false
})

/**
 * 安全数据，为空时返回默认值
 */
const safeData = computed(() => {
  if (isEmpty.value && defaultValue.value !== undefined) {
    return defaultValue.value
  }
  return data.value
})

/**
 * 是否应该渲染默认插槽
 */
const shouldRender = computed(() => {
  return !isEmpty.value
})
</script>

<style scoped>
.null-guard {
  width: 100%;
  height: 100%;
}

.null-guard-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #999;
  background-color: #f9f9f9;
  border-radius: 8px;
  min-height: 200px;
  width: 100%;
}

.fallback-icon {
  margin-bottom: 1rem;
  color: #ccc;
}

.fallback-icon svg {
  stroke-width: 1.5;
}

.fallback-text h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #666;
}

.fallback-text p {
  margin: 0;
  font-size: 0.9rem;
  color: #888;
}
</style>

<!-- AI_DONE: coder1 @2026-02-04T16:33:47 -->