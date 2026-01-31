<template>
  <header class="mobile-header">
    <div class="header-logo">
      <i class="fas fa-chart-line header-logo-icon"></i>
      <span>竞彩扫盘<small class="header-subtitle">2026移动演示版</small></span>
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

<script>
import { useAppStore } from '@/stores';

export default {
  name: 'HeaderComponent',
  setup() {
    const store = useAppStore();
    
    const refreshData = () => {
      store.generateMockData();
    };
    
    return {
      refreshData
    };
  }
};
</script>

<style scoped>
.mobile-header {
  position: fixed;
  top: 0;
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
}

.header-logo {
  font-weight: 700;
  font-size: 18px;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-logo-icon {
  color: var(--primary);
  font-size: 24px;
}

.header-subtitle {
  font-size: 11px;
  color: var(--text-sub);
  font-weight: normal;
  margin-left: 4px;
}

.header-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-btn {
  background: var(--primary);
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:active {
  transform: scale(0.95);
  background: var(--primary-hover);
}

.refresh-btn.spinning i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-indicator {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 16px;
  background: rgba(35, 134, 54, 0.2);
  color: #7ee787;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7ee787;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>