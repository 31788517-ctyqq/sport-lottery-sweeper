# 中英文映射与别名关联增强方案 + 官方信息自动收录系统设计方案 + 菜单位置计划

## 1. 项目概述

本文档详细介绍了竞彩足球扫盘系统中关于实体中英文映射与别名关联增强方案、官方信息自动收录系统设计方案以及相关功能在后台管理系统的菜单位置安排。

### 1.1 项目背景

竞彩足球扫盘系统是一个专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。随着系统功能不断扩展，需要处理来自不同数据源的球队、联赛等实体信息，这些信息往往存在名称差异、多语言表达和官方渠道多样化的问题。

### 1.2 问题定义

1. **中英文映射与别名关联问题**：
   - 不同数据源对同一实体使用不同名称
   - 中英文名称不一致导致数据匹配困难
   - 缺乏标准化的实体标识符，影响数据整合

2. **官方信息收录问题**：
   - 缺乏统一的官方信息管理机制
   - 无法有效收集和验证球队/联赛的官方网站、社交媒体账号
   - 难以利用官方信息增强数据采集能力

## 2. 中英文映射与别名关联增强方案

### 2.1 设计目标

- 实现球队、联赛等实体的中英文名称标准化
- 建立多语言别名映射机制
- 提供自动化的名称匹配和转换功能
- 与现有系统无缝集成

### 2.2 数据模型设计

```python
# 球队名称映射表
TEAM_MAPPINGS = {
    "real_madrid": {
        "zh": ["皇家马德里", "皇马"],
        "en": ["Real Madrid", "RM"],
        "jp": ["レアル・マドリード"],
        "official_info": {
            "website": "https://www.realmadrid.com/",
            "twitter": "https://twitter.com/realmadrid",
            "facebook": "https://www.facebook.com/realmadrid",
            "instagram": "https://www.instagram.com/realmadrid/",
            "weibo": "https://weibo.com/realmadrid",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["RMCF", "RealMadridCF"],
            "football_data_org": ["Real Madrid Club de Fútbol"]
        }
    },
    "barcelona": {
        "zh": ["巴塞罗那", "巴萨"],
        "en": ["FC Barcelona", "Barça"],
        "jp": ["FCバルセロナ"],
        "official_info": {
            "website": "https://www.fcbarcelona.com/",
            "twitter": "https://twitter.com/fcbarcelona",
            "facebook": "https://www.facebook.com/FCBarcelona",
            "instagram": "https://www.instagram.com/fcbarcelona/",
            "weibo": "https://weibo.com/fcbarcelona",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["FCB", "Barca"],
            "football_data_org": ["Futbol Club Barcelona"]
        }
    }
    # 更多球队映射...
}

# 联赛名称映射表
LEAGUE_MAPPINGS = {
    "premier_league": {
        "zh": ["英超联赛", "英格兰超级联赛"],
        "en": ["Premier League"],
        "official_info": {
            "website": "https://www.premierleague.com/",
            "twitter": "https://twitter.com/premierleague",
            "facebook": "https://www.facebook.com/premierleague",
            "instagram": "https://www.instagram.com/premierleague/",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["EPL"],
            "football_data_org": ["English Premier League"]
        }
    },
    "la_liga": {
        "zh": ["西甲联赛", "西班牙甲级联赛"],
        "en": ["La Liga"],
        "official_info": {
            "website": "https://www.laliga.com/",
            "twitter": "https://twitter.com/laliga",
            "facebook": "https://www.facebook.com/LaLiga",
            "instagram": "https://www.instagram.com/laliga/",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["LALIGA"],
            "football_data_org": ["Primera División"]
        }
    }
    # 更多联赛映射...
}
```

### 2.3 服务层实现

