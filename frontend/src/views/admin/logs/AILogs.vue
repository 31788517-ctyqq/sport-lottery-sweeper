<template>
  <div class="ai-logs-container">
    <el-card>
      <div slot="header">
        <span>AI服务日志</span>
        <div class="header-tools">
          <el-input
            v-model="searchQuery"
            placeholder="搜索日志..."
            style="width: 200px; margin-right: 10px;"
            suffix-icon="el-icon-search"
          ></el-input>
          <el-select v-model="logLevelFilter" placeholder="日志级别" style="width: 120px; margin-right: 10px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="DEBUG" value="DEBUG"></el-option>
            <el-option label="INFO" value="INFO"></el-option>
            <el-option label="WARN" value="WARN"></el-option>
            <el-option label="ERROR" value="ERROR"></el-option>
            <el-option label="CRITICAL" value="CRITICAL"></el-option>
          </el-select>
          <el-select v-model="moduleFilter" placeholder="模块筛选" style="width: 150px; margin-right: 10px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="AI服务" value="ai"></el-option>
            <el-option label="LLM" value="llm"></el-option>
            <el-option label="对话助手" value="conversation"></el-option>
            <el-option label="智能体" value="agent"></el-option>
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

      <el-table 
        :data="logs" 
        style="width: 100%" 
        height="600" 
        border 
        v-loading="loading"
        :row-key="getRowKey">
        <el-table-column prop="timestamp" label="时间" width="160">
          <template #default="scope">
            {{ scope.row.timestamp }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120">
          <template #default="scope">
            {{ scope.row.module }}
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息">
          <template #default="scope">
            {{ scope.row.message }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" type="link" @click="viewDetails(scope.row)">查看详情</el-button>
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
        <p><strong>模块:</strong> {{ selectedLog.module }}</p>
        <p><strong>消息:</strong> {{ selectedLog.message }}</p>
        <p v-if="selectedLog.extra_data"><strong>额外数据:</strong> {{ selectedLog.extra_data }}</p>
        <p v-if="selectedLog.user_id"><strong>用户ID:</strong> {{ selectedLog.user_id }}</p>
        <p v-if="selectedLog.ip_address"><strong>IP地址:</strong> {{ selectedLog.ip_address }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="showDetailDialog = false">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import http from '@/utils/http';  // 使用配置了拦截器的实例

const API_BASE = '/api/v1/admin/system';

export default {
  name: 'AILogs',
  data() {
    return {
      searchQuery: '',
      logLevelFilter: '',
      moduleFilter: '',
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
    // 为表格行添加唯一键，防止渲染错乱
    getRowKey(row) {
      return row.id + '_' + row.timestamp;
    },
    
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
        
        if (this.moduleFilter) {
          params.module = this.moduleFilter;
        }
        
        if (this.searchQuery) {
          params.search = this.searchQuery;
        }
        
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0].toISOString();
          params.end_date = this.dateRange[1].toISOString();
        }
        
        const response = await http.get(`${API_BASE}/logs/db/ai`, { params });  // 使用http实例
        // 处理响应数据：http拦截器可能返回数组或对象
        let logsData = [];
        let totalFromResponse = 0;
        
        if (Array.isArray(response)) {
          // 直接返回数组的情况
          logsData = response;
        } else if (response && typeof response === 'object') {
          // 对象响应，可能包含items或data字段
          if (Array.isArray(response.items)) {
            logsData = response.items;
            totalFromResponse = response.total || 0;
          } else if (Array.isArray(response.data)) {
            logsData = response.data;
            totalFromResponse = response.total || 0;
          }
          // 如果response是对象但没有items/data数组，logsData保持为空数组
        }
        
        this.logs = logsData;
        
        // 设置总数：优先使用响应中的total，否则调用统计API
        if (totalFromResponse > 0) {
          this.totalLogs = totalFromResponse;
        } else {
          // 调用统计API获取总数
          try {
            const statsResponse = await http.get(`${API_BASE}/logs/db/statistics`);
            if (statsResponse && statsResponse.total_logs !== undefined) {
              this.totalLogs = statsResponse.total_logs;
            } else {
              // 如果统计API也不可用，使用一个较大的默认值
              this.totalLogs = logsData.length > 0 ? 1000 : 0;
            }
          } catch (statsError) {
            console.warn('无法获取日志总数，使用默认值:', statsError);
            this.totalLogs = logsData.length > 0 ? 1000 : 0;
          }
        }
      } catch (error) {
        if (error.response?.status === 401) {
          this.$message.error('登录已过期，请重新登录');
          this.$router.push('/login'); // 跳转登录页
        } else {
          console.error('加载AI服务日志失败:', error);
          this.$message.error('加载AI服务日志失败');
        }
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
          return ''
        case 'DEBUG':
          return 'info'
        default:
          return ''
      }
    },
    
    refreshLogs() {
      this.currentPage = 1;
      this.loadLogs();
    }
  },
  
  mounted() {
    this.loadLogs();
  }
}
</script>

<style lang="scss" scoped>
.ai-logs-container {
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

  .stack-trace {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    white-space: pre-wrap;
    word-break: break-all;
    overflow-x: auto;
    max-height: 300px;
    overflow-y: auto;
  }
}
</style>