// This file has been deprecated and replaced by the version in /views/admin/crawler/
// It is kept as a backup for reference purposes
// Main functionality is now in: src/views/admin/crawler/DataSourceManagement.vue

<template>
  <div class="data-source-management">
    <h1>数据源管理</h1>
    
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleAdd">添加数据源</el-button>
      <el-button type="success" @click="handleAdd100qiu">添加100qiu数据源</el-button>
      <el-input 
        v-model="searchQuery" 
        placeholder="搜索数据源..." 
        style="width: 300px; margin-left: 20px;"
        @keyup.enter.native="handleSearch"
      />
      <el-button icon="el-icon-search" @click="handleSearch" style="margin-left: 10px;">搜索</el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-table 
      :data="dataSources" 
      style="width: 100%; margin-top: 20px;" 
      v-loading="loading"
    >
      <el-table-column prop="source_id" label="ID" width="120"></el-table-column>
      <el-table-column prop="name" label="名称" width="200"></el-table-column>
      <el-table-column prop="type" label="类型" width="120"></el-table-column>
      <el-table-column prop="url" label="URL" width="300">
        <template slot-scope="scope">
          <el-popover trigger="hover" placement="top">
            <p>{{ scope.row.url }}</p>
            <div slot="reference" class="name-wrapper">
              <el-tag size="small">{{ scope.row.url | ellipsis }}</el-tag>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag 
            :type="scope.row.status === 'online' ? 'success' : 'danger'"
          >
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="error_rate" label="错误率" width="100">
        <template slot-scope="scope">
          <span>{{ scope.row.error_rate }}%</span>
        </template>
      </el-table-column>
      <el-table-column prop="last_update" label="最后更新" width="180">
        <template slot-scope="scope">
          {{ scope.row.last_update | formatDate }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <!-- 100qiu数据源特有的获取按钮 -->
          <el-button 
            v-if="scope.row.type === '100qiu'" 
            size="mini" 
            type="success" 
            @click="handleFetch(scope.row.id)"
            :loading="fetchingId === scope.row.id"
          >
            获取
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        @current-change="handlePageChange"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
      ></el-pagination>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataSourceManagement',
  data() {
    return {
      searchQuery: '',
      dataSources: [],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      fetchingId: null // 用于跟踪正在获取的数据源ID
    }
  },
  methods: {
    handleAdd() {
      // 打开新增表单
      this.$router.push('/admin/data-source/add')
    },
    handleAdd100qiu() {
      // 打开100qiu专用表单
      this.$router.push('/admin/data-source/add-100qiu')
    },
    handleSearch() {
      this.currentPage = 1;
      this.loadData();
    },
    handlePageChange(page) {
      this.currentPage = page;
      this.loadData();
    },
    handleEdit(row) {
      // 编辑数据源
      this.$router.push(`/admin/data-source/edit/${row.id}`)
    },
    handleDelete(row) {
      // 删除数据源
      this.$confirm('确定要删除此数据源吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用删除API
        this.deleteSource(row.id);
      }).catch(() => {
        // 取消操作
      });
    },
    // 100qiu数据源获取功能
    async handleFetch(id) {
      this.fetchingId = id;
      try {
        const response = await fetch(`/api/v1/data-source-100qiu/${id}/fetch`, {
          method: 'POST',
          credentials: 'include'
        });
        const result = await response.json();
        
        if (result.success) {
          this.$message.success(`获取成功，获取数量：${result.total_fetched}；${result.message}`);
        } else {
          throw new Error(result.message || '获取失败');
        }
      } catch (error) {
        console.error('获取数据失败:', error);
        let errorMessage = '获取失败';
        if (typeof error === 'string') {
          errorMessage = error;
        } else if (error.message) {
          errorMessage = error.message;
        }
        this.$message.error(errorMessage);
      } finally {
        this.fetchingId = null;
      }
    },
    // 修改loadData方法，使用直接fetch调用
    async loadData() {
      this.loading = true;
      try {
        // 构建查询参数
        const queryParams = [];
        if (this.currentPage) queryParams.push(`page=${this.currentPage}`);
        if (this.pageSize) queryParams.push(`size=${this.pageSize}`);
        if (this.searchQuery) queryParams.push(`search=${encodeURIComponent(this.searchQuery)}`);
        
        const queryString = queryParams.length > 0 ? '?' + queryParams.join('&') : '';
        const url = `/api/v1/admin/sources${queryString}`;
        
        const response = await fetch(url, {
          method: 'GET',
          credentials: 'include'
        });
        const data = await response.json();
        if (data.success) {
          this.dataSources = data.data.items;
          this.total = data.data.total;
        } else {
          throw new Error('加载失败');
        }
      } catch (error) {
        console.error('加载数据失败:', error);
        this.$message.error('加载失败');
      } finally {
        this.loading = false;
      }
    },
    deleteSource(id) {
      // 删除指定ID的数据源
      this.$api.crawler.deleteSource(id).then(res => {
        this.$message.success('删除成功');
        this.loadData();
      }).catch(err => {
        this.$message.error('删除失败');
      });
    }
  },
  mounted() {
    this.loadData();
  }
}
</script>

<style scoped>
.data-source-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 400px;
}
</style>