<template>
  <div class="intelligence-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>多模态分析</h2>
      <p class="page-description">整合文本、图像、视频等多种媒体形式的情报分析</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="addMultimodalTask">
        新建分析任务
      </el-button>
      <el-button type="success" :icon="VideoPlay" @click="startAnalysis">
        开始分析
      </el-button>
      <el-button type="warning" :icon="RefreshLeft" @click="refreshData">
        刷新数据
      </el-button>
      <el-button type="info" :icon="Upload" @click="uploadMedia">
        上传媒体
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.textCount }}</div>
              <div class="stats-label">文本情报</div>
            </div>
            <el-icon class="stats-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.imageCount }}</div>
              <div class="stats-label">图像情报</div>
            </div>
            <el-icon class="stats-icon"><Picture /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.videoCount }}</div>
              <div class="stats-label">视频情报</div>
            </div>
            <el-icon class="stats-icon"><VideoCamera /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.integrationScore }}</div>
              <div class="stats-label">融合评分</div>
            </div>
            <el-icon class="stats-icon"><Connection /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- Media Sources Tab -->
      <el-tab-pane label="多媒体源" name="sources">
        <div class="tab-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>多媒体情报源</span>
                <el-button type="primary" size="small" @click="addSource">添加源</el-button>
              </div>
            </template>
            <el-table :data="mediaSources" style="width: 100%" v-loading="loading">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="名称" width="150" />
              <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                  <el-tag :type="getSourceTypeTag(scope.row.type)">
                    {{ scope.row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusTagType(scope.row.status)">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="lastUpdate" label="最后更新" width="180" />
              <el-table-column prop="dataCount" label="数据量" width="100" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="editSource(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteSource(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Analysis Results Tab -->
      <el-tab-pane label="分析结果" name="results">
        <div class="tab-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>多模态融合分析结果</span>
              </div>
            </template>
            <div class="analysis-results">
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="result-content">
                    <h4>综合分析结论</h4>
                    <p>
                      基于多模态数据融合分析，我们发现近期关于XX足球队的情报呈现出明显的积极趋势。
                      文本分析显示正面情绪占比达到72%，图像识别捕捉到球员训练积极性较高，
                      视频分析表明战术配合日趋成熟。综合来看，该球队在未来几场比赛中表现
                      有望超出市场预期。
                    </p>
                    <h4>关键发现</h4>
                    <ul>
                      <li>球员伤病情况好转，主力阵容趋于完整</li>
                      <li>新教练战术体系逐步被队员接受</li>
                      <li>主场优势明显，球迷支持力度增强</li>
                      <li>对手分析显示赛程安排相对有利</li>
                    </ul>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="result-summary">
                    <el-card class="summary-card">
                      <div class="summary-content">
                        <div class="summary-number">{{ fusionConfidence }}%</div>
                        <div class="summary-label">融合置信度</div>
                      </div>
                    </el-card>
                    <el-card class="summary-card">
                      <div class="summary-content">
                        <div class="summary-number">{{ reliabilityScore }}</div>
                        <div class="summary-label">可信度评分</div>
                      </div>
                    </el-card>
                    <el-card class="summary-card">
                      <div class="summary-content">
                        <div class="summary-number">{{ updateFrequency }}</div>
                        <div class="summary-label">更新频率(/天)</div>
                      </div>
                    </el-card>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Media Gallery Tab -->
      <el-tab-pane label="媒体画廊" name="gallery">
        <div class="tab-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>多媒体情报画廊</span>
              </div>
            </template>
            <div class="gallery-container">
              <el-row :gutter="20">
                <el-col :span="6" v-for="item in mediaGallery" :key="item.id">
                  <el-card class="media-card" @click="previewMedia(item)">
                    <div class="media-preview">
                      <img v-if="item.type === 'image'" :src="item.thumbnail" alt="Image Preview" />
                      <div v-else-if="item.type === 'video'" class="video-placeholder">
                        <el-icon><VideoCamera /></el-icon>
                        <span>视频</span>
                      </div>
                      <div v-else class="text-placeholder">
                        <el-icon><Document /></el-icon>
                        <span>文本</span>
                      </div>
                    </div>
                    <div class="media-info">
                      <h4>{{ item.title }}</h4>
                      <p class="media-type">{{ item.type }}</p>
                      <p class="media-date">{{ item.date }}</p>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Media Preview Dialog -->
    <el-dialog v-model="showPreviewDialog" title="媒体预览" width="80%">
      <div v-if="selectedMedia">
        <div v-if="selectedMedia.type === 'image'" class="preview-image">
          <img :src="selectedMedia.url" :alt="selectedMedia.title" style="width: 100%; height: auto;" />
        </div>
        <div v-else-if="selectedMedia.type === 'video'" class="preview-video">
          <video :src="selectedMedia.url" controls style="width: 100%; height: auto;">
            您的浏览器不支持视频播放
          </video>
        </div>
        <div v-else class="preview-text">
          <h4>{{ selectedMedia.title }}</h4>
          <p>{{ selectedMedia.content }}</p>
        </div>
        <div class="preview-details">
          <p><strong>来源：</strong>{{ selectedMedia.source }}</p>
          <p><strong>分析结果：</strong>{{ selectedMedia.analysisResult }}</p>
          <p><strong>采集时间：</strong>{{ selectedMedia.date }}</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPreviewDialog = false">关闭</el-button>
          <el-button type="primary" @click="showPreviewDialog = false">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, VideoPlay, RefreshLeft, Upload, Document, Picture, VideoCamera, Connection 
} from '@element-plus/icons-vue'

// Tab control
const activeTab = ref('sources')

// Stats
const stats = reactive({
  textCount: 1240,
  imageCount: 890,
  videoCount: 245,
  integrationScore: 8.7
})

// Loading state
const loading = ref(false)

// Analysis metrics
const fusionConfidence = ref(89)
const reliabilityScore = ref(9.2)
const updateFrequency = ref(12)

const buildInlinePlaceholder = (width, height, text) =>
  `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <rect width="100%" height="100%" fill="#eef1f6"/>
      <rect x="8" y="8" width="${width - 16}" height="${height - 16}" rx="8" ry="8" fill="#dfe6ef"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-size="16" font-family="Arial,sans-serif">${text}</text>
    </svg>`
  )}`

const imageThumbPlaceholder = buildInlinePlaceholder(150, 150, 'IMAGE')
const imagePreviewPlaceholder = buildInlinePlaceholder(600, 400, 'PREVIEW')

// Media sources data
const mediaSources = ref([
  { id: 1, name: '社交媒体监测', type: '文本', status: '活跃', lastUpdate: '2024-01-15 10:30', dataCount: 420 },
  { id: 2, name: '官方视频源', type: '视频', status: '活跃', lastUpdate: '2024-01-15 09:45', dataCount: 180 },
  { id: 3, name: '新闻图片库', type: '图像', status: '维护', lastUpdate: '2024-01-15 08:20', dataCount: 320 },
  { id: 4, name: '专家评论聚合', type: '文本', status: '活跃', lastUpdate: '2024-01-15 07:15', dataCount: 280 },
  { id: 5, name: '球迷论坛', type: '文本', status: '活跃', lastUpdate: '2024-01-15 06:30', dataCount: 560 }
])

// Media gallery data
const mediaGallery = ref([
  { id: 1, title: '训练场照片', type: 'image', thumbnail: imageThumbPlaceholder, date: '2024-01-15', url: imagePreviewPlaceholder, source: '官方媒体', content: '球队在训练场上的表现', analysisResult: '积极情绪' },
  { id: 2, title: '赛后采访', type: 'video', date: '2024-01-14', url: '#', source: '体育频道', content: '主教练赛后采访', analysisResult: '信心满满' },
  { id: 3, title: '专家分析', type: '文本', date: '2024-01-14', url: '#', source: '体育报纸', content: '对下周比赛的专业分析文章', analysisResult: '看好主队' },
  { id: 4, title: '球迷活动', type: 'image', thumbnail: imageThumbPlaceholder, date: '2024-01-13', url: imagePreviewPlaceholder, source: '社交媒体', content: '球迷助威活动', analysisResult: '热情高涨' }
])

// Selected media for preview
const selectedMedia = ref(null)
const showPreviewDialog = ref(false)

// Methods
const addMultimodalTask = () => {
  ElMessage.success('新建多模态分析任务')
}

const startAnalysis = () => {
  ElMessage.success('开始多模态融合分析...')
  // Simulate API call
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('分析完成！')
  }, 1500)
}

const refreshData = () => {
  ElMessage.info('刷新数据中...')
}

const uploadMedia = () => {
  ElMessage.info('上传媒体文件...')
}

const getSourceTypeTag = (type) => {
  if (type === '文本') return 'primary'
  if (type === '图像') return 'success'
  if (type === '视频') return 'warning'
  return 'info'
}

const getStatusTagType = (status) => {
  if (status === '活跃') return 'success'
  if (status === '维护') return 'warning'
  if (status === '停用') return 'danger'
  return 'info'
}

const addSource = () => {
  ElMessage.success('添加新情报源')
}

const editSource = (item) => {
  ElMessage.info(`编辑情报源: ${item.name}`)
}

const deleteSource = (item) => {
  ElMessageBox.confirm(
    `确定要删除情报源 "${item.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    mediaSources.value = mediaSources.value.filter(i => i.id !== item.id)
    ElMessage.success('删除成功')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

