<template>
  <div class="department-management-container">
    <el-row :gutter="20">
      <!-- 部门树 -->
      <el-col :xs="24" :lg="8">
        <el-card class="dept-tree-card">
          <template #header>
            <div class="card-header">
              <h3>组织架构</h3>
              <div class="header-actions">
                <el-button type="primary" size="small" @click="handleCreateDept">
                  <el-icon><Plus /></el-icon>
                  新增部门
                </el-button>
                <el-button @click="refreshData">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="dept-tree-container">
            <el-tree
              ref="deptTreeRef"
              :data="departmentTree"
              node-key="id"
              :props="treeProps"
              :expand-on-click-node="false"
              :highlight-current="true"
              class="modern-tree"
              @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <span class="node-content">
                    <span class="node-icon">
                      <el-icon v-if="data.children && data.children.length > 0"><FolderOpened /></el-icon>
                      <el-icon v-else><Document /></el-icon>
                    </span>
                    <span class="node-label">{{ node.label }}</span>
                  </span>
                  <span class="node-meta">
                    <span class="user-count" v-if="data.userCount !== undefined">
                      {{ data.userCount }}人
                    </span>
                    <span class="node-actions" v-if="!data.isSystem">
                      <el-button 
                        type="primary" 
                        size="small" 
                        text
                        @click.stop="handleEditDept(data)"
                      >
                        编辑
                      </el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        text
                        @click.stop="handleDeleteDept(data)"
                      >
                        删除
                      </el-button>
                    </span>
                  </span>
                </div>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>
      
      <!-- 部门详情 -->
      <el-col :xs="24" :lg="16">
        <el-card class="dept-detail-card">
          <template #header>
            <div class="card-header" v-if="selectedDept">
              <h3>部门详情 - {{ selectedDept.name }}</h3>
              <div class="header-actions">
                <el-button type="primary" @click="handleSaveDept" :loading="saving">
                  保存修改
                </el-button>
                <el-button @click="handleResetDept">
                  重置
                </el-button>
              </div>
            </div>
            <div v-else class="card-header">
              <h3>部门详情</h3>
              <span class="tip-text">请选择左侧部门查看详情</span>
            </div>
          </template>
          
          <div v-if="selectedDept" class="dept-detail-content">
            <!-- 基本信息 -->
            <div class="detail-section">
              <h4>基本信息</h4>
              <el-form 
                ref="deptFormRef"
                :model="selectedDept" 
                :rules="deptRules"
                label-width="100px"
                class="detail-form"
              >
                <el-form-item label="部门名称" prop="name">
                  <el-input 
                    v-model="selectedDept.name" 
                    placeholder="请输入部门名称"
                    :disabled="selectedDept.isSystem"
                  />
                </el-form-item>
                
                <el-form-item label="部门编码" prop="code">
                  <el-input 
                    v-model="selectedDept.code" 
                    placeholder="请输入部门编码"
                    :disabled="selectedDept.isSystem"
                  />
                </el-form-item>
                
                <el-form-item label="上级部门">
                  <el-tree-select
                    v-model="selectedDept.parentId"
                    :data="departmentOptions"
                    :props="treeSelectProps"
                    placeholder="请选择上级部门"
                    check-strictly
                    :disabled="selectedDept.isSystem || isCircularReference"
                    clearable
                  />
                </el-form-item>
                
                <el-form-item label="部门描述">
                  <el-input
                    v-model="selectedDept.description"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入部门描述"
                  />
                </el-form-item>
                
                <el-form-item label="部门负责人">
                  <el-select
                    v-model="selectedDept.managerId"
                    placeholder="请选择负责人"
                    clearable
                    filterable
                  >
                    <el-option
                      v-for="user in deptUsers"
                      :key="user.id"
                      :label="user.realName || user.username"
                      :value="user.id"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="排序序号">
                  <el-input-number
                    v-model="selectedDept.sortOrder"
                    :min="0"
                    :max="999"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
                
                <el-form-item label="状态">
                  <el-radio-group v-model="selectedDept.status">
                    <el-radio value="active">正常</el-radio>
                    <el-radio value="inactive">停用</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </div>
            
            <!-- 部门成员 -->
            <div class="detail-section">
              <div class="section-header">
                <h4>部门成员 ({{ deptUsers.length }})</h4>
                <el-button type="primary" size="small" @click="handleAddMembers">
                  添加成员
                </el-button>
              </div>
              
              <div class="member-list">
                <div 
                  v-for="user in deptUsers" 
                  :key="user.id"
                  class="member-item"
                >
                  <div class="member-info">
                    <el-avatar :size="32" :src="user.avatar">
                      {{ (user.realName || user.username).charAt(0).toUpperCase() }}
                    </el-avatar>
                    <div class="member-details">
                      <div class="member-name">{{ user.realName || user.username }}</div>
                      <div class="member-role">{{ user.roleNames?.join(', ') || '无角色' }}</div>
                    </div>
                  </div>
                  <div class="member-actions">
                    <el-button 
                      type="danger" 
                      size="small" 
                      text
                      @click="handleRemoveMember(user)"
                    >
                      移除
                    </el-button>
                  </div>
                </div>
                
                <div v-if="deptUsers.length === 0" class="empty-members">
                  <el-empty description="暂无成员" :image-size="60" />
                </div>
              </div>
            </div>
            
            <!-- 子部门 -->
            <div class="detail-section" v-if="childDepts.length > 0">
              <h4>子部门 ({{ childDepts.length }})</h4>
              <div class="child-dept-list">
                <el-tag 
                  v-for="dept in childDepts" 
                  :key="dept.id"
                  class="child-dept-tag"
                  @click="handleNodeClick(null, dept)"
                  style="cursor: pointer; margin: 2px;"
                >
                  {{ dept.name }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <div v-else class="no-selection">
            <el-empty description="请选择一个部门查看详情" />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 部门编辑对话框 -->
    <DeptEditDialog
      v-model="showDeptDialog"
      :mode="deptDialogMode"
      :dept-data="currentDept"
      :parent-depts="departmentOptions"
      @saved="handleDeptSaved"
      @closed="handleDeptDialogClosed"
    />
    
    <!-- 添加成员对话框 -->
    <AddMembersDialog
      v-model="showAddMembersDialog"
      :dept-id="selectedDept?.id"
      :exclude-user-ids="deptUsers.map(u => u.id)"
      @added="handleMembersAdded"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, FolderOpened, Document } from '@element-plus/icons-vue'
