<template>
  <header class="mobile-header">
    <div class="header-logo">
      <i class="fas fa-chart-line header-logo-icon"></i>
      <span>竞彩扫盘<small class="header-subtitle">2026移动版</small></span>
    </div>
    <div class="header-right">
      <div class="status-indicator">
        <span class="status-dot"></span>
        <span>数据引擎运行中</span>
      </div>
      <button class="refresh-btn" @click="refreshData">
        <i class="fas fa-sync-alt"></i>
      </button>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const refreshData = () => {
  // 触发全局数据刷新事件
  window.dispatchEvent(new CustomEvent('refresh-data'))
}
</script>

<style scoped>
/* 顶部导航栏 */
.mobile-header {
  position: fixed;
  top: var(--safe-area-top);
  left: 0;
  right: 0;
  height: 56px;
  background: rgba(13, 17, 23, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  z-index: 1000;
  display: flex;
  align-items: center;
  padding: 0 16px;
  box-sizing: border-box;
}

.header-logo {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

.header-logo-icon {
  margin-right: 8px;
  color: var(--primary);
}

.header-subtitle {
  font-size: 10px;
  color: var(--text-sub);
  margin-left: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-sub);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
  display: inline-block;
}

.refresh-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.refresh-btn:hover {
  background: var(--primary);
  color: white;
}
</style>
