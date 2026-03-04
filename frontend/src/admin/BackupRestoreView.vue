<template>
  <div class="backup-restore-view">
    <h1>备份与恢复</h1>
    
    <el-card class="operation-card">
      <div slot="header"><span>执行备份</span></div>
      <p>点击下方按钮立即创建一个完整的数据备份。</p>
      <el-button type="primary" @click="performBackup" :loading="backupLoading">开始备份</el-button>
    </el-card>

    <el-card class="operation-card">
      <div slot="header"><span>恢复备份</span></div>
      <p>选择一个备份文件进行恢复。请注意，恢复操作将覆盖当前数据。</p>
      <el-upload
        class="upload-demo"
        drag
        action="/api/restore/upload" 
        :on-success="onRestoreUploadSuccess"
        :before-upload="beforeRestoreUpload"
        accept=".sql,.zip,.bak"
        :show-file-list="false"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将备份文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">只能上传.sql, .zip, .bak文件</div>
      </el-upload>
    </el-card>

    <el-table :data="backupHistory" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="filename" label="文件名" width="300"></el-table-column>
      <el-table-column prop="size" label="大小" width="150"></el-table-column>
      <el-table-column prop="createTime" label="创建时间"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="downloadBackup(scope.row)">下载</el-button>
          <el-button size="mini" type="danger" @click="deleteBackup(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
const mockBackups = [
  { id: 1, filename: 'backup_20231201_100000.sql', size: '150 MB', createTime: '2023-12-01 10:00:00' },
  { id: 2, filename: 'backup_20231115_093000.zip', size: '85 MB', createTime: '2023-11-15 09:30:00' }
];

export default {
  name: 'BackupRestoreView',
  data() {
    return {
      backupLoading: false,
      backupHistory: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.backupHistory = [...mockBackups];
    },
    performBackup() {
      this.backupLoading = true;
      // 模拟异步备份操作
      setTimeout(() => {
        this.backupLoading = false;
        this.$message.success('备份任务已启动，请在历史记录中查看结果。');
        // 这里可以触发一个轮询来更新历史记录
      }, 2000);
    },
    beforeRestoreUpload(file) {
      // 可以在这里做文件校验
      const isSqlZipBak = file.name.endsWith('.sql') || file.name.endsWith('.zip') || file.name.endsWith('.bak');
      const isLt5G = file.size / 1024 / 1024 / 1024 < 5;

      if (!isSqlZipBak) {
        this.$message.error('上传文件只能是 SQL, ZIP 或 BAK 格式!');
      }
      if (!isLt5G) {
        this.$message.error('上传文件大小不能超过 5GB!');
      }
      return isSqlZipBak && isLt5G;
    },
    onRestoreUploadSuccess(response, file) {
      console.log('Restore upload success:', response, file);
      this.$message.success('备份文件上传成功，恢复任务已提交。');
    },
    downloadBackup(row) {
      console.log('Downloading backup:', row.filename);
      // 实现下载逻辑，例如 window.open(`/api/download/${row.filename}`)
      this.$message.info(`正在模拟下载 ${row.filename}`);
    },
    deleteBackup(row) {
      console.log('Deleting backup:', row.filename);
      this.$confirm(`此操作将永久删除备份文件 "${row.filename}"。是否继续?`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.backupHistory = this.backupHistory.filter(b => b.id !== row.id);
        this.$message.success('删除成功!');
      });
    }
  }
};
</script>

<style scoped>
.backup-restore-view {
  padding: 20px;
}
.operation-card {
  width: 48%;
  display: inline-block;
  vertical-align: top;
  margin-right: 20px;
  margin-bottom: 20px;
}
.upload-demo {
  margin-top: 20px;
}
</style>