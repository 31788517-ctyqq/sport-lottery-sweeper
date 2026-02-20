<template>
  <el-container class="admin-layout">
    <!-- 渚ц竟鏍?-->
    <el-aside width="200px" class="sidebar">
      <div class="logo">褰╃エ鎵洏绯荤粺</div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#424242"
        text-color="#e4e7ed"
        active-text-color="#409EFF"
        unique-opened
      >
        <!-- 1. 浠〃鍙?-->
        <el-menu-item index="/admin/dashboard">
          <el-icon><House /></el-icon>
          <span>浠〃鍙?</span>
        </el-menu-item>

        <!-- 2. 鐢ㄦ埛绠＄悊 -->
        <el-sub-menu index="/admin/users">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>鐢ㄦ埛绠＄悊</span>
          </template>
          <el-menu-item index="/admin/users/list">鐢ㄦ埛鍒楄〃</el-menu-item>
          <el-menu-item index="/admin/users/roles">瑙掕壊涓庢潈闄?</el-menu-item>
          <el-menu-item index="/admin/users/departments">閮ㄩ棬绠＄悊</el-menu-item>
          <el-menu-item index="/admin/users/profile">涓汉涓績</el-menu-item>
          <el-menu-item index="/admin/users/profiles">鐢ㄦ埛鐢诲儚绠＄悊</el-menu-item>
          <el-menu-item index="/admin/users/logs">鎿嶄綔鏃ュ織</el-menu-item>
        </el-sub-menu>

        <!-- 鏂板: 绮剧畻宸ュ叿涓績 -->
        <el-sub-menu index="/admin/analytic-tools">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>绮剧畻宸ュ叿涓績</span>
          </template>
          <el-menu-item index="/admin/beidan-filter">鍖楀崟涓夌淮绛涢€夊櫒</el-menu-item>
        </el-sub-menu>

        <!-- 3. 鏁版嵁婧愮鐞?-->
        <el-sub-menu index="/admin/data-source">
          <template #title>
            <el-icon><SetUp /></el-icon>
            <span>鏁版嵁婧愮鐞?</span>
          </template>
          <!-- AI_WORKING: coder1 @2026-02-04 - 娣诲姞浠诲姟鎵ц鐩戞帶鑿滃崟椤?-->
          <el-menu-item index="/admin/data-source/config">鏁版嵁婧愰厤缃?</el-menu-item>
          <el-menu-item index="/admin/data-source/task-console">浠诲姟鎺у埗鍙?</el-menu-item>
          <el-menu-item index="/admin/data-source/monitor">鐖櫕鐩戞帶</el-menu-item>
          <el-menu-item index="/admin/data-source/data-center">鏁版嵁涓績</el-menu-item>
          <el-menu-item index="/admin/data-source/ip-pool">IP姹犵鐞?</el-menu-item>
          <el-menu-item index="/admin/data-source/headers">璇锋眰澶寸鐞?</el-menu-item>
          <el-menu-item index="/admin/data-source/task-monitor">浠诲姟鎵ц鐩戞帶</el-menu-item>
          <!-- AI_DONE: coder1 @2026-02-04 -->
        </el-sub-menu>

        <!-- 4. 姣旇禌鏁版嵁绠＄悊 -->
        <el-sub-menu index="/admin/match-data">
          <template #title>
            <el-icon><Soccer /></el-icon>
            <span>姣旇禌鏁版嵁绠＄悊</span>
          </template>
          <el-menu-item index="/admin/match-data/schedule/jczq">绔炲僵璧涚▼</el-menu-item>
          <el-menu-item index="/admin/match-data/schedule/bd">鍖楀崟璧涚▼</el-menu-item>
        </el-sub-menu>

        <!-- 5. 骞冲眬棰勬祴绠＄悊 -->
        <el-sub-menu index="/admin/draw-prediction">
          <template #title>
            <el-icon><Histogram /></el-icon>
            <span>骞冲眬棰勬祴绠＄悊</span>
          </template>
          <el-menu-item index="/admin/draw-prediction/data-features">鏁版嵁涓庣壒寰佺鐞?</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/training-evaluation">妯″瀷璁粌涓庤瘎浼?</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/model-deployment">妯″瀷绠＄悊涓庨儴缃?</el-menu-item>
          <el-menu-item index="/admin/draw-prediction/prediction-monitoring">棰勬祴鏈嶅姟涓庣洃鎺?</el-menu-item>
        </el-sub-menu>

        <!-- 6. AI鏈嶅姟绠＄悊 -->
        <el-sub-menu index="/admin/ai-services">
          <template #title>
            <el-icon><ChatLineRound /></el-icon>
            <span>AI鏈嶅姟绠＄悊</span>
          </template>
          <el-menu-item index="/admin/ai-services/local">鏈湴AI鏈嶅姟</el-menu-item>
          <el-menu-item index="/admin/ai-services/remote">杩滅▼AI鏈嶅姟</el-menu-item>
          <el-menu-item index="/admin/ai-services/costs">鎴愭湰鐩戞帶</el-menu-item>
          <el-menu-item index="/admin/ai-services/agents">鏅鸿兘浣撶鐞?</el-menu-item>
          <el-menu-item index="/admin/ai-services/models">棰勬祴妯″瀷绠＄悊</el-menu-item>
          <el-menu-item index="/admin/ai-services/conversation">瀵硅瘽鍔╂墜</el-menu-item>
          <el-menu-item index="/admin/ai-services/config">閰嶇疆绠＄悊</el-menu-item>
        </el-sub-menu>

        <!-- 7. 鏅鸿兘鍐崇瓥 -->
        <el-sub-menu index="/admin/intelligent-decision">
          <template #title>
            <el-icon><Management /></el-icon>
            <span>鏅鸿兘鍐崇瓥</span>
          </template>
          <el-menu-item index="/admin/intelligent-decision/hedging">瀵瑰啿绛栫暐绠＄悊</el-menu-item>
          <el-menu-item index="/admin/intelligent-decision/recommendations">鎺ㄨ崘绯荤粺绠＄悊</el-menu-item>
          <el-menu-item index="/admin/intelligent-decision/risk-control">椋庨櫓鎺у埗</el-menu-item>
        </el-sub-menu>

        <!-- 9. 鎯呮姤鍒嗘瀽 -->
        <el-sub-menu index="/admin/intelligence">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>鎯呮姤鍒嗘瀽</span>
          </template>
          <el-menu-item index="/admin/intelligence/screening">鏅鸿兘绛涢€?</el-menu-item>
          <el-menu-item index="/admin/intelligence/collection">閲囬泦绠＄悊</el-menu-item>
          <el-menu-item index="/admin/intelligence/model">妯″瀷绠＄悊</el-menu-item>
          <el-menu-item index="/admin/intelligence/weight">鏉冮噸绠＄悊</el-menu-item>
          <el-menu-item index="/admin/intelligence/sentiment">鎯呮劅鍒嗘瀽</el-menu-item>
          <el-menu-item index="/admin/intelligence/multimodal">澶氭ā鎬佸垎鏋?</el-menu-item>
        </el-sub-menu>

        <!-- 11. 绯荤粺绠＄悊 -->
        <el-sub-menu index="/admin/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>绯荤粺绠＄悊</span>
          </template>
          <el-menu-item index="/admin/system/config">绯荤粺閰嶇疆</el-menu-item>
        </el-sub-menu>

        <!-- 12. 鏃ュ織绠＄悊 -->
        <el-sub-menu index="/admin/logs">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>鏃ュ織绠＄悊</span>
          </template>
          <el-menu-item index="/admin/logs">鏃ュ織鎬昏</el-menu-item>
          <el-menu-item index="/admin/logs/system">绯荤粺鏃ュ織</el-menu-item>
          <el-menu-item index="/admin/logs/user">鐢ㄦ埛鏃ュ織</el-menu-item>
          <el-menu-item index="/admin/logs/security">瀹夊叏鏃ュ織</el-menu-item>
          <el-menu-item index="/admin/logs/api">API鏃ュ織</el-menu-item>
          <el-menu-item index="/admin/logs/ai">AI鏈嶅姟鏃ュ織</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 椤堕儴瀵艰埅鏍?-->
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">棣栭〉</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title || '褰撳墠椤? }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="user-info">
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ authStore.user?.username || '绠＄悊鍛? }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">閫€鍑虹櫥褰?</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 涓诲唴瀹瑰尯 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  House, 
  UserFilled,
  SetUp, 
  Soccer,
  ChatLineRound,
  Management,
  Document, 
  Memo,
  Setting, 
  Tickets,
  ArrowDown,
  DataAnalysis
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  background: #f9fafb; /* 鏇存煍鍜岀殑椤甸潰鑳屾櫙 */
}

