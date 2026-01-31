<template>
  <div class="crawler-source-config">
    <!-- 新增源卡片区域 -->
    <el-card header="添加新数据源" class="add-source-card">
      <div class="add-source-content">
        <p>在此添加新的爬虫数据源</p>
        <el-button type="primary" @click="openAddDialog">新增源</el-button>
      </div>
    </el-card>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline class="filter-bar">
        <el-form-item label="源名称">
          <el-input 
            v-model="filters.name" 
            placeholder="模糊搜索" 
            clearable 
            style="width: 200px;"
          />
        </el-form-item>
        
        <el-form-item label="源ID">
          <el-input 
            v-model="filters.id" 
            placeholder="精确/前缀匹配" 
            clearable 
            style="width: 200px;"
          />
        </el-form-item>
        
        <el-form-item label="内容分类">
          <el-select 
            v-model="filters.category" 
            placeholder="请选择分类" 
            clearable 
            multiple
            collapse-tags
            style="width: 250px;"
          >
            <el-option 
              v-for="item in categoryOptions" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadSources">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据列表 -->
    <el-card class="table-card">
      <el-table 
        :data="filteredSources" 
        border 
        stripe 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editSource(row)">修改</el-button>
            <el-button size="small" type="danger" @click="deleteSource(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadSources"
          @current-change="loadSources"
        />
      </div>
    </el-card>

    <!-- 新增/编辑源 Dialog -->
    <el-dialog 
      v-model="addDialogVisible" 
      :title="isEdit ? '编辑数据源' : '新增数据源'" 
      width="800px" 
      @opened="focusNameInput"
    >
      <el-form 
        :model="sourceForm" 
        :rules="formRules" 
        ref="formRef" 
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="任务名称" prop="name">
              <el-input 
                v-model="sourceForm.name" 
                placeholder="请输入爬虫任务名称"
                ref="nameInput"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务ID">
              <el-input 
                v-model="sourceForm.id" 
                placeholder="自动生成"
                readonly 
                disabled
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="内容分类" prop="category">
          <el-select 
            v-model="sourceForm.category" 
            placeholder="请选择内容分类" 
            style="width: 100%;"
          >
            <el-option 
              v-for="item in categoryOptions" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="代码格式" prop="format">
          <el-select v-model="sourceForm.format" placeholder="请选择代码格式" @change="onFormatChange">
            <el-option label="Python" value="python" />
            <el-option label="YAML" value="yaml" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>

        <el-form-item label="预设模板" prop="presetTemplate">
          <el-select 
            v-model="sourceForm.presetTemplate" 
            placeholder="选择预设模板（可选）" 
            clearable 
            @change="onPresetChange"
          >
            <el-option 
              v-for="template in availablePresetTemplates"
              :key="template.key"
              :label="template.label"
              :value="template.key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="代码配置" prop="code">
          <div class="code-editor-container">
            <div class="editor-toolbar">
              <el-button size="small" @click="restoreDefaultTemplate">恢复默认模板</el-button>
              <span class="editor-hint">支持Tab键缩进</span>
            </div>
            <el-input
              type="textarea"
              :rows="15"
              v-model="sourceForm.code"
              placeholder="在此编辑代码配置..."
              class="code-textarea"
              ref="codeEditor"
              @keydown.tab.prevent="handleTab"
            />
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSources, createSource, deleteSource } from '@/api/crawlerConfig.js'

// 数据源列表
const sources = ref([])
const loading = ref(false)

// 筛选条件
const filters = reactive({
  name: '',
  id: '',
  category: []
})

// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 分类选项（情报分类枚举 + 足球sp）
const categoryOptions = ref([
  // 情报分类枚举
  { value: 'match_data', label: '比赛数据' },
  { value: 'team_info', label: '球队信息' },
  { value: 'player_stats', label: '球员统计' },
  { value: 'odds_analysis', label: '赔率分析' },
  { value: 'news_intel', label: '新闻情报' },
  { value: 'historical_data', label: '历史数据' },
  // 足球sp分类
  { value: 'football_sp_odds', label: '足球SP赔率' },
  { value: 'football_sp_analysis', label: '足球SP分析' },
  { value: 'football_sp_prediction', label: '足球SP预测' }
])

// 新增/编辑相关
const addDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const nameInput = ref(null)
const codeEditor = ref(null)

const sourceForm = ref({
  name: '',
  id: '',
  category: '',
  format: 'python',
  presetTemplate: '',
  code: ''
})

// 计算可用预设模板
const availablePresetTemplates = computed(() => {
  return Object.values(presetTemplates).filter(t => t.format === sourceForm.value.format)
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择内容分类', trigger: 'change' }
  ],
  format: [
    { required: true, message: '请选择代码格式', trigger: 'change' }
  ],
  code: [
    { required: true, message: '代码配置不能为空', trigger: 'blur' }
  ]
}

