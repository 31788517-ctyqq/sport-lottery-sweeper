<template>
  <div class="page-browser-container">
    <el-card class="page-browser-card">
      <template #header>
        <div class="card-header">
          <span class="title">页面浏览器</span>
          <el-button class="button" type="primary" @click="refreshPages">刷新页面列表</el-button>
        </div>
      </template>

      <!-- 搜索和过滤 -->
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索页面..."
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        <el-select
          v-model="selectedModule"
          placeholder="选择模块"
          clearable
          class="module-select"
        >
          <el-option
            v-for="module in allModules"
            :key="module"
            :label="module"
            :value="module"
          />
        </el-select>
      </div>

      <!-- 页面列表 -->
      <div class="page-list">
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item
            v-for="(pages, moduleName) in filteredModules"
            :key="moduleName"
            :title="`${moduleName} (${Object.keys(pages).length} 个页面)`"
            :name="moduleName"
          >
            <el-row :gutter="12">
              <el-col
                v-for="(pageComponent, pageName) in pages"
                :key="pageName"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
              >
                <el-card class="page-card" shadow="hover">
                  <template #header>
                    <div class="page-card-header">
                      <span class="page-name">{{ pageName }}</span>
                    </div>
                  </template>
                  <el-button
                    type="text"
                    class="page-link"
                    @click="openPage(moduleName, pageName)"
                  >
                    访问页面
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 页面预览弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentModuleName + ' / ' + currentPageName"
      width="80%"
      top="5vh"
      class="page-preview-dialog"
    >
      <div class="preview-content">
        <component :is="currentPageComponent" v-if="currentPageComponent" />
        <el-empty v-else description="页面组件加载中..." />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { pageMap, getAllModules, getPagesInModule, findPageComponent } from '@/utils/pageMap';

export default {
  name: 'PageBrowser',
  setup() {
    const searchQuery = ref('');
    const selectedModule = ref('');
    const activeNames = ref([]);
    const dialogVisible = ref(false);
    const currentPageComponent = ref(null);
    const currentModuleName = ref('');
    const currentPageName = ref('');

    // 获取所有模块
    const allModules = computed(() => getAllModules());

    // 根据搜索和筛选条件过滤模块
    const filteredModules = computed(() => {
      let result = { ...pageMap };
      
      // 按模块筛选
      if (selectedModule.value) {
        result = {
          [selectedModule.value]: result[selectedModule.value]
        };
      }
      
      // 按搜索词筛选
      if (searchQuery.value) {
        const searchLower = searchQuery.value.toLowerCase();
        const filteredResult = {};
        
        for (const [moduleName, pages] of Object.entries(result)) {
          const filteredPages = {};
          
          for (const [pageName, pageComponent] of Object.entries(pages)) {
            if (
              moduleName.toLowerCase().includes(searchLower) ||
              pageName.toLowerCase().includes(searchLower)
            ) {
              filteredPages[pageName] = pageComponent;
            }
          }
          
          if (Object.keys(filteredPages).length > 0) {
            filteredResult[moduleName] = filteredPages;
          }
        }
        
        result = filteredResult;
      }
      
      return result;
    });

    // 刷新页面列表
    const refreshPages = () => {
      ElMessage.success('页面列表已刷新');
    };

    // 打开页面预览
    const openPage = async (moduleName, pageName) => {
      currentModuleName.value = moduleName;
      currentPageName.value = pageName;

      try {
        // 动态加载组件
        const component = findPageComponent(moduleName, pageName);
        if (component) {
          const loadedComponent = await component();
          currentPageComponent.value = loadedComponent.default || loadedComponent;
          dialogVisible.value = true;
        } else {
          ElMessage.error(`找不到页面组件: ${moduleName}/${pageName}`);
        }
      } catch (error) {
        console.error(`加载页面组件失败: ${moduleName}/${pageName}`, error);
        ElMessage.error(`加载页面失败: ${moduleName}/${pageName}`);
      }
    };

    return {
      searchQuery,
      selectedModule,
      activeNames,
      dialogVisible,
      currentPageComponent,
      currentModuleName,
      currentPageName,
      allModules,
      filteredModules,
      refreshPages,
      openPage
    };
  }
};
</script>

<style scoped>
.page-browser-container {
  padding: 20px;
}

.page-browser-card {
  min-height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.search-section {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.module-select {
  width: 200px;
}

.page-list {
  margin-top: 20px;
}

.page-card {
  margin-bottom: 10px;
}

.page-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-name {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.page-link {
  width: 100%;
  text-align: center;
}

.preview-content {
  min-height: 50vh;
}

@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
  }

  .search-input {
    max-width: none;
    margin-bottom: 10px;
  }

  .module-select {
    width: 100%;
  }
}
</style>