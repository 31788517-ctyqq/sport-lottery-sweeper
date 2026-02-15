<template>
  <div class="log-management-container">
    <el-card class="log-header">
      <h2>日志管理中心</h2>
      <p>系统各类日志的集中管理与分析平台</p>
    </el-card>

    <el-row :gutter="20" class="log-stats">
      <el-col :span="6">
        <el-card class="log-stat-item">
          <div class="stat-content">
            <i class="el-icon-document"></i>
            <div class="stat-info">
              <p class="stat-number">{{ totalLogs }}</p>
              <p class="stat-label">总日志数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="log-stat-item">
          <div class="stat-content">
            <i class="el-icon-warning"></i>
            <div class="stat-info">
              <p class="stat-number">{{ errorLogs }}</p>
              <p class="stat-label">错误日志</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="log-stat-item">
          <div class="stat-content">
            <i class="el-icon-user"></i>
            <div class="stat-info">
              <p class="stat-number">{{ userActivities }}</p>
              <p class="stat-label">用户活动</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="log-stat-item">
          <div class="stat-content">
            <i class="el-icon-lock"></i>
            <div class="stat-info">
              <p class="stat-number">{{ securityEvents }}</p>
              <p class="stat-label">安全事件</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="log-navigation">
      <div class="log-menu">
        <el-button type="primary" size="large" @click="$router.push('/admin/logs/system')">
          <i class="el-icon-document"></i>
          <span>系统日志</span>
        </el-button>
        <el-button type="info" size="large" @click="$router.push('/admin/logs/user')">
          <i class="el-icon-user"></i>
          <span>用户日志</span>
        </el-button>
        <el-button type="danger" size="large" @click="$router.push('/admin/logs/security')">
          <i class="el-icon-lock"></i>
          <span>安全日志</span>
        </el-button>
        <el-button type="warning" size="large" @click="$router.push('/admin/logs/api')">
          <i class="el-icon-monitor"></i>
          <span>API日志</span>
        </el-button>
      </div>
    </el-card>

    <!-- 最近日志 -->
    <el-card class="recent-logs-card">
      <template #header>
        <span>最近日志</span>
        <el-button type="link" @click="refreshData">刷新</el-button>
      </template>
      <LogTable
        :logs="recentLogs"
        :loading="loadingRecent"
        :show-filters="false"
        :show-actions="false"
        :show-pagination="false"
        @view-details="viewLogDetails"
      />
    </el-card>
  </div>
</template>

<script>
import http from '@/utils/http';  // 使用配置了拦截器的实例
import LogTable from '@/components/LogTable.vue';
import { processLogResponse } from '@/utils/logUtils.js';

const API_BASE = '/api/admin/system';

export default {
  name: 'LogManagement',
  components: {
    LogTable
  },
  data() {
    return {
      totalLogs: 0,
      errorLogs: 0,
      userActivities: 0,
      securityEvents: 0,
      recentLogs: [],
      loadingRecent: false
    }
  },
  methods: {
    getTagType(level) {
      switch(level.toUpperCase()) {
        case 'ERROR':
          return 'danger'
        case 'WARN':
        case 'WARNING':
          return 'warning'
        case 'INFO':
          return 'info'
        case 'DEBUG':
          return 'primary'
        case 'CRITICAL':
          return 'danger'
        default:
          return 'info'
      }
    },

    getLogTypeTagType(logType) {
      switch(logType) {
        case 'system':
          return 'primary'
        case 'user':
          return 'success'
        case 'security':
          return 'warning'
        case 'api':
          return 'info'
        default:
          return 'default'
      }
    },
    
    async loadStatistics() {
      try {
        const stats = await http.get(`${API_BASE}/logs/db/statistics`);  // 使用http实例
        
        this.totalLogs = stats.total_logs || 0;
        this.errorLogs = stats.logs_by_level?.ERROR || 0;
        // 从模块统计中获取用户和安全相关日志数量
        this.userActivities = stats.logs_by_module?.user || 0;
        this.securityEvents = stats.logs_by_module?.security || 0;
      } catch (error) {
        if (error.response?.status === 401) {
          // 开发环境下只显示提示，不跳转避免循环
          if (import.meta.env.MODE === 'development') {
            console.warn('🔧 开发模式：跳过401跳转')
            this.$message.warning('开发模式：模拟登录过期状态')
          } else {
            this.$message.error('登录已过期，请重新登录');
            this.$router.push('/login');
          }
        } else {
          console.error('加载日志统计失败:', error);
          this.$message.error('加载日志统计失败');
        }
      }
    },
    
    async loadRecentLogs() {
      this.loadingRecent = true;
      try {
        const response = await http.get(`${API_BASE}/logs/db/system?skip=0&limit=5`);  // 使用http实例
        const { items } = processLogResponse(response);
        this.recentLogs = items;
      } catch (error) {
        if (error.response?.status === 401) {
          // 开发环境下只显示提示，不跳转避免循环
          if (import.meta.env.MODE === 'development') {
            console.warn('🔧 开发模式：跳过401跳转')
            this.$message.warning('开发模式：模拟登录过期状态')
          } else {
            this.$message.error('登录已过期，请重新登录');
            this.$router.push('/login');
          }
        } else {
          console.error('加载最近日志失败:', error);
          this.$message.error('加载最近日志失败');
        }
      } finally {
        this.loadingRecent = false;
      }
    },

    refreshData() {
      this.loadStatistics();
      this.loadRecentLogs();
    },

    viewLogDetails(log) {
      // 显示详情弹窗
      console.log('查看日志详情:', log);
      this.$message.info('日志详情功能开发中...');
    }
  },
  
  mounted() {
    this.loadStatistics();
    this.loadRecentLogs();
  }
}
</script>

<style lang="scss" scoped>
.log-management-container {
  padding: 20px;

  .log-header {
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      color: #303133;
    }
    
    p {
      margin: 10px 0 0 0;
      color: #909399;
    }
  }

  .log-stats {
    margin-bottom: 20px;

    .log-stat-item {
      .stat-content {
        display: flex;
        align-items: center;

        i {
          font-size: 36px;
          margin-right: 15px;
          color: #409EFF;
        }

        .stat-info {
          flex: 1;

          .stat-number {
            font-size: 24px;
            font-weight: bold;
            margin: 0;
            color: #303133;
          }

          .stat-label {
            font-size: 14px;
            margin: 5px 0 0 0;
            color: #909399;
          }
        }
      }
    }
  }

  .log-navigation {
    margin-bottom: 20px;

    .log-menu {
      display: flex;
      justify-content: space-around;
      flex-wrap: wrap;
      gap: 15px;

      button {
        flex: 1;
        min-width: 180px;
        margin: 5px;
        
        i {
          margin-right: 5px;
        }
      }
    }
  }

  .recent-logs-card {
    .el-table {
      margin-top: 10px;
    }
  }
}
</style>