<template>
  <el-dialog
    title="批量分配角色"
    v-model="visible"
    width="500px"
    @close="handleClose"
  >
    <div class="batch-assign-content">
      <div class="selected-users">
        <h4>已选择用户 ({{ selectedUsers.length }})</h4>
        <div class="user-list">
          <el-tag
            v-for="user in selectedUsers"
            :key="user.id"
            closable
            @close="removeUser(user.id)"
            class="user-tag"
          >
            {{ user.realName }} ({{ user.username }})
          </el-tag>
        </div>
      </div>
      
      <el-divider />
      
      <el-form :model="formData" label-width="80px">
        <el-form-item label="角色">
          <el-select
            v-model="formData.roleIds"
            multiple
            placeholder="请选择要分配的角色"
            style="width: 100%"
          >
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="有效期限">
          <el-date-picker
            v-model="formData.expireTime"
            type="datetime"
            placeholder="选择有效期至"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  modelValue: Boolean,
  selectedUsers: Array,
  roles: Array
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit'])

// 响应式数据
const visible = ref(false)
const submitting = ref(false)

const formData = reactive({
  roleIds: [],
  expireTime: null,
  remark: ''
})

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (!val) {
    resetForm()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const resetForm = () => {
  Object.assign(formData, {
    roleIds: [],
    expireTime: null,
    remark: ''
  })
}

const removeUser = (userId) => {
  emit('remove-user', userId)
}

const handleSubmit = async () => {
  if (props.selectedUsers.length === 0) {
    ElMessage.warning('请先选择用户')
    return
  }
  
  if (formData.roleIds.length === 0) {
    ElMessage.warning('请选择至少一个角色')
    return
  }
  
  try {
    submitting.value = true
    
    const submitData = {
      userIds: props.selectedUsers.map(u => u.id),
      roleIds: formData.roleIds,
      expireTime: formData.expireTime,
      remark: formData.remark
    }
    
    emit('submit', submitData)
    
  } catch (error) {
    console.error('批量分配角色失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

// 暴露方法
defineExpose({
  visible
})
</script>

<style scoped>
.batch-assign-content {
  max-height: 400px;
  overflow-y: auto;
}

.selected-users h4 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.user-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-tag {
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>