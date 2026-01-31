<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">源配置</span>
        <div>
          <el-button type="primary" size="small" @click="openForm()">新增配置</el-button>
          <el-button type="success" size="small" @click="importConfig" style="margin-left: 10px;">导入配置</el-button>
          <el-upload
            :http-request="handleFileUpload"
            :show-file-list="false"
            accept=".json,.yaml,.yml,.py,.txt"
            style="display: inline-block; margin-left: 10px;">
            <el-button type="warning" size="small">导入文件</el-button>
          </el-upload>
          <el-button type="info" size="small" @click="exportConfig" style="margin-left: 10px;">导出配置</el-button>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="config_type" label="类型" width="100" />
        <el-table-column prop="config_format" label="格式" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.config_format || 'json' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.version }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="openVersionHistory(scope.row)">版本历史</el-button>
            <el-button size="small" @click="openForm(scope.row)">编辑</el-button>
            <el-button size="small" @click="testConnection(scope.row.id)" :loading="testingIds.includes(scope.row.id)">测试连接</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 配置编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="formTitle" width="800px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.config_type" placeholder="请选择配置类型">
            <el-option label="全局" value="global" />
            <el-option label="单源" value="single" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置格式">
          <el-select v-model="form.config_format" placeholder="请选择配置格式">
            <el-option label="JSON" value="json" />
            <el-option label="Python" value="python" />
            <el-option label="YAML" value="yaml" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置内容">
          <el-input 
            v-if="form.config_format === 'python'"
            v-model="form.contentValue" 
            type="textarea" 
            :rows="15" 
            placeholder='请输入 Python 爬虫脚本，例如：
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")' />
          <el-input 
            v-else
            v-model="form.contentValue" 
            type="textarea" 
            :rows="12" 
            placeholder='请输入 JSON 配置，例如：
{
  "headers": {
    "User-Agent": "Mozilla/5.0...",
    "Accept": "application/json"
  },
  "timeout": 30,
  "retry_times": 3
}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- 版本历史对话框 -->
    <el-dialog v-model="versionDialogVisible" title="配置版本历史" width="70%">
      <el-table :data="versionHistory" border>
        <el-table-column prop="version" label="版本号" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="rollbackToVersion(scope.row)">回滚至此版本</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="versionDialogVisible=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { 
  getConfigs, 
  createConfig, 
  updateConfig, 
  deleteConfig, 
  getConfigVersions, 
  rollbackConfig, 
  exportConfigs, 
  importConfigs,
  testConnection as apiTestConnection
} from '@/api/crawlerConfig'

const tableData = ref([])
const dialogVisible = ref(false)
const versionDialogVisible = ref(false)
const versionHistory = ref([])
const currentConfigId = ref(null)
const testingIds = ref([])

const form = reactive({ 
  id: null, 
  name: '', 
  config_type: 'global', 
  config_format: 'json',
  contentValue: '' 
})
let isEdit = false

const formTitle = computed(() => isEdit ? '编辑配置' : '新增配置')

const loadData = async () => {
  const res = await getConfigs()
  tableData.value = res.data || []
}

