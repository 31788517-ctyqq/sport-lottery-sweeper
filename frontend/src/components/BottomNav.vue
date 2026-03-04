<template>
  <nav class="bottom-nav">
    <div 
      class="nav-item" 
      :class="{ active: currentView === 'home' }"
      @click="navigateTo('home')"
    >
      <i class="fas fa-home nav-icon"></i>
      <span>首页</span>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentView === 'filter' }"
      @click="navigateTo('filter')"
    >
      <i class="fas fa-filter nav-icon"></i>
      <span>筛选</span>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentView === 'favorites' }"
      @click="navigateTo('favorites')"
    >
      <i class="far fa-star nav-icon"></i>
      <span>收藏</span>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentView === 'profile' }"
      @click="navigateTo('profile')"
    >
      <i class="fas fa-user nav-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue';
import { useAppStore } from '../stores';

export default {
  name: 'BottomNav',
  setup() {
    const store = useAppStore();
    
    const currentView = computed(() => store.currentView);
    
    const navigateTo = (view) => {
      store.setCurrentView(view);
    };
    
    return {
      currentView,
      navigateTo
    };
  }
};
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(13, 17, 23, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: var(--safe-area-bottom);
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-sub);
  font-size: 11px;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s;
  padding: 8px 0;
  flex: 1;
}

.nav-item:active {
  color: var(--primary);
}

.nav-item.active {
  color: var(--primary);
}

.nav-icon {
  font-size: 20px;
}
</style>