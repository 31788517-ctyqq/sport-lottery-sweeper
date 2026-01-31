<template>
  <div class="role-permission-container">
    <el-row :gutter="20">
      <!-- 角色列表 -->
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
                  <el-tag v-if="role.isSystem" size="small" type="info" style="margin-left: 8px;">系统</el-tag>
                </div>
                <div class="role-desc">{{ role.description }}</div>
              </div>
              <div class="role-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  text
                  @click.stop="handleEditRole(role)"
                  :disabled="role.isSystem"
                >
                  编辑
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  text
                  @click.stop="handleDeleteRole(role)"
                  :disabled="role.isSystem || role.name === '超级管理员'"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 权限配置 -->
      <el-col :xs="24" :lg="16">
        <el-card class="permissions-card">
          <template #header>
            <div class="card-header" v-if="selectedRole">
              <h3>权限配置 - {{ selectedRole.name }}</h3>
              <div class="header-actions">
                <el-button type="primary" @click="handleSavePermissions" :loading="saving">
                  保存权限
                </el-button>
                <el-button @click="handleResetPermissions">
                  重置
                </el-button>
              </div>
            </div>
            <div v-else class="card-header">
              <h3>权限配置</h3>
              <span class="tip-text">请先选择一个角色</span>
            </div>
          </template>
          
          <div v-if="selectedRole" class="permissions-content">
            <!-- 权限树 -->
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
            
            <!-- 权限说明 -->
            <div class="permission-help">
              <h4>权限说明</h4>
              <ul>
                <li><strong>勾选权限</strong>：为该角色分配对应权限</li>
                <li><strong>父子权限</strong>：勾选父权限会自动选中所有子权限</li>
                <li><strong>系统角色</strong>：系统内置角色不可删除</li>
                <li><strong>权限生效</strong>：保存后立即生效，无需重启</li>
              </ul>
            </div>
          </div>
          
          <div v-else class="no-selection">
            <el-empty description="请选择一个角色进行权限配置" />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 角色编辑对话框 -->
    <RoleEditDialog
      v-model="showRoleDialog"
      :mode="roleDialogMode"
      :role-data="currentRole"
      @saved="handleRoleSaved"
      @closed="handleRoleDialogClosed"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import RoleEditDialog from '@/components/admin/RoleEditDialog.vue'
import { getRoles, createRole, updateRole, deleteRole } from '@/api/modules/roles'
import { getPermissions } from '@/api/modules/permissions'

const roles = ref([])
const permissions = ref([])
const permissionTree = ref([])
const selectedRole = ref(null)
const roleSearchKeyword = ref('')
const saving = ref(false)
const showRoleDialog = ref(false)
const roleDialogMode = ref('create') // 'create' | 'edit'
const currentRole = ref({})

const treeProps = {
  children: 'children',
  label: 'name'
}

// 过滤角色列表
const filteredRoles = computed(() => {
  if (!roleSearchKeyword.value) {
    return roles.value
  }
  return roles.value.filter(role => 
    role.name.toLowerCase().includes(roleSearchKeyword.value.toLowerCase()) ||
    role.description.toLowerCase().includes(roleSearchKeyword.value.toLowerCase())
  )
})

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await getRoles({ status: 'active' })
    if (response && response.data) {
      roles.value = Array.isArray(response.data) ? response.data : []
      // 默认选中第一个角色
      if (roles.value.length > 0 && !selectedRole.value) {
        selectRole(roles.value[0])
      }
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

// 加载权限列表
const loadPermissions = async () => {
  try {
    const response = await getPermissions({ tree: true })
    if (response && response.data) {
      permissions.value = Array.isArray(response.data) ? response.data : []
      permissionTree.value = buildPermissionTree(permissions.value)
    }
  } catch (error) {
    console.error('加载权限列表失败:', error)
    ElMessage.error('加载权限列表失败')
  }
}

// 构建权限树
const buildPermissionTree = (permissions) => {
  const tree = []
  const map = new Map()
  
  // 创建映射
  permissions.forEach(permission => {
    map.set(permission.id, { ...permission, children: [] })
  })
  
  // 构建树结构
  permissions.forEach(permission => {
    const node = map.get(permission.id)
    if (permission.parentId && map.has(permission.parentId)) {
      map.get(permission.parentId).children.push(node)
    } else {
      tree.push(node)
    }
  })
  
  return tree
}

// 选择角色
const selectRole = (role) => {
  selectedRole.value = { ...role, permissions: role.permissions || [] }
}

// 新建角色
const handleCreateRole = () => {
  roleDialogMode.value = 'create'
  currentRole.value = {}
  showRoleDialog.value = true
}

// 编辑角色
const handleEditRole = (role) => {
  roleDialogMode.value = 'edit'
  currentRole.value = { ...role }
  showRoleDialog.value = true
}

// 删除角色
const handleDeleteRole = async (role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteRole(role.id)
    ElMessage.success('删除成功')
    loadRoles()
    if (selectedRole.value?.id === role.id) {
      selectedRole.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 保存权限
const handleSavePermissions = async () => {
  if (!selectedRole.value) return
  
  try {
    saving.value = true
    const checkedKeys = permissionTreeRef.value.getCheckedKeys()
    const halfCheckedKeys = permissionTreeRef.value.getHalfCheckedKeys()
    const allCheckedKeys = [...checkedKeys, ...halfCheckedKeys]
    
    await updateRole(selectedRole.value.id, {
      ...selectedRole.value,
      permissions: allCheckedKeys
    })
    
    ElMessage.success('权限保存成功')
    loadRoles() // 刷新角色列表
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存权限失败')
  } finally {
    saving.value = false
  }
}

// 重置权限
const handleResetPermissions = () => {
  if (selectedRole.value) {
    permissionTreeRef.value.setCheckedKeys(selectedRole.value.permissions || [])
    ElMessage.info('已重置为原始权限')
  }
}

// 角色保存回调
const handleRoleSaved = () => {
  loadRoles()
}

// 角色对话框关闭回调
const handleRoleDialogClosed = () => {
  currentRole.value = {}
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
  background: #f0f9ff;
}

.role-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.role-info {
  flex: 1;
}

.role-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.role-desc {
  font-size: 12px;
  color: #909399;
}

.role-actions {
  display: flex;
  gap: 4px;
}

.permissions-content {
  min-height: 500px;
}

.permission-tree {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
}

.modern-tree {
  background: transparent;
}

.tree-node {
  display: flex;
  flex-direction: column;
}

.node-label {
  font-weight: 500;
}

.node-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.permission-help {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.permission-help h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.permission-help ul {
  margin: 0;
  padding-left: 20px;
}

.permission-help li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

@media (max-width: 768px) {
  .role-permission-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
}
</style>