// 代码模板定义
const codeTemplates = {
  python: `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫任务配置
任务名称: {{name}}
分类: {{category}}
"""

import requests
from bs4 import BeautifulSoup
import json
import time

class CrawlerTask:
    def __init__(self):
        self.base_url = "{{base_url}}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.timeout = 30
        self.retries = 3
    
    def fetch_page(self, url):
        """获取页面内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None
    
    def parse_data(self, html):
        """解析数据"""
        soup = BeautifulSoup(html, 'html.parser')
        # TODO: 根据目标网站结构编写解析逻辑
        data = {
            "timestamp": time.time(),
            "source": self.base_url,
            "category": "{{category}}"
        }
        return data
    
    def run(self):
        """执行爬虫任务"""
        html = self.fetch_page(self.base_url)
        if html:
            data = self.parse_data(html)
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return data
        return None

if __name__ == "__main__":
    crawler = CrawlerTask()
    crawler.run()`,
  yaml: `# 爬虫任务配置
# 任务名称: {{name}}
# 分类: {{category}}

name: "爬虫任务"
type: "web_crawler"
version: "1.0"
category: "{{category}}"

# 目标配置
target:
  base_url: "{{base_url}}"
  encoding: "utf-8"
  timeout: 30
  retries: 3

# 请求头配置
headers:
  User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

# 抓取配置
fetch:
  method: "GET"
  delay: 1
  concurrent: 1

# 解析配置
parse:
  engine: "beautifulsoup"
  selector_type: "css"

# 输出配置
output:
  format: "json"
  file: "output_{timestamp}.json"
  pretty: true`,
  json: `{
  "name": "爬虫任务-{{name}}",
  "type": "web_crawler",
  "version": "1.0",
  "category": "{{category}}",
  "description": "爬虫任务配置文件",
  "target": {
    "base_url": "{{base_url}}",
    "encoding": "utf-8",
    "timeout": 30,
    "retries": 3
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  },
  "fetch": {
    "method": "GET",
    "delay": 1,
    "concurrent": 1
  },
  "parse": {
    "engine": "beautifulsoup",
    "selector_type": "css"
  },
  "output": {
    "format": "json",
    "file": "output_{timestamp}.json",
    "pretty": true
  }
}`
}

// 预设模板定义
const presetTemplates = {
  python_basic: {
    key: 'python_basic',
    label: 'Python - 基础爬虫',
    format: 'python',
    template: `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础爬虫模板
分类: {{category}}
"""

import requests
from bs4 import BeautifulSoup
import json

class BasicCrawler:
    def __init__(self):
        self.base_url = "https://example.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def crawl(self):
        try:
            resp = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            # TODO: 添加解析逻辑
            return {"status": "success", "category": "{{category}}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    crawler = BasicCrawler()
    result = crawler.crawl()
    print(json.dumps(result, ensure_ascii=False))`
  }
}

onMounted(() => {
  loadSources()
})

// 加载数据源列表
async function loadSources() {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize,
      ...filters
    }
    
    // 使用真实API调用
    const response = await getSources(params)
    
    if (response.code === 200) {
      sources.value = response.data
      // 如果API返回分页信息，更新分页
      if (response.pagination) {
        pagination.total = response.pagination.total
        pagination.currentPage = response.pagination.page
        pagination.pageSize = response.pagination.size
      }
      ElMessage.success(`成功加载 ${response.data.length} 个数据源`)
    } else {
      ElMessage.error(response.message || '加载数据源失败')
    }
    
    // 模拟数据已删除 - 使用真实API
    /* 示例数据结构，实际使用时删除
    {
      id: '0002',
      name: '球队信息爬虫',
      category: 'team_info',
      createTime: '2024-01-14 14:20:00',
      status: 'active'
    }*/
    
  } catch (error) {
    console.error('加载数据源失败:', error)
    ElMessage.error('网络错误或服务器无响应')
  } finally {
    loading.value = false
  }
}

// 计算属性：筛选后的数据源
const filteredSources = computed(() => {
  return sources.value.filter(item => {
    const nameOk = item.name.toLowerCase().includes((filters.name || '').toLowerCase())
    const idOk = String(item.id).includes(filters.id || '')
    const catOk = filters.category.length ? filters.category.includes(item.category) : true
    return nameOk && idOk && catOk
  })
})

// 重置筛选条件
function resetFilters() {
  filters.name = ''
  filters.id = ''
  filters.category = []
  loadSources()
}

