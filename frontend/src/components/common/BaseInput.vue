<template>
  <div
    :class="[
      'base-input',
      {
        'base-input--disabled': disabled,
        'base-input--error': hasError,
        'base-input--success': success,
        'base-input--with-left-icon': leftIcon,
        'base-input--with-right-icon': rightIcon || showPasswordToggle,
        'base-input--with-prefix': $slots.prefix,
        'base-input--with-suffix': $slots.suffix,
      }
    ]"
  >
    <label v-if="label" :for="id" class="base-input__label">
      {{ label }}
      <span v-if="required" class="base-input__required">*</span>
    </label>

    <div class="base-input__wrapper">
      <div v-if="$slots.prefix" class="base-input__prefix">
        <slot name="prefix"></slot>
      </div>

      <i v-if="leftIcon" :class="leftIcon" class="base-input__icon-left"></i>

      <input
        :id="id"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :autocomplete="autocomplete"
        :autofocus="autofocus"
        :maxlength="maxlength"
        :minlength="minlength"
        :step="step"
        :min="min"
        :max="max"
        :name="name"
        :class="['base-input__field', inputClass]"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @change="handleChange"
        ref="inputRef"
      />

      <i v-if="rightIcon" :class="rightIcon" class="base-input__icon-right"></i>

      <button
        v-if="showPasswordToggle && type === 'password'"
        type="button"
        class="base-input__password-toggle"
        @click="togglePasswordVisibility"
        tabindex="-1"
      >
        <i :class="passwordVisible ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
      </button>

      <div v-if="$slots.suffix" class="base-input__suffix">
        <slot name="suffix"></slot>
      </div>

      <button
        v-if="clearable && modelValue"
        type="button"
        class="base-input__clear"
        @click="handleClear"
        tabindex="-1"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div v-if="hasError || hint" class="base-input__feedback">
      <div v-if="hasError" class="base-input__error">
        <i class="fas fa-exclamation-circle"></i>
        {{ errorMessage }}
      </div>
      <div v-else-if="hint" class="base-input__hint">
        {{ hint }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  // 基础属性
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'password', 'email', 'number', 'tel', 'url', 'search', 'date', 'time', 'datetime-local'].includes(value)
  },
  id: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  // 状态
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  // 验证
  errorMessage: {
    type: String,
    default: ''
  },
  success: {
    type: Boolean,
    default: false
  },
  hint: {
    type: String,
    default: ''
  },
  // 图标
  leftIcon: {
    type: String,
    default: ''
  },
  rightIcon: {
    type: String,
    default: ''
  },
  // 功能
  clearable: {
    type: Boolean,
    default: false
  },
  showPasswordToggle: {
    type: Boolean,
    default: false
  },
  autocomplete: {
    type: String,
    default: 'off'
  },
  autofocus: {
    type: Boolean,
    default: false
  },
  // HTML属性
  maxlength: {
    type: [String, Number],
    default: null
  },
  minlength: {
    type: [String, Number],
    default: null
  },
  step: {
    type: [String, Number],
    default: null
  },
  min: {
    type: [String, Number],
    default: null
  },
  max: {
    type: [String, Number],
    default: null
  },
  // 样式
  inputClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'update:modelValue',
  'input',
  'blur',
  'focus',
  'change',
  'clear',
  'keydown',
  'keyup'
])

const inputRef = ref(null)
const passwordVisible = ref(false)
const isFocused = ref(false)

const inputType = computed(() => {
  if (props.type === 'password' && passwordVisible.value) {
    return 'text'
  }
  return props.type
})

const hasError = computed(() => {
  return !!props.errorMessage
})

// 方法
const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  emit('input', event)
}

const handleBlur = (event) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event) => {
  isFocused.value = true
  emit('focus', event)
}

const handleChange = (event) => {
  emit('change', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const togglePasswordVisibility = () => {
  passwordVisible.value = !passwordVisible.value
}

const focus = () => {
  inputRef.value?.focus()
}

const blur = () => {
  inputRef.value?.blur()
}

defineExpose({
  focus,
  blur
})
</script>

<style scoped>
.base-input {
  margin-bottom: 1rem;
  text-align: left;
}

.base-input__label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
}

.base-input__required {
  color: var(--danger);
}

.base-input__wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background-color: var(--bg-input);
  transition: all 0.2s ease;
}

.base-input__wrapper:hover {
  border-color: var(--primary-light);
}

.base-input--error .base-input__wrapper {
  border-color: var(--danger);
}

.base-input--success .base-input__wrapper {
  border-color: var(--success);
}

.base-input--disabled .base-input__wrapper {
  background-color: var(--bg-disabled);
  cursor: not-allowed;
}

.base-input__field {
  flex: 1;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.5;
  outline: none;
}

.base-input__field:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.base-input__field::placeholder {
  color: var(--text-placeholder);
}

.base-input__icon-left,
.base-input__icon-right {
  color: var(--text-secondary);
  font-size: 1rem;
  flex-shrink: 0;
}

.base-input__icon-left {
  padding-left: 1rem;
}

.base-input__icon-right {
  padding-right: 1rem;
}

.base-input__password-toggle,
.base-input__clear {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.base-input__password-toggle:hover,
.base-input__clear:hover {
  color: var(--text-primary);
}

.base-input__prefix,
.base-input__suffix {
  padding: 0 0.75rem;
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.875rem;
  white-space: nowrap;
  border: none;
}

.base-input__prefix {
  border-right: 1px solid var(--border-color);
  border-radius: 0.375rem 0 0 0.375rem;
}

.base-input__suffix {
  border-left: 1px solid var(--border-color);
  border-radius: 0 0.375rem 0.375rem 0;
}

.base-input__feedback {
  margin-top: 0.375rem;
  font-size: 0.875rem;
  min-height: 1.25rem;
}

.base-input__error {
  color: var(--danger);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.base-input__hint {
  color: var(--text-secondary);
}
</style>