.sidebar {
  background-color: #424242;
  /* 鍘绘帀鍘氶噸闃村奖锛屼粎淇濈暀缁嗗井灞傛 */
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.08);
}

.logo {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  padding: 16px 8px;
  border-bottom: 1px solid #383838;
  letter-spacing: 1px;
}

.menu {
  border-right: none;
  height: calc(100vh - 60px);
  background-color: #424242;
}

.menu :deep(.el-sub-menu__title),
.menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  padding-left: 24px !important;
}

.menu :deep(.el-sub-menu .el-menu-item) {
  background-color: #2c2c2c;
  padding-left: 44px !important;
}

.menu :deep(.el-sub-menu__title) {
  color: #e4e7ed;
  font-weight: 500;
}

.menu :deep(.el-menu-item) {
  color: #acacac;
}

.menu :deep(.el-menu-item:hover),
.menu :deep(.el-sub-menu__title:hover) {
  background-color: #4a4a4a !important;
}

.menu :deep(.el-icon) {
  width: 20px;
  text-align: center;
  margin-right: 8px;
  vertical-align: middle;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 椤堕儴瀵艰埅鏍?- 骞插噣鐜颁唬 */
.header {
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #e5e7eb; /* 缁嗙伆绾夸唬鏇垮帤閲嶉槾褰?*/
  /* 鍘绘帀 box-shadow锛屽噺灏戣瑙夊帇杩?*/
  z-index: 10;
}

.breadcrumb {
  font-size: 15px;
  color: #374151;
}

.user-info {
  cursor: pointer;
  color: #374151;
  font-weight: 500;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 涓诲唴瀹瑰尯 - 杞荤泩鑳屾櫙锛岄€傚綋鐣欑櫧 */
.main {
  background: #f9fafb;
  padding: 24px;
  min-height: calc(100vh - 60px);
}
</style>