```python
class MatchDataProcessor:
    def __init__(self, source_config):
        self.source_config = source_config
        self.source_id = source_config.get('source_id', 'default')
        
    def process_match_data(self, raw_data):
        # 标准化球队名称
        processed_data = {
            'home_team_id': self._normalize_team_name(raw_data.get('home_team')),
            'away_team_id': self._normalize_team_name(raw_data.get('away_team')),
            'league_id': self._normalize_league_name(raw_data.get('league')),
            # ... other fields ...
        }
        
        return processed_data
        
    def _normalize_team_name(self, team_name):
        """标准化球队名称，返回业务唯一标识符"""
        if not team_name:
            return None
            
        # 尝试精确匹配
        standard_id = get_standard_name('team', team_name, self.source_id)
        if standard_id:
            return standard_id
            
        # 尝试模糊匹配（处理拼写错误或缩写）
        for possible_match in self._fuzzy_match_candidates(team_name):
            standard_id = get_standard_name('team', possible_match, self.source_id)
            if standard_id:
                return standard_id
                
        # 无法匹配时记录日志并返回原始值
        logger.warning(f"无法标准化球队名称: {team_name} (来源: {self.source_id})")
        return team_name  # 保留原始值作为后备
        
    def _fuzzy_match_candidates(self, name):
        """生成可能的模糊匹配候选"""
        # 移除常见停用词
        cleaned = re.sub(r'\b(fc|cf|club|united)\b', '', name, flags=re.IGNORECASE)
        # 生成缩写形式
        initials = ''.join([w[0].upper() for w in re.findall(r'\w+', cleaned)])
        # 生成常见变体
        return [
            name.lower(),
            name.upper(),
            name.title(),
            initials,
            re.sub(r'[\s\-_]+', '', name)
        ]
        
    def _normalize_league_name(self, league_name):
        """标准化联赛名称，返回业务唯一标识符"""
        # 实现与_team_name类似
```

### 2.4 API接口设计

```python
@router.post("/matches/standardize")
async def standardize_match_data(
    raw_data: dict,
    source_id: str = Query(..., description="数据源标识符")
):
    """
    将原始比赛数据标准化为系统内部格式
    """
    processor = MatchDataProcessor({'source_id': source_id})
    
    try:
        # 验证必要字段
        required_fields = ['home_team', 'away_team', 'match_time']
        if not all(field in raw_data for field in required_fields):
            return JSONResponse(
                status_code=422,
                content={"error": "缺少必要字段", "missing": [f for f in required_fields if f not in raw_data]}
            )
            
        # 标准化处理
        standardized = processor.process_match_data(raw_data)
        
        # 验证标准化结果
        if not standardized.get('home_team_id') or not standardized.get('away_team_id'):
            return JSONResponse(
                status_code=400,
                content={"error": "无法识别球队名称", "data": raw_data}
            )
            
        return {"standardized_data": standardized}
        
    except Exception as e:
        logger.error(f"标准化处理失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "内部错误", "message": str(e)}
        )
```

## 3. 官方信息自动收录系统设计方案

### 3.1 设计目标

- 自动收集球队和联赛的官方网站、社交媒体账号
- 提供官方信息验证和更新机制
- 集成到现有数据采集流程中
- 为场外信息抓取提供支持

### 3.2 服务层实现

