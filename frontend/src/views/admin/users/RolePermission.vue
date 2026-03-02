<template>
  <div class="role-permission-container">
    <!-- 角色等级说明 -->
    <el-card class="role-level-guide" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <h3>📋 角色等级体系</h3>
        </div>
      </template>
      <div class="role-levels-grid">
        <div v-for="(level, idx) in roleLevels" :key="idx" class="level-item">
          <div :class="['level-badge', `level-${level.value}`]">L{{ level.value }}</div>
          <div class="level-info">
            <div class="level-name">{{ level.name }}</div>
            <div class="level-desc">{{ level.description }}</div>
          </div>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <el-card class="roles-card">
          <template #header>
            <div class="card-header">
              <h3>角色管理</h3>
              <el-button type="primary" size="small" @click="handleCreateRole">
                <el-icon><Plus /></el-icon>
                新建角色
              </el-button>
            </div>
          </template>

          <div class="roles-search">
            <el-input
              v-model="roleSearchKeyword"
              placeholder="搜索角色名称"
              clearable
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <div class="roles-list">
            <div
              v-for="role in filteredRoles"
              :key="role.id"
              class="role-item"
              :class="{ active: selectedRole?.id === role.id }"
              @click="selectRole(role)"
            >
              <div class="role-info">
                <div class="role-name">
                  {{ role.name }}
                  <el-tag v-if="role.is_system" size="small" type="info" style="margin-left: 8px;">系统</el-tag>
                  <el-tag 
                    v-if="role.level" 
                    :class="['level-tag', `level-${role.level}`]"
                    style="margin-left: 4px;"
                  >
                    {{ getRoleLevelName(role.level) }}
                  </el-tag>
                </div>
                <div class="role-desc">{{ role.description || '-' }}</div>
              </div>
              <div class="role-actions">
                <el-button type="primary" size="small" text @click.stop="handleEditRole(role)">编辑</el-button>
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click.stop="handleDeleteRole(role)"
                  :disabled="role.is_system || role.name === '超级管理员'"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="16">
        <el-card class="permissions-card">
          <template #header>
            <div class="card-header" v-if="selectedRole">
              <h3>权限配置 - {{ selectedRole.name }}</h3>
              <div class="header-actions">
                <el-button type="primary" @click="handleSavePermissions" :loading="saving">保存权限</el-button>
                <el-button @click="handleResetPermissions">重置</el-button>
              </div>
            </div>
            <div v-else class="card-header">
              <h3>权限配置</h3>
              <span class="tip-text">请先选择一个角色</span>
            </div>
          </template>

          <div v-if="selectedRole" class="permissions-content">
            <div class="permission-tree">
              <el-tree
                ref="permissionTreeRef"
                :data="permissionTree"
                show-checkbox
                node-key="id"
                :props="treeProps"
                :default-checked-keys="selectedRole.permissions"
                :check-strictly="false"
                class="modern-tree"
              >
                <template #default="{ node, data }">
                  <div class="tree-node">
                    <span class="node-label">{{ node.label }}</span>
                    <span v-if="data.description" class="node-desc">{{ data.description }}</span>
                  </div>
                </template>
              </el-tree>
            </div>

            <div class="permission-help">
              <h4>权限说明</h4>
              <ul>
                <li><strong>勾选权限</strong>：为该角色分配对应权限</li>
                <li><strong>父子权限</strong>：勾选父权限会自动选中子权限</li>
                <li><strong>系统角色</strong>：系统内置角色不可删除</li>
                <li><strong>权限生效</strong>：保存后立即生效</li>
              </ul>
            </div>
          </div>

          <div v-else class="no-selection">
            <el-empty description="请选择一个角色进行权限配置" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <RoleEditDialog
      v-model="showRoleDialog"
      :role-data="currentRole"
      :permission-tree="permissionTree"
      @submit="handleRoleSubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import RoleEditDialog from '@/components/admin/RoleEditDialog.vue'
import { getRoles, createRole, updateRole, deleteRole } from '@/api/modules/roles'
import { getPermissions } from '@/api/modules/permissions'

// 角色等级配置
const roleLevels = [
  { value: 5, name: '超级管理员', description: '系统所有者 - 所有权限' },
  { value: 4, name: '管理员', description: '部门带头人 - 大部分管理权限' },
  { value: 3, name: '审计员', description: '合规监督者 - 查看日志和报表' },
  { value: 2, name: '运营员', description: '日常执行者 - 数据维护和执行权限' },
  { value: 1, name: '观察者', description: '只读用户 - 只读访问权限' },
]

const roles = ref([])
const permissionTree = ref([])
const selectedRole = ref(null)
const roleSearchKeyword = ref('')
const saving = ref(false)
const showRoleDialog = ref(false)
const roleDialogMode = ref('create')
const currentRole = ref({})
const permissionTreeRef = ref(null)

const treeProps = {
  children: 'children',
  label: 'name'
}

const filteredRoles = computed(() => {
  if (!roleSearchKeyword.value) return roles.value
  const key = roleSearchKeyword.value.toLowerCase()
  return roles.value.filter((role) =>
    (role.name || '').toLowerCase().includes(key) ||
    (role.description || '').toLowerCase().includes(key)
  )
})

const normalizePermissions = (input) => (input || []).map((p) => (typeof p === 'object' ? p.id : p))

const getRoleLevelName = (level) => {
  const levelObj = roleLevels.find(l => l.value === level)
  return levelObj ? `${levelObj.name} (L${level})` : `L${level}`
}

