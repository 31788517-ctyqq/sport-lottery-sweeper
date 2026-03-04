<template>
  <el-dialog
    class="um-dialog"
    v-model="visible"
    title="批量分配角色"
    width="560px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="batch-assign-content">
      <el-alert type="info" :closable="false" show-icon class="mb-12">
        已选择 {{ selectedUserCount }} 个用户
      </el-alert>

      <el-form :model="formData" label-width="90px">
        <el-form-item label="目标角色" required>
          <el-select
            v-model="formData.roleIds"
            multiple
            placeholder="请选择角色"
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

        <el-form-item label="备注">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="2"
            maxlength="200"
            show-word-limit
            placeholder="可选：记录本次批量分配原因"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认分配</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  selectedUserIds: { type: Array, default: () => [] },
  roles: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = ref(false)
const submitting = ref(false)

const formData = reactive({
  roleIds: [],
  remark: ''
})

const selectedUserCount = computed(() => props.selectedUserIds.length)

const resetForm = () => {
  formData.roleIds = []
  formData.remark = ''
}

const handleSubmit = async () => {
  if (selectedUserCount.value === 0) {
    ElMessage.warning('请先在列表中选择用户')
    return
  }
  if (!formData.roleIds.length) {
    ElMessage.warning('请至少选择一个角色')
    return
  }

  submitting.value = true
  try {
    emit('submit', {
      userIds: [...props.selectedUserIds],
      roleIds: [...formData.roleIds],
      remark: formData.remark
    })
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
    if (val) resetForm()
  },
  { immediate: true }
)

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) resetForm()
})
</script>

<style scoped>
:deep(.um-dialog.el-dialog) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: none;
  overflow: hidden;
}

:deep(.um-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 14px 16px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.um-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

:deep(.um-dialog .el-dialog__body) {
  padding: 16px;
}

:deep(.um-dialog .el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
}

.batch-assign-content {
  max-height: 420px;
  overflow-y: auto;
}

.mb-12 {
  margin-bottom: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