```python
class OfficialInfoService:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "SportLotterySweeper/1.0 (+https://yourdomain.com/bot)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
            }
        )
    
    async def verify_all_official_links(self, entity_type: str = "all") -> Dict[str, Any]:
        """验证所有实体的官方链接状态"""
        results = {
            "teams": {},
            "leagues": {},
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "needs_update": 0,
                "last_verified": datetime.utcnow().isoformat()
            }
        }
        
        if entity_type in ["all", "teams"]:
            for team_id, team_data in TEAM_MAPPINGS.items():
                if "official_info" in team_data:
                    verification = await self.verify_entity_official_info("team", team_id, team_data["official_info"])
                    results["teams"][team_id] = verification
                    self._update_summary(results["summary"], verification)
        
        if entity_type in ["all", "leagues"]:
            for league_id, league_data in LEAGUE_MAPPINGS.items():
                if "official_info" in league_data:
                    verification = await self.verify_entity_official_info("league", league_id, league_data["official_info"])
                    results["leagues"][league_id] = verification
                    self._update_summary(results["summary"], verification)
        
        return results
    
    async def verify_entity_official_info(self, entity_type: str, entity_id: str, official_info: Dict) -> Dict:
        """验证单个实体的官方信息"""
        verification_result = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": "valid",
            "details": {},
            "last_verified": datetime.utcnow().isoformat(),
            "verification_time": time.time()
        }
        
        for platform, url in official_info.items():
            if platform in ["verified", "last_verified"]:
                continue
                
            if not url:
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "missing",
                    "message": "无官方链接"
                }
                continue
                
            # 检查URL格式
            if not self._validate_url_format(platform, url):
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "invalid_format",
                    "message": "URL格式无效"
                }
                verification_result["status"] = "invalid"
                continue
                
            # 验证URL可达性和真实性
            try:
                result = await self._verify_platform_url(platform, url)
                verification_result["details"][platform] = result
                
                if result["status"] != "valid":
                    verification_result["status"] = "invalid"
            except Exception as e:
                logger.error(f"验证{platform}链接失败 {url}: {str(e)}", exc_info=True)
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "error",
                    "message": str(e)
                }
                verification_result["status"] = "error"
        
        return verification_result
    
    def _validate_url_format(self, platform: str, url: str) -> bool:
        """验证URL格式是否符合平台要求"""
        if platform not in PLATFORM_VALIDATION_RULES:
            # 通用URL验证
            return bool(re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/]?", url))
        
        rule = PLATFORM_VALIDATION_RULES[platform]
        return bool(re.match(rule["pattern"], url))
    
    async def _verify_platform_url(self, platform: str, url: str) -> Dict:
        """验证特定平台的URL"""
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": None,
            "redirect_url": None,
            "verification_time": time.time()
        }
        
        # 首先检查HTTP状态
        try:
            response = await self._make_request_with_retry(url)
            result["http_status"] = response.status_code
            result["redirect_url"] = str(response.url)
            
            if response.status_code != 200:
                result["status"] = "unreachable"
                result["message"] = f"HTTP状态码: {response.status_code}"
                return result
        except Exception as e:
            result["status"] = "unreachable"
            result["message"] = f"请求失败: {str(e)}"
            return result
        
        # 根据平台执行特定验证
        if platform == "website":
            return self._verify_website(response)
        elif platform == "twitter":
            return self._verify_twitter(response, url)
        elif platform == "facebook":
            return self._verify_facebook(response, url)
        elif platform == "instagram":
            return self._verify_instagram(response, url)
        elif platform == "weibo":
            return self._verify_weibo(response, url)
        
        return result
    
    async def discover_official_links(self, entity_type: str, entity_id: str) -> Dict:
        """尝试发现实体的官方链接"""
        # 实现搜索引擎查询和模式匹配逻辑
        # 这里简化实现
        results = {
            "website": None,
            "twitter": None,
            "facebook": None,
            "instagram": None,
            "weibo": None,
            "confidence": 0.0,
            "sources": []
        }
        
        # 模拟搜索引擎查询
        search_queries = [
            f"{entity_id.replace('_', ' ')} official website",
            f"{entity_id.replace('_', ' ')} twitter",
            f"{entity_id.replace('_', ' ')} facebook"
        ]
        
        # 实际应用中应调用搜索引擎API
        for query in search_queries:
            # 模拟搜索结果
            if "website" in query:
                results["website"] = f"https://www.{entity_id}.com/"
                results["confidence"] = max(results["confidence"], 0.7)
                results["sources"].append("search_engine")
            elif "twitter" in query:
                results["twitter"] = f"https://twitter.com/{entity_id}"
                results["confidence"] = max(results["confidence"], 0.6)
        
        return results
```

### 3.3 自动化任务调度