const openForm = (row = null) => {
  if (row) {
    isEdit = true
    form.id = row.id
    form.name = row.name
    form.config_type = row.config_type
    form.config_format = row.config_format || 'json'
    
    // 根据格式设置内容值
    if (form.config_format === 'python' || form.config_format === 'yaml') {
      form.contentValue = typeof row.content === 'object' 
        ? JSON.stringify(row.content, null, 2) 
        : String(row.content)
    } else {
      form.contentValue = JSON.stringify(row.content, null, 2)
    }
  } else {
    isEdit = false
    form.id = null
    form.name = ''
    form.config_type = 'global'
    form.config_format = 'json'
    form.contentValue = ''
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    let contentObj;
    
    // 根据配置格式处理内容
    if (form.config_format === 'json') {
      contentObj = JSON.parse(form.contentValue)
    } else {
      // 对于Python或YAML格式，直接保存字符串
      contentObj = form.contentValue
    }
    
    const payload = { 
      name: form.name, 
      config_type: form.config_type,
      config_format: form.config_format,
      content: contentObj,
      version: Date.now().toString() // 使用时间戳作为版本号
    }
    
    if (isEdit) {
      await updateConfig(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createConfig(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error('提交配置时出错:', e)
    if (form.config_format === 'json') {
      ElMessage.error('JSON 格式错误或请求失败')
    } else {
      ElMessage.error('配置内容格式错误或请求失败')
    }
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该配置吗？', '提示', { type: 'warning' })
    await deleteConfig(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    // 用户取消操作
  }
}

const openVersionHistory = async (row) => {
  currentConfigId.value = row.id
  try {
    const res = await getConfigVersions(row.id)
    versionHistory.value = res.data || []
  } catch (error) {
    // 如果API未实现，使用模拟数据
    versionHistory.value = [
      { id: 1, version: 'v1.0.0', created_at: '2024-01-01 10:00:00', description: '初始版本' },
      { id: 2, version: 'v1.1.0', created_at: '2024-01-02 15:30:00', description: '添加了代理配置' },
      { id: 3, version: 'v1.2.0', created_at: '2024-01-03 09:15:00', description: '更新了请求头' },
      { id: 4, version: row.version, created_at: row.updated_at, description: '当前版本' }
    ]
    ElMessage.warning('版本历史API暂未实现，显示模拟数据')
  }
  versionDialogVisible.value = true
}

const rollbackToVersion = async (versionRow) => {
  try {
    await ElMessageBox.confirm(`确定要回滚到版本 ${versionRow.version} 吗？`, '警告', { type: 'warning' })
    await rollbackConfig(currentConfigId.value, versionRow.version)
    ElMessage.success(`已回滚到版本 ${versionRow.version}`)
    versionDialogVisible.value = false
    loadData()
  } catch (error) {
    // 用户取消操作或回滚失败
    if (error !== 'cancel') {
      ElMessage.error('回滚失败')
    }
  }
}

const importConfig = () => {
  ElMessageBox.prompt('请输入配置名称', '导入配置', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.+/,
    inputErrorMessage: '配置名称不能为空'
  }).then(({ value }) => {
    // 默认提供一个Python爬虫示例
    const pythonExample = `import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 目标网址
url = 'https://trade.500.com/jczq/'

# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    # 1. 发起请求
    print(f"正在抓取页面：{url}")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # 检查请求是否成功
    response.encoding = 'utf-8'  # 设置编码
    
    # 2. 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. 准备一个列表来存储所有比赛
    all_matches = []
    current_date = None  # 用于追踪当前正在解析的日期
    
    # 4. 遍历页面中的所有表格行
    for row in soup.find_all('tr'):
        # 查找日期行：包含"收起"和日期文字的tr
        if '收起' in row.get_text():
            # 尝试从文本中提取日期，例如"收起 2026-01-23 星期五"
            text_parts = row.get_text(strip=True).split()
            for part in text_parts:
                if '-' in part and part.count('-') == 2:  # 简单的日期格式判断
                    current_date = part
                    print(f"发现赛程日期：{current_date}")
                    break
            continue  # 日期行本身不是比赛，跳过
        
        # 检查当前行是否是比赛行（比赛行通常有特定的class或结构）
        # 这里我们通过检查是否有"场次编号"样式的td来判定
        match_cells = row.find_all('td')
        if len(match_cells) >= 8:  # 比赛数据行通常有较多的td单元格
            try:
                # 提取关键数据
                # 第1个td：场次编号，如"周五002"
                match_number = match_cells[0].get_text(strip=True) if match_cells[0] else ''
                
                # 第2个td：联赛名称，如"亚青赛"
                league = match_cells[1].get_text(strip=True) if match_cells[1] else ''
                
                # 第3个td：比赛时间，如"01-23 23:00"
                match_time_str = match_cells[2].get_text(strip=True) if match_cells[2] else ''
                # 将时间字符串转换为完整的日期时间
                if current_date and match_time_str:
                    full_time_str = f"{current_date.split('-')[0]}-{match_time_str}"  # 如"2026-01-23 23:00"
                else:
                    full_time_str = f"{current_date} {match_time_str}" if current_date else match_time_str
                
                # 第4个td：比赛队伍（可能包含排名信息）
                teams_cell = match_cells[3]
                teams_text = teams_cell.get_text(strip=True) if teams_cell else ''
                
                # 如果队伍文本为空，则可能球队名在内部的span标签里
                if not teams_text and teams_cell.find('span'):
                    teams_text = teams_cell.find('span').get_text(strip=True)
                
                # 第5个td：让球数，如"0"，"-1"，"+1"
                handicap = match_cells[4].get_text(strip=True) if len(match_cells) > 4 else ''
                
                # 第6,7,8个td：胜、平、负的赔率
                win_odds = match_cells[5].get_text(strip=True) if len(match_cells) > 5 else ''
                draw_odds = match_cells[6].get_text(strip=True) if len(match_cells) > 6 else ''
                lose_odds = match_cells[7].get_text(strip=True) if len(match_cells) > 7 else ''
                
                # 构建比赛信息字典
                match_info = {
                    '日期': current_date,
                    '场次': match_number,
                    '联赛': league,
                    '比赛时间': full_time_str,
                    '对战队伍': teams_text,
                    '让球': handicap,
                    '胜赔': win_odds,
                    '平赔': draw_odds,
                    '负赔': lose_odds
                }
                
                # 只添加包含基本信息的有效比赛（避免空行）
                if match_number and league:
                    all_matches.append(match_info)
                    
            except Exception as e:
                # 如果某行解析出错，跳过并继续
                continue
    
    # 5. 数据处理与保存
    if all_matches:
        print(f"\\n成功抓取到 {len(all_matches)} 场比赛！")
        
        # 转换为DataFrame以便查看和保存
        df_matches = pd.DataFrame(all_matches)
        
        # 按日期和场次排序
        if '日期' in df_matches.columns and '场次' in df_matches.columns:
            df_matches = df_matches.sort_values(['日期', '场次'])
        
        # 显示前几行数据
        print("\\n前10场比赛预览：")
        print(df_matches.head(10).to_string(index=False))
        
        # 保存到CSV文件
        filename = f'jczq_schedule_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df_matches.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\\n所有赛程已保存到文件：{filename}")
        
        # 按日期统计比赛数量
        if '日期' in df_matches.columns:
            print("\\n各日期比赛数量统计：")
            date_stats = df_matches['日期'].value_counts().sort_index()
            for date, count in date_stats.items():
                print(f"  {date}: {count} 场")
    else:
        print("未在页面中找到比赛数据，请检查页面结构或选择器。")

except requests.exceptions.RequestException as e:
    print(f"网络请求出错：{e}")
except Exception as e:
    print(f"程序执行过程中出错：{e}")

print("\\n程序执行完毕！")`
    
    form.name = value
    form.config_type = 'single'
    form.config_format = 'python'
    form.contentValue = pythonExample
    isEdit = false
    dialogVisible.value = true
    ElMessage.success('Python爬虫示例已加载，请根据需要修改')
  }).catch(() => {
    // 用户取消操作
  })
}

const exportConfig = async () => {
  try {
    const res = await exportConfigs()
    // 创建并下载文件
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `crawler_configs_${new Date().toISOString().slice(0, 19)}.json`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElNotification({
      title: '导出成功',
      message: '配置已导出到文件',
      type: 'success'
    })
  } catch (error) {
    // 如果API未实现，使用浏览器原生导出
    const blob = new Blob([JSON.stringify(tableData.value, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `crawler_configs_${new Date().toISOString().slice(0, 19)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElNotification({
      title: '导出成功',
      message: '配置已导出到文件（使用浏览器原生功能）',
      type: 'success'
    })
  }
}

const handleFileUpload = async ({ file }) => {
  try {
    // 创建 FormData 对象用于上传文件
    const formData = new FormData()
    formData.append('file', file)
    
    // 调用导入API
    await importConfigs(formData)
    ElMessage.success('配置文件上传成功')
    loadData() // 重新加载数据
  } catch (error) {
    // 如果API未实现，使用简单的文本导入
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target.result
        // 根据文件扩展名确定格式
        let format = 'json'
        if (file.name.endsWith('.py')) {
          format = 'python'
        } else if (file.name.endsWith('.yaml') || file.name.endsWith('.yml')) {
          format = 'yaml'
        }
        
        form.config_format = format
        form.contentValue = content
        form.name = file.name.replace(/\.[^/.]+$/, "") // 去掉扩展名作为配置名
        
        ElMessage.success(`${format.toUpperCase()}配置文件读取成功，请在表单中查看`)
      } catch (parseError) {
        ElMessage.error('配置文件格式错误')
      }
    }
    reader.readAsText(file)
  }
}

const testConnection = async (id) => {
  testingIds.value.push(id)
  try {
    await apiTestConnection(id)
    ElMessage.success('连接测试成功')
  } catch (error) {
    ElMessage.error('连接测试失败')
  } finally {
    testingIds.value = testingIds.value.filter(item => item !== id)
  }
}

loadData()
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.card-header {
  font-weight: bold;
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>