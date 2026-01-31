<template>
  <div class="api-logs-container">
    <el-card>
      <div slot="header">
        <span>API日志</span>
        <div class="header-tools">
          <el-input
            v-model="searchQuery"
            placeholder="搜索日志..."
            style="width: 200px; margin-right: 10px;"
            suffix-icon="el-icon-search"
          ></el-input>
          <el-select v-model="logLevelFilter" placeholder="日志级别" style="width: 120px; margin-right: 10px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="INFO" value="INFO"></el-option>
            <el-option label="WARN" value="WARN"></el-option>
            <el-option label="ERROR" value="ERROR"></el-option>
            <el-option label="CRITICAL" value="CRITICAL"></el-option>
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 350px; margin-right: 10px;">
          </el-date-picker>
          <el-button type="primary" @click="applyFilters">筛选</el-button>
        </div>
      </div>

      <el-table :data="logs" style="width: 100%" height="600" border v-loading="loading">
        <el-table-column prop="timestamp" label="时间" width="160"></el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template slot-scope="scope">
            <el-tag :type="getTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="request_path" label="请求路径" width="200"></el-table-column>
        <el-table-column prop="response_status" label="状态码" width="100"></el-table-column>
        <el-table-column prop="duration_ms" label="耗时(ms)" width="100"></el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="150"></el-table-column>
        <el-table-column prop="message" label="消息"></el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button size="mini" type="link" @click="viewDetails(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[20, 50, 100, 200]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalLogs">
        </el-pagination>
      </div>
    </el-card>

    <!-- 日志详情弹窗 -->
    <el-dialog title="日志详情" :visible.sync="showDetailDialog" width="60%">
      <div v-if="selectedLog">
        <p><strong>时间:</strong> {{ selectedLog.timestamp }}</p>
        <p><strong>级别:</strong> <el-tag :type="getTagType(selectedLog.level)">{{ selectedLog.level }}</el-tag></p>
        <p><strong>请求路径:</strong> {{ selectedLog.request_path }}</p>
        <p><strong>响应状态:</strong> {{ selectedLog.response_status }}</p>
        <p><strong>耗时:</strong> {{ selectedLog.duration_ms }}ms</p>
        <p><strong>IP地址:</strong> {{ selectedLog.ip_address }}</p>
        <p><strong>用户代理:</strong> {{ selectedLog.user_agent }}</p>
        <p><strong>会话ID:</strong> {{ selectedLog.session_id }}</p>
        <p><strong>消息:</strong> {{ selectedLog.message }}</p>
        <p v-if="selectedLog.extra_data"><strong>额外数据:</strong> {{ selectedLog.extra_data }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="showDetailDialog = false">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE = '/api/v1/admin/system';

export default {
  name: 'APILogs',
  data() {
    return {
      searchQuery: '',
      logLevelFilter: '',
      dateRange: [],
      currentPage: 1,
      pageSize: 50,
      totalLogs: 0,
      showDetailDialog: false,
      selectedLog: null,
      logs: [],
      loading: false
    }
  },
  methods: {
    async loadLogs() {
      this.loading = true;
      try {
        // 构建查询参数
        const params = {
          skip: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize,
        };
        
        if (this.logLevelFilter) {
          params.level = this.logLevelFilter;
        }
        
        if (this.searchQuery) {
          params.search = this.searchQuery;
        }
        
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0].toISOString();
          params.end_date = this.dateRange[1].toISOString();
        }
        
        const response = await axios.get(`${API_BASE}/logs/db/api`, { params });
        this.logs = response.data.items || [];
        this.totalLogs = response.data.total || 0;
      } catch (error) {
        console.error('加载API日志失败:', error);
        this.$message.error('加载API日志失败');
      } finally {
        this.loading = false;
      }
    },
    
    applyFilters() {
      this.currentPage = 1;  // 重置到第一页
      this.loadLogs();
    },
    
    handleSizeChange(val) {
      this.pageSize = val;
      this.loadLogs();
    },
    
    handleCurrentChange(val) {
      this.currentPage = val;
      this.loadLogs();
    },
    
    viewDetails(log) {
      this.selectedLog = log;
      this.showDetailDialog = true;
    },
    
    getTagType(level) {
      switch(level.toUpperCase()) {
        case 'ERROR':
        case 'CRITICAL':
          return 'danger'
        case 'WARN':
        case 'WARNING':
          return 'warning'
        case 'INFO':
          return 'info'
        case 'DEBUG':
          return 'primary'
        default:
          return 'info'
      }
    }
  },
  
  mounted() {
    this.loadLogs();
  }
}
</script>

<style lang="scss" scoped>
.api-logs-container {
  padding: 20px;

  .header-tools {
    float: right;
    display: flex;
    align-items: center;
  }

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
}
</style>