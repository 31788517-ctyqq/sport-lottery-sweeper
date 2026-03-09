<template>
  <div class="intelligence-management">
    <h1>情报管理</h1>
    <el-button type="primary" @click="handlePublish">发布新情报</el-button>
    <el-table :data="intelligenceReports" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="180"></el-table-column>
      <el-table-column prop="title" label="标题" width="250"></el-table-column>
      <el-table-column prop="source" label="来源" width="180"></el-table-column>
      <el-table-column prop="priority" label="优先级">
        <template slot-scope="scope">
          <el-tag :type="getPriorityTagType(scope.row.priority)">{{ scope.row.priority }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="publishDate" label="发布时间"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleView(scope.row)">详情</el-button>
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleArchive(scope.row)">归档</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockIntelligence = [
  { id: 1, title: '关于XX技术趋势的分析报告', source: '内部研究', priority: '高', publishDate: '2023-11-10' },
  { id: 2, title: '竞争对手Y公司最新产品动态', source: '公开信息', priority: '中', publishDate: '2023-11-05' }
];

export default {
  name: 'IntelligenceManagement',
  data() {
    return {
      intelligenceReports: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.intelligenceReports = [...mockIntelligence];
    },
    getPriorityTagType(priority) {
        if (priority === '高') return 'danger';
        if (priority === '中') return 'warning';
        return 'info';
    },
    handlePublish() {
      console.log('Publish new intelligence report');
    },
    handleView(row) {
      console.log('View intelligence report:', row);
    },
    handleEdit(row) {
      console.log('Edit intelligence report:', row);
    },
    handleArchive(row) {
      console.log('Archive intelligence report:', row);
      this.intelligenceReports = this.intelligenceReports.filter(i => i.id !== row.id);
    }
  }
};
</script>

<style scoped>
.intelligence-management {
  padding: 20px;
}
</style>