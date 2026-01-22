<template>
  <nav class="bottom-nav">
    <div 
      class="nav-item" 
      :class="{ active: currentNav === 'home' }"
      @click="switchNav('home')"
    >
      <i class="fas fa-home nav-icon"></i>
      <span>首页</span>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentNav === 'filter' }"
      @click="switchNav('filter')"
    >
      <i class="fas fa-filter nav-icon"></i>
      <span>筛选</span>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentNav === 'favorites' }"
      @click="switchNav('favorites')"
    >
      <i class="far fa-star nav-icon"></i>
      <span>收藏</span>
    </div>
    <div 
      class="nav-item" 
      :class="{ active: currentNav === 'profile' }"
      @click="switchNav('profile')"
    >
      <i class="fas fa-user nav-icon"></i>
      <span>我的</span>
    </div>
  </nav>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()
const currentNav = ref('home')

const switchNav = (nav) => {
  currentNav.value = nav
  switch(nav) {
    case 'home':
      router.push('/')
      break
    case 'filter':
      router.push('/filter')
      break
    case 'favorites':
      router.push('/favorites')
      break
    case 'profile':
      router.push('/profile')
      break
  }
}

// 监听路由变化
watch(route, (newRoute) => {
  if (newRoute.path === '/') currentNav.value = 'home'
  else if (newRoute.path.includes('filter')) currentNav.value = 'filter'
  else if (newRoute.path.includes('favorites')) currentNav.value = 'favorites'
  else if (newRoute.path.includes('profile')) currentNav.value = 'profile'
}, { immediate: true })
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: var(--bg-header);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 10px;
  padding-bottom: var(--safe-area-bottom);
  box-sizing: border-box;
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-sub);
  font-size: 12px;
}

.nav-item.active {
  color: var(--primary);
  background: rgba(88, 166, 255, 0.1);
}

.nav-icon {
  font-size: 18px;
  margin-bottom: 2px;
}
</style>