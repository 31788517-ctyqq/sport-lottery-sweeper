

爬虫管理模下的http://localhost:3015/admin/crawler/data-source数据源管理页面按照以下布局设计帮我生成页面：

1、在系统架构参考其布局和代码
2、页面布局在数据源管理页面，对应在整个页面的在右边页面区域；
3、功能和布局设计以代码里面的为主；
4、在不和项目系统发生冲突的基础上计量去设计。
5、这个页面包含以下部分：数据源注册管理、解析配置管理、api接口设计

以下是包含部分的页面代码布局参考：
数据源注册管理：

# models/source.py
from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

class SourceType(Enum):
    WEB = "web"           # 网页数据源
    API = "api"           # API接口
    RSS = "rss"           # RSS订阅
    DATABASE = "database" # 数据库
    FILE = "file"         # 文件

class FootballLeague(Enum):
    PREMIER_LEAGUE = "premier_league"
    LA_LIGA = "la_liga"
    SERIE_A = "serie_a"
    BUNDESLIGA = "bundesliga"
    LIGUE_1 = "ligue_1"
    CSL = "chinese_super_league"  # 中超
    ACL = "afc_champions_league"  # 亚冠

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)          # 数据源名称
    type = Column(Enum(SourceType), nullable=False)     # 数据源类型
    category = Column(String(50), default="football")   # 分类
    
    # 足球专项字段
    leagues = Column(JSON, default=list)                # 覆盖的联赛
    data_types = Column(JSON, default=list)            # 数据类型: ["schedule", "odds", "result", "stats"]
    
    # 访问配置
    url = Column(String(500))                          # 访问地址
    method = Column(String(10), default="GET")         # HTTP方法
    headers = Column(JSON, default=dict)               # 请求头
    params = Column(JSON, default=dict)                # 查询参数
    auth_config = Column(JSON, default=dict)           # 认证配置
    
    # 解析配置
    parser_type = Column(String(20), default="css")    # 解析器类型
    parser_config = Column(JSON, default=dict)         # 解析配置
    
    # 状态管理
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)              # 采集优先级
    success_rate = Column(Integer, default=0)          # 成功率
    last_crawl_time = Column(DateTime)                 # 最后采集时间
    
    # 监控字段
    total_requests = Column(Integer, default=0)        # 总请求数
    failed_requests = Column(Integer, default=0)       # 失败请求数
    avg_response_time = Column(Integer)                # 平均响应时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    解析配置管理：

# models/parser_config.py
class ParserConfig(Base):
    __tablename__ = "parser_configs"
    
    id = Column(UUID, primary_key=True)
    source_id = Column(UUID, ForeignKey('data_sources.id'))
    name = Column(String(100))  # 配置名称
    
    # 足球数据字段映射
    field_mappings = Column(JSON, default={
        "match_id": {"selector": "td:nth-child(1)", "type": "text"},
        "league": {"selector": "td:nth-child(2)", "type": "text"},
        "match_time": {"selector": "td:nth-child(3)", "type": "datetime"},
        "teams": {"selector": "td:nth-child(4)", "type": "text"},
        "handicap": {"selector": "td:nth-child(5)", "type": "text"},
        "home_odds": {"selector": "td:nth-child(6)", "type": "float"},
        "draw_odds": {"selector": "td:nth-child(7)", "type": "float"},
        "away_odds": {"selector": "td:nth-child(8)", "type": "float"}
    })
    
    # 数据清洗规则
    cleaning_rules = Column(JSON, default={
        "teams": {"remove_patterns": [r"\[\d+\]", r"\[\d+/\d+\]"]},
        "match_time": {"timezone": "Asia/Shanghai", "format": "MM-DD HH:mm"}
    })
    
    # 验证规则
    validation_rules = Column(JSON, default={
        "required_fields": ["match_id", "league", "match_time"],
        "odds_range": {"min": 1.0, "max": 1000.0},
        "time_format": "YYYY-MM-DD HH:mm"
    })

api接口设计

# api/sources.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

router = APIRouter(prefix="/api/sources", tags=["data-sources"])

