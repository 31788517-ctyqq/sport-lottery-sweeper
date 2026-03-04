<!-- frontend/src/components/admin/DataTable.vue -->
<template>
  <div class="data-table-component">
    <!-- Filters/Actions Bar (Optional) -->
    <div class="table-controls" v-if="showControls">
      <van-search
        v-model="searchValue"
        placeholder="搜索..."
        shape="round"
        @search="handleSearch"
      />
      <van-button size="small" type="primary" @click="$emit('add')">新增</van-button>
    </div>

    <!-- Table Content using Vant List -->
    <van-list
      v-model:loading="loading"
      :finished="finished"
      finished-text="没有更多了"
      @load="onLoad"
    >
      <van-cell-group inset v-if="data.length > 0">
        <van-cell
          v-for="item in data"
          :key="item.id"
          clickable
          @click="$emit('row-click', item)"
        >
          <template #title>
            <div class="row-header">
              <span class="row-id">{{ item.id }}</span>
              <span class="row-status" :class="getStatusClass(item.status)">{{ item.status }}</span>
            </div>
          </template>
          <template #label>
            <div class="row-details">
              <p><strong>名称:</strong> {{ item.name || 'N/A' }}</p>
              <p><strong>描述:</strong> {{ item.description || 'N/A' }}</p>
              <p><strong>更新时间:</strong> {{ formatDate(item.updatedAt) }}</p>
            </div>
          </template>
          <template #default>
            <div class="row-actions">
              <van-button size="mini" type="primary" @click.stop="$emit('edit', item)">编辑</van-button>
              <van-button size="mini" type="danger" @click.stop="$emit('delete', item)">删除</van-button>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
      <van-empty v-else description="暂无数据" />
    </van-list>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { format } from 'date-fns'; // Example using date-fns

// Props
defineProps({
  showControls: {
    type: Boolean,
    default: true
  }
});

// Emits
const emit = defineEmits(['load-more', 'search', 'add', 'edit', 'delete', 'row-click']);

// Data
const data = ref([]);
const loading = ref(false);
const finished = ref(false);
const searchValue = ref('');

// Methods
const onLoad = () => {
  // Simulate loading data
  setTimeout(() => {
    const newData = generateMockData(); // Replace with actual API call
    data.value.push(...newData);
    loading.value = false;

    if (data.value.length >= 20) { // Example finish condition
      finished.value = true;
    }
  }, 1000);
};

const handleSearch = () => {
    emit('search', searchValue.value);
    // Reset list state for new search
    data.value = [];
    finished.value = false;
    // Optionally trigger a new load based on search term
    // onLoad(); // Or call an API directly
};

const getStatusClass = (status) => {
  // Example status mapping
  switch(status) {
    case 'active': return 'status-active';
    case 'inactive': return 'status-inactive';
    case 'pending': return 'status-pending';
    default: return '';
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return format(new Date(dateString), 'yyyy-MM-dd HH:mm');
};

// Mock data generator
const generateMockData = () => {
  const statuses = ['active', 'inactive', 'pending'];
  const names = ['Item A', 'Item B', 'Item C', 'Item D', 'Item E'];
  const descriptions = ['Description 1', 'Description 2', 'Description 3', 'Description 4', 'Description 5'];
  const now = Date.now();
  return Array.from({ length: 5 }, (_, i) => ({
    id: `${now + i}`,
    name: names[i % names.length],
    description: descriptions[i % descriptions.length],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    updatedAt: new Date(now - Math.random() * 100000000).toISOString()
  }));
};

onMounted(() => {
  // Initial load
  onLoad();
});
</script>

<style scoped>
.data-table-component {
  padding: var(--van-padding-xs) 0;
}
.table-controls {
  padding: 0 var(--van-padding-md) var(--van-padding-xs);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.row-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.row-id {
  font-weight: bold;
}
.row-status {
  font-size: var(--van-font-size-xs);
  padding: 2px 6px;
  border-radius: 4px;
}
.status-active { background-color: var(--van-success-color); color: white; }
.status-inactive { background-color: var(--van-gray-5); color: var(--van-gray-8); }
.status-pending { background-color: var(--van-warning-color); color: white; }
.row-details {
  margin-top: var(--van-padding-xs);
  font-size: var(--van-font-size-sm);
  color: var(--van-gray-6);
}
.row-details p {
  margin: var(--van-padding-xs) 0;
}
.row-actions {
  display: flex;
  gap: var(--van-padding-xs);
}
</style>