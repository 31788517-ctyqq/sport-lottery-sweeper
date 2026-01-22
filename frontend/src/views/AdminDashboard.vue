<template>
  <div class="admin-dashboard">
    <header class="admin-header">
      <div class="header-left">
        <h1>🏆 管理后台</h1>
        <nav class="admin-nav">
          <router-link to="/admin/dashboard">概览</router-link>
          <router-link to="/admin/users">用户管理</router-link>
          <router-link to="/admin/data">数据管理</router-link>
          <router-link to="/admin/reviews">数据审核</router-link>
          <router-link to="/admin/system">系统管理</router-link>
        </nav>
      </div>
      <div class="header-right">
        <div class="user-info">
          <span>{{ userInfo.username }}</span>
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
      </div>
    </header>

    <main class="dashboard-content">
      <div class="stats-grid">
        <div class="stat-card">
          <h3>总用户数</h3>
          <p class="stat-number">{{ stats.totalUsers }}</p>
          <p class="stat-change">+{{ stats.newUsersToday }} 今日新增</p>
        </div>
        <div class="stat-card">
          <h3>待审核数据</h3>
          <p class="stat-number">{{ stats.pendingReviews }}</p>
          <p class="stat-change">+{{ stats.newPendingToday }} 今日提交</p>
        </div>
        <div class="stat-card">
          <h3>比赛总数</h3>
          <p class="stat-number">{{ stats.totalMatches }}</p>
          <p class="stat-change">+{{ stats.newMatchesToday }} 今日新增</p>
        </div>
        <div class="stat-card">
          <h3>系统负载</h3>
          <p class="stat-number">{{ stats.systemLoad }}%</p>
          <p class="stat-change">{{ stats.systemStatus }}</p>
        </div>
      </div>

      <div class="dashboard-sections">
        <div class="section">
          <h2>最新活动</h2>
          <div class="activity-list">
            <div v-for="activity in activities" :key="activity.id" class="activity-item">
              <div class="activity-icon">{{ activity.icon }}</div>
              <div class="activity-details">
                <p>{{ activity.description }}</p>
                <small>{{ activity.timestamp }}</small>
              </div>
            </div>
          </div>
        </div>

        <div class="section">
          <h2>待办事项</h2>
          <div class="todo-list">
            <div v-for="task in tasks" :key="task.id" class="todo-item">
              <div class="todo-status" :class="{ 'completed': task.completed }">
                {{ task.title }}
              </div>
              <div class="todo-actions">
                <button v-if="!task.completed" @click="completeTask(task.id)" class="complete-btn">
                  完成
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAdminStore } from '@/stores/admin';
import { getAdminInfo } from '@/api/admin';

export default {
  name: 'AdminDashboard',
  setup() {
    const router = useRouter();
    const adminStore = useAdminStore();
    
    const userInfo = ref({});
    const stats = ref({
      totalUsers: 0,
      newUsersToday: 0,
      pendingReviews: 0,
      newPendingToday: 0,
      totalMatches: 0,
      newMatchesToday: 0,
      systemLoad: 0,
      systemStatus: '正常'
    });
    
    const activities = ref([
      { id: 1, icon: '👤', description: '管理员 admin 登录', timestamp: '刚刚' },
      { id: 2, icon: '📥', description: '提交了15条比赛数据待审核', timestamp: '2分钟前' },
      { id: 3, icon: '✅', description: '批准了8条情报数据', timestamp: '5分钟前' },
      { id: 4, icon: '📊', description: '更新了预测模型配置', timestamp: '1小时前' },
      { id: 5, icon: '🔄', description: '系统数据同步完成', timestamp: '2小时前' }
    ]);
    
    const tasks = ref([
      { id: 1, title: '审核今日提交的比赛数据', completed: false },
      { id: 2, title: '检查系统日志', completed: false },
      { id: 3, title: '更新联赛信息', completed: true },
      { id: 4, title: '回复用户反馈', completed: false }
    ]);

    const loadUserInfo = async () => {
      try {
        const info = await getAdminInfo();
        userInfo.value = info;
      } catch (error) {
        console.error('获取用户信息失败:', error);
        // 如果获取用户信息失败，可能是token无效
        adminStore.logout();
        router.push('/admin/login');
      }
    };

    const loadStats = async () => {
      // 这里应该是获取统计信息的API调用
      // 模拟数据
      stats.value = {
        totalUsers: 1242,
        newUsersToday: 5,
        pendingReviews: 24,
        newPendingToday: 8,
        totalMatches: 5632,
        newMatchesToday: 12,
        systemLoad: 42,
        systemStatus: '正常'
      };
    };

    const handleLogout = () => {
      adminStore.logout();
      router.push('/admin/login');
    };

    const completeTask = (taskId) => {
      const task = tasks.value.find(t => t.id === taskId);
      if (task) {
        task.completed = true;
      }
    };

    onMounted(async () => {
      if (!adminStore.isAuthenticated) {
        router.push('/admin/login');
        return;
      }
      
      await Promise.all([loadUserInfo(), loadStats()]);
    });

    return {
      userInfo,
      stats,
      activities,
      tasks,
      handleLogout,
      completeTask
    };
  }
};
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
  color: #f0f6fc;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.admin-header h1 {
  font-size: 20px;
  color: #58a6ff;
  margin: 0;
}

.admin-nav {
  display: flex;
  gap: 20px;
}

.admin-nav a {
  color: #c9d1d9;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.admin-nav a:hover,
.admin-nav a.router-link-active {
  background: rgba(88, 166, 255, 0.2);
  color: #58a6ff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logout-btn {
  background: #da3633;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background: #f85149;
}

.dashboard-content {
  padding: 30px 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #8b949e;
  font-size: 14px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 5px 0;
  color: #58a6ff;
}

.stat-change {
  margin: 0;
  font-size: 14px;
  color: #3fb950;
}

.dashboard-sections {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #58a6ff;
  font-size: 18px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.activity-icon {
  font-size: 20px;
}

.activity-details p {
  margin: 0 0 4px 0;
  font-size: 14px;
}

.activity-details small {
  color: #8b949e;
  font-size: 12px;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.todo-status {
  flex: 1;
}

.todo-status.completed {
  text-decoration: line-through;
  color: #3fb950;
}

.todo-actions {
  display: flex;
  gap: 8px;
}

.complete-btn {
  background: #238636;
  color: white;
  border: none;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }
  
  .dashboard-sections {
    grid-template-columns: 1fr;
  }
  
  .admin-nav {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>