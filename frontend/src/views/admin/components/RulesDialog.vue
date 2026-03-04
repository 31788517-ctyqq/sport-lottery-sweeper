<template>
  <el-dialog title="P级计算规则" v-model="dialogVisible" width="60%">
    <div v-if="rules">
      <h3>评级标准</h3>
      <ul>
        <li><strong>P1：</strong>{{ rules.p1_criteria }}</li>
        <li><strong>P2：</strong>{{ rules.p2_criteria }}</li>
        <li><strong>P3：</strong>{{ rules.p3_criteria }}</li>
        <li><strong>P4：</strong>{{ rules.p4_criteria }}</li>
        <li><strong>P5：</strong>{{ rules.p5_criteria }}</li>
        <li><strong>P6：</strong>{{ rules.p6_criteria }}</li>
        <li><strong>P7：</strong>{{ rules.p7_criteria }}</li>
      </ul>
      
      <h3>降级规则</h3>
      <ol>
        <li v-for="(rule, index) in rules.derating_rules" :key="index">{{ rule }}</li>
      </ol>
      
      <h3>排序规则</h3>
      <ol>
        <li v-for="(rule, index) in rules.sort_rules" :key="'sort'+index">{{ rule }}</li>
      </ol>
    </div>
  </el-dialog>
</template>

<script>
import { defineComponent, computed } from 'vue';
import { ElDialog } from 'element-plus';

export default defineComponent({
  name: 'RulesDialog',
  components: {
    ElDialog
  },
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    rules: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible'],
  setup(props, { emit }) {
    const dialogVisible = computed({
      get: () => props.visible,
      set: (val) => emit('update:visible', val)
    });

    return {
      dialogVisible
    };
  }
});
</script>

<style scoped>
h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #6b6763;
}

ul, ol {
  padding-left: 20px;
}

li {
  margin-bottom: 8px;
  line-height: 1.4;
}
</style>
