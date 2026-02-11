<template>
  <div class="intelligence-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>图谱管理</h2>
      <p class="page-description">管理知识图谱和关联关系网络</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="showCreateGraphDialog = true">
        新建图谱
      </el-button>
      <el-button type="success" :icon="VideoPlay" @click="startAnalysis">
        开始分析
      </el-button>
      <el-button type="warning" :icon="RefreshLeft" @click="refreshGraph">
        刷新图谱
      </el-button>
      <el-button type="info" :icon="Share" @click="exportGraph">
        导出图谱
      </el-button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalNodes }}</div>
              <div class="stats-label">图谱节点</div>
            </div>
            <el-icon class="stats-icon"><Share /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalEdges }}</div>
              <div class="stats-label">关联关系</div>
            </div>
            <el-icon class="stats-icon"><Connection /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.graphTypes }}</div>
              <div class="stats-label">图谱类型</div>
            </div>
            <el-icon class="stats-icon"><CollectionTag /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.insights }}</div>
              <div class="stats-label">洞察发现</div>
            </div>
            <el-icon class="stats-icon"><View /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Main Content Tabs -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- Graph Visualization Tab -->
      <el-tab-pane label="图谱可视化" name="visualization">
        <div class="tab-content">
          <!-- Graph Controls -->
          <div class="graph-controls">
            <el-row :gutter="16" align="middle">
              <el-col :span="6">
                <el-select v-model="selectedGraph" placeholder="选择图谱" @change="loadGraph">
                  <el-option 
                    v-for="graph in graphList" 
                    :key="graph.id"
                    :label="graph.name" 
                    :value="graph.id"
                  />
                </el-select>
              </el-col>
              <el-col :span="12">
                <el-button-group>
                  <el-button 
                    v-for="layout in layouts" 
                    :key="layout.key"
                    :type="selectedLayout === layout.key ? 'primary' : ''"
                    @click="changeLayout(layout.key)"
                  >
                    {{ layout.label }}
                  </el-button>
                </el-button-group>
              </el-col>
              <el-col :span="6">
                <div class="graph-actions">
                  <el-button size="small" @click="zoomIn">放大</el-button>
                  <el-button size="small" @click="zoomOut">缩小</el-button>
                  <el-button size="small" @click="fitView">适应</el-button>
                  <el-button size="small" type="primary" @click="centerView">居中</el-button>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- Graph Canvas -->
          <el-card class="graph-canvas-card">
            <div class="graph-canvas-container">
              <div ref="graphCanvas" class="graph-canvas" style="height: 600px;"></div>
              
              <!-- Node Details Panel -->
              <div v-if="selectedNode" class="node-details-panel">
                <div class="panel-header">
                  <h4>{{ selectedNode.label }}</h4>
                  <el-button size="small" icon="Close" @click="selectedNode = null" circle />
                </div>
                <div class="panel-content">
                  <div class="node-property">
                    <span class="property-label">类型:</span>
                    <el-tag :type="getNodeTypeColor(selectedNode.type)" size="small">
                      {{ selectedNode.type }}
                    </el-tag>
                  </div>
                  <div class="node-property">
                    <span class="property-label">属性:</span>
                    <div class="node-attributes">
                      <div v-for="(value, key) in selectedNode.attributes" :key="key" class="attribute-item">
                        <span class="attr-key">{{ key }}:</span>
                        <span class="attr-value">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="node-relations">
                    <h5>关联关系</h5>
                    <div class="relation-list">
                      <div v-for="relation in selectedNode.relations" :key="relation.id" class="relation-item">
                        <el-link type="primary" @click="focusOnNode(relation.target)">
                          {{ relation.target }}
                        </el-link>
                        <el-tag size="small">{{ relation.type }}</el-tag>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Graph Filters -->
          <el-card class="graph-filters-card">
            <template #header>图谱过滤器</template>
            <div class="filter-section">
              <div class="filter-group">
                <label>节点类型:</label>
                <el-checkbox-group v-model="visibleNodeTypes">
                  <el-checkbox v-for="type in nodeTypes" :key="type" :value="type">
                    {{ type }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
              <div class="filter-group">
                <label>关系类型:</label>
                <el-checkbox-group v-model="visibleEdgeTypes">
                  <el-checkbox v-for="type in edgeTypes" :key="type" :value="type">
                    {{ type }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
              <div class="filter-group">
                <label>搜索节点:</label>
                <el-input 
                  v-model="nodeSearchQuery" 
                  placeholder="输入节点名称搜索"
                  clearable
                  @input="searchNodes"
                >
                  <template #append>
                    <el-button :icon="Search" @click="searchNodes" />
                  </template>
                </el-input>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Graph Analytics Tab -->
      <el-tab-pane label="图谱分析" name="analytics">
        <div class="tab-content">
          <!-- Analytics Overview -->
          <el-row :gutter="20" class="analytics-overview">
            <el-col :span="8">
              <el-card class="analytics-card">
                <template #header>中心性分析</template>
                <div ref="centralityChart" style="height: 250px;"></div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="analytics-card">
                <template #header>社区发现</template>
                <div ref="communityChart" style="height: 250px;"></div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="analytics-card">
                <template #header>路径分析</template>
                <div ref="pathChart" style="height: 250px;"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Network Metrics -->
          <el-row :gutter="20" class="network-metrics">
            <el-col :span="12">
              <el-card>
                <template #header>网络指标</template>
                <div class="metrics-grid">
                  <div class="metric-item">
                    <span class="metric-label">平均度:</span>
                    <span class="metric-value">{{ networkMetrics.avgDegree }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">聚类系数:</span>
                    <span class="metric-value">{{ networkMetrics.clusteringCoefficient }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">直径:</span>
                    <span class="metric-value">{{ networkMetrics.diameter }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">密度:</span>
                    <span class="metric-value">{{ networkMetrics.density }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>重要节点</template>
                <el-table :data="importantNodes" style="width: 100%">
                  <el-table-column prop="rank" label="排名" width="60" />
                  <el-table-column prop="node" label="节点" min-width="120" />
                  <el-table-column prop="centrality" label="中心性" width="100">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.centrality" :stroke-width="6" />
                    </template>
                  </el-table-column>
                  <el-table-column prop="type" label="类型" width="100">
                    <template #default="scope">
                      <el-tag :type="getNodeTypeColor(scope.row.type)" size="small">
                        {{ scope.row.type }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Knowledge Base Tab -->
      <el-tab-pane label="知识库" name="knowledge">
        <div class="tab-content">
          <!-- Knowledge Categories -->
          <div class="knowledge-categories">
            <el-collapse v-model="activeKnowledgeCategory">
              <el-collapse-item 
                v-for="category in knowledgeCategories" 
                :key="category.key"
                :title="category.label" 
                :name="category.key"
              >
                <div class="knowledge-grid">
                  <el-card 
                    v-for="item in category.items" 
                    :key="item.id"
                    class="knowledge-card"
                    @click="viewKnowledgeItem(item)"
                  >
                    <template #header>
                      <div class="knowledge-header">
                        <span class="knowledge-title">{{ item.title }}</span>
                        <el-tag size="small" :type="getKnowledgeTypeColor(item.type)">
                          {{ item.type }}
                        </el-tag>
                      </div>
                    </template>
                    <p class="knowledge-desc">{{ item.description }}</p>
                    <div class="knowledge-meta">
                      <span class="meta-item">节点数: {{ item.nodeCount }}</span>
                      <span class="meta-item">更新: {{ item.updatedAt }}</span>
                    </div>
                  </el-card>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>

      <!-- Graph Builder Tab -->
      <el-tab-pane label="图谱构建" name="builder">
        <div class="tab-content">
          <!-- Builder Tools -->
          <el-row :gutter="20" class="builder-tools">
            <el-col :span="6">
              <el-card class="tools-card">
                <template #header>构建工具</template>
                <div class="tool-buttons">
                  <el-button type="primary" :icon="Plus" @click="addNodeMode = true" :class="{ active: addNodeMode }">
                    添加节点
                  </el-button>
                  <el-button type="success" :icon="Link" @click="addEdgeMode = true" :class="{ active: addEdgeMode }">
                    添加关系
                  </el-button>
                  <el-button type="warning" :icon="Edit" @click="editMode = true" :class="{ active: editMode }">
                    编辑模式
                  </el-button>
                  <el-button type="danger" :icon="Delete" @click="deleteMode = true" :class="{ active: deleteMode }">
                    删除模式
                  </el-button>
                </div>
              </el-card>
            </el-col>
            <el-col :span="18">
              <el-card class="builder-canvas-card">
                <template #header>图谱构建画布</template>
                <div class="builder-canvas" style="height: 500px; background: #f8f9fa; border: 2px dashed #ddd; display: flex; align-items: center; justify-content: center;">
                  <div class="canvas-placeholder">
                    <el-icon size="48" color="#ccc"><Share /></el-icon>
                    <p>图谱构建区域</p>
                    <p style="font-size: 12px; color: #999;">选择左侧工具开始构建图谱</p>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- Entity Types -->
          <el-card class="entity-types-card">
            <template #header>实体类型定义</template>
            <el-table :data="entityTypes" style="width: 100%">
              <el-table-column prop="name" label="实体名称" width="150" />
              <el-table-column prop="icon" label="图标" width="80">
                <template #default="scope">
                  <el-icon><component :is="scope.row.icon" /></el-icon>
                </template>
              </el-table-column>
              <el-table-column prop="color" label="颜色" width="100">
                <template #default="scope">
                  <div class="color-preview" :style="{ backgroundColor: scope.row.color }"></div>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" min-width="200" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="editEntityType(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteEntityType(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Graph Dialog -->
    <el-dialog 
      v-model="showCreateGraphDialog" 
      :title="isEditing ? '编辑图谱' : '新建图谱'"
      width="600px"
    >
      <el-form :model="graphForm" :rules="graphFormRules" ref="graphFormRef" label-width="100px">
        <el-form-item label="图谱名称" prop="name">
          <el-input v-model="graphForm.name" placeholder="请输入图谱名称" />
        </el-form-item>
        <el-form-item label="图谱类型" prop="type">
          <el-select v-model="graphForm.type" placeholder="请选择图谱类型">
            <el-option label="比赛关系图" value="match-relation" />
            <el-option label="球队关系图" value="team-relation" />
            <el-option label="球员关系图" value="player-relation" />
            <el-option label="赔率关联图" value="odds-correlation" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="graphForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入图谱描述"
          />
        </el-form-item>
        <el-form-item label="数据源" prop="dataSource">
          <el-select v-model="graphForm.dataSource" placeholder="请选择数据源">
            <el-option label="MySQL数据库" value="mysql" />
            <el-option label="MongoDB" value="mongodb" />
            <el-option label="API接口" value="api" />
            <el-option label="文件导入" value="file" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置信息" prop="config">
          <el-input 
            v-model="graphForm.config" 
            type="textarea" 
            :rows="4"
            placeholder="请输入JSON格式的图谱配置"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateGraphDialog = false">取消</el-button>
          <el-button type="primary" @click="saveGraphConfig">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, VideoPlay, RefreshLeft, Share, Connection, CollectionTag, View,
  Search, Link, Edit, Delete, Close, ZoomIn, ZoomOut 
} from '@element-plus/icons-vue'

// Reactive data
const activeTab = ref('visualization')
const activeKnowledgeCategory = ref(['entities'])
const selectedGraph = ref('')
const selectedLayout = ref('force')
const selectedNode = ref(null)
const loading = ref(false)
const showCreateGraphDialog = ref(false)
const isEditing = ref(false)

// Mode flags
const addNodeMode = ref(false)
const addEdgeMode = ref(false)
const editMode = ref(false)
const deleteMode = ref(false)

// Stats data
const stats = reactive({
  totalNodes: 2540,
  totalEdges: 5680,
  graphTypes: 4,
  insights: 127
})

// Graph list
const graphList = ref([
  { id: 1, name: '比赛关系图谱', type: 'match-relation', nodes: 1200, edges: 2800 },
  { id: 2, name: '球队关系图谱', type: 'team-relation', nodes: 850, edges: 2100 },
  { id: 3, name: '球员关系图谱', type: 'player-relation', nodes: 490, edges: 780 }
])

// Layout options
const layouts = ref([
  { key: 'force', label: '力导向' },
  { key: 'circular', label: '环形' },
  { key: 'grid', label: '网格' },
  { key: 'hierarchical', label: '层次' }
])

// Node types and filters
const nodeTypes = ref(['球队', '球员', '比赛', '联赛', '教练', '场馆'])
const edgeTypes = ref(['参赛', '执教', '隶属', '对阵', '主办', '转会'])
const visibleNodeTypes = ref(nodeTypes.value)
const visibleEdgeTypes = ref(edgeTypes.value)
const nodeSearchQuery = ref('')

// Graph form
const graphForm = reactive({
  name: '',
  type: '',
  description: '',
  dataSource: '',
  config: ''
})

const graphFormRules = {
  name: [{ required: true, message: '请输入图谱名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择图谱类型', trigger: 'change' }]
}

// Knowledge categories
const knowledgeCategories = ref([
  {
    key: 'entities',
    label: '实体知识',
    items: [
      { id: 1, title: '球队实体', type: '基础', description: '包含所有球队相关信息和属性', nodeCount: 320, updatedAt: '2024-01-20' },
      { id: 2, title: '球员实体', type: '基础', description: '球员个人信息、技能评级等', nodeCount: 2150, updatedAt: '2024-01-22' }
    ]
  },
  {
    key: 'relations',
    label: '关系知识',
    items: [
      { id: 3, title: '比赛关系', type: '关联', description: '比赛参与者和结果关系', nodeCount: 890, updatedAt: '2024-01-21' },
      { id: 4, title: '转会关系', type: '动态', description: '球员转会历史和合同关系', nodeCount: 456, updatedAt: '2024-01-19' }
    ]
  }
])

// Entity types
const entityTypes = ref([
  { name: '球队', icon: 'OfficeBuilding', color: '#409eff' },
  { name: '球员', icon: 'User', color: '#67c23a' },
  { name: '比赛', icon: 'Trophy', color: '#e6a23c' },
  { name: '联赛', icon: 'Collection', color: '#f56c6c' },
  { name: '教练', icon: 'Avatar', color: '#909399' },
  { name: '场馆', icon: 'House', color: '#c069af' }
])

// Network metrics
const networkMetrics = reactive({
  avgDegree: 4.47,
  clusteringCoefficient: 0.68,
  diameter: 8,
  density: 0.0021
})

// Important nodes
const importantNodes = ref([
  { rank: 1, node: '皇家马德里', centrality: 95, type: '球队' },
  { rank: 2, node: '梅西', centrality: 92, type: '球员' },
  { rank: 3, node: '欧冠联赛', centrality: 88, type: '联赛' },
  { rank: 4, node: '巴塞罗那', centrality: 85, type: '球队' },
  { rank: 5, node: '英超联赛', centrality: 82, type: '联赛' }
])

// Mock selected node data
const mockSelectedNode = {
  id: 1,
  label: '皇家马德里',
  type: '球队',
  attributes: {
    '成立年份': '1902',
    '主场': '伯纳乌球场',
    '联赛': '西甲',
    '市值': '€3.2B'
  },
  relations: [
    { id: 1, target: '巴塞罗那', type: '对阵' },
    { id: 2, target: '本泽马', type: '拥有' },
    { id: 3, target: '欧冠联赛', type: '参加' }
  ]
}

// Methods
const getNodeTypeColor = (type) => {
  const colors = { '球队': 'primary', '球员': 'success', '比赛': 'warning', '联赛': 'danger', '教练': 'info', '场馆': 'default' }
  return colors[type] || 'info'
}

const getKnowledgeTypeColor = (type) => {
  const colors = { '基础': 'primary', '关联': 'success', '动态': 'warning' }
  return colors[type] || 'info'
}

const loadGraph = () => {
  console.log('Loading graph:', selectedGraph.value)
  ElMessage.info('加载图谱数据')
}

const changeLayout = (layout) => {
  selectedLayout.value = layout
  console.log('Changing layout to:', layout)
}

const zoomIn = () => {
  console.log('Zoom in')
}

const zoomOut = () => {
  console.log('Zoom out')
}

const fitView = () => {
  console.log('Fit view')
}

const centerView = () => {
  console.log('Center view')
}

const focusOnNode = (nodeId) => {
  console.log('Focus on node:', nodeId)
}

const searchNodes = () => {
  if (nodeSearchQuery.value) {
    console.log('Searching nodes:', nodeSearchQuery.value)
  }
}

const startAnalysis = () => {
  ElMessage.info('启动图谱分析')
}

const refreshGraph = () => {
  ElMessage.success('图谱刷新完成')
}

const exportGraph = () => {
  ElMessage.info('导出图谱数据')
}

const viewKnowledgeItem = (item) => {
  ElMessage.info(`查看知识项: ${item.title}`)
}

const editEntityType = (entity) => {
  ElMessage.info(`编辑实体类型: ${entity.name}`)
}

const deleteEntityType = (entity) => {
  ElMessageBox.confirm(`确定要删除实体类型"${entity.name}"吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  })
}

const saveGraphConfig = () => {
  ElMessage.success(isEditing.value ? '图谱更新成功' : '图谱创建成功')
  showCreateGraphDialog.value = false
  resetGraphForm()
}

const resetGraphForm = () => {
  Object.assign(graphForm, {
    name: '',
    type: '',
    description: '',
    dataSource: '',
    config: ''
  })
  isEditing.value = false
}

// Event handlers for mode switching
const handleModeChange = (mode) => {
  addNodeMode.value = false
  addEdgeMode.value = false
  editMode.value = false
  deleteMode.value = false
  if (mode) {
    mode.value = true
  }
}

onMounted(() => {
  console.log('Graph Management mounted')
  // Set default selected graph
  if (graphList.value.length > 0) {
    selectedGraph.value = graphList.value[0].id
  }
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

.graph-controls {
  margin-bottom: 20px;
}

.graph-actions {
  display: flex;
  gap: 8px;
}

.graph-canvas-card {
  margin-bottom: 20px;
}

.graph-canvas-container {
  position: relative;
}

.graph-canvas {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.node-details-panel {
  position: absolute;
  right: 20px;
  top: 20px;
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.panel-header h4 {
  margin: 0;
  color: #303133;
}

.panel-content {
  padding: 16px;
}

.node-property {
  margin-bottom: 16px;
}

.property-label {
  font-weight: bold;
  color: #606266;
  display: block;
  margin-bottom: 8px;
}

.node-attributes {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
}

.attribute-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 12px;
}

.attr-key {
  color: #909399;
}

.attr-value {
  color: #303133;
  font-weight: bold;
}

.node-relations h5 {
  margin: 0 0 12px 0;
  color: #303133;
}

.relation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.relation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.graph-filters-card {
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
}

.analytics-overview {
  margin-bottom: 20px;
}

.analytics-card {
  height: 350px;
}

.network-metrics {
  margin-bottom: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px 0;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  color: #909399;
}

.metric-value {
  font-weight: bold;
  color: #303133;
}

.knowledge-categories {
  margin-top: 16px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.knowledge-card {
  cursor: pointer;
  transition: all 0.3s;
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.knowledge-title {
  font-weight: bold;
  color: #303133;
}

.knowledge-desc {
  color: #606266;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.knowledge-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.builder-tools {
  margin-bottom: 20px;
}

.tools-card {
  height: fit-content;
}

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-buttons .el-button.active {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.builder-canvas-card {
  margin-bottom: 20px;
}

.canvas-placeholder {
  text-align: center;
  color: #999;
}

.canvas-placeholder p {
  margin: 8px 0;
}

.entity-types-card {
  margin-top: 20px;
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.builder-tools {
  margin-bottom: 20px;
}

.tools-card {
  height: fit-content;
}

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-buttons .el-button.active {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.builder-canvas-card {
  margin-bottom: 20px;
}

.canvas-placeholder {
  text-align: center;
  color: #999;
}

.canvas-placeholder p {
  margin: 8px 0;
}

.entity-types-card {
  margin-top: 20px;
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
}
</style>