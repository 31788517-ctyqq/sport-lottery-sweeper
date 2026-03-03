<template>
  <div class="department-management-container morandi-page um-page">
    <el-row :gutter="16">
      <el-col :xs="24" :lg="9">
        <el-card class="morandi-card dept-tree-card">
          <template #header>
            <div class="card-header">
              <span>组织架构</span>
              <div class="header-actions">
                <el-button type="primary" size="small" @click="handleCreateDept">新增部门</el-button>
                <el-button size="small" :loading="loadingDepts" @click="refreshData">刷新</el-button>
              </div>
            </div>
          </template>

          <div class="dept-tree-container">
            <el-tree
              v-loading="loadingDepts"
              :data="departmentTree"
              node-key="id"
              :props="treeProps"
              :expand-on-click-node="false"
              :highlight-current="true"
              @node-click="handleNodeClick"
            >
              <template #default="{ data }">
                <div class="tree-node">
                  <div class="tree-node-left">
                    <span>{{ data.name }}</span>
                    <el-tag size="small" type="info">{{ data.userCount || 0 }}人</el-tag>
                  </div>
                  <div class="tree-node-actions">
                    <el-button type="primary" size="small" text @click.stop="handleEditDept(data)">编辑</el-button>
                    <el-button type="danger" size="small" text @click.stop="handleDeleteDept(data)">删除</el-button>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="15">
        <el-card class="morandi-card dept-detail-card">
          <template #header>
            <div class="card-header">
              <span v-if="selectedDept">部门详情 - {{ selectedDept.name }}</span>
              <span v-else>部门详情</span>
              <div v-if="selectedDept" class="header-actions">
                <el-button type="primary" :loading="saving" @click="handleSaveDept">保存</el-button>
                <el-button @click="handleResetDept">重置</el-button>
              </div>
            </div>
          </template>

          <template v-if="selectedDept">
            <div class="dept-detail-content">
              <el-form ref="deptFormRef" :model="selectedDept" :rules="deptRules" label-width="100px" class="form-panel">
                <el-form-item label="部门名称" prop="name">
                  <el-input v-model="selectedDept.name" placeholder="请输入部门名称" />
                </el-form-item>
                <el-form-item label="上级部门">
                  <el-tree-select
                    v-model="selectedDept.parentId"
                    :data="departmentOptions"
                    :props="treeSelectProps"
                    placeholder="可选"
                    check-strictly
                    clearable
                  />
                </el-form-item>
                <el-form-item label="部门负责人">
                  <el-select v-model="selectedDept.managerId" placeholder="可选" clearable filterable>
                    <el-option
                      v-for="user in managerUsers"
                      :key="user.id"
                      :label="user.realName || user.username"
                      :value="user.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="排序">
                  <el-input-number
                    v-model="selectedDept.sortOrder"
                    :min="0"
                    :max="9999"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item label="状态">
                  <el-radio-group v-model="selectedDept.status">
                    <el-radio :value="true">启用</el-radio>
                    <el-radio :value="false">停用</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="描述">
                  <el-input v-model="selectedDept.description" type="textarea" :rows="3" placeholder="请输入部门描述" />
                </el-form-item>
              </el-form>

              <div class="section-title">
                <span>部门成员（{{ deptUsers.length }}）</span>
                <el-button type="primary" size="small" @click="handleAddMembers">添加成员</el-button>
              </div>

              <el-table v-loading="loadingMembers" :data="deptUsers" size="small" max-height="320">
                <el-table-column prop="realName" label="姓名" min-width="120" />
                <el-table-column prop="username" label="用户名" min-width="120" />
                <el-table-column prop="email" label="邮箱" min-width="180" />
                <el-table-column prop="phone" label="手机号" min-width="120" />
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button type="danger" size="small" text @click="handleRemoveMember(row)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>

              <div class="section-title">
                <span>子部门（{{ childDepts.length }}）</span>
              </div>
              <div class="child-tags">
                <el-tag
                  v-for="dept in childDepts"
                  :key="dept.id"
                  class="child-tag"
                  @click="setSelectedDeptById(dept.id)"
                >
                  {{ dept.name }}
                </el-tag>
                <span v-if="childDepts.length === 0" class="empty-tip">暂无子部门</span>
              </div>
            </div>
          </template>

          <el-empty v-else description="请在左侧选择一个部门查看详情" />
        </el-card>
      </el-col>
    </el-row>

    <DeptEditDialog
      v-model="showDeptDialog"
      :dept-data="currentDept"
      :department-tree="departmentOptions"
      :managers="managerUsers"
      @submit="handleDeptSubmit"
    />

    <AddMembersDialog
      v-model="showAddMembersDialog"
      :department-id="selectedDeptId"
      :exclude-user-ids="deptUsers.map((user) => user.id)"
      @submit="handleMembersSubmit"
    />
  </div>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import AddMembersDialog from '@/components/admin/AddMembersDialog.vue'
