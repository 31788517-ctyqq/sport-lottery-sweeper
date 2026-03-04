# 后台管理系统权限控制实现

## 概述

本文档详细说明如何在后台管理系统中实现细粒度的权限控制，包括用户角色管理、功能权限分配、数据访问控制等方面。

## 权限模型设计

### 1. 角色层级结构
- **超级管理员 (Super Admin)**：拥有系统全部权限
- **系统管理员 (System Admin)**：管理用户、系统配置、日志
- **AI管理员 (AI Admin)**：管理LLM服务、智能体、预测模型
- **运营管理员 (Operation Admin)**：管理数据源、比赛数据、用户内容
- **普通管理员 (Normal Admin)**：有限的查看和操作权限

### 2. 权限粒度设计
- **菜单权限**：控制菜单项的可见性
- **页面权限**：控制页面级别的访问
- **操作权限**：控制按钮/功能的可用性
- **数据权限**：控制数据的读写范围

## 后端权限实现

### 1. 数据模型定义

#### 用户与角色模型
```python
# backend/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # 如 "admin", "ai_admin", "operator"
    description = Column(String)
    permissions = Column(String)  # JSON格式存储权限列表
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
```

#### 权限模型
```python
# backend/models/permission.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from ..database import Base
from datetime import datetime

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # 如 "admin:users:read"
    description = Column(Text)
    resource = Column(String, nullable=False)  # 如 "users", "llm", "agents"
    action = Column(String, nullable=False)   # 如 "read", "write", "delete"
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. 权限检查依赖项

```python
# backend/dependencies/permissions.py
from fastapi import Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..auth import verify_token
from ..crud.user import get_user_by_username

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(verify_token)) -> User:
    """获取当前用户"""
    user = get_user_by_username(db, username=token.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    return user

def require_permission(permission: str):
    """权限检查装饰器"""
    def permission_checker(current_user: User = Depends(get_current_user)):
        # 检查用户是否具有超级用户权限
        if current_user.is_superuser:
            return current_user
            
        # 检查用户角色是否包含所需权限
        user_permissions = get_user_permissions(current_user)
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要: {permission}"
            )
        
        return current_user
    return permission_checker

def get_user_permissions(user: User) -> List[str]:
    """获取用户的所有权限"""
    permissions = set()
    
    # 如果是超级用户，返回所有权限
    if user.is_superuser:
        return ["*:*:*"]  # 所有资源的所有操作
    
    # 从用户角色获取权限
    for user_role in user.roles:
        role = user_role.role
        if role.permissions:
            import json
            role_perms = json.loads(role.permissions)
            permissions.update(role_perms)
    
    return list(permissions)
