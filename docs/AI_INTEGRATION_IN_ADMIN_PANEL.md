# AI功能集成到后台管理系统

## 概述

本文档详细说明如何将项目中的AI功能集成到后台管理系统中，包括LLM服务管理、智能体监控、预测模型管理等AI原生功能。

## AI功能架构

### 1. LLM服务层
- **统一接口**：通过LLMService统一管理不同提供商
- **成本控制**：监控API调用成本和使用量
- **多提供商**：支持OpenAI、Gemini、Qwen等

### 2. 智能体系统
- **自主决策**：智能体自动执行任务
- **协作机制**：多智能体协同工作
- **通信协议**：标准化通信机制

### 3. 预测与分析
- **机器学习模型**：传统ML预测
- **LLM辅助分析**：自然语言解释预测
- **多模态分析**：图像/视频分析

## 后台管理AI功能模块

### 1. LLM服务管理模块

#### 1.1 功能描述
- 管理不同LLM提供商的配置
- 监控API使用量和成本
- 配置默认提供商和参数

#### 1.2 前端实现
```vue
<template>
  <div class="llm-management">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="提供商管理" name="providers">
        <el-table :data="providers" style="width: 100%">
          <el-table-column prop="name" label="提供商" width="150"></el-table-column>
          <el-table-column prop="enabled" label="状态" width="100">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="updateProvider(row)" />
            </template>
          </el-table-column>
          <el-table-column prop="requestCount" label="请求数" width="100"></el-table-column>
          <el-table-column prop="cost" label="成本" width="100">
            <template #default="{ row }">
              ¥{{ row.cost.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="editProvider(row)">编辑</el-button>
              <el-button size="small" type="primary" @click="testProvider(row)">测试</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="成本监控" name="costs">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>LLM服务成本统计</span>
            </div>
          </template>
          
          <div ref="costChartRef" style="height: 400px;"></div>
          
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="6">
              <el-statistic title="本月总成本" :value="monthlyCost" :precision="2">
                <template #suffix>元</template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="总请求数" :value="totalRequests"></el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="平均响应时间" :value="avgResponseTime" :precision="2">
                <template #suffix>s</template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功率" :value="successRate" :precision="2">
                <template #suffix>%</template>
              </el-statistic>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { aiApi } from '@/api/ai'
import * as echarts from 'echarts'

const activeTab = ref('providers')
const providers = ref([])
const monthlyCost = ref(0)
const totalRequests = ref(0)
const avgResponseTime = ref(0)
const successRate = ref(0)

// 图表引用
const costChartRef = ref<HTMLDivElement>()

onMounted(async () => {
  await loadProviders()
  await loadCostStats()
  initCostChart()
})

const loadProviders = async () => {
  try {
    const response = await aiApi.getProviders()
    providers.value = response.data
  } catch (error) {
    ElMessage.error('加载提供商失败')
  }
}

const loadCostStats = async () => {
  try {
    const response = await aiApi.getCostStats()
    // 计算统计值
    monthlyCost.value = response.data.reduce((sum, stat) => sum + stat.cost, 0)
    totalRequests.value = response.data.reduce((sum, stat) => sum + stat.requestCount, 0)
    avgResponseTime.value = response.data.reduce((sum, stat) => sum + stat.avgResponseTime, 0) / response.data.length || 0
    successRate.value = response.data.reduce((sum, stat) => sum + stat.successRate, 0) / response.data.length || 0
  } catch (error) {
    ElMessage.error('加载成本统计失败')
  }
}

const initCostChart = () => {
  const chart = echarts.init(costChartRef.value!)
  chart.setOption({
    title: { text: '月度成本趋势' },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'] },
    yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
    series: [{
      data: [1200, 1320, 1010, 1340, 900, 2300, 2100],
      type: 'line',
      smooth: true,
      areaStyle: {}
    }]
  })
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

const updateProvider = async (provider: any) => {
  try {
    await aiApi.updateProvider(provider.name, { enabled: provider.enabled })
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const testProvider = async (provider: any) => {
  try {
    // 发送测试请求
    const response = await aiApi.testProvider(provider.name)
    ElMessage.success(`测试成功: ${response.data.message}`)
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

const editProvider = (provider: any) => {
  // 打开编辑对话框
}
</script>
```

