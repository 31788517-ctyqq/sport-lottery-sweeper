<template>
  <div class="admin-dashboard">
    <h1>管理仪表板</h1>
    <p>欢迎使用系统管理后台。</p>
    <!-- 示例卡片 -->
    <el-row :gutter="20" class="dashboard-cards">
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>总用户数</span>
          </div>
          <div class="item">{{ $ensureNotNull(stats.users, 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>今日活跃</span>
          </div>
          <div class="item">{{ $ensureNotNull(stats.activeToday, 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>数据源</span>
          </div>
          <div class="item">{{ $ensureNotNull(stats.dataSources, 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>待处理情报</span>
          </div>
          <div class="item">{{ $ensureNotNull(stats.pendingIntel, 0) }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Null安全防护示例 -->
    <div class="null-safety-demo">
      <h3>Null安全防护示例</h3>
      <p>以下展示如何安全处理可能为null的数据：</p>
      
      <div class="example-item">
        <strong>系统健康状态:</strong>
        <ul>
          <li>CPU: {{ $safeGet(dashboardData, 'details.systemHealth.cpu', 0) }}%</li>
          <li>内存: {{ $safeGet(dashboardData, 'details.systemHealth.memory', 0) }}%</li>
          <li>磁盘: {{ $safeGet(dashboardData, 'details.systemHealth.disk', 'N/A') }}</li>
        </ul>
      </div>
      
      <div class="example-item">
        <strong>错误率（使用回退链）:</strong>
        <span>{{ $coalesce(stats.errorRate, dashboardData?.errorRate, 0) }}%</span>
      </div>
      
      <div class="example-item">
        <strong>最近活动数量:</strong>
        <span>{{ getRecentActivities().length }} 条</span>
      </div>
    </div>
  </div>
</template>

<script>
// AI_WORKING: coder1 @2026-02-04T16:44:47 - 添加null安全防护混入
import nullSafetyMixin from '@/mixins/nullSafetyMixin.js'

export default {
  name: 'AdminDashboard',
  // 添加null安全混入
  mixins: [nullSafetyMixin],
  data() {
    return {
      dashboardData: null,
      stats: {
        users: null,
        activeToday: null,
        dataSources: null,
        pendingIntel: null,
        errorRate: null,
        uptime: null
      }
    };
  },
  mounted() {
    this.loadDashboardData();
  },
  methods: {
    loadDashboardData() {
      // 模拟API调用，返回可能包含null的数据
      const mockApiResponse = {
        success: true,
        data: {
          users: 1234,
          activeToday: 567,
          dataSources: 8,
          pendingIntel: 23,
          // 模拟某些字段可能为null
          errorRate: null,
          uptime: null,
          details: {
            recentActivities: null,
            systemHealth: {
              cpu: 45,
              memory: 78,
              // 模拟嵌套null
              disk: null
            }
          }
        }
      };
      
      // 使用安全方法处理API响应
      const safeData = this.$deepNullGuard(mockApiResponse.data, {
        users: 0,
        activeToday: 0,
        dataSources: 0,
        pendingIntel: 0,
        errorRate: 0,
        uptime: 100,
        details: {
          recentActivities: [],
          systemHealth: {
            cpu: 0,
            memory: 0,
            disk: 0
          }
        }
      });
      
      this.dashboardData = safeData;
      this.stats = {
        users: this.$ensureNotNull(safeData.users, 0),
        activeToday: this.$ensureNotNull(safeData.activeToday, 0),
        dataSources: this.$ensureNotNull(safeData.dataSources, 0),
        pendingIntel: this.$ensureNotNull(safeData.pendingIntel, 0),
        errorRate: this.$coalesce(safeData.errorRate, safeData.details?.systemHealth?.errorRate, 0),
        uptime: this.$coalesce(safeData.uptime, safeData.details?.systemHealth?.uptime, 100)
      };
    },
    
    // 安全获取系统健康信息
    getSystemHealth() {
      if (!this.dashboardData) {
        return { cpu: 0, memory: 0, disk: 0 };
      }
      
      // 使用$safeGet安全访问嵌套属性
      return this.$safeGet(this.dashboardData, 'details.systemHealth', {
        cpu: 0,
        memory: 0,
        disk: 0
      });
    },
    
    // 安全获取最近活动
    getRecentActivities() {
      const activities = this.$safeGet(this.dashboardData, 'details.recentActivities', []);
      // 确保每个活动都有必要字段
      return activities.map(activity => ({
        id: this.$ensureNotNull(activity.id, 0),
        action: this.$ensureNotNull(activity.action, '未知操作'),
        timestamp: this.$ensureNotNull(activity.timestamp, new Date()),
        user: this.$deepNullGuard(activity.user, { name: '未知用户', role: 'guest' })
      }));
    }
  }
};
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}
.dashboard-cards .el-col {
  margin-bottom: 20px;
}
.item {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}

/* Null安全防护示例样式 */
.null-safety-demo {
  margin-top: 40px;
  padding: 24px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.null-safety-demo h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.null-safety-demo p {
  color: #64748b;
  margin-bottom: 20px;
}

.example-item {
  margin-bottom: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.example-item strong {
  display: block;
  margin-bottom: 8px;
  color: #475569;
}

.example-item ul {
  margin: 8px 0 0 20px;
  color: #475569;
}

.example-item li {
  margin-bottom: 4px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dashboard-cards .el-col {
    margin-bottom: 16px;
  }
  
  .null-safety-demo {
    padding: 16px;
  }
}
</style>