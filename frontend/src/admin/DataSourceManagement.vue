<template>
  <div class="data-source-management">
    <h1>数据源管理</h1>
    <el-button type="primary" @click="handleAdd">添加数据源</el-button>
    <el-table :data="dataSources" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="name" label="名称" width="180"></el-table-column>
      <el-table-column prop="type" label="类型" width="180"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleTest(scope.row)">测试连接</el-button>
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockDataSources = [
  { id: 1, name: 'MySQL-Prod', type: 'MySQL', status: 'active' },
  { id: 2, name: 'PostgreSQL-Staging', type: 'PostgreSQL', status: 'inactive' }
];

export default {
  name: 'DataSourceManagement',
  data() {
    return {
      dataSources: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.dataSources = [...mockDataSources];
    },
    handleAdd() {
      console.log('Add new data source');
    },
    handleTest(row) {
      console.log('Testing connection for:', row.name);
    },
    handleEdit(row) {
      console.log('Edit data source:', row);
    },
    handleDelete(row) {
      console.log('Delete data source:', row);
      this.dataSources = this.dataSources.filter(ds => ds.id !== row.id);
    }
  }
};
</script>

<style scoped>
.data-source-management {
  padding: 20px;
}
</style>