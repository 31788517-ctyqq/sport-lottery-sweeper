<template>
  <div class="api-management-view">
    <h1>API管理</h1>
    <el-button type="primary" @click="handleCreate">新增API</el-button>
    <el-table :data="apis" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="100"></el-table-column>
      <el-table-column prop="name" label="接口名称" width="200"></el-table-column>
      <el-table-column prop="path" label="路径" width="250"></el-table-column>
      <el-table-column prop="method" label="方法" width="100">
        <template slot-scope="scope">
          <el-tag :type="getMethodTagType(scope.row.method)">{{ scope.row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'enabled' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="rateLimit" label="速率限制" width="150"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleView(scope.row)">详情</el-button>
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleToggleStatus(scope.row)">
            {{ scope.row.status === 'enabled' ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockApis = [
  { id: 1, name: '获取用户列表', path: '/api/users', method: 'GET', status: 'enabled', rateLimit: '100/min' },
  { id: 2, name: '创建用户', path: '/api/users', method: 'POST', status: 'disabled', rateLimit: '50/min' }
];

export default {
  name: 'ApiManagementView',
  data() {
    return {
      apis: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.apis = [...mockApis];
    },
    getMethodTagType(method) {
        const colorMap = { 'GET': 'success', 'POST': 'warning', 'PUT': 'primary', 'DELETE': 'danger' };
        return colorMap[method] || 'info';
    },
    handleCreate() {
      console.log('Create new API');
    },
    handleView(row) {
      console.log('View API details:', row);
    },
    handleEdit(row) {
      console.log('Edit API:', row);
    },
    handleToggleStatus(row) {
      console.log(`Toggling status for API ID ${row.id}`);
      row.status = row.status === 'enabled' ? 'disabled' : 'enabled';
    }
  }
};
</script>

<style scoped>
.api-management-view {
  padding: 20px;
}
</style>