<template>
  <button 
    class="switch-button" 
    :class="{ active: modelValue }"
    @click="toggle"
    :aria-pressed="modelValue"
  >
    <div class="switch-slider">
      <div class="switch-thumb"></div>
    </div>
  </button>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const toggle = () => {
  const newValue = !props.modelValue
  emit('update:modelValue', newValue)
  emit('change', newValue)
}
</script>

<style scoped>
.switch-button {
  position: relative;
  width: 48px;
  height: 26px;
  border: none;
  background: var(--text-sub);
  border-radius: 13px;
  cursor: pointer;
  transition: background 0.3s;
  flex-shrink: 0;
}

.switch-button.active {
  background: var(--primary);
}

.switch-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  transition: transform 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.switch-button.active .switch-slider {
  transform: translateX(22px);
}

.switch-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}
</style>