@router.get("/", response_model=List[SourceResponse])
async def list_sources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    league: Optional[str] = None,
    status: Optional[str] = None
):
    """获取数据源列表"""
    query = db.query(DataSource)
    
    if type:
        query = query.filter(DataSource.type == type)
    if league:
        query = query.filter(DataSource.leagues.contains([league]))
    if status == "active":
        query = query.filter(DataSource.is_active == True)
    elif status == "inactive":
        query = query.filter(DataSource.is_active == False)
    
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/", response_model=SourceResponse)
async def create_source(source_data: SourceCreate):
    """创建新数据源"""
    # 验证配置
    validator = SourceValidator(source_data)
    if not validator.validate():
        raise HTTPException(status_code=400, detail="配置验证失败")
    
    # 测试连接
    tester = SourceTester(source_data)
    test_result = await tester.test_connection()
    if not test_result.success:
        raise HTTPException(status_code=400, detail=f"连接测试失败: {test_result.message}")
    
    # 创建数据源
    source = DataSource(**source_data.dict())
    db.add(source)
    db.commit()
    db.refresh(source)
    
    # 自动创建关联任务
    task_service.create_related_tasks(source.id)
    
    return source

@router.post("/{source_id}/test")
async def test_source(source_id: UUID):
    """测试数据源配置"""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    tester = SourceTester(source)
    result = await tester.full_test()
    
    # 更新健康状态
    source.success_rate = result.success_rate
    source.last_test_time = datetime.utcnow()
    db.commit()
    
    return result

@router.get("/templates")
async def get_source_templates():
    """获取数据源模板"""
    templates = {
        "500_jczq": {
            "name": "500彩票网-竞彩足球",
            "type": "web",
            "url": "https://trade.500.com/jczq/",
            "parser_type": "css",
            "field_mappings": {...},
            "description": "竞彩足球赛程与赔率"
        },
        "aoke_odds": {
            "name": "澳客网-赔率数据",
            "type": "web",
            "url": "https://www.okooo.com/soccer/odds/",
            "parser_type": "xpath",
            "field_mappings": {...}
        }
    }
    return templates

以下是页面前端组件设计参考：
<!-- components/SourceList.vue -->
<template>
  <div class="source-manager">
    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-input v-model="searchQuery" placeholder="搜索数据源" clearable />
      <el-select v-model="filterType" placeholder="类型筛选">
        <el-option label="全部" value="" />
        <el-option label="网页" value="web" />
        <el-option label="API" value="api" />
      </el-select>
      <el-select v-model="filterLeague" placeholder="联赛筛选">
        <el-option v-for="league in leagues" :key="league.value" 
                   :label="league.label" :value="league.value" />
      </el-select>
      <el-button type="primary" @click="handleCreate">新增数据源</el-button>
      <el-button @click="refreshList">刷新</el-button>
    </div>
    
    <!-- 数据源列表 -->
    <el-table :data="sources" v-loading="loading">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="name" label="名称" width="200">
        <template #default="{row}">
          <div class="source-name">
            <el-tag :type="getStatusType(row)" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
            <span>{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{row}">
          <el-tag>{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="leagues" label="联赛" width="150">
        <template #default="{row}">
          <el-tag v-for="league in row.leagues.slice(0,2)" 
                  :key="league" size="small" class="league-tag">
            {{ league }}
          </el-tag>
          <span v-if="row.leagues.length > 2">等{{ row.leagues.length }}个</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="success_rate" label="健康度" width="120">
        <template #default="{row}">
          <div class="health-indicator">
            <el-progress 
              :percentage="row.success_rate" 
              :status="getHealthStatus(row.success_rate)"
              :stroke-width="8"
              :width="80"
            />
            <span class="rate-text">{{ row.success_rate }}%</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="last_crawl_time" label="最后采集" width="180">
        <template #default="{row}">
          {{ formatTime(row.last_crawl_time) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{row}">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" @click="handleTest(row)">测试</el-button>
          <el-dropdown @command="handleCommand($event, row)">
            <el-button size="small">
              更多<i class="el-icon-arrow-down"></i>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logs">查看日志</el-dropdown-item>
                <el-dropdown-item command="enable" 
                  v-if="!row.is_active">启用</el-dropdown-item>
                <el-dropdown-item command="disable" 
                  v-if="row.is_active">停用</el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <span style="color: #f56c6c;">删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
    
    <!-- 创建/编辑对话框 -->
    <SourceFormDialog
      v-model="formDialogVisible"
      :source="currentSource"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import SourceFormDialog from './SourceFormDialog.vue'

// 状态管理
const sources = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 搜索和筛选
const searchQuery = ref('')
const filterType = ref('')
const filterLeague = ref('')

// 加载数据
const loadSources = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      type: filterType.value,
      league: filterLeague.value,
      search: searchQuery.value
    }
    const response = await api.get('/sources', { params })
    sources.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('加载数据源失败')
  } finally {
    loading.value = false
  }
}

// 健康度状态判断
const getHealthStatus = (rate) => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'exception'
}
</script>