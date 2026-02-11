<template>
  <el-card class="multi-strategy-card" v-if="showMultiStrategyPanel">
    <div slot="header" class="clearfix">
      <span>多策略筛选配置</span>
    </div>
    
    <el-form :model="multiStrategyForm" label-width="120px">
      <el-form-item label="任务名称">
        <el-input 
          v-model="multiStrategyForm.taskName" 
          placeholder="请输入任务名称"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="选择策略">
        <el-checkbox-group v-model="multiStrategyForm.selectedStrategies">
          <el-checkbox 
            v-for="strategy in availableStrategies" 
            :key="strategy.id" 
            :label="strategy.id"
          >
            {{ strategy.name }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      
      <el-form-item label="执行频率">
        <el-select v-model="multiStrategyForm.cronType" @change="updateCronExpression">
          <el-option label="每小时" value="hourly"></el-option>
          <el-option label="每天" value="daily"></el-option>
          <el-option label="每周" value="weekly"></el-option>
          <el-option label="自定义" value="custom"></el-option>
        </el-select>
        
        <el-input 
          v-if="multiStrategyForm.cronType === 'custom'"
          v-model="multiStrategyForm.cronExpression" 
          placeholder="请输入Cron表达式"
          style="margin-top: 10px;"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="消息格式">
        <el-radio-group v-model="multiStrategyForm.messageFormat">
          <el-radio label="text">纯文本</el-radio>
          <el-radio label="table">表格形式</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="钉钉通知">
        <el-switch v-model="multiStrategyForm.dingtalkEnabled"></el-switch>
        <div v-if="multiStrategyForm.dingtalkEnabled" style="margin-top: 10px;">
          <el-input 
            v-model="multiStrategyForm.dingtalkWebhook" 
            placeholder="请输入钉钉机器人Webhook URL"
            style="width: 80%;"
          ></el-input>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="saveMultiStrategyConfig">保存配置</el-button>
        <el-button @click="executeNow">立即执行</el-button>
        <el-button @click="togglePanel">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>

  <el-button 
    v-else 
    type="info" 
    @click="togglePanel"
    style="margin-bottom: 20px;"
  >
    配置多策略筛选
  </el-button>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

export default {
  name: 'MultiStrategyConfig',
  props: {
    showMultiStrategyPanel: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:showMultiStrategyPanel', 'strategy-configured'],
  setup(props, { emit }) {
    const availableStrategies = ref([]);
    
    const multiStrategyForm = reactive({
      taskName: '',
      selectedStrategies: [],
      cronType: 'daily',
      cronExpression: '0 9 * * *', // 默认每天上午9点
      messageFormat: 'table',
      dingtalkEnabled: false,
      dingtalkWebhook: ''
    });

    // 获取可用策略列表
    const loadAvailableStrategies = async () => {
      try {
        const response = await request({
          url: '/v1/multi-strategy/strategies',
          method: 'GET'
        });
        
        if (response.success) {
          availableStrategies.value = response.data.map(id => ({
            id,
            name: id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) // 转换为标题格式
          }));
        } else {
          console.error('获取策略列表失败:', response.message);
        }
      } catch (error) {
        console.error('获取策略列表失败:', error);
        ElMessage.error('获取策略列表失败');
      }
    };

    // 更新cron表达式
    const updateCronExpression = (type) => {
      switch(type) {
        case 'hourly':
          multiStrategyForm.cronExpression = '0 * * * *'; // 每小时
          break;
        case 'daily':
          multiStrategyForm.cronExpression = '0 9 * * *'; // 每天上午9点
          break;
        case 'weekly':
          multiStrategyForm.cronExpression = '0 9 * * 1'; // 每周一上午9点
          break;
        default:
          multiStrategyForm.cronExpression = '';
      }
    };

    // 保存多策略配置
    const saveMultiStrategyConfig = async () => {
      if (!multiStrategyForm.taskName) {
        ElMessage.error('请输入任务名称');
        return;
      }

      if (multiStrategyForm.selectedStrategies.length === 0) {
        ElMessage.error('请至少选择一个策略');
        return;
      }

      if (multiStrategyForm.dingtalkEnabled && !multiStrategyForm.dingtalkWebhook) {
        ElMessage.error('请输入钉钉机器人Webhook URL');
        return;
      }

      try {
        const payload = {
          task_name: multiStrategyForm.taskName,
          strategy_ids: multiStrategyForm.selectedStrategies,
          cron_expression: multiStrategyForm.cronExpression,
          message_format: multiStrategyForm.messageFormat,
          user_id: 'current_user_id', // 这里需要获取当前用户ID
          dingtalk_webhook: multiStrategyForm.dingtalkEnabled ? multiStrategyForm.dingtalkWebhook : null,
          enabled: true
        };

        const response = await request({
          url: '/v1/multi-strategy/config',
          method: 'POST',
          data: payload
        });

        if (response.success) {
          ElMessage.success(response.message || '多策略配置保存成功');
          togglePanel(); // 关闭面板
          emit('strategy-configured', payload);
        } else {
          ElMessage.error(response.message || '保存配置失败');
        }
      } catch (error) {
        console.error('保存多策略配置失败:', error);
        ElMessage.error('保存配置失败: ' + error.message);
      }
    };

    // 立即执行
    const executeNow = async () => {
      if (multiStrategyForm.selectedStrategies.length === 0) {
        ElMessage.error('请至少选择一个策略');
        return;
      }

      try {
        const response = await request({
          url: '/v1/multi-strategy/execute',
          method: 'POST',
          data: {
            strategy_ids: multiStrategyForm.selectedStrategies,
            message_format: multiStrategyForm.messageFormat
          }
        });

        if (response.success) {
          ElMessage.success('多策略筛选执行成功');
          
          // 如果启用了钉钉通知，模拟发送
          if (multiStrategyForm.dingtalkEnabled && multiStrategyForm.dingtalkWebhook) {
            // 这里在实际应用中会调用后端发送钉钉消息
            console.log('模拟发送钉钉消息:', response.formatted_message);
          }
        } else {
          ElMessage.error(response.message || '执行失败');
        }
      } catch (error) {
        console.error('执行多策略筛选失败:', error);
        ElMessage.error('执行失败: ' + error.message);
      }
    };

    // 切换面板显示状态
    const togglePanel = () => {
      emit('update:showMultiStrategyPanel', !props.showMultiStrategyPanel);
    };

    onMounted(() => {
      loadAvailableStrategies();
    });

    return {
      availableStrategies,
      multiStrategyForm,
      updateCronExpression,
      saveMultiStrategyConfig,
      executeNow,
      togglePanel
    };
  }
};
</script>

<style scoped>
.multi-strategy-card {
  margin-top: 20px;
  max-width: 800px;
}
</style>