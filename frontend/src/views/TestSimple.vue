<template>
  <div style="background: blue; color: white; padding: 20px;">
    <h1>Test Simple Component</h1>
    <p>This is a test component to check if routing works.</p>
    <p>Current path: {{ $route.path }}</p>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const $route = useRoute()
</script>

<style scoped>
/* 样式 */
</style>