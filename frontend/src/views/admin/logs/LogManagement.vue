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

    <el-card class="recent-logs">
      <div slot="header">
        <span>最近日志</span>
        <el-button style="float: right; padding: 3px 0" type="link" @click="refreshRecentLogs">刷新</el-button>
      </div>
      <el-table :data="recentLogs" style="width: 100%" v-loading="loadingRecent">
        <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template slot-scope="scope">
            <el-tag :type="getTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120"></el-table-column>
        <el-table-column prop="message" label="消息"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE = '/api/v1/admin/system';

export default {
  name: 'LogManagement',
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
    
    async loadStatistics() {
      try {
        const response = await axios.get(`${API_BASE}/logs/db/statistics`);
        const stats = response.data;
        
        this.totalLogs = stats.total_logs || 0;
        this.errorLogs = stats.level_stats?.find(stat => stat.level === 'ERROR')?.count || 0;
        this.userActivities = stats.module_stats?.find(stat => stat.module === 'user')?.count || 0;
        this.securityEvents = stats.module_stats?.find(stat => stat.module === 'security')?.count || 0;
      } catch (error) {
        console.error('加载日志统计失败:', error);
        this.$message.error('加载日志统计失败');
      }
    },
    
    async loadRecentLogs() {
      this.loadingRecent = true;
      try {
        const response = await axios.get(`${API_BASE}/logs/db/system?skip=0&limit=5`);
        this.recentLogs = response.data.items || [];
      } catch (error) {
        console.error('加载最近日志失败:', error);
        this.$message.error('加载最近日志失败');
      } finally {
        this.loadingRecent = false;
      }
    },
    
    async refreshRecentLogs() {
      await this.loadRecentLogs();
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

  .recent-logs {
    .el-table {
      margin-top: 10px;
    }
  }
}
</style>