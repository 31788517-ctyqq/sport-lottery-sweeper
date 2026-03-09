<template>
  <div class="data-quality-view">
    <h1>数据质量监控</h1>
    <el-card class="quality-summary">
      <div slot="header"><span>总体质量评分</span></div>
      <el-progress type="circle" :percentage="85" color="#6f7ad3"></el-progress>
    </el-card>

    <el-table :data="qualityMetrics" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="dataSource" label="数据源" width="200"></el-table-column>
      <el-table-column prop="metricName" label="指标" width="200"></el-table-column>
      <el-table-column prop="value" label="值" width="100"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === '正常' ? 'success' : 'danger'">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastCheckTime" label="最后检查时间"></el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockMetrics = [
  { dataSource: 'MySQL-Prod', metricName: '完整性', value: '95%', status: '正常', lastCheckTime: '2023-12-01 10:00' },
  { dataSource: 'MySQL-Prod', metricName: '准确性', value: '88%', status: '异常', lastCheckTime: '2023-12-01 10:00' },
  { dataSource: 'PostgreSQL-Staging', metricName: '一致性', value: '99%', status: '正常', lastCheckTime: '2023-12-01 09:30' }
];

export default {
  name: 'DataQualityView',
  data() {
    return {
      qualityMetrics: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.qualityMetrics = [...mockMetrics];
    }
  }
};
</script>

<style scoped>
.data-quality-view {
  padding: 20px;
}
.quality-summary {
  width: 200px;
  text-align: center;
  display: inline-block;
  vertical-align: top;
  margin-right: 20px;
}
</style>