const loadRoles = async () => {
  try {
    // 移除status过滤，加载所有角色看看有哪些
    const response = await getRoles({})
    const payload = response?.data ?? response
    roles.value = Array.isArray(payload) ? payload : []
    if (roles.value.length > 0 && !selectedRole.value) {
      selectRole(roles.value[0])
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

const loadPermissions = async () => {
  try {
    const response = await getPermissions({ tree: true })
    const payload = response?.data ?? response
    const rows = Array.isArray(payload) ? payload : []
    if (rows.length > 0 && rows[0]?.children) {
      permissionTree.value = rows
    } else {
      const map = new Map()
      const tree = []
      rows.forEach((p) => map.set(p.id, { ...p, children: [] }))
      rows.forEach((p) => {
        const node = map.get(p.id)
        if (p.parentId && map.has(p.parentId)) map.get(p.parentId).children.push(node)
        else tree.push(node)
      })
      permissionTree.value = tree
    }
  } catch (error) {
    console.error('加载权限列表失败:', error)
    ElMessage.error('加载权限列表失败')
  }
}

const selectRole = (role) => {
  selectedRole.value = {
    ...role,
    permissions: normalizePermissions(role.permissions || [])
  }
}

const handleCreateRole = () => {
  roleDialogMode.value = 'create'
  currentRole.value = { level: 2 }  // 默认为运营员(L2)
  showRoleDialog.value = true
}

const handleEditRole = (role) => {
  roleDialogMode.value = 'edit'
  currentRole.value = { 
    ...role, 
    permissions: normalizePermissions(role.permissions || []) 
  }
  showRoleDialog.value = true
}

const handleDeleteRole = async (role) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色 "${role.name}" 吗？此操作不可恢复。`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteRole(role.id)
    ElMessage.success('删除成功')
    if (selectedRole.value?.id === role.id) selectedRole.value = null
    await loadRoles()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSavePermissions = async () => {
  if (!selectedRole.value || !permissionTreeRef.value) return
  try {
    saving.value = true
    const checkedKeys = permissionTreeRef.value.getCheckedKeys()
    const halfCheckedKeys = permissionTreeRef.value.getHalfCheckedKeys()
    const allCheckedKeys = [...checkedKeys, ...halfCheckedKeys]
    await updateRole(selectedRole.value.id, {
      name: selectedRole.value.name,
      description: selectedRole.value.description,
      level: selectedRole.value.level,
      is_system: selectedRole.value.is_system,
      permissions: allCheckedKeys
    })
    ElMessage.success('权限保存成功')
    await loadRoles()
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存权限失败')
  } finally {
    saving.value = false
  }
}

const handleResetPermissions = () => {
  if (selectedRole.value && permissionTreeRef.value) {
    permissionTreeRef.value.setCheckedKeys(selectedRole.value.permissions || [])
    ElMessage.info('已重置为原始权限')
  }
}

const handleRoleSubmit = async (formData) => {
  try {
    const payload = {
      name: formData.name,
      description: formData.description,
      level: formData.level,
      is_system: formData.is_system || false,
      permissions: normalizePermissions(formData.permissions)
    }
    if (roleDialogMode.value === 'edit' && currentRole.value?.id) {
      await updateRole(currentRole.value.id, payload)
      ElMessage.success('角色更新成功')
    } else {
      await createRole(payload)
      ElMessage.success('角色创建成功')
    }
    showRoleDialog.value = false
    currentRole.value = {}
    await loadRoles()
  } catch (error) {
    console.error('角色保存失败:', error)
    ElMessage.error('角色保存失败')
  }
}

onMounted(() => {
  loadRoles()
  loadPermissions()
})
</script>

<style scoped>
.role-permission-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.role-level-guide {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.role-levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.level-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 6px;
  color: white;
  font-weight: bold;
  font-size: 16px;
}

.level-badge.level-5 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.level-badge.level-4 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.level-badge.level-3 {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.level-badge.level-2 {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
}

.level-badge.level-1 {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #333;
}

.level-info {
  flex: 1;
}

.level-name {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.level-desc {
  font-size: 12px;
  color: #909399;
}

.level-tag {
  font-weight: 600;
}

.level-tag.level-5 {
  background-color: #667eea;
  color: white;
}

.level-tag.level-4 {
  background-color: #f5576c;
  color: white;
}

.level-tag.level-3 {
  background-color: #fa709a;
  color: white;
}

.level-tag.level-2 {
  background-color: #30cfd0;
  color: white;
}

.level-tag.level-1 {
  background-color: #a8edea;
  color: #333;
}

.roles-card,
.permissions-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.card-header h3 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.tip-text {
  color: #909399;
  font-size: 14px;
}

.roles-search {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
}

.roles-list {
  max-height: 600px;
  overflow-y: auto;
}

.role-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.role-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.role-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
  border-width: 2px;
}

.role-info {
  flex: 1;
  min-width: 0;
}

.role-name {
  font-weight: 600;
  margin-bottom: 4px;
  color: #303133;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.role-desc {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role-actions {
  display: flex;
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
}

.permissions-content {
  display: grid;
  gap: 16px;
}

.permission-tree {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 12px;
  max-height: 420px;
  overflow: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-size: 14px;
  font-weight: 500;
}

.node-desc {
  color: #909399;
  font-size: 12px;
}

.permission-help {
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  padding: 12px;
  background: #fafafa;
}

.permission-help h4 {
  margin: 0 0 8px;
}

.permission-help ul {
  margin: 0;
  padding-left: 18px;
  color: #606266;
}

.no-selection {
  min-height: 360px;
  display: grid;
  place-items: center;
}

@media (max-width: 1200px) {
  .role-permission-container {
    padding: 10px;
  }

  .role-levels-grid {
    grid-template-columns: 1fr;
  }
}
</style>
