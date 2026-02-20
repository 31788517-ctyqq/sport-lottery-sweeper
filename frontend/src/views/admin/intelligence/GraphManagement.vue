<template>
  <div class="intelligence-graph-page">
    <div class="page-header">
      <div>
        <h2>图谱管理</h2>
        <p>基于采集结果构建比赛-来源-情报类型的关联图谱</p>
      </div>
      <div class="header-actions">
        <el-select v-model="query.days" style="width: 130px">
          <el-option label="最近3天" :value="3" />
          <el-option label="最近7天" :value="7" />
          <el-option label="最近15天" :value="15" />
          <el-option label="最近30天" :value="30" />
        </el-select>
        <el-input-number v-model="query.limit" :min="50" :max="5000" :step="50" />
        <el-switch
          v-model="query.includePrediction"
          inline-prompt
          active-text="含预测"
          inactive-text="仅场外"
        />
        <el-button :icon="Refresh" :loading="loading.graph" type="primary" @click="loadGraphData">
          刷新图谱
        </el-button>
      </div>
    </div>

    <el-row :gutter="12" class="stats-row">
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card">
          <div class="stat-label">采集条数</div>
          <div class="stat-value">{{ graph.stats.total_items }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card">
          <div class="stat-label">图谱节点</div>
          <div class="stat-value">{{ graph.stats.total_nodes }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card">
          <div class="stat-label">关联边</div>
          <div class="stat-value">{{ graph.stats.total_edges }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card">
          <div class="stat-label">比赛数</div>
          <div class="stat-value">{{ graph.stats.total_matches }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card">
          <div class="stat-label">来源数</div>
          <div class="stat-value">{{ graph.stats.total_sources }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card">
          <div class="stat-label">类型数</div>
          <div class="stat-value">{{ graph.stats.total_types }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" class="main-row">
      <el-col :xs="24" :lg="17">
        <el-card shadow="never" class="graph-card" v-loading="loading.graph">
          <template #header>
            <div class="card-header">图谱可视化</div>
          </template>
          <div ref="graphRef" class="graph-canvas" />
          <el-empty v-if="!loading.graph && !graph.nodes.length" description="暂无可用图谱数据" />
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="7">
        <el-card shadow="never" class="side-card">
          <template #header>
            <div class="card-header">网络指标</div>
          </template>
          <div class="metric-item">
            <span>平均度</span>
            <strong>{{ graph.networkMetrics.avg_degree }}</strong>
          </div>
          <div class="metric-item">
            <span>密度</span>
            <strong>{{ graph.networkMetrics.density }}</strong>
          </div>
          <div class="metric-item">
            <span>节点数</span>
            <strong>{{ graph.networkMetrics.node_count }}</strong>
          </div>
          <div class="metric-item">
            <span>边数</span>
            <strong>{{ graph.networkMetrics.edge_count }}</strong>
          </div>
        </el-card>

        <el-card shadow="never" class="side-card">
          <template #header>
            <div class="card-header">节点详情</div>
          </template>
          <div v-if="selectedNode" class="node-detail">
            <el-tag size="small" type="primary">{{ selectedNode.category }}</el-tag>
            <h4>{{ selectedNode.name }}</h4>
            <div class="detail-row">
              <span>热度值</span>
              <strong>{{ selectedNode.value }}</strong>
            </div>
            <div class="detail-row" v-for="entry in selectedMetaEntries" :key="entry.key">
              <span>{{ entry.key }}</span>
              <strong>{{ entry.value }}</strong>
            </div>
            <div class="detail-row">
              <span>关联边</span>
              <strong>{{ relatedEdges.length }}</strong>
            </div>
          </div>
          <el-empty v-else description="点击图谱节点查看详情" :image-size="72" />
        </el-card>

        <el-card shadow="never" class="side-card">
          <template #header>
            <div class="card-header">Top 节点</div>
          </template>
          <el-table :data="graph.topNodes" size="small" max-height="260" empty-text="暂无数据">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="name" label="节点" min-width="120" show-overflow-tooltip />
            <el-table-column prop="degree" label="度" width="70" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getCollectionGraphOverview } from '@/api/intelligenceCollection'

const graphRef = ref(null)
const loading = reactive({ graph: false })
const query = reactive({
  days: 7,
  limit: 800,
  includePrediction: true
})

const graph = reactive({
  stats: {
    total_items: 0,
    total_nodes: 0,
    total_edges: 0,
    total_matches: 0,
    total_sources: 0,
    total_types: 0
  },
  nodes: [],
  edges: [],
  categories: [],
  topNodes: [],
  networkMetrics: {
    avg_degree: 0,
    density: 0,
    node_count: 0,
    edge_count: 0
  }
})

const selectedNodeId = ref('')
let graphChart = null

const categoryColorMap = {
  match: '#5b8ff9',
  team: '#5ad8a6',
  league: '#f6bd16',
  source: '#6f5ef9',
  intel_type: '#ff8a45'
}

const selectedNode = computed(() => graph.nodes.find((x) => x.id === selectedNodeId.value) || null)

const selectedMetaEntries = computed(() => {
  const meta = selectedNode.value?.meta || {}
  return Object.entries(meta)
    .filter(([, value]) => value !== null && value !== undefined && String(value).trim() !== '')
    .map(([key, value]) => ({ key, value: String(value) }))
})

const relatedEdges = computed(() => {
  const id = selectedNodeId.value
  if (!id) return []
  return graph.edges.filter((x) => x.source === id || x.target === id)
})

const buildChartOption = () => {
  const categoryIndexMap = new Map(
    (graph.categories || []).map((c, idx) => [String(c.key || '').toLowerCase(), idx])
  )

  const chartNodes = (graph.nodes || []).map((node) => {
    const key = String(node.type || '').toLowerCase()
    const cidx = categoryIndexMap.has(key) ? categoryIndexMap.get(key) : 0
    return {
      ...node,
      category: cidx,
      symbolSize: node.symbol_size || 22,
      itemStyle: {
        color: categoryColorMap[key] || '#7f8c8d'
      }
    }
  })

  const chartLinks = (graph.edges || []).map((edge) => ({
    ...edge,
    value: edge.count || 1,
    lineStyle: {
      width: Math.min(6, 1 + Math.log2((edge.count || 1) + 1)),
      opacity: 0.6
    }
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'edge') {
          const edge = params.data || {}
          return `${edge.relation || 'relation'}<br/>权重: ${edge.count || 1}`
        }
        const node = params.data || {}
        return `${node.name || '-'}<br/>类型: ${node.category ?? '-'}<br/>热度: ${node.value || 0}`
      }
    },
    animationDuration: 300,
    animationDurationUpdate: 300,
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        data: chartNodes,
        links: chartLinks,
        categories: (graph.categories || []).map((c) => ({ name: c.name })),
        focusNodeAdjacency: true,
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: 6,
        label: {
          show: chartNodes.length <= 120,
          position: 'right',
          formatter: '{b}',
          fontSize: 11
        },
        force: {
          repulsion: 180,
          gravity: 0.08,
          edgeLength: [70, 220]
        },
        lineStyle: {
          color: '#8ea0b5',
          opacity: 0.55,
          curveness: 0.2
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 2.5,
            opacity: 0.95
          }
        }
      }
    ]
  }
}

const renderGraph = async () => {
  await nextTick()
  if (!graphRef.value) return
  if (!graphChart) {
    graphChart = echarts.init(graphRef.value)
    graphChart.on('click', (params) => {
      if (params?.dataType === 'node' && params.data?.id) {
        selectedNodeId.value = params.data.id
      }
    })
  }
  graphChart.setOption(buildChartOption(), true)
}

const loadGraphData = async () => {
  loading.graph = true
  try {
    const data = await getCollectionGraphOverview({
      days: query.days,
      limit: query.limit,
      include_prediction: query.includePrediction
    })

    graph.stats = {
      ...graph.stats,
      ...(data?.stats || {})
    }
    graph.nodes = Array.isArray(data?.nodes) ? data.nodes : []
    graph.edges = Array.isArray(data?.edges) ? data.edges : []
    graph.categories = Array.isArray(data?.categories) ? data.categories : []
    graph.topNodes = Array.isArray(data?.top_nodes) ? data.top_nodes : []
    graph.networkMetrics = {
      ...graph.networkMetrics,
      ...(data?.network_metrics || {})
    }

    if (selectedNodeId.value && !graph.nodes.some((x) => x.id === selectedNodeId.value)) {
      selectedNodeId.value = ''
    }

    await renderGraph()
  } catch (error) {
    console.error('加载图谱失败', error)
    ElMessage.error('加载图谱失败')
  } finally {
    loading.graph = false
  }
}

const handleResize = () => {
  if (graphChart) graphChart.resize()
}

onMounted(async () => {
  await loadGraphData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (graphChart) {
    graphChart.dispose()
    graphChart = null
  }
})
</script>

<style scoped>
.intelligence-graph-page {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  color: #1f2d3d;
}

.page-header p {
  margin: 6px 0 0;
  color: #6b7280;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.stats-row {
  margin-bottom: 12px;
}

.stat-card {
  border-radius: 10px;
}

.stat-label {
  color: #8091a7;
  font-size: 12px;
}

.stat-value {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 600;
  color: #274862;
}

.main-row {
  margin-bottom: 12px;
}

.graph-card,
.side-card {
  border-radius: 10px;
}

.graph-canvas {
  height: 680px;
}

.card-header {
  font-weight: 600;
  color: #2a3f54;
}

.metric-item,
.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #4b5b6a;
}

.metric-item strong,
.detail-row strong {
  color: #1f2937;
}

.node-detail h4 {
  margin: 10px 0;
  color: #0f172a;
}

.side-card {
  margin-bottom: 12px;
}

@media (max-width: 1200px) {
  .graph-canvas {
    height: 560px;
  }
}
</style>
