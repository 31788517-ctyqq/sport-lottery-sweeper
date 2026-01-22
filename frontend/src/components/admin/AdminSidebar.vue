<!-- frontend/src/components/admin/AdminSidebar.vue -->
<template>
  <div class="admin-sidebar-wrapper">
    <!-- Trigger Button (usually a hamburger menu in admin layout header) -->
    <!-- This button would typically be in AdminLayout's left slot -->
    <van-button icon="wap-nav" @click="showSidebar = true" />

    <!-- Sidebar using Vant Popup/Drawer -->
    <van-popup
      v-model:show="showSidebar"
      position="left"
      :style="{ width: '70%', height: '100%' }"
      teleport="body" <!-- Ensure it overlays correctly -->
    >
      <div class="sidebar-content">
        <h2 class="sidebar-title">管理菜单</h2>
        <van-cell-group inset>
          <van-cell
            v-for="item in menuItems"
            :key="item.path"
            :title="item.title"
            :to="item.path"
            is-link
            @click="onMenuItemClick(item)"
          />
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const showSidebar = ref(false);

// Define sidebar menu items
const menuItems = [
  { path: '/admin/dashboard', title: '仪表板' },
  { path: '/admin/users', title: '用户管理' },
  { path: '/admin/datasources', title: '数据源管理' },
  { path: '/admin/matches', title: '比赛管理' },
  { path: '/admin/intelligence', title: '情报管理' },
  { path: '/admin/dataquality', title: '数据质量' },
  { path: '/admin/system', title: '系统配置' },
  { path: '/admin/monitoring', title: '监控运维' },
  { path: '/admin/api', title: 'API管理' },
  { path: '/admin/logs', title: '日志管理' },
  { path: '/admin/backup', title: '备份恢复' }
];

const onMenuItemClick = (item) => {
  // Close sidebar after navigation
  showSidebar.value = false;
  // Navigate to the selected item's path
  router.push({ path: item.path });
};
</script>

<style scoped>
.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--van-padding-md);
}
.sidebar-title {
  margin: 0 0 var(--van-padding-sm) 0;
  font-size: var(--van-font-size-lg);
  font-weight: bold;
  padding: 0 var(--van-padding-xs);
}
</style>