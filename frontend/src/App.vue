<template>
  <div id="app">
    <!-- 路由视图 -->
    <router-view />
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useAppStore } from './stores';

export default {
  name: 'App',
  setup() {
    const store = useAppStore();
    
    onMounted(() => {
      // 页面加载完成后生成模拟数据
      setTimeout(() => {
        store.generateMockData();
      }, 800);
    });
    
    return {};
  }
};
</script>

<style>
/* 全局样式 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-main);
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
}
</style>