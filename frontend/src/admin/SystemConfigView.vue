<template>
  <div class="system-config-view">
    <h1>系统配置</h1>
    <el-form ref="configForm" :model="configForm" label-width="150px" style="max-width: 600px;">
      <el-form-item label="网站标题">
        <el-input v-model="configForm.siteTitle"></el-input>
      </el-form-item>
      <el-form-item label="默认语言">
        <el-select v-model="configForm.defaultLang" placeholder="请选择">
          <el-option label="中文" value="zh-CN"></el-option>
          <el-option label="English" value="en-US"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="启用注册">
        <el-switch v-model="configForm.enableRegistration"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">保存配置</el-button>
        <el-button @click="onCancel">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'SystemConfigView',
  data() {
    return {
      configForm: {
        siteTitle: '我的系统',
        defaultLang: 'zh-CN',
        enableRegistration: true,
      }
    };
  },
  methods: {
    onSubmit() {
      console.log('Saving configuration:', this.configForm);
      // 实现保存逻辑
      this.$message.success('配置保存成功！');
    },
    onCancel() {
      // 实现取消逻辑，例如重置表单
      this.$refs.configForm.resetFields();
    }
  }
};
</script>

<style scoped>
.system-config-view {
  padding: 20px;
}
</style>