```

### 3. API权限控制示例

```python
# backend/api/v1/admin/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...models.user import User
from ...schemas.user import UserResponse
from ...dependencies.permissions import require_permission, get_current_user

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("admin:users:list")),
    db: Session = Depends(get_db)
):
    """获取用户列表 - 需要 admin:users:list 权限"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permission("admin:users:create")),
    db: Session = Depends(get_db)
):
    """创建用户 - 需要 admin:users:create 权限"""
    # 创建用户的逻辑
    pass

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_permission("admin:users:update")),
    db: Session = Depends(get_db)
):
    """更新用户 - 需要 admin:users:update 权限"""
    # 更新用户的逻辑
    pass

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("admin:users:delete")),
    db: Session = Depends(get_db)
):
    """删除用户 - 需要 admin:users:delete 权限"""
    # 删除用户的逻辑
    pass
```

## 前端权限实现

### 1. 权限状态管理

```typescript
// src/stores/permission.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePermissionStore = defineStore('permission', () => {
  // 用户权限列表
  const permissions = ref<string[]>([])
  
  // 设置用户权限
  const setPermissions = (perms: string[]) => {
    permissions.value = perms
  }
  
  // 检查是否有特定权限
  const hasPermission = computed(() => (perm: string) => {
    // 如果有通配符权限，则允许所有操作
    if (permissions.value.includes('*:*:*')) {
      return true
    }
    
    // 检查具体权限
    return permissions.value.includes(perm)
  })
  
  // 检查资源权限
  const hasResourcePermission = computed(() => (resource: string, action: string) => {
    if (permissions.value.includes('*:*:*')) {
      return true
    }
    
    // 检查具体资源权限
    return permissions.value.includes(`${resource}:${action}`) ||
           permissions.value.includes(`${resource}:*`) ||
           permissions.value.includes(`*:${action}`)
  })
  
  // 重置权限
  const resetPermissions = () => {
    permissions.value = []
  }
  
  return {
    permissions,
    setPermissions,
    hasPermission,
    hasResourcePermission,
    resetPermissions
  }
})
```

### 2. 权限指令

```typescript
// src/directives/permission.ts
import { Directive, App } from 'vue'
import { usePermissionStore } from '@/stores/permission'

interface PermissionDirectiveBinding {
  value: string | string[]
}

const permissionDirective: Directive = {
  mounted(el, binding) {
    const { value } = binding as unknown as { value: string | string[] }
    const permissionStore = usePermissionStore()
    
    // 检查权限
    const hasPerm = Array.isArray(value)
      ? value.some(perm => permissionStore.hasPermission(perm))
      : permissionStore.hasPermission(value)
    
    if (!hasPerm) {
      el.style.display = 'none'
    }
  },
  updated(el, binding) {
    const { value } = binding as unknown as { value: string | string[] }
    const permissionStore = usePermissionStore()
    
    // 检查权限
    const hasPerm = Array.isArray(value)
      ? value.some(perm => permissionStore.hasPermission(perm))
      : permissionStore.hasPermission(value)
    
    if (!hasPerm) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}

export default {
  install(app: App) {
    app.directive('permission', permissionDirective)
  }
}
```

### 3. 路由守卫

```typescript
// src/router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/DashboardView.vue'),
        meta: { permissions: ['admin:dashboard:view'] }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { permissions: ['admin:users:list'] }
      },
      {
        path: 'ai/providers',
        name: 'AIProviders',
        component: () => import('@/views/admin/LLMManagement.vue'),
        meta: { permissions: ['admin:ai:manage'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()
  
  // 检查是否需要认证
  if (to.meta?.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 检查权限
  if (to.meta?.permissions) {
    // 如果用户没有必要的权限，重定向到无权限页面
    const requiredPerms = to.meta.permissions as string[]
    const hasAnyPerm = requiredPerms.some(perm => permissionStore.hasPermission(perm))
    
    if (!hasAnyPerm) {
      next('/unauthorized')
      return
    }
  }
  
  next()
})

export default router
```

### 4. 组件级权限控制

```vue
<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <!-- 只有有创建权限的用户才能看到创建按钮 -->
          <el-button 
            v-permission="'admin:users:create'" 
            type="primary" 
            @click="showCreateDialog"
          >
            新增用户
          </el-button>
        </div>
      </template>
      
      <el-table :data="users">
        <el-table-column prop="id" label="ID" width="100"></el-table-column>
        <el-table-column prop="username" label="用户名"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="isActive" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'danger'">
              {{ row.isActive ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <!-- 编辑权限 -->
            <el-button 
              v-permission="'admin:users:update'" 
              size="small" 
              @click="editUser(row)"
            >
              编辑
            </el-button>
            <!-- 删除权限 -->
            <el-button 
              v-permission="'admin:users:delete'" 
              size="small" 
              type="danger" 
              @click="deleteUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 权限配置对话框 - 只有管理员才能看到 -->
    <el-dialog 
      v-if="$permission.hasPermission('admin:roles:manage')" 
      v-model="roleDialogVisible" 
      title="配置角色权限" 
      width="50%"
    >
      <!-- 角色权限配置内容 -->
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api/user'
import { usePermissionStore } from '@/stores/permission'

const permissionStore = usePermissionStore()
const users = ref<any[]>([])
const roleDialogVisible = ref(false)

onMounted(async () => {
  await loadUsers()
})

const loadUsers = async () => {
  try {
    // 检查是否有列表权限
    if (!permissionStore.hasPermission('admin:users:list')) {
      ElMessage.error('您没有查看用户列表的权限')
      return
    }
    
    const response = await userApi.getUsers()
    users.value = response.data
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

const showCreateDialog = () => {
  // 此按钮只有有权限的用户才能看到，但仍可检查权限
  console.log('打开创建用户对话框')
}

const editUser = (user: any) => {
  // 检查编辑权限
  if (!permissionStore.hasPermission('admin:users:update')) {
    ElMessage.error('您没有编辑用户的权限')
    return
  }
  console.log('编辑用户:', user)
}

const deleteUser = async (user: any) => {
  // 检查删除权限
  if (!permissionStore.hasPermission('admin:users:delete')) {
    ElMessage.error('您没有删除用户的权限')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await userApi.deleteUser(user.id)
    ElMessage.success('删除成功')
    await loadUsers() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>
```

## 权限管理界面

### 1. 角色管理页面

```vue
<template>
  <div class="role-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button 
            v-permission="'admin:roles:create'" 
            type="primary" 
            @click="showCreateRoleDialog"
          >
            新增角色
          </el-button>
        </div>
      </template>
      
      <el-table :data="roles">
        <el-table-column prop="name" label="角色名" width="200"></el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column label="权限数" width="100">
          <template #default="{ row }">
            {{ getPermissionCount(row.permissions) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              v-permission="'admin:roles:update'" 
              size="small" 
              @click="editRole(row)"
            >
              编辑权限
            </el-button>
            <el-button 
              v-permission="'admin:roles:delete'" 
              size="small" 
              type="danger" 
              @click="deleteRole(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 编辑权限对话框 -->
    <el-dialog v-model="permissionDialogVisible" title="编辑角色权限" width="60%">
      <el-tree
        ref="treeRef"
        :data="permissionTree"
        :props="treeProps"
        node-key="id"
        show-checkbox
        :default-checked-keys="checkedPermissions"
      />
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { roleApi } from '@/api/role'

const roles = ref<any[]>([])
const permissionDialogVisible = ref(false)
const currentRoleId = ref<number | null>(null)
const checkedPermissions = ref<number[]>([])
const treeRef = ref()
const permissionTree = ref([])
const treeProps = {
  children: 'children',
  label: 'label'
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await roleApi.getRoles()
    roles.value = response.data
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  }
}

// 获取权限数
const getPermissionCount = (permissions: string[]) => {
  return permissions ? JSON.parse(permissions).length : 0
}

// 编辑角色权限
const editRole = async (role: any) => {
  currentRoleId.value = role.id
  
  try {
    // 加载权限树
    const permTreeResponse = await roleApi.getPermissionTree()
    permissionTree.value = permTreeResponse.data
    
    // 加载当前角色的权限
    const rolePermsResponse = await roleApi.getRolePermissions(role.id)
    checkedPermissions.value = rolePermsResponse.data.map((p: any) => p.id)
    
    permissionDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载权限数据失败')
  }
}

// 保存权限
const savePermissions = async () => {
  if (!currentRoleId.value) return
  
  try {
    const checkedKeys = treeRef.value.getCheckedKeys(true)
    await roleApi.updateRolePermissions(currentRoleId.value, checkedKeys)
    ElMessage.success('权限更新成功')
    permissionDialogVisible.value = false
    await loadRoles() // 刷新列表
  } catch (error) {
    ElMessage.error('权限更新失败')
  }
}

// 删除角色
const deleteRole = async (role: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await roleApi.deleteRole(role.id)
    ElMessage.success('删除成功')
    await loadRoles() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 初始化
loadRoles()
</script>
```

## 权限控制最佳实践

### 1. 安全原则
- **最小权限原则**：只授予完成任务所需的最小权限
- **权限分离**：将敏感操作权限与一般操作权限分离
- **定期审查**：定期审查和清理不必要的权限分配

### 2. 性能优化
- **权限缓存**：缓存用户权限以减少数据库查询
- **批量查询**：批量获取用户权限信息
- **权限预加载**：在用户登录时预加载权限信息

### 3. 用户体验
- **友好的错误提示**：提供清晰的权限不足提示
- **引导性界面**：引导用户联系管理员获取权限
- **渐进式披露**：根据权限逐步展示功能

### 4. 监控与审计
- **权限变更日志**：记录所有权限变更操作
- **异常访问监控**：监控未授权访问尝试
- **权限使用分析**：分析权限使用情况以优化配置

## 测试策略

### 1. 单元测试
```python
def test_user_permissions():
    # 测试用户权限获取
    pass

def test_permission_check():
    # 测试权限检查逻辑
    pass
```

### 2. 集成测试
```python
def test_api_permission_control():
    # 测试API权限控制
    pass
```

### 3. 端到端测试
```typescript
// 测试权限控制的前端功能
describe('Permission Control', () => {
  it('should hide elements without permission', () => {
    // 测试无权限时元素隐藏
  })
})
```

通过以上设计和实现，我们可以建立一个安全、灵活、可扩展的权限控制系统，确保后台管理系统中的各项功能只能被有权限的用户访问和操作。