const previewMedia = (item) => {
  selectedMedia.value = item
  showPreviewDialog.value = true
}

onMounted(() => {
  console.log('Multimodal Analysis module loaded')
})
</script>

<style scoped>
.intelligence-management-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  position: relative;
  overflow: hidden;
}

.stats-content {
  position: relative;
  z-index: 2;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 48px;
  color: #409eff;
  opacity: 0.1;
  z-index: 1;
}

.management-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 20px;
}

.analysis-results {
  padding: 20px 0;
}

.result-content h4 {
  margin: 16px 0 8px;
  color: #303133;
}

.result-content ul {
  padding-left: 20px;
}

.result-content li {
  margin: 8px 0;
  color: #606266;
}

.result-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-card {
  text-align: center;
}

.summary-content {
  padding: 10px 0;
}

.summary-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
}

.gallery-container {
  padding: 10px 0;
}

.media-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.media-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.media-preview {
  text-align: center;
  padding: 10px;
}

.media-preview img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}

.video-placeholder, .text-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
}

.video-placeholder el-icon, .text-placeholder el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.media-info {
  padding: 10px 0 0;
}

.media-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.media-type {
  font-size: 12px;
  color: #909399;
  margin: 0 0 4px;
}

.media-date {
  font-size: 12px;
  color: #c0c4cc;
  margin: 0;
}

.preview-image {
  text-align: center;
  margin-bottom: 20px;
}

.preview-video {
  text-align: center;
  margin-bottom: 20px;
}

.preview-details {
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

.preview-details p {
  margin: 8px 0;
  line-height: 1.5;
}
</style>
