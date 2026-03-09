<template>
  <div class="agent-workflow-visualization">
    <div class="workflow-header">
      <h3>{{ title }}</h3>
      <div class="workflow-actions">
        <el-button size="small" @click="zoomIn">
          <i class="el-icon-zoom-in"></i>
        </el-button>
        <el-button size="small" @click="zoomOut">
          <i class="el-icon-zoom-out"></i>
        </el-button>
        <el-button size="small" @click="fitToView">
          <i class="el-icon-c-scale-to-original"></i>
        </el-button>
        <el-button size="small" @click="toggleLayout">
          <i class="el-icon-s-operation"></i>
          {{ layout === 'horizontal' ? '垂直布局' : '水平布局' }}
        </el-button>
        <el-select v-model="viewMode" size="small" style="width: 120px;">
          <el-option label="完整视图" value="full" />
          <el-option label="简化视图" value="simplified" />
          <el-option label="状态视图" value="status" />
        </el-select>
      </div>
    </div>

    <div class="workflow-container" ref="container">
      <svg
        ref="svg"
        :width="svgWidth"
        :height="svgHeight"
        class="workflow-svg"
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @wheel="onWheel"
      >
        <!-- 定义箭头标记 -->
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
          </marker>
          <marker
            id="arrowhead-success"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#67c23a" />
          </marker>
          <marker
            id="arrowhead-error"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#f56c6c" />
          </marker>
          <marker
            id="arrowhead-warning"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="#e6a23c" />
          </marker>
        </defs>

        <!-- 背景网格 -->
        <g v-if="showGrid">
          <pattern
            id="gridPattern"
            width="50"
            height="50"
            patternUnits="userSpaceOnUse"
          >
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e0e0e0" stroke-width="1" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#gridPattern)" />
        </g>

        <!-- 连接线 -->
        <g class="connections">
          <path
            v-for="(edge, index) in edges"
            :key="`edge-${index}`"
            :d="calculateEdgePath(edge)"
            :stroke="getEdgeColor(edge)"
            :stroke-width="getEdgeWidth(edge)"
            fill="none"
            :marker-end="getEdgeMarker(edge)"
            class="connection-line"
            @click="onEdgeClick(edge)"
          />
        </g>

        <!-- 工作流节点 -->
        <g class="nodes">
          <g
            v-for="(node, index) in nodes"
            :key="`node-${index}`"
            :transform="`translate(${node.x}, ${node.y})`"
            @mousedown="onNodeMouseDown(node, $event)"
            @click="onNodeClick(node)"
            @dblclick="onNodeDoubleClick(node)"
            class="workflow-node"
          >
            <!-- 节点主体 -->
            <rect
              :width="node.width"
              :height="node.height"
              :rx="8"
              :ry="8"
              :fill="getNodeFillColor(node)"
              :stroke="getNodeBorderColor(node)"
              stroke-width="2"
              class="node-body"
            />

            <!-- 节点图标 -->
            <text
              :x="node.width / 2"
              :y="25"
              text-anchor="middle"
              class="node-icon"
              v-html="getNodeIcon(node)"
            />

            <!-- 节点标题 -->
            <text
              :x="node.width / 2"
              :y="50"
              text-anchor="middle"
              class="node-title"
              font-weight="bold"
            >
              {{ node.name }}
            </text>

            <!-- 节点状态 -->
            <text
              v-if="node.status"
              :x="node.width / 2"
              :y="node.height - 15"
              text-anchor="middle"
              class="node-status"
              :fill="getStatusColor(node.status)"
            >
              {{ getStatusText(node.status) }}
            </text>

            <!-- 执行时间 -->
            <text
              v-if="node.executionTime"
              :x="node.width / 2"
              :y="node.height - 5"
              text-anchor="middle"
              class="node-time"
              font-size="10"
              fill="#666"
            >
              {{ formatTime(node.executionTime) }}
            </text>

            <!-- 选中状态指示器 -->
            <rect
              v-if="node.selected"
              :width="node.width + 8"
              :height="node.height + 8"
              :rx="12"
              :ry="12"
              :x="-4"
              :y="-4"
              fill="none"
              stroke="#409eff"
              stroke-width="2"
              stroke-dasharray="5,5"
              class="selection-indicator"
            />
          </g>
        </g>

        <!-- 当前执行的节点高亮 -->
        <g v-if="activeNode">
          <circle
            :cx="activeNode.x + activeNode.width / 2"
            :cy="activeNode.y + activeNode.height / 2"
            :r="Math.max(activeNode.width, activeNode.height) / 2 + 15"
            fill="none"
            stroke="#409eff"
            stroke-width="2"
            stroke-dasharray="5,5"
            opacity="0.5"
            class="active-node-highlight"
          />
        </g>

        <!-- 节点连接点 -->
        <g class="connection-points">
          <circle
            v-for="(point, index) in connectionPoints"
            :key="`point-${index}`"
            :cx="point.x"
            :cy="point.y"
            r="4"
            fill="#fff"
            stroke="#409eff"
            stroke-width="2"
            class="connection-point"
            @mousedown="onConnectionPointMouseDown(point, $event)"
          />
        </g>
      </svg>
    </div>

    <!-- 节点详情面板 -->
    <el-drawer
      v-model="showNodeDetail"
      :title="selectedNode ? `${selectedNode.name} - 详情` : '节点详情'"
      size="400px"
      direction="rtl"
    >
      <div v-if="selectedNode" class="node-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="节点ID">{{ selectedNode.id }}</el-descriptions-item>
          <el-descriptions-item label="节点名称">{{ selectedNode.name }}</el-descriptions-item>
          <el-descriptions-item label="节点类型">
            <el-tag :type="getNodeTypeTag(selectedNode.type)">
              {{ selectedNode.type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(selectedNode.status)">
              {{ selectedNode.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatTime(selectedNode.executionTime) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(selectedNode.startTime) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDateTime(selectedNode.endTime) }}
          </el-descriptions-item>
          <el-descriptions-item label="输入参数">
            <pre class="config-pre">{{ JSON.stringify(selectedNode.input, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="输出结果">
            <pre class="config-pre">{{ JSON.stringify(selectedNode.output, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>

        <div class="node-actions" style="margin-top: 20px;">
          <el-button type="primary" @click="executeNode(selectedNode)" v-if="canExecuteNode(selectedNode)">
            执行节点
          </el-button>
          <el-button @click="editNode(selectedNode)">编辑配置</el-button>
          <el-button type="danger" @click="removeNode(selectedNode)">移除节点</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 工作流控制面板 -->
    <el-card class="workflow-control-panel" shadow="never">
      <template #header>
        <div class="panel-header">
          <span>工作流控制</span>
          <div class="panel-actions">
            <el-button size="small" type="primary" @click="executeWorkflow" :loading="executing">
              {{ executing ? '执行中...' : '执行工作流' }}
            </el-button>
            <el-button size="small" @click="resetWorkflow">重置</el-button>
            <el-button size="small" @click="saveWorkflow">保存</el-button>
          </div>
        </div>
      </template>

      <div class="workflow-info">
        <div class="info-item">
          <span class="info-label">节点总数:</span>
          <span class="info-value">{{ nodes.length }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">连接数:</span>
          <span class="info-value">{{ edges.length }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">完成节点:</span>
          <span class="info-value">{{ completedNodes }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">执行进度:</span>
          <span class="info-value">{{ executionProgress }}%</span>
        </div>
      </div>

      <el-progress :percentage="executionProgress" :stroke-width="10" />

      <div class="workflow-stats" style="margin-top: 15px;">
        <el-tag v-for="stat in workflowStats" :key="stat.label" :type="stat.type">
          {{ stat.label }}: {{ stat.value }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 组件属性
const props = defineProps({
  workflowData: {
    type: Object,
    default: () => ({
      nodes: [],
      edges: [],
      metadata: {}
    })
  },
  title: {
    type: String,
    default: '智能体工作流'
  },
  width: {
    type: Number,
    default: 800
  },
  height: {
    type: Number,
    default: 600
  },
  interactive: {
    type: Boolean,
    default: true
  },
  showGrid: {
    type: Boolean,
    default: true
  }
})

// 响应式数据
const svgWidth = ref(props.width)
const svgHeight = ref(props.height)
const viewMode = ref('full')
const layout = ref('horizontal') // 'horizontal' | 'vertical'
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const selectedNode = ref(null)
const showNodeDetail = ref(false)
const activeNode = ref(null)
const executing = ref(false)

// 工作流数据
const nodes = ref([])
const edges = ref([])
const connectionPoints = ref([])

// 计算属性
const completedNodes = computed(() => {
  return nodes.value.filter(node => node.status === 'completed').length
})

const executionProgress = computed(() => {
  if (nodes.value.length === 0) return 0
  return Math.round((completedNodes.value / nodes.value.length) * 100)
})

const workflowStats = computed(() => [
  { label: '等待', value: nodes.value.filter(n => n.status === 'pending').length, type: 'info' },
  { label: '运行中', value: nodes.value.filter(n => n.status === 'running').length, type: 'primary' },
  { label: '成功', value: nodes.value.filter(n => n.status === 'completed').length, type: 'success' },
  { label: '失败', value: nodes.value.filter(n => n.status === 'error').length, type: 'danger' }
])

// 节点类型图标映射
const nodeIcons = {
  'input': '🔢',
  'output': '📤',
  'process': '⚙️',
  'decision': '🤔',
  'api': '🌐',
  'database': '🗄️',
  'llm': '🤖',
  'crawler': '🕷️',
  'analysis': '📊',
  'prediction': '🔮',
  'alert': '🚨',
  'default': '📄'
}

// 状态颜色映射
const statusColors = {
  'pending': '#909399',
  'running': '#409eff',
  'completed': '#67c23a',
  'error': '#f56c6c',
  'warning': '#e6a23c'
}

// 节点类型颜色映射
const nodeTypeColors = {
  'input': '#e6f7ff',
  'output': '#f6ffed',
  'process': '#fff7e6',
  'decision': '#f0f5ff',
  'api': '#f9f0ff',
  'database': '#e6fffb',
  'llm': '#fff0f6',
  'crawler': '#f0fff3',
  'analysis': '#fcf8e3',
  'prediction': '#e8f4fd',
  'alert': '#fff2e8',
  'default': '#fafafa'
}

// 节点边框颜色映射
const nodeBorderColors = {
  'input': '#91d5ff',
  'output': '#b7eb8f',
  'process': '#ffd591',
  'decision': '#adc6ff',
  'api': '#d3adf7',
  'database': '#87e8de',
  'llm': '#ffadd2',
  'crawler': '#95de64',
  'analysis': '#ffc53d',
  'prediction': '#69c0ff',
  'alert': '#ff9c6e',
  'default': '#d9d9d9'
}

// 方法
const getNodeIcon = (node) => {
  return nodeIcons[node.type] || nodeIcons.default
}

const getNodeFillColor = (node) => {
  return nodeTypeColors[node.type] || nodeTypeColors.default
}

const getNodeBorderColor = (node) => {
  return nodeBorderColors[node.type] || nodeBorderColors.default
}

const getStatusColor = (status) => {
  return statusColors[status] || statusColors.default
}

const getStatusText = (status) => {
  const texts = {
    'pending': '等待中',
    'running': '运行中',
    'completed': '已完成',
    'error': '错误',
    'warning': '警告'
  }
  return texts[status] || status
}

const getEdgeColor = (edge) => {
  if (edge.status === 'success') return '#67c23a'
  if (edge.status === 'error') return '#f56c6c'
  if (edge.status === 'warning') return '#e6a23c'
  if (edge.status === 'active') return '#409eff'
  return '#666'
}

const getEdgeWidth = (edge) => {
  return edge.weight ? edge.weight * 2 : 2
}

const getEdgeMarker = (edge) => {
  if (edge.status === 'success') return 'url(#arrowhead-success)'
  if (edge.status === 'error') return 'url(#arrowhead-error)'
  if (edge.status === 'warning') return 'url(#arrowhead-warning)'
  return 'url(#arrowhead)'
}

const calculateEdgePath = (edge) => {
  const sourceNode = nodes.value.find(n => n.id === edge.source)
  const targetNode = nodes.value.find(n => n.id === edge.target)
  
  if (!sourceNode || !targetNode) return ''
  
  const sourceX = sourceNode.x + sourceNode.width
  const sourceY = sourceNode.y + sourceNode.height / 2
  const targetX = targetNode.x
  const targetY = targetNode.y + targetNode.height / 2
  
  // 贝塞尔曲线路径
  const midX = (sourceX + targetX) / 2
  return `M ${sourceX} ${sourceY} C ${midX} ${sourceY}, ${midX} ${targetY}, ${targetX} ${targetY}`
}

const formatTime = (time) => {
  if (!time) return '--'
  if (time < 1000) return `${time}ms`
  return `${(time / 1000).toFixed(2)}s`
}

const formatDateTime = (datetime) => {
  if (!datetime) return '--'
  return new Date(datetime).toLocaleString()
}

const getNodeTypeTag = (type) => {
  const tags = {
    'input': 'primary',
    'output': 'success',
    'process': 'warning',
    'decision': 'info',
    'api': 'primary',
    'database': 'success',
    'llm': 'warning',
    'crawler': 'info',
    'analysis': 'primary',
    'prediction': 'success',
    'alert': 'danger',
    'default': 'info'
  }
  return tags[type] || 'info'
}

const getStatusTag = (status) => {
  const tags = {
    'pending': 'info',
    'running': 'primary',
    'completed': 'success',
    'error': 'danger',
    'warning': 'warning'
  }
  return tags[status] || 'info'
}

const canExecuteNode = (node) => {
  return node.status === 'pending' || node.status === 'error'
}

// 事件处理
const onMouseDown = (event) => {
  if (!props.interactive) return
  isDragging.value = true
  dragStart.value = { x: event.clientX - pan.value.x, y: event.clientY - pan.value.y }
}

const onMouseMove = (event) => {
  if (!isDragging.value || !props.interactive) return
  pan.value = {
    x: event.clientX - dragStart.value.x,
    y: event.clientY - dragStart.value.y
  }
  updateTransform()
}

const onMouseUp = () => {
  isDragging.value = false
}

const onWheel = (event) => {
  if (!props.interactive) return
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  zoom.value = Math.min(Math.max(zoom.value * delta, 0.1), 5)
  updateTransform()
}

const onNodeClick = (node) => {
  if (!props.interactive) return
  // 清除其他节点的选中状态
  nodes.value.forEach(n => n.selected = false)
  node.selected = true
  selectedNode.value = node
  showNodeDetail.value = true
}

const onNodeDoubleClick = (node) => {
  if (!props.interactive) return
  ElMessage.info(`双击节点: ${node.name}`)
}

const onEdgeClick = (edge) => {
  if (!props.interactive) return
  ElMessage.info(`点击连接: ${edge.source} -> ${edge.target}`)
}

const onNodeMouseDown = (node, event) => {
  if (!props.interactive) return
  event.stopPropagation()
  // 节点拖动逻辑可以在这里实现
}

const onConnectionPointMouseDown = (point, event) => {
  if (!props.interactive) return
  event.stopPropagation()
  // 连接点拖动逻辑可以在这里实现
}

// 控制方法
const zoomIn = () => {
  zoom.value = Math.min(zoom.value * 1.2, 5)
  updateTransform()
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value * 0.8, 0.1)
  updateTransform()
}

const fitToView = () => {
  // 计算所有节点的边界框
  if (nodes.value.length === 0) return
  
  const bounds = {
    minX: Math.min(...nodes.value.map(n => n.x)),
    minY: Math.min(...nodes.value.map(n => n.y)),
    maxX: Math.max(...nodes.value.map(n => n.x + n.width)),
    maxY: Math.max(...nodes.value.map(n => n.y + n.height))
  }
  
  const width = bounds.maxX - bounds.minX
  const height = bounds.maxY - bounds.minY
  
  // 计算合适的缩放级别
  const scaleX = svgWidth.value / (width + 100)
  const scaleY = svgHeight.value / (height + 100)
  zoom.value = Math.min(scaleX, scaleY, 1)
  
  // 居中显示
  pan.value = {
    x: (svgWidth.value - width * zoom.value) / 2 - bounds.minX * zoom.value,
    y: (svgHeight.value - height * zoom.value) / 2 - bounds.minY * zoom.value
  }
  
  updateTransform()
}

const toggleLayout = () => {
  layout.value = layout.value === 'horizontal' ? 'vertical' : 'horizontal'
  arrangeNodes()
}

const executeNode = async (node) => {
  try {
    node.status = 'running'
    ElMessage.success(`开始执行节点: ${node.name}`)
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    node.status = 'completed'
    node.executionTime = 1000
    node.endTime = new Date().toISOString()
    
    ElMessage.success(`节点执行完成: ${node.name}`)
  } catch (error) {
    node.status = 'error'
    node.error = error.message
    ElMessage.error(`节点执行失败: ${error.message}`)
  }
}

const executeWorkflow = async () => {
  if (executing.value) return
  
  executing.value = true
  ElMessage.info('开始执行工作流...')
  
  try {
    // 重置所有节点状态
    nodes.value.forEach(node => {
      if (node.status !== 'completed') {
        node.status = 'pending'
        node.executionTime = null
        node.startTime = null
        node.endTime = null
      }
    })
    
    // 按顺序执行节点（简化版本）
    for (const node of nodes.value) {
      if (node.status === 'pending') {
        activeNode.value = node
        node.startTime = new Date().toISOString()
        await executeNode(node)
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }
    
    activeNode.value = null
    ElMessage.success('工作流执行完成！')
  } catch (error) {
    ElMessage.error(`工作流执行失败: ${error.message}`)
  } finally {
    executing.value = false
  }
}

const resetWorkflow = () => {
  nodes.value.forEach(node => {
    node.status = 'pending'
    node.executionTime = null
    node.startTime = null
    node.endTime = null
    node.error = null
  })
  edges.value.forEach(edge => {
    edge.status = null
  })
  activeNode.value = null
  ElMessage.success('工作流已重置')
}

const saveWorkflow = () => {
  const workflow = {
    nodes: nodes.value.map(n => ({
      id: n.id,
      name: n.name,
      type: n.type,
      x: n.x,
      y: n.y
    })),
    edges: edges.value.map(e => ({
      source: e.source,
      target: e.target,
      type: e.type
    })),
    metadata: {
      layout: layout.value,
      createdAt: new Date().toISOString()
    }
  }
  
  ElMessage.success('工作流已保存')
  console.log('保存的工作流:', workflow)
}

const editNode = (node) => {
  ElMessage.info(`编辑节点: ${node.name}`)
  // 实际应用中可以打开节点编辑对话框
}

const removeNode = (node) => {
  ElMessageBox.confirm(
    `确定要移除节点 "${node.name}" 吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = nodes.value.findIndex(n => n.id === node.id)
    if (index !== -1) {
      nodes.value.splice(index, 1)
      // 移除相关的连接
      edges.value = edges.value.filter(e => e.source !== node.id && e.target !== node.id)
      ElMessage.success('节点已移除')
    }
  }).catch(() => {})
}

// 布局算法
const arrangeNodes = () => {
  if (nodes.value.length === 0) return
  
  if (layout.value === 'horizontal') {
    // 水平布局
    const nodeWidth = 120
    const nodeHeight = 100
    const horizontalSpacing = 200
    const verticalSpacing = 150
    
    nodes.value.forEach((node, index) => {
      const row = Math.floor(index / 3)
      const col = index % 3
      
      node.x = col * horizontalSpacing + 50
      node.y = row * verticalSpacing + 50
      node.width = nodeWidth
      node.height = nodeHeight
    })
  } else {
    // 垂直布局
    const nodeWidth = 120
    const nodeHeight = 100
    const verticalSpacing = 120
    
    nodes.value.forEach((node, index) => {
      node.x = 100
      node.y = index * verticalSpacing + 50
      node.width = nodeWidth
      node.height = nodeHeight
    })
  }
}

// 更新SVG变换
const updateTransform = () => {
  const svg = svgRef.value
  if (!svg) return
  
  const transform = `translate(${pan.value.x}, ${pan.value.y}) scale(${zoom.value})`
  svg.querySelectorAll('.nodes, .connections, .connection-points').forEach(g => {
    g.setAttribute('transform', transform)
  })
}

// 引用
const container = ref(null)
const svgRef = ref(null)

// 生命周期
onMounted(() => {
  // 初始化数据
  if (props.workflowData.nodes && props.workflowData.nodes.length > 0) {
    nodes.value = props.workflowData.nodes.map(node => ({
      ...node,
      width: node.width || 120,
      height: node.height || 100,
      status: node.status || 'pending',
      selected: false
    }))
  } else {
    // 默认示例数据
    nodes.value = [
      { id: '1', name: '数据输入', type: 'input', x: 50, y: 50, status: 'completed' },
      { id: '2', name: '数据清洗', type: 'process', x: 200, y: 50, status: 'running' },
      { id: '3', name: '特征提取', type: 'analysis', x: 350, y: 50, status: 'pending' },
      { id: '4', name: '模型预测', type: 'prediction', x: 500, y: 50, status: 'pending' },
      { id: '5', name: '结果输出', type: 'output', x: 650, y: 50, status: 'pending' }
    ].map(node => ({
      ...node,
      width: 120,
      height: 100,
      selected: false
    }))
  }
  
  if (props.workflowData.edges && props.workflowData.edges.length > 0) {
    edges.value = props.workflowData.edges
  } else {
    // 默认示例连接
    edges.value = [
      { source: '1', target: '2', type: 'data' },
      { source: '2', target: '3', type: 'data' },
      { source: '3', target: '4', type: 'data' },
      { source: '4', target: '5', type: 'result' }
    ]
  }
  
  // 自动布局
  arrangeNodes()
  fitToView()
})

onUnmounted(() => {
  // 清理工作
})

// 监听数据变化
watch(() => props.workflowData, (newData) => {
  if (newData.nodes) {
    nodes.value = newData.nodes.map(node => ({
      ...node,
      width: node.width || 120,
      height: node.height || 100,
      status: node.status || 'pending',
      selected: false
    }))
  }
  if (newData.edges) {
    edges.value = newData.edges
  }
  arrangeNodes()
}, { deep: true })
</script>

<style scoped>
.agent-workflow-visualization {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
}

.workflow-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.workflow-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.workflow-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.workflow-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.workflow-svg:active {
  cursor: grabbing;
}

.workflow-node {
  cursor: pointer;
  transition: transform 0.2s;
}

.workflow-node:hover {
  transform: scale(1.05);
}

.node-body {
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.1));
}

.node-icon {
  font-size: 24px;
  pointer-events: none;
}

.node-title {
  font-size: 12px;
  fill: #303133;
  pointer-events: none;
}

.node-status {
  font-size: 10px;
  font-weight: bold;
  pointer-events: none;
}

.node-time {
  pointer-events: none;
}

.selection-indicator {
  pointer-events: none;
}

.connection-line {
  cursor: pointer;
  transition: stroke-width 0.2s;
}

.connection-line:hover {
  stroke-width: 3;
}

.connection-point {
  cursor: crosshair;
  transition: r 0.2s;
}

.connection-point:hover {
  r: 6;
}

.active-node-highlight {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 0.8; }
  100% { opacity: 0.5; }
}

.workflow-control-panel {
  margin-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.workflow-info {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
}

.info-item {
  text-align: center;
}

.info-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  display: block;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.workflow-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.node-detail {
  padding: 0 16px;
}

.config-pre {
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow: auto;
  margin: 0;
}

.node-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>