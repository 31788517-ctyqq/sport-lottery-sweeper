<template>
  <div class="user-management">
    <h1>用户管理</h1>
    <el-button type="primary" @click="handleCreate">添加用户</el-button>
    <el-table :data="users" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="180"></el-table-column>
      <el-table-column prop="username" label="用户名" width="180"></el-table-column>
      <el-table-column prop="email" label="邮箱"></el-table-column>
      <el-table-column prop="role" label="角色"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
// 假设这是从API获取的数据
const mockUsers = [
  { id: 1, username: 'admin', email: 'admin@example.com', role: 'Admin' },
  { id: 2, username: 'user1', email: 'user1@example.com', role: 'User' }
];

export default {
  name: 'UserManagement',
  data() {
    return {
      users: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      // 模拟API调用
      this.users = [...mockUsers];
    },
    handleCreate() {
      console.log('Create new user');
      // 实现创建逻辑
    },
    handleEdit(row) {
      console.log('Edit user:', row);
      // 实现编辑逻辑
    },
    handleDelete(row) {
      console.log('Delete user:', row);
      // 实现删除逻辑
      this.users = this.users.filter(u => u.id !== row.id);
    }
  }
};
</script>

<style scoped>
.user-management {
  padding: 20px;
}
</style>