```python
@shared_task(bind=True, max_retries=3)
def verify_official_links_task(self, entity_type="all"):
    """
    验证官方链接任务
    :param entity_type: 验证类型 ('team', 'league', 'all')
    """
    try:
        logger.info(f"开始执行官方链接验证任务 (类型: {entity_type})")
        result = official_info_service.verify_all_official_links(entity_type)
        
        # 记录验证摘要
        summary = result["summary"]
        logger.info(
            f"官方链接验证完成 | 总数: {summary['total']} | "
            f"有效: {summary['valid']} | 无效: {summary['invalid']} | "
            f"需更新: {summary['needs_update']} | "
            f"最后验证: {summary['last_verified']}"
        )
        
        return {
            "status": "success",
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"官方链接验证任务失败: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@shared_task(bind=True, max_retries=3)
def discover_official_links_task(self, entity_type="all", confidence_threshold=0.6):
    """
    自动发现官方链接任务
    :param entity_type: 发现类型 ('team', 'league', 'all')
    :param confidence_threshold: 置信度阈值
    """
    try:
        logger.info(f"开始执行官方链接发现任务 (类型: {entity_type}, 置信度阈值: {confidence_threshold})")
        
        # 获取需要发现的实体列表
        from config.entity_mappings import TEAM_MAPPINGS, LEAGUE_MAPPINGS
        
        entities_to_check = []
        
        if entity_type in ["all", "teams"]:
            for team_id, team_data in TEAM_MAPPINGS.items():
                if "official_info" not in team_data or not team_data.get("official_info", {}).get("verified", False):
                    entities_to_check.append(("team", team_id))
        
        if entity_type in ["all", "leagues"]:
            for league_id, league_data in LEAGUE_MAPPINGS.items():
                if "official_info" not in league_data or not league_data.get("official_info", {}).get("verified", False):
                    entities_to_check.append(("league", league_id))
        
        results = []
        for entity_type, entity_id in entities_to_check:
            try:
                discovery = official_info_service.discover_official_links(entity_type, entity_id)
                if discovery["confidence"] >= confidence_threshold:
                    # 更新官方信息（但不自动标记为已验证）
                    updated_info = {k: v for k, v in discovery.items() if k in ["website", "twitter", "facebook", "instagram", "weibo"]}
                    updated_info["verified"] = False
                    updated_info["discovery_source"] = "auto_discovery"
                    updated_info["discovery_time"] = datetime.utcnow().isoformat()
                    
                    official_info_service.update_official_info(entity_type, entity_id, updated_info)
                    results.append({
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "status": "updated",
                        "confidence": discovery["confidence"]
                    })
            except Exception as e:
                logger.error(f"发现{entity_type} {entity_id}官方链接失败: {str(e)}", exc_info=True)
                results.append({
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"官方链接发现任务完成 | 成功: {len([r for r in results if r['status'] == 'updated'])} | 失败: {len([r for r in results if r['status'] == 'error'])}")
        return {
            "status": "success",
            "total": len(entities_to_check),
            "updated": len([r for r in results if r['status'] == 'updated']),
            "errors": len([r for r in results if r['status'] == 'error']),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"官方链接发现任务失败: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

# 定期任务调度配置
CELERY_BEAT_SCHEDULE = {
    'daily-official-links-verification': {
        'task': 'backend.tasks.official_info_tasks.verify_official_links_task',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点执行
        'args': ('all',)
    },
    'weekly-official-links-discovery': {
        'task': 'backend.tasks.official_info_tasks.discover_official_links_task',
        'schedule': crontab(day_of_week=0, hour=3, minute=30),  # 每周日3:30执行
        'args': ('all', 0.6)
    }
}
```

## 4. 菜单位置计划

根据**后台管理系统菜单架构与融合规范**(memory id="72db7209-6a69-468e-9661-102fcf0bbb9d")，我们将新功能融合到现有菜单中，而不是创建新的主菜单。

### 4.1 中英文映射与别名关联功能

- **主菜单**: 系统管理
- **子菜单**: 实体映射管理
- **路径**: `/admin/system/entity-mappings`
- **组件**: `@/views/admin/system/EntityMappings.vue`
- **权限**: ['admin', 'manager']
- **图标**: `map-location`

**实现方式**:
1. 在`frontend/src/router/modules/system-routes.js`中添加新路由
2. 创建`EntityMappings.vue`组件，提供映射管理界面
3. 集成到系统管理菜单中

### 4.2 官方信息自动收录系统

- **主菜单**: 数据源管理
- **子菜单**: 官方信息管理
- **路径**: `/admin/data-source/official-info`
- **组件**: `@/views/admin/crawler/OfficialInfoManagement.vue`
- **权限**: ['admin', 'manager']
- **图标**: `link`

**实现方式**:
1. 在`frontend/src/router/modules/crawler-routes.js`中添加新路由
2. 创建`OfficialInfoManagement.vue`组件，提供官方信息管理界面
3. 集成到数据源管理菜单中

### 4.3 菜单结构更新

```javascript
// frontend/src/router/modules/system-routes.js
{
  path: 'system',
  name: 'SystemManagement',
  redirect: '/admin/system/config',
  meta: {
    title: '系统管理',
    icon: 'Setting',
    roles: ['admin'],
    order: 12
  },
  children: [
    // ... 现有路由 ...
    {
      path: 'entity-mappings',
      name: 'EntityMappings',
      component: () => import('@/views/admin/system/EntityMappings.vue'),
      meta: {
        title: '实体映射管理',
        icon: 'map-location',
        roles: ['admin', 'manager'],
        keepAlive: true
      }
    }
  ]
}

// frontend/src/router/modules/crawler-routes.js
{
  path: 'data-source',
  name: 'DataSourceManagement',
  redirect: '/admin/data-source/config',
  meta: {
    title: '数据源管理',
    icon: 'SetUp',
    roles: ['admin', 'manager']
  },
  children: [
    // ... 现有路由 ...
    {
      path: 'official-info',
      name: 'OfficialInfoManagement',
      component: () => import('@/views/admin/crawler/OfficialInfoManagement.vue'),
      meta: {
        title: '官方信息管理',
        icon: 'link',
        roles: ['admin', 'manager'],
        keepAlive: true
      }
    }
  ]
}
```

