<template>
  <div class="data-management-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 数据管理</h1>
      <p class="page-description">管理比赛数据、情报数据和系统数据</p>
    </div>

    <!-- 快速操作工具栏 -->
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchKeyword"
          type="text"
          placeholder="搜索数据..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">
          <span>🔍</span> 搜索
        </button>
      </div>
      
      <div class="filters">
        <select v-model="filters.dataType" @change="handleFilterChange">
          <option value="">全部类型</option>
          <option value="match">比赛数据</option>
          <option value="intelligence">情报数据</option>
          <option value="prediction">预测数据</option>
          <option value="sp">SP数据</option>
          <option value="user">用户数据</option>
        </select>
        
        <select v-model="filters.status" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已批准</option>
          <option value="rejected">已拒绝</option>
          <option value="published">已发布</option>
        </select>
      </div>

      <div class="actions">
        <button class="action-btn primary" @click="addNewData">
          <span>➕</span> 添加数据
        </button>
        <button class="action-btn secondary" @click="importData">
          <span>📥</span> 导入数据
        </button>
        <button class="action-btn tertiary" @click="exportData">
          <span>📤</span> 导出数据
        </button>
        <button class="action-btn refresh" @click="refreshData">
          <span>🔄</span> 刷新
        </button>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon matches">
          <i class="icon-calendar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">比赛数据</div>
          <div class="stat-value">{{ stats.matchesCount }}</div>
          <div class="stat-change positive">+{{ stats.newMatchesToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon intelligence">
          <i class="icon-brain"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">情报数据</div>
          <div class="stat-value">{{ stats.intelligenceCount }}</div>
          <div class="stat-change positive">+{{ stats.newIntelligenceToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon prediction">
          <i class="icon-chart"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">预测数据</div>
          <div class="stat-value">{{ stats.predictionsCount }}</div>
          <div class="stat-change positive">+{{ stats.newPredictionsToday }} 今日新增</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon sp">
          <i class="icon-line-chart"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">SP数据</div>
          <div class="stat-value">{{ stats.spCount }}</div>
          <div class="stat-change positive">+{{ stats.newSpToday }} 今日新增</div>
        </div>
      </div>
    </div>

    <!-- 数据列表 -->
    <div class="data-section">
      <div class="section-header">
        <h2>📋 数据列表</h2>
        <div class="data-stats">
          <span class="stat-item">显示: {{ filteredData.length }} 条</span>
          <span class="stat-item total">总计: {{ allData.length }} 条</span>
        </div>
      </div>
      
      <div class="data-table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" /></th>
              <th>ID</th>
              <th>数据类型</th>
              <th>标题/描述</th>
              <th>来源</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedData" :key="item.id" :class="{ selected: item.selected }">
              <td><input type="checkbox" v-model="item.selected" /></td>
              <td>{{ item.id }}</td>
              <td>
                <span class="data-type-badge" :class="item.dataType">
                  {{ dataTypeLabels[item.dataType] }}
                </span>
              </td>
              <td>{{ item.title || item.description || 'N/A' }}</td>
              <td>{{ item.source }}</td>
              <td>
                <span class="status-badge" :class="item.status">
                  {{ statusLabels[item.status] }}
                </span>
              </td>
              <td>{{ formatDate(item.createdAt) }}</td>
              <td>
                <button class="action-btn view" @click="viewData(item)">👁️</button>
                <button class="action-btn edit" @click="editData(item)">✏️</button>
                <button class="action-btn delete" @click="deleteData(item)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button 
          class="pagination-btn" 
          @click="prevPage" 
          :disabled="currentPage === 1"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button 
          class="pagination-btn" 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 添加/编辑数据对话框 -->
    <div v-if="showDataModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingData ? '编辑数据' : '添加数据' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>数据类型 *</label>
            <select v-model="currentData.dataType">
              <option value="match">比赛数据</option>
              <option value="intelligence">情报数据</option>
              <option value="prediction">预测数据</option>
              <option value="sp">SP数据</option>
              <option value="user">用户数据</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>标题 *</label>
            <input 
              v-model="currentData.title" 
              type="text" 
              placeholder="输入数据标题"
            />
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="currentData.description" 
              placeholder="输入数据描述"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group" v-if="currentData.dataType === 'match'">
            <label>比赛信息</label>
            <input 
              v-model="currentData.matchInfo" 
              type="text" 
              placeholder="例如：主队 vs 客队，联赛名称"
            />
          </div>
          
          <div class="form-group" v-if="currentData.dataType === 'sp'">
            <label>SP值</label>
            <input 
              v-model.number="currentData.spValue" 
              type="number" 
              step="0.01"
              placeholder="输入SP数值"
            />
          </div>
          
          <div class="form-group">
            <label>数据来源</label>
            <input 
              v-model="currentData.source" 
              type="text" 
              placeholder="输入数据来源"
            />
          </div>
          
          <div class="form-group">
            <label>状态</label>
            <select v-model="currentData.status">
              <option value="pending">待审核</option>
              <option value="approved">已批准</option>
              <option value="rejected">已拒绝</option>
              <option value="published">已发布</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button 
            class="btn primary" 
            @click="saveData"
            :disabled="!isValidData"
          >
            {{ editingData ? '更新' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 数据详情对话框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>数据详情 - {{ selectedData.title || selectedData.description }}</h3>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <div class="detail-label">ID</div>
            <div class="detail-value">{{ selectedData.id }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">数据类型</div>
            <div class="detail-value">
              <span class="data-type-badge" :class="selectedData.dataType">
                {{ dataTypeLabels[selectedData.dataType] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">标题</div>
            <div class="detail-value">{{ selectedData.title || 'N/A' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">描述</div>
            <div class="detail-value">{{ selectedData.description || 'N/A' }}</div>
          </div>
          <div class="detail-row" v-if="selectedData.matchInfo">
            <div class="detail-label">比赛信息</div>
            <div class="detail-value">{{ selectedData.matchInfo }}</div>
          </div>
          <div class="detail-row" v-if="selectedData.spValue">
            <div class="detail-label">SP值</div>
            <div class="detail-value">{{ selectedData.spValue }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">来源</div>
            <div class="detail-value">{{ selectedData.source || 'N/A' }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">状态</div>
            <div class="detail-value">
              <span class="status-badge" :class="selectedData.status">
                {{ statusLabels[selectedData.status] }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <div class="detail-label">创建时间</div>
            <div class="detail-value">{{ formatDate(selectedData.createdAt) }}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">更新时间</div>
            <div class="detail-value">{{ formatDate(selectedData.updatedAt) }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeDetailModal">关闭</button>
          <button class="btn primary" @click="editData(selectedData)">编辑</button>
        </div>
      </div>
    </div>

    <!-- 导入数据对话框 -->
    <div v-if="showImportModal" class="modal-overlay" @click="closeImportModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📥 导入数据</h3>
          <button class="close-btn" @click="closeImportModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>选择文件</label>
            <input 
              type="file" 
              accept=".csv,.xlsx,.xls,.json"
              @change="handleFileUpload"
              ref="fileInputRef"
            />
          </div>
          
          <div class="form-group">
            <label>数据类型</label>
            <select v-model="importDataType">
              <option value="match">比赛数据</option>
              <option value="intelligence">情报数据</option>
              <option value="prediction">预测数据</option>
              <option value="sp">SP数据</option>
              <option value="user">用户数据</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>导入模式</label>
            <div class="radio-group">
              <label>
                <input 
                  type="radio" 
                  v-model="importMode" 
                  value="create"
                />
                创建新数据
              </label>
              <label>
                <input 
                  type="radio" 
                  v-model="importMode" 
                  value="update"
                />
                更新现有数据
              </label>
            </div>
          </div>
          
          <div class="upload-preview" v-if="previewData.length > 0">
            <h4>预览数据 (前5行)</h4>
            <table class="preview-table">
              <thead>
                <tr>
                  <th v-for="(header, index) in previewHeaders" :key="index">{{ header }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIndex) in previewData.slice(0, 5)" :key="rowIndex">
                  <td v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeImportModal">取消</button>
          <button 
            class="btn primary" 
            @click="performImport"
            :disabled="!selectedFile"
          >
            开始导入
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 模拟数据
const allData = ref([
  {
    id: 1,
    dataType: 'match',
    title: '英超：曼城 vs 切尔西',
    description: '2023年12月英超联赛比赛信息',
    matchInfo: '曼城主场对阵切尔西',
    source: '500彩票网',
    status: 'published',
    createdAt: new Date(Date.now() - 86400000),
    updatedAt: new Date(Date.now() - 86400000)
  },
  {
    id: 2,
    dataType: 'intelligence',
    title: '意甲分析：尤文图斯近期状态',
    description: '分析尤文图斯近期比赛表现和战术变化',
    source: '体育情报网',
    status: 'approved',
    createdAt: new Date(Date.now() - 172800000),
    updatedAt: new Date(Date.now() - 86400000)
  },
  {
    id: 3,
    dataType: 'prediction',
    title: '德甲预测：拜仁慕尼黑胜率',
    description: '基于历史数据预测拜仁慕尼黑未来比赛胜率',
    source: 'AI预测系统',
    status: 'pending',
    createdAt: new Date(Date.now() - 3600000),
    updatedAt: new Date(Date.now() - 3600000)
  },
  {
    id: 4,
    dataType: 'sp',
    title: '欧冠：皇马 VS 曼城 SP值',
    description: '皇家马德里对阵曼城的SP数据',
    spValue: 2.45,
    source: 'SP数据源',
    status: 'published',
    createdAt: new Date(Date.now() - 7200000),
    updatedAt: new Date(Date.now() - 3600000)
  },
  {
    id: 5,
    dataType: 'match',
    title: '西甲：巴萨 vs 皇马',
    description: '2023年11月国家德比比赛信息',
    matchInfo: '巴塞罗那主场对阵皇家马德里',
    source: '体育直播网',
    status: 'rejected',
    createdAt: new Date(Date.now() - 259200000),
    updatedAt: new Date(Date.now() - 172800000)
  },
  {
    id: 6,
    dataType: 'intelligence',
    title: '法甲：大巴黎进攻策略分析',
    description: '巴黎圣日耳曼近期进攻战术深度分析',
    source: '足球分析网',
    status: 'pending',
    createdAt: new Date(Date.now() - 1800000),
    updatedAt: new Date(Date.now() - 1800000)
  },
  {
    id: 7,
    dataType: 'prediction',
    title: '英超：利物浦赛季冠军概率',
    description: '利物浦本赛季获得英超冠军的概率预测',
    source: '机器学习模型',
    status: 'approved',
    createdAt: new Date(Date.now() - 14400000),
    updatedAt: new Date(Date.now() - 7200000)
  },
  {
    id: 8,
    dataType: 'sp',
    title: '欧联杯：法兰克福 SP值',
    description: '法兰克福在欧联杯中的SP数据',
    spValue: 1.85,
    source: 'SP数据源',
    status: 'published',
    createdAt: new Date(Date.now() - 21600000),
    updatedAt: new Date(Date.now() - 14400000)
  }
])

// 搜索和筛选
const searchKeyword = ref('')
const filters = ref({
  dataType: '',
  status: ''
})

// 统计数据
const stats = ref({
  matchesCount: 125,
  intelligenceCount: 89,
  predictionsCount: 64,
  spCount: 245,
  newMatchesToday: 5,
  newIntelligenceToday: 3,
  newPredictionsToday: 2,
  newSpToday: 12
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 数据模态框
const showDataModal = ref(false)
const editingData = ref(null)
const currentData = ref({
  id: null,
  dataType: 'match',
  title: '',
  description: '',
  matchInfo: '',
  spValue: null,
  source: '',
  status: 'pending'
})

// 详情模态框
const showDetailModal = ref(false)
const selectedData = ref({})

// 导入模态框
const showImportModal = ref(false)
const importDataType = ref('match')
const importMode = ref('create')
const selectedFile = ref(null)
const previewData = ref([])
const previewHeaders = ref([])
const fileInputRef = ref(null)

// 计算属性
const filteredData = computed(() => {
  let data = [...allData.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(item => 
      item.title.toLowerCase().includes(keyword) ||
      item.description.toLowerCase().includes(keyword) ||
      item.source.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.dataType) {
    data = data.filter(item => item.dataType === filters.value.dataType)
  }
  
  if (filters.value.status) {
    data = data.filter(item => item.status === filters.value.status)
  }
  
  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / pageSize.value)
})

const dataTypeLabels = {
  match: '比赛数据',
  intelligence: '情报数据',
  prediction: '预测数据',
  sp: 'SP数据',
  user: '用户数据'
}

const statusLabels = {
  pending: '待审核',
  approved: '已批准',
  rejected: '已拒绝',
  published: '已发布'
}

const isValidData = computed(() => {
  return currentData.value.title.trim() !== '' && 
         currentData.value.dataType !== ''
})

// 方法
const handleSearch = () => {
  console.log('搜索关键词:', searchKeyword.value)
  currentPage.value = 1
}

const handleFilterChange = () => {
  console.log('筛选条件改变:', filters.value)
  currentPage.value = 1
}

const refreshData = () => {
  console.log('刷新数据列表')
  currentPage.value = 1
}

const addNewData = () => {
  editingData.value = null
  currentData.value = {
    id: null,
    dataType: 'match',
    title: '',
    description: '',
    matchInfo: '',
    spValue: null,
    source: '',
    status: 'pending'
  }
  showDataModal.value = true
}

const editData = (data) => {
  editingData.value = data
  currentData.value = { ...data }
  showDataModal.value = true
}

const closeModal = () => {
  showDataModal.value = false
  editingData.value = null
}

const saveData = () => {
  if (!isValidData.value) return
  
  if (editingData.value) {
    // 更新现有数据
    const index = allData.value.findIndex(d => d.id === editingData.value.id)
    if (index !== -1) {
      allData.value[index] = { ...currentData.value, id: editingData.value.id }
    }
  } else {
    // 添加新数据
    const newId = Math.max(...allData.value.map(d => d.id)) + 1
    allData.value.push({
      ...currentData.value,
      id: newId,
      createdAt: new Date(),
      updatedAt: new Date()
    })
  }
  
  closeModal()
}

const viewData = (data) => {
  selectedData.value = data
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedData.value = {}
}

const deleteData = (data) => {
  if (confirm(`确定要删除 "${data.title}" 吗？`)) {
    const index = allData.value.indexOf(data)
    if (index !== -1) {
      allData.value.splice(index, 1)
    }
  }
}

const toggleSelectAll = () => {
  const isSelected = paginatedData.value.some(item => item.selected)
  paginatedData.value.forEach(item => item.selected = !isSelected)
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const importData = () => {
  showImportModal.value = true
  selectedFile.value = null
  previewData.value = []
  previewHeaders.value = []
}

const closeImportModal = () => {
  showImportModal.value = false
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0]
  
  // 模拟文件预览
  if (selectedFile.value) {
    // 在实际应用中，这里会解析文件内容并显示预览
    previewHeaders.value = ['ID', '标题', '类型', '状态', '创建时间']
    previewData.value = [
      ['1', '测试数据1', '比赛数据', '已发布', '2023-12-01'],
      ['2', '测试数据2', '情报数据', '待审核', '2023-12-02'],
      ['3', '测试数据3', '预测数据', '已批准', '2023-12-03'],
      ['4', '测试数据4', 'SP数据', '已发布', '2023-12-04'],
      ['5', '测试数据5', '比赛数据', '已拒绝', '2023-12-05']
    ]
  }
}

const performImport = () => {
  if (!selectedFile.value) return
  
  alert(`开始导入 ${selectedFile.value.name} 文件`)
  // 在实际应用中，这里会执行实际的导入逻辑
  closeImportModal()
}

const exportData = () => {
  alert('导出数据功能将在后续版本中实现')
  // 在实际应用中，这里会导出当前筛选的数据
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 初始化数据
onMounted(() => {
  console.log('Data Management 页面已加载')
})
</script>

<style scoped>
.data-management-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 工具栏样式 */
.toolbar {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn {
  padding: 10px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-btn:hover {
  background: #2563eb;
}

.filters {
  display: flex;
  gap: 12px;
}

.filters select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn.primary {
  background: #10b981;
  color: white;
}

.action-btn.primary:hover {
  background: #059669;
}

.action-btn.secondary {
  background: #6366f1;
  color: white;
}

.action-btn.secondary:hover {
  background: #4f46e5;
}

.action-btn.tertiary {
  background: #f59e0b;
  color: white;
}

.action-btn.tertiary:hover {
  background: #d97706;
}

.action-btn.refresh {
  background: #94a3b8;
  color: white;
}

.action-btn.refresh:hover {
  background: #64748b;
}

.action-btn.view {
  background: #e5e7eb;
  color: #374151;
  padding: 6px 10px;
}

.action-btn.view:hover {
  background: #d1d5db;
}

.action-btn.edit {
  background: #94a3b8;
  color: white;
  padding: 6px 10px;
}

.action-btn.edit:hover {
  background: #64748b;
}

.action-btn.delete {
  background: #ef4444;
  color: white;
  padding: 6px 10px;
}

.action-btn.delete:hover {
  background: #dc2626;
}

/* 统计卡片样式 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.matches {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.intelligence {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.prediction {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.sp {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.positive {
  color: #059669;
}

/* 数据区域样式 */
.data-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.section-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.data-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #6b7280;
}

.data-table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.data-table tbody tr:hover {
  background-color: #f9fafb;
}

.data-table tbody tr.selected {
  background-color: #e0f2fe;
}

.data-type-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.data-type-badge.match {
  background: #dbeafe;
  color: #1d4ed8;
}

.data-type-badge.intelligence {
  background: #f0f9ff;
  color: #0369a1;
}

.data-type-badge.prediction {
  background: #ecfdf5;
  color: #047857;
}

.data-type-badge.sp {
  background: #fffbeb;
  color: #92400e;
}

.data-type-badge.user {
  background: #f3e8ff;
  color: #7e22ce;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.approved {
  background: #dcfce7;
  color: #166534;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge.published {
  background: #ddd6fe;
  color: #6d28d9;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.2);
}

.large-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #9ca3af;
}

.close-btn:hover {
  color: #6b7280;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1f2937;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.upload-preview {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

.preview-table th,
.preview-table td {
  padding: 8px;
  border: 1px solid #e5e7eb;
  text-align: left;
}

.preview-table th {
  background: #f3f4f6;
  font-weight: 600;
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-label {
  width: 120px;
  font-weight: 600;
  color: #374151;
}

.detail-value {
  flex: 1;
  color: #6b7280;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn.cancel:hover {
  background: #e5e7eb;
}

.btn.primary {
  background: #3b82f6;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn.primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .data-management-container {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .data-table {
    min-width: 600px;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
  
  .modal-content {
    width: 95vw;
  }
  
  .large-modal {
    width: 95vw;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: auto;
    margin-bottom: 4px;
  }
}
</style>