import DeptEditDialog from '@/components/admin/DeptEditDialog.vue'
import AddMembersDialog from '@/components/admin/AddMembersDialog.vue'
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '@/api/modules/departments'
import { getUsers } from '@/api/modules/users'

const departmentTree = ref([])
const departments = ref([])
const users = ref([])
const selectedDept = ref(null)
const saving = ref(false)
const showDeptDialog = ref(false)
const deptDialogMode = ref('create')
const currentDept = ref({})
const showAddMembersDialog = ref(false)

const treeProps = {
  children: 'children',
  label: 'name'
}

const treeSelectProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

// 表单引用
const deptFormRef = ref(null)

// 部门表单验证规则
const deptRules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入部门编码', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_-]+$/, message: '只能包含字母、数字、下划线和横线', trigger: 'blur' }
  ]
}

// 计算属性
const departmentOptions = computed(() => {
  return buildDepartmentOptions(departments.value)
})

const deptUsers = computed(() => {
  if (!selectedDept.value) return []
  return users.value.filter(user => user.departmentId === selectedDept.value.id)
})

const childDepts = computed(() => {
  if (!selectedDept.value) return []
  return departments.value.filter(dept => dept.parentId === selectedDept.value.id)
})

const isCircularReference = computed(() => {
  if (!selectedDept.value || !selectedDept.value.parentId) return false
  
  // 检查是否形成循环引用
  let currentParentId = selectedDept.value.parentId
  while (currentParentId) {
    if (currentParentId === selectedDept.value.id) {
      return true
    }
    const parent = departments.value.find(d => d.id === currentParentId)
    currentParentId = parent?.parentId
  }
  return false
})

// 构建部门选项（扁平化树结构）
const buildDepartmentOptions = (depts, level = 0, result = []) => {
  depts.forEach(dept => {
    if (!dept.isSystem) {
      result.push({
        ...dept,
        disabled: level > 0 && dept.id === selectedDept.value?.id
      })
    }
    if (dept.children && dept.children.length > 0) {
      buildDepartmentOptions(dept.children, level + 1, result)
    }
  })
  return result
}