import DeptEditDialog from '@/components/admin/DeptEditDialog.vue'
import {
  addDepartmentMembers,
  createDepartment,
  deleteDepartment,
  getDepartmentMembers,
  getDepartmentStats,
  getDepartments,
  removeDepartmentMember,
  updateDepartment
} from '@/api/modules/departments'
import { getUsers } from '@/api/modules/users'

const loadingDepts = ref(false)
const loadingMembers = ref(false)
const saving = ref(false)

const departmentTree = ref([])
const flatDepartments = ref([])
const managerUsers = ref([])
const deptUsers = ref([])

const selectedDeptId = ref(null)
const selectedDept = ref(null)
const selectedDeptOrigin = ref(null)

const showDeptDialog = ref(false)
const currentDept = ref({})
const showAddMembersDialog = ref(false)

const deptFormRef = ref(null)

const treeProps = { children: 'children', label: 'name' }
const treeSelectProps = { children: 'children', label: 'name', value: 'id' }

const deptRules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应在 2 到 50 个字符之间', trigger: 'blur' }
  ]
}

const normalizeStatus = (value) => {
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value === 1
  if (typeof value === 'string') {
    const lowered = value.toLowerCase()
    return lowered === 'active' || lowered === 'true' || lowered === '1'
  }
  return true
}

const normalizeDepartmentNode = (node) => ({
  id: Number(node.id),
  name: node.name || '',
  parentId: node.parentId ?? node.parent_id ?? null,
  managerId: node.managerId ?? node.leader_id ?? null,
  sortOrder: Number(node.sortOrder ?? node.sort_order ?? 0),
  description: node.description || '',
  status: normalizeStatus(node.status),
  userCount: Number(node.userCount ?? node.user_count ?? 0),
  children: Array.isArray(node.children) ? node.children.map(normalizeDepartmentNode) : []
})

const flattenTree = (nodes, acc = []) => {
  nodes.forEach((node) => {
    acc.push(node)
    if (node.children?.length) flattenTree(node.children, acc)
  })
  return acc
}

const cloneDepartment = (dept) => JSON.parse(JSON.stringify(dept))

const selectedDeptDescendantIds = computed(() => {
  const ids = new Set()
  if (!selectedDeptId.value) return ids

  const walk = (parentId) => {
    flatDepartments.value.forEach((node) => {
      if (node.parentId === parentId && !ids.has(node.id)) {
        ids.add(node.id)
        walk(node.id)
      }
    })
  }

  walk(selectedDeptId.value)
  return ids
})

const departmentOptions = computed(() => {
  const mapTreeOptions = (nodes) =>
    nodes.map((node) => ({
      ...node,
      disabled: node.id === selectedDeptId.value || selectedDeptDescendantIds.value.has(node.id),
      children: node.children?.length ? mapTreeOptions(node.children) : []
    }))

  return mapTreeOptions(departmentTree.value)
})

const childDepts = computed(() => {
  if (!selectedDeptId.value) return []
  return flatDepartments.value.filter((dept) => dept.parentId === selectedDeptId.value)
})

const isCircularReference = computed(() => {
  if (!selectedDept.value || !selectedDept.value.parentId) return false
  let parentId = selectedDept.value.parentId
  while (parentId) {
    if (parentId === selectedDeptId.value) return true
    const parent = flatDepartments.value.find((dept) => dept.id === parentId)
    parentId = parent?.parentId
  }
  return false
})

const normalizeUser = (row) => ({
  ...row,
  id: Number(row.id),
  realName: row.realName || row.real_name || row.username || `用户${row.id}`,
  username: row.username || '',
  email: row.email || '',
  phone: row.phone || ''
})

const deptToPayload = (dept) => ({
  name: dept.name,
  parent_id: dept.parentId ?? null,
  description: dept.description || '',
  leader_id: dept.managerId ?? null,
  sort_order: Number(dept.sortOrder || 0),
  status: !!dept.status
})

const parseDepartmentRows = (response) => {
  const payload = response?.data ?? response
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload)) return payload
  return []
}

const parseDepartmentStats = (response) => {
  const payload = response?.data ?? response
  const stats = payload?.data ?? payload ?? {}
  return stats?.department_user_counts || stats?.departmentUserCounts || {}
}

