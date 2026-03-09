<template>
  <div class="basic-settings">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="basicSettingsFormRef"
      label-width="140px"
      class="settings-form"
    >
      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>系统基本信息</span>
          </div>
        </template>
        
        <el-form-item label="系统名称" prop="systemName">
          <el-input v-model="form.systemName" placeholder="请输入系统名称" />
        </el-form-item>
        
        <el-form-item label="系统描述" prop="systemDescription">
          <el-input 
            v-model="form.systemDescription" 
            type="textarea" 
            :rows="3"
            placeholder="请输入系统描述信息" 
          />
        </el-form-item>
        
        <el-form-item label="系统Logo">
          <el-upload
            class="logo-uploader"
            action="/api/upload"
            :show-file-list="false"
            :on-success="handleLogoUploadSuccess"
            :before-upload="beforeLogoUpload"
          >
            <img v-if="form.logoUrl" :src="form.logoUrl" class="logo-image" />
            <el-icon v-else class="logo-uploader-icon">
              <Plus />
            </el-icon>
          </el-upload>
        </el-form-item>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>菜单管理</span>
            <div class="menu-actions">
              <el-button type="primary" size="small" @click="addMenu(null)">添加菜单</el-button>
            </div>
          </div>
        </template>
        
        <div class="menu-management">
          <el-tree
            ref="menuTreeRef"
            :data="menuList"
            node-key="id"
            :props="{ label: 'name', children: 'children' }"
            draggable
            :allow-drop="allowDrop"
            @node-drag-end="handleDragEnd"
            :expand-on-click-node="false"
            class="menu-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node-content">
                <span class="menu-name">{{ node.label }}</span>
                <span class="menu-route">{{ data.route }}</span>
                <div class="node-actions">
                  <el-button size="small" type="primary" @click.stop="addMenu(data)">添加子菜单</el-button>
                  <el-button size="small" @click.stop="editMenu(data)">编辑</el-button>
                  <el-button size="small" type="danger" @click.stop="deleteMenu(data)">删除</el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </el-card>

      <el-card class="setting-group">
        <template #header>
          <div class="group-header">
            <span>系统配置</span>
          </div>
        </template>
        
        <el-form-item label="系统维护模式">
          <el-switch
            v-model="form.maintenanceMode"
            inline-prompt
            active-text="开启"
            inactive-text="关闭"
          />
          <div class="setting-description">开启后普通用户将无法访问系统</div>
        </el-form-item>
        
        <el-form-item label="数据保留天数" prop="dataRetentionDays">
          <el-input-number 
            v-model="form.dataRetentionDays" 
            :min="1" 
            :max="365"
            controls-position="right"
          />
          <div class="setting-description">超过指定天数的数据将被自动清理</div>
        </el-form-item>
        
        <el-form-item label="会话超时时间(分钟)" prop="sessionTimeout">
          <el-input-number 
            v-model="form.sessionTimeout" 
            :min="5" 
            :max="1440"
            controls-position="right"
          />
          <div class="setting-description">用户无操作后会话超时的时间</div>
        </el-form-item>
      </el-card>

      <div class="form-actions">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetForm">重置</el-button>
      </div>
    </el-form>

    <!-- 菜单管理对话框 -->
    <el-dialog
      :title="menuDialogTitle"
      v-model="menuDialogVisible"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="menuForm"
        :rules="menuFormRules"
        ref="menuFormRef"
        label-width="100px"
      >
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="路由路径" prop="route">
          <el-input v-model="menuForm.route" placeholder="请输入路由路径，如 /dashboard" />
        </el-form-item>
        <el-form-item label="菜单图标" prop="icon">
          <el-input v-model="menuForm.icon" placeholder="请输入图标名称，如 Dashboard" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="menuDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleMenuDialogConfirm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'BasicSettings',
  setup() {
    const authStore = useAuthStore()
    
    // 表单数据
    const form = ref({
      systemName: '竞彩足球扫盘系统',
      systemDescription: '专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。',
      logoUrl: '',
      maintenanceMode: false,
      dataRetentionDays: 90,
      sessionTimeout: 30
    })

    // 菜单管理数据
    const menuList = ref([
      {
        id: 1,
        name: '仪表盘',
        route: '/dashboard',
        icon: 'Dashboard',
        parentId: null,
        sortOrder: 1,
        children: []
      },
      {
        id: 2,
        name: '比赛管理',
        route: '/matches',
        icon: 'Football',
        parentId: null,
        sortOrder: 2,
        children: [
          {
            id: 3,
            name: '比赛列表',
            route: '/matches/list',
            icon: 'List',
            parentId: 2,
            sortOrder: 1,
            children: []
          },
          {
            id: 4,
            name: '比赛分析',
            route: '/matches/analysis',
            icon: 'TrendCharts',
            parentId: 2,
            sortOrder: 2,
            children: []
          }
        ]
      },
      {
        id: 5,
        name: '系统设置',
        route: '/settings',
        icon: 'Setting',
        parentId: null,
        sortOrder: 3,
        children: [
          {
            id: 6,
            name: '基础设置',
            route: '/settings/basic',
            icon: 'Tools',
            parentId: 5,
            sortOrder: 1,
            children: []
          }
        ]
      }
    ])

    // 菜单对话框相关
    const menuDialogVisible = ref(false)
    const menuDialogTitle = ref('')
    const menuForm = ref({
      id: null,
      name: '',
      route: '',
      icon: '',
      parentId: null
    })
    const menuFormRules = {
      name: [
        { required: true, message: '请输入菜单名称', trigger: 'blur' },
        { min: 2, max: 20, message: '长度在2到20个字符', trigger: 'blur' }
      ],
      route: [
        { required: true, message: '请输入路由路径', trigger: 'blur' }
      ],
      icon: [
        { required: true, message: '请选择菜单图标', trigger: 'blur' }
      ]
    }
    const menuTreeRef = ref(null)
    const menuFormRef = ref(null)

    // 表单验证规则
    const rules = {
      systemName: [
        { required: true, message: '请输入系统名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在2到50个字符', trigger: 'blur' }
      ],
      systemDescription: [
        { required: true, message: '请输入系统描述', trigger: 'blur' }
      ],
      dataRetentionDays: [
        { required: true, message: '请输入数据保留天数', trigger: 'blur' }
      ],
      sessionTimeout: [
        { required: true, message: '请输入会话超时时间', trigger: 'blur' }
      ]
    }

    // 权限检查
    const hasPermission = (requiredRole) => {
      if (!authStore.userInfo) return false
      const userRoles = authStore.userInfo.roles || []
      return userRoles.includes('super_admin') || userRoles.includes(requiredRole)
    }

    // 菜单管理方法
    const allowDrop = (draggingNode, dropNode, type) => {
      // 只允许在节点内部或之间拖拽，不允许放到外部
      return type !== 'none'
    }

    const handleDragEnd = async (draggingNode, dropNode, dropType) => {
      try {
        // 重新计算排序顺序
        const updateOrder = (nodes, parentId = null) => {
          nodes.forEach((node, index) => {
            node.sortOrder = index + 1
            node.parentId = parentId
            if (node.children && node.children.length > 0) {
              updateOrder(node.children, node.id)
            }
          })
        }
        updateOrder(menuList.value)
        
        // TODO: 调用后端API保存排序
        ElMessage.success('菜单排序已保存')
      } catch (error) {
        console.error('保存菜单排序失败:', error)
        ElMessage.error('保存排序失败，请重试')
      }
    }

    const addMenu = (parentMenu) => {
      menuDialogTitle.value = parentMenu ? `添加子菜单到【${parentMenu.name}】` : '添加菜单'
      menuForm.value = {
        id: null,
        name: '',
        route: '',
        icon: '',
        parentId: parentMenu ? parentMenu.id : null
      }
      menuDialogVisible.value = true
    }

    const editMenu = (menu) => {
      menuDialogTitle.value = '编辑菜单'
      menuForm.value = {
        id: menu.id,
        name: menu.name,
        route: menu.route,
        icon: menu.icon,
        parentId: menu.parentId
      }
      menuDialogVisible.value = true
    }

    const deleteMenu = async (menu) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除菜单【${menu.name}】吗？删除后无法恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 递归删除菜单及其子菜单
        const removeMenu = (menuList, menuId) => {
          for (let i = 0; i < menuList.length; i++) {
            if (menuList[i].id === menuId) {
              menuList.splice(i, 1)
              return true
            }
            if (menuList[i].children && menuList[i].children.length > 0) {
              if (removeMenu(menuList[i].children, menuId)) {
                return true
              }
            }
          }
          return false
        }
        
        removeMenu(menuList.value, menu.id)
        ElMessage.success('菜单删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除菜单失败:', error)
          ElMessage.error('删除菜单失败，请重试')
        }
      }
    }

    const handleMenuDialogConfirm = async () => {
      try {
        // 表单验证
        if (!menuForm.value.name.trim()) {
          ElMessage.error('请输入菜单名称')
          return
        }
        
        if (menuForm.value.id) {
          // 编辑菜单
          const updateMenu = (menuList, menuId, newData) => {
            for (let i = 0; i < menuList.length; i++) {
              if (menuList[i].id === menuId) {
                Object.assign(menuList[i], newData)
                return true
              }
              if (menuList[i].children && menuList[i].children.length > 0) {
                if (updateMenu(menuList[i].children, menuId, newData)) {
                  return true
                }
              }
            }
            return false
          }
          
          updateMenu(menuList.value, menuForm.value.id, {
            name: menuForm.value.name,
            route: menuForm.value.route,
            icon: menuForm.value.icon,
            parentId: menuForm.value.parentId
          })
          ElMessage.success('菜单编辑成功')
        } else {
          // 添加菜单
          const newMenu = {
            id: Date.now(), // 临时ID，实际应由后端生成
            name: menuForm.value.name,
            route: menuForm.value.route,
            icon: menuForm.value.icon,
            parentId: menuForm.value.parentId,
            sortOrder: 1,
            children: []
          }
          
          if (menuForm.value.parentId) {
            // 添加到父菜单
            const addToParent = (menuList, parentId, newMenu) => {
              for (let i = 0; i < menuList.length; i++) {
                if (menuList[i].id === parentId) {
                  if (!menuList[i].children) {
                    menuList[i].children = []
                  }
                  menuList[i].children.push(newMenu)
                  // 更新子菜单排序
                  menuList[i].children.forEach((child, index) => {
                    child.sortOrder = index + 1
                  })
                  return true
                }
                if (menuList[i].children && menuList[i].children.length > 0) {
                  if (addToParent(menuList[i].children, parentId, newMenu)) {
                    return true
                  }
                }
              }
              return false
            }
            
            addToParent(menuList.value, menuForm.value.parentId, newMenu)
          } else {
            // 添加到根菜单
            menuList.value.push(newMenu)
            // 更新根菜单排序
            menuList.value.forEach((menu, index) => {
              menu.sortOrder = index + 1
            })
          }
          ElMessage.success('菜单添加成功')
        }
        
        menuDialogVisible.value = false
        // 刷新树视图
        nextTick(() => {
          if (menuTreeRef.value) {
            menuTreeRef.value.updateKeyChildren()
          }
        })
      } catch (error) {
        console.error('保存菜单失败:', error)
        ElMessage.error('保存菜单失败，请重试')
      }
    }

    // 保存系统配置
    const saveSettings = async () => {
      try {
        // TODO: 实现后端API调用
        ElMessage.success('基础设置保存成功')
      } catch (error) {
        console.error('保存设置失败:', error)
        ElMessage.error('网络请求失败，请检查网络连接')
      }
    }

    const resetForm = () => {
      form.value = {
        systemName: '竞彩足球扫盘系统',
        systemDescription: '专业的足球数据采集、分析和预测平台，为竞彩足球提供全面的数据支持与智能决策辅助。',
        logoUrl: '',
        maintenanceMode: false,
        dataRetentionDays: 90,
        sessionTimeout: 30
      }
    }

    const handleLogoUploadSuccess = (response, file) => {
      form.value.logoUrl = URL.createObjectURL(file.raw)
      ElMessage.success('Logo上传成功')
    }

    const beforeLogoUpload = (rawFile) => {
      if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
        ElMessage.error('Logo图片只能是 JPG/PNG 格式!')
        return false
      }
      if (rawFile.size / 1024 / 1024 > 2) {
        ElMessage.error('Logo图片大小不能超过 2MB!')
        return false
      }
      return true
    }

    return {
      form,
      rules,
      saveSettings,
      resetForm,
      handleLogoUploadSuccess,
      beforeLogoUpload,
      Plus,
      hasPermission,
      // 菜单管理相关
      menuList,
      menuDialogVisible,
      menuDialogTitle,
      menuForm,
      menuFormRules,
      menuTreeRef,
      menuFormRef,
      allowDrop,
      handleDragEnd,
      addMenu,
      editMenu,
      deleteMenu,
      handleMenuDialogConfirm
    }
  }
}
</script>

<style scoped>
.basic-settings {
  padding: 20px 0;
}

.settings-form {
  max-width: 800px;
}

.setting-group {
  margin-bottom: 20px;
}

.group-header {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-description {
  color: #909399;
  font-size: 13px;
  margin-top: 5px;
}

.logo-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 100px;
  height: 100px;
}

.logo-uploader:hover {
  border-color: var(--el-color-primary);
}

.logo-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
}

.logo-image {
  width: 100px;
  height: 100px;
  display: block;
}

.form-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-form {
    max-width: 100%;
  }
}

/* 菜单管理样式 */
.menu-management {
  padding: 10px 0;
}

.menu-tree {
  padding: 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  background-color: var(--el-fill-color-light);
}

.tree-node-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}

.menu-name {
  font-weight: 500;
  margin-right: 10px;
}

.menu-route {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  background-color: var(--el-fill-color);
  padding: 2px 6px;
  border-radius: 3px;
  margin-right: 10px;
}

.node-actions {
  display: flex;
  gap: 8px;
  opacity: 0.8;
}

.node-actions:hover {
  opacity: 1;
}

.menu-actions {
  display: flex;
  gap: 10px;
}
</style>