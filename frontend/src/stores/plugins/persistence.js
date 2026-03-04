// frontend/src/store/plugins/persistence.js
import { defineStore, storeToRefs } from 'pinia';

/**
 * Pinia 持久化插件
 * @param {Object} options - 插件选项
 * @param {string} [options.storage='localStorage'] - 存储方式 ('localStorage' 或 'sessionStorage')
 * @param {Array<string>} [options.exclude=[]] - 不需要持久化的 store 名称列表
 * @param {Function} [options.beforeRestore] - 恢复状态前的回调
 * @param {Function} [options.afterRestore] - 恢复状态后的回调
 */
export const createPersistPlugin = (options = {}) => {
  const storage = options.storage || 'localStorage';
  const exclude = options.exclude || [];
  const beforeRestore = options.beforeRestore || (() => {});
  const afterRestore = options.afterRestore || (() => {});

  return (context) => {
    const { store, pinia, options: storeOptions } = context;

    // 如果 store 在排除列表中，则不进行持久化
    if (exclude.includes(store.$id)) {
      return;
    }

    const storageKey = `pinia_${store.$id}`;

    // --- 从存储中恢复状态 ---
    const restoreState = () => {
      try {
        const savedState = window[storage].getItem(storageKey);
        if (savedState) {
          const parsedState = JSON.parse(savedState);
          beforeRestore({ store, savedState: parsedState });

          // 使用 $patch 方法安全地更新状态
          store.$patch(parsedState);

          afterRestore({ store, restoredState: parsedState });
        }
      } catch (error) {
        console.warn(`Failed to restore state for store "${store.$id}" from ${storage}:`, error);
      }
    };

    // --- 将状态保存到存储 ---
    const saveState = (state) => {
      try {
        // 过滤掉计算属性 (getters)，只序列化 state
        const stateToSave = {};
        Object.keys(state).forEach(key => {
          // 简单过滤，避免序列化复杂对象或函数
          if (
            typeof state[key] !== 'function' &&
            !(state[key] instanceof Function) &&
            typeof state[key] !== 'object' ||
            state[key] === null ||
            Array.isArray(state[key]) ||
            typeof state[key] === 'string' ||
            typeof state[key] === 'number' ||
            typeof state[key] === 'boolean'
          ) {
             stateToSave[key] = state[key];
          } else {
              // 对于对象，尝试浅拷贝其基本类型值
              if (typeof state[key] === 'object' && state[key] !== null) {
                  stateToSave[key] = {};
                  for (let subKey in state[key]) {
                      if (
                          typeof state[key][subKey] !== 'function' &&
                          typeof state[key][subKey] !== 'object' ||
                          state[key][subKey] === null ||
                          Array.isArray(state[key][subKey]) ||
                          typeof state[key][subKey] === 'string' ||
                          typeof state[key][subKey] === 'number' ||
                          typeof state[key][subKey] === 'boolean'
                      ) {
                           stateToSave[key][subKey] = state[key][subKey];
                      }
                  }
              }
          }
        });
        window[storage].setItem(storageKey, JSON.stringify(stateToSave));
      } catch (error) {
        console.warn(`Failed to save state for store "${store.$id}" to ${storage}:`, error);
      }
    };

    // 应用启动时恢复状态
    // 注意：这里需要确保 DOM 已加载，或者在 Pinia 初始化之后执行
    // 一个更安全的方式是在 main.js 或根组件挂载后手动调用一次 restoreState
    // 但为了插件本身自动运行，我们将其放在 onMounted 钩子中
    // 由于插件无法直接访问 Vue 生命周期，我们可以利用 store 的初始化时机
    // 通过订阅 store 的 $subscribe，在第一次初始化后恢复状态
    let isFirstInit = true;
    const unsubscribe = store.$subscribe(
      (mutation, state) => {
        if (isFirstInit) {
          // 第一次订阅时，说明 store 刚创建，此时尝试恢复
          restoreState();
          isFirstInit = false;
        } else {
          // 之后的任何状态变化都触发保存
          saveState(state);
        }
      },
      { detached: true } // detached 确保即使没有组件监听该 store，插件也能工作
    );

    // 可选：返回一个卸载函数来清理订阅
    // 但在 Pinia 插件中通常不需要
  };
};

// --- 使用示例 ---
// 在 store/index.js 中使用:
// import { createPinia } from 'pinia';
// import { createPersistPlugin } from './plugins/persistence';
//
// const pinia = createPinia();
// pinia.use(createPersistPlugin({
//   storage: 'localStorage',
//   exclude: ['notifications'], // 不持久化 notifications store
// }));
//
// app.use(pinia);
//
// --- 在某个 store 定义中 ---
// import { defineStore } from 'pinia';
//
// export const useUserStore = defineStore('user', {
//   state: () => ({
//     userInfo: null,
//     token: '',
//     // ...
//   }),
//   // actions 和 getters...
// });
// // 这个 store 的状态会被自动持久化