const applyDepartmentUserCounts = (nodes, countsMap) =>
  nodes.map((node) => {
    const countValue = countsMap?.[node.id] ?? countsMap?.[String(node.id)]
    const nextNode = {
      ...node,
      userCount: Number.isFinite(Number(countValue)) ? Number(countValue) : Number(node.userCount || 0)
    }

    if (Array.isArray(node.children) && node.children.length) {
      nextNode.children = applyDepartmentUserCounts(node.children, countsMap)
    }

    return nextNode
  })

const parseMemberRows = (response) => {
  const payload = response?.data ?? response
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload?.items)) return payload.items
  if (Array.isArray(payload)) return payload
  return []
}

const loadDepartments = async (keepSelection = true) => {
  loadingDepts.value = true
  try {
    const [response, statsResponse] = await Promise.all([
      getDepartments({ tree: true }),
      getDepartmentStats().catch((error) => {
        console.warn('加载部门人数统计失败，使用默认值:', error)
        return null
      })
    ])
    const rawRows = parseDepartmentRows(response).map(normalizeDepartmentNode)
    const countMap = parseDepartmentStats(statsResponse)
    const rows = applyDepartmentUserCounts(rawRows, countMap)
    departmentTree.value = rows
    flatDepartments.value = flattenTree(rows, [])

    if (flatDepartments.value.length === 0) {
      selectedDeptId.value = null
      selectedDept.value = null
      selectedDeptOrigin.value = null
      deptUsers.value = []
      return
    }

    const targetId =
      keepSelection && selectedDeptId.value && flatDepartments.value.some((dept) => dept.id === selectedDeptId.value)
        ? selectedDeptId.value
        : flatDepartments.value[0].id
    await setSelectedDeptById(targetId)
  } catch (error) {
    console.error('鍔犺浇閮ㄩ棬澶辫触:', error)
    ElMessage.error('加载部门失败，请检查接口状态')
    departmentTree.value = []
    flatDepartments.value = []
    selectedDeptId.value = null
    selectedDept.value = null
    selectedDeptOrigin.value = null
    deptUsers.value = []
  } finally {
    loadingDepts.value = false
  }
}

const loadManagerUsers = async () => {
  try {
    const pageSize = 100
    let page = 1
    let pages = 1
    const allRows = []

    while (page <= pages) {
      const response = await getUsers({ page, size: pageSize, status: 'active' })
      const payload = response?.data ?? response
      const rows = Array.isArray(payload?.items) ? payload.items : []
      allRows.push(...rows)
      pages = Number(payload?.pages || 1)
      page += 1
    }

    managerUsers.value = allRows.map(normalizeUser)
  } catch (error) {
    console.error('加载用户失败:', error)
    managerUsers.value = []
  }
}

const loadDeptMembers = async () => {
  if (!selectedDeptId.value) {
    deptUsers.value = []
    return
  }
  loadingMembers.value = true
  try {
    const response = await getDepartmentMembers(selectedDeptId.value, { skip: 0, limit: 500 })
    deptUsers.value = parseMemberRows(response).map(normalizeUser)
  } catch (error) {
    console.error('鍔犺浇閮ㄩ棬鎴愬憳澶辫触:', error)
    ElMessage.error('鍔犺浇閮ㄩ棬鎴愬憳澶辫触')
    deptUsers.value = []
  } finally {
    loadingMembers.value = false
  }
}

const setSelectedDeptById = async (deptId) => {
  const target = flatDepartments.value.find((dept) => dept.id === Number(deptId))
  if (!target) return
  selectedDeptId.value = target.id
  selectedDept.value = cloneDepartment(target)
  selectedDeptOrigin.value = cloneDepartment(target)
  await loadDeptMembers()
}

const handleNodeClick = async (node) => {
  await setSelectedDeptById(node.id)
}

const handleCreateDept = () => {
  currentDept.value = {
    parentId: selectedDeptId.value ?? null,
    managerId: null,
    sortOrder: 0,
    status: true,
    description: ''
  }
  showDeptDialog.value = true
}

const handleEditDept = (dept) => {
  currentDept.value = cloneDepartment(dept)
  showDeptDialog.value = true
}

const handleDeptSubmit = async (formData) => {
  try {
    if (formData.id) {
      await updateDepartment(formData.id, deptToPayload(formData))
      ElMessage.success('閮ㄩ棬鏇存柊鎴愬姛')
      showDeptDialog.value = false
      await loadDepartments(true)
      return
    }

    await createDepartment(deptToPayload(formData))
    ElMessage.success('閮ㄩ棬鍒涘缓鎴愬姛')
    showDeptDialog.value = false
    await loadDepartments(false)
  } catch (error) {
    console.error('淇濆瓨閮ㄩ棬澶辫触:', error)
    ElMessage.error('淇濆瓨閮ㄩ棬澶辫触')
  }
}

