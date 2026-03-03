<template>
  <div class="user-list-container">
    <el-card class="users-card">
      <template #header>
        <div class="card-header">
          <h3>用户列表</h3>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新增用户
            </el-button>
            <el-button type="success" :loading="importing" @click="handleImport">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
            <el-button @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和控制区域 -->
      <div class="users-controls">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6" :lg="4">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名、邮箱或姓名"
              clearable
              class="search-input"
            />
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="3">
            <el-select
              v-model="filters.status"
              placeholder="状态筛选"
              clearable
              class="status-selector"
            >
              <el-option label="全部状态" value="" />
              <el-option label="正常" value="active" />
              <el-option label="禁用" value="inactive" />
              <el-option label="锁定" value="locked" />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="3">
            <el-select
              v-model="filters.departmentId"
              placeholder="部门筛选"
              clearable
              class="dept-selector"
            >
              <el-option label="全部部门" value="" />
              <el-option 
                v-for="dept in departments" 
                :key="dept.id"
                :label="dept.name" 
                :value="dept.id" 
              />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="3">
            <el-select
              v-model="filters.roleValue"
              placeholder="角色筛选"
              clearable
              class="role-selector"
            >
              <el-option label="全部角色" value="" />
              <el-option 
                v-for="role in roleFilterOptions"
                :key="role.value"
                :label="role.label"
                :value="role.value"
              />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="24" :md="9" :lg="9">
            <el-button type="primary" @click="handleSearch" class="action-btn">
              查询
            </el-button>
            <el-button @click="handleReset" class="action-btn">
              重置
            </el-button>
            <el-button type="info" @click="refreshData" class="action-btn">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 操作按钮区域 -->
      <div class="action-bar">
        <div class="bulk-actions">
          <el-button 
            v-if="selectedUsers.length > 0"
            type="danger" 
            @click="handleBatchDisable"
          >
            批量禁用 ({{ selectedUsers.length }})
          </el-button>
          <el-button 
            v-if="selectedUsers.length > 0"
            type="warning" 
            @click="handleBatchEnable"
          >
            批量启用 ({{ selectedUsers.length }})
          </el-button>
          <el-button 
            v-if="selectedUsers.length > 0"
            type="primary" 
            @click="handleBatchAssignRole"
          >
            批量分配角色
          </el-button>
        </div>
        <div class="view-actions">
          <div class="density-switch">
            <span class="density-label">表格密度</span>
            <el-radio-group v-model="tableDensity" size="small" @change="handleDensityChange">
              <el-radio-button label="small">紧凑</el-radio-button>
              <el-radio-button label="default">标准</el-radio-button>
              <el-radio-button label="large">宽松</el-radio-button>
            </el-radio-group>
          </div>
          <el-popover placement="bottom-end" trigger="click" width="220">
            <template #reference>
              <el-button class="column-config-trigger" size="small">
                <el-icon><SetUp /></el-icon>
                列显示配置
              </el-button>
            </template>
            <div class="column-config-popover">
              <div class="column-config-title">显示列</div>
              <el-checkbox-group v-model="visibleColumnKeys" @change="handleVisibleColumnsChange">
                <el-checkbox
                  v-for="column in allColumns"
                  :key="column.key"
                  :label="column.key"
                >
                  {{ column.label }}
                </el-checkbox>
              </el-checkbox-group>
              <div class="column-config-actions">
                <el-button text size="small" @click="resetColumnVisibility">恢复默认</el-button>
              </div>
            </div>
          </el-popover>
        </div>
      </div>

      <!-- 表格区域 -->
      <div class="table-wrapper">
        <el-table
          :data="tableData" 
          stripe 
          style="width: 100%" 
          v-loading="loading"
          :size="tableDensity"
          height="calc(100vh - 380px)"
          :header-cell-style="{background: '#f5f7fa', color: '#606266'}"
          class="modern-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column v-if="isColumnVisible('username')" prop="username" label="用户名" width="120" />
          <el-table-column v-if="isColumnVisible('realName')" prop="realName" label="姓名" width="100" />
          <el-table-column v-if="isColumnVisible('email')" prop="email" label="邮箱" width="180" />
          <el-table-column v-if="isColumnVisible('phone')" prop="phone" label="手机号" width="130" />
          <el-table-column v-if="isColumnVisible('departmentName')" prop="departmentName" label="部门" width="120">
            <template #default="scope">
              {{ scope.row.departmentName || '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('roleNames')" prop="roleNames" label="角色" width="150">
            <template #default="scope">
              <el-tag  
                v-for="role in getDisplayRoleNames(scope.row)" 
                :key="role"
                size="small"
                style="margin-right: 4px; margin-bottom: 2px;"
              >
                {{ role }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('status')" prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isColumnVisible('lastLoginTime')" prop="lastLoginTime" label="最后登录" width="160">
            <template #default="scope">
              {{ formatDate(scope.row.lastLoginTime) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="scope">
              <div class="op-actions">
                <el-button type="primary" size="small" @click="handleView(scope.row.id)">
                  查看
                </el-button>
                <el-button type="warning" size="small" @click="handleEdit(scope.row.id)">
                  编辑
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="handleToggleStatus(scope.row)"
                  :disabled="scope.row.username === 'admin'"
                >
                  {{ scope.row.status === 'active' ? '禁用' : '启用' }}
                </el-button>
              </div>
            </template>
          </el-table-column>
          <template #empty>
            <div class="table-empty-state">
              <el-empty :description="emptyState.description">
                <el-button
                  v-if="emptyState.actionText"
                  type="primary"
                  link
                  @click="handleEmptyAction"
                >
                  {{ emptyState.actionText }}
                </el-button>
              </el-empty>
            </div>
          </template>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <input
      ref="importInputRef"
      class="import-file-input"
      type="file"
      accept=".csv,text/csv"
      style="display: none"
      @change="handleImportFileChange"
    />

    <!-- 用户详情/编辑对话框 -->
    <UserDetailDialog 
      v-model="showUserDialog"
      :mode="dialogMode"
      :user-id="currentUserId"
      @saved="handleUserSaved"
      @closed="handleDialogClosed"
    />

    <!-- 批量分配角色对话框 -->
    <BatchAssignRoleDialog
      v-model="showBatchRoleDialog"
      :selected-user-ids="selectedUsers"
      :roles="roles"
      @submit="handleRolesAssigned"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Refresh, SetUp } from '@element-plus/icons-vue'
import UserDetailDialog from '@/components/admin/UserDetailDialog.vue'
import BatchAssignRoleDialog from '@/components/admin/BatchAssignRoleDialog.vue'
import { getUsers, disableUsers, enableUsers, exportUsers, batchAssignRoles, importUsers } from '@/api/modules/users'
import { getDepartments } from '@/api/modules/departments'
import { getRoles } from '@/api/modules/roles'

const USER_LIST_VIEW_STATE_KEY = 'admin_user_list_view_state_v1'
const SEARCH_DEBOUNCE_MS = 450
const DEFAULT_VISIBLE_COLUMNS = ['username', 'realName', 'email', 'phone', 'departmentName', 'roleNames', 'status', 'lastLoginTime']
const ROLE_VALUE_ALIAS_MAP = Object.freeze({
  super_admin: 'super_admin',
  admin: 'admin',
  moderator: 'moderator',
  auditor: 'auditor',
  operator: 'operator',
  '超级管理员': 'super_admin',
  '管理员': 'admin',
  '版主': 'moderator',
  '审计员': 'auditor',
  '运营员': 'operator'
})
const ROLE_LABEL_FALLBACK = Object.freeze({
  super_admin: '超级管理员',
  admin: '管理员',
  moderator: '版主',
  auditor: '审计员',
  operator: '运营员'
})

const allColumns = [
  { key: 'username', label: '用户名' },
  { key: 'realName', label: '姓名' },
  { key: 'email', label: '邮箱' },
  { key: 'phone', label: '手机号' },
  { key: 'departmentName', label: '部门' },
  { key: 'roleNames', label: '角色' },
  { key: 'status', label: '状态' },
  { key: 'lastLoginTime', label: '最后登录' }
]

const tableData = ref([])
const departments = ref([])
const roles = ref([])
const loading = ref(false)
const loadError = ref('')
const searchKeyword = ref('')
const selectedUsers = ref([])
const showUserDialog = ref(false)
const showBatchRoleDialog = ref(false)
const dialogMode = ref('view') // 'view' | 'edit' | 'create'
const currentUserId = ref(null)
const importInputRef = ref(null)
const importing = ref(false)
const tableDensity = ref('default')
const visibleColumnKeys = ref([...DEFAULT_VISIBLE_COLUMNS])
let searchDebounceTimer = null

const filters = reactive({
  status: '',
  departmentId: '',
  roleValue: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
  pages: 0
})

const normalizeRoleValue = (roleRecord) => {
  const raw = roleRecord?.value ?? roleRecord?.role ?? roleRecord?.code ?? roleRecord?.key ?? roleRecord?.name ?? roleRecord?.label
  if (raw === undefined || raw === null) return ''
  const token = String(raw).trim()
  if (!token) return ''
  return ROLE_VALUE_ALIAS_MAP[token] || ROLE_VALUE_ALIAS_MAP[token.toLowerCase()] || token.toLowerCase()
}

const normalizeRoleLabel = (roleRecord, normalizedValue) => {
  const raw = roleRecord?.label ?? roleRecord?.display_name ?? roleRecord?.displayName ?? roleRecord?.name_cn ?? roleRecord?.name
  const token = String(raw || '').trim()
  if (token) {
    const alias = ROLE_LABEL_FALLBACK[token.toLowerCase()]
    return alias || token
  }
  return ROLE_LABEL_FALLBACK[normalizedValue] || normalizedValue || '-'
}

const roleFilterOptions = computed(() => {
  const options = []
  const seen = new Set()

  for (const role of roles.value) {
    const value = normalizeRoleValue(role)
    if (!value || seen.has(value)) continue
    seen.add(value)
    options.push({
      value,
      label: normalizeRoleLabel(role, value)
    })
  }

  // 兜底：角色接口异常时，至少支持按当前列表角色筛选
  if (options.length === 0) {
    for (const user of tableData.value) {
      const value = normalizeRoleValue({ value: user.role })
      if (!value || seen.has(value)) continue
      seen.add(value)
      options.push({
        value,
        label: user.roleLabel || ROLE_LABEL_FALLBACK[value] || value
      })
    }
  }

  return options
})

const hasActiveFilters = computed(() =>
  Boolean(searchKeyword.value.trim() || filters.status || filters.departmentId || filters.roleValue)
)

const emptyState = computed(() => {
  if (loadError.value) {
    return {
      description: `加载失败：${loadError.value}`,
      actionText: '重新加载',
      action: 'retry'
    }
  }
  if (hasActiveFilters.value) {
    return {
      description: '未找到匹配用户，请调整筛选条件后重试',
      actionText: '清空筛选',
      action: 'reset'
    }
  }
  return {
    description: '暂无用户数据，可先新增用户或导入 CSV',
    actionText: '刷新数据',
    action: 'refresh'
  }
})

const isColumnVisible = (columnKey) => visibleColumnKeys.value.includes(columnKey)

const persistViewState = () => {
  if (typeof window === 'undefined') return
  const state = {
    searchKeyword: searchKeyword.value,
    filters: {
      status: filters.status,
      departmentId: filters.departmentId,
      roleValue: filters.roleValue
    },
    pagination: {
      page: pagination.page,
      size: pagination.size
    },
    tableDensity: tableDensity.value,
    visibleColumnKeys: visibleColumnKeys.value
  }
  window.localStorage.setItem(USER_LIST_VIEW_STATE_KEY, JSON.stringify(state))
}

const restoreViewState = () => {
  if (typeof window === 'undefined') return
  const raw = window.localStorage.getItem(USER_LIST_VIEW_STATE_KEY)
  if (!raw) return

  try {
    const state = JSON.parse(raw)
    if (typeof state.searchKeyword === 'string') searchKeyword.value = state.searchKeyword
    if (state.filters && typeof state.filters === 'object') {
      filters.status = typeof state.filters.status === 'string' ? state.filters.status : ''
      filters.departmentId = typeof state.filters.departmentId === 'string' ? state.filters.departmentId : ''
      filters.roleValue = typeof state.filters.roleValue === 'string' ? state.filters.roleValue : ''
    }
    if (state.pagination && typeof state.pagination === 'object') {
      pagination.page = Number.isFinite(Number(state.pagination.page)) ? Math.max(1, Number(state.pagination.page)) : 1
      pagination.size = Number.isFinite(Number(state.pagination.size)) ? Math.max(1, Number(state.pagination.size)) : 20
    }
    if (['small', 'default', 'large'].includes(state.tableDensity)) {
      tableDensity.value = state.tableDensity
    }
    if (Array.isArray(state.visibleColumnKeys)) {
      const validKeys = state.visibleColumnKeys.filter((key) => allColumns.some((column) => column.key === key))
      visibleColumnKeys.value = validKeys.length > 0 ? [...new Set(validKeys)] : [...DEFAULT_VISIBLE_COLUMNS]
    }
  } catch (error) {
    console.warn('恢复用户列表状态失败，已忽略:', error)
  }
}

const clearSearchDebounce = () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
}

const queueDebouncedSearch = () => {
  clearSearchDebounce()
  searchDebounceTimer = setTimeout(() => {
    pagination.page = 1
    persistViewState()
    loadUsers()
  }, SEARCH_DEBOUNCE_MS)
}

const handleVisibleColumnsChange = (keys) => {
  if (!Array.isArray(keys) || keys.length === 0) {
    visibleColumnKeys.value = ['username']
  } else {
    visibleColumnKeys.value = [...new Set(keys)]
  }
  persistViewState()
}

const resetColumnVisibility = () => {
  visibleColumnKeys.value = [...DEFAULT_VISIBLE_COLUMNS]
  persistViewState()
}

const handleDensityChange = () => {
  persistViewState()
}

const handleEmptyAction = () => {
  if (emptyState.value.action === 'retry') {
    loadUsers()
    return
  }
  if (emptyState.value.action === 'reset') {
    handleReset()
    return
  }
  refreshData()
}

// 加载用户列表
const loadUsers = async ({ allowRoleFallback = true } = {}) => {
  loading.value = true
  loadError.value = ''
  try {
    const selectedDepartment = departments.value.find((dept) => dept.id === Number(filters.departmentId))
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchKeyword.value?.trim() || '',
      status: filters.status,
      departmentName: selectedDepartment?.name || '',
      roleValue: filters.roleValue
    }
    
    const response = await getUsers(params)
    if (response && response.data) {
      tableData.value = response.data.items || []
      pagination.total = response.data.total || 0
      pagination.pages = response.data.pages || 0
      persistViewState()
    }
  } catch (error) {
    const statusCode = Number(error?.response?.status || 0)
    if (allowRoleFallback && statusCode === 422 && filters.roleValue) {
      const invalidRole = filters.roleValue
      filters.roleValue = ''
      persistViewState()
      ElMessage.warning(`角色筛选值 "${invalidRole}" 与当前接口不兼容，已自动清空`)
      await loadUsers({ allowRoleFallback: false })
      return
    }

    tableData.value = []
    pagination.total = 0
    pagination.pages = 0
    loadError.value = error?.response?.data?.detail || error?.message || '请求失败'
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 加载部门列表
const loadDepartments = async () => {
  try {
    const response = await getDepartments({ tree: false })
    const payload = response?.data ?? response
    const rows = Array.isArray(payload?.data) ? payload.data : Array.isArray(payload) ? payload : []
    departments.value = rows.map((item) => ({
      id: Number(item.id),
      name: item.name || ''
    }))
  } catch (error) {
    console.error('加载部门列表失败:', error)
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await getRoles({ status: 'active' })
    const payload = response?.data ?? response
    const rows = Array.isArray(payload?.items)
      ? payload.items
      : Array.isArray(payload?.data)
        ? payload.data
        : Array.isArray(payload)
          ? payload
          : []
    roles.value = rows

    if (filters.roleValue && !roleFilterOptions.value.some((item) => item.value === filters.roleValue)) {
      filters.roleValue = ''
      persistViewState()
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  clearSearchDebounce()
  pagination.page = 1
  persistViewState()
  loadUsers()
}

// 重置
const handleReset = () => {
  clearSearchDebounce()
  searchKeyword.value = ''
  filters.status = ''
  filters.departmentId = ''
  filters.roleValue = ''
  pagination.page = 1
  persistViewState()
  loadUsers()
}

// 表格多选处理
const handleSelectionChange = (selection) => {
  selectedUsers.value = selection.map(item => item.id)
}

// 分页大小改变
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  persistViewState()
  loadUsers()
}

// 分页
const handlePageChange = (page) => {
  pagination.page = page
  persistViewState()
  loadUsers()
}

// 刷新数据
const refreshData = () => {
  loadUsers()
  loadDepartments()
  loadRoles()
}

// 查看用户
const handleView = (userId) => {
  currentUserId.value = userId
  dialogMode.value = 'view'
  showUserDialog.value = true
}

// 编辑用户
const handleEdit = (userId) => {
  currentUserId.value = userId
  dialogMode.value = 'edit'
  showUserDialog.value = true
}

// 新建用户
const handleCreate = () => {
  currentUserId.value = null
  dialogMode.value = 'create'
  showUserDialog.value = true
}

// 切换用户状态
const handleToggleStatus = async (user) => {
  const newStatus = user.status === 'active' ? 'inactive' : 'active'
  const actionText = newStatus === 'active' ? '启用' : '禁用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${actionText}用户 "${user.username}" 吗？`,
      `确认${actionText}`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (newStatus === 'active') {
      await enableUsers([user.id])
    } else {
      await disableUsers([user.id])
    }
    
    ElMessage.success(`${actionText}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${actionText}失败:`, error)
      ElMessage.error(`${actionText}失败`)
    }
  }
}

// 批量禁用
const handleBatchDisable = async () => {
  if (selectedUsers.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要禁用选中的 ${selectedUsers.value.length} 个用户吗？`,
      '确认批量禁用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await disableUsers(selectedUsers.value)
    ElMessage.success('批量禁用成功')
    selectedUsers.value = []
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量禁用失败:', error)
      ElMessage.error('批量禁用失败')
    }
  }
}

// 批量启用
const handleBatchEnable = async () => {
  if (selectedUsers.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要启用选中的 ${selectedUsers.value.length} 个用户吗？`,
      '确认批量启用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await enableUsers(selectedUsers.value)
    ElMessage.success('批量启用成功')
    selectedUsers.value = []
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量启用失败:', error)
      ElMessage.error('批量启用失败')
    }
  }
}

// 批量分配角色
const handleBatchAssignRole = () => {
  if (selectedUsers.value.length === 0) return
  showBatchRoleDialog.value = true
}

// 导入用户
const handleImport = () => {
  if (importing.value) return
  importInputRef.value?.click()
}

const formatImportErrorMessage = (errors = []) => {
  if (!Array.isArray(errors) || errors.length === 0) return ''
  const lines = errors.slice(0, 5).map((item) => {
    const line = item?.line ?? '-'
    const reason = item?.reason || item?.error || '未知错误'
    return `第 ${line} 行: ${reason}`
  })
  if (errors.length > 5) {
    lines.push(`... 其余 ${errors.length - 5} 条错误请查看导入文件`)
  }
  return lines.join('\n')
}

const handleImportFileChange = async (event) => {
  const file = event?.target?.files?.[0]
  if (!file) return

  const resetFileInput = () => {
    if (importInputRef.value) {
      importInputRef.value.value = ''
    }
  }

  if (!file.name.toLowerCase().endsWith('.csv')) {
    ElMessage.warning('仅支持 CSV 文件导入')
    resetFileInput()
    return
  }

  try {
    importing.value = true
    const response = await importUsers(file)
    const payload = response?.data || {}
    const totalRows = Number(payload.total_rows || 0)
    const importedCount = Number(payload.imported_count || 0)
    const skippedCount = Number(payload.skipped_count || 0)
    const defaultPasswordCount = Number(payload.default_password_count || 0)
    const errors = Array.isArray(payload.errors) ? payload.errors : []

    let message = `导入完成：总计 ${totalRows} 行，成功 ${importedCount} 行，跳过 ${skippedCount} 行`
    if (defaultPasswordCount > 0) {
      message += `，其中 ${defaultPasswordCount} 行使用默认密码`
    }

    if (errors.length > 0) {
      const details = formatImportErrorMessage(errors)
      await ElMessageBox.alert(`${message}\n\n错误明细:\n${details}`, '导入结果', {
        confirmButtonText: '知道了',
        type: 'warning'
      })
    } else {
      ElMessage.success(message)
    }

    await loadUsers()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error(error?.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
    resetFileInput()
  }
}

// 导出用户
const handleExport = () => {
  const selectedDepartment = departments.value.find((dept) => dept.id === Number(filters.departmentId))
  exportUsers({
    search: searchKeyword.value?.trim() || undefined,
    status: filters.status || undefined,
    department: selectedDepartment?.name || undefined,
    role: filters.roleValue || undefined
  }).catch((error) => {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  })
}

// 用户保存回调
const handleUserSaved = () => {
  loadUsers()
}

// 对话框关闭回调
const handleDialogClosed = () => {
  currentUserId.value = null
}

// 角色分配完成回调
const handleRolesAssigned = async (payload) => {
  try {
    await batchAssignRoles(payload)
    ElMessage.success('批量分配角色成功')
    showBatchRoleDialog.value = false
    selectedUsers.value = []
    await loadUsers()
  } catch (error) {
    console.error('批量分配角色失败:', error)
    ElMessage.error('批量分配角色失败')
  }
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    active: '正常',
    inactive: '禁用',
    locked: '锁定'
  }
  return statusMap[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const tagTypeMap = {
    active: 'success',
    inactive: 'danger',
    locked: 'warning'
  }
  return tagTypeMap[status] || 'info'
}

const getDisplayRoleNames = (row) => {
  if (Array.isArray(row.roleNames) && row.roleNames.length > 0) {
    return row.roleNames
  }
  if (row.roleLabel) {
    return [row.roleLabel]
  }
  if (row.role) {
    return [row.role]
  }
  return ['-']
}

restoreViewState()

watch(searchKeyword, () => {
  persistViewState()
  queueDebouncedSearch()
})

watch(
  () => [filters.status, filters.departmentId, filters.roleValue],
  () => {
    persistViewState()
  }
)

watch(
  () => [pagination.page, pagination.size],
  () => {
    persistViewState()
  }
)

watch(tableDensity, () => {
  persistViewState()
})

watch(
  () => visibleColumnKeys.value,
  () => {
    persistViewState()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  clearSearchDebounce()
})

onMounted(async () => {
  await loadDepartments()
  await loadRoles()
  await loadUsers()
})
</script>

<style scoped>
.user-list-container {
  --m-bg: #eef1f3;
  --m-card: #f7f8f9;
  --m-border: #d8dde2;
  --m-head: #e8ecef;
  --m-text: #405063;
  --m-subtext: #7d8792;
  padding: 16px;
  background: radial-gradient(circle at 20% 20%, #f3f6f7 0, var(--m-bg) 48%, #e9edef 100%);
  min-height: calc(100vh - 110px);
}

.users-card {
  border-radius: 14px;
  border: 1px solid var(--m-border);
  box-shadow: 0 6px 18px rgba(101, 114, 130, 0.1);
  background: var(--m-card);
}

.users-card :deep(.el-card__header) {
  background: var(--m-head);
  border-bottom: 1px solid var(--m-border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--m-text);
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.users-controls {
  padding: 16px;
  background: #f9fbfc;
  border-bottom: 1px solid var(--m-border);
}

.search-input {
  width: 100%;
}

.status-selector,
.dept-selector,
.role-selector {
  width: 100%;
}

.action-bar {
  padding: 12px 16px;
  background: #f9fbfc;
  border-bottom: 1px solid var(--m-border);
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.bulk-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.view-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.density-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.density-label {
  font-size: 12px;
  color: var(--m-subtext);
}

.column-config-popover {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.column-config-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--m-text);
}

.column-config-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}

.action-btn {
  border-radius: 8px;
}

.table-wrapper {
  padding: 0;
}

.modern-table {
  border-radius: 0 0 14px 14px;
}

.modern-table :deep(th.el-table__cell) {
  background: #edf1f4 !important;
  color: var(--m-text);
  font-weight: 600;
}

.op-actions {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
}

.op-actions .el-button + .el-button {
  margin-left: 0;
}

.table-empty-state {
  padding: 28px 0;
}

.pagination-wrapper {
  padding: 16px;
  background: #f9fbfc;
  border-top: 1px solid var(--m-border);
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .user-list-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .users-controls .el-col {
    margin-bottom: 10px;
  }

  .view-actions {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
  }
}
</style>