### 4.4 组件实现

#### 4.4.1 EntityMappings.vue 组件

```vue
<template>
  <div class="entity-mappings">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队映射" name="teams">
        <mapping-table 
          :entity-type="'team'" 
          :columns="['zh', 'en', 'source_aliases']"
          @update="handleUpdate"
        />
      </el-tab-pane>
      <el-tab-pane label="联赛映射" name="leagues">
        <mapping-table 
          :entity-type="'league'" 
          :columns="['zh', 'en', 'source_aliases']"
          @update="handleUpdate"
        />
      </el-tab-pane>
    </el-tabs>
    
    <div class="mapping-documentation">
      <h3>映射规则说明</h3>
      <ul>
        <li>业务ID格式: <code>team_[英文标识]</code> 或 <code>league_[英文标识]</code> (如 team_real_madrid)</li>
        <li>中文别名应包含常用简称和全称</li>
        <li>来源别名需指定数据源ID (如 sports_data_api)</li>
        <li>系统将自动进行模糊匹配和大小写处理</li>
      </ul>
    </div>
  </div>
</template>

<script>
import MappingTable from './components/MappingTable.vue'

export default {
  name: 'EntityMappings',
  components: { MappingTable },
  data() {
    return {
      activeTab: 'teams'
    }
  },
  methods: {
    handleUpdate(entityType, updatedData) {
      // 调用API更新映射配置
      this.$api.system.updateEntityMappings(entityType, updatedData)
        .then(() => {
          this.$message.success('映射配置已更新')
          // 通知数据处理服务刷新缓存
          this.$api.crawler.refreshMappingCache()
        })
    }
  }
}
</script>
```

#### 4.4.2 OfficialInfoManagement.vue 组件