// 加载部门列表
const loadDepartments = async () => {
  try {
    const response = await getDepartments({ tree: true })
    if (response && response.data) {
      departmentTree.value = Array.isArray(response.data) ? response.data : []
      departments.value = flattenDepartments(departmentTree.value)
    }
  } catch (error) {
    console.error('加载部门列表失败:', error)
    ElMessage.error('加载部门列表失败')
  }
}

// 扁平化部门树
const flattenDepartments = (tree, result = []) => {
  tree.forEach(node => {
    result.push(node)
    if (node.children && node.children.length > 0) {
      flattenDepartments(node.children, result)
    }
  })
  return result
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await getUsers({ status: 'active' })
    if (response && response.data) {
      users.value = Array.isArray(response.data.items) ? response.data.items : []
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 节点点击
const handleNodeClick = (data, node) => {
  const dept = node || departments.value.find(d => d.id === data.id)
  if (dept) {
    selectedDept.value = { ...dept }
  }
}

// 新建部门
const handleCreateDept = () => {
  deptDialogMode.value = 'create'
  currentDept.value = {
    parentId: selectedDept.value?.id || null,
    sortOrder: 0,
    status: 'active'
  }
  showDeptDialog.value = true
}

// 编辑部门
const handleEditDept = (dept) => {
  deptDialogMode.value = 'edit'
  currentDept.value = { ...dept }
  showDeptDialog.value = true
}

// 删除部门
const handleDeleteDept = async (dept) => {
  try {
    // 检查是否有子部门
    const hasChildren = departments.value.some(d => d.parentId === dept.id)
    if (hasChildren) {
      ElMessage.warning('该部门下有子部门，无法删除')
      return
    }
    
    // 检查是否有用户
    const hasUsers = users.value.some(u => u.departmentId === dept.id)
    if (hasUsers) {
      ElMessage.warning('该部门下有用户，无法删除')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要删除部门 "${dept.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteDepartment(dept.id)
    ElMessage.success('删除成功')
    loadDepartments()
    if (selectedDept.value?.id === dept.id) {
      selectedDept.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 保存部门
const handleSaveDept = async () => {
  if (!selectedDept.value) return
  
  try {
    await deptFormRef.value.validate()
    saving.value = true
    
    if (selectedDept.value.id) {
      await updateDepartment(selectedDept.value.id, selectedDept.value)
    } else {
      await createDepartment(selectedDept.value)
    }
    
    ElMessage.success('保存成功')
    loadDepartments()
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('保存失败:', error)
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

// 重置部门
const handleResetDept = () => {
  if (selectedDept.value) {
    const original = departments.value.find(d => d.id === selectedDept.value.id)
    if (original) {
      selectedDept.value = { ...original }
    }
  }
}

// 添加成员
const handleAddMembers = () => {
  showAddMembersDialog.value = true
}

// 移除成员
const handleRemoveMember = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要将用户 "${user.realName || user.username}" 从部门中移除吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API将用户从部门移除
    ElMessage.success('移除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除失败:', error)
      ElMessage.error('移除失败')
    }
  }
}

// 部门保存回调
const handleDeptSaved = () => {
  loadDepartments()
}

// 部门对话框关闭回调
const handleDeptDialogClosed = () => {
  currentDept.value = {}
}

// 成员添加完成回调
const handleMembersAdded = () => {
  loadUsers()
}

// 刷新数据
const refreshData = () => {
  loadDepartments()
  loadUsers()
}

onMounted(() => {
  loadDepartments()
  loadUsers()
})
</script>

<style scoped>
.department-management-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.dept-tree-card,
.dept-detail-card {
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

.dept-tree-container {
  max-height: 600px;
  overflow-y: auto;
}

.modern-tree {
  background: transparent;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 4px 0;
}

.node-content {
  display: flex;
  align-items: center;
  flex: 1;
}

.node-icon {
  margin-right: 8px;
  color: #409eff;
}

.node-label {
  font-weight: 500;
}

.node-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-count {
  font-size: 12px;
  color: #909399;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.node-actions {
  display: flex;
  gap: 4px;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.detail-form {
  background: #fafafa;
  padding: 20px;
  border-radius: 6px;
}

.member-list {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.member-item:last-child {
  border-bottom: none;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-details {
  flex: 1;
}

.member-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.member-role {
  font-size: 12px;
  color: #909399;
}

.empty-members {
  padding: 40px;
  text-align: center;
}

.child-dept-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.child-dept-tag {
  margin: 2px;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

@media (max-width: 768px) {
  .department-management-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .detail-form {
    padding: 16px;
  }
}
</style>