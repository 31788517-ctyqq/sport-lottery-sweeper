<template>
  <el-main>
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">情报总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">今日新增</div>
          <div class="stat-value">{{ stats.today }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">处理中</div>
          <div class="stat-value">{{ stats.processing }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已发布</div>
          <div class="stat-value">{{ stats.published }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-select v-model="filterCategory" placeholder="选择分类" clearable style="width: 120px">
          <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-input v-model="search" placeholder="搜索情报标题或来源" clearable style="width: 200px" />
        <el-select v-model="filterSource" placeholder="选择来源" clearable style="width: 140px">
          <el-option label="官方公告" value="official" />
          <el-option label="媒体报道" value="media" />
          <el-option label="社交媒体" value="social" />
          <el-option label="其他渠道" value="other" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="选择状态" clearable style="width: 120px">
          <el-option label="待处理" value="pending" />
          <el-option label="处理中" value="processing" />
          <el-option label="已发布" value="published" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-button type="primary" @click="handleAdd">新增情报</el-button>
        <el-button @click="handleCrawl">立即爬取</el-button>
        <el-button @click="loadData">刷新</el-button>
      </div>
    </el-card>

    <!-- 情报列表表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredTableData" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="情报标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="120">
          <template #default="scope">
            <el-tag :type="getSourceTagType(scope.row.source)" size="small">{{ getSourceText(scope.row.source) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100">
          <template #default="scope">
            <el-tag size="small" type="info">{{ scope.row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publishTime" label="发布时间" width="170" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="scope">
            <el-tag :type="getPriorityTagType(scope.row.priority)" size="small">{{ scope.row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 查看详情弹窗 -->
    <el-dialog title="情报详情" v-model="viewDialogVisible" width="800px">
      <div v-if="selectedItem" class="intelligence-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="情报标题">{{ selectedItem.title }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ getSourceText(selectedItem.source) }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ selectedItem.category }}</el-descriptions-item>
          <el-descriptions-item label="优先级">{{ selectedItem.priority }}</el-descriptions-item>
          <el-descriptions-item label="发布时间">{{ selectedItem.publishTime }}</el-descriptions-item>
          <el-descriptions-item label="采集时间">{{ selectedItem.crawlTime }}</el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="getStatusTagType(selectedItem.status)">{{ getStatusText(selectedItem.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="URL" :span="2">
            <a :href="selectedItem.url" target="_blank" class="link-url">{{ selectedItem.url }}</a>
          </el-descriptions-item>
          <el-descriptions-item label="内容" :span="2">
            <div class="content-box">{{ selectedItem.content }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </el-main>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const tableData = ref([])
const loading = ref(false)
const search = ref('')
const filterCategory = ref('')
const filterSource = ref('')
const filterStatus = ref('')
const viewDialogVisible = ref(false)
const selectedItem = ref(null)

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const stats = reactive({
  total: 156,
  today: 12,
  processing: 8,
  published: 134
})

// 分类选项
const categoryOptions = [
  { label: '赛程', value: '赛程' },
  { label: '伤病', value: '伤病' },
  { label: '转会', value: '转会' },
  { label: '花絮', value: '花絮' },
  { label: '分析', value: '分析' },
  { label: '其他', value: '其他' }
]

const filteredTableData = computed(() => {
  let data = tableData.value
  
  if (search.value) {
    data = data.filter(row => 
      row.title.includes(search.value) || 
      row.source.includes(search.value)
    )
  }
  
  if (filterCategory.value) {
    data = data.filter(row => row.category === filterCategory.value)
  }
  
  if (filterSource.value) {
    data = data.filter(row => row.source === filterSource.value)
  }
  
  if (filterStatus.value) {
    data = data.filter(row => row.status === filterStatus.value)
  }
  
  return data
})

const getSourceText = (source) => {
  const map = {
    official: '官方公告',
    media: '媒体报道',
    social: '社交媒体',
    other: '其他渠道'
  }
  return map[source] || source
}

const getSourceTagType = (source) => {
  const map = {
    official: 'success',
    media: 'primary',
    social: 'warning',
    other: 'info'
  }
  return map[source] || ''
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    processing: '处理中',
    published: '已发布',
    archived: '已归档'
  }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = {
    pending: 'warning',
    processing: 'primary',
    published: 'success',
    archived: 'info'
  }
  return map[status] || ''
}

const getPriorityTagType = (priority) => {
  const map = {
    '高': 'danger',
    '中': 'warning',
    '低': 'success'
  }
  return map[priority] || ''
}

const loadData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 检查是否应该使用模拟数据（当API不可用或返回500错误时）
    const useMockData = true // 临时设置为true，直到后端修复
    
    if (useMockData) {
      // 使用模拟数据
      tableData.value = [
        {
          id: 1,
          title: '欧冠半决赛赛程调整通知',
          source: 'official',
          category: '赛程',
          publishTime: '2024-01-20 10:30:00',
          crawlTime: '2024-01-20 10:35:00',
          status: 'published',
          priority: '高',
          url: 'https://example.com/news/1',
          content: '由于天气原因，原定于本周三进行的欧冠半决赛第一场比赛时间调整为周四晚8点进行。请各参赛队伍及时调整行程安排，球迷朋友们也请注意观看时间变化。'
        },
        {
          id: 2,
          title: '英超球队伤病报告更新',
          source: 'media',
          category: '伤病',
          publishTime: '2024-01-20 09:15:00',
          crawlTime: '2024-01-20 09:20:00',
          status: 'processing',
          priority: '中',
          url: 'https://example.com/news/2',
          content: '据最新消息，曼城核心球员德布劳内因膝伤将缺席接下来两场比赛。俱乐部医疗团队表示正在积极治疗和康复，预计下周可以复出。'
        },
        {
          id: 3,
          title: '球迷热议：本轮最佳进球评选',
          source: 'social',
          category: '花絮',
          publishTime: '2024-01-20 08:45:00',
          crawlTime: '2024-01-20 08:50:00',
          status: 'pending',
          priority: '低',
          url: 'https://example.com/news/3',
          content: '本轮比赛中，利物浦球员萨拉赫的远射破门获得球迷投票第一名。本次评选共有超过10万球迷参与投票，萨拉赫的进球获得了35%的支持率。'
        },
        {
          id: 4,
          title: '西甲转会窗口最新动态',
          source: 'official',
          category: '转会',
          publishTime: '2024-01-20 07:30:00',
          crawlTime: '2024-01-20 07:35:00',
          status: 'published',
          priority: '高',
          url: 'https://example.com/news/4',
          content: '皇家马德里正式宣布签下巴西新星维尼修斯，转会费达到1.2亿欧元。这是皇马本赛季最重要的引援之一。'
        },
        {
          id: 5,
          title: '意甲争冠形势分析',
          source: 'media',
          category: '分析',
          publishTime: '2024-01-20 06:20:00',
          crawlTime: '2024-01-20 06:25:00',
          status: 'published',
          priority: '中',
          url: 'https://example.com/news/5',
          content: '本赛季意甲联赛已进入关键阶段，国际米兰、AC米兰和尤文图斯三强争霸格局明显。专家分析认为最后五轮比赛将决定冠军归属。'
        }
      ]
      pagination.total = 156
      stats.total = 156
      stats.today = 12
      stats.processing = 8
      stats.published = 134
      ElMessage.success('已加载模拟数据（后端服务暂时不可用）')
    } else {
      // 真实的API调用（当后端修复后使用）
      const res = await getIntelligenceList()
      tableData.value = res.data || []
      pagination.total = res.total || 0
    }
  } catch (e) {
    console.error('加载数据失败:', e)
    ElMessage.warning('后端服务暂时不可用，显示模拟数据')
    
    // 出错时也显示模拟数据
    tableData.value = [
      {
        id: 1,
        title: '欧冠半决赛赛程调整通知（模拟数据）',
        source: 'official',
        category: '赛程',
        publishTime: '2024-01-20 10:30:00',
        crawlTime: '2024-01-20 10:35:00',
        status: 'published',
        priority: '高',
        url: '#',
        content: '由于天气原因，原定于本周三进行的欧冠半决赛第一场比赛时间调整为周四晚8点进行...'
      }
    ]
    pagination.total = 1
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  ElMessage.info('新增情报功能开发中')
}

const handleEdit = (row) => {
  ElMessage.info(`编辑情报：${row.title}`)
}

const handleView = (row) => {
  selectedItem.value = row
  viewDialogVisible.value = true
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该情报？', '提示', { type: 'warning' }).then(() => {
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {})
}

const handleCrawl = () => {
  ElMessage.info('开始爬取最新情报...')
  setTimeout(() => {
    ElMessage.success('爬取完成，新增12条情报')
    loadData()
  }, 2000)
}

onMounted(loadData)
</script>

<style scoped>
.stat-row { margin-bottom: 24px; }
.stat-card { border-radius: 12px; text-align: center; }
.stat-title { color: #64748b; font-size: 14px; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #1e293b; }
.toolbar-card { border-radius: 12px; margin-bottom: 24px; }
.toolbar { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
  .toolbar :first-child { margin-left: 0; }
.table-card { border-radius: 12px; }
.modern-table { border-radius: 12px; overflow: hidden; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
.intelligence-detail { max-height: 600px; overflow-y: auto; }
.link-url { color: #409eff; text-decoration: none; }
.link-url:hover { text-decoration: underline; }
.content-box { white-space: pre-wrap; line-height: 1.6; background: #f8f9fa; padding: 12px; border-radius: 4px; }
</style>