<template>
  <div class="mobile-layout-wrapper">
    <!-- 极简版本，仅用于测试 -->
    <div style="background: purple; color: white; padding: 20px;">
      <h2>Mobile Layout Wrapper (Minimal)</h2>
      <p>Title: {{ title }}</p>
      <p>Layout Mode: {{ layoutMode }}</p>
      <div style="border: 1px dashed white; padding: 10px;">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '北单三维筛选器'
  },
  layoutMode: {
    type: String,
    default: 'auto'
  }
})
</script>

<style scoped>
.mobile-layout-wrapper {
  width: 100%;
  height: 100%;
}
</style>