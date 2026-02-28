<template>
  <div class="entity-mappings">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="球队映射" name="teams">
        <mapping-table :entity-type="'team'" :columns="['zh', 'en', 'source_aliases']" />
      </el-tab-pane>
      <el-tab-pane label="联赛映射" name="leagues">
        <mapping-table :entity-type="'league'" :columns="['zh', 'en', 'source_aliases']" />
      </el-tab-pane>
    </el-tabs>

    <div class="mapping-documentation">
      <h3>映射规则说明</h3>
      <ul>
        <li>请维护球队和联赛的多语言名称与来源别名映射。</li>
        <li>来源别名格式: <code>source_a:a1,a2;source_b:b1,b2</code>。</li>
        <li>保存后将实时影响数据标准化和官方信息页面展示。</li>
      </ul>
    </div>
  </div>
</template>

<script>
import MappingTable from './components/MappingTable.vue'

export default {
  name: 'EntityMappings',
  components: { MappingTable },
  data() {
    return {
      activeTab: 'teams'
    }
  }
}
</script>

<style scoped>
.entity-mappings {
  padding: 20px;
}

.mapping-documentation {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.mapping-documentation h3 {
  margin-top: 0;
  color: #333;
}

.mapping-documentation ul {
  padding-left: 20px;
}

.mapping-documentation code {
  background-color: #eef1f5;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