// 打开新增对话框
function openAddDialog() {
  isEdit.value = false
  sourceForm.value = {
    name: '',
    id: generateNextId(),
    category: '',
    format: 'python',
    presetTemplate: '',
    code: codeTemplates.python
  }
  addDialogVisible.value = true
}

// 编辑数据源
function editSource(row) {
  isEdit.value = true
  sourceForm.value = {
    ...row,
    format: 'python',
    presetTemplate: '',
    code: codeTemplates.python
  }
  addDialogVisible.value = true
}

// 删除数据源
async function deleteSource(id) {
  try {
    await ElMessageBox.confirm('确定要删除此数据源吗？', '确认删除', {
      type: 'warning'
    })
    
    // 使用真实API删除数据源
    const response = await deleteSource(id)
    
    if (response.code === 200) {
      ElMessage.success('删除成功')
      await loadSources() // 重新加载列表
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 保存数据源
async function confirmSave() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          // 更新API调用
          // await axios.put(`/api/crawler-sources/${sourceForm.value.id}`, sourceForm.value)
          ElMessage.success('更新成功')
        } else {
          // 使用真实API创建数据源
          try {
            const response = await createSource(sourceForm)
            if (response.code === 200) {
              ElMessage.success('创建成功')
              addDialogVisible.value = false
              resetForm()
              await loadSources() // 重新加载列表
            } else {
              ElMessage.error(response.message || '创建失败')
            }
          } catch (error) {
            console.error('创建数据源失败:', error)
            ElMessage.error('创建失败，请检查输入信息')
          }
        }
        addDialogVisible.value = false
        loadSources()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

// 生成下一个ID
function generateNextId() {
  const numericIds = sources.value
    .map(item => parseInt(item.id))
    .filter(id => !isNaN(id))
    .sort((a, b) => a - b)
  
  let nextId = 1
  for (const id of numericIds) {
    if (id !== nextId) {
      break
    }
    nextId++
  }
  
  return nextId.toString().padStart(4, '0')
}

// 聚焦名称输入框
function focusNameInput() {
  nextTick(() => {
    nameInput.value?.focus()
  })
}

// 格式变更处理
function onFormatChange() {
  if (sourceForm.value.code && sourceForm.value.code !== codeTemplates[sourceForm.value.format]) {
    ElMessageBox.confirm(
      '切换格式将清空当前代码，是否继续？',
      '确认切换',
      {
        confirmButtonText: '继续',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      resetCodeForNewFormat()
    }).catch(() => {
      sourceForm.value.format = sourceForm.value.format === 'python' ? 'yaml' : 'python'
    })
  } else {
    resetCodeForNewFormat()
  }
}

// 重置为新格式的默认代码
function resetCodeForNewFormat() {
  const template = codeTemplates[sourceForm.value.format]
  const filledTemplate = template
    .replace(/{{name}}/g, sourceForm.value.name || '未命名任务')
    .replace(/{{category}}/g, sourceForm.value.category || '未分类')
    .replace(/{{base_url}}/g, 'https://example.com')
  
  sourceForm.value.code = filledTemplate
  sourceForm.value.presetTemplate = ''
}

// 预设模板变更
function onPresetChange(key) {
  if (key && presetTemplates[key]) {
    const template = presetTemplates[key].template
    const filledTemplate = template
      .replace(/{{name}}/g, sourceForm.value.name || '未命名任务')
      .replace(/{{category}}/g, sourceForm.value.category || '未分类')
    
    sourceForm.value.code = filledTemplate
  }
}

// 恢复默认模板
function restoreDefaultTemplate() {
  const template = codeTemplates[sourceForm.value.format]
  const filledTemplate = template
    .replace(/{{name}}/g, sourceForm.value.name || '未命名任务')
    .replace(/{{category}}/g, sourceForm.value.category || '未分类')
    .replace(/{{base_url}}/g, 'https://example.com')
  
  sourceForm.value.code = filledTemplate
}

// 处理Tab键缩进
function handleTab(event) {
  const textarea = event.target
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  
  const spaces = '    '
  sourceForm.value.code = 
    sourceForm.value.code.substring(0, start) +
    spaces +
    sourceForm.value.code.substring(end)
  
  nextTick(() => {
    textarea.selectionStart = textarea.selectionEnd = start + spaces.length
  })
}
</script>

<style scoped>
.crawler-source-config {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.add-source-card {
  margin-bottom: 20px;
}

.add-source-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.add-source-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-bar {
  margin: 0;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.code-editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-hint {
  font-size: 12px;
  color: #909399;
}

.code-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.el-card__header) {
  background-color: #fafafa;
  font-weight: bold;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-pagination) {
  font-weight: normal;
}
</style>