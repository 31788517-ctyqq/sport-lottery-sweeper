<template>
  <!-- 确保 value 已在 data 或 setup 中定义 -->
  <input v-model="value" />
</template>

<script>
export default {
  data() {
    return {
      value: '' // 确保 value 已初始化
    }
  }
}
</script>