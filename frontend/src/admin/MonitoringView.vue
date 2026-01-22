<template>
  <div class="monitoring-view">
    <h1>监控运维</h1>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>CPU 使用率</span>
          </div>
          <el-progress type="dashboard" :percentage="75" color="#67c23a"></el-progress>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>内存使用率</span>
          </div>
          <el-progress type="dashboard" :percentage="60" color="#e6a23c"></el-progress>
        </el-card>
      </el-col>
    </el-row>

    <el-table :data="serverLogs" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="timestamp" label="时间戳" width="200"></el-table-column>
      <el-table-column prop="level" label="级别" width="100">
        <template slot-scope="scope">
          <el-tag :type="getLogLevelTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="message" label="消息"></el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockLogs = [
  { timestamp: '2023-12-01 10:00:01', level: 'INFO', message: '系统启动' },
  { timestamp: '2023-12-01 10:05:23', level: 'WARN', message: '磁盘空间不足' },
  { timestamp: '2023-12-01 10:10:45', level: 'ERROR', message: '数据库连接失败' }
];

export default {
  name: 'MonitoringView',
  data() {
    return {
      serverLogs: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.serverLogs = [...mockLogs];
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
.monitoring-view {
  padding: 20px;
}
.box-card {
  height: 250px;
  text-align: center;
}
</style>