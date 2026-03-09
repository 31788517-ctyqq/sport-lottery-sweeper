<!-- frontend/src/components/admin/AdminLayout.vue -->
<template>
  <div class="admin-layout">
    <!-- Header Navigation -->
    <van-nav-bar
      :title="layoutTitle"
      fixed
      safe-area-inset-top
      placeholder
    >
      <!-- 可以在这里添加左侧按钮或右侧按钮 -->
      <template #left>
        <van-icon name="arrow-left" @click="handleBack" />
      </template>
      <template #right>
        <slot name="nav-right"></slot> <!-- 允许父组件插入右侧内容 -->
      </template>
    </van-nav-bar>

    <!-- Main Content Area -->
    <div class="admin-content" :style="{ paddingTop: 'var(--van-nav-bar-height)' }">
      <slot></slot> <!-- 子组件内容将插入此处 -->
    </div>

    <!-- Optional: Bottom Tabbar for Admin (if needed) -->
    <!--
    <van-tabbar route>
      <van-tabbar-item replace to="/admin/dashboard" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item replace to="/admin/users" icon="user-o">用户</van-tabbar-item>
      <van-tabbar-item replace to="/admin/data" icon="setting-o">数据</van-tabbar-item>
    </van-tabbar>
    -->
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// 计算当前路由对应的标题
const layoutTitle = computed(() => {
  // 可以根据路由 meta 信息来动态设置标题
  return route.meta?.title || '管理后台';
});

// 处理返回按钮点击
const handleBack = () => {
  router.go(-1); // 或者跳转到指定路由，如 router.push('/dashboard')
};
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.admin-content {
  flex: 1;
  overflow-y: auto; /* 允许内容滚动 */
  padding-bottom: var(--van-tabbar-height, 0); /* 如果有 tabbar，留出空间 */
}
</style>