```vue
<template>
  <div class="official-info-management">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队官方信息" name="teams">
        <entity-official-info-table 
          :entity-type="'team'"
          :columns="['website', 'twitter', 'facebook', 'instagram', 'weibo']"
          @verify="handleVerify"
          @discover="handleDiscover"
          @update="handleUpdate"
        />
      </el-tab-pane>
      <el-tab-pane label="联赛官方信息" name="leagues">
        <entity-official-info-table 
          :entity-type="'league'"
          :columns="['website', 'twitter', 'facebook', 'instagram']"
          @verify="handleVerify"
          @discover="handleDiscover"
          @update="handleUpdate"
        />
      </el-tab-pane>
    </el-tabs>
    
    <div class="verification-controls">
      <el-button type="primary" @click="handleVerifyAll">
        <el-icon><Refresh /></el-icon>
        全量验证
      </el-button>
      <el-button @click="handleDiscoverAll">
        <el-icon><Search /></el-icon>
        自动发现
      </el-button>
      <el-button @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      
      <div class="verification-status">
        <span :class="{'status-valid': verificationSummary.valid > 0}">
          有效: {{ verificationSummary.valid }}
        </span>
        <span :class="{'status-invalid': verificationSummary.invalid > 0}">
          无效: {{ verificationSummary.invalid }}
        </span>
        <span :class="{'status-warning': verificationSummary.needs_update > 0}">
          需更新: {{ verificationSummary.needs_update }}
        </span>
        <span>总数: {{ verificationSummary.total }}</span>
        <span>最后验证: {{ verificationSummary.last_verified }}</span>
      </div>
    </div>
    
    <div class="info-documentation">
      <h3>官方信息管理说明</h3>
      <ul>
        <li>官方信息用于增强场外信息抓取，提高数据完整性和准确性</li>
        <li>验证状态: 
          <span class="status-badge status-valid">有效</span>
          <span class="status-badge status-invalid">无效</span>
          <span class="status-badge status-warning">需更新</span>
        </li>
        <li>点击"自动发现"可尝试搜索可能的官方链接</li>
        <li>验证结果每30天自动标记为需更新，请定期验证</li>
        <li>社交媒体账号建议优先选择带官方认证标识的账号</li>
      </ul>
    </div>
  </div>
</template>

<script>
import EntityOfficialInfoTable from './components/EntityOfficialInfoTable.vue'
import { Refresh, Search } from '@element-plus/icons-vue'

export default {
  name: 'OfficialInfoManagement',
  components: { 
    EntityOfficialInfoTable,
    Refresh,
    Search
  },
  data() {
    return {
      activeTab: 'teams',
      verificationSummary: {
        total: 0,
        valid: 0,
        invalid: 0,
        needs_update: 0,
        last_verified: 'N/A'
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const response = await this.$api.system.getOfficialInfoSummary()
        this.verificationSummary = response.data.summary
      } catch (error) {
        this.$message.error('加载官方信息摘要失败')
      }
    },
    
    async handleVerify(entityType, entityId) {
      try {
        await this.$api.system.verifyOfficialInfo(entityType, entityId)
        this.$message.success('验证任务已提交')
        setTimeout(() => this.loadData(), 2000)
      } catch (error) {
        this.$message.error('提交验证任务失败')
      }
    },
    
    async handleDiscover(entityType, entityId) {
      try {
        await this.$api.system.discoverOfficialInfo(entityType, entityId)
        this.$message.success('发现任务已提交')
        setTimeout(() => this.loadData(), 2000)
      } catch (error) {
        this.$message.error('提交发现任务失败')
      }
    },
    
    async handleUpdate(entityType, entityId, updates) {
      try {
        await this.$api.system.updateOfficialInfo(entityType, entityId, updates)
        this.$message.success('官方信息已更新')
      } catch (error) {
        this.$message.error('更新官方信息失败')
      }
    },
    
    async handleVerifyAll() {
      try {
        await this.$api.system.verifyOfficialInfo('all')
        this.$message.success('全量验证任务已提交')
        setTimeout(() => this.loadData(), 2000)
      } catch (error) {
        this.$message.error('提交全量验证任务失败')
      }
    },
    
    async handleDiscoverAll() {
      try {
        await this.$api.system.discoverOfficialInfo('all')
        this.$message.success('全量发现任务已提交')
        setTimeout(() => this.loadData(), 2000)
      } catch (error) {
        this.$message.error('提交全量发现任务失败')
      }
    },
    
    refreshData() {
      this.loadData()
    }
  }
}
</script>
```

## 5. 实施计划

### 5.1 第一阶段：后端开发（1-2周）
- 实现实体映射配置文件
- 开发映射服务和标准化处理逻辑
- 创建官方信息验证服务
- 实现API接口

### 5.2 第二阶段：前端开发（1-2周）
- 修改路由配置文件
- 开发实体映射管理界面
- 开发官方信息管理界面
- 集成API调用

### 5.3 第三阶段：自动化任务（1周）
- 实现定时验证任务
- 实现自动发现任务
- 配置Celery调度

### 5.4 第四阶段：测试与部署（1周）
- 进行功能测试
- 进行集成测试
- 部署到生产环境

## 6. 验收标准

1. **中英文映射功能**：
   - 能够正确识别和标准化不同数据源的实体名称
   - 提供可视化管理界面，支持映射配置
   - 支持模糊匹配和别名识别

2. **官方信息收录功能**：
   - 能够自动发现和验证官方链接
   - 提供官方信息管理界面
   - 实现定期验证和更新机制

3. **菜单位置**：
   - 功能正确集成到系统管理菜单中
   - 功能正确集成到数据源管理菜单中
   - 符合项目菜单架构规范

## 7. 风险与缓解措施

1. **数据一致性风险**：使用事务确保映射配置更新的一致性
2. **性能影响风险**：实现缓存机制，避免频繁查询映射表
3. **外部依赖风险**：对官方信息验证实现超时和重试机制
4. **安全风险**：验证外部链接的安全性，防止恶意链接注入

## 8. 维护与监控

1. **监控指标**：映射成功率、验证任务执行情况、官方信息有效性
2. **日志记录**：记录映射和验证过程中的关键操作
3. **告警机制**：对验证失败或链接失效的情况发出告警
4. **定期审查**：定期审查映射配置和官方信息的有效性