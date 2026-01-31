<template>
  <div id="app">
    <router-view />
    <GlobalErrorHandler ref="globalErrorHandler" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GlobalErrorHandler from './components/GlobalErrorHandler.vue'

// 全局错误处理器引用
const globalErrorHandler = ref(null)

// 抛出测试错误的函数（仅用于演示）
const throwError = () => {
  throw new Error('这是一个测试错误')
}

// 测试Promise拒绝（仅用于演示）
const rejectPromise = () => {
  Promise.reject(new Error('这是一个测试Promise拒绝'))
}

// 暴露全局错误处理方法到window对象
onMounted(() => {
  if (globalErrorHandler.value) {
    window.$errorHandler = globalErrorHandler.value
    
    // 添加一个便捷方法用于手动触发错误
    window.showError = (message, title = '错误', type = 'error', duration = 5000) => {
      globalErrorHandler.value.addError({
        title,
        message,
        type,
        duration
      })
    }
  }
})
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>