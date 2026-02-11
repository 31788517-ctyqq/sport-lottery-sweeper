# 组件与API命名规范

## 1. 组件命名规范

### 1.1 通用组件命名
- 以 `Generic` 或 `Base` 为前缀，例如：`GenericTable`、`GenericForm`、`BaseButton`
- 功能性组件以功能词为后缀，例如：`DataTable`、`SearchForm`、`ModalDialog`

### 1.2 业务组件命名
- 以业务领域为前缀，例如：`UserList`、`MatchCard`、`AdminMenu`
- 页面组件以 `Page` 或 `View` 结尾，例如：`UserManagementView`、`DashboardPage`

### 1.3 原子组件命名
- 基础组件以 `Base` 为前缀，例如：`BaseInput`、`BaseSelect`、`BaseButton`
- 布局组件以 `Layout` 为后缀，例如：`MainLayout`、`SidebarLayout`

## 2. API 命名规范

### 2.1 API 函数命名
- 获取列表：`get<Entity>Lists`，例如：`getUserLists`、`getMatchLists`
- 获取单个：`get<Entity>`，例如：`getUser`、`getMatch`
- 创建：`create<Entity>`，例如：`createUser`、`createMatch`
- 更新：`update<Entity>`，例如：`updateUser`、`updateMatch`
- 删除：`delete<Entity>`，例如：`deleteUser`、`deleteMatch`
- 批量操作：`batch<Operation><Entity>`，例如：`batchDeleteUsers`

### 2.2 API 模块命名
- 按功能领域划分，例如：`auth`、`user`、`match`、`admin`
- 复杂功能可嵌套，例如：`crawler.source`、`intelligence.analysis`

### 2.3 API 路径命名
- 使用名词复数形式，例如：`/users`、`/matches`、`/leagues`
- 嵌套资源使用斜杠，例如：`/users/:id/roles`、`/matches/:id/odds`
- 操作使用动词，例如：`/users/batch-delete`、`/matches/import`

## 3. Store 命名规范

### 3.1 Store 名称
- 使用驼峰命名法，以 `use` 开头，`Store` 结尾
- 例如：`useUserStore`、`useDataManagerStore`、`useMatchStore`

### 3.2 State 属性命名
- 使用名词，保持语义清晰
- 例如：`currentUser`、`userList`、`isLoading`、`errorMessages`

### 3.3 Actions 方法命名
- 使用动词开头，表示具体操作
- 例如：`fetchUserList`、`updateUser`、`deleteUser`、`resetState`

## 4. 文件命名规范

### 4.1 组件文件
- Vue 组件使用 PascalCase，例如：`GenericTable.vue`、`UserManagementView.vue`
- 小型组件可使用 kebab-case，例如：`search-input.vue`、`user-avatar.vue`

### 4.2 JavaScript/TypeScript 文件
- 使用 kebab-case，例如：`data-manager.js`、`user-api.js`
- Store 文件使用 camelCase，例如：`userManager.js`

### 4.3 目录命名
- 使用 kebab-case，例如：`common-components`、`user-modules`
- 按功能分组，例如：`views/admin`、`components/common`、`api/modules`

## 5. 代码组织规范

### 5.1 组件结构
```
<template>
  <!-- 模板内容 -->
</template>

<script setup>
// 组件逻辑
</script>

<style scoped>
/* 样式 */
</style>
```

### 5.2 API 模块结构
```javascript
// 导入
import apiClient from '../index'

// API 函数定义
export const getUsers = async (params) => {
  // 实现
}

// 导出
export default {
  getUsers
}
```

### 5.3 Store 结构
```javascript
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', {
  state: () => ({
    // 状态定义
  }),
  
  getters: {
    // 计算属性
  },
  
  actions: {
    // 方法定义
  }
})
```

## 6. 通用组件使用规范

### 6.1 GenericTable 使用规范
```vue
<GenericTable
  :columns="tableColumns"
  :table-data="dataList"
  :loading="loading"
  :pagination="pagination"
  @current-change="handlePageChange"
>
  <!-- 插槽内容 -->
</GenericTable>
```

### 6.2 GenericForm 使用规范
```vue
<GenericForm
  :fields="formFields"
  :initial-data="formData"
  @submit="handleSubmit"
/>
```

### 6.3 数据管理 Store 使用规范
```javascript
import { useDataManagerStore } from '@/stores/dataManager'

const dataStore = useDataManagerStore()

// 获取数据
await dataStore.fetchList('apiEndpoint')

// 更新数据
await dataStore.updateItem('apiEndpoint', id, data)
```

这些规范旨在提高代码的可维护性、可读性和可复用性，确保团队开发的一致性。