<template>
  <div class="log-management">
    <h1>日志管理</h1>
    <el-form :inline="true" :model="queryForm" class="demo-form-inline">
      <el-form-item label="日志级别">
        <el-select v-model="queryForm.level" placeholder="请选择">
          <el-option label="全部" value=""></el-option>
          <el-option label="INFO" value="INFO"></el-option>
          <el-option label="WARN" value="WARN"></el-option>
          <el-option label="ERROR" value="ERROR"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="关键词">
        <el-input v-model="queryForm.keyword" placeholder="请输入关键词"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onQuery">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="logs" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="timestamp" label="时间戳" width="200"></el-table-column>
      <el-table-column prop="level" label="级别" width="100">
        <template slot-scope="scope">
          <el-tag :type="getLogLevelTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="service" label="服务名" width="150"></el-table-column>
      <el-table-column prop="message" label="消息"></el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockAllLogs = [
  { timestamp: '2023-12-01 10:00:01', level: 'INFO', service: 'user-service', message: 'User login successful' },
  { timestamp: '2023-12-01 10:05:23', level: 'WARN', service: 'db-service', message: 'Slow query detected' },
  { timestamp: '2023-12-01 10:10:45', level: 'ERROR', service: 'api-gateway', message: 'Request timeout' },
  { timestamp: '2023-12-01 10:12:10', level: 'INFO', service: 'auth-service', message: 'Token generated' }
];

export default {
  name: 'LogManagement',
  data() {
    return {
      logs: [],
      queryForm: {
        level: '',
        keyword: ''
      }
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.logs = [...mockAllLogs];
    },
    onQuery() {
      let filteredLogs = mockAllLogs;
      if (this.queryForm.level) {
        filteredLogs = filteredLogs.filter(log => log.level === this.queryForm.level);
      }
      if (this.queryForm.keyword) {
        const kw = this.queryForm.keyword.toLowerCase();
        filteredLogs = filteredLogs.filter(log => log.message.toLowerCase().includes(kw));
      }
      this.logs = filteredLogs;
    },
    getLogLevelTagType(level) {
        if (level === 'ERROR') return 'danger';
        if (level === 'WARN') return 'warning';
        if (level === 'INFO') return 'info';
        return 'primary';
    }
  }
};
</script>

<style scoped>
.log-management {
  padding: 20px;
}
.demo-form-inline {
  display: flex;
  align-items: flex-start; /* 对齐按钮 */
}
</style>