const handleSaveDept = async () => {
  if (!selectedDept.value || !selectedDeptId.value) return
  if (isCircularReference.value) {
    ElMessage.warning('上级部门设置会形成循环，请修改后再保存')
    return
  }
  try {
    await deptFormRef.value?.validate()
    saving.value = true
    await updateDepartment(selectedDeptId.value, deptToPayload(selectedDept.value))
    ElMessage.success('淇濆瓨鎴愬姛')
    await loadDepartments(true)
  } catch (error) {
    if (error !== false) {
      console.error('淇濆瓨澶辫触:', error)
      ElMessage.error('淇濆瓨澶辫触')
    }
  } finally {
    saving.value = false
  }
}

const handleResetDept = () => {
  if (!selectedDeptOrigin.value) return
  selectedDept.value = cloneDepartment(selectedDeptOrigin.value)
}

const handleDeleteDept = async (dept) => {
  try {
    await ElMessageBox.confirm(`确定删除部门“${dept.name}”？此操作不可恢复。`, '删除确认', {
      type: 'warning'
    })
    await deleteDepartment(dept.id)
    ElMessage.success('鍒犻櫎鎴愬姛')

    if (selectedDeptId.value === dept.id) {
      selectedDeptId.value = null
      selectedDept.value = null
      selectedDeptOrigin.value = null
      deptUsers.value = []
    }
    await loadDepartments(false)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('鍒犻櫎澶辫触:', error)
      ElMessage.error('鍒犻櫎澶辫触')
    }
  }
}

const handleAddMembers = () => {
  if (!selectedDeptId.value) {
    ElMessage.warning('璇峰厛閫夋嫨閮ㄩ棬')
    return
  }
  showAddMembersDialog.value = true
}

const handleMembersSubmit = async ({ userIds }) => {
  if (!selectedDeptId.value || !Array.isArray(userIds) || !userIds.length) return
  try {
    await addDepartmentMembers(selectedDeptId.value, userIds)
    ElMessage.success('鎴愬憳娣诲姞鎴愬姛')
    showAddMembersDialog.value = false
    await loadDeptMembers()
    await loadDepartments(true)
  } catch (error) {
    console.error('娣诲姞鎴愬憳澶辫触:', error)
    ElMessage.error('娣诲姞鎴愬憳澶辫触')
  }
}

const handleRemoveMember = async (user) => {
  if (!selectedDeptId.value) return
  try {
    await ElMessageBox.confirm(`确定将“${user.realName || user.username}”移出该部门吗？`, '移除确认', {
      type: 'warning'
    })
    await removeDepartmentMember(selectedDeptId.value, user.id)
    ElMessage.success('绉婚櫎鎴愬姛')
    await loadDeptMembers()
    await loadDepartments(true)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('绉婚櫎澶辫触:', error)
      ElMessage.error('绉婚櫎澶辫触')
    }
  }
}

const refreshData = async () => {
  await Promise.all([loadDepartments(true), loadManagerUsers()])
}

onMounted(async () => {
  await Promise.all([loadDepartments(false), loadManagerUsers()])
})
</script>

<style scoped>
.morandi-page {
  --m-bg: #f5f7fa;
  --m-card: #ffffff;
  --m-border: #ebeef5;
  --m-head: #ffffff;
  --m-text: #303133;
  --m-subtext: #909399;
}

.department-management-container {
  min-height: calc(100vh - 110px);
  padding: 20px;
  background: var(--m-bg);
}

.morandi-card {
  border: 1px solid var(--m-border);
  border-radius: 4px;
  box-shadow: none;
  background: var(--m-card);
}

.morandi-card :deep(.el-card__header) {
  background: var(--m-head);
  border-bottom: 1px solid var(--m-border);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--m-text);
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.tree-node {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 12px;
  padding-right: 6px;
}

.tree-node-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.tree-node-left > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-node-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.tree-node-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.dept-tree-container :deep(.el-tree-node) {
  width: 100%;
}

.dept-tree-container :deep(.el-tree-node__content) {
  min-height: 40px;
  padding: 4px 0;
}

.form-panel {
  padding: 12px 0;
}

.section-title {
  margin: 14px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--m-text);
  font-weight: 600;
}

.child-tags {
  min-height: 36px;
}

.child-tag {
  margin-right: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}

.empty-tip {
  color: var(--m-subtext);
}

@media (max-width: 992px) {
  .department-management-container {
    padding: 12px;
  }
}
</style>