#### 1.3 后端API实现
```python
# backend/api/v1/admin/llm.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ... import crud, models, schemas
from ...database import get_db
from ...dependencies import get_current_user
from ...services.llm_service import llm_service

router = APIRouter(prefix="/admin/llm", tags=["admin-llm"])

@router.get("/providers", response_model=List[schemas.LLMProviderConfig])
def get_llm_providers(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取LLM提供商列表"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    providers = []
    for name, provider in llm_service.providers.items():
        # 获取提供商统计信息
        stats = llm_service.get_provider_stats(name)
        providers.append({
            "name": name,
            "enabled": name in llm_service.providers,
            "request_count": stats.get("request_count", 0),
            "cost": stats.get("cost", 0.0)
        })
    
    return providers

@router.put("/providers/{provider_name}", response_model=schemas.LLMProviderConfig)
def update_llm_provider(
    provider_name: str,
    config: schemas.LLMProviderUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新LLM提供商配置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 更新提供商配置
    if config.enabled and provider_name not in llm_service.providers:
        # 重新注册提供商
        api_key = config.api_key or get_api_key_from_db(provider_name, db)
        if api_key:
            llm_service.register_provider(provider_name, api_key)
    elif not config.enabled and provider_name in llm_service.providers:
        # 从服务中移除提供商
        del llm_service.providers[provider_name]
    
    return {
        "name": provider_name,
        "enabled": config.enabled,
        "request_count": 0,  # 实际实现中应从统计中获取
        "cost": 0.0
    }

@router.get("/costs", response_model=List[schemas.AIServiceStats])
def get_llm_costs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取LLM成本统计"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    stats = []
    for name, provider in llm_service.providers.items():
        provider_stats = llm_service.get_provider_stats(name)
        stats.append({
            "provider": name,
            "request_count": provider_stats.get("request_count", 0),
            "cost": provider_stats.get("cost", 0.0),
            "avg_response_time": provider_stats.get("avg_response_time", 0.0),
            "success_rate": provider_stats.get("success_rate", 0.0)
        })
    
    return stats
```

### 2. 智能体管理模块

#### 2.1 功能描述
- 监控各智能体运行状态
- 配置智能体参数
- 查看智能体执行日志

#### 2.2 前端实现
```vue
<template>
  <div class="agent-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>智能体管理</span>
          <el-button type="primary" @click="refreshAgents">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="agents" style="width: 100%">
        <el-table-column prop="id" label="ID" width="150"></el-table-column>
        <el-table-column prop="name" label="名称" width="200"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastExecuted" label="上次执行" width="180"></el-table-column>
        <el-table-column prop="taskCount" label="任务数" width="100"></el-table-column>
        <el-table-column prop="errorCount" label="错误数" width="100"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewLogs(row)">查看日志</el-button>
            <el-button size="small" type="primary" @click="executeAgent(row)">立即执行</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 日志对话框 -->
    <el-dialog v-model="logDialogVisible" title="智能体日志" width="80%">
      <el-table :data="agentLogs" height="400">
        <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLogLevelType(row.level)">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息"></el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { aiApi } from '@/api/ai'

const agents = ref([])
const agentLogs = ref([])
const logDialogVisible = ref(false)
const selectedAgent = ref(null)

onMounted(async () => {
  await loadAgents()
})

const loadAgents = async () => {
  try {
    const response = await aiApi.getAgentStatus()
    agents.value = response.data.map(agent => ({
      ...agent,
      lastExecuted: agent.lastExecuted ? new Date(agent.lastExecuted).toLocaleString() : '从未执行'
    }))
  } catch (error) {
    ElMessage.error('加载智能体状态失败')
  }
}

const refreshAgents = async () => {
  await loadAgents()
  ElMessage.success('已刷新')
}

const getStatusType = (status: string) => {
  switch (status.toLowerCase()) {
    case 'running':
      return 'success'
    case 'stopped':
      return 'info'
    case 'error':
      return 'danger'
    default:
      return 'warning'
  }
}

const getLogLevelType = (level: string) => {
  switch (level.toLowerCase()) {
    case 'error':
      return 'danger'
    case 'warn':
      return 'warning'
    case 'info':
      return 'info'
    default:
      return 'primary'
  }
}

const viewLogs = async (agent: any) => {
  selectedAgent.value = agent
  try {
    // 获取智能体日志
    agentLogs.value = [
      { timestamp: new Date().toLocaleString(), level: 'info', message: '智能体启动成功' },
      { timestamp: new Date().toLocaleString(), level: 'info', message: '开始执行任务' },
      { timestamp: new Date().toLocaleString(), level: 'success', message: '任务执行成功' }
    ]
    logDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取日志失败')
  }
}

const executeAgent = async (agent: any) => {
  try {
    await aiApi.executeAgent(agent.id)
    ElMessage.success('已发送执行指令')
  } catch (error) {
    ElMessage.error('执行失败')
  }
}
</script>
```

