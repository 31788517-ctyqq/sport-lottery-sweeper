<template>
  <el-form 
    ref="formRef" 
    :model="formData" 
    :rules="computedRules"
    :label-position="labelPosition"
    :label-width="labelWidth"
    :inline="inline"
    :size="size"
  >
    <el-row :gutter="gutter">
      <el-col 
        v-for="field in fields" 
        :key="field.name"
        :span="field.span || colSpan"
        :xs="field.xs || { span: 24 }"
        :sm="field.sm || { span: 12 }"
        :md="field.md || { span: 8 }"
        :lg="field.lg || { span: 6 }"
      >
        <el-form-item 
          :label="field.label"
          :prop="field.name"
          :required="field.required"
          :rules="field.rules"
        >
          <!-- 输入框 -->
          <el-input
            v-if="field.type === 'input' || !field.type"
            v-model="formData[field.name]"
            :placeholder="field.placeholder"
            :type="field.inputType || 'text'"
            :maxlength="field.maxlength"
            :show-word-limit="!!field.maxlength"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            v-bind="field.attrs || {}"
          >
            <template v-if="field.prepend" #prepend>{{ field.prepend }}</template>
            <template v-if="field.append" #append>{{ field.append }}</template>
          </el-input>

          <!-- 选择框 -->
          <el-select
            v-else-if="field.type === 'select'"
            v-model="formData[field.name]"
            :placeholder="field.placeholder"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            :multiple="field.multiple"
            :filterable="field.filterable !== false"
            v-bind="field.attrs || {}"
          >
            <el-option
              v-for="option in field.options || []"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>

          <!-- 日期选择器 -->
          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="formData[field.name]"
            :type="field.dateType || 'date'"
            :placeholder="field.placeholder"
            :format="field.format || 'YYYY-MM-DD'"
            :value-format="field.valueFormat || 'YYYY-MM-DD'"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            v-bind="field.attrs || {}"
          />

          <!-- 数字输入框 -->
          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="formData[field.name]"
            :placeholder="field.placeholder"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            :precision="field.precision"
            :controls="field.controls !== false"
            :disabled="field.disabled"
            v-bind="field.attrs || {}"
          />

          <!-- 开关 -->
          <el-switch
            v-else-if="field.type === 'switch'"
            v-model="formData[field.name]"
            :active-text="field.activeText"
            :inactive-text="field.inactiveText"
            :disabled="field.disabled"
            v-bind="field.attrs || {}"
          />

          <!-- 文本域 -->
          <el-input
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.name]"
            :type="'textarea'"
            :placeholder="field.placeholder"
            :rows="field.rows || 4"
            :maxlength="field.maxlength"
            :show-word-limit="!!field.maxlength"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            v-bind="field.attrs || {}"
          />

          <!-- 自定义插槽 -->
          <slot 
            v-else 
            :name="field.name" 
            :field="field" 
            :formData="formData"
          >
            <!-- 默认渲染 -->
            <el-input
              v-model="formData[field.name]"
              :placeholder="field.placeholder"
              :type="field.inputType || 'text'"
              :clearable="field.clearable !== false"
              :disabled="field.disabled"
              v-bind="field.attrs || {}"
            />
          </slot>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- 表单操作按钮 -->
    <el-form-item v-if="showActions" class="form-actions">
      <slot name="actions" :submit="submit" :reset="reset">
        <el-button type="primary" @click="submit" :loading="submitting">
          {{ submitButtonText }}
        </el-button>
        <el-button @click="reset" :disabled="submitting">
          {{ resetButtonText }}
        </el-button>
        <el-button @click="$emit('cancel')" v-if="showCancel">
          {{ cancelButtonText }}
        </el-button>
      </slot>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElDatePicker, ElInputNumber, ElSwitch, ElRow, ElCol, ElButton } from 'element-plus'

// 定义组件属性
const props = defineProps({
  // 字段配置数组
  fields: {
    type: Array,
    required: true
  },
  // 初始数据
  initialData: {
    type: Object,
    default: () => ({})
  },
  // 标签位置
  labelPosition: {
    type: String,
    default: 'right'
  },
  // 标签宽度
  labelWidth: {
    type: String,
    default: '120px'
  },
  // 是否水平排列
  inline: {
    type: Boolean,
    default: false
  },
  // 表单大小
  size: {
    type: String,
    default: 'default'
  },
  // 栅格间隔
  gutter: {
    type: Number,
    default: 20
  },
  // 列跨度
  colSpan: {
    type: Number,
    default: 8
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: true
  },
  // 提交按钮文字
  submitButtonText: {
    type: String,
    default: '提交'
  },
  // 重置按钮文字
  resetButtonText: {
    type: String,
    default: '重置'
  },
  // 是否显示取消按钮
  showCancel: {
    type: Boolean,
    default: false
  },
  // 取消按钮文字
  cancelButtonText: {
    type: String,
    default: '取消'
  }
})

// 定义事件
const emit = defineEmits(['submit', 'reset', 'cancel'])

// 表单引用
const formRef = ref(null)

// 表单数据
const formData = reactive({ ...props.initialData })

// 提交状态
const submitting = ref(false)

// 计算验证规则
const computedRules = computed(() => {
  const rules = {}
  props.fields.forEach(field => {
    if (field.rules) {
      rules[field.name] = field.rules
    }
  })
  return rules
})

// 提交表单
const submit = async () => {
  try {
    const valid = await formRef.value.validate()
    if (valid) {
      submitting.value = true
      await emit('submit', { ...formData })
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

// 重置表单
const reset = () => {
  Object.assign(formData, props.initialData)
  formRef.value?.clearValidate()
  emit('reset')
}

// 监听初始数据变化
watch(
  () => props.initialData,
  (newData) => {
    Object.assign(formData, newData)
  },
  { deep: true }
)

// 暴露方法给父组件
defineExpose({
  validate: () => formRef.value.validate(),
  validateField: (props) => formRef.value.validateField(props),
  resetFields: () => formRef.value.resetFields(),
  clearValidate: () => formRef.value.clearValidate(),
  formData
})
</script>

<style scoped>
.form-actions {
  margin-top: 24px;
  text-align: center;
}
</style>