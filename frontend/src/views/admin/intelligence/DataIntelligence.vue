<template>
  <div class="data-intelligence-container">
    <el-card class="data-intelligence-card">
      <template #header>
        <div class="card-header">
          <h3>数据情报</h3>
        </div>
      </template>
      
      <!-- 数据情报内容 -->
      <div class="content-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">1,234</div>
                <div class="stat-label">数据总量</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">567</div>
                <div class="stat-label">今日新增</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">89%</div>
                <div class="stat-label">准确率</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">23</div>
                <div class="stat-label">活跃情报</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 情报列表 -->
        <el-card class="data-list-card">
          <div class="card-header">
            <h4>情报列表</h4>
            <el-button type="primary" @click="addNewIntelligence">新增情报</el-button>
          </div>
          
          <el-table :data="intelligenceList" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="scope">
                <el-tag :type="getIntelligenceTypeTag(scope.row.type)">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="source" label="来源" width="120" />
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="scope">
                <el-rate 
                  v-model="scope.row.priority" 
                  :max="3" 
                  disabled 
                  show-score 
                  score-template="{value}" 
                  :colors="['#F56C6C', '#E6A23C', '#67C23A']"
                />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getIntelligenceStatusTag(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewDetail(scope.row)">查看</el-button>
                <el-button size="small" type="primary" @click="editIntelligence(scope.row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 数据状态
const intelligenceList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 初始化数据
onMounted(() => {
  loadIntelligenceList()
})

// 加载情报列表
const loadIntelligenceList = async () => {
  loading.value = true
  
  // 模拟数据加载
  setTimeout(() => {
    intelligenceList.value = [
      { id: 1, title: '英超联赛数据分析报告', type: '分析', source: '爬虫', priority: 3, status: '已发布', createdAt: '2024-01-20 10:30:00' },
      { id: 2, title: '德甲球队状态趋势预测', type: '预测', source: '模型', priority: 2, status: '审核中', createdAt: '2024-01-20 09:15:00' },
      { id: 3, title: '意甲关键球员伤病情报', type: '情报', source: '新闻', priority: 3, status: '已发布', createdAt: '2024-01-20 08:45:00' },
      { id: 4, title: '西甲球队近期表现对比', type: '对比', source: '数据库', priority: 1, status: '草稿', createdAt: '2024-01-19 17:20:00' },
      { id: 5, title: '法甲联赛赔率变动分析', type: '分析', source: 'API', priority: 2, status: '已发布', createdAt: '2024-01-19 16:10:00' },
      { id: 6, title: '荷甲青年队潜力评估', type: '评估', source: '专家', priority: 1, status: '审核中', createdAt: '2024-01-19 15:05:00' },
      { id: 7, title: '葡超转会市场动态', type: '动态', source: '新闻', priority: 2, status: '已发布', createdAt: '2024-01-19 14:30:00' },
      { id: 8, title: '俄超天气影响预测', type: '预测', source: '气象', priority: 3, status: '已发布', createdAt: '2024-01-19 13:45:00' },
      { id: 9, title: '美职联季后赛形势分析', type: '分析', source: '统计', priority: 2, status: '草稿', createdAt: '2024-01-19 12:20:00' },
      { id: 10, title: '中超外援政策影响', type: '政策', source: '官方', priority: 1, status: '已发布', createdAt: '2024-01-19 11:15:00' },
    ]
    total.value = 100
    loading.value = false
  }, 800)
}

// 处理分页大小改变
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadIntelligenceList()
}

// 处理当前页改变
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadIntelligenceList()
}

// 获取情报类型标签
const getIntelligenceTypeTag = (type) => {
  const typeMap = {
    '分析': 'info',
    '预测': 'warning',
    '情报': 'success',
    '对比': 'primary',
    '评估': 'danger',
    '动态': 'info',
    '政策': 'primary'
  }
  return typeMap[type] || 'info'
}

// 获取情报状态标签
const getIntelligenceStatusTag = (status) => {
  const statusMap = {
    '已发布': 'success',
    '审核中': 'warning',
    '草稿': 'info'
  }
  return statusMap[status] || 'info'
}

// 查看详情
const viewDetail = (item) => {
  ElMessage.info(`查看情报 ${item.id} 详情`)
}

// 编辑情报
const editIntelligence = (item) => {
  ElMessage.info(`编辑情报 ${item.id}`)
}

// 新增情报
const addNewIntelligence = () => {
  ElMessage.info('新增情报')
}

</script>

<style scoped>
.data-intelligence-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: 100%;
}

.data-intelligence-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-weight: 600;
  color: #303133;
}

.card-header h4 {
  margin: 0;
  font-weight: 500;
  color: #606266;
}

.stat-card {
  text-align: center;
  margin-bottom: 20px;
}

.stat-item {
  padding: 10px 0;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.content-section {
  margin-top: 20px;
}

.data-list-card {
  margin-top: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-table {
  margin-top: 20px;
}
</style>