#### 2.3 后端API实现
```python
# backend/api/v1/admin/agents.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ... import crud, models, schemas
from ...database import get_db
from ...dependencies import get_current_user
from ...agents.communication_protocol import communication_hub

router = APIRouter(prefix="/admin/agents", tags=["admin-agents"])

@router.get("/", response_model=List[schemas.AgentStatus])
def get_agent_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有智能体状态"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    status = communication_hub.get_agent_status()
    agents = []
    
    for agent_id, agent_status in status.items():
        # 获取智能体详细信息
        agents.append({
            "id": agent_id,
            "name": agent_id.replace("_", " ").title(),
            "status": agent_status,
            "last_executed": None,  # 实际实现中应从数据库或日志获取
            "task_count": 0,  # 实际实现中应从数据库获取
            "error_count": 0  # 实际实现中应从数据库获取
        })
    
    return agents

@router.post("/{agent_id}/execute")
def execute_agent(
    agent_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """立即执行智能体"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    if agent_id not in communication_hub.agents:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    # 这里需要触发智能体执行
    # 具体实现取决于智能体的执行机制
    # 可能需要通过Celery任务或其他异步机制执行
    
    return {"message": f"已发送执行指令给智能体 {agent_id}"}
```

### 3. 预测模型管理模块

#### 3.1 功能描述
- 管理预测模型配置
- 监控模型性能指标
- 查看预测准确率分析

## AI功能集成最佳实践

### 1. 错误处理
- 对LLM调用实现重试机制
- 优雅处理API配额超限
- 提供备用提供商

### 2. 性能优化
- 实现响应缓存机制
- 使用异步处理提高响应速度
- 合理设置请求频率限制

### 3. 成本控制
- 实时监控API使用成本
- 设置预算警告机制
- 提供成本优化建议

### 4. 安全考虑
- 安全存储API密钥
- 实现访问权限控制
- 记录AI服务使用日志

## 测试与验证

### 1. 单元测试
```python
def test_llm_service_management():
    # 测试LLM服务管理功能
    pass

def test_agent_status_monitoring():
    # 测试智能体状态监控
    pass
```

### 2. 集成测试
```python
def test_admin_ai_endpoints():
    # 测试后台AI管理端点
    pass
```

### 3. 端到端测试
```typescript
// 测试前端AI管理界面
describe('AI Management UI', () => {
  it('should display provider statistics', () => {
    // 测试提供商统计显示
  })
})
```

## 部署与维护

### 1. 环境配置
- 配置LLM API密钥
- 设置成本监控阈值
- 配置智能体执行参数

### 2. 监控告警
- 设置成本超限告警
- 配置智能体异常告警
- 监控API可用性

### 3. 定期维护
- 清理过期API密钥
- 评估提供商性能
- 优化成本使用