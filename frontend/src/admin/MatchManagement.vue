<template>
  <div class="match-management">
    <h1>比赛管理</h1>
    <el-button type="primary" @click="handleCreate">创建比赛</el-button>
    <el-table :data="matches" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="180"></el-table-column>
      <el-table-column prop="name" label="比赛名称" width="250"></el-table-column>
      <el-table-column prop="startDate" label="开始日期"></el-table-column>
      <el-table-column prop="endDate" label="结束日期"></el-table-column>
      <el-table-column prop="status" label="状态">
         <template slot-scope="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleView(scope.row)">查看</el-button>
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockMatches = [
  { id: 1, name: '全国大学生程序设计竞赛', startDate: '2023-10-01', endDate: '2023-10-03', status: '已结束' },
  { id: 2, name: '国际人工智能挑战赛', startDate: '2024-05-15', endDate: '2024-05-17', status: '进行中' },
  { id: 3, name: '未来科技黑客马拉松', startDate: '2024-08-20', endDate: '2024-08-22', status: '未开始' }
];

export default {
  name: 'MatchManagement',
  data() {
    return {
      matches: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.matches = [...mockMatches];
    },
    getStatusTagType(status) {
        if (status === '进行中') return 'success';
        if (status === '未开始') return 'info';
        if (status === '已结束') return 'warning';
        return 'danger';
    },
    handleCreate() {
      console.log('Create new match');
    },
    handleView(row) {
      console.log('View match details:', row);
    },
    handleEdit(row) {
      console.log('Edit match:', row);
    },
    handleDelete(row) {
      console.log('Delete match:', row);
      this.matches = this.matches.filter(m => m.id !== row.id);
    }
  }
};
</script>

<style scoped>
.match-management {
  padding: 20px;
}
</style>