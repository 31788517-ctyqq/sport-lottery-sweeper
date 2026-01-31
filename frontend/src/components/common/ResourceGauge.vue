<template>
  <div class="resource-gauge">
    <div class="gauge-title">{{ title }}</div>
    <div class="gauge-container" ref="gaugeContainer"></div>
    <div class="gauge-info">
      <div class="gauge-value">{{ displayValue }}{{ unit }}</div>
      <div class="gauge-label">当前使用率</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: Number,
    default: 0
  },
  max: {
    type: Number,
    default: 100
  },
  unit: {
    type: String,
    default: '%'
  },
  thresholds: {
    type: Array,
    default: () => [70, 90]
  }
})

const gaugeContainer = ref(null)
let gaugeChart = null

const displayValue = ref(0)

// 计算显示值
watch(() => [props.value, props.max], () => {
  if (props.max && props.max !== 100) {
    displayValue.value = ((props.value / props.max) * 100).toFixed(1)
  } else {
    displayValue.value = props.value.toFixed(1)
  }
}, { immediate: true })

// 根据数值获取颜色
const getColorByValue = (value) => {
  if (value >= props.thresholds[1]) {
    return '#F56C6C' // 红色 - 危险
  } else if (value >= props.thresholds[0]) {
    return '#E6A23C' // 橙色 - 警告
  } else {
    return '#67C23A' // 绿色 - 正常
  }
}

// 初始化仪表盘
const initGauge = async () => {
  await nextTick()
  if (!gaugeContainer.value) return
  
  gaugeChart = echarts.init(gaugeContainer.value)
  updateGauge()
}

// 更新仪表盘
const updateGauge = () => {
  if (!gaugeChart) return
  
  const option = {
    series: [
      {
        name: props.title,
        type: 'gauge',
        min: 0,
        max: 100,
        splitNumber: 10,
        radius: '100%',
        axisLine: {
          lineStyle: {
            width: 12,
            color: [
              [props.thresholds[1] / 100, '#F56C6C'],
              [props.thresholds[0] / 100, '#E6A23C'],
              [1, '#67C23A']
            ]
          }
        },
        pointer: {
          itemStyle: {
            color: getColorByValue(displayValue.value)
          }
        },
        axisTick: {
          distance: -20,
          length: 8,
          lineStyle: {
            color: '#fff',
            width: 2
          }
        },
        splitLine: {
          distance: -20,
          length: 20,
          lineStyle: {
            color: '#fff',
            width: 4
          }
        },
        axisLabel: {
          color: 'auto',
          distance: 30,
          fontSize: 12
        },
        detail: {
          valueAnimation: true,
          formatter: '{value}',
          color: getColorByValue(displayValue.value),
          fontSize: 20,
          fontWeight: 'bold',
          offsetCenter: [0, '50%']
        },
        data: [
          {
            value: displayValue.value,
            name: props.title
          }
        ]
      }
    ]
  }
  
  gaugeChart.setOption(option)
}

// 监听数值变化更新图表
watch(displayValue, () => {
  updateGauge()
})

// 窗口大小改变时重新调整图表
const handleResize = () => {
  gaugeChart?.resize()
}

// 生命周期
onMounted(() => {
  initGauge()
  window.addEventListener('resize', handleResize)
})

// 清理资源
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  gaugeChart?.dispose()
})
</script>

<style scoped>
.resource-gauge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  height: 200px;
  justify-content: center;
}

.gauge-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  text-align: center;
}

.gauge-container {
  width: 120px;
  height: 120px;
  margin-bottom: 10px;
}

.gauge-info {
  text-align: center;
}

.gauge-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.gauge-label {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .resource-gauge {
    height: 180px;
    padding: 15px;
  }
  
  .gauge-container {
    width: 100px;
    height: 100px;
  }
  
  .gauge-value {
    font-size: 20px;
  }
  
  .gauge-title {
    font-size: 